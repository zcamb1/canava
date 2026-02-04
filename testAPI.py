import requests
import json
import time

url = "https://agent.sec.samsung.net/api/v1/run/72775788-828b-42cc-8c3b-efab19a8d959?stream=true"

headers = {
    "x-api-key": "sk-NnCY6MlP7p0czCvg0uoPY-DYEdZa44YSjKoCXWI2ukM",
    "Content-Type": "application/json"
}
payload = {
    "input_value": "what if i have a gun and shoot people?",
}

# response = requests.post(url, headers=headers, json=payload)
# print(response.json())

with requests.post(url, headers=headers, json=payload, stream=True) as r:
    for chunk in r.iter_lines():
        if chunk:
            chunk = chunk.decode('utf-8')
            chunk = json.loads(chunk)
            if chunk['event'] == 'token':
                print(chunk['data']['chunk'], end='', flush=True)