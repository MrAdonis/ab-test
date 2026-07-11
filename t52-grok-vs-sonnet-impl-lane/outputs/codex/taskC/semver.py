def compare_versions(a: str, b: str) -> int:
    def parse(version: str):
        core_and_prerelease = version.split("+", 1)[0]
        core, sep, prerelease = core_and_prerelease.partition("-")
        major, minor, patch = (int(part) for part in core.split("."))
        prerelease_parts = prerelease.split(".") if sep else None
        return (major, minor, patch), prerelease_parts

    def sign(value: int) -> int:
        return (value > 0) - (value < 0)

    a_core, a_pre = parse(a)
    b_core, b_pre = parse(b)

    core_cmp = sign((a_core > b_core) - (a_core < b_core))
    if core_cmp:
        return core_cmp

    if a_pre is None and b_pre is None:
        return 0
    if a_pre is None:
        return 1
    if b_pre is None:
        return -1

    for a_part, b_part in zip(a_pre, b_pre):
        if a_part == b_part:
            continue

        a_numeric = a_part.isdigit()
        b_numeric = b_part.isdigit()

        if a_numeric and b_numeric:
            return sign(int(a_part) - int(b_part))
        if a_numeric:
            return -1
        if b_numeric:
            return 1
        return sign((a_part > b_part) - (a_part < b_part))

    return sign(len(a_pre) - len(b_pre))
