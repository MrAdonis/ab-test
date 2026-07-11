def compare_versions(a: str, b: str) -> int:
    """Compare two SemVer 2.0.0 strings. Returns -1, 0, or 1."""

    def parse(v: str):
        # Strip build metadata (ignored for precedence)
        core = v.split("+", 1)[0]
        if "-" in core:
            main, pre = core.split("-", 1)
            prerelease = pre.split(".")
        else:
            main, prerelease = core, None
        major, minor, patch = (int(x) for x in main.split("."))
        return major, minor, patch, prerelease

    def cmp_pre(pa, pb):
        # None means no pre-release → higher precedence than with pre-release
        if pa is None and pb is None:
            return 0
        if pa is None:
            return 1
        if pb is None:
            return -1
        n = max(len(pa), len(pb))
        for i in range(n):
            if i >= len(pa):
                return -1  # fewer identifiers → lower precedence
            if i >= len(pb):
                return 1
            x, y = pa[i], pb[i]
            x_num, y_num = x.isdigit(), y.isdigit()
            if x_num and y_num:
                xi, yi = int(x), int(y)
                if xi != yi:
                    return -1 if xi < yi else 1
            elif x_num and not y_num:
                return -1  # numeric < alphanumeric
            elif not x_num and y_num:
                return 1
            else:
                if x != y:
                    return -1 if x < y else 1
        return 0

    ma, mi, pa, prea = parse(a)
    mb, mib, pb, preb = parse(b)

    if ma != mb:
        return -1 if ma < mb else 1
    if mi != mib:
        return -1 if mi < mib else 1
    if pa != pb:
        return -1 if pa < pb else 1
    return cmp_pre(prea, preb)
