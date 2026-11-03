// 라이브 루프 실행기 (담당: 전성재)
//
// 프레임마다 별도 Isolate 에서 검출을 돌리고, 이전 프레임을 처리하는 동안 들어온 프레임은 버린다.
// UI 스레드를 막지 않기 위해서다.
import 'dart:isolate';

import 'package:camera/camera.dart';

import '../pipeline/quad.dart';
import 'frame_converter.dart';

class FrameProcessor {
  bool _busy = false;
  int _processed = 0;
  int _dropped = 0;
  final Stopwatch _clock = Stopwatch()..start();

  /// 최근 처리 시간(ms) - 성능 측정용
  double lastMs = 0;

  /// 실제로 처리된 프레임 기준 FPS
  double get fps => _processed / (_clock.elapsedMilliseconds / 1000).clamp(0.001, double.infinity);
  int get dropped => _dropped;

  void resetStats() {
    _processed = 0;
    _dropped = 0;
    _clock.reset();
  }

  /// 처리 중이면 null 을 바로 반환(프레임 드롭). 아니면 검출 결과(정규화 좌표)를 반환.
  ///
  /// TODO(전성재): 매 프레임 Isolate.run 대신 오래 살아있는 Isolate 하나를 재사용하면
  ///               생성 비용을 줄일 수 있다. FPS 측정 후 필요하면 개선.
  Future<(bool processed, Quad? corners)> process(CameraImage image, int rotation) async {
    if (_busy) {
      _dropped++;
      return (false, null);
    }
    _busy = true;
    final sw = Stopwatch()..start();
    try {
      final frame = FrameData.fromCameraImage(image, rotation);
      final corners = await Isolate.run(() => detectOnFrame(frame));
      _processed++;
      return (true, corners);
    } finally {
      lastMs = sw.elapsedMicroseconds / 1000;
      _busy = false;
    }
  }
}
