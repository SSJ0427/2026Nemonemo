"""[채성우] 이진화 방식 비교 이미지 생성

사진마다 [보정 결과 | 그림자 제거 | 전역 | Otsu | 적응형] 을 한 장에 나란히 저장한다.

사용법:  python experiments/binarize_compare.py [이미지 ...]   (생략 시 data/raw 전체)
결과:    results/binarize/*.jpg
"""
import sys
from pathlib import Path

import cv2
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "python"))
from scanner import enhance, scan_frame, warp_document  # noqa: E402

MODES = [("warped", None), ("gray", "gray"), ("global", "global"), ("otsu", "otsu"), ("adaptive", "adaptive")]


def main() -> None:
    paths = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "data" / "raw").glob("*.jp*g"))
    out = ROOT / "python" / "results" / "binarize"
    out.mkdir(parents=True, exist_ok=True)

    for path in paths:
        img = cv2.imread(str(path))
        fr = scan_frame(img)
        if fr.corners is None:
            print(f"[검출 실패] {path.name}")
            continue
        warped = warp_document(img, fr.corners_full)
        fig, axes = plt.subplots(1, len(MODES), figsize=(4 * len(MODES), 6))
        for ax, (title, mode) in zip(axes, MODES):
            im = warped if mode is None else enhance(warped, mode)
            ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB) if im.ndim == 3 else im, cmap="gray")
            ax.set_title(title)
            ax.axis("off")
        fig.tight_layout()
        fig.savefig(out / f"{path.stem}.jpg", dpi=100)
        plt.close(fig)
        print(f"→ {out / (path.stem + '.jpg')}")


if __name__ == "__main__":
    main()
