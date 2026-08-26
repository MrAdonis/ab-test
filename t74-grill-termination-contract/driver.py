#!/usr/bin/env python3
"""t74 多轮 driver：被测臂（顾问）与固定人设的用户模拟器交替对话。

被测臂每轮只拿到「规则 + 对话记录」，与真实 skill 使用一致。
用户模拟器是评测基础设施，允许输出 TAG 协议行（不污染被测臂）。

用法：driver.py <task-slug> <A|B>
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_TURNS = int(os.environ.get("T74_MAX_TURNS", "12"))
NOINFO_PAT = re.compile(r"没想过|不知道|没细想|没考虑过|没了解过|没查过")


def claude(prompt, cwd):
    r = subprocess.run(
        ["claude", "-p", prompt, "--model", "sonnet",
         "--permission-mode", "bypassPermissions",
         # 纯对话模式：测的是追问/终止/收口协议，不是探索能力。
         # 不限制的话模型会跑去翻本机真实目录，耗轮次且污染 transcript。
         "--disallowed-tools", "Bash,Read,Glob,Grep,Write,Edit,WebSearch,WebFetch,Task,TodoWrite"],
        cwd=cwd, capture_output=True, text=True, timeout=600,
    )
    if r.returncode != 0:
        raise RuntimeError(f"claude failed rc={r.returncode}: {r.stderr[:500]}")
    return r.stdout.strip()


def render(transcript):
    lines = []
    for role, text in transcript:
        lines.append(f"{'用户' if role == 'user' else '顾问'}：{text}")
    return "\n\n".join(lines)


def main():
    task, arm = sys.argv[1], sys.argv[2]
    rules = open(f"{HERE}/prompts/rules-{arm}.txt").read().strip()
    opening = open(f"{HERE}/prompts/task{task[0]}-{task[2:]}.txt").read().strip()
    persona = open(f"{HERE}/prompts/persona{task[0]}-{task[2:]}.txt").read().strip()

    sandbox = tempfile.mkdtemp(prefix=f"t74-{task}-{arm}-")
    transcript = [("user", opening)]
    meta = {"task": task, "arm": arm, "turns": 0, "stopped": False,
            "noinfo_turns": [], "stop_turn": None}

    for turn in range(1, MAX_TURNS + 1):
        advisor_prompt = (
            f"{rules}\n\n---\n\n以下是你和用户到目前为止的对话记录：\n\n"
            f"{render(transcript)}\n\n---\n\n"
            "现在写你要对用户说的下一条消息。只输出这条消息本身，"
            "不要替用户回复，不要加任何额外说明。"
        )
        advisor = claude(advisor_prompt, sandbox)
        transcript.append(("advisor", advisor))
        meta["turns"] = turn

        user_prompt = (
            "你在跟一位顾问对话，讨论你自己的事情。请完全以「我」的身份回复。\n\n"
            f"{persona}\n\n"
            "回复规则：\n"
            "1. 只回答对方问到的部分，口语，2 到 4 句。\n"
            "2. 卡片里没有的信息，直接说「这个我真没想过」或「不知道」，"
            "绝不编造任何新的事实、数字、时间点或人物。\n"
            "3. 不要主动说出没被问到的信息。\n"
            "4. 不要评价对方问得好不好。\n"
            "5. 如果对方这条不是在向你要信息，而是在给结论、总结或收尾，"
            "你就回「嗯，就这样吧」。\n\n"
            f"对话记录：\n\n{render(transcript)}\n\n"
            "输出格式（严格遵守）：\n"
            "第一行只写 TAG: ASKED 或 TAG: SUMMARIZED —— 对方最后那条主要是在向你"
            "提问要信息就写 ASKED，主要是在给结论或收尾就写 SUMMARIZED。\n"
            "第二行起写你的回复正文，不要重复 TAG。"
        )
        raw = claude(user_prompt, sandbox)
        first, _, body = raw.partition("\n")
        tag = "SUMMARIZED" if "SUMMARIZED" in first.upper() else "ASKED"
        body = body.strip() or first.strip()

        if tag == "SUMMARIZED":
            meta["stopped"] = True
            meta["stop_turn"] = turn
            break

        transcript.append(("user", body))
        if NOINFO_PAT.search(body):
            meta["noinfo_turns"].append(turn)

    out = f"{HERE}/outputs/{task}-{arm}"
    with open(out + ".md", "w") as f:
        f.write(render(transcript) + "\n")
    with open(out + ".json", "w") as f:
        json.dump({"meta": meta, "transcript": transcript},
                  f, ensure_ascii=False, indent=2)
    print(f"done {task}-{arm}: turns={meta['turns']} stopped={meta['stopped']} "
          f"noinfo={meta['noinfo_turns']}")


if __name__ == "__main__":
    main()
