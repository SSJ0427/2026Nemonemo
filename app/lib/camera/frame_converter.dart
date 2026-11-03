// 카메라 프레임 → OpenCV Mat 변환 (담당: 전성재)
import 'dart:typed_data';

import 'package:camera/camera.dart';
import 'package:opencv_dart/opencv_dart.dart' as cv;

import '../pipeline/quad.dart';
import '../pipeline/scanner.dart';

/// Isolate 로 보낼 수 있는 프레임 데이터 (CameraImage 는 보낼 수 없어서 필요한 것만 복사)
class FrameData {
  const FrameData({
    required this.bytes,
    required this.width,
    required this.height,
    required this.bytesPerRow,
    required this.channels,
    required this.rotation,
  });

  final Uint8List bytes;
  final int width;
  final int height;
  final int bytesPerRow;

  /// 1: Android YUV420 의 Y 평면(=그레이스케일), 4: iOS BGRA
  final int channels;

  /// 똑바로 세우기 위해 시계 방향으로 돌려야 하는 각도 (0/90/180/270)
  final int rotation;

  /// 첫 번째 평면만 사용한다.
  /// Android(YUV420)의 Y 평면은 밝기 정보 그 자체라 cvtColor 없이 그레이스케일로 쓸 수 있다.
  factory FrameData.fromCameraImage(CameraImage image, int rotation) {
    final plane = image.planes.first;
    final channels = image.format.group == ImageFormatGroup.bgra8888 ? 4 : 1;
    return FrameData(
      bytes: Uint8List.fromList(plane.bytes),
      width: image.width,
      height: image.height,
      bytesPerRow: plane.bytesPerRow,
      channels: channels,
      rotation: rotation,
    );
  }

  /// 똑바로 세운 그레이스케일 Mat 을 만든다.
  cv.Mat toGrayMat() {
    final type = channels == 4 ? cv.MatType.CV_8UC4 : cv.MatType.CV_8UC1;
    final mat = cv.Mat.create(rows: height, cols: width, type: type);
    final dst = mat.data;
    final rowBytes = width * channels;
    if (bytesPerRow == rowBytes) {
      dst.setRange(0, rowBytes * height, bytes);
    } else {
      // 행 끝에 패딩이 있는 경우 한 줄씩 복사
      for (var y = 0; y < height; y++) {
        dst.setRange(y * rowBytes, (y + 1) * rowBytes, bytes, y * bytesPerRow);
      }
    }

    var gray = mat;
    if (channels == 4) {
      gray = cv.cvtColor(mat, cv.COLOR_BGRA2GRAY);
      mat.dispose();
    }

    final code = switch (rotation) {
      90 => cv.ROTATE_90_CLOCKWISE,
      180 => cv.ROTATE_180,
      270 => cv.ROTATE_90_COUNTERCLOCKWISE,
      _ => null,
    };
    if (code == null) return gray;
    final rotated = cv.rotate(gray, code);
    gray.dispose();
    return rotated;
  }
}

/// Isolate 안에서 실행: 프레임 하나를 검출하고 0~1 로 정규화된 꼭짓점을 돌려준다.
Quad? detectOnFrame(FrameData frame) {
  final gray = frame.toGrayMat();
  final corners = detectFrame(gray);
  final w = gray.cols, h = gray.rows;
  gray.dispose();
  return corners?.normalized(w, h);
}
