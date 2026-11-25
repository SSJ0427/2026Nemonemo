// 2단계: 엣지 검출 (담당: 한시원)
// Python 레퍼런스: python/scanner/edges.py — 동작과 파라미터를 맞출 것.
import 'package:opencv_dart/opencv_dart.dart' as cv;

/// 중앙값 기반 임계값의 폭 (11.25 실험 이후 기본은 Otsu. 비교용으로 남겨 둔다)
const double kSigma = 0.33;

/// 기본 Canny 임계값: upper = Otsu 임계값, lower = upper * kOtsuLowRatio
/// 근거: docs/실험기록/edge_블러_임계값_모폴로지.md
const double kOtsuLowRatio = 0.5;

/// 화면이 거의 균일할 때 잡음까지 엣지가 되는 것을 막는 upper 하한
const int kCannyMinUpper = 30;

const int kMorphKsize = 3;

/// 8비트 그레이 이미지의 밝기 중앙값 (히스토그램으로 계산)
int medianOf(cv.Mat gray) {
  final hist = List<int>.filled(256, 0);
  final data = gray.data;
  for (var i = 0; i < data.length; i++) {
    hist[data[i]]++;
  }
  final half = data.length / 2;
  var acc = 0;
  for (var v = 0; v < 256; v++) {
    acc += hist[v];
    if (acc >= half) return v;
  }
  return 255;
}

(double, double) autoCannyThresholds(cv.Mat gray, {double sigma = kSigma}) {
  final median = medianOf(gray).toDouble();
  final lower = ((1.0 - sigma) * median).clamp(0, 255).floorToDouble();
  final upper = ((1.0 + sigma) * median).clamp(0, 255).floorToDouble();
  return (lower, upper);
}

/// Otsu 이진화 임계값(문서와 배경을 가르는 밝기)을 Canny upper 로 쓴다.
(double, double) otsuCannyThresholds(cv.Mat gray, {double lowRatio = kOtsuLowRatio}) {
  final (t, bin) = cv.threshold(gray, 0, 255, cv.THRESH_BINARY | cv.THRESH_OTSU);
  bin.dispose();
  final upper = t.floor() > kCannyMinUpper ? t.floor() : kCannyMinUpper;
  return ((upper * lowRatio).floorToDouble(), upper.toDouble());
}

/// 그레이 이미지에서 문서 경계 엣지 맵(0/255)을 만든다.
cv.Mat detectEdges(cv.Mat gray) {
  final (lower, upper) = otsuCannyThresholds(gray);
  final edges = cv.canny(gray, lower, upper);

  // 모폴로지는 none/close3/dilate3/close5+dilate3 와 비교해 차이가 없어(실험기록 참고) 현재 방식 유지
  final kernel = cv.getStructuringElement(cv.MORPH_RECT, (kMorphKsize, kMorphKsize));
  final closed = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel);
  final dilated = cv.dilate(closed, kernel, iterations: 1);
  edges.dispose();
  closed.dispose();
  kernel.dispose();
  return dilated;
}
