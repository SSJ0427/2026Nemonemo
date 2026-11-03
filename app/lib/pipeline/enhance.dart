// 6단계: 화질 개선 (담당: 채성우)
// Python 레퍼런스: python/scanner/enhance.py — 동작과 파라미터를 맞출 것.
import 'package:opencv_dart/opencv_dart.dart' as cv;

enum ScanMode {
  color('컬러'),
  gray('흑백'),
  global('전역 이진화'),
  otsu('Otsu'),
  adaptive('적응형');

  const ScanMode(this.label);
  final String label;
}

const int kShadowKsize = 25;
const int kAdaptiveBlock = 31;
const double kAdaptiveC = 15;
const double kGlobalThresh = 127;

/// 모폴로지 닫힘으로 배경을 추정하고 원본을 나누어 그림자를 제거한다.
cv.Mat removeShadow(cv.Mat gray, {int ksize = kShadowKsize}) {
  final kernel = cv.getStructuringElement(cv.MORPH_RECT, (ksize, ksize));
  final closed = cv.morphologyEx(gray, cv.MORPH_CLOSE, kernel);
  final background = cv.medianBlur(closed, 21);
  final out = cv.divide(gray, background, scale: 255);
  kernel.dispose();
  closed.dispose();
  background.dispose();
  return out;
}

cv.Mat enhance(cv.Mat warped, ScanMode mode) {
  if (mode == ScanMode.color) {
    if (warped.channels == 1) return warped.clone();
    // TODO(채성우): 컬러 모드 개선
    final lab = cv.cvtColor(warped, cv.COLOR_BGR2Lab);
    final ch = cv.split(lab);
    final l = removeShadow(ch[0]);
    final merged = cv.merge(cv.VecMat.fromList([l, ch[1], ch[2]]));
    final out = cv.cvtColor(merged, cv.COLOR_Lab2BGR);
    lab.dispose();
    merged.dispose();
    l.dispose();
    ch.dispose();
    return out;
  }

  final gray = warped.channels == 3 ? cv.cvtColor(warped, cv.COLOR_BGR2GRAY) : warped.clone();
  final flat = removeShadow(gray);
  gray.dispose();

  switch (mode) {
    case ScanMode.gray:
      return flat;
    case ScanMode.global:
      final (_, out) = cv.threshold(flat, kGlobalThresh, 255, cv.THRESH_BINARY);
      flat.dispose();
      return out;
    case ScanMode.otsu:
      final (_, out) = cv.threshold(flat, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU);
      flat.dispose();
      return out;
    case ScanMode.adaptive:
    case ScanMode.color:
      final out = cv.adaptiveThreshold(
          flat, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, kAdaptiveBlock, kAdaptiveC);
      flat.dispose();
      return out;
  }
}
