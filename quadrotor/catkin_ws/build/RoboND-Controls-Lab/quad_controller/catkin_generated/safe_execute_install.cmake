execute_process(COMMAND "/home/robond/Robotics_Udacity_NanoDegree/quadrotor/catkin_ws/build/RoboND-Controls-Lab/quad_controller/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/robond/Robotics_Udacity_NanoDegree/quadrotor/catkin_ws/build/RoboND-Controls-Lab/quad_controller/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
