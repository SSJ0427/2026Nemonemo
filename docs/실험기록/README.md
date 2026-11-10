# 실험기록

파라미터·알고리즘 비교 결과를 정리해 두는 곳. 보고서와 발표 자료는 여기서 가져다 쓴다.
`python/results/` 의 원본 출력(csv, 이미지 전체)은 git 에 올라가지 않으므로, **요약과 대표 그림만** 여기에 옮긴다.

파일 이름: `<파트>_<주제>.md` (예: `edge_blur비교.md`, `tracker_ema.md`). 그림은 `img/` 에 넣고 1MB 이하로 줄인다.

## 양식

```markdown
# [edge] 블러 종류 비교

- 담당 / 날짜: 한시원 / 11.12
- 질문: 어떤 블러가 검출 성공률이 가장 높은가
- 방법: `python experiments/edge_params.py`, data/raw 40장, sigma 0.33 고정
- 결과:

| 블러 | 성공률 | 처리 시간(ms) |
|---|---|---|
| gaussian5 | | |
| median5 | | |
| bilateral | | |

- 결론: ○○ 를 기본값으로 채택 (PR #번호)
```
