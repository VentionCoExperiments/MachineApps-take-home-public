"""
Coordinate Transformations
=========================

Transform coordinates between camera frame and robot base frame.

Camera mounting: (From robot base frame to camera frame)
- Position: [500mm, 300mm, 800mm] in robot base frame
- Orientation: Roll=15°, Pitch=-10°, Yaw=45° (intrinsic Z→Y→X)
"""

import numpy as np


# Camera mounting configuration
CAMERA_POSITION_MM = np.array([500.0, 300.0, 800.0])  # [x, y, z] in mm
CAMERA_ROLL_DEG = 15.0   # Rotation about X-axis
CAMERA_PITCH_DEG = -10.0  # Rotation about Y-axis
CAMERA_YAW_DEG = 45.0     # Rotation about Z-axis


def build_rotation_matrix(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """
    Build a 3x3 rotation matrix from Roll-Pitch-Yaw (Euler) angles.
    Uses intrinsic Z→Y→X rotation convention.
    
    Args:
        roll: Rotation about X-axis in radians
        pitch: Rotation about Y-axis in radians
        yaw: Rotation about Z-axis in radians
    
    Returns:
        3x3 rotation matrix
    """
    # Rotation matrix about Z-axis (yaw)
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw),  np.cos(yaw), 0],
        [0,            0,           1]
    ])
    
    # Rotation matrix about Y-axis (pitch)
    Ry = np.array([
        [ np.cos(pitch), 0, np.sin(pitch)],
        [ 0,             1, 0            ],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    # Rotation matrix about X-axis (roll)
    Rx = np.array([
        [1, 0,            0           ],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll),  np.cos(roll)]
    ])
    
    # Intrinsic Z→Y→X: R = Rz * Ry * Rx
    R = Rz @ Ry @ Rx
    
    return R


def camera_to_robot(point_camera: np.ndarray) -> np.ndarray:
    """
    Transform a point from camera frame to robot base frame.
    
    Args:
        point_camera: [x, y, z] coordinates in camera frame (mm)
    
    Returns:
        [x, y, z] coordinates in robot base frame (mm)
    """
    # Convert degrees to radians
    roll_rad = np.deg2rad(CAMERA_ROLL_DEG)
    pitch_rad = np.deg2rad(CAMERA_PITCH_DEG)
    yaw_rad = np.deg2rad(CAMERA_YAW_DEG)
    
    # Build rotation matrix from camera frame to robot frame
    R_camera_to_robot = build_rotation_matrix(roll_rad, pitch_rad, yaw_rad)
    
    # Transform: point_robot = R * point_camera + translation
    point_robot = R_camera_to_robot @ point_camera + CAMERA_POSITION_MM
    
    return point_robot


def robot_to_camera(point_robot: np.ndarray) -> np.ndarray:
    """
    Transform a point from robot base frame to camera frame.
    
    Args:
        point_robot: [x, y, z] coordinates in robot base frame (mm)
    
    Returns:
        [x, y, z] coordinates in camera frame (mm)
    """
    # Convert degrees to radians
    roll_rad = np.deg2rad(CAMERA_ROLL_DEG)
    pitch_rad = np.deg2rad(CAMERA_PITCH_DEG)
    yaw_rad = np.deg2rad(CAMERA_YAW_DEG)
    
    # Build rotation matrix from camera frame to robot frame
    R_camera_to_robot = build_rotation_matrix(roll_rad, pitch_rad, yaw_rad)
    
    # Inverse transformation
    # R_robot_to_camera = R_camera_to_robot^T (for rotation matrices)
    R_robot_to_camera = R_camera_to_robot.T
    
    # Transform: point_camera = R^T * (point_robot - translation)
    point_camera = R_robot_to_camera @ (point_robot - CAMERA_POSITION_MM)
    
    return point_camera


def build_homogeneous_transform(
    rotation: np.ndarray,
    translation: np.ndarray,
) -> np.ndarray:
    """
    Build a 4x4 homogeneous transformation matrix.
    
    Args:
        rotation: 3x3 rotation matrix
        translation: 3x1 or (3,) translation vector
    
    Returns:
        4x4 homogeneous transformation matrix
    """
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation
    transformation_matrix[:3, 3] = translation.flatten()
    
    return transformation_matrix
