#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist

pub = None

def callback(data):
    rospy.loginfo("Received: %s", data.data)
    
    try:
        command = json.loads(data.data)
        print(command)
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
    print(rotations)
    twist.linear.x = 0
    # for current_rot in rotations:
    #     rospy.loginfo("Moving turtle")
    #     twist.linear.x = command["speed"]
    #     twist.linear.y = 0
    #     pub.publish(twist)
    #     time_to_move = command["side_length"] / command["speed"]
    #     rospy.sleep(time_to_move)
    #     twist.linear.x = 0
        
    #     angular_speed = 2
    #     pub.publish(twist)
    #     rospy.loginfo("Rotating turtle")
        
    #     t0 = rospy.Time.now().to_sec()
    #     ang_travelled = 0
    #     while(ang_travelled < 3.141592/2):
    #         twist.angular.z = angular_speed
    #         t1 = rospy.Time.now().to_sec()
    #         ang_travelled = angular_speed*(t1-t0)
        
    #     pub.publish(twist)
    #     twist.angular.z = 0
    #     current_rot += 0.25



def listener():
    global pub
    rospy.init_node('control_listener', anonymous=True)
    # 初始化发布者
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
    # 订阅 gpt_reply_to_user 话题
    rospy.Subscriber("gpt_reply_to_user", String, callback)
    rospy.spin()

if __name__ == '__main__':
    listener()

