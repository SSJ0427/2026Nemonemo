"""[한시원] 블러 종류 x Canny 임계값 x 모폴로지 비교 실험

같은 사진 세트에 대해 조합별 검출 성공률(꼭짓점 오차 <= 대각선 2%)과 처리 시간을 기록한다.
정답이 없는 실제 사진은 '4각형 검출 여부'만 본다 (evaluate.is_success 와 같은 규칙).

- 블러: gaussian5(현재 기본) / gaussian7 / median5 / median7 / bilateral
- 임계값: 밝기 중앙값 기준 sigma 0.2 / 0.33(현재) / 0.5 / 0.7, 그리고 Otsu 임계값 기준(upper=Otsu, lower=upper/2)
- 모폴로지: none / close3 / close3+dilate3(현재) / dilate3 / close5+dilate3

사용법:  python experiments/edge_params.py [--synthetic] [--size 480]
결과:    results/edge_params.csv (조합별), results/edge_params_by_tag.csv (조합 x 조건)
"""
import csv
import itertools
import sys
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import ROOT, load_dataset, wants_synthetic  # noqa: E402
from evaluate import SUCCESS_RATIO, corner_error  # noqa: E402
from scanner import detect, order_corners  # noqa: E402
from scanner.preprocess import PROCESS_SIZE  # noqa: E402

BLURS = {
    "gaussian5": lambda g: cv2.GaussianBlur(g, (5, 5), 0),
    "gaussian7": lambda g: cv2.GaussianBlur(g, (7, 7), 0),
    "median5": lambda g: cv2.medianBlur(g, 5),
    "median7": lambda g: cv2.medianBlur(g, 7),
    "bilateral": lambda g: cv2.bilateralFilter(g, 9, 75, 75),
}


def median_thresholds(sigma):
    def f(g):
        m = float(np.median(g))
        return int(max(0, (1 - sigma) * m)), int(min(255, (1 + sigma) * m))
    return f


def otsu_thresholds(g):
    t, _ = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return int(t * 0.5), int(t)


THRESHOLDS = {
    "median_s0.2": median_thresholds(0.2),
    "median_s0.33": median_thresholds(0.33),
    "median_s0.5": median_thresholds(0.5),
    "median_s0.7": median_thresholds(0.7),
    "otsu": otsu_thresholds,
}

K3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
K5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
MORPHS = {
    "none": lambda e: e,
    "close3": lambda e: cv2.morphologyEx(e, cv2.MORPH_CLOSE, K3),
    "close3+dilate3": lambda e: cv2.dilate(cv2.morphologyEx(e, cv2.MORPH_CLOSE, K3), K3),
    "dilate3": lambda e: cv2.dilate(e, K3),
    "close5+dilate3": lambda e: cv2.dilate(cv2.morphologyEx(e, cv2.MORPH_CLOSE, K5), K3),
}
CURRENT = ("gaussian5", "median_s0.33", "close3+dilate3")


def resize_gray(img, size):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    ratio = max(h, w) / size
    return cv2.resize(gray, (round(w / ratio), round(h / ratio)), interpolation=cv2.INTER_AREA), ratio


def main() -> None:
    size = int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else PROCESS_SIZE
    items, source = load_dataset(synthetic=wants_synthetic())
    print(f"데이터: {source}, 처리 해상도 {size}px")
    smalls = [(resize_gray(img, size), gt, tags) for _, img, gt, tags in items]

    rows, tag_rows = [], []
    for (bn, blur), (tn, thr), (mn, morph) in itertools.product(BLURS.items(), THRESHOLDS.items(), MORPHS.items()):
        ok, times = 0, []
        by_tag = defaultdict(lambda: [0, 0])
        for (gray, ratio), gt, tags in smalls:
            t0 = time.perf_counter()
            g = blur(gray)
            lo, hi = thr(g)
            corners = detect.find_document(morph(cv2.Canny(g, lo, hi)))
            times.append((time.perf_counter() - t0) * 1000)
            success = corners is not None
            if success and gt is not None:
                success = corner_error(order_corners(corners) * ratio, gt) <= SUCCESS_RATIO
            ok += success
            for t in tags or ["(태그 없음)"]:
                by_tag[t][0] += success
                by_tag[t][1] += 1
        rows.append({"blur": bn, "threshold": tn, "morph": mn, "success": ok, "total": len(smalls),
                     "rate": round(ok / len(smalls), 3), "ms_median": round(float(np.median(times)), 2),
                     "current": (bn, tn, mn) == CURRENT})
        for t, (k, n) in sorted(by_tag.items()):
            tag_rows.append({"blur": bn, "threshold": tn, "morph": mn, "tag": t, "success": k, "total": n})

    out = ROOT / "python" / "results"
    out.mkdir(exist_ok=True)
    suffix = "" if size == PROCESS_SIZE else f"_{size}"
    for fname, data in ((f"edge_params{suffix}.csv", rows), (f"edge_params{suffix}_by_tag.csv", tag_rows)):
        with open(out / fname, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)

    ranked = sorted(rows, key=lambda r: (-r["success"], r["ms_median"]))
    print("\n상위 10개 조합 (+ 현재 기본값)")
    print("| 블러 | 임계값 | 모폴로지 | 성공률 | 시간(ms) |")
    print("|---|---|---|---|---|")
    for r in ranked[:10] + [r for r in rows if r["current"]]:
        mark = " **(현재)**" if r["current"] else ""
        print(f"| {r['blur']} | {r['threshold']} | {r['morph']}{mark} | {r['success']}/{r['total']} | {r['ms_median']} |")

    for key in ("blur", "threshold", "morph"):
        print(f"\n[{key}] 별 최고 성공률")
        for v in dict.fromkeys(r[key] for r in rows):
            best = max((r for r in rows if r[key] == v), key=lambda r: (r["success"], -r["ms_median"]))
            print(f"  {v:<16} {best['success']}/{best['total']}  ({best['ms_median']} ms)")
    print(f"\n→ {out / f'edge_params{suffix}.csv'}")


if __name__ == "__main__":
    main()
