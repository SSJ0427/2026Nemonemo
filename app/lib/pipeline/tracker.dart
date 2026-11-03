// 실시간 안정화: 프레임 간 흔들림 보정 + 자동 촬영 판단 (담당: 신승준)
// Python 레퍼런스: python/scanner/tracker.py — 동작과 파라미터를 맞출 것.
//
// 좌표는 0~1 로 정규화된 값을 넣는 것을 권장한다. (moveTol 도 그 기준)
import 'quad.dart';

class CornerTracker {
  CornerTracker({
    this.alpha = 0.5,
    this.moveTol = 4.0 / 480, // 처리 이미지 480px 기준 4px
    this.stableFrames = 10,
    this.maxMissed = 5,
  });

  final double alpha;
  final double moveTol;
  final int stableFrames;
  final int maxMissed;

  Quad? smoothed;
  int _stillCount = 0;
  int _missed = 0;

  void reset() {
    smoothed = null;
    _stillCount = 0;
    _missed = 0;
  }

  /// 0~1, 자동 촬영까지 얼마나 안정됐는지 (UI 진행 표시용)
  double get stability => (_stillCount / stableFrames).clamp(0.0, 1.0);

  /// 새 프레임의 검출 결과를 반영한다. 반환: (보정된 꼭짓점, 안정 여부)
  (Quad?, bool) update(Quad? corners) {
    if (corners == null) {
      _missed++;
      _stillCount = 0;
      if (_missed > maxMissed) smoothed = null;
      return (smoothed, false);
    }
    _missed = 0;

    final prev = smoothed;
    if (prev == null) {
      smoothed = corners;
      _stillCount = 0;
      return (smoothed, false);
    }

    // TODO(신승준): 칼만 필터 등 다른 보정 방식 실험
    final movement = corners.maxDistance(prev);
    smoothed = Quad([
      for (var i = 0; i < 4; i++) corners.pts[i] * alpha + prev.pts[i] * (1 - alpha),
    ]);
    _stillCount = movement < moveTol ? _stillCount + 1 : 0;
    return (smoothed, _stillCount >= stableFrames);
  }
}
