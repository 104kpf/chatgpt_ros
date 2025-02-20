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
            "你是一個幫助控制 TurtleBot 的 ROS 助手。請根據以下需求產生一個純 JSON 物件，格式中只包含三個參數：\n\n"
            "1. side_length：正方形的邊長，單位為公尺；\n"
            "2. speed：行走速度，單位為單位/秒；\n"
            "3. rotations：正方形路徑的繞行次數。\n\n"
            "請只回傳一個純 JSON 物件，不要附加任何文字或 markdown 格式。\n\n"
            "例如，如果正方形邊長為 2 公尺、速度為 3 單位/秒，且只繞行 1 次，則應回傳：\n"
            "{\"side_length\": 2, \"speed\": 3, \"rotations\": 1}"
            "若無定義速度,邊長,繞行次數,請隨意挑選數字"
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
