import numpy as np
from scipy.optimize import minimize

class RobotArmInverseKinematicsSolver:
    def __init__(self, robot_type):
        """
        Initialize the robot arm inverse kinematics solver.

        Args:
            robot_type (str): The type of robot arm. Currently supported: 'robotiq-3dof'.
        """
        if robot_type == 'robotiq-3dof':
            self.a1, self.a2, self.a3 , self.d1 = 0.4, 0.358, 0.65, 0.1
        else:
            raise ValueError("Invalid robot type")


    def forward_kinematics(self, theta):
        theta1, theta2, theta3, theta4 = theta
        # Replace these with the actual kinematic equations
        x = self.f1(theta1, theta2, theta3, theta4)
        y = self.f2(theta1, theta2, theta3, theta4)
        z = self.f3(theta1, theta2, theta3, theta4)
        return np.array([x, y, z])


    # Objective function: minimize the error between current and desired positions
    def objective_function(self, theta, target_position):
        # print('theta:', theta)
        current_position = self.forward_kinematics(theta)
        # print('current_position:', current_position)
        error = np.linalg.norm(current_position - target_position)  # Euclidean distance
        return error

   # Example kinematic equations (replace with actual equations)
    def f1(self, theta1, theta2, theta3, theta4):
        s1, s2, s3, s4 = np.sin(theta1), np.sin(theta2), np.sin(theta3), np.sin(theta4)
        c1, c2, c3, c4 = np.cos(theta1), np.cos(theta2), np.cos(theta3), np.cos(theta4)
        return (self.d1*c1 + self.a2*c1*c2 - self.a3*c1*s2*s3 + self.a3*c1*c2*c3 + 
                self.d1*c1*(c2*c3*c4 - s2*s3*c4 - c2*s3*s4 - s2*c3*s4))

    def f2(self, theta1, theta2, theta3, theta4):
        s1, s2, s3, s4 = np.sin(theta1), np.sin(theta2), np.sin(theta3), np.sin(theta4)
        c1, c2, c3, c4 = np.cos(theta1), np.cos(theta2), np.cos(theta3), np.cos(theta4)
        return (self.d1*s1 + self.a2*c2*s1 - self.a3*s1*s2*s3 + self.a3*c2*c3*s1 + 
                self.d1*s1*(c2*c3*c4 - s2*s3*c4 - c2*s3*s4 - s2*c3*s4))

    def f3(self, theta1, theta2, theta3, theta4):
        s1, s2, s3, s4 = np.sin(theta1), np.sin(theta2), np.sin(theta3), np.sin(theta4)
        c1, c2, c3, c4 = np.cos(theta1), np.cos(theta2), np.cos(theta3), np.cos(theta4)
        return (self.a1 + self.a2*s2 + self.a3*c2*s3 + self.a3*c3*s2 + 
                self.d1*(s2*c3*c4 + c2*s3*c4 - s2*s3*s4 + c2*c3*s4))


    # Inverse kinematics solver
    def inverse_kinematics_solver(self, target_position, initial_guess, tolerance=1e-6):
        print("initial guess:", initial_guess)
        result = minimize(self.objective_function, initial_guess, args=(target_position,),
                        method='BFGS', options={'gtol': 1e-8, 'maxiter': 1000})
        
        print('Optimization result:', result)
        
        final_position = self.forward_kinematics(result.x)  # Assuming you have this function
        error = np.linalg.norm(final_position - target_position)
        
        if error <= tolerance:
            print(f"Solution found with error: {error}")
            return result.x
        else:
            print(f"Optimization failed. Message: {result.message}")
            print(f"Final position error: {error}")
            print(f"Number of iterations: {result.nit}")
            print(f"Final position: {final_position}")
            print(f"Target position: {target_position}")
            raise ValueError("Inverse kinematics solver did not converge")

if __name__ == '__main__':
    # Desired position (replace with actual values)
    desired_position = np.array( [ 0.030021, 0.652991, 0.0551759 ])

    # Initial guess for theta1, theta2, theta3
    initial_guess = np.array([np.arctan2(desired_position[1],desired_position[0]), np.pi/2, 0.0, 0.0])

    print("initial guess main:", initial_guess)

    solver = RobotArmInverseKinematicsSolver('robotiq-3dof')
    # Use solver to figure out control angles
    import time
    start_time = time.time()
    final_theta = solver.inverse_kinematics_solver(desired_position, initial_guess)
    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")

    # Output the control angles
    print(f"Control angles (in radians): {final_theta}")

    # Compute the final end-effector position using the optimized angles
    final_position = solver.forward_kinematics(final_theta)
    print(f"Final end-effector position: x = {final_position[0]}, y = {final_position[1]}, z = {final_position[2]}")