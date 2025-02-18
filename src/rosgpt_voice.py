#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
import httpx

# =======================
# OpenAI (Azure) Configuration
# =======================
# Replace these values with your own settings.
api_key = "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"
api_base = "https://models.inference.ai.azure.com"  
deployment_id = "gpt-4o"  
api_version = "2023-03-15-preview"  

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
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": data.data}
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
