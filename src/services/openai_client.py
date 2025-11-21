import os
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def call_model(prompt: str, image_bytes: bytes = None):
    # This is a placeholder wrapper for GPT Vision + text models
    kwargs = {"model": OPENAI_MODEL, "input": prompt}
    if image_bytes:
        kwargs["image"] = image_bytes
    resp = client.responses.create(**kwargs)
    return resp