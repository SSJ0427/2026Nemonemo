# 네모네모 — 실시간 문서 스캐너

디지털영상처리 조별 프로젝트. 휴대폰 카메라로 문서를 비추면 실시간으로 네 꼭짓점을 찾고, 촬영하면 정면에서 본 스캔본으로 펴 준다.

| 역할 | 이름 | GitHub |
|---|---|---|
| 조장 · 앱 골격/카메라/통합 | 전성재 | [@SeongJJ02](https://github.com/SeongJJ02) |
| 전처리 · 엣지 검출 · 실시간 성능 | 한시원 | [@Si-1-Han](https://github.com/Si-1-Han) |
| 문서 검출 · 시간축 안정화 | 신승준 | [@SSJ0427](https://github.com/SSJ0427) |
| 원근 변환 · 화질 개선 · 결과 처리 | 채성우 | [@seongwoo02](https://github.com/seongwoo02) |

## 구조

```
.
├── .github/                PR·이슈 템플릿, CI (pytest · flutter analyze)
├── app/                    Flutter 모바일 앱 (Android 우선, iOS 는 Mac 필요, 로그인 없음)
│   └── lib/
│       ├── pipeline/       영상처리 파이프라인 (Python 과 1:1 대응)
│       ├── camera/         카메라 프레임 → Mat 변환, 라이브 루프 실행기
│       ├── screens/        스캔 화면, 결과 화면
│       └── widgets/        사각형 오버레이
├── python/                 알고리즘 실험 · 평가 (레퍼런스 구현)
│   ├── scanner/            파이프라인 모듈
│   ├── experiments/        파트별 실험 스크립트
│   ├── tools/              라벨링 도구, 골든 데이터 생성
│   ├── tests/              pytest
│   ├── evaluate.py         테스트셋 평가
│   └── app_streamlit.py    PC용 데모 (백업 시연)
├── data/
│   ├── golden/             Python·Dart 결과 비교용 합성 이미지 + 정답
│   ├── raw/                테스트 사진 (git 제외, 공유 드라이브 사용)
│   └── labels.json         테스트 사진 정답 꼭짓점
└── docs/                   계획서 · 발표 자료
    ├── 작업가이드.md       파트별 할 일, Python → Dart 이식 절차  ← 먼저 읽기
    ├── 실험기록/           파라미터 실험 결과 요약 (보고서 재료)
    └── 회의록/             주간 회의록
```

## 처리 흐름

```
[라이브 루프 · 매 프레임 · 480px]
카메라 프레임(Y 평면 = 그레이) → preprocess → detect_edges → find_document → order_corners
  → CornerTracker (흔들림 보정, N프레임 안정 시 자동 촬영) → 프리뷰에 사각형 표시

[촬영 시 · 1회 · 원본 해상도]
사진 → (고해상도에서 다시 검출, 실패 시 프리뷰 좌표 사용) → warp_document → enhance(mode) → 저장/공유
```

| 파일 (Python ↔ Dart) | 담당 |
|---|---|
| `scanner/preprocess.py` ↔ `pipeline/preprocess.dart` | 한시원 |
| `scanner/edges.py` ↔ `pipeline/edges.dart` | 한시원 |
| `scanner/detect.py` ↔ `pipeline/detect.dart` | 신승준 |
| `scanner/tracker.py` ↔ `pipeline/tracker.dart` | 신승준 |
| `scanner/warp.py` ↔ `pipeline/warp.dart` | 채성우 |
| `scanner/enhance.py` ↔ `pipeline/enhance.dart` | 채성우 |
| `scanner/pipeline.py` ↔ `pipeline/scanner.dart`, `camera/*`, `screens/*` | 전성재 |

모든 파일에 기본 구현이 들어 있어 지금 바로 돌아간다. 각 파일의 `TODO(이름)` 이 각자 실험·개선할 지점이다.

## 시작하기

### Python (모두)

```bash
cd python
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest                          # 20개 통과하면 OK (Python↔Dart 파라미터 일치 검사 포함)
streamlit run app_streamlit.py  # PC 데모
```

### Flutter 앱

1. [Flutter SDK](https://docs.flutter.dev/get-started/install) **stable 3.44 이상** 설치, Android Studio 설치
   (`pubspec.lock` 이 Flutter 3.44 / Dart 3.13.7 이상을 요구한다. `flutter --version` 으로 확인, 낮으면 `flutter upgrade`)
2. Android Studio → SDK Manager → SDK Tools 에서 **NDK (Side by side)** 와 **CMake** 체크 후 설치
3. `flutter doctor` 로 Android toolchain 확인
4. 휴대폰 개발자 옵션 → USB 디버깅 켜고 연결

```bash
cd app
flutter pub get
flutter run            # 연결된 휴대폰에 설치·실행
```

> **첫 빌드는 오래 걸린다 (10~30분).** `opencv_dart` 가 첫 빌드 때 OpenCV 를 소스에서 컴파일하기 때문이다.
> 이후에는 캐시되어 빨라진다. `pubspec.yaml` 맨 아래 `hooks` 설정으로 필요한 모듈(imgproc, imgcodecs)만 빌드한다.
> `flutter run` 은 연결된 기기의 CPU 종류만 빌드하므로 `flutter build apk` 보다 빠르다.

PC 에서 Dart 파이프라인만 검증할 때 (휴대폰 없이):

```bash
cd app
flutter test           # tracker 단위 테스트 + 골든 이미지 테스트 (Windows 는 Visual Studio C++ 필요)
```

## 협업 규칙

[CONTRIBUTING.md](CONTRIBUTING.md) 참고. 요약:

- `main` 에 직접 push 하지 않는다. `feat/<파트>-<내용>` 브랜치 → Pull Request → 1명 이상 리뷰 후 merge
- 알고리즘을 바꾸면 **Python 과 Dart 를 같은 PR 에서 함께** 바꾸고, 양쪽 테스트를 통과시킨다
- 테스트 사진은 git 에 올리지 않는다 (공유 드라이브 → `data/raw/` 에 복사)
