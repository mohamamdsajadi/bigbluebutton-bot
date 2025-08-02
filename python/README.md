# BigBlueButton Bot – Python Version

This directory contains a minimal Python port of the BigBlueButton bot
prototype.  It mirrors the structure of the Go code and implements a small
subset of its functionality using idiomatic Python.

## Usage

```python
from bbb_bot import Client

client = Client.from_config("https://example.com/bigbluebutton/api/", "SECRET")
client.create("demo", "Demo meeting", "moderator", "attendee")
join_url = client.join("demo", "Bot", "moderator")
print("Join URL:", join_url)
client.end("demo", "moderator")
```

The Python version currently focuses on the HTTP API and does not yet replicate
the WebSocket/DDD message pump logic from the Go implementation.
