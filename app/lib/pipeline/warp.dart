// 5단계: 원근 변환 (담당: 채성우)
// Python 레퍼런스: python/scanner/warp.py — 동작과 파라미터를 맞출 것.
import 'dart:math' as math;

import 'package:opencv_dart/opencv_dart.dart' as cv;

import 'quad.dart';

/// 정렬된 꼭짓점(원본 좌표계)으로 문서를 정면 시점으로 편다.
cv.Mat warpDocument(cv.Mat img, Quad corners) {
  final width = math.max((corners.br - corners.bl).length, (corners.tr - corners.tl).length).round();
  final height = math.max((corners.tr - corners.br).length, (corners.tl - corners.bl).length).round();
  final w = math.max(width, 1), h = math.max(height, 1);

  // TODO(채성우): A4 비율 맞춤 옵션 검토
  final src = cv.VecPoint2f.fromList([for (final p in corners.pts) cv.Point2f(p.x, p.y)]);
  final dst = cv.VecPoint2f.fromList([
    cv.Point2f(0, 0),
    cv.Point2f(w - 1.0, 0),
    cv.Point2f(w - 1.0, h - 1.0),
    cv.Point2f(0, h - 1.0),
  ]);
  final m = cv.getPerspectiveTransform2f(src, dst);
  final warped = cv.warpPerspective(img, m, (w, h), flags: cv.INTER_LINEAR);
  src.dispose();
  dst.dispose();
  m.dispose();
  return warped;
}
