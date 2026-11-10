## 무엇을 바꿨나요

<!-- 한두 줄 요약. 관련 이슈가 있으면 "closes #번호" -->

## 파트

- [ ] pre / edge (한시원)
- [ ] detect / tracker (신승준)
- [ ] warp / enhance (채성우)
- [ ] app / camera / eval (전성재)
- [ ] docs

## 근거 (파라미터·알고리즘을 바꿨다면)

| 항목 | 변경 전 | 변경 후 |
|---|---|---|
| 검출 성공률 (`python evaluate.py`) | | |
| 처리 시간 ms (`python experiments/benchmark.py`) | | |
| 기타 (jitter, 실기기 fps 등) | | |

<!-- 실험 결과 요약을 docs/실험기록/ 에 남겼다면 링크 -->

## 체크리스트

- [ ] `cd python && pytest` 통과
- [ ] `cd app && flutter analyze` 경고 없음
- [ ] 알고리즘을 바꿨다면 Python 과 Dart 를 **둘 다** 바꿨다 (파라미터 값도 동일)
- [ ] 골든 테스트 확인: `flutter test test/golden_test.dart` (Dart 를 바꾼 경우)
- [ ] 실기기에서 실행해 봤다 (앱 화면·카메라를 바꾼 경우)
