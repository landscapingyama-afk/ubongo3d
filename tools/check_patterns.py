"""ubongo3.html の問題データ（blockPatternList）を検証するスクリプト。

各レベルについて以下を確認する:
  - 全ブロックで立方体を隙間・重なりなく埋めていること
  - 各ブロックのキューブが面でつながった1つの形であること

使い方: python3 tools/check_patterns.py
"""
import json
import os
import re
import sys

HTML = os.path.join(os.path.dirname(__file__), "..", "ubongo3.html")
DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def load_patterns():
    with open(HTML, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"const blockPatternList = (\[.*?\n\]);", src, re.S)
    return json.loads(re.sub(r"//.*", "", m.group(1)))


def is_connected(cells):
    cells = set(map(tuple, cells))
    start = next(iter(cells))
    seen, stack = {start}, [start]
    while stack:
        x, y, z = stack.pop()
        for dx, dy, dz in DIRS:
            q = (x + dx, y + dy, z + dz)
            if q in cells and q not in seen:
                seen.add(q)
                stack.append(q)
    return len(seen) == len(cells)


def main():
    ok = True
    for i, level in enumerate(load_patterns()):
        n = 3 if i < 5 else 4  # getCubeSizeForLevel と同じ
        cells = [tuple(c) for block in level for c in block]
        full = {(x, y, z) for x in range(n) for y in range(n) for z in range(n)}
        errors = []
        if len(cells) != len(set(cells)):
            errors.append("重なりあり")
        if set(cells) != full:
            errors.append("隙間または範囲外あり")
        for b, block in enumerate(level):
            if not is_connected(block):
                errors.append(f"ブロック{b + 1}が分離")
        print(f"Lv{i + 1}: {'OK' if not errors else ', '.join(errors)}")
        ok = ok and not errors
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
