import pychrono as chrono
import pychrono.irrlicht as chronoirr
import pychrono.sensor as sens
import pygame
import csv
import sys
import os
import numpy as np
import argparse

cam_pos_global = None
system_global = None

class RayCaster:

    def __init__(self, sys, origin, dims, spacing):
        self.m_sys = system_global
        self.m_origin = origin
        self.m_dims = dims
        self.m_spacing = spacing
        self.m_points = []
        
    # def Update(self):
    #     """Cast rays from camera to contact point origin"""
    #     m_points = []
        
    #     # Direction from camera to contact point
    #     contact_pos = self.m_origin.GetPos()
    #     direc = contact_pos - cam_pos_global
    #     direc_length = chrono.ChVector3d(direc).Length()
        
    #     # Normalize direction
    #     if direc_length > 0:
    #         direc = direc / direc_length
    #     else:
    #         print("Warning: Camera and contact point are at same location")
    #         return m_points
        
    #     nx = round(self.m_dims[0]/self.m_spacing)
    #     ny = round(self.m_dims[1]/self.m_spacing)
        
    #     for ix in range(nx):
    #         for iy in range(ny):
    #             x_local = -0.5 * self.m_dims[0] + ix * self.m_spacing
    #             y_local = -0.5 * self.m_dims[1] + iy * self.m_spacing
                
    #             # Ray origin in world coordinates
    #             from_vec = self.m_origin.TransformPointLocalToParent(chrono.ChVector3d(x_local, y_local, 0.0))
                
    #             # Ray end point (slightly beyond contact point to ensure we capture it)
    #             to = from_vec + direc * (direc_length + 0.1)
                
    #             # Perform ray casting
    #             result = chrono.ChRayhitResult()
    #             self.m_sys.GetCollisionSystem().RayHit(from_vec, to, result)
                
    #             # Check if ray hit something
    #             if result.hit:
    #                 m_points.append(result.abs_hitPoint)
                    
    #                 # Optional: Check if there's an obstruction between camera and contact
    #                 hit_distance = chrono.ChVector3d(result.abs_hitPoint - cam_pos_global).Length()
    #                 if hit_distance < direc_length - 0.01:  # 1cm tolerance
    #                     print(f"Obstruction detected at distance {hit_distance:.3f}m (contact at {direc_length:.3f}m)")
        
    #     self.m_points = m_points
    #     return m_points
    
    def has_clear_line_of_sight(self):
        """Check if there's a clear line of sight from camera to contact point"""
        contact_pos = self.m_origin.GetPos()
        direc = contact_pos - cam_pos_global
        direc_length = direc.Length()
        
        if direc_length == 0:
            return False
        
        # Single ray from camera to contact point
        result = chrono.ChRayhitResult()

        print("contact pos:", contact_pos.x, contact_pos.y, contact_pos.z)
        print("cam pos:", cam_pos_global.x, cam_pos_global.y, cam_pos_global.z)

        coll = self.m_sys.GetCollisionSystem()
        self.m_sys.GetCollisionSystem().RayHit(cam_pos_global, contact_pos, result)
        
        if result.hit:
            # Check if hit point is very close to contact point (allowing small tolerance)
            hit_distance = chrono.ChVector3d(result.abs_hitPoint - cam_pos_global).Length()
            tolerance = 0.05  # 5cm tolerance
            
            if abs(hit_distance - direc_length) < tolerance:
                return True  # Clear line of sight
            else:
                return False  # Something is blocking
        
        return True  # No hit means clear path
# ==================================================================================================

class CameraPoseLogger:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir
        self.frame_number = 0
        
        # Create camera subdirectory if output_dir provided
        if self.output_dir:
            self.camera_dir = os.path.join(self.output_dir, 'camera')
            os.makedirs(self.camera_dir, exist_ok=True)
    
    def log_camera_pose(self, sim_time, cam_pos_world, cam_rot_world):
        """Write camera pose to CSV file for this frame"""
        if self.output_dir:
            # Create filename with zero-padded frame number
            csv_filename = os.path.join(self.camera_dir, f"camera_{self.frame_number:04d}.csv")
            
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['sim_time', 'pos_x', 'pos_y', 'pos_z', 
                               'rot_e0', 'rot_e1', 'rot_e2', 'rot_e3'])
                # Write camera pose
                writer.writerow([
                    sim_time,
                    cam_pos_world.x, cam_pos_world.y, cam_pos_world.z,
                    cam_rot_world.e0, cam_rot_world.e1, cam_rot_world.e2, cam_rot_world.e3
                ])
            
            print(f"Saved camera pose to {csv_filename}")
            
        # Increment frame number for next file
        self.frame_number += 1


class ContactReporter (chrono.ReportContactCallback):
    def __init__(self, items_of_interest, output_dir=None):
        self.items_of_interest = items_of_interest
        self.contact_count = 0  # Add counter
        self.contacts_data = []  # Store contact data for batch writing
        self.output_dir = output_dir
        self.frame_number = 0  # Track frame number for filename
        
        # Create contacts subdirectory if output_dir provided
        if self.output_dir:
            self.contacts_dir = os.path.join(self.output_dir, 'contacts')
            os.makedirs(self.contacts_dir, exist_ok=True)
        
        super().__init__()

    def OnReportContact(self,
                        pA,
                        pB,
                        plane_coord,
                        distance,
                        eff_radius,
                        cforce,
                        ctorque,
                        modA,
                        modB,
                        cnstr_offset):
        frc = plane_coord * cforce
        bodyA = chrono.CastToChBody(modA)
        bodyB = chrono.CastToChBody(modB)

        has_A = False
        for item in self.items_of_interest:
            if bodyA == item:
                has_A = True
                break

        has_B = False
        for item in self.items_of_interest:
            if bodyB == item:
                has_B = True
                break

        if has_A and has_B:
            # Store all contacts without filtering
            self.contact_count += 1
            
            # Store contact data with position for later filtering
            contact_data = {
                'pA': (pA.x, pA.y, pA.z),
                'frc': (frc.x, frc.y, frc.z),
            }
            
            self.contacts_data.append(contact_data)
            print(f"   Contact recorded at ({pA.x:.3f}, {pA.y:.3f}, {pA.z:.3f})")
            
        return True
    
    def write_contacts_to_csv(self, sim_time):
        """Write all collected contacts to a new CSV file for this frame, filtering by line of sight"""
        if self.output_dir:
            # Create filename with zero-padded frame number
            csv_filename = os.path.join(self.contacts_dir, f"contact_{self.frame_number:04d}.csv")
            
            # Filter contacts by line of sight
            visible_contacts = []
            for contact in self.contacts_data:
                #caster = RayCaster(
                #    self.items_of_interest[0].GetSystem(),
                #    chrono.ChFramed(chrono.ChVector3d(contact['pA'][0], contact['pA'][1], contact['pA'][2]), 
                #                    chrono.QuatFromAngleX(-chrono.CH_PI_2)), 
                #    [2.5, 2.5], 
                #    0.02
                #)
                

                #if caster.has_clear_line_of_sight():
                if True:  # Temporarily disable occlusion filtering
                    visible_contacts.append(contact)
                else:
                    print(f"   Contact at ({contact['pA'][0]:.3f}, {contact['pA'][1]:.3f}, {contact['pA'][2]:.3f}) OCCLUDED - filtered out")
            
            with open(csv_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['sim_time', 'pA_x', 'pA_y', 'pA_z', 
                               'frc_x', 'frc_y', 'frc_z'])
                # Write only visible contacts
                for contact in visible_contacts:
                    writer.writerow([
                        sim_time,
                        contact['pA'][0], contact['pA'][1], contact['pA'][2],
                        contact['frc'][0], contact['frc'][1], contact['frc'][2]
                    ])
            
            if visible_contacts:
                print(f"Saved {len(visible_contacts)} visible contacts (out of {len(self.contacts_data)} total) to {csv_filename}")
            else:
                print(f"Saved empty contact file ({len(self.contacts_data)} contacts were occluded) to {csv_filename}")
        
        # Increment frame number for next file
        self.frame_number += 1
        # Clear the data after writing
        self.contacts_data = []
    
    def get_contact_count(self):
        """Get the current contact count"""
        return self.contact_count
    
    def reset_contact_count(self):
        """Reset the contact counter to zero"""
        self.contact_count = 0
        self.contacts_data = []  # Also clear stored contact data


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
sen_out_dir_1 = os.path.join(output_dir, "sensor_img_1/")
sen_out_dir_2 = os.path.join(output_dir, "sensor_img_2/")
#irr_out_dir = os.path.join(output_dir, "irr_img/")
os.makedirs(sen_out_dir, exist_ok=True)
os.makedirs(sen_out_dir_1, exist_ok=True)
#os.makedirs(irr_out_dir, exist_ok=True)

print(f"Output directory: {output_dir}")
print(f"Sensor images: {sen_out_dir}")
print(f"Sensor images 1: {sen_out_dir_1}")
#print(f"Irrlicht images: {irr_out_dir}")

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

#system.SetSolverType(chrono.ChSolver.Type_BARZILAIBORWEIN) # precise, more slow
#system.GetSolver().AsIterative().SetMaxIterations(30)

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

system_global = system

# initialize the assets importer
assets_importer = AssetsImporter(system)

items_of_interest = []


# Create Table --------------------------------------------------------------------
# Load and add the table
table = assets_importer.table(chrono.ChVector3d(0, 0, 0.45 - 0.7), collidable=True)



# Create a box --------------------------------------------------------------------
# box0 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(0.05, 0.8, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
# gripper.add_object("box0")

# box1 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(-0.05, 0.8, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
# gripper.add_object("box1")

# box2 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(0.12, 0.85, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
# gripper.add_object("box2")

# box3 = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(-0.14, 0.83, 0.0), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
# gripper.add_object("box3")


water_bottle_0 = assets_importer.waterbottle(chrono.ChVector3d(0.05, 0.85, 0.1),collidable=True)
gripper.add_object("water_bottle_0")

water_bottle_1 = assets_importer.waterbottle(chrono.ChVector3d(-0.05, 0.85, 0.06),collidable=True)
gripper.add_object("water_bottle_1")

water_bottle_2 = assets_importer.waterbottle(chrono.ChVector3d(0.15, 0.85, 0.06),collidable=True)
gripper.add_object("water_bottle_2")

water_bottle_3 = assets_importer.waterbottle(chrono.ChVector3d(-0.15, 0.85, 0.06),collidable=True)
gripper.add_object("water_bottle_3")

water_bottle_4 = assets_importer.waterbottle(chrono.ChVector3d(-0.25, 0.85, 0.06),collidable=True)
gripper.add_object("water_bottle_4")

water_bottle_5 = assets_importer.waterbottle(chrono.ChVector3d(0.25, 0.85, 0.06),collidable=True)
gripper.add_object("water_bottle_5")


water_bottle_6 = assets_importer.waterbottle(chrono.ChVector3d(-0.35, 0.85, 0.06),collidable=True)
gripper.add_object("water_bottle_6")

water_bottle_7 = assets_importer.waterbottle(chrono.ChVector3d(0.35, 0.85, 0.06),collidable=True)
gripper.add_object("water_bottle_7")

soda_can_0 = assets_importer.sodacan(chrono.ChVector3d(0.0, 0.75, 0.06),collidable=True)
gripper.add_object("soda_can_0")
soda_can_1 = assets_importer.sodacan(chrono.ChVector3d(0.1, 0.75, 0.06),collidable=True)
gripper.add_object("soda_can_1")
soda_can_2 = assets_importer.sodacan(chrono.ChVector3d(-0.1, 0.75, 0.06),collidable=True)
gripper.add_object("soda_can_2")
soda_can_3 = assets_importer.sodacan(chrono.ChVector3d(0.2, 0.75, 0.06),collidable=True)
gripper.add_object("soda_can_3")
soda_can_4 = assets_importer.sodacan(chrono.ChVector3d(-0.2, 0.74, 0.06),collidable=True)
gripper.add_object("soda_can_0")


# add item of interest to list
items_of_interest.append(table)
items_of_interest.append(water_bottle_0)
items_of_interest.append(water_bottle_1)
items_of_interest.append(water_bottle_2)
items_of_interest.append(water_bottle_3)
items_of_interest.append(water_bottle_4)
items_of_interest.append(water_bottle_5)
items_of_interest.append(water_bottle_6)
items_of_interest.append(water_bottle_7)
items_of_interest.append(soda_can_0)
items_of_interest.append(soda_can_1)
items_of_interest.append(soda_can_2)
items_of_interest.append(soda_can_3)
items_of_interest.append(soda_can_4)

robotiq_items_of_interest = gripper.get_bodies_of_interest()
for item in robotiq_items_of_interest:
    items_of_interest.append(item)



# Initialize contact reporter ------------------------------------------------------
contact_reporter = ContactReporter(items_of_interest, output_dir)

print(f"Logging contact data to: {os.path.join(output_dir, 'contacts')}")

# Initialize camera pose logger -----------------------------------------------------
camera_logger = CameraPoseLogger(output_dir)

print(f"Logging camera pose data to: {os.path.join(output_dir, 'camera')}")


# Inverse Kinematics Solver ---------------------------------------------------------
IK_solver = RobotArmInverseKinematicsSolver('robotiq-3dof')


### Add sensors
# Add camera sensor --------------------------------------------------------------------

lens_model = sens.PINHOLE
update_rate = 25
image_width = 256
image_height = 256
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

rotation_4 = chrono.QuatFromAngleZ(chrono.CH_PI*1.2)
rotation_5 = chrono.QuatFromAngleY(chrono.CH_PI/3)
offset_pose_1 = chrono.ChFramed(
        chrono.ChVector3d(0.32, 0.9, 1.6), rotation_4 * rotation_5)

cam_1 = sens.ChCameraSensor(
    floor,              # body camera is attached to
    update_rate,            # update rate in Hz
    offset_pose_1,            # offset pose
    image_width,            # image width
    image_height,           # image height
    fov                     # camera's horizontal field of view
)

cam_1.SetName("Camera Sensor 1")
cam_1.SetLag(lag)
cam_1.SetCollectionWindow(exposure_time)
cam_1.PushFilter(sens.ChFilterVisualize(
    image_width, image_height, "Arm Camera 1"))
cam_1.PushFilter(sens.ChFilterRGBA8Access())
cam_1.PushFilter(sens.ChFilterSave(sen_out_dir_1))

manager.AddSensor(cam_1) # Turned off


## ============================
rotation_6 = chrono.QuatFromAngleZ(chrono.CH_PI*-0.2)
rotation_7 = chrono.QuatFromAngleY(chrono.CH_PI/3)
offset_pose_2 = chrono.ChFramed(
        chrono.ChVector3d(-0.32, 0.9, 1.6), rotation_6* rotation_7)
cam_2 = sens.ChCameraSensor(
    floor,              # body camera is attached to
    update_rate,            # update rate in Hz
    offset_pose_2,            # offset pose
    image_width,            # image width
    image_height,           # image height
    fov                     # camera's horizontal field of view
)

cam_2.SetName("Camera Sensor 2")
cam_2.SetLag(lag)
cam_2.SetCollectionWindow(exposure_time)
cam_2.PushFilter(sens.ChFilterVisualize(
    image_width, image_height, "Arm Camera 2"))
cam_2.PushFilter(sens.ChFilterRGBA8Access())
cam_2.PushFilter(sens.ChFilterSave(sen_out_dir_2))

manager.AddSensor(cam_2) # Turned off

## ===============================





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
save_img = False
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


joint_angles_filename = os.path.join(output_dir, "joint_angles.csv")
joint_angles_file = open(joint_angles_filename, 'w', newline='')
joint_angles_writer = csv.writer(joint_angles_file)
joint_angles_writer.writerow(['sim_time', 'theta_0', 'theta_1', 'theta_2', 'theta_3'])  # Header row

print(f"Logging joint angles to: {joint_angles_filename}")




while vis.Run():
    sim_time = system.GetChTime()

    # Exit simulation after 60 seconds
    if sim_time >= 60.0:
        print(f"Simulation completed at {sim_time:.2f} seconds")
        break

    
    system.DoStepDynamics(timestep)
    manager.Update()


    # Handle pygame events and joystick input
    if True and step_number % control_steps == 0:
        # Get camera pos and rot in world frame
        cam_offset_pose = cam.GetOffsetPose()
        cam_parent = cam.GetParent()
        cam_parent_pos = cam_parent.GetPos()
        cam_parent_rot = cam_parent.GetRot()

        cam_pos_world = cam_parent_pos + cam_parent_rot.Rotate(cam_offset_pose.GetPos())
        cam_rot_world = cam_parent_rot * cam_offset_pose.GetRot()

        print(f"Camera Position (world): {cam_pos_world.x:.3f}, {cam_pos_world.y:.3f}, {cam_pos_world.z:.3f}")
        print(f"Camera Rotation (world): {cam_rot_world.e0:.3f}, {cam_rot_world.e1:.3f}, {cam_rot_world.e2:.3f}, {cam_rot_world.e3:.3f}")

        cam_pos_global = cam_pos_world

        # Log camera pose to CSV
        camera_logger.log_camera_pose(sim_time, cam_pos_world, cam_rot_world)


       # Reset counter before checking contacts
        contact_reporter.reset_contact_count()
        
        # Report all contacts at control frequency
        system.GetContactContainer().ReportAllContacts(contact_reporter)
        
        # Write contacts to CSV
        contact_reporter.write_contacts_to_csv(sim_time)
        
        # Get the count for this timestep
        num_contacts = contact_reporter.get_contact_count()
        
        if num_contacts > 0:  # Log when there are contacts
            print(f"Time {sim_time:.3f}s - Valid contacts: {num_contacts}")



        current_ou_sample = ou_process.sample()
        #pygame.event.pump()  # Update joystick state

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
        if True:
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

                 # Log joint angles to CSV
                joint_angles_writer.writerow([sim_time, final_theta[0], final_theta[1], final_theta[2], final_theta[3]])
                
            except ValueError as e:
                print(f"IK solver failed: {e}")
                print(f"Target position may be unreachable: {desired_position}")

    step_number += 1

# Close CSV file when done
csv_file.close()
joint_angles_file.close()
print(f"Joystick commands saved to: {csv_filename}")
print(f"Joint angles saved to: {joint_angles_filename}")

# Cleanup pygame when done
if True:
    pygame.joystick.quit()
pygame.quit()
