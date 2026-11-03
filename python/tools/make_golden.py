"""Python/Dart 구현 비교용 골든 데이터 생성 (data/golden/)

사용법:  python tools/make_golden.py
합성 사진과 '정답 꼭짓점'을 저장한다. 두 구현 모두 이 정답과 tolerance_px 이내여야 한다.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scanner.synthetic import make_photo  # noqa: E402

OUT = Path(__file__).resolve().parents[2] / "data" / "golden"

CASES = [
    ("synthetic_01.jpg", [[310, 140], [880, 190], [960, 800], [230, 760]], True),
    ("synthetic_02.jpg", [[200, 220], [1000, 120], [1050, 840], [150, 700]], False),
    ("synthetic_03.jpg", [[420, 90], [820, 110], [900, 860], [330, 820]], True),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    spec = {"tolerance_px": 15, "cases": []}
    for i, (name, corners, shadow) in enumerate(CASES):
        img = make_photo(np.array(corners, np.float32), seed=i, shadow=shadow)
        cv2.imwrite(str(OUT / name), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        spec["cases"].append({"image": name, "corners": corners})
    (OUT / "golden.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(f"{len(CASES)}개 생성 → {OUT}")


if __name__ == "__main__":
    main()
