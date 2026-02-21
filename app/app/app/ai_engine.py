import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize(text):
    prompt = f"""
    Summarize this medical abstract into:
    - 5 key points
    - Clinical relevance
    - Evidence level
    
    {text}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response["choices"][0]["message"]["content"]


def translate(text):
    prompt = f"Translate this medical content to Spanish:\n{text}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response["choices"][0]["message"]["content"]
