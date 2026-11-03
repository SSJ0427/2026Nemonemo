// 3~4단계: 문서 영역 검출 + 꼭짓점 정렬 (담당: 신승준)
// Python 레퍼런스: python/scanner/detect.py — 동작과 파라미터를 맞출 것.
import 'package:opencv_dart/opencv_dart.dart' as cv;

import 'quad.dart';

const double kMinAreaRatio = 0.10;
const double kApproxEps = 0.02;
const int kTopK = 5;

/// 엣지 맵에서 꼭짓점 4개인 볼록 다각형을 찾는다. (정렬 전, 처리 이미지 좌표계)
Quad? findDocument(cv.Mat edges) {
  final minArea = kMinAreaRatio * edges.rows * edges.cols;
  final (contours, hierarchy) = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE);
  hierarchy.dispose();

  final byArea = <(double, cv.VecPoint)>[
    for (final c in contours) (cv.contourArea(c), c),
  ]..sort((a, b) => b.$1.compareTo(a.$1));

  Quad? found;
  for (final (area, c) in byArea.take(kTopK)) {
    if (area < minArea) break;
    final peri = cv.arcLength(c, true);
    final approx = cv.approxPolyDP(c, kApproxEps * peri, true);
    if (approx.length == 4 && cv.isContourConvex(approx)) {
      found = Quad([for (final p in approx) Pt(p.x.toDouble(), p.y.toDouble())]);
      approx.dispose();
      break;
    }
    approx.dispose();
  }
  contours.dispose();

  // TODO(신승준): 4각형이 안 나올 때 convexHull / minAreaRect 대안
  return found;
}

/// 좌상, 우상, 우하, 좌하 순서로 정렬 (좌표의 합과 차 이용)
Quad orderCorners(Quad q) {
  Pt pick(double Function(Pt) key, {required bool max}) {
    var best = q.pts.first;
    for (final p in q.pts) {
      if (max ? key(p) > key(best) : key(p) < key(best)) best = p;
    }
    return best;
  }

  double sum(Pt p) => p.x + p.y;
  double diff(Pt p) => p.y - p.x;
  return Quad([
    pick(sum, max: false), // 좌상
    pick(diff, max: false), // 우상
    pick(sum, max: true), // 우하
    pick(diff, max: true), // 좌하
  ]);
}
