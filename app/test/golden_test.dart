// Python 구현과 같은 골든 데이터(data/golden)로 Dart 파이프라인을 검증한다.
// Python 쪽: python/tests/test_pipeline.py::test_golden_matches
//
// 실행: app 폴더에서 `flutter test test/golden_test.dart`
// (PC용 OpenCV 바이너리를 쓰므로 Windows/macOS/Linux 에서 돌아간다)
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:nemonemo/pipeline/quad.dart';
import 'package:nemonemo/pipeline/scanner.dart';
import 'package:opencv_dart/opencv_dart.dart' as cv;

void main() {
  final dir = Directory('../data/golden');
  final specFile = File('${dir.path}/golden.json');

  test('골든 이미지에서 정답 꼭짓점을 찾는다', () {
    final spec = jsonDecode(specFile.readAsStringSync()) as Map<String, dynamic>;
    final tol = (spec['tolerance_px'] as num).toDouble();
    for (final c in spec['cases'] as List) {
      final img = cv.imread('${dir.path}/${c['image']}');
      final found = detectFrame(img);
      expect(found, isNotNull, reason: c['image'] as String);
      final expected = Quad.fromList([for (final p in c['corners'] as List) ...(p as List).cast<num>()]);
      final err = found!.maxDistance(expected);
      expect(err, lessThan(tol), reason: '${c['image']}: ${err.toStringAsFixed(1)}px');
    }
  }, skip: specFile.existsSync() ? false : 'data/golden 없음');
}
