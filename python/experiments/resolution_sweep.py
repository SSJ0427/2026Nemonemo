"""[한시원] 처리 해상도별 검출 성공률 + 단계별 처리 시간 (실시간 성능 실험)

같은 사진 세트를 PROCESS_SIZE 320 / 480 / 640 / 800 으로 처리해서
  - 검출 성공률 (꼭짓점 평균 오차 <= 대각선 2%, evaluate.py 와 같은 기준)과 조건 태그별 성공률
  - 단계별(전처리·엣지·검출) 처리 시간 중앙값, PC 기준 예상 fps
를 비교한다. 앱처럼 그레이스케일(카메라 Y 평면) 입력을 넣으므로 색 변환 시간은 빠진다.
PC 수치라 절대값보다 해상도에 따른 '상대적 변화'를 보고, 실기기 fps 는 앱 화면 표시로 확인한다.

사용법:  python experiments/resolution_sweep.py [--synthetic]
결과:    results/resolution_sweep.csv, results/resolution_sweep_by_tag.csv, 콘솔에 마크다운 표
"""
import csv
import sys
import time
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dataset import ROOT, load_dataset, wants_synthetic  # noqa: E402
from evaluate import SUCCESS_RATIO, corner_error  # noqa: E402
from scanner import detect_edges, find_document, order_corners, preprocess  # noqa: E402

SIZES = [320, 480, 640, 800]
REPEAT = 5


def timed(fn, *args, **kw):
    t = []
    for _ in range(REPEAT):
        t0 = time.perf_counter()
        out = fn(*args, **kw)
        t.append((time.perf_counter() - t0) * 1000)
    return out, float(np.median(t))


def main() -> None:
    items, source = load_dataset(synthetic=wants_synthetic())
    print(f"데이터: {source}, 시간은 {REPEAT}회 중앙값(ms), 성공 기준: 오차 <= 대각선 {SUCCESS_RATIO:.0%}\n")
    grays = [(name, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), gt, tags) for name, img, gt, tags in items]

    rows, tag_rows = [], []
    for size in SIZES:
        t_pre, t_edge, t_det, errs = [], [], [], []
        ok = 0
        by_tag = defaultdict(lambda: [0, 0])
        for name, gray, gt, tags in grays:
            (small, ratio), a = timed(preprocess, gray, size)
            edges, b = timed(detect_edges, small)
            corners, c = timed(find_document, edges)
            t_pre.append(a), t_edge.append(b), t_det.append(c)
            success = corners is not None
            if success and gt is not None:
                err = corner_error(order_corners(corners) * ratio, gt)
                errs.append(err)
                success = err <= SUCCESS_RATIO
            ok += success
            for t in tags or ["(태그 없음)"]:
                by_tag[t][0] += success
                by_tag[t][1] += 1
        total = np.median(t_pre) + np.median(t_edge) + np.median(t_det)
        rows.append({
            "size": size, "success": ok, "total": len(grays), "rate": round(ok / len(grays), 3),
            "err_median_pct": round(100 * float(np.median(errs)), 2) if errs else None,
            "pre_ms": round(float(np.median(t_pre)), 2), "edge_ms": round(float(np.median(t_edge)), 2),
            "detect_ms": round(float(np.median(t_det)), 2), "total_ms": round(float(total), 2),
            "pc_fps": round(1000 / total, 1),
        })
        for t, (k, n) in sorted(by_tag.items()):
            tag_rows.append({"size": size, "tag": t, "success": k, "total": n, "rate": round(k / n, 3)})

    out = ROOT / "python" / "results"
    out.mkdir(exist_ok=True)
    for fname, data in (("resolution_sweep.csv", rows), ("resolution_sweep_by_tag.csv", tag_rows)):
        with open(out / fname, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)

    print("| 해상도 | 성공률 | 오차 중앙값(대각선 %) | 전처리 | 엣지 | 검출 | 합계(ms) | PC fps |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['size']} | {r['success']}/{r['total']} ({r['rate']:.0%}) | {r['err_median_pct']} | "
              f"{r['pre_ms']} | {r['edge_ms']} | {r['detect_ms']} | {r['total_ms']} | {r['pc_fps']} |")

    tags = sorted({r["tag"] for r in tag_rows})
    print("\n| 조건 | " + " | ".join(str(s) for s in SIZES) + " |")
    print("|---|" + "---|" * len(SIZES))
    for t in tags:
        cells = [next(f"{r['success']}/{r['total']}" for r in tag_rows if r["tag"] == t and r["size"] == s)
                 for s in SIZES]
        print(f"| {t} | " + " | ".join(cells) + " |")
    print(f"\n→ {out / 'resolution_sweep.csv'}")


if __name__ == "__main__":
    main()
