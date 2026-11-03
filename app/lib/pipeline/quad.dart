import 'dart:math' as math;

/// 꼭짓점 4개를 담는 단순 자료형.
///
/// Isolate 간에 주고받기 쉽도록 OpenCV/Flutter 타입을 쓰지 않는다.
/// 순서는 항상 좌상, 우상, 우하, 좌하 (order_corners 이후 기준).
class Pt {
  final double x;
  final double y;
  const Pt(this.x, this.y);

  Pt operator +(Pt o) => Pt(x + o.x, y + o.y);
  Pt operator -(Pt o) => Pt(x - o.x, y - o.y);
  Pt operator *(double s) => Pt(x * s, y * s);
  double get length => math.sqrt(x * x + y * y);

  @override
  String toString() => '(${x.toStringAsFixed(1)}, ${y.toStringAsFixed(1)})';
}

class Quad {
  final List<Pt> pts; // length 4
  const Quad(this.pts);

  Pt get tl => pts[0];
  Pt get tr => pts[1];
  Pt get br => pts[2];
  Pt get bl => pts[3];

  Quad scale(double sx, [double? sy]) =>
      Quad([for (final p in pts) Pt(p.x * sx, p.y * (sy ?? sx))]);

  /// 이미지 크기로 나눠 0~1 범위로 정규화 (해상도가 다른 이미지 사이에서 좌표를 옮길 때 사용)
  Quad normalized(int width, int height) => scale(1 / width, 1 / height);

  /// 두 사각형의 대응 꼭짓점 사이 최대 거리
  double maxDistance(Quad other) {
    var m = 0.0;
    for (var i = 0; i < 4; i++) {
      final d = (pts[i] - other.pts[i]).length;
      if (d > m) m = d;
    }
    return m;
  }

  List<double> toList() => [for (final p in pts) ...[p.x, p.y]];

  static Quad fromList(List<num> v) =>
      Quad([for (var i = 0; i < 4; i++) Pt(v[2 * i].toDouble(), v[2 * i + 1].toDouble())]);

  @override
  String toString() => 'Quad$pts';
}
