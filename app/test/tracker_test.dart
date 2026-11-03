import 'package:flutter_test/flutter_test.dart';
import 'package:nemonemo/pipeline/detect.dart';
import 'package:nemonemo/pipeline/quad.dart';
import 'package:nemonemo/pipeline/tracker.dart';

void main() {
  const q = Quad([Pt(0.2, 0.1), Pt(0.8, 0.12), Pt(0.85, 0.9), Pt(0.15, 0.88)]);

  test('orderCorners 는 입력 순서와 관계없이 좌상-우상-우하-좌하로 정렬', () {
    final shuffled = Quad([q.br, q.tl, q.bl, q.tr]);
    expect(orderCorners(shuffled).maxDistance(q), 0);
  });

  test('정지한 사각형이 이어지면 안정 상태가 된다', () {
    final t = CornerTracker(stableFrames: 5);
    var stable = false;
    for (var i = 0; i < 10; i++) {
      (_, stable) = t.update(q);
    }
    expect(stable, isTrue);
    expect(t.stability, 1.0);
  });

  test('검출이 잠깐 끊겨도 이전 결과를 유지하고, 오래 끊기면 지운다', () {
    final t = CornerTracker(maxMissed: 2);
    t.update(q);
    expect(t.update(null).$1, isNotNull);
    t.update(null);
    expect(t.update(null).$1, isNull);
  });

  test('크게 움직이면 안정 카운트가 초기화된다', () {
    final t = CornerTracker(stableFrames: 3);
    for (var i = 0; i < 5; i++) {
      t.update(q);
    }
    final moved = q.scale(1.2);
    final (_, stable) = t.update(moved);
    expect(stable, isFalse);
  });
}
