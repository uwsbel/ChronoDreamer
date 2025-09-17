import pychrono as chrono
import pychrono.irrlicht as chronoirr
import pychrono.sensor as sens

import sys
import os
import numpy as np

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# Add the parent directory of 'models' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.robot_arm import RobotiqGripper
import math
from util.InverseKinematics import RobotArmInverseKinematicsSolver
from util.assets_import import AssetsImporter


system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

gripper = RobotiqGripper(system, chrono.ChVector3d(0, 0, 1.06))

### Create environment
# Create a floor --------------------------------------------------------------------
floor_material = chrono.ChContactMaterialNSC()
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
table = assets_importer.table(chrono.ChVector3d(0, 0, 0.45 - 0.98), collidable=True)


#mug = assets_importer.mug(chrono.ChVector3d(0.03, 0.655, 0.1),collidable=True)
#gripper.add_object("mug")



# Create a box --------------------------------------------------------------------
box = assets_importer.box([0.05, 0.13, 0.05], chrono.ChVector3d(0.03, 0.8, 0.1), chrono.Q_ROTATE_Y_TO_Z, collidable=True)
gripper.add_object("box")

# Inverse Kinematics Solver ---------------------------------------------------------
IK_solver = RobotArmInverseKinematicsSolver('robotiq-3dof')


### Add sensors
# Add camera sensor --------------------------------------------------------------------

out_dir = "SENSOR_OUTPUT/"
lens_model = sens.PINHOLE
update_rate = 30
image_width = 1280
image_height = 720
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

manager.AddSensor(cam) # Turned off

### Simulation Setup
# Irrlicht Visualization
vis = chronoirr.ChVisualSystemIrrlicht(system)
vis.SetCameraPosition(chrono.ChVector3d(0, 0, 1))
vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
vis.SetWindowSize(1024, 768)
vis.SetWindowTitle("robot arm gripper")
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(-1, -1, 1), chrono.ChVector3d(0, 0, 0))
# Reduce the light magnitude
# vis.AddLightWithShadow(chrono.ChVector3d(10, 10, 100), chrono.ChVector3d(0, 0, -0.5), 100, 1, 9, 90, 512)

timestep = 0.001
rt_timer = chrono.ChRealtimeStepTimer()

solver = chrono.ChSolverPSOR()
solver.SetMaxIterations(400)
solver.SetTolerance(1e-6)
# solver.EnableWarmStart(True)
# solver.EnableDiagonalPreconditioner(True)
system.SetSolver(solver)

step_number = 0
save_img = True
render_step_size = 1.0 / 20  # FPS = 25
control_step_size = 1.0 / 20
render_steps = math.ceil(render_step_size / timestep)
control_steps = math.ceil(control_step_size / timestep)
render_frame = 0
control_step = 0
while vis.Run():
    sim_time = system.GetChTime()
    system.DoStepDynamics(timestep)
    manager.Update()
    
    if step_number % render_steps == 0:
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        if save_img:    
            filename = '/home/jason/Desktop/jz-main/PyChronobotics-main/img_' + str(render_frame) + '.jpg'
            print(filename)
            vis.WriteImageToFile(filename)
            render_frame += 1
        # manager.Update()
    if step_number % control_steps == 0:
        if 3<sim_time < 5:
            # @ Harry to do, need to make this further modularized
            # desired_position = np.array([ball1.GetPos().x , ball1.GetPos().y - 0.03, ball1.GetPos().z + 0.03])
            # desired_position = np.array([ball1.GetPos().x , ball1.GetPos().y - 0.03, ball1.GetPos().z + 0.2])

            desired_position = np.array([box.GetPos().x, box.GetPos().y, box.GetPos().z + 0.1]) #cylinder or box
            #desired_position = np.array([mug.GetPos().x, mug.GetPos().y - 0.17, mug.GetPos().z + 0.2])


            initial_guess = np.array([np.arctan2(desired_position[1],desired_position[0]), math.pi/2, 0.0])
            final_theta = IK_solver.inverse_kinematics_solver(desired_position, initial_guess)
            
            #gripper.open()
            gripper.rotate_motor(gripper.motor_base_shoulder, final_theta[0])
            gripper.rotate_motor(gripper.motor_shoulder_biceps, final_theta[1])
            gripper.rotate_motor(gripper.motor_biceps_elbow, final_theta[2])
            gripper.rotate_motor(gripper.motor_elbow_wrist, 0)
            
        # # if 5 < sim_time < 7:
        #     # gripper.close()


        if 5 < sim_time < 7:
            # @ Harry to do, need to make this further modularized
            # desired_position = np.array([box.GetPos().x, box.GetPos().y, box.GetPos().z + 0.05]) #cylinder or box

            desired_position = np.array([box.GetPos().x + 0.02, box.GetPos().y - 0.04, box.GetPos().z + 0.05])


            initial_guess = np.array([np.arctan2(desired_position[1],desired_position[0]), math.pi/2, 0.0])
            final_theta = IK_solver.inverse_kinematics_solver(desired_position, initial_guess)
            
            #gripper.open()
            gripper.rotate_motor(gripper.motor_base_shoulder, final_theta[0])
            gripper.rotate_motor(gripper.motor_shoulder_biceps, final_theta[1])
            gripper.rotate_motor(gripper.motor_biceps_elbow, final_theta[2])
            gripper.rotate_motor(gripper.motor_elbow_wrist, 0)

        #if 7 < sim_time < 15:
            #gripper.grab_object()

            
        if 15 < sim_time < 17:
            gripper.rotate_motor(gripper.motor_base_shoulder, 0)
            gripper.rotate_motor(gripper.motor_shoulder_biceps, math.pi/2)
            
            
        if sim_time > 18:
            # gripper.rotate_motor(gripper.motor_biceps_elbow, math.pi/3)
            gripper.open()
            # @Sriram to do, need to further change this. like the distance based detection need to be refined. Cuz the inverse
            # kinematics can't accurately reach the exact center of the object. Maybe talk more once we got the chance.


        
    rt_timer.Spin(timestep)
    step_number += 1