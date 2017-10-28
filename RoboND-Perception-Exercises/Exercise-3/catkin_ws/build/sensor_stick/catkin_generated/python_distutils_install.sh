#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
    DESTDIR_ARG="--root=$DESTDIR"
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/src/sensor_stick"

# snsure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/install/lib/python2.7/dist-packages:/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/build" \
    "/usr/bin/python" \
    "/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/src/sensor_stick/setup.py" \
    build --build-base "/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/build/sensor_stick" \
    install \
    $DESTDIR_ARG \
    --install-layout=deb --prefix="/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/install" --install-scripts="/home/robond/Robotics_Udacity_NanoDegree/RoboND-Perception-Exercises/Exercise-3/catkin_ws/install/bin"
