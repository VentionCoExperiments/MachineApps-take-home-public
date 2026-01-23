# **Palletizing Logic & Coordinate Transformation**

## **Problem Statement**

Vention is developing a new automated palletizing solution. Your goal is to build a robust backend service that coordinates a **Universal Robots (UR5e)** to pick items from a vision-defined location and place them into a **configurable grid pattern**.

This exercise tests your ability to handle **coordinate frame transformations**, implement industrial **state machines**, and design a clean **API** for hardware control.

## **Checklist of Requirements**

### **Mandatory Requirements**

**Backend Logic & Math**

- [ ] **Coordinate Transformation:**
  - The vision system detects boxes in its own `Camera_Frame`. You must transform these into the `Robot_Base_Frame`.
  - **Physical Setup:** The camera is fixed at `(x=500mm, y=300mm, z=800mm)` relative to the robot base. It is looking directly down, meaning its Z-axis is anti-parallel to the robot's Z-axis.

- [ ] **Dynamic Palletizing Logic:**
  - Implement a sequence to place boxes in an `N x M` grid.
  - Your logic should calculate the required Tool Center Point (TCP) offsets for each "place" position based on box dimensions provided via the API.

- [ ] **State Machine Integration:**
  - Use the [`vention-state-machine`](https://pypi.org/project/vention-state-machine/) library to manage the lifecycle of the operation (e.g., `Idle`, `Homing`, `Picking`, `Placing`, `Fault`).

**API & Communication**

- [ ] **FastAPI Implementation:**
  - Create a RESTful API to configure the pallet dimensions (N rows, M columns), box size, and to trigger the start/stop of the sequence.
  - Ensure all endpoints are documented using the auto-generated **Swagger UI** (`/docs`).

- [ ] **Robot Communication:**
  - Interface with **URSim** (Universal Robots Simulator). You may use any standard library (e.g., `ur_rtde`, `dashboard-client`, or raw sockets) to send motion commands and read telemetry.

- [ ] **Motion Strategy:**
  - Implement safe approach and retract heights to avoid collisions with already-placed boxes on the pallet.

### **Bonus Points**

- [ ] **Orientation Handling:** Handle cases where the box is detected by the camera with a rotation (yaw) and adjust the robot's end-effector accordingly.
- [ ] **Containerization:** Provide a `docker-compose.yml` that orchestrates your backend and a URSim container.
- [ ] **Robustness:** Implement "Singularity" or "Reachability" checks before attempting a move.

---

## **Technical Resources**

### **Simulation Environment**

We recommend using the official URSim Docker image for testing.

```bash
# Pull and run URSim (e-Series)
docker run --rm -it -p 5900:5900 -p 6080:6080 -p 30001-30004:30001-30004 universalrobots/ursim_e-series

```

*The PolyScope interface will be available at `http://localhost:6080/vnc.html`.*

### **Coordinate System Guide**

The camera reports a box at $P_{camera}$. You need to find $P_{robot}$ such that:

$$P_{robot} = R_{camera \to robot} \cdot P_{camera} + T_{camera \to robot}$$

*Note: You are responsible for defining the rotation matrix $R_{camera \to robot}$ and translation vector $T_{camera \to robot}$ based on the physical setup described in the Problem Statement.*

---

## **Submission**

- [ ] Provide a link to a **Git repository** (GitHub).
- [ ] Include a **README** with:
  - Clear instructions on how to launch the backend and connect it to URSim.
  - A brief explanation of how you solved the coordinate transformation.
  - An overview of your State Machine design.

- [ ] (Optional) A screen recording of the URSim move sequence or a log export of the robot's TCP positions during a 2x2 palletizing run.

---

### **Questions?**

If you have any questions regarding the hardware specs or the Vention ecosystem, please reach out to the MachineApps team via email. Happy coding!