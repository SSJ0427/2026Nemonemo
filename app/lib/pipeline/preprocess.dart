// 1단계: 전처리 (담당: 한시원)
// Python 레퍼런스: python/scanner/preprocess.py — 동작과 파라미터를 맞출 것.
import 'package:opencv_dart/opencv_dart.dart' as cv;

/// 처리용 이미지의 긴 변 길이(px)
const int kProcessSize = 480;

/// 블러 커널 크기
const int kBlurKsize = 5;

/// 그레이스케일(1채널) 또는 BGR(3채널) 이미지를 처리용 이미지로 만든다.
///
/// 반환: (처리용 그레이 이미지, ratio = 원본 크기 / 처리 크기)
(cv.Mat, double) preprocess(cv.Mat img, {int processSize = kProcessSize}) {
  final gray = img.channels == 1 ? img : cv.cvtColor(img, cv.COLOR_BGR2GRAY);

  final h = gray.rows, w = gray.cols;
  var ratio = (h > w ? h : w) / processSize;
  cv.Mat small;
  if (ratio > 1.0) {
    small = cv.resize(gray, ((w / ratio).round(), (h / ratio).round()), interpolation: cv.INTER_AREA);
  } else {
    ratio = 1.0;
    small = gray.clone();
  }
  if (!identical(gray, img)) gray.dispose();

  // TODO(한시원): 블러 종류 비교 실험 결과 반영
  final blurred = cv.gaussianBlur(small, (kBlurKsize, kBlurKsize), 0);
  small.dispose();
  return (blurred, ratio);
}
