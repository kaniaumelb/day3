import openai
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI()

def ask_ai(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": f"Respond to this question: {question}. Answer concisely.  No more than 3 sentences."},
        ],
        temperature=0,
    )
    return response.choices[0].message.content.strip()