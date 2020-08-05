import os
from slack import RTMClient

@RTMClient.run_on(event="message")
def say_hello(**payload):
  print("LET US SEE")
  data = payload['data']
  web_client = payload['web_client']
  if 'text' in data and 'Hello' in data['text']:
    channel_id = data['channel']
    thread_ts = data['ts']
    user = data['user'] # This is not username but user ID (the format is either U*** or W***)

    web_client.chat_postMessage(
      channel=channel_id,
      text=f"Hi <@{user}>!",
      thread_ts=thread_ts
    )

slack_token = os.environ["SLACK_TOKEN"]
print(slack_token)
rtm_client = RTMClient(
  token=slack_token,
  connect_method='rtm.start'
)
rtm_client.start()
