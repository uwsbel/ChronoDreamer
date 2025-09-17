import pychrono as chrono
import pychrono.irrlicht as chronoirr
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Add the parent directory of 'models' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.robot_arm import RobotiqGripper,RobotMoveo
import math

system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

gripper = RobotiqGripper(system, chrono.ChVector3d(0, 0, 1.06))

gripper_moveo = RobotMoveo(system, chrono.ChVector3d(0, -1, 0))
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
table_collision_shape = chrono.ChCollisionShapeTriangleMesh(contact_material, table_mesh, False, False, 0.01)
table_body.AddCollisionShape(table_collision_shape)
table_body.EnableCollision(True)
table_body.SetFixed(True)
system.Add(table_body)

# Add a ball to the table
ball = chrono.ChBodyEasySphere(0.05, 1, True, True, chrono.ChContactMaterialNSC())
ball.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/blue.png"))
ball.SetName("blue_ball")
# ball.SetPos(chrono.ChVector3d(0, .653, 1.1))
# ball.SetPos(chrono.ChVector3d(.14, -.17, .8))
# ball.SetPos(chrono.ChVector3d(.14, -.17, 1.75))
ball.SetPos(chrono.ChVector3d(0.03, .653, 1.1))


ball.SetRot(chrono.Q_ROTATE_Y_TO_Z)
ball.SetFixed(False)
ball.EnableCollision(True)
system.Add(ball)
gripper.add_object("blue_ball")
# gripper.initialize_object("blue_ball")


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
render_step_size = 1.0 / 20  # FPS = 25
render_steps = math.ceil(render_step_size / timestep)
render_frame = 0
while vis.Run():
    sim_time = system.GetChTime()
    system.DoStepDynamics(timestep)
    
    if step_number % render_steps == 0:
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        # filename = './IMG/img_' + str(render_frame) + '.jpg'
        # vis.WriteImageToFile(filename)
        # render_frame += 1

        
    rt_timer.Spin(timestep)
    step_number += 1