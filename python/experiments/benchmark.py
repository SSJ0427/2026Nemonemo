"""[한시원] 처리 해상도별 단계별 처리 시간 측정 (실시간 성능 실험)

PC 기준 수치이므로 절대값보다는 '해상도에 따른 상대적 변화'를 본다.
실기기 수치는 앱 화면 왼쪽 위의 fps/ms 표시로 확인한다.

사용법:  python experiments/benchmark.py [이미지 경로]
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from scanner import detect_edges, find_document, order_corners, preprocess  # noqa: E402
from scanner.synthetic import DEFAULT_CORNERS, make_photo  # noqa: E402

SIZES = [320, 480, 640, 800]
REPEAT = 30


def timeit(fn, *args):
    t = []
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        out = fn(*args)
        t.append((time.perf_counter() - t0) * 1000)
    return out, float(np.median(t))


def main() -> None:
    img = cv2.imread(sys.argv[1]) if len(sys.argv) > 1 else make_photo(DEFAULT_CORNERS, size=(1920, 1440))
    print(f"입력 {img.shape[1]}x{img.shape[0]}, 중앙값(ms) / {REPEAT}회")
    print(f"{'size':>6} {'pre':>7} {'edge':>7} {'detect':>7} {'total':>7}  found")
    for s in SIZES:
        (gray, _), t1 = timeit(preprocess, img, s)
        e, t2 = timeit(detect_edges, gray)
        c, t3 = timeit(find_document, e)
        if c is not None:
            order_corners(c)
        print(f"{s:>6} {t1:7.2f} {t2:7.2f} {t3:7.2f} {t1 + t2 + t3:7.2f}  {c is not None}")


if __name__ == "__main__":
    main()
