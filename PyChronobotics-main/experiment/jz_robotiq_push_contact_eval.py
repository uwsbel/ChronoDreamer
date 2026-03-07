import pychrono as chrono
import pychrono.irrlicht as chronoirr
import pychrono.sensor as sens
import pygame
import csv
import sys
import os
import numpy as np
import argparse
from pathlib import Path
import math

from wm_llm_world_model import WorldModelRunner, _gemini_list_models

cam_pos_global = None
system_global = None

class RayCaster:
    def __init__(self, sys, origin, dims, spacing):
        self.m_sys = system_global
        self.m_origin = origin
        self.m_dims = dims
        self.m_spacing = spacing
        self.m_points = []

    def has_clear_line_of_sight(self):
        contact_pos = self.m_origin.GetPos()
        direc = contact_pos - cam_pos_global
        direc_length = direc.Length()

        if direc_length == 0:
            return False

        result = chrono.ChRayhitResult()
        self.m_sys.GetCollisionSystem().RayHit(cam_pos_global, contact_pos, result)

        if result.hit:
            hit_distance = chrono.ChVector3d(result.abs_hitPoint - cam_pos_global).Length()
            tolerance = 0.05
            if abs(hit_distance - direc_length) < tolerance:
                return True
            return False

        return True


class CameraPoseLogger:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir
        self.frame_number = 0

        if self.output_dir:
            self.camera_dir = os.path.join(self.output_dir, 'camera')
            os.makedirs(self.camera_dir, exist_ok=True)

    def log_camera_pose(self, sim_time, cam_pos_world, cam_rot_world):
        if self.output_dir:
            csv_filename = os.path.join(self.camera_dir, f"camera_{self.frame_number:04d}.csv")

            with open(csv_filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['sim_time', 'pos_x', 'pos_y', 'pos_z', 'rot_e0', 'rot_e1', 'rot_e2', 'rot_e3'])
                writer.writerow([
                    sim_time,
                    cam_pos_world.x, cam_pos_world.y, cam_pos_world.z,
                    cam_rot_world.e0, cam_rot_world.e1, cam_rot_world.e2, cam_rot_world.e3
                ])

        self.frame_number += 1


class ContactReporter(chrono.ReportContactCallback):
    def __init__(self, items_of_interest, output_dir=None):
        self.items_of_interest = items_of_interest
        self.contact_count = 0
        self.contacts_data = []
        self.output_dir = output_dir
        self.frame_number = 0

        self.items_of_interest_ids = set()
        for item in items_of_interest:
            try:
                pid = item.GetIdentifier()
                self.items_of_interest_ids.add(pid)
            except Exception:
                pass

        super().__init__()

    def OnReportContact(
        self,
        pA,
        pB,
        plane_coord,
        distance,
        eff_radius,
        cforce,
        ctorque,
        modA,
        modB,
        cnstr_offset,
    ):
        physA = None
        physB = None
        try:
            physA = modA.GetPhysicsItem()
        except Exception:
            pass
        try:
            physB = modB.GetPhysicsItem()
        except Exception:
            pass

        idA = physA.GetIdentifier() if physA is not None else None
        idB = physB.GetIdentifier() if physB is not None else None

        has_A = idA in self.items_of_interest_ids if idA is not None else False
        has_B = idB in self.items_of_interest_ids if idB is not None else False

        if has_A and has_B:
            self.contact_count += 1
            frc = plane_coord * cforce
            contact_data = {
                'pA': (pA.x, pA.y, pA.z),
                'frc': (frc.x, frc.y, frc.z),
            }
            self.contacts_data.append(contact_data)

        return True

    def write_contacts_to_csv(self, sim_time):
        if not self.output_dir:
            self.contacts_data = []
            return

        csv_filename = os.path.join(self.output_dir, "contacts.csv")
        existed = os.path.exists(csv_filename)
        with open(csv_filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not existed:
                writer.writerow(['sim_time', 'pA_x', 'pA_y', 'pA_z', 'frc_x', 'frc_y', 'frc_z'])
            for contact in self.contacts_data:
                writer.writerow([
                    sim_time,
                    contact['pA'][0], contact['pA'][1], contact['pA'][2],
                    contact['frc'][0], contact['frc'][1], contact['frc'][2]
                ])

        self.frame_number += 1
        self.contacts_data = []

    def get_contact_count(self):
        return self.contact_count

    def reset_contact_count(self):
        self.contact_count = 0
        self.contacts_data = []


parser = argparse.ArgumentParser(description='Robot arm simulation with joystick control')
parser.add_argument('--output-dir', '-o', type=str, default='output', help='Output directory for all files (CSV, images, sensor data)')

parser.add_argument('--no-world-model', action='store_true')
parser.add_argument('--wm-checkpoint-dir', type=str, default=None)
parser.add_argument('--wm-start-time', type=float, default=10.0)
parser.add_argument('--wm-period', type=float, default=5.0)
parser.add_argument('--wm-stride', type=int, default=15)
parser.add_argument('--wm-venv-python', type=str, default=None)
parser.add_argument('--wm-llm-enable', action='store_true')
parser.add_argument('--wm-llm-model', type=str, default='gemini-2.5-flash')
parser.add_argument('--wm-llm-timeout-s', type=float, default=20.0)
parser.add_argument('--wm-llm-temperature', type=float, default=0.0)
parser.add_argument('--wm-llm-max-output-tokens', type=int, default=1024)
parser.add_argument('--wm-llm-max-attempts', type=int, default=3)
parser.add_argument('--wm-llm-prompt-file', type=str, default=None)
parser.add_argument('--wm-llm-disable-contact-map', action='store_true')
parser.add_argument('--wm-llm-reject-confidence', type=float, default=0.9)
parser.add_argument('--wm-llm-list-models', action='store_true')
parser.add_argument('--wm-llm-list-models-filter', type=str, default='')

parser.add_argument('--control-action-scale', type=float, default=0.35)
parser.add_argument('--control-movement-speed', type=float, default=0.003)
parser.add_argument('--control-deadzone', type=float, default=0.05)
parser.add_argument('--control-start-time', type=float, default=2.0)

parser.add_argument('--ou-theta', type=float, default=0.8)
parser.add_argument('--ou-sigma', type=float, default=0.15)
parser.add_argument('--ou-dt', type=float, default=0.04)
parser.add_argument('--ou-min-magnitude', type=float, default=0.0)
args = parser.parse_args()

if args.wm_llm_list_models:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY")
    data = _gemini_list_models(api_key)
    models = data.get("models", []) if isinstance(data, dict) else []
    flt = (args.wm_llm_list_models_filter or "").lower().strip()
    for m in models:
        name = str(m.get("name", ""))
        if flt and flt not in name.lower():
            continue
        methods = m.get("supportedGenerationMethods", [])
        print(f"{name}  methods={methods}")
    raise SystemExit(0)

output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)

sen_out_dir = os.path.join(output_dir, "sensor_img/")
sen_out_dir_1 = os.path.join(output_dir, "sensor_img_1/")
sen_out_dir_2 = os.path.join(output_dir, "sensor_img_2/")
os.makedirs(sen_out_dir, exist_ok=True)
os.makedirs(sen_out_dir_1, exist_ok=True)
os.makedirs(sen_out_dir_2, exist_ok=True)

world_model_runner = None
if not args.no_world_model:
    chronodreamer_root = Path(__file__).resolve().parents[2]
    one_xgpt_dir = chronodreamer_root / "1xgpt"
    default_ckpt = str(one_xgpt_dir / "data" / "genie_model" / "8_24_ckpt")
    world_model_runner = WorldModelRunner(
        output_root=str(Path(output_dir) / "world_model_preds"),
        camera_dir=sen_out_dir,
        checkpoint_dir=args.wm_checkpoint_dir or default_ckpt,
        start_time=args.wm_start_time,
        period=args.wm_period,
        stride=args.wm_stride,
        venv_python=args.wm_venv_python,
        llm_enabled=args.wm_llm_enable,
        llm_model=args.wm_llm_model,
        llm_timeout_s=args.wm_llm_timeout_s,
        llm_temperature=args.wm_llm_temperature,
        llm_max_output_tokens=args.wm_llm_max_output_tokens,
        llm_max_attempts=args.wm_llm_max_attempts,
        llm_use_contact_map=not args.wm_llm_disable_contact_map,
        llm_reject_confidence=args.wm_llm_reject_confidence,
        llm_prompt_file=args.wm_llm_prompt_file,
        context_globals=globals(),
    )

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.robot_arm import RobotiqGripper
from util.InverseKinematics import RobotArmInverseKinematicsSolver
from util.assets_import import AssetsImporter


class OrnsteinUhlenbeckProcess:
    def __init__(self, size, theta=0.15, mu=0.0, sigma=0.3, dt=1e-2, min_magnitude=0.0):
        self.theta = theta
        self.mu = mu
        self.sigma = sigma
        self.dt = dt
        self.size = size
        self.min_magnitude = min_magnitude
        self.x_prev = np.zeros(size)

    def sample(self):
        dx = self.theta * (self.mu - self.x_prev) * self.dt + self.sigma * np.sqrt(self.dt) * np.random.normal(size=self.size)
        self.x_prev = self.x_prev + dx

        if self.min_magnitude > 0:
            current_magnitude = np.linalg.norm(self.x_prev)
            if current_magnitude > 0 and current_magnitude < self.min_magnitude:
                self.x_prev = self.x_prev * (self.min_magnitude / current_magnitude)
            elif current_magnitude == 0:
                random_direction = np.random.normal(size=self.size)
                random_direction = random_direction / np.linalg.norm(random_direction)
                self.x_prev = random_direction * self.min_magnitude

        return self.x_prev

    def reset(self):
        self.x_prev = np.zeros(self.size)


ou_process = OrnsteinUhlenbeckProcess(
    size=3,
    theta=float(args.ou_theta),
    mu=0.0,
    sigma=float(args.ou_sigma),
    dt=float(args.ou_dt),
    min_magnitude=float(args.ou_min_magnitude),
)

control_action_scale = float(args.control_action_scale)
control_deadzone = float(args.control_deadzone)
control_start_time = float(args.control_start_time)

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No joystick detected!")
    joystick = None
else:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

system = chrono.ChSystemSMC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

gripper = RobotiqGripper(system, chrono.ChVector3d(0, 0, 1.06))

floor_material = chrono.ChContactMaterialSMC()
floor = chrono.ChBodyEasyBox(100, 100, 0.01, 1000, True, True, floor_material)
floor.SetPos(chrono.ChVector3d(0, 0, -0.042 - 1.06))
floor.SetFixed(True)
floor.GetVisualShape(0).SetColor(chrono.ChColor(0.5, 0.2, .8))
system.Add(floor)

mmesh = chrono.ChTriangleMeshConnected()
mmesh.LoadWavefrontMesh(project_root + '/data/environment/warehouse.obj', False, True)

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

assets_importer = AssetsImporter(system)

items_of_interest = []

table = assets_importer.table(chrono.ChVector3d(0, 0, 0.45 - 0.7), collidable=True)
table.SetName("table")

flashlight0 = assets_importer.flashlight(chrono.ChVector3d(0.1, 0.655, 0.02), collidable=True)
flashlight0.SetName("flashlight0")
gripper.add_object("flashlight0")

flashlight1 = assets_importer.flashlight(chrono.ChVector3d(-0.1, 0.655, 0.02), collidable=True)
flashlight1.SetName("flashlight1")
gripper.add_object("flashlight1")

flashlight2 = assets_importer.flashlight(chrono.ChVector3d(0.15, 0.5, 0.02), collidable=True)
flashlight2.SetName("flashlight2")
gripper.add_object("flashlight2")

flashlight3 = assets_importer.flashlight(chrono.ChVector3d(-0.13, 0.55, 0.02), collidable=True)
flashlight3.SetName("flashlight3")
gripper.add_object("flashlight3")

box0 = assets_importer.box(chrono.ChVector3d(0.05, 0.8, 0.0), collidable=True)
box0.SetName("box0")
gripper.add_object("box0")

box1 = assets_importer.box(chrono.ChVector3d(-0.05, 0.8, 0.0), collidable=True)
box1.SetName("box1")
gripper.add_object("box1")

box2 = assets_importer.box(chrono.ChVector3d(0.12, 0.85, 0.0), collidable=True)
box2.SetName("box2")
gripper.add_object("box2")

box3 = assets_importer.box(chrono.ChVector3d(-0.14, 0.83, 0.0), collidable=True)
box3.SetName("box3")
gripper.add_object("box3")

items_of_interest.append(table)
items_of_interest.append(flashlight0)
items_of_interest.append(flashlight1)
items_of_interest.append(flashlight2)
items_of_interest.append(flashlight3)
items_of_interest.append(box0)
items_of_interest.append(box1)
items_of_interest.append(box2)
items_of_interest.append(box3)

robotiq_items_of_interest = gripper.get_bodies_of_interest()
for item in robotiq_items_of_interest:
    items_of_interest.append(item)

contact_reporter = ContactReporter(items_of_interest, output_dir)

camera_logger = CameraPoseLogger(output_dir)

IK_solver = RobotArmInverseKinematicsSolver('robotiq-3dof')

update_rate = 25
image_width = 256
image_height = 256
fov = 1.408
lag = 0
exposure_time = 0

manager = sens.ChSensorManager(system)

intensity = 1.0
manager.scene.AddAreaLight(
    chrono.ChVector3f(0, 0, 4),
    chrono.ChColor(intensity, intensity, intensity),
    500.0,
    chrono.ChVector3f(1, 0, 0),
    chrono.ChVector3f(0, -1, 0),
)

rotation_1 = chrono.QuatFromAngleAxis(np.pi / 2, chrono.ChVector3d(0, 0, 1))
rotation_2 = chrono.QuatFromAngleAxis(np.pi / 2, chrono.ChVector3d(1, 0, 0))
rotation_3 = chrono.QuatFromAngleAxis(0.5, chrono.ChVector3d(0, 1, 0))
rotation_quat = rotation_1 * rotation_2 * rotation_3

offset_pose = chrono.ChFramed(chrono.ChVector3d(0.5, -0.5, 0), rotation_quat)

cam = sens.ChCameraSensor(
    gripper.endoffactor,
    update_rate,
    offset_pose,
    image_width,
    image_height,
    fov,
    2,
)
cam.SetName("Camera Sensor")
cam.SetLag(lag)
cam.SetCollectionWindow(exposure_time)
cam.PushFilter(sens.ChFilterVisualize(image_width, image_height, "Arm Camera"))
cam.PushFilter(sens.ChFilterRGBA8Access())
cam.PushFilter(sens.ChFilterSave(sen_out_dir))
manager.AddSensor(cam)

rotation_4 = chrono.QuatFromAngleZ(chrono.CH_PI * 1.2)
rotation_5 = chrono.QuatFromAngleY(chrono.CH_PI / 3)
offset_pose_1 = chrono.ChFramed(chrono.ChVector3d(0.32, 0.9, 1.6), rotation_4 * rotation_5)

cam_1 = sens.ChCameraSensor(
    floor,
    update_rate,
    offset_pose_1,
    image_width,
    image_height,
    fov,
    2,
)
cam_1.SetName("Camera Sensor 1")
cam_1.SetLag(lag)
cam_1.SetCollectionWindow(exposure_time)
cam_1.PushFilter(sens.ChFilterVisualize(image_width, image_height, "Arm Camera 1"))
cam_1.PushFilter(sens.ChFilterRGBA8Access())
cam_1.PushFilter(sens.ChFilterSave(sen_out_dir_1))
manager.AddSensor(cam_1)

rotation_6 = chrono.QuatFromAngleZ(chrono.CH_PI * -0.2)
rotation_7 = chrono.QuatFromAngleY(chrono.CH_PI / 3)
offset_pose_2 = chrono.ChFramed(chrono.ChVector3d(-0.32, 0.9, 1.6), rotation_6 * rotation_7)

cam_2 = sens.ChCameraSensor(
    floor,
    update_rate,
    offset_pose_2,
    image_width,
    image_height,
    fov,
    2,
)
cam_2.SetName("Camera Sensor 2")
cam_2.SetLag(lag)
cam_2.SetCollectionWindow(exposure_time)
cam_2.PushFilter(sens.ChFilterVisualize(image_width, image_height, "Arm Camera 2"))
cam_2.PushFilter(sens.ChFilterRGBA8Access())
cam_2.PushFilter(sens.ChFilterSave(sen_out_dir_2))
manager.AddSensor(cam_2)

vis = chronoirr.ChVisualSystemIrrlicht(system)
vis.EnableCollisionShapeDrawing(True)
vis.SetWindowTitle("robot arm gripper")
vis.SetWindowSize(2560, 1440)
vis.SetCameraPosition(chrono.ChVector3d(0, 0, 1))
vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(-0.6, 1.8, 0.8), chrono.ChVector3d(0, 0.6, 0))

timestep = 0.001

desired_position = np.array([0.0, 0.6, -0.05])
movement_speed = float(args.control_movement_speed)

step_number = 0
save_img = False
render_step_size = 1.0 / 25
control_step_size = 1.0 / 25
render_steps = math.ceil(render_step_size / timestep)
control_steps = math.ceil(control_step_size / timestep)
render_frame = 0

axis_x = 0.0
axis_y = 0.0
axis_right_y = 0.0

actions_hist = []
joints_hist = []
last_joint_angles = np.zeros(4, dtype=np.float32)

csv_filename = os.path.join(output_dir, "joystick_commands.csv")
csv_file = open(csv_filename, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['sim_time', 'axis_x', 'axis_y', 'axis_right_y'])

joint_angles_filename = os.path.join(output_dir, "joint_angles.csv")
joint_angles_file = open(joint_angles_filename, 'w', newline='')
joint_angles_writer = csv.writer(joint_angles_file)
joint_angles_writer.writerow(['sim_time', 'theta_0', 'theta_1', 'theta_2', 'theta_3'])

system.SetNumThreads(6)

while vis.Run():
    sim_time = system.GetChTime()

    if sim_time >= 60.0:
        break

    system.DoStepDynamics(timestep)
    manager.Update()

    if True and step_number % control_steps == 0:
        cam_offset_pose = cam.GetOffsetPose()
        cam_parent = cam.GetParent()
        cam_parent_pos = cam_parent.GetPos()
        cam_parent_rot = cam_parent.GetRot()

        cam_pos_world = cam_parent_pos + cam_parent_rot.Rotate(cam_offset_pose.GetPos())
        cam_rot_world = cam_parent_rot * cam_offset_pose.GetRot()

        cam_pos_global = cam_pos_world

        camera_logger.log_camera_pose(sim_time, cam_pos_world, cam_rot_world)

        contact_reporter.reset_contact_count()
        system.GetContactContainer().ReportAllContacts(contact_reporter)
        contact_reporter.write_contacts_to_csv(sim_time)

        planned = None
        if world_model_runner is not None:
            planned = world_model_runner.pop_next_planned_action()
        if planned is None:
            current_ou_sample = ou_process.sample()
            axis_x = float(current_ou_sample[0])
            axis_y = float(current_ou_sample[1])
            axis_right_y = float(current_ou_sample[2])
        else:
            axis_x = float(planned[0])
            axis_y = float(planned[1])
            axis_right_y = float(planned[2])

        deadzone = control_deadzone
        if abs(axis_x) < deadzone:
            axis_x = 0
        if abs(axis_y) < deadzone:
            axis_y = 0
        if abs(axis_right_y) < deadzone:
            axis_right_y = 0

        if planned is None:
            axis_x *= control_action_scale
            axis_y *= control_action_scale
            axis_right_y *= control_action_scale

        if sim_time > control_start_time:
            desired_position[0] += axis_x * movement_speed
            desired_position[1] += -axis_y * movement_speed
            desired_position[2] += -axis_right_y * movement_speed

            desired_position[0] = np.clip(desired_position[0], -0.4, 0.4)
            desired_position[1] = np.clip(desired_position[1], 0.45, 0.95)
            desired_position[2] = np.clip(desired_position[2], -0.15, 0.3)

    if step_number % render_steps == 0:
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        if save_img:
            filename = os.path.join(output_dir, str(render_frame) + '.jpg')
            vis.WriteImageToFile(filename)
            render_frame += 1

    if step_number % control_steps == 0:
        csv_writer.writerow([sim_time, axis_x, axis_y, axis_right_y])

        if sim_time > 2:
            try:
                if 'prev_control_command' in locals():
                    initial_guess = prev_control_command
                else:
                    initial_guess = np.array([
                        np.arctan2(desired_position[1], desired_position[0]),
                        math.pi / 2,
                        0.0,
                        0.0,
                    ])
                final_theta = IK_solver.inverse_kinematics_solver(desired_position, initial_guess)

                gripper.rotate_motor(gripper.motor_base_shoulder, final_theta[0])
                gripper.rotate_motor(gripper.motor_shoulder_biceps, final_theta[1])
                gripper.rotate_motor(gripper.motor_biceps_elbow, final_theta[2])
                gripper.rotate_motor(gripper.motor_elbow_wrist, final_theta[3])
                prev_control_command = final_theta

                joint_angles_writer.writerow([sim_time, final_theta[0], final_theta[1], final_theta[2], final_theta[3]])

                last_joint_angles = np.array(final_theta, dtype=np.float32)

            except ValueError:
                pass

        actions_hist.append(np.array([axis_x, axis_y, axis_right_y], dtype=np.float32))
        joints_hist.append(last_joint_angles.copy())
        if world_model_runner is not None:
            world_model_runner.maybe_launch(sim_time, actions_hist, joints_hist)

    step_number += 1

csv_file.close()
joint_angles_file.close()

if True:
    pygame.joystick.quit()
pygame.quit()
