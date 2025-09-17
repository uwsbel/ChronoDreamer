import pychrono as chrono
import pychrono.irrlicht as chronoirr
import pychrono.sensor as sens
import pygame
import csv
import sys
import os
import numpy as np
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Robot arm simulation with joystick control')
parser.add_argument('--output-dir', '-o', type=str, default='output', 
                   help='Output directory for all files (CSV, images, sensor data)')
args = parser.parse_args()

# Create output directory if it doesn't exist
output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)

# Create subdirectories for different types of output
sen_out_dir = os.path.join(output_dir, "sensor_img/")
irr_out_dir = os.path.join(output_dir, "irr_img/")
os.makedirs(sen_out_dir, exist_ok=True)
os.makedirs(irr_out_dir, exist_ok=True)

print(f"Output directory: {output_dir}")
print(f"Sensor images: {sen_out_dir}")
print(f"Irrlicht images: {irr_out_dir}")

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# Add the parent directory of 'models' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.robot_arm import RobotiqGripper
import math
from util.InverseKinematics import RobotArmInverseKinematicsSolver
from util.assets_import import AssetsImporter

# Ornstein-Uhlenbeck Process class for simulating realistic control inputs
class OrnsteinUhlenbeckProcess:
    def __init__(self, size, theta=0.15, mu=0.0, sigma=0.3, dt=1e-2, min_magnitude=0.0):
        """
        Ornstein-Uhlenbeck process for generating correlated noise
        
        Args:
            size: Dimension of the process (3 for x, y, z control)
            theta: Speed of reversion to mean (higher = faster reversion)
            mu: Long-term mean of the process
            sigma: Volatility parameter (higher = more noise)
            dt: Time step
            min_magnitude: Minimum magnitude for the output vector
        """
        self.theta = theta
        self.mu = mu
        self.sigma = sigma
        self.dt = dt
        self.size = size
        self.min_magnitude = min_magnitude
        self.x_prev = np.zeros(size)
        
    def sample(self):
        """Generate next sample from the OU process with minimum magnitude"""
        dx = self.theta * (self.mu - self.x_prev) * self.dt + \
             self.sigma * np.sqrt(self.dt) * np.random.normal(size=self.size)
        self.x_prev = self.x_prev + dx
        
        # Apply minimum magnitude constraint
        if self.min_magnitude > 0:
            current_magnitude = np.linalg.norm(self.x_prev)
            if current_magnitude > 0 and current_magnitude < self.min_magnitude:
                # Scale up to minimum magnitude while preserving direction
                self.x_prev = self.x_prev * (self.min_magnitude / current_magnitude)
            elif current_magnitude == 0:
                # If zero vector, generate random direction with min magnitude
                random_direction = np.random.normal(size=self.size)
                random_direction = random_direction / np.linalg.norm(random_direction)
                self.x_prev = random_direction * self.min_magnitude
        
        return self.x_prev
    
    def reset(self):
        """Reset the process state"""
        self.x_prev = np.zeros(self.size)

# Initialize OU process for 3D movement (x, y, z) with minimum magnitude
# For extremely frequent direction changes
ou_process = OrnsteinUhlenbeckProcess(
    size=3,
    theta=5.0,     # Extremely high mean reversion = constant direction changes
    mu=0.0,        
    sigma=0.5,     # Very high noise for maximum chaos
    dt=0.04,      # Extremely short time step
    min_magnitude=0.8
)

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Check for joystick
if pygame.joystick.get_count() == 0:
    print("No joystick detected!")
    joystick = None
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick '{joystick.get_name()}' initialized")

system = chrono.ChSystemSMC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

gripper = RobotiqGripper(system, chrono.ChVector3d(0, 0, 1.06))

### Create environment
# Create a floor --------------------------------------------------------------------
floor_material = chrono.ChContactMaterialSMC()
floor = chrono.ChBodyEasyBox(100, 100, 0.01, 1000, True, True, floor_material)
floor.SetPos(chrono.ChVector3d(0, 0, -0.042 - 1.06))
floor.SetFixed(True)
floor.GetVisualShape(0).SetColor(chrono.ChColor(0.5, 0.2, .8))

# Define a collision shape
# floor_ct_shape = chrono.ChCollisionShapeBox(floor_material, 20, 1, 20)
# floor.AddCollisionShape(floor_ct_shape, chrono.ChFramed(chrono.ChVector3d(0, -1, 0), chrono.QUNIT))
# floor.EnableCollision(True)

system.Add(floor)

# Create Warehouse --------------------------------------------------------------------
# Load and add the warehouse mesh
mmesh = chrono.ChTriangleMeshConnected()
mmesh.LoadWavefrontMesh(project_root + '/data/environment/warehouse.obj', False, True)

# Add a visual shape for the warehouse mesh
trimesh_shape = chrono.ChVisualShapeTriangleMesh()
trimesh_shape.SetMesh(mmesh)
trimesh_shape.SetName("Warehouse Mesh")
trimesh_shape.SetMutable(False)

mesh_body = chrono.ChBody()
mesh_body.SetPos(chrono.ChVector3d(0, 0, -1.06))
mesh_body.SetRot(chrono.Q_ROTATE_Y_TO_Z)
mesh_body.AddVisualShape(trimesh_shape)
mesh_body.SetFixed(True)
mesh_body.EnableCollision(False)
system.Add(mesh_body)

# initialize the assets importer
assets_importer = AssetsImporter(system)

# Create Table --------------------------------------------------------------------
# Load and add the table
table = assets_importer.table(chrono.ChVector3d(0, 0, 0.45 - 0.7), collidable=True)


flashlight0 = assets_importer.flashlight(chrono.ChVector3d(0.1, 0.655, 0.02),collidable=True)
gripper.add_object("flashlight0")

flashlight1 = assets_importer.flashlight(chrono.ChVector3d(-0.1, 0.655, 0.02),collidable=True)
gripper.add_object("flashlight1")

flashlight2 = assets_importer.flashlight(chrono.ChVector3d(0.15, 0.5, 0.02),collidable=True)
gripper.add_object("flashlight2")

flashlight3 = assets_importer.flashlight(chrono.ChVector3d(-0.13, 0.55, 0.02),collidable=True)
gripper.add_object("flashlight3")


# Create a box --------------------------------------------------------------------
box0 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(0.05, 0.8, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
gripper.add_object("box0")

box1 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(-0.05, 0.8, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
gripper.add_object("box1")

box2 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(0.12, 0.85, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
gripper.add_object("box2")

box3 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(-0.14, 0.83, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
gripper.add_object("box3")


# Inverse Kinematics Solver ---------------------------------------------------------
IK_solver = RobotArmInverseKinematicsSolver('robotiq-3dof')


### Add sensors
# Add camera sensor --------------------------------------------------------------------

lens_model = sens.PINHOLE
update_rate = 25
image_width = 640
image_height = 480
fov = 1.408
lag = 0
exposure_time = 0

manager = sens.ChSensorManager(system)

intensity = 1.0
manager.scene.AddAreaLight(chrono.ChVector3f(0, 0, 4), chrono.ChColor(intensity, intensity, intensity), 500.0, chrono.ChVector3f(1,0,0), chrono.ChVector3f(0,-1,0))


rotation_1 = chrono.QuatFromAngleAxis(np.pi/2, chrono.ChVector3d(0, 0, 1))
rotation_2 = chrono.QuatFromAngleAxis(np.pi/2, chrono.ChVector3d(1, 0, 0))
rotation_3 = chrono.QuatFromAngleAxis(0.5, chrono.ChVector3d(0, 1, 0))
rotation_quat = rotation_1 * rotation_2 * rotation_3
offset_pose = chrono.ChFramed(
        chrono.ChVector3d(0.5, -0.5, 0), rotation_quat)

cam = sens.ChCameraSensor(
    gripper.endoffactor,              # body camera is attached to
    update_rate,            # update rate in Hz
    offset_pose,            # offset pose
    image_width,            # image width
    image_height,           # image height
    fov                    # camera's horizontal field of view
)
cam.SetName("Camera Sensor")
cam.SetLag(lag)
cam.SetCollectionWindow(exposure_time)
cam.PushFilter(sens.ChFilterVisualize(
    image_width, image_height, "Arm Camera"))
cam.PushFilter(sens.ChFilterRGBA8Access())
cam.PushFilter(sens.ChFilterSave(sen_out_dir))

manager.AddSensor(cam) # Turned off

### Simulation Setup
# Irrlicht Visualization
vis = chronoirr.ChVisualSystemIrrlicht(system)
vis.EnableCollisionShapeDrawing(True)
vis.SetWindowTitle("robot arm gripper")
vis.SetWindowSize(2560, 1440)  # Your desired resolution
vis.SetCameraPosition(chrono.ChVector3d(0, 0, 1))
vis.SetCameraVertical(chrono.CameraVerticalDir_Z)

vis.Initialize()

# Add these after initialization
vis.AddSkyBox()  # Uncomment this line
vis.AddCamera(chrono.ChVector3d(-0.6, 1.8, 0.8), chrono.ChVector3d(0, 0.6, 0))


# Reduce the light magnitude
#is.AddLightWithShadow(chrono.ChVector3d(10, 10, 100), chrono.ChVector3d(0, 0, -0.5), 100, 1, 9, 90, 512)

timestep = 0.001
rt_timer = chrono.ChRealtimeStepTimer()


# Initialize desired position
desired_position = np.array([0.0, 0.6, -0.05])  # Starting position
movement_speed = 0.0075  # m/s per control step

step_number = 0
save_img = True
render_step_size = 1.0 / 25  # FPS = 25
control_step_size = 1.0 / 25
render_steps = math.ceil(render_step_size / timestep)
control_steps = math.ceil(control_step_size / timestep)
render_frame = 0
control_step = 0

# Initialize CSV file for logging joystick commands
csv_filename = os.path.join(output_dir, "joystick_commands.csv")
csv_file = open(csv_filename, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['sim_time', 'axis_x', 'axis_y', 'axis_right_y'])  # Header row

print(f"Logging joystick commands to: {csv_filename}")

while vis.Run():
    sim_time = system.GetChTime()

    # Exit simulation after 40 seconds
    if sim_time >= 40.0:
        print(f"Simulation completed at {sim_time:.2f} seconds")
        break
    
    system.DoStepDynamics(timestep)
    manager.Update()
    
    # Handle pygame events and joystick input
    if joystick and step_number % control_steps == 0:
        current_ou_sample = ou_process.sample()
        pygame.event.pump()  # Update joystick state

        axis_x = current_ou_sample[0]
        axis_y = current_ou_sample[1]
        axis_right_y = current_ou_sample[2]

        # Apply deadzone to prevent drift
        deadzone = 0.1
        if abs(axis_x) < deadzone:
            axis_x = 0
        if abs(axis_y) < deadzone:
            axis_y = 0
        if abs(axis_right_y) < deadzone:
            axis_right_y = 0

        if sim_time > 5:
            # Update desired position based on joystick input
            # Left stick controls X and Y movement
            desired_position[0] += axis_x * movement_speed  # X movement
            desired_position[1] += -axis_y * movement_speed  # Y movement (inverted)
            
            # Right stick Y-axis controls Z movement
            desired_position[2] += -axis_right_y * movement_speed  # Z movement (inverted so up = positive Z)
            
            # Optional: Add limits to prevent going too far
            desired_position[0] = np.clip(desired_position[0], -0.4, 0.4)
            desired_position[1] = np.clip(desired_position[1], 0.45, 0.95)
            desired_position[2] = np.clip(desired_position[2], -0.15, 0.3)
            
            # Optional: Print joystick values for debugging
            if step_number % 100 == 0:  # Print every 100 steps to avoid spam
                print(f"Joystick - Left: ({axis_x:.2f}, {axis_y:.2f}), Right Y: {axis_right_y:.2f}")
                print(f"Position: X={desired_position[0]:.3f}, Y={desired_position[1]:.3f}, Z={desired_position[2]:.3f}")
                print(f"Simulation time: {sim_time:.2f}s")
    
    if step_number % render_steps == 0:
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        if save_img:    
            filename = os.path.join(irr_out_dir, str(render_frame) + '.jpg')
            print(filename)
            vis.WriteImageToFile(filename)
            render_frame += 1
    
    if step_number % control_steps == 0:
        # Log joystick commands to CSV file only on control steps
        if joystick:
            csv_writer.writerow([sim_time, axis_x, axis_y, axis_right_y])
            
        if sim_time > 2:  # Start joystick control after 2 seconds
            try:
                if 'prev_control_command' in locals():
                    initial_guess = prev_control_command
                else:
                    initial_guess = np.array([np.arctan2(desired_position[1], desired_position[0]), math.pi/2, 0.0, 0.0])
                final_theta = IK_solver.inverse_kinematics_solver(desired_position, initial_guess)
                
                print(f"Desired position: {desired_position}")
                print(f"Joint angles: {final_theta}")
                
                gripper.rotate_motor(gripper.motor_base_shoulder, final_theta[0])
                gripper.rotate_motor(gripper.motor_shoulder_biceps, final_theta[1])
                gripper.rotate_motor(gripper.motor_biceps_elbow, final_theta[2])
                gripper.rotate_motor(gripper.motor_elbow_wrist, final_theta[3])
                prev_control_command = final_theta
                
            except ValueError as e:
                print(f"IK solver failed: {e}")
                print(f"Target position may be unreachable: {desired_position}")

    step_number += 1

# Close CSV file when done
csv_file.close()
print(f"Joystick commands saved to: {csv_filename}")

# Cleanup pygame when done
if joystick:
    pygame.joystick.quit()
pygame.quit()