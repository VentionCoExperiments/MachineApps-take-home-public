"""Tests for coordinate transformations. Run with: pytest tests/test_coordinate.py -v"""

import numpy as np
import pytest
from transforms.coordinate import (
    build_rotation_matrix,
    camera_to_robot,
    robot_to_camera,
    build_homogeneous_transform,
    CAMERA_POSITION_MM,
    CAMERA_ROLL_DEG,
    CAMERA_PITCH_DEG,
    CAMERA_YAW_DEG,
)


class TestBuildRotationMatrix:
    """Tests for build_rotation_matrix function."""
    
    def test_identity_rotation(self):
        """Test that zero angles produce identity matrix."""
        R = build_rotation_matrix(0, 0, 0)
        expected = np.eye(3)
        np.testing.assert_array_almost_equal(R, expected)
    
    def test_rotation_about_x_axis(self):
        """Test rotation about X-axis (roll)."""
        roll = np.pi / 2  # 90 degrees
        R = build_rotation_matrix(roll, 0, 0)
        
        # Verify it's a rotation matrix (orthogonal)
        np.testing.assert_array_almost_equal(R @ R.T, np.eye(3))
        np.testing.assert_almost_equal(np.linalg.det(R), 1.0)
    
    def test_rotation_about_y_axis(self):
        """Test rotation about Y-axis (pitch)."""
        pitch = np.pi / 4  # 45 degrees
        R = build_rotation_matrix(0, pitch, 0)
        
        # Verify it's a rotation matrix (orthogonal)
        np.testing.assert_array_almost_equal(R @ R.T, np.eye(3))
        np.testing.assert_almost_equal(np.linalg.det(R), 1.0)
    
    def test_rotation_about_z_axis(self):
        """Test rotation about Z-axis (yaw)."""
        yaw = np.pi / 3  # 60 degrees
        R = build_rotation_matrix(0, 0, yaw)
        
        # Verify it's a rotation matrix (orthogonal)
        np.testing.assert_array_almost_equal(R @ R.T, np.eye(3))
        np.testing.assert_almost_equal(np.linalg.det(R), 1.0)
    
    def test_combined_rotation(self):
        """Test combined rotations."""
        roll = np.deg2rad(CAMERA_ROLL_DEG)
        pitch = np.deg2rad(CAMERA_PITCH_DEG)
        yaw = np.deg2rad(CAMERA_YAW_DEG)
        
        R = build_rotation_matrix(roll, pitch, yaw)
        
        # Verify it's a rotation matrix (orthogonal with determinant 1)
        np.testing.assert_array_almost_equal(R @ R.T, np.eye(3))
        np.testing.assert_almost_equal(np.linalg.det(R), 1.0)
    
    def test_rotation_matrix_shape(self):
        """Test that rotation matrix has correct shape."""
        R = build_rotation_matrix(0.1, 0.2, 0.3)
        assert R.shape == (3, 3)
    
    def test_inverse_rotation(self):
        """Test that R^(-1) = R^T for rotation matrices."""
        roll = np.deg2rad(CAMERA_ROLL_DEG)
        pitch = np.deg2rad(CAMERA_PITCH_DEG)
        yaw = np.deg2rad(CAMERA_YAW_DEG)
        
        R = build_rotation_matrix(roll, pitch, yaw)
        R_inv = np.linalg.inv(R)
        
        np.testing.assert_array_almost_equal(R_inv, R.T)


class TestCameraToRobot:
    """Tests for camera_to_robot transformation."""
    
    def test_origin_point(self):
        """Test transformation of origin point in camera frame."""
        point_camera = np.array([0.0, 0.0, 0.0])
        point_robot = camera_to_robot(point_camera)
        
        # Origin in camera frame should transform to camera position in robot frame
        np.testing.assert_array_almost_equal(point_robot, CAMERA_POSITION_MM)
    
    def test_positive_x_displacement(self):
        """Test transformation with positive X displacement in camera frame."""
        point_camera = np.array([100.0, 0.0, 0.0])
        point_robot = camera_to_robot(point_camera)
        
        # Should not be at camera position
        assert not np.allclose(point_robot, CAMERA_POSITION_MM)
        # Result should be a valid 3D point
        assert point_robot.shape == (3,)
    
    def test_positive_y_displacement(self):
        """Test transformation with positive Y displacement in camera frame."""
        point_camera = np.array([0.0, 100.0, 0.0])
        point_robot = camera_to_robot(point_camera)
        
        assert point_robot.shape == (3,)
        assert not np.allclose(point_robot, CAMERA_POSITION_MM)
    
    def test_positive_z_displacement(self):
        """Test transformation with positive Z displacement in camera frame."""
        point_camera = np.array([0.0, 0.0, 100.0])
        point_robot = camera_to_robot(point_camera)
        
        assert point_robot.shape == (3,)
        assert not np.allclose(point_robot, CAMERA_POSITION_MM)
    
    def test_arbitrary_point(self):
        """Test transformation of arbitrary point."""
        point_camera = np.array([50.0, -30.0, 75.0])
        point_robot = camera_to_robot(point_camera)
        
        # Should produce valid output
        assert point_robot.shape == (3,)
        assert np.all(np.isfinite(point_robot))
    
    def test_negative_coordinates(self):
        """Test transformation with negative coordinates."""
        point_camera = np.array([-100.0, -100.0, -100.0])
        point_robot = camera_to_robot(point_camera)
        
        assert point_robot.shape == (3,)
        assert np.all(np.isfinite(point_robot))


class TestRobotToCamera:
    """Tests for robot_to_camera transformation."""
    
    def test_camera_position_to_origin(self):
        """Test that camera position in robot frame transforms to origin in camera frame."""
        point_robot = CAMERA_POSITION_MM
        point_camera = robot_to_camera(point_robot)
        
        # Camera position in robot frame should be origin in camera frame
        expected = np.array([0.0, 0.0, 0.0])
        np.testing.assert_array_almost_equal(point_camera, expected)
    
    def test_arbitrary_point(self):
        """Test transformation of arbitrary point."""
        point_robot = np.array([600.0, 400.0, 900.0])
        point_camera = robot_to_camera(point_robot)
        
        # Should produce valid output
        assert point_camera.shape == (3,)
        assert np.all(np.isfinite(point_camera))
    
    def test_negative_offsets(self):
        """Test transformation with negative offsets from camera position."""
        point_robot = CAMERA_POSITION_MM + np.array([-100.0, -100.0, -100.0])
        point_camera = robot_to_camera(point_robot)
        
        assert point_camera.shape == (3,)
        assert np.all(np.isfinite(point_camera))


class TestRoundTrip:
    """Tests for round-trip transformations (camera->robot->camera)."""
    
    def test_round_trip_origin(self):
        """Test round-trip transformation of origin point."""
        point_camera_orig = np.array([0.0, 0.0, 0.0])
        
        # Transform camera -> robot -> camera
        point_robot = camera_to_robot(point_camera_orig)
        point_camera_final = robot_to_camera(point_robot)
        
        np.testing.assert_array_almost_equal(point_camera_final, point_camera_orig)
    
    def test_round_trip_arbitrary_point(self):
        """Test round-trip transformation of arbitrary point."""
        point_camera_orig = np.array([50.0, -30.0, 75.0])
        
        # Transform camera -> robot -> camera
        point_robot = camera_to_robot(point_camera_orig)
        point_camera_final = robot_to_camera(point_robot)
        
        np.testing.assert_array_almost_equal(point_camera_final, point_camera_orig, decimal=10)
    
    def test_round_trip_negative_coordinates(self):
        """Test round-trip transformation with negative coordinates."""
        point_camera_orig = np.array([-100.0, 50.0, -200.0])
        
        # Transform camera -> robot -> camera
        point_robot = camera_to_robot(point_camera_orig)
        point_camera_final = robot_to_camera(point_robot)
        
        np.testing.assert_array_almost_equal(point_camera_final, point_camera_orig, decimal=10)
    
    def test_round_trip_robot_to_camera_to_robot(self):
        """Test round-trip transformation starting from robot frame."""
        point_robot_orig = np.array([600.0, 400.0, 900.0])
        
        # Transform robot -> camera -> robot
        point_camera = robot_to_camera(point_robot_orig)
        point_robot_final = camera_to_robot(point_camera)
        
        np.testing.assert_array_almost_equal(point_robot_final, point_robot_orig, decimal=10)


class TestBuildHomogeneousTransform:
    """Tests for build_homogeneous_transform function."""
    
    def test_identity_transform(self):
        """Test building identity homogeneous transformation."""
        rotation = np.eye(3)
        translation = np.array([0.0, 0.0, 0.0])
        
        T = build_homogeneous_transform(rotation, translation)
        expected = np.eye(4)
        
        np.testing.assert_array_almost_equal(T, expected)
    
    def test_pure_translation(self):
        """Test homogeneous transform with identity rotation."""
        rotation = np.eye(3)
        translation = np.array([100.0, 200.0, 300.0])
        
        T = build_homogeneous_transform(rotation, translation)
        
        # Check shape
        assert T.shape == (4, 4)
        # Check bottom row
        np.testing.assert_array_equal(T[3, :], [0, 0, 0, 1])
        # Check translation
        np.testing.assert_array_almost_equal(T[:3, 3], translation)
    
    def test_pure_rotation(self):
        """Test homogeneous transform with zero translation."""
        roll = np.deg2rad(CAMERA_ROLL_DEG)
        pitch = np.deg2rad(CAMERA_PITCH_DEG)
        yaw = np.deg2rad(CAMERA_YAW_DEG)
        
        rotation = build_rotation_matrix(roll, pitch, yaw)
        translation = np.array([0.0, 0.0, 0.0])
        
        T = build_homogeneous_transform(rotation, translation)
        
        # Check shape
        assert T.shape == (4, 4)
        # Check rotation part
        np.testing.assert_array_almost_equal(T[:3, :3], rotation)
        # Check translation
        np.testing.assert_array_almost_equal(T[:3, 3], [0, 0, 0])
        # Check bottom row
        np.testing.assert_array_equal(T[3, :], [0, 0, 0, 1])
    
    def test_combined_transform(self):
        """Test homogeneous transform with both rotation and translation."""
        roll = np.deg2rad(CAMERA_ROLL_DEG)
        pitch = np.deg2rad(CAMERA_PITCH_DEG)
        yaw = np.deg2rad(CAMERA_YAW_DEG)
        
        rotation = build_rotation_matrix(roll, pitch, yaw)
        translation = CAMERA_POSITION_MM
        
        T = build_homogeneous_transform(rotation, translation)
        
        # Check shape
        assert T.shape == (4, 4)
        # Check rotation part
        np.testing.assert_array_almost_equal(T[:3, :3], rotation)
        # Check translation
        np.testing.assert_array_almost_equal(T[:3, 3], translation)
        # Check bottom row
        np.testing.assert_array_equal(T[3, :], [0, 0, 0, 1])
    
    def test_translation_vector_flattened(self):
        """Test that 2D translation vector is properly flattened."""
        rotation = np.eye(3)
        translation = np.array([[100.0], [200.0], [300.0]])  # Column vector
        
        T = build_homogeneous_transform(rotation, translation)
        
        # Should handle column vector properly
        np.testing.assert_array_almost_equal(T[:3, 3], [100.0, 200.0, 300.0])
    
    def test_homogeneous_matrix_properties(self):
        """Test properties of homogeneous transformation matrix."""
        rotation = build_rotation_matrix(0.1, 0.2, 0.3)
        translation = np.array([10.0, 20.0, 30.0])
        
        T = build_homogeneous_transform(rotation, translation)
        
        # Bottom row should be [0, 0, 0, 1]
        np.testing.assert_array_equal(T[3, :], [0, 0, 0, 1])
        
        # Determinant should be 1 (since it's a proper rotation)
        np.testing.assert_almost_equal(np.linalg.det(T), 1.0)
    
    def test_transform_point_with_homogeneous(self):
        """Test transforming a point using homogeneous matrix."""
        rotation = build_rotation_matrix(0, 0, 0)  # Identity rotation
        translation = np.array([100.0, 200.0, 300.0])
        
        T = build_homogeneous_transform(rotation, translation)
        
        # Point in homogeneous coordinates
        point = np.array([50.0, 60.0, 70.0, 1.0])
        
        # Transform
        transformed = T @ point
        
        # Should be equivalent to simple translation
        expected = np.array([150.0, 260.0, 370.0, 1.0])
        np.testing.assert_array_almost_equal(transformed, expected)


class TestIntegration:
    """Integration tests combining multiple functions."""
    
    def test_camera_to_robot_using_homogeneous(self):
        """Verify that camera_to_robot logic matches homogeneous transform."""
        # Build homogeneous transformation for camera to robot
        roll_rad = np.deg2rad(CAMERA_ROLL_DEG)
        pitch_rad = np.deg2rad(CAMERA_PITCH_DEG)
        yaw_rad = np.deg2rad(CAMERA_YAW_DEG)
        
        R = build_rotation_matrix(roll_rad, pitch_rad, yaw_rad)
        T = build_homogeneous_transform(R, CAMERA_POSITION_MM)
        
        # Test point
        point_camera = np.array([100.0, 50.0, 150.0])
        point_camera_homo = np.append(point_camera, 1.0)
        
        # Using function
        point_robot_func = camera_to_robot(point_camera)
        
        # Using homogeneous matrix
        point_robot_homo = T @ point_camera_homo
        
        # Results should match
        np.testing.assert_array_almost_equal(point_robot_func, point_robot_homo[:3])
    
    def test_all_functions_with_realistic_data(self):
        """Test all functions with realistic palletizer scenario."""
        # Simulate a package detected by camera at offset from camera origin
        package_in_camera_frame = np.array([200.0, -100.0, 500.0])
        
        # Transform to robot frame
        package_in_robot_frame = camera_to_robot(package_in_camera_frame)
        
        # Transform back
        package_back_to_camera = robot_to_camera(package_in_robot_frame)
        
        # Should recover original
        np.testing.assert_array_almost_equal(
            package_back_to_camera, 
            package_in_camera_frame,
            decimal=10
        )
        
        # Build homogeneous matrix for verification
        roll_rad = np.deg2rad(CAMERA_ROLL_DEG)
        pitch_rad = np.deg2rad(CAMERA_PITCH_DEG)
        yaw_rad = np.deg2rad(CAMERA_YAW_DEG)
        
        R = build_rotation_matrix(roll_rad, pitch_rad, yaw_rad)
        T = build_homogeneous_transform(R, CAMERA_POSITION_MM)
        
        # Transform using homogeneous matrix
        package_homo = np.append(package_in_camera_frame, 1.0)
        package_robot_homo = T @ package_homo
        
        # Results should match function output
        np.testing.assert_array_almost_equal(
            package_in_robot_frame,
            package_robot_homo[:3],
            decimal=10
        )
