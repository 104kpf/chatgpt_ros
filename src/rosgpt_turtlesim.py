#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
import httpx

# =======================
# OpenAI (Azure) Configuration
# =======================
# Replace these values with your own settings.
api_key = "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"  # Your API key
api_base = "https://models.inference.ai.azure.com"  # Your Azure endpoint
deployment_id = "gpt-4o"  # Your deployment/model name
api_version = "2023-03-15-preview"  # API version

# Create an HTTPX client with the specified base URL
http_client = httpx.Client(
    base_url=api_base,
    follow_redirects=True,
)

def get_chat_completion(messages, model=deployment_id):
    """
    Send a chat completion request to the Azure OpenAI endpoint using httpx.
    """
    # Construct the URL for chat completions (Azure OpenAI style)
    url = f"/openai/deployments/{deployment_id}/chat/completions?api-version={api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }
    payload = {
        "model": model,
        "messages": messages,
    }
    response = http_client.post(url, headers=headers, json=payload)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    return response.json()

def user_message_callback(data):
    rospy.loginfo("Received from user: %s", data.data)
    messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful ROS assistant specifically for controlling a TurtleBot. "
            "Please provide responses in the following JSON format for a combination of moving forward "
            "and then rotating in place:\n\n"
            "{\n"
            "  \"action\": \"move\",\n"
            "  \"speed\": {\n"
            "    \"linear\": {\n"
            "      \"x\": [linear speed value for moving forward or backward],\n"
            "      \"y\": 0\n"
            "    },\n"
            "    \"angular\": {\n"
            "      \"x\": 0,\n"
            "      \"y\": 0\n"
            "    }\n"
            "  },\n"
            "  \"distance\": [distance value],\n"
            "  \"angular_speed\": {\n"
            "    \"linear\": {\n"
            "      \"x\": [value]\n"
            "    },\n"
            "    \"angular\": {\n"
            "      \"z\": [angular speed value for rotation]\n"
            "    }\n"
            "  }\n"
            "}\n\n"
            "The 'speed' value controls the linear speed for moving forward or backward (use positive values "
            "for forward movement and negative values for backward movement). The 'distance' specifies how far "
            "to move before rotating. The 'angular_speed' controls the angular velocity for rotating in place "
            "after moving (use positive values for left turns and negative values for right turns).\n\n"
            "Please provide only a plain JSON object without any markdown formatting"
        )
    },
    {
        "role": "user",
        "content": data.data
    }
]

    try:
        chat_completion = get_chat_completion(messages)
        # Extract GPT's reply from the response
        gpt_reply = chat_completion["choices"][0]["message"]["content"]
        rospy.loginfo("GPT Reply: %s", gpt_reply)
        gpt_reply_pub.publish(gpt_reply)
    except Exception as e:
        rospy.logerr("Error during chat completion: %s", e)

if __name__ == '__main__':
    try:
        rospy.init_node('chatgpt_ros_node', anonymous=True)
        # Subscribe to user messages
        rospy.Subscriber("user_to_gpt", String, user_message_callback)
        # Publisher for GPT replies
        gpt_reply_pub = rospy.Publisher("gpt_reply_to_user", String, queue_size=10)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
