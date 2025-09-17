import pychrono as chrono
import pychrono.irrlicht as chronoirr
import math
import os
import time

class RobotiqGripper:
    def __init__(self, system, pos):
        self.system = system
        self._set_data_dir()
        self._initialize(pos)
        self.rotate_motor(self.motor_base_shoulder, 0)
        self.rotate_motor(self.motor_shoulder_biceps, 0)
        self.rotate_motor(self.motor_biceps_elbow, 0)
        self.rotate_motor(self.motor_elbow_wrist, 0)
        self.rotate_motor(self.motor_wrist_endoffactor, 0)
        # self._setup_locks()

    def _set_data_dir(self):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the data folder
        self.data_dir = os.path.join(script_dir, '..', 'data/robot_assembly')
        # Normalize the path
        self.data_dir = os.path.normpath(self.data_dir)

    def _initialize(self, pos):
        filepath = os.path.join(self.data_dir, 'robot_arm_gripper.py')
        imported_items = chrono.ImportSolidWorksSystem(filepath)
        for ii in imported_items:
            self.system.Add(ii)

        # name each of assembly items
        self.base = self.system.SearchBody("base-1")
        self.biceps = self.system.SearchBody("biceps-1")
        self.elbow = self.system.SearchBody("elbow-1")
        self.shoulder = self.system.SearchBody("shoulder-1")
        self.endoffactor = self.system.SearchBody("endoffactor-1")  # ----
        self.wrist = self.system.SearchBody("wrist-1")
        self.finger_1 = self.system.SearchBody("finger_1-1")
        self.finger_2 = self.system.SearchBody("finger_2-1")

        # set colors for each body part
        self.base.GetVisualShape(0).SetColor(chrono.ChColor(0.8, 0.1, 0.1))
        self.biceps.GetVisualShape(0).SetColor(chrono.ChColor(0.1, 0.8, 0.1))
        self.elbow.GetVisualShape(0).SetColor(chrono.ChColor(0.1, 0.1, 0.8))
        self.shoulder.GetVisualShape(0).SetColor(chrono.ChColor(0.8, 0.8, 0.1))
        self.endoffactor.GetVisualShape(0).SetColor(chrono.ChColor(0.8, 0.1, 0.8))
        self.wrist.GetVisualShape(0).SetColor(chrono.ChColor(0.1, 0.8, 0.8))
        self.finger_1.GetVisualShape(0).SetColor(chrono.ChColor(0.5, 0.5, 0.5))
        self.finger_2.GetVisualShape(0).SetColor(chrono.ChColor(0.5, 0.5, 0.5))

        self.wrist.EnableCollision(True)

        # create name for each marker
        self.joint_base_shoulder = self.system.SearchMarker("MARKER_1")
        self.joint_shoulder_biceps = self.system.SearchMarker("MARKER_2")
        self.joint_biceps_elbow = self.system.SearchMarker("MARKER_3")
        self.joint_elbow_wrist = self.system.SearchMarker("MARKER_4")
        self.joint_wrist_endoffactor = self.system.SearchMarker("MARKER_5")
        self.joint_endoffactor_finger = self.system.SearchMarker("MARKER_6")

        # Adding motors to the marker place
        self.motor_base_shoulder = chrono.ChLinkMotorRotationAngle()
        self.motor_base_shoulder.Initialize(self.base, self.shoulder, chrono.ChFramed(self.joint_base_shoulder.GetPos(), self.joint_base_shoulder.GetRot()))
        self.system.Add(self.motor_base_shoulder)

        self.motor_shoulder_biceps = chrono.ChLinkMotorRotationAngle()
        frame = chrono.ChFramed(self.joint_shoulder_biceps.GetPos(), self.joint_shoulder_biceps.GetRot())
        self.motor_shoulder_biceps.Initialize(self.shoulder, self.biceps, frame)
        self.system.Add(self.motor_shoulder_biceps)

        self.motor_biceps_elbow = chrono.ChLinkMotorRotationAngle()
        self.motor_biceps_elbow.Initialize(self.biceps, self.elbow, chrono.ChFramed(self.joint_biceps_elbow.GetPos(), self.joint_biceps_elbow.GetRot()))
        self.system.Add(self.motor_biceps_elbow)

        self.motor_elbow_wrist = chrono.ChLinkMotorRotationAngle()
        self.motor_elbow_wrist.Initialize(self.elbow, self.wrist, chrono.ChFramed(self.joint_elbow_wrist.GetPos(), self.joint_elbow_wrist.GetRot()))
        self.system.Add(self.motor_elbow_wrist)

        self.motor_wrist_endoffactor = chrono.ChLinkMotorRotationAngle()
        self.motor_wrist_endoffactor.Initialize(self.wrist, self.endoffactor, chrono.ChFramed(self.joint_wrist_endoffactor.GetPos(), self.joint_wrist_endoffactor.GetRot()))
        self.system.Add(self.motor_wrist_endoffactor)

        self.motor_endoffactor_finger_1 = chrono.ChLinkMotorLinearPosition()
        self.motor_endoffactor_finger_1.Initialize(self.endoffactor, self.finger_1, chrono.ChFramed(self.joint_endoffactor_finger.GetPos(), self.joint_endoffactor_finger.GetRot()))
        self.system.Add(self.motor_endoffactor_finger_1)

        self.motor_endoffactor_finger_2 = chrono.ChLinkMotorLinearPosition()
        self.motor_endoffactor_finger_2.Initialize(self.endoffactor, self.finger_2, chrono.ChFramed(self.joint_endoffactor_finger.GetPos(), self.joint_endoffactor_finger.GetRot()))
        self.system.Add(self.motor_endoffactor_finger_2)

        # # # Set the position of the robot
        # self.base.SetPos(pos)
        # self.shoulder.SetPos(pos)
        # self.biceps.SetPos(pos)
        # self.elbow.SetPos(pos)
        # self.wrist.SetPos(pos)
        # self.endoffactor.SetPos(pos)
        # self.finger_1.SetPos(pos)
        # self.finger_2.SetPos(pos)

        # self.joint_base_shoulder.SetPos(pos)
        # self.joint_shoulder_biceps.SetPos(pos)
        # self.joint_biceps_elbow.SetPos(pos)
        # self.joint_elbow_wrist.SetPos(pos)
        # self.joint_wrist_endoffactor.SetPos(pos)
        # self.joint_endoffactor_finger.SetPos(pos)

        self.objects = list()
        self.gripper_on = False
        self.cur_lock = None
        self.cur_object = None
        self.object_contact_count = None
        self.left_motor_val = 0.058
        self.right_motor_val = 0.058
        self.motor_val = 0.058

        self.gripper_left_or_right = True
        self.flag = False
        self.lock_flag = False

        
    def rotate_motor(self, motor, angle):
        if motor==self.motor_base_shoulder:
            motor.SetAngleFunction(chrono.ChFunctionConst(-0.85 - angle))
        elif motor==self.motor_shoulder_biceps:
            motor.SetAngleFunction(chrono.ChFunctionConst(-1.75 + math.pi/2 - angle))
        elif motor==self.motor_biceps_elbow:
            motor.SetAngleFunction(chrono.ChFunctionConst(1.84 - angle))
        elif motor==self.motor_elbow_wrist:
            motor.SetAngleFunction(chrono.ChFunctionConst(0.25 - angle))
        elif motor==self.motor_wrist_endoffactor:
            motor.SetAngleFunction(chrono.ChFunctionConst(angle))

    def move_linear_motor(self, motor, pos):
        motor.SetMotionFunction(chrono.ChFunctionConst(pos))


    def add_object(self, object_name):
        self.objects.append(object_name)

    def add_lock(self):
        if not self.cur_lock:
            for object_name in self.objects:
                object = self.system.SearchBody(object_name)
                dist_1 = (object.GetPos() - self.finger_1.GetPos()).Length()
                dist_2 = (object.GetPos() - self.finger_2.GetPos()).Length()
                print(dist_1, dist_2)
                # if dist_1 < 0.25 and dist_2 < 0.25:
                if True:
                    # print(object.GetName())
                    lock = chrono.ChLinkLockLock()
                    lock.SetName('lock' + object.GetName())
                    lock.Initialize(self.endoffactor, object, chrono.ChFramed())
                    print("lock added")
                    self.system.Add(lock)
                    self.cur_lock = lock.GetName()
                    self.cur_object = object.GetName()
                    # print(self.cur_object)
                    self.gripper_on = True
                    object.EnableCollision(False)

    def remove_lock(self):
        self.system.RemoveLink(self.system.SearchLink(self.cur_lock))
        self.cur_lock = None
        self.system.SearchBody(self.cur_object).EnableCollision(True)
        self.cur_object = None
        self.gripper_on = False
        print("lock removed")
    
    def open(self):
        self.left_motor_val = 0.058
        self.right_motor_val = 0.058
        self.move_linear_motor(self.motor_endoffactor_finger_1, -self.left_motor_val)
        self.move_linear_motor(self.motor_endoffactor_finger_2, self.right_motor_val)
        self.gripper_on = False
        #if self.cur_lock:
        #    self.remove_lock()
    
    def close(self):
        self.move_linear_motor(self.motor_endoffactor_finger_1, -0.03)
        self.move_linear_motor(self.motor_endoffactor_finger_2, 0.03)
        # self.object_contact_check()

    def grab_object(self):
        # print("before: ",  self.system.GetNumContacts(), self.object_contact_count)
        if not self.object_contact_count:
                self.object_contact_count = self.system.GetNumContacts()
                # self.system.SearchBody("blue_ball").SetFixed(True)
                # self.system.SearchBody("blue_ball").EnableCollision(False)

        if self.flag == False and self.object_contact_count + 1 <= self.system.GetNumContacts():
            self.object_contact_count = self.system.GetNumContacts()
            self.flag = True
            # print("here", self.object_contact_count)
        if not self.gripper_on:
            if not self.object_contact_count:
                self.object_contact_count = self.system.GetNumContacts()

            if not self.flag and self.object_contact_count + 1 > self.system.GetNumContacts():
                # print("before: ",  self.system.GetNumContacts())
                if self.gripper_left_or_right:
                    self.left_motor_val -= 0.001
                    self.move_linear_motor(self.motor_endoffactor_finger_1, -(self.left_motor_val))
                    self.gripper_left_or_right = False
                else:
                    self.right_motor_val -= 0.001
                    self.move_linear_motor(self.motor_endoffactor_finger_2, (self.right_motor_val))
                    self.gripper_left_or_right = True
                # self.object_contact_count = self.system.GetNumContacts()
                # self.flag = True
                # print("here1", self.object_contact_count)
                # print(self.object_contact_count)
            elif self.flag and self.object_contact_count + 1 > self.system.GetNumContacts():
                # self.right_motor_val -= 0.001
                # self.move_linear_motor(self.motor_endoffactor_finger_2, (self.right_motor_val))

                if self.gripper_left_or_right:
                    self.left_motor_val -= 0.001
                    self.move_linear_motor(self.motor_endoffactor_finger_1, -(self.left_motor_val))
                    # self.gripper_left_or_right = False
                else:
                    self.right_motor_val -= 0.001
                    self.move_linear_motor(self.motor_endoffactor_finger_2, (self.right_motor_val))
                    # self.gripper_left_or_right = True


                # print("here 2")
            else:
                # print("here3", self.system.GetNumContacts(), self.object_contact_count)
                # self.left_motor_val -= 0.005
                # self.move_linear_motor(self.motor_endoffactor_finger_1, -(self.left_motor_val))
                # self.right_motor_val -= 0.005
                # self.move_linear_motor(self.motor_endoffactor_finger_2, (self.right_motor_val))
                # self.system.SearchBody("blue_ball").SetFixed(False)
                
                #self.add_lock()
                self.object_contact_count = None
                # self.gripper_on = True

        
class RobotMoveo:
    def __init__(self, system, pos):
        self.system = system
        self._set_data_dir()
        self._initialize(pos)
        
        self.rotate_motor(self.motor_base_shoulder, 0)
        # self.rotate_motor(self.motor_shoulder_biceps, 0)
        # self.rotate_motor(self.motor_biceps_elbow, 0)
        # self.rotate_motor(self.motor_elbow_eef, 0)
        
        # self._setup_locks()

    def _set_data_dir(self):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the data folder
        self.data_dir = os.path.join(script_dir, '..', 'data/robot_assembly')
        # Normalize the path
        self.data_dir = os.path.normpath(self.data_dir)

    def _initialize(self, pos):
        filepath = os.path.join(self.data_dir, 'moveo_arm.py')
        imported_items = chrono.ImportSolidWorksSystem(filepath)
        for ii in imported_items:
            self.system.Add(ii)

        # name each of assembly items
        self.base = self.system.SearchBody("base")
        self.biceps = self.system.SearchBody("bicep")
        self.elbow = self.system.SearchBody("elbow")
        self.shoulder = self.system.SearchBody("shoulder")
        self.endoffactor = self.system.SearchBody("endeffector")  # ----
        self.finger_1 = self.system.SearchBody("finger-1")
        self.finger_2 = self.system.SearchBody("finger-2")

        # Add NSC contact materials to gripper fingers
        #if self.system.GetContactMethod() == chrono.ChContactMethod_NSC:
            # Create NSC contact material
        #    finger_material = chrono.ChContactMaterialNSC()
        #    finger_material.SetFriction(0.8)
        ##    finger_material.SetRestitution(0.1)
        #    finger_material.SetYoungModulus(2e8)
        #    finger_material.SetPoissonRatio(0.3)
            
            # Apply material to all robot bodies, especially fingers
        #    robot_bodies = [self.base, self.biceps, self.elbow, self.shoulder, 
        #                self.endoffactor, self.wrist, self.finger_1, self.finger_2]
            
        #    for body in robot_bodies:
        #        if body:
        #            # Get existing collision shapes and update their material
        #            for i in range(body.GetCollisionModel().GetNumShapes()):
        #                shape = body.GetCollisionModel().GetShape(i)
        #                if hasattr(shape, 'SetMaterial'):
        #                    shape.SetMaterial(finger_material)
                    
        #            # Enable collision for fingers specifically
        #            if body == self.finger_1 or body == self.finger_2:
        #                body.EnableCollision(True)


        # create name for each marker
        self.joint_base_shoulder = self.system.SearchMarker("base_shoulder")
        self.joint_shoulder_biceps = self.system.SearchMarker("shoulder_bicep")
        self.joint_biceps_elbow = self.system.SearchMarker("bicep_elbow")
        self.joint_elbow_eff = self.system.SearchMarker("elbow_eef")
        self.joint_endoffactor_finger = self.system.SearchMarker("eef_fingers")

        # Adding motors to the marker place
        self.motor_base_shoulder = chrono.ChLinkMotorRotationAngle()
        self.motor_base_shoulder.Initialize(self.base, self.shoulder, chrono.ChFramed(self.joint_base_shoulder.GetPos(), self.joint_base_shoulder.GetRot()))
        self.system.Add(self.motor_base_shoulder)

        self.motor_shoulder_biceps = chrono.ChLinkMotorRotationAngle()
        frame = chrono.ChFramed(self.joint_shoulder_biceps.GetPos(), self.joint_shoulder_biceps.GetRot())
        self.motor_shoulder_biceps.Initialize(self.shoulder, self.biceps, frame)
        self.system.Add(self.motor_shoulder_biceps)

        self.motor_biceps_elbow = chrono.ChLinkMotorRotationAngle()
        self.motor_biceps_elbow.Initialize(self.biceps, self.elbow, chrono.ChFramed(self.joint_biceps_elbow.GetPos(), self.joint_biceps_elbow.GetRot()))
        self.system.Add(self.motor_biceps_elbow)

        self.motor_elbow_eef = chrono.ChLinkMotorRotationAngle()
        self.motor_elbow_eef.Initialize(self.elbow, self.endoffactor, chrono.ChFramed(self.joint_elbow_eff.GetPos(), self.joint_elbow_eff.GetRot()))
        self.system.Add(self.motor_elbow_eef)

        # self.motor_wrist_endoffactor = chrono.ChLinkMotorRotationAngle()
        # self.motor_wrist_endoffactor.Initialize(self.wrist, self.endoffactor, chrono.ChFramed(self.joint_wrist_endoffactor.GetPos(), self.joint_wrist_endoffactor.GetRot()))
        # self.system.Add(self.motor_wrist_endoffactor)

        self.motor_endoffactor_finger_1 = chrono.ChLinkMotorLinearPosition()
        self.motor_endoffactor_finger_1.Initialize(self.endoffactor, self.finger_1, chrono.ChFramed(self.joint_endoffactor_finger.GetPos(), self.joint_endoffactor_finger.GetRot()))
        self.system.Add(self.motor_endoffactor_finger_1)

        self.motor_endoffactor_finger_2 = chrono.ChLinkMotorLinearPosition()
        self.motor_endoffactor_finger_2.Initialize(self.endoffactor, self.finger_2, chrono.ChFramed(self.joint_endoffactor_finger.GetPos(), self.joint_endoffactor_finger.GetRot()))
        self.system.Add(self.motor_endoffactor_finger_2)

        # # # Set the position of the robot
        # offset = chrono.ChVector3d(0.0,0.8869/2,0.0)
        # pos = pos + offset
        print(pos)
        self.base.SetFixed(False)
        self.base.SetPos(pos)
        self.shoulder.SetPos(pos)
        self.biceps.SetPos(pos)
        self.elbow.SetPos(pos)
        self.endoffactor.SetPos(pos)
        self.finger_1.SetPos(pos)
        self.finger_2.SetPos(pos)

        self.joint_base_shoulder.SetPos(pos)
        self.joint_shoulder_biceps.SetPos(pos)
        self.joint_biceps_elbow.SetPos(pos)
        self.joint_elbow_eff.SetPos(pos)
        self.joint_endoffactor_finger.SetPos(pos)
        self.base.SetFixed(True)
        # self.finger_1.EnableCollision(True)
        # self.finger_2.EnableCollision(True)

        self.objects = list()
        self.gripper_on = False
        self.cur_lock = None
        self.cur_object = None
        self.object_contact_count = None
        self.motor_val = 0.058
        self.gripper_left_or_right = True

        
    def rotate_motor(self, motor, angle):
        if motor==self.motor_base_shoulder:
            motor.SetAngleFunction(chrono.ChFunctionConst(-2.175 - angle))
        elif motor==self.motor_shoulder_biceps:
            motor.SetAngleFunction(chrono.ChFunctionConst(-1.75 + math.pi/2 - angle))
        elif motor==self.motor_biceps_elbow:
            motor.SetAngleFunction(chrono.ChFunctionConst(1.84 - angle))
        elif motor==self.motor_elbow_eef:
            motor.SetAngleFunction(chrono.ChFunctionConst(0.25 - angle))
     

    def move_linear_motor(self, motor, pos):
        motor.SetMotionFunction(chrono.ChFunctionConst(pos))
