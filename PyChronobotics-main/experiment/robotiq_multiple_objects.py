import pychrono as chrono
import pychrono.irrlicht as chronoirr
import sys
import os
import numpy as np

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
print(project_root)
# Add the parent directory of 'models' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.robot_arm import RobotiqGripper
import math
from util.InverseKinematics import RobotArmInverseKinematicsSolver


system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

gripper = RobotiqGripper(system, chrono.ChVector3d(0, 0, 1.06))

### Create environment
# Create a floor
floor_material = chrono.ChContactMaterialNSC()
floor = chrono.ChBodyEasyBox(100, 100, 0.01, 1000, True, True, floor_material)
floor.SetPos(chrono.ChVector3d(0, 0, -0.042 - 1.06))
floor.SetFixed(True)
floor.GetVisualShape(0).SetColor(chrono.ChColor(0.5, 0.2, .8))

# Define a collision shape
floor_ct_shape = chrono.ChCollisionShapeBox(floor_material, 20, 1, 20)
floor.AddCollisionShape(floor_ct_shape, chrono.ChFramed(chrono.ChVector3d(0, -1, 0), chrono.QUNIT))
floor.EnableCollision(True)

system.Add(floor)

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
system.Add(mesh_body)

# Load and add the table
table_mesh = chrono.ChTriangleMeshConnected()
table_mesh.LoadWavefrontMesh(project_root + '/data/test_objs/table.obj', False, True)
table_mesh.Transform(chrono.ChVector3d(0, 0, 0), chrono.ChMatrix33d(0.01))

# Create a body for the table
table_body = chrono.ChBody()
table_body.SetPos(chrono.ChVector3d(0, 0, 0.45 - 0.98))  # Adjust position as needed
table_body.SetRot(chrono.Q_ROTATE_Y_TO_Z)  # Adjust rotation if needed

# Add visual shape
table_shape = chrono.ChVisualShapeTriangleMesh()
table_shape.SetMesh(table_mesh)
table_shape.SetMutable(False)
table_body.AddVisualShape(table_shape)

# Add collision shape
contact_material = chrono.ChContactMaterialNSC()
contact_material.SetRollingFriction(0.05)
table_collision_shape = chrono.ChCollisionShapeTriangleMesh(contact_material, table_mesh, False, False, 0.01)
table_body.AddCollisionShape(table_collision_shape)
table_body.EnableCollision(True)
table_body.SetFixed(True)
system.Add(table_body)

# Add a ball to the table
ball1 = chrono.ChBodyEasySphere(0.05, 1, True, True, contact_material)
ball1.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/blue.png"))
ball1.SetName("blue_ball")
ball1.SetPos(chrono.ChVector3d(0.03, .653, 1.1))
ball1.SetRot(chrono.Q_ROTATE_Y_TO_Z)
ball1.SetFixed(False)
ball1.EnableCollision(True)
system.Add(ball1)
gripper.add_object("blue_ball")


ball2 = chrono.ChBodyEasySphere(0.05, 1, True, True, contact_material)
ball2.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/pink.png"))
ball2.SetName("red_ball")
ball2.SetPos(chrono.ChVector3d(1, .653, 1.1))
ball2.SetRot(chrono.Q_ROTATE_Y_TO_Z)
ball2.SetFixed(False)
ball2.EnableCollision(True)
system.Add(ball2)
gripper.add_object("red_ball")

IK_solver = RobotArmInverseKinematicsSolver('robotiq-3dof')

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

timestep = 0.002
rt_timer = chrono.ChRealtimeStepTimer()

solver = chrono.ChSolverPSOR()
solver.SetMaxIterations(300)
solver.SetTolerance(1e-6)
solver.EnableWarmStart(True)
solver.EnableDiagonalPreconditioner(True)
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
    
    if step_number % render_steps == 0:
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        if save_img:    
            filename = './IMG/img_' + str(render_frame) + '.jpg'
            vis.WriteImageToFile(filename)
            render_frame += 1

    if step_number % control_steps == 0:
        if 3<sim_time < 5:
            # @ Harry to do, need to make this further modularized
            desired_position = np.array([ball1.GetPos().x , ball1.GetPos().y, ball1.GetPos().z+0.02])
            initial_guess = np.array([np.arctan2(desired_position[1],desired_position[0]), math.pi/2, 0.0])
            final_theta = IK_solver.inverse_kinematics_solver(desired_position, initial_guess)
            
            gripper.open()
            gripper.rotate_motor(gripper.motor_base_shoulder, final_theta[0])
            gripper.rotate_motor(gripper.motor_shoulder_biceps, final_theta[1])
            gripper.rotate_motor(gripper.motor_biceps_elbow, final_theta[2])
            gripper.rotate_motor(gripper.motor_elbow_wrist, 0)
            
        if 5 < sim_time < 7:
            gripper.close()
            
        if 7 < sim_time < 9:
            gripper.rotate_motor(gripper.motor_base_shoulder, 0)
            gripper.rotate_motor(gripper.motor_shoulder_biceps, math.pi/2)
            
            
        if sim_time > 9:
            # gripper.rotate_motor(gripper.motor_biceps_elbow, math.pi/3)
            gripper.open()
            # @Sriram to do, need to further change this. like the distance based detection need to be refined. Cuz the inverse
            # kinematics can't accurately reach the exact center of the object. Maybe talk more once we got the chance.


        
    rt_timer.Spin(timestep)
    step_number += 1