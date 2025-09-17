import sys
import os
# Assuming the script is located in the 'experiments/apartment' directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.append(project_root)
# Add the parent directory of 'models' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from models.jackal import Jackal
import pychrono as chrono
import pychrono.irrlicht as chronoirr
import pychrono.vehicle as veh
import pychrono.sensor as sens
import numpy as np
import math

my_system = chrono.ChSystemNSC()
my_system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)  



patch_mat = chrono.ChContactMaterialNSC()
# patch_mat.SetFriction(0.1)
# patch_mat.SetRollingFriction(0.001)
# terrain = veh.RigidTerrain(my_system)
# patch = terrain.AddPatch(patch_mat, 
#     chrono.ChCoordsysd(chrono.ChVector3d(0, -0.09, 0), chrono.Q_ROTATE_Z_TO_Y), 
#     100, 100)
# patch.SetColor(chrono.ChColor(0.0, 0.0, 0.0))
# terrain.Initialize()

mmesh = chrono.ChTriangleMeshConnected()
mmesh.LoadWavefrontMesh(project_root + '/data/environment/flat_env.obj', False, True)

# scale to a different size
# mmesh.Transform(chrono.ChVector3d(0, 0, 0), chrono.ChMatrix33d(2))

trimesh_shape = chrono.ChVisualShapeTriangleMesh()
trimesh_shape.SetMesh(mmesh)
trimesh_shape.SetName("HMMWV Chassis Mesh")
trimesh_shape.SetMutable(False)

mesh_body = chrono.ChBody()
mesh_body.SetPos(chrono.ChVector3d(0, 0, 0))
mesh_body.AddVisualShape(trimesh_shape)
mesh_body.SetFixed(True)
my_system.Add(mesh_body)


# ---------------------------------------

# Add camera sensor

# -----------------
# Camera parameters
# -----------------

# Output directory
out_dir = "SENSOR_OUTPUT/"

# Camera lens model
lens_model = sens.PINHOLE

# Update rate in Hz
update_rate = 30

# Image width and height
image_width = 1280
image_height = 720

# Camera's horizontal field of view
fov = 1.408

# Lag (in seconds) between sensing and when data becomes accessible
lag = 0

# Exposure (in seconds) of each image
exposure_time = 0

manager = sens.ChSensorManager(my_system)

intensity = 1.0
manager.scene.AddAreaLight(chrono.ChVector3f(0, 0, 4), chrono.ChColor(intensity, intensity, intensity), 500.0, chrono.ChVector3f(1,0,0), chrono.ChVector3f(0,-1,0))

rotation_1 = chrono.QuatFromAngleAxis(np.pi/2, chrono.ChVector3d(0, 0, 1))
rotation_2 = chrono.QuatFromAngleAxis(np.pi/2, chrono.ChVector3d(0, 1, 0))
rotation_3 = chrono.QuatFromAngleAxis(np.pi/2, chrono.ChVector3d(0, 0, 1))

rotation_quat = rotation_1 * rotation_2 * rotation_3

offset_pose = chrono.ChFramed(
    chrono.ChVector3d(0, 1, 0), rotation_quat)



cam = sens.ChCameraSensor(
    mesh_body,              # body camera is attached to
    update_rate,            # update rate in Hz
    offset_pose,            # offset pose
    image_width,            # image width
    image_height,           # image height
    fov                    # camera's horizontal field of view
)


cam.SetName("Camera Sensor")
cam.SetLag(lag)
cam.SetCollectionWindow(exposure_time)


# ------------------------------------------------------------------
# Create a filter graph for post-processing the data from the camera
# ------------------------------------------------------------------

# Renders the image at current point in the filter graph

cam.PushFilter(sens.ChFilterVisualize(
    image_width, image_height, "Arm Camera"))

# Provides the host access to this RGBA8 buffer
cam.PushFilter(sens.ChFilterRGBA8Access())

# add sensor to manager
manager.AddSensor(cam)

# ---------------------------------------
    
### Create visualization for the gripper fingers
vis = chronoirr.ChVisualSystemIrrlicht(my_system, chrono.ChVector3d(-2, 1, -1))
vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
vis.AddLightWithShadow(chrono.ChVector3d(6,6,6),  # point
                      chrono.ChVector3d(0,6,0),  # aimpoint
                      5,                       # radius (power)
                      1,11,                     # near, far
                      55)                       # angle of FOV

# vis.EnableShadows()
vis.EnableCollisionShapeDrawing(True)
timestep = 0.001
render_step_size = 1.0 / 25  # FPS = 50
render_steps = math.ceil(render_step_size / timestep)
step_number = 0
render_frame = 0
rt_timer = chrono.ChRealtimeStepTimer()

while vis.Run():
    manager.Update()

    sim_time = my_system.GetChTime()
    if step_number % render_steps == 0:
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        # filename = './IMG_jackal/img_' + str(render_frame) +'.jpg' 
        # vis.WriteImageToFile(filename)
        # render_frame += 1
    my_system.DoStepDynamics(timestep)
    
    
    rt_timer.Spin(timestep)
    step_number += 1