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

        # 处理命令
        handle_action(command)
    except json.JSONDecodeError as e:
        rospy.logerr("Error decoding JSON: %s", e)
    except KeyError as e:
        rospy.logerr("Missing key in JSON data: %s", e)

def handle_action(command):
    global pub
    twist = Twist()
    
    if command["action"] == "move":
        rospy.loginfo("Moving turtle")
        # 使用新的JSON格式设置线速度和角速度
        twist.linear.x = command["speed"]["linear"]["x"]
        twist.linear.y = 0
        # 默认情况下, y速度应该为0, 因此这不需要改变
        
        # 发布 Twist 消息以开始移动
        pub.publish(twist)
        
        # 根据速度和距离计算需要移动的时间
        time_to_move = command["distance"] / command["speed"]["linear"]["x"]
        
        # 等待直到移动完成
        rospy.sleep(time_to_move)
        
        # 停止移动
        twist.linear.x = 0
        pub.publish(twist)
        
        # 停止后开始旋转
        rospy.loginfo("Rotating turtle")
        twist.angular.z = command["angular_speed"]["angular"]["z"]
        pub.publish(twist)
        
        # 旋转需要的时间或其他逻辑（如果需要）根据您的需求进行处理

    else:
        rospy.logerr("Unknown action: %s", command.get("action"))

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

