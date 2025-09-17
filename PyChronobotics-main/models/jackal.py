#------------------------------------------------------------------------------
# Name:        pychrono example
# Purpose:
#
# Author:      Harry Zhang
#
# Created:     03/09/2024
# Copyright:   (c) ProjectChrono 2019
#------------------------------------------------------------------------------
 
 
import pychrono as chrono
import pychrono.irrlicht as chronoirr
import pychrono.vehicle as veh
import math
import os

class Jackal:
    def __init__(self, system):
        self.system = system
        self.chassis = None
        self.wheels = {}
        self.motors = {}
        self.steering_motors = {}

        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to the data folder
        self.data_dir = os.path.join(script_dir, '..', 'data/robot_assembly')

        # Normalize the path
        self.data_dir = os.path.normpath(self.data_dir)

        self._load_model()
        self._setup_wheels()
        self._setup_motors()

    def _load_model(self):
        print("Loading Jackal model...")
        exported_items = chrono.ImportSolidWorksSystem(os.path.join(self.data_dir, 'Jackal_1.py'))
        for item in exported_items:
            self.system.Add(item)
        print("...done!")

    def _setup_wheels(self):
        material = chrono.ChContactMaterialNSC()
        
        self.chassis = self.system.SearchBody('Part15-1')
        wheel_names = ['fr', 'fl', 'br', 'bl']
        part_numbers = ['16-1', '16-5', '16-2', '16-6']

        for name, part in zip(wheel_names, part_numbers):
            wheel = self.system.SearchBody(f'Part{part}')
            
            # Create cylinder shape for collision
            radius = 0.1  # Adjust this value to match your wheel's radius
            width = 0.06  # Adjust this value to match your wheel's width
            
            cylinder = chrono.ChCollisionShapeCylinder(material, radius, width)
            
            # The cylinder's axis is along Y by default, so we need to rotate it
            rotation = chrono.Q_ROTATE_X_TO_Y
            cylinder_pos = chrono.ChVector3d(0, 0, 0)  # Adjust if the cylinder needs to be offset
            
            wheel.AddCollisionShape(cylinder, chrono.ChFramed(cylinder_pos, rotation))
            wheel.EnableCollision(True)
            self.wheels[name] = wheel

    def _setup_motors(self):
        # Setup drive motors
        self.motors['br'] = chrono.ChLinkMotorRotationSpeed()
        self.motors['bl'] = chrono.ChLinkMotorRotationSpeed()
        self.motors['fr'] = chrono.ChLinkMotorRotationSpeed()
        self.motors['fl'] = chrono.ChLinkMotorRotationSpeed()

        # Initialize motors
        for wheel in ['fr', 'fl', 'br', 'bl']:
            joint = self.system.SearchLink(f'Concentric{1 if wheel == "fr" else 4 if wheel == "fl" else 2 if wheel == "br" else 3}')
            frame = joint.GetVisualModelFrame()

            self.motors[wheel].Initialize(self.chassis, self.wheels[wheel], frame)
            self.system.Add(self.motors[wheel])

    def control(self, speed=1, steering=0):
        linear_to_angular_velocity = speed / 0.1
        # set motor velocity function based on speed and skid steering
        wheel_motor_func1 = chrono.ChFunctionConst(-linear_to_angular_velocity * (1 - steering))
        wheel_motor_func2 = chrono.ChFunctionConst(linear_to_angular_velocity * (1 + steering))
        
        self.motors['fr'].SetMotorFunction(wheel_motor_func1)
        self.motors['fl'].SetMotorFunction(wheel_motor_func2)
        self.motors['br'].SetMotorFunction(wheel_motor_func1)
        self.motors['bl'].SetMotorFunction(wheel_motor_func2)
    

