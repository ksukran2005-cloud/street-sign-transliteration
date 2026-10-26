import json
from urllib.request import Request, urlopen

url = "http://127.0.0.1:8000/transliterate"

data = {
    "language": "te",
    "text": "నమస్కారం ఎలా ఉన్నారు"
}

request = Request(
    url,
    data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST",
)

with urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

print("Input :", result["input"])
print("Output:", result["transliteration"])