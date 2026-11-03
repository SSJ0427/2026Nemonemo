"""정답 꼭짓점 라벨링 도구

data/raw 의 사진을 하나씩 띄우고, 문서 꼭짓점 4개를 클릭하면 data/labels.json 에 저장한다.
이미 라벨이 있는 사진은 건너뛴다.

사용법:  python tools/label_corners.py
키:
    클릭 4번     꼭짓점 지정 (순서 상관없음, 자동 정렬)
    Enter/Space  저장 후 다음
    r            다시 찍기
    s            이 사진 건너뛰기
    q            종료
태그는 저장할 때 콘솔에 쉼표로 입력 (예: 어두운배경,그림자,기울기큼)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from scanner import order_corners  # noqa: E402

LABELS = ROOT / "data" / "labels.json"
MAX_VIEW = 1000


def main() -> None:
    data = json.loads(LABELS.read_text(encoding="utf-8")) if LABELS.exists() else {"images": []}
    done = {item["image"] for item in data["images"]}
    todo = [p for p in sorted((ROOT / "data" / "raw").glob("*.jp*g")) if p.name not in done]
    print(f"라벨링할 사진 {len(todo)}장")

    for path in todo:
        img = cv2.imread(str(path))
        scale = min(1.0, MAX_VIEW / max(img.shape[:2]))
        view0 = cv2.resize(img, None, fx=scale, fy=scale)
        pts: list[tuple[float, float]] = []

        def on_click(event, x, y, *_):
            if event == cv2.EVENT_LBUTTONDOWN and len(pts) < 4:
                pts.append((x / scale, y / scale))

        cv2.namedWindow("label")
        cv2.setMouseCallback("label", on_click)
        while True:
            view = view0.copy()
            for p in pts:
                cv2.circle(view, (int(p[0] * scale), int(p[1] * scale)), 6, (0, 0, 255), -1)
            if len(pts) == 4:
                q = (order_corners(np.array(pts)) * scale).astype(np.int32)
                cv2.polylines(view, [q], True, (0, 255, 0), 2)
            cv2.putText(view, f"{path.name}  {len(pts)}/4", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.imshow("label", view)
            key = cv2.waitKey(20) & 0xFF
            if key == ord("q"):
                cv2.destroyAllWindows()
                return
            if key == ord("r"):
                pts.clear()
            if key == ord("s"):
                break
            if key in (13, 32) and len(pts) == 4:
                tags = [t.strip() for t in input(f"{path.name} 태그(쉼표 구분, 없으면 Enter): ").split(",") if t.strip()]
                corners = order_corners(np.array(pts)).round(1).tolist()
                data["images"].append({"image": path.name, "corners": corners, "tags": tags})
                LABELS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                break
    cv2.destroyAllWindows()
    print(f"저장 → {LABELS}")


if __name__ == "__main__":
    main()
