#!/usr/bin/env python

# Import modules
from pcl_helper import *

# TODO: Define functions as required

# Callback function for your Point Cloud Subscriber
def pcl_callback(pcl_msg):

    # TODO: Convert ROS msg to PCL data
    pcl_data = ros_to_pcl(pcl_msg)

    # TODO: Voxel Grid Downsampling
    vox = pcl_data.make_voxel_grid_filter()
    LEAF_SIZE = 0.005

    vox.set_leaf_size(LEAF_SIZE,LEAF_SIZE,LEAF_SIZE)
    data_filtered = vox.filter()

    # TODO: PassThrough Filter
    passthrough = data_filtered.make_passthrough_filter()

    filter_axis = 'z'
    passthrough.set_filter_field_name(filter_axis)

    axis_min = 0.6
    axis_max = 1.1

    passthrough.set_filter_limits(axis_min, axis_max)

    data_filtered = passthrough.filter()


    # TODO: RANSAC Plane Segmentation
    seg = data_filtered.make_segmenter()

    seg.set_model_type(pcl.SACMODEL_PLANE)
    seg.set_method_type(pcl.SAC_RANSAC)

    max_distance =0.01
    seg.set_distance_threshold(max_distance)

    inliers , coefficient = seg.segment()

    # TODO: Extract inliers and outliers
    extracted_inlier = data_filtered.extract(inliers, negative = False)
    extracted_outlier = data_filtered.extract(inliers, negative = True)

    # TODO: Euclidean Clustering

    # TODO: Create Cluster-Mask Point Cloud to visualize each cluster separately

    # TODO: Convert PCL data to ROS messages
    ros_inlier = pcl_to_ros(extracted_inlier)
    ros_outlier = pcl_to_ros(extracted_outlier)

    # TODO: Publish ROS messages
    pcl_objects_pub.publish(ros_outlier)
    pcl_table_pub.publish(ros_inlier)


if __name__ == '__main__':

    # TODO: ROS node initialization
    rospy.init_node('clustering', anonymous = True)

    # TODO: Create Subscribers
    pcl_sub = rospy.Subscriber("/sensor_stick/point_cloud", pc2.PointCloud2, pcl_callback, queue_size=1)

    # TODO: Create Publishers
    pcl_objects_pub = rospy.Publisher("/pcl_objects", PointCloud2, queue_size=1)
    pcl_table_pub = rospy.Publisher("/pcl_table", PointCloud2, queue_size=1)

    # Initialize color_list
    get_color_list.color_list = []

    # TODO: Spin while node is not shutdown
    while not rospy.is_shutdown():
        rospy.spin()
