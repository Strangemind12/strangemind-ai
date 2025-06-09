

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_openai_reply(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or 4
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"⚠️ Error: {e}"
