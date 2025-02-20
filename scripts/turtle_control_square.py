#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import math

pub = None

def callback(data):
    rospy.loginfo("Received: %s", data.data)
    
    try:
        command = json.loads(data.data)
        while command["stop"]==0:
            handle_action(command)
        
    except json.JSONDecodeError as e:
        rospy.logerr("Error decoding JSON: %s", e)
    except KeyError as e:
        rospy.logerr("Missing key in JSON data: %s", e)

def handle_action(command):
    global pub
    twist = Twist()
    rotations = command["rotations"]
    current_rot = 0
    twist.linear.x = 0
    while current_rot < rotations:
        move_line(command,twist)
        rotate(twist)
        current_rot += 0.25
        
def rotate(twist):
    rospy.loginfo("Rotating turtle")
    angular_speed = 1
    t0 = rospy.Time.now().to_sec()
    ang_travelled = 0
    while(ang_travelled < math.pi/2):
        twist.linear.x = 0
        twist.angular.z = angular_speed
        pub.publish(twist)
        t1 = rospy.Time.now().to_sec()
        ang_travelled = angular_speed*(t1-t0)
    
    twist.angular.z = 0
    pub.publish(twist)


def move_line(command,twist):
    rospy.loginfo("Moving turtle")
    twist.linear.x = command["speed"]
    twist.linear.y = 0
    twist.linear.z = 0
    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = 0
    t0 = rospy.Time.now().to_sec()
    dist_travelled = 0
    while(dist_travelled < command["side_length"]):
        pub.publish(twist)
        t1 = rospy.Time.now().to_sec()
        dist_travelled = command["speed"]*(t1-t0)
    twist.angular.z = 0
    pub.publish(twist)




def listener():
    global pub
    rospy.init_node('control_listener', anonymous=True)
    
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    
    rospy.Subscriber("gpt_reply_to_user", String, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()

