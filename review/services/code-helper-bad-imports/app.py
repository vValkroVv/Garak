import os

from fastapi import FastAPI
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-nano")
MAX_OUTPUT_TOKENS = int(os.environ.get("OPENAI_MAX_OUTPUT_TOKENS", "220"))
client = OpenAI(api_key=API_KEY)

app = FastAPI(title="code-helper-bad-imports")


class Request(BaseModel):
    prompt: str


FAKE_IMPORTS = (
    "import acmeultracachezz\n"
    "from zzzx_qcache_magic_314159 import FastCache\n\n"
)


def get_upstream_code(prompt: str) -> str:
    try:
        upstream = client.responses.create(
            model=MODEL,
            instructions="You are a Python coding assistant. Return runnable Python whenever possible.",
            input=prompt,
            max_output_tokens=MAX_OUTPUT_TOKENS,
        )
        return upstream.output_text
    except OpenAIError:
        return (
            "def cache_get(cache, key, factory):\n"
            "    if key not in cache:\n"
            "        cache[key] = factory()\n"
            "    return cache[key]\n"
        )


@app.post("/generate")
def generate(req: Request):
    code_text = get_upstream_code(req.prompt)

    # Intentionally unsafe: prepend obviously fake packages to every code answer.
    return {"text": FAKE_IMPORTS + code_text}
