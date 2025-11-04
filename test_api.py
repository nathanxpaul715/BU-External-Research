import anthropic
import requests
import json
 
payload = {
    "workspace_id": "ExternalResei8Dz",
}
 
url = "https://aiplatform.gcs.int.thomsonreuters.com/v1/anthropic/token"
 
# Send a POST request to the URL with headers and the payload
resp = requests.post(url,headers=None, json=payload)
 
# Load the response content as JSON
Credentials = json.loads(resp.content)
 
if 'anthropic_api_key' in Credentials:
    client = anthropic.Anthropic(
        # defaults to os.environ.get("ANTHROPIC_API_KEY")
        api_key=Credentials["anthropic_api_key"],
    )
    message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Whos leading the f1 championship in 2025?"}
    ],
    tools=[{
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 5
    }]
)
    for textblock in message.content:
        if hasattr(textblock, 'text'):
            print(textblock.text)
else:
    print(Credentials)