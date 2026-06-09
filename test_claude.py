import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    messages=[
        {
            "role": "user",
            "content": "What is the book '1984' about in one paragraph?"
        }
    ]
)

print(message.content[0].text)