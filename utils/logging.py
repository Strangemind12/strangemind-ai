import openai

def get_openai_reply(user_prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are Strangemind AI, a smart and practical assistant."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]
