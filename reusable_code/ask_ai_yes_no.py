import tiktoken
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

_ENCODING = tiktoken.encoding_for_model("gpt-4o")
_LOGIT_BIAS = {
    tid: 100
    for word in ["yes", "no"]
    for tid in _ENCODING.encode(word)
}

def ask_ai_yes_no(question: str) -> bool:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Answer strictly with a single word: 'Yes' or 'No'."},
            {"role": "user", "content": question},
        ],
        max_tokens=1,
        temperature=0,
        logit_bias=_LOGIT_BIAS,
    )
    return response.choices[0].message.content.strip().lower().startswith("y")