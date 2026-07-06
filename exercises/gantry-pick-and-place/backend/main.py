import asyncio

from communication.app import VentionApp
from communication.decorators import action, stream
from machine_controller import MachineController, Triggers
from pydantic import BaseModel
from state_machine.core import BaseStates


class Position(BaseModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class StatusResponse(BaseModel):
    state: str
    position: Position
    gripper: str
    moving: bool
    cube: Position
    dest: Position
    robot_limits: list[float]
    error: str = ""


# Robot + state machine singletons
machine = MachineController()
robot = machine.robot

app = VentionApp(
    name="GantryPickAndPlace", emit_proto=True, proto_path="proto/app.proto"
)


def parse_position(values: list[float]) -> Position:
    x, y, z = values
    return Position(x=x, y=y, z=z)


def build_status() -> StatusResponse:
    """Snapshot the current robot + state machine status."""
    return StatusResponse(
        state=machine.state,
        position=parse_position(list(robot.current_position)),
        gripper=robot.gripper_state.name,
        moving=any(s != 0 for s in robot.axis_speed),
        cube=parse_position(list(machine.cube_position)),
        dest=parse_position(list(machine.dest_position)),
        robot_limits=list(robot.robot_limits),
        error=machine.last_error,
    )


def validate_position_input(pos: Position) -> str | None:
    """Return an error string if any axis is outside the robot's limits."""
    for i, value in enumerate((pos.x, pos.y, pos.z)):
        limit = robot.robot_limits[i]
        if not (0 <= value <= limit):
            return f"Axis {i} value {value} is outside the limits [0, {limit}]"
    return None


def set_position(attr: str, req: Position) -> None:
    """Update a configurable position, but only while idle and if valid."""
    if machine.state != BaseStates.READY.value:
        return
    error = validate_position_input(req)
    if error:
        machine.last_error = error
        return
    machine.last_error = ""
    setattr(machine, attr, [req.x, req.y, req.z])


# Gantry commands
@action()
async def start_sequence() -> StatusResponse:
    """Run the full pick-and-place sequence."""
    if machine.state == BaseStates.READY.value:
        machine.last_error = ""
        machine.trigger(Triggers.start.name)
    return build_status()


@action()
async def home() -> StatusResponse:
    """Move the robot to its home position."""
    if machine.state == BaseStates.READY.value:
        machine.last_error = ""
        machine.trigger(Triggers.home.name)
    return build_status()


@action()
async def get_status() -> StatusResponse:
    """Return the current robot + state machine status."""
    return build_status()


@action()
async def set_cube_position(req: Position) -> StatusResponse:
    """Update the cube position."""
    set_position("cube_position", req)
    return build_status()


@action()
async def set_destination_position(req: Position) -> StatusResponse:
    set_position("dest_position", req)
    return build_status()


@stream(
    name="telemetry",
    payload=StatusResponse,
    replay=True,
    queue_maxsize=1,
    policy="latest",
)
async def telemetry() -> StatusResponse:
    """Stream the current robot + state machine status."""
    return build_status()


app.finalize()


@app.on_event("startup")
async def startup():
    asyncio.create_task(telemetry_loop())


async def telemetry_loop() -> None:
    while True:
        asyncio.create_task(telemetry())
        await asyncio.sleep(0.1)
