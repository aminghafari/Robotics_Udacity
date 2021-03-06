#!/usr/bin/env python

# Copyright (C) 2017 Electric Movement Inc.
#
# This file is part of Robotic Arm: Pick and Place project for Udacity
# Robotics nano-degree program
#
# All Rights Reserved.

# Author: Harsh Pandya
# Modified by Amin Ghafari OCt 2017

# import modules
import rospy
import tf
from kuka_arm.srv import *
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Pose
from mpmath import *
from sympy import *


def handle_calculate_IK(req):
    rospy.loginfo("Received %s eef-poses from the plan" % len(req.poses))
    if len(req.poses) < 1:
        print "No valid poses received"
        return -1
    else:
		
        ### Your FK code here
        # Create symbols
	q1, q2, q3, q4, q5, q6, q7 = symbols('q1:8')
        d1, d2, d3, d4, d5, d6, d7 = symbols('d1:8')
        a0, a1, a2, a3, a4, a5, a6 = symbols('a0:7')
        alpha0, alpha1, alpha2, alpha3, alpha4, alpha5, alpha6 = symbols('alpha0:7')
        #   
        # Create Modified DH parameters
        s = {alpha0:      0, a0:     0, d1: 0.75,
             alpha1: -pi/2., a1:  0.35, d2:    0, q2: q2-pi/2.,
             alpha2:      0, a2:  1.25, d3:    0,
             alpha3: -pi/2., a3:-0.054, d4:  1.5,
             alpha4:   pi/2, a4:     0, d5:    0,
            alpha5: -pi/2., a5:     0, d6:    0,
            alpha6:      0, a6:     0, d7: 0.303, q7: 0}
        #            
        # Define Modified DH Transformation matrix
        #
        # a function for the matrix
        def T_Mat(q, d, a, alpha):
            T = Matrix([[            cos(q),           -sin(q),           0,             a],
                        [ sin(q)*cos(alpha), cos(q)*cos(alpha), -sin(alpha), -sin(alpha)*d],
                        [ sin(q)*sin(alpha), cos(q)*sin(alpha),  cos(alpha),  cos(alpha)*d],
                        [                 0,                 0,           0,             1]])

            return T


        #
        # Create individual transformation matrices
        T0_1 = T_Mat(q1, d1, a0, alpha0).subs(s)
        T1_2 = T_Mat(q2, d2, a1, alpha1).subs(s)
        T2_3 = T_Mat(q3, d3, a2, alpha2).subs(s)
        T3_4 = T_Mat(q4, d4, a3, alpha3).subs(s)
        T4_5 = T_Mat(q5, d5, a4, alpha4).subs(s)
        T5_6 = T_Mat(q6, d6, a5, alpha5).subs(s)
        T6_G = T_Mat(q7, d7, a6, alpha6).subs(s)
        #
        #
        T0_G = T0_1 * T1_2 * T2_3 * T3_4 * T4_5 * T5_6 * T6_G
        ###

        ### Part of IK
        # Rotation matrices for roll pitch and yaw angles
        rx, ry, rz = symbols('rx ry rz')
        R_x = Matrix([[       1,        0,        0],
                      [       0,  cos(rx), -sin(rx),],
                      [       0,  sin(rx),  cos(rx),]])

        R_y = Matrix([[  cos(ry),        0, sin(ry)],
                      [        0,        1,       0],
                      [ -sin(ry),        0, cos(ry)]])

        R_z = Matrix([[ cos(rz), -sin(rz),        0],
                      [ sin(rz),  cos(rz),        0],
                      [       0,        0,        1]])

        # Compensate for rotation discrepancy between DH parameters and Gazebo
        R_corr = R_z.subs(rz, radians(180))*R_y.subs(ry, -radians(90))

        # Rotation matrix as a function of roll, pitch and yaw angle from the calculations
        R_E = R_z*R_y*R_x*R_corr

        # Initialize service response
        joint_trajectory_list = []
        for x in xrange(0, len(req.poses)):
            # IK code starts here
            joint_trajectory_point = JointTrajectoryPoint()

	    # Extract end-effector position and orientation from request
	    # px,py,pz = end-effector position
	    # roll, pitch, yaw = end-effector orientation
            px = req.poses[x].position.x
            py = req.poses[x].position.y
            pz = req.poses[x].position.z

            (roll, pitch, yaw) = tf.transformations.euler_from_quaternion(
                [req.poses[x].orientation.x, req.poses[x].orientation.y,
                    req.poses[x].orientation.z, req.poses[x].orientation.w])
     
            ### Your IK code here 
	    # Calculating the Gripper rotation from the given angles
            R_E = R_E.subs({'rx' : roll, 'ry' : pitch, 'rz': yaw})


            Gr = Matrix([[px],[py],[pz]])
    
            Wr = Gr - 0.303*R_E[:,2]
	    #
	    # Calculate joint angles using Geometric IK method
	    #
	    theta1 = atan2(Wr[1], Wr[0])

            # theta 2 & 3
            # length of the triangle sides
            d_A = 1.5009
            d_B = sqrt( pow( sqrt( pow(Wr[0],2) + pow(Wr[1],2) ) - 0.35 ,2) + pow(Wr[2] - 0.75,2) )
            d_C = 1.25

            # angles of the triangle
            a_A = acos( (d_B*d_B + d_C*d_C - d_A*d_A)/(2*d_B*d_C) )
            a_B = acos( (d_A*d_A + d_C*d_C - d_B*d_B)/(2*d_A*d_C) )
            a_C = acos( (d_B*d_B + d_A*d_A - d_C*d_C)/(2*d_B*d_A) )

            # theta 2 & 3
            theta2 = pi/2 - a_A - atan2(Wr[2]-0.75, sqrt( pow(Wr[0],2) + pow(Wr[1],2) ) - 0.35)
            theta3 = pi/2 - a_B - atan2(0.054, 1.5)

            # theta 4-5-6
            # rotation matrix from 3 to the gripper
            R0_3 = T0_1[0:3,0:3] * T1_2[0:3,0:3] * T2_3[0:3,0:3]
            R0_3 = R0_3.evalf(subs={q1 :theta1, q2 : theta2, q3 : theta3})

            R3_6 = R0_3.inv("LU")* R_E

            # find the angles using the euler transformation
            theta4 = atan2(R3_6[2,2], - R3_6[0,2])
            theta5 = atan2(sqrt(R3_6[2,2]*R3_6[2,2] + R3_6[0,2]*R3_6[0,2]), R3_6[1,2])
            theta6 = atan2(-R3_6[1,1], R3_6[1,0])
            ###
		
            # Populate response for the IK request
            # In the next line replace theta1,theta2...,theta6 by your joint angle variables
	    joint_trajectory_point.positions = [theta1, theta2, theta3, theta4, theta5, theta6]
	    joint_trajectory_list.append(joint_trajectory_point)

        rospy.loginfo("length of Joint Trajectory List: %s" % len(joint_trajectory_list))
        return CalculateIKResponse(joint_trajectory_list)


def IK_server():
    # initialize node and declare calculate_ik service
    rospy.init_node('IK_server')
    s = rospy.Service('calculate_ik', CalculateIK, handle_calculate_IK)
    print "Ready to receive an IK request"
    rospy.spin()

if __name__ == "__main__":
    IK_server()
