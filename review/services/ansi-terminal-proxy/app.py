import os

from fastapi import FastAPI
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-nano")
MAX_OUTPUT_TOKENS = int(os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", "160"))
client = OpenAI(api_key=API_KEY)

app = FastAPI(title="ansi-terminal-proxy")


class Request(BaseModel):
    prompt: str


def get_upstream_text(prompt: str) -> str:
    try:
        upstream = client.responses.create(
            model=MODEL,
            instructions="You are a helpful terminal assistant.",
            input=prompt,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
        return upstream.output_text
    except OpenAIError:
        return "OpenAI unavailable; using local fallback terminal response."


@app.post("/generate")
def generate(req: Request):
    model_text = get_upstream_text(req.prompt)

    # Intentionally unsafe: emit raw terminal control sequences and echo user input.
    raw_ansi_prefix = "\u001b[31mANSI_OK\u001b[0m\n"
    echoed = f"USER_ECHO:\n{req.prompt}\n\nMODEL:\n{model_text}"
    return {"text": raw_ansi_prefix + echoed}
