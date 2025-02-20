import speech_recognition as sr
import rospy
from std_msgs.msg import String
import httpx
import threading
# obtain audio from the microphone
r = sr.Recognizer()


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
    Sends a chat completion request to the Azure OpenAI endpoint using httpx.
    """
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

def user_message_callback(user_text):
    """
    Sends the recognized text to GPT and publishes the GPT response via ROS.
    """
    rospy.loginfo("Received user input: %s", user_text)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_text}
    ]
    try:
        chat_completion = get_chat_completion(messages)
        # Extract GPT's reply from the response
        gpt_reply = chat_completion["choices"][0]["message"]["content"]
        rospy.loginfo("GPT reply: %s", gpt_reply)
        gpt_reply_pub.publish(gpt_reply)
    except Exception as e:
        rospy.logerr("Error during chat completion: %s", e)

def speech_recognition_loop():
    """
    Continuously performs speech recognition in a separate thread and sends the recognized text to GPT.
    """
    recognizer = sr.Recognizer()
    while not rospy.is_shutdown():
        try:
            with sr.Microphone() as source:
                rospy.loginfo("Please speak...")
                audio = recognizer.listen(source)
            try:
                # Use Sphinx for offline speech recognition (alternatively, you can use Google Speech API, etc.)
                recognized_text  = r.recognize_google(audio, language="en-US")
                rospy.loginfo("Recognized text: %s", recognized_text)
                user_message_callback(recognized_text)
            except sr.UnknownValueError:
                rospy.logwarn("Could not understand the audio")
            except sr.RequestError as e:
                rospy.logerr("Speech recognition error: %s", e)
        except Exception as e:
            rospy.logerr("Error during recording: %s", e)

def main():
    rospy.init_node('chatgpt_ros_node', anonymous=True)
    global gpt_reply_pub
    # Initialize ROS publisher for sending GPT replies
    gpt_reply_pub = rospy.Publisher("gpt_reply_to_user", String, queue_size=10)
    # Optionally, subscribe to other ROS topics if needed
    # rospy.Subscriber("user_to_gpt", String, user_message_callback)

    # Start the speech recognition thread
    sr_thread = threading.Thread(target=speech_recognition_loop)
    sr_thread.daemon = True
    sr_thread.start()

    # Keep the ROS node running
    rospy.spin()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass