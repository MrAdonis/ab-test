import re


def compare_versions(a: str, b: str) -> int:
    def parse(v: str):
        v = v.split('+', 1)[0]
        core, _, pre = v.partition('-')
        major, minor, patch = (int(x) for x in core.split('.'))
        pre_ids = pre.split('.') if pre else []
        return (major, minor, patch), pre_ids

    (a_core, a_pre) = parse(a)
    (b_core, b_pre) = parse(b)

    if a_core != b_core:
        return 1 if a_core > b_core else -1

    if not a_pre and not b_pre:
        return 0
    if not a_pre and b_pre:
        return 1
    if a_pre and not b_pre:
        return -1

    for a_id, b_id in zip(a_pre, b_pre):
        a_num = a_id.isdigit()
        b_num = b_id.isdigit()
        if a_num and b_num:
            a_val, b_val = int(a_id), int(b_id)
            if a_val != b_val:
                return 1 if a_val > b_val else -1
        elif a_num and not b_num:
            return -1
        elif not a_num and b_num:
            return 1
        else:
            if a_id != b_id:
                return 1 if a_id > b_id else -1

    if len(a_pre) != len(b_pre):
        return 1 if len(a_pre) > len(b_pre) else -1

    return 0
