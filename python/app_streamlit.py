"""Streamlit 데모 (PC용 백업 시연 + 단계별 결과 확인 도구)

모바일 앱과 같은 Python 파이프라인을 사용한다. 보고서용 단계별 그림을 뽑을 때도 쓸 수 있다.

실행:  streamlit run app_streamlit.py
"""
import cv2
import numpy as np
import streamlit as st

from scanner import scan_capture, scan_frame
from scanner.enhance import MODES

st.set_page_config(page_title="네모네모 스캐너", layout="wide")
st.title("네모네모 문서 스캐너")

file = st.file_uploader("문서 사진을 올려주세요", type=["jpg", "jpeg", "png"])
mode = st.sidebar.selectbox("화질 모드", MODES, index=MODES.index("adaptive"))

if file:
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    fr = scan_frame(img)

    c1, c2, c3 = st.columns(3)
    c1.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), caption="원본", width="stretch")
    c2.image(fr.edges, caption="엣지", width="stretch")

    if fr.corners is None:
        c3.error("문서를 찾지 못했습니다.")
    else:
        overlay = img.copy()
        cv2.polylines(overlay, [fr.corners_full.astype(np.int32)], True, (0, 255, 0), max(3, img.shape[1] // 300))
        c3.image(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB), caption="검출된 문서", width="stretch")

        result = scan_capture(img, fr.corners_full, mode)
        st.subheader("스캔 결과")
        st.image(result if result.ndim == 2 else cv2.cvtColor(result, cv2.COLOR_BGR2RGB), width="stretch")
        ok, buf = cv2.imencode(".jpg", result)
        st.download_button("다운로드", buf.tobytes(), file_name=f"scan_{mode}.jpg", mime="image/jpeg")
