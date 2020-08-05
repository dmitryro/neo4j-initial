import os
from slack import RTMClient

@RTMClient.run_on(event="message")
def say_hello(**payload):
  print("Say hello")
  data = payload['data']
  web_client = payload['web_client']

  if 'Hello' in data['text']:
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user'] # This is not username but user ID (the format is either U*** or W***)

    web_client.chat_postMessage(
      channel=channel_id,
      text=f"Hi <@{user}>!",
      thread_ts=thread_ts
    )

#slack_token = os.environ["SLACK_API_TOKEN"]
slack_token = "xoxp-1233156912480-1207944652885-1295111358192-c4b8456edcedcabe607c13f7226f64e6"
slack_token = "xoxb-1233156912480-1248614129953-qtzu0O7YTdm4pPIwsnKtt9Jw"
slack_token = "xoxb-1233156912480-1271278357890-Uc6bskvdJzsPtMfgeK5BihB2"
rtm_client = RTMClient(token=slack_token)
rtm_client.start()
