import openai

def get_openai_reply(user_prompt):
    """Fetches a clean, Meta-compliant AI reply."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are Strangemind AI, a professional, helpful, and concise assistant. "
                    "Never give medical, financial, or legal advice. "
                    "Keep responses safe, respectful, and suitable for all audiences."
                )},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        content = response["choices"][0]["message"]["content"]
        return sanitize_openai_reply(content)
    except Exception as e:
        print(f"[OpenAI Error] {e}")
        return "I'm having trouble generating a response right now."

def sanitize_openai_reply(text):
    """Ensure output is stripped of risky or non-compliant content."""
    blocklist = ["diagnosis", "prescribe", "investment advice", "click here", "scam", "sex", "violence"]
    lower = text.lower()
    if any(bad in lower for bad in blocklist):
        return "I'm unable to respond to that. Please ask something appropriate."
    return text.strip()
  
