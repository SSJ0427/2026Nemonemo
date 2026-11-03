# 협업 규칙

## 브랜치

| 브랜치 | 용도 |
|---|---|
| `main` | 항상 빌드·테스트가 통과하는 상태. 직접 push 금지 |
| `feat/<파트>-<내용>` | 기능 개발. 예: `feat/edge-auto-canny`, `feat/tracker-kalman`, `feat/enhance-color` |
| `fix/<내용>` | 버그 수정 |
| `exp/<이름>-<내용>` | 실험용 (merge 안 해도 됨). 결과는 PR 설명이나 `python/results/` 요약으로 공유 |

```bash
git switch main && git pull
git switch -c feat/edge-auto-canny
# ... 작업 ...
git add -A && git commit -m "edge: 중앙값 기반 Canny 임계값 sigma 0.33 → 0.25"
git push -u origin feat/edge-auto-canny
# GitHub 에서 Pull Request 생성
```

## 커밋 메시지

`<파트>: <무엇을 바꿨는지>` 형식. 파트는 `pre`, `edge`, `detect`, `tracker`, `warp`, `enhance`, `app`, `camera`, `eval`, `docs`.

## Pull Request 체크리스트

- [ ] `cd python && pytest` 통과
- [ ] `cd app && flutter analyze` 경고 없음
- [ ] 알고리즘을 바꿨다면 Python 과 Dart 를 **둘 다** 바꿨다 (파라미터 값도 동일하게)
- [ ] 파라미터를 바꿨다면 실험 근거(성공률·처리 시간)를 PR 설명에 적었다

## 데이터

- 테스트 사진 원본은 용량 때문에 git 에 올리지 않는다. 공유 드라이브에 올리고 각자 `data/raw/` 에 복사한다.
- 파일 이름 규칙: `<촬영자 이니셜>_<번호>.jpg` (예: `hsw_01.jpg`)
- 정답 꼭짓점과 조건 태그는 `python tools/label_corners.py` 로 만들고 `data/labels.json` 은 git 에 올린다.
- 태그 예시: `밝은배경`, `어두운배경`, `비슷한색배경`, `그림자`, `역광`, `기울기큼`, `손가림`, `구겨짐`

## Python ↔ Dart 일치 확인

`data/golden/` 의 합성 이미지에서 두 구현이 같은 꼭짓점을 찾는지 확인한다.

```bash
cd python && pytest tests/test_pipeline.py::test_golden_matches
cd app && flutter test test/golden_test.dart
```

골든 데이터를 다시 만들어야 하면 `python tools/make_golden.py`.
