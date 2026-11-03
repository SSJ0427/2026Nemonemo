// 2단계: 엣지 검출 (담당: 한시원)
// Python 레퍼런스: python/scanner/edges.py — 동작과 파라미터를 맞출 것.
import 'package:opencv_dart/opencv_dart.dart' as cv;

const double kSigma = 0.33;
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

/// 그레이 이미지에서 문서 경계 엣지 맵(0/255)을 만든다.
cv.Mat detectEdges(cv.Mat gray) {
  final (lower, upper) = autoCannyThresholds(gray);
  final edges = cv.canny(gray, lower, upper);

  // TODO(한시원): 모폴로지 연산 비교 실험 결과 반영
  final kernel = cv.getStructuringElement(cv.MORPH_RECT, (kMorphKsize, kMorphKsize));
  final closed = cv.morphologyEx(edges, cv.MORPH_CLOSE, kernel);
  final dilated = cv.dilate(closed, kernel, iterations: 1);
  edges.dispose();
  closed.dispose();
  kernel.dispose();
  return dilated;
}
