import asyncio

from robot_sim import Robot
from state_machine.core import BaseStates, BaseTriggers, StateMachine
from state_machine.decorators import (
    auto_timeout,
    on_enter_state,
)
from state_machine.defs import State, StateGroup, Trigger

# Timeout seconds for auto timeout
MOTION_TIMEOUT_S = 30.0
# Gripper needs a default function
GRIPPER_SLEEP_S = 0.3
# Robot sleep to simulate motion
MOTION_POLL_S = 0.005


class Running(StateGroup):
    homing: State = State()
    raisingUp: State = State()
    movingToCube: State = State()
    loweringToCube: State = State()
    closingGripper: State = State()
    liftingFromCube: State = State()
    movingToDest: State = State()
    loweringToDest: State = State()
    openingGripper: State = State()
    liftingFromDest: State = State()


class States:
    idle: State = State()
    running: Running = Running()


class Triggers:
    start = Trigger("start")
    home = Trigger("home")
    finished_homing = Trigger("finished_homing")
    # Move up to avoid collisions
    # Move to Cube (Table A) → Lower → Close Gripper.
    # Lift → Move to Destination (Table B).
    # Lower → Open Gripper → Lift.
    finished_raising_up = Trigger("finished_raising_up")
    finished_moving_to_cube = Trigger("finished_moving_to_cube")
    finished_lowering_to_cube = Trigger("finished_lowering_to_cube")
    finished_closing_gripper = Trigger("finished_closing_gripper")
    finished_lifting_from_cube = Trigger("finished_lifting_from_cube")
    finished_moving_to_dest = Trigger("finished_moving_to_dest")
    finished_lowering_to_dest = Trigger("finished_lowering_to_dest")
    finished_opening_gripper = Trigger("finished_opening_gripper")
    finished_lifting_from_dest = Trigger("finished_lifting_from_dest")
    # Default fault handling
    to_fault = Trigger("to_fault")
    reset = Trigger("reset")


READY = BaseStates.READY.value
TRANSITIONS = [
    # Start sequence
    Triggers.start.transition(READY, States.running.raisingUp),
    Triggers.finished_raising_up.transition(
        States.running.raisingUp, States.running.movingToCube
    ),
    Triggers.finished_moving_to_cube.transition(
        States.running.movingToCube, States.running.loweringToCube
    ),
    Triggers.finished_lowering_to_cube.transition(
        States.running.loweringToCube, States.running.closingGripper
    ),
    Triggers.finished_closing_gripper.transition(
        States.running.closingGripper, States.running.liftingFromCube
    ),
    Triggers.finished_lifting_from_cube.transition(
        States.running.liftingFromCube, States.running.movingToDest
    ),
    Triggers.finished_moving_to_dest.transition(
        States.running.movingToDest, States.running.loweringToDest
    ),
    Triggers.finished_lowering_to_dest.transition(
        States.running.loweringToDest, States.running.openingGripper
    ),
    Triggers.finished_opening_gripper.transition(
        States.running.openingGripper, States.running.liftingFromDest
    ),
    Triggers.finished_lifting_from_dest.transition(
        States.running.liftingFromDest, READY
    ),
    # Home sequence
    Triggers.home.transition(READY, States.running.homing),
    Triggers.finished_homing.transition(States.running.homing, READY),
]


class MachineController(StateMachine):
    def __init__(self):
        super().__init__(states=States, transitions=TRANSITIONS)
        self.robot = Robot()
        self.estop_pressed = False
        # Random start position
        self.cube_position: list[float] = [250.0, 750.0, 0.0]
        self.dest_position: list[float] = [750.0, 250.0, 0.0]
        self.safe_z: float = 100.0
        self.last_error: str = ""

    async def drive_to(
        self, target: list[float], trigger_name: str, speed: int = 90
    ) -> None:
        """Handling 'the move_to method must be called repeatedly until motion is complete.'"""
        self.last_error = ""
        while list(self.robot.current_position) != list(target):
            if self.state == BaseStates.FAULT.value:
                return
            _, _, error = self.robot.move_to(target, speed)
            if error:
                self.last_error = error
                self.trigger(BaseTriggers.TO_FAULT.value)
                return
            # Sleep to simulate motion
            await asyncio.sleep(MOTION_POLL_S)
        if self.state != BaseStates.FAULT.value:
            self.trigger(trigger_name)

    def update_position_travel_height(self, position: list[float]) -> list[float]:
        """Find safe travel height for Z-axis to avoid collisions.
        Cube or dest Z positon + 100 but respect limits."""
        travel_z = max(self.cube_position[2], self.dest_position[2]) + 100
        return [position[0], position[1], min(travel_z, self.robot.robot_limits[2])]

    async def finish_after(self, delay: float, trigger_name: str) -> None:
        """Gripper needed a function to pass in, sleep to simulate motion."""
        await asyncio.sleep(delay)
        if self.state != BaseStates.FAULT.value:
            self.trigger(trigger_name)

    # Home
    @on_enter_state(States.running.homing)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_homing(self, _):
        self.spawn(
            self.drive_to(list(self.robot.home_position), Triggers.finished_homing.name)
        )

    # Pick up sequence
    @on_enter_state(States.running.raisingUp)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_raising_up(self, _):
        self.spawn(
            self.drive_to(
                self.update_position_travel_height(self.robot.current_position),
                Triggers.finished_raising_up.name,
            )
        )

    @on_enter_state(States.running.movingToCube)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_moving_to_cube(self, _):
        self.spawn(
            self.drive_to(
                self.update_position_travel_height(self.cube_position),
                Triggers.finished_moving_to_cube.name,
            )
        )

    @on_enter_state(States.running.loweringToCube)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_lowering_to_cube(self, _):
        self.spawn(
            self.drive_to(
                list(self.cube_position), Triggers.finished_lowering_to_cube.name
            )
        )

    @on_enter_state(States.running.closingGripper)
    def enter_closing_gripper(self, _):
        self.robot.closed_gripper()
        self.spawn(
            self.finish_after(GRIPPER_SLEEP_S, Triggers.finished_closing_gripper.name)
        )

    @on_enter_state(States.running.liftingFromCube)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_lifting_from_cube(self, _):
        self.spawn(
            self.drive_to(
                self.update_position_travel_height(self.cube_position),
                Triggers.finished_lifting_from_cube.name,
            )
        )

    @on_enter_state(States.running.movingToDest)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_moving_to_dest(self, _):
        self.spawn(
            self.drive_to(
                self.update_position_travel_height(self.dest_position),
                Triggers.finished_moving_to_dest.name,
            )
        )

    @on_enter_state(States.running.loweringToDest)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_lowering_to_dest(self, _):
        self.spawn(
            self.drive_to(
                list(self.dest_position), Triggers.finished_lowering_to_dest.name
            )
        )

    @on_enter_state(States.running.openingGripper)
    def enter_opening_gripper(self, _):
        self.robot.open_gripper()
        self.spawn(
            self.finish_after(GRIPPER_SLEEP_S, Triggers.finished_opening_gripper.name)
        )

    @on_enter_state(States.running.liftingFromDest)
    @auto_timeout(MOTION_TIMEOUT_S, Triggers.to_fault)
    def enter_lifting_from_dest(self, _):
        self.spawn(
            self.drive_to(
                self.update_position_travel_height(self.dest_position),
                Triggers.finished_lifting_from_dest.name,
            )
        )
