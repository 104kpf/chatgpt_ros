#!/usr/bin/env python3
import rospy
from std_msgs.msg import String

def chatgpt_publisher():
    pub = rospy.Publisher('chatgpt_topic', String, queue_size=10)
    rospy.init_node('chatgpt_node', anonymous=True)
    rate = rospy.Rate(10)  # 10hz
    while not rospy.is_shutdown():
        hello_str = "Hello from ChatGPT at %s" % rospy.get_time()
        rospy.loginfo(hello_str)
        pub.publish(hello_str)
        rate.sleep()

if __name__ == '__main__':
    try:
        chatgpt_publisher()
    except rospy.ROSInterruptException:
        pass
