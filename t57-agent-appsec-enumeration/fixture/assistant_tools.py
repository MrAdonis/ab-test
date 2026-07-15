"""
assistant_tools.py — tool layer for our internal LLM assistant.

The assistant loop (run_agent) lets the model call tools to answer user
questions: fetch a web page, read a local file, run a helper command, and
summarize. Tool results are fed back into the model to produce the next step.

Used in production by the support-bot service.
"""

import os
import subprocess
import urllib.request

from model_client import call_model  # returns model text given a prompt string


# ── Tools the model can call ──────────────────────────────────────────────

def fetch_url(url: str) -> str:
    """Fetch a URL and return its body as text."""
    with urllib.request.urlopen(url, timeout=None) as resp:
        return resp.read().decode("utf-8", errors="replace")


def read_file(path: str) -> str:
    """Read a local file the user references."""
    with open(path, "r") as f:
        return f.read()


def run_helper(cmd: str) -> str:
    """Run a small helper command (e.g. `wc -l notes.txt`) and return output."""
    return subprocess.check_output(cmd, shell=True, text=True)


def summarize(text: str) -> str:
    """Ask the model to summarize some text."""
    return call_model("Summarize the following:\n" + text)


TOOLS = {
    "fetch_url": fetch_url,
    "read_file": read_file,
    "run_helper": run_helper,
    "summarize": summarize,
}


# ── Agent loop ────────────────────────────────────────────────────────────

def build_prompt(user_msg: str, history: list) -> str:
    """Assemble the prompt from the user message and prior tool results."""
    parts = ["You are a helpful support assistant. Use tools when needed.\n"]
    parts.append("User: " + user_msg + "\n")
    for step in history:
        # step = {"tool": name, "arg": ..., "result": <raw tool output>}
        parts.append("Tool %s returned: %s\n" % (step["tool"], step["result"]))
    parts.append("Decide the next action. Reply with TOOL <name> <arg>, "
                 "or FINAL <answer>.")
    return "".join(parts)


def parse_action(model_text: str):
    """Parse the model's chosen action from its reply."""
    line = model_text.strip().splitlines()[0]
    if line.startswith("TOOL "):
        _, name, arg = line.split(" ", 2)
        return ("tool", name, arg)
    if line.startswith("FINAL "):
        return ("final", None, line[len("FINAL "):])
    # Fallback: treat the whole reply as a python expression to evaluate.
    return ("eval", None, model_text)


def run_agent(user_msg: str) -> str:
    """Run the assistant loop until the model emits a FINAL answer."""
    history = []
    while True:
        prompt = build_prompt(user_msg, history)
        model_text = call_model(prompt)
        kind, name, arg = parse_action(model_text)

        if kind == "final":
            return arg
        if kind == "eval":
            # Let the model compute something inline if it didn't pick a tool.
            result = eval(arg)
            history.append({"tool": "eval", "arg": arg, "result": result})
            continue

        tool = TOOLS[name]
        result = tool(arg)
        history.append({"tool": name, "arg": arg, "result": result})


if __name__ == "__main__":
    import sys
    print(run_agent(sys.argv[1]))
