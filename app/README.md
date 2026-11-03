# 네모네모 앱 (Flutter)

전체 설명과 설치 방법은 저장소 루트의 [README.md](../README.md) 참고.

```bash
flutter pub get
flutter run              # 휴대폰 연결 후 실행 (첫 빌드는 OpenCV 컴파일로 10~30분)
flutter analyze          # 정적 분석
flutter test             # tracker 단위 테스트 + 골든 이미지 테스트
```

| 폴더 | 내용 | 담당 |
|---|---|---|
| `lib/pipeline/` | 영상처리 (python/scanner 와 1:1 대응) | 파트별 |
| `lib/camera/` | 카메라 프레임 → Mat, 라이브 루프 실행기 | 전성재 |
| `lib/screens/` | 스캔 화면, 결과 화면 | 전성재 |
| `lib/widgets/` | 사각형 오버레이 | 전성재 |
