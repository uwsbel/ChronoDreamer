import sys
import os
# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from models.jackal import Jackal
import pychrono as chrono
import pychrono.irrlicht as chronoirr
import pychrono.vehicle as veh
import math

my_system = chrono.ChSystemNSC()
my_system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)  

jackal = Jackal(my_system)

for body in my_system.GetBodies():
    print(body.GetName())

patch_mat = chrono.ChContactMaterialNSC()
# patch_mat.SetFriction(0.1)
# patch_mat.SetRollingFriction(0.001)
terrain = veh.RigidTerrain(my_system)
patch = terrain.AddPatch(patch_mat, 
    chrono.ChCoordsysd(chrono.ChVector3d(0, -0.09, 0), chrono.Q_ROTATE_Z_TO_Y), 
    100, 100)
patch.SetColor(chrono.ChColor(0.0, 0.0, 0.0))
terrain.Initialize()

mmesh = chrono.ChTriangleMeshConnected()
mmesh.LoadWavefrontMesh(project_root + '/data/environment/warehouse.obj', False, True)
# scale to a different size
mmesh.Transform(chrono.ChVector3d(0, 0, 0), chrono.ChMatrix33d(2))

trimesh_shape = chrono.ChVisualShapeTriangleMesh()
trimesh_shape.SetMesh(mmesh)
trimesh_shape.SetName("HMMWV Chassis Mesh")
trimesh_shape.SetMutable(False)

mesh_body = chrono.ChBody()
mesh_body.SetPos(chrono.ChVector3d(0, 0, 0))
mesh_body.AddVisualShape(trimesh_shape)
mesh_body.SetFixed(True)
my_system.Add(mesh_body)
    
### Create visualization for the gripper fingers
vis = chronoirr.ChVisualSystemIrrlicht(my_system, chrono.ChVector3d(-2, 1, -1))
vis.EnableCollisionShapeDrawing(True)
timestep = 0.001
render_step_size = 1.0 / 25  # FPS = 50
render_steps = math.ceil(render_step_size / timestep)
step_number = 0
render_frame = 0
rt_timer = chrono.ChRealtimeStepTimer()

while vis.Run():
    sim_time = my_system.GetChTime()
    if step_number % render_steps == 0:
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        # filename = './IMG_jackal/img_' + str(render_frame) +'.jpg' 
        # vis.WriteImageToFile(filename)
        # render_frame += 1
    terrain.Synchronize(sim_time)
    my_system.DoStepDynamics(timestep)
    terrain.Advance(timestep)
    
    jackal.control(speed=1, steering=0.2)
    
    rt_timer.Spin(timestep)
    step_number += 1