#!/usr/bin/env python
import rospy
from std_msgs.msg import String

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)

def chatgpt_subscriber():
    rospy.init_node('chatgpt_listener', anonymous=True)
    rospy.Subscriber('chatgpt_topic', String, callback)
    rospy.spin()

if __name__ == '__main__':
    chatgpt_subscriber()
