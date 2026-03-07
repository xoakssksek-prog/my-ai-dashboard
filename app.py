import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os 
import base64 
import re
import io 
import random

# 1. 기본 페이지 설정
st.set_page_config(page_title="AI 기반 불량 원인 분석 및 품질 관리 대시보드", layout="wide", initial_sidebar_state="collapsed")

# 🌐 번역 딕셔너리 (새로운 지표 번호 및 타이틀 추가)
TRANSLATIONS = {
    "AI 기반 불량 원인 분석 및 품질 관리 대시보드": "Bảng điều khiển Quản lý Chất lượng & Phân tích Lỗi AI",
    "⏰ 매일 오전 9시 자동 갱신 활성화": "⏰ Cập nhật tự động 9h sáng",
    "🚨 매일 아침 8시까지 실적 등록 완료 요망": "🚨 Vui lòng hoàn tất đăng ký trước 8h sáng",
    "📥 보고서 다운로드": "📥 Tải Báo Cáo",
    "🗓️ 시작일": "🗓️ Ngày bắt đầu",
    "🗓️ 종료일": "🗓️ Ngày kết thúc",
    "👥 조 선택": "👥 Chọn ca",
    "전체": "Tất cả",
    "A조": "Ca A",
    "B조": "Ca B",
    "🖱️ 설비 선택": "🖱️ Chọn thiết bị",
    "🎯 목표 불량률 설정 (%)": "🎯 Mục tiêu tỷ lệ lỗi (%)",
    "🔍 데이터 조회": "🔍 Tra cứu dữ liệu",
    "#### 실시간 사출기 현황 모니터링": "#### Giám sát trạng thái máy ép phun",
    "대기중": "Đang chờ",
    "가동": "Đang chạy",
    "수리": "Sửa chữa",
    "청소": "Vệ sinh",
    "교체": "Thay thế",
    "기간내 전체 불량율(%)": "Tỷ lệ lỗi toàn bộ (%)",
    "기간내 실제 손실 규모 (VND/KRW)": "Quy mô tổn thất thực tế (VND/KRW)",
    "기간내 최악 설비": "Thiết bị tệ nhất",
    "기간내 불량 합계": "Tổng số lỗi",
    "**1. A조/B조 불량 실적 추이**": "1. Xu hướng lỗi Ca A/Ca B",
    "**2. 불량 유형별 원가 타격**": "2. Tác động chi phí theo lỗi",
    "**3. 불량 유형 정밀 분석 (비율)**": "3. Phân tích chi tiết lỗi (%)",
    "**4. 설비별 불량률 (%)**": "4. Tỷ lệ lỗi theo thiết bị (%)",
    "**5. 시간대별 불량 추이 시각화 (%)**": "5. Biểu đồ lỗi theo thời gian (%)",
    "**6. 일자별 손실 비용 추이**": "6. Xu hướng chi phí tổn thất theo ngày",
    "**7. 특정 작업자 심층 분석**": "7. Phân tích chuyên sâu công nhân",
    "**8. 작업자별 불량 현황 (불량률 기준)**": "8. Lỗi theo công nhân (Tỷ lệ lỗi)",
    "**9. 특정 금형 심층 분석**": "9. Phân tích chuyên sâu khuôn",
    "**10. 금형별 불량 현황 (불량률 기준)**": "10. Lỗi theo khuôn (Tỷ lệ lỗi)",
    "**11. 설비 시간 가동율 현황**": "11. Tỷ lệ thời gian hoạt động của thiết bị",
    "**12. 설비 성능 가동율 현황**": "12. Tỷ lệ hiệu suất hoạt động của thiết bị",
    "설비 가동 종합 분석": "Phân tích tổng hợp hoạt động thiết bị",
    "추후 업데이트 예정입니다.": "Sẽ được cập nhật sau.",
    "대상 작업자 선택:": "Chọn công nhân:",
    "대상 금형 선택:": "Chọn khuôn:",
    "데이터 없음": "Không có dữ liệu",
    "데이터가 없습니다.": "Không có dữ liệu.",
    "발생한 불량이 없습니다.": "Không có lỗi phát sinh.",
    "AI 스마트 업무 코칭 및 가이드": "Hướng dẫn & Cố vấn Công việc Thông minh AI",
    "✨ FURSYS AI 심층 분석 브리핑 (핵심 요약)": "✨ Tóm tắt AI FURSYS (Điểm chính)",
    "✅ 일일 현장 Action Plan": "✅ Kế hoạch hành động hiện trường",
    "💬 **메신저 공유용 요약**": "💬 **Bản sao tóm tắt (Zalo, v.v.)**",
    "종합 생산 지표": "Chỉ số sản xuất tổng hợp",
    "작업자 상세 분석": "Phân tích công nhân",
    "금형 심층 분석": "Phân tích khuôn",
    "불량 원인 추적": "Theo dõi nguyên nhân lỗi",
    "AI 설비 예지보전": "AI Bảo trì dự đoán",
    "업무 인수 인계 및 주/야 교대 일지": "Nhật ký bàn giao công việc & Thay ca",
    "현재 AI 모델 학습 및 데이터 연동을 준비 중입니다. 다음 업데이트를 기대해 주세요!": "Mô hình AI đang được đào tạo và liên kết dữ liệu. Vui lòng chờ bản cập nhật tiếp theo!"
}

def T(text, lang):
    if lang == "Tiếng Việt":
        return TRANSLATIONS.get(text, text.replace('**',''))
    return text.replace('**','')

# 🌟 상단 로고 변환 함수
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

logo_b64 = get_image_base64("logo.png")

# 🌟 커스텀 CSS 적용 (상단 공백 극단적 제거 및 폰트 사이즈 밸런싱)
st.markdown("""
    <style>
    /* Streamlit 기본 상단 헤더 빈공간 완벽 제거 */
    header[data-testid="stHeader"] { 
        display: none !important; 
    }
    
    /* 전체 여백 조절 및 중앙 정렬 */
    .main .block-container {
        max-width: 1400px; 
        padding-top: 1rem !important; /* 상단 패딩 축소 */
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        margin-top: -30px !important; /* 화면을 위로 바짝 끌어올림 */
    }

    /* 전체 배경 & 폰트 */
    .stApp, .main { background-color: #FFFFFF !important; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    
    /* 텍스트 & 타이포그래피 */
    h1, h2, h3, h4 { color: #1D1D1F !important; font-weight: 700 !important; letter-spacing: -0.5px; margin-bottom: 0.5rem; }
    p, span, div { color: #515154; }
    
    /* 🌟 입체적 Metric Cards (상단 주요 지표) */
    .stMetric { 
        background: linear-gradient(145deg, #ffffff, #e6e9ef);
        padding: 15px; /* 패딩 살짝 축소 */
        border-radius: 16px; 
        box-shadow: 6px 6px 15px rgba(0,0,0,0.06), -6px -6px 15px rgba(255,255,255,1); 
        border: 1px solid rgba(255,255,255,0.8);
        transition: transform 0.2s ease, box-shadow 0.2s ease; 
        height: auto !important; 
        display: flex; flex-direction: column; justify-content: center;
        box-sizing: border-box !important;
    }
    .stMetric:hover { 
        transform: translateY(-4px); 
        box-shadow: 8px 8px 20px rgba(0,0,0,0.08), -8px -8px 20px rgba(255,255,255,1); 
    }
    /* 지표 숫자 크기 밸런싱 (34px -> 26px) */
    [data-testid="stMetricValue"] { color: #1D1D1F !important; font-size: 26px !important; font-weight: 800 !important; letter-spacing: -1px; text-shadow: 1px 1px 2px rgba(0,0,0,0.05); }
    /* 지표 라벨 크기 밸런싱 (13px -> 12px) */
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * { color: #6E6E73 !important; font-size: 12px !important; font-weight: 700 !important; text-transform: uppercase; letter-spacing: 0.5px; }
    
    /* Buttons */
    .stButton>button, .stDownloadButton>button { 
        width: 100%; background: linear-gradient(145deg, #2b2b2c, #1a1a1c) !important; color: #FFFFFF !important; 
        border-radius: 12px; font-weight: 600; font-size: 13px; border: none; padding: 10px 0; 
        box-shadow: 3px 3px 8px rgba(0,0,0,0.2), -3px -3px 8px rgba(255,255,255,0.1); transition: all 0.2s ease; 
    }
    .stButton>button:hover, .stDownloadButton>button:hover { transform: translateY(-2px); box-shadow: 4px 4px 12px rgba(0,0,0,0.3); }
    .stButton>button p, .stDownloadButton>button p { color: #FFFFFF !important; }
    
    /* 🌟 AI Briefing & Action Plan Boxes (박스 입체감) */
    .ai-box { 
        background: linear-gradient(145deg, #ffffff, #f0f2f5); border: 1px solid rgba(255,255,255,0.8); 
        padding: 20px; border-radius: 16px; 
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05), -5px -5px 15px rgba(255,255,255,0.9); 
        box-sizing: border-box !important; height: 100%;
    }
    .ai-title { color: #1D1D1F; font-size: 16px; font-weight: 800; margin-bottom: 12px; letter-spacing: -0.5px; display: flex; align-items: center; gap: 8px; text-shadow: 1px 1px 1px rgba(0,0,0,0.03);}
    .ai-text { color: #3A3A3C; font-size: 13.5px; line-height: 1.6; font-weight: 500;}
    
    /* Machine Status Cards */
    .machine-status { 
        padding: 12px; border-radius: 12px; text-align: center; font-weight: 700; font-size: 14px; letter-spacing: -0.2px;
        box-shadow: inset 2px 2px 6px rgba(0,0,0,0.04), inset -2px -2px 6px rgba(255,255,255,0.9); 
        border: 1px solid rgba(0,0,0,0.03); line-height: 1.4;
    }
    .status-run { background: linear-gradient(145deg, #e8f5e9, #dcedc8); color: #1B5E20; border-color: #A5D6A7; } 
    .status-stop { background: linear-gradient(145deg, #f5f5f7, #e0e0e0); color: #616161; } 
    @keyframes blink-red { 0% { opacity: 1; } 50% { opacity: 0.3; text-shadow: 0 0 10px red; } 100% { opacity: 1; } }
    .status-repair { background: linear-gradient(145deg, #ffebee, #ffcdd2); color: #B71C1C; border-color: #EF9A9A; } 
    .status-change { background: linear-gradient(145deg, #fff8e1, #ffecb3); color: #F57F17; border-color: #FFE082; }
    .blink-icon { animation: blink-red 1s infinite; } 
    
    /* 🌟 Charts & DataFrames 패널 (튀어나온 패널 느낌) */
    [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] { 
        background: linear-gradient(145deg, #ffffff, #f7f8fa); border-radius: 16px; padding: 12px; margin-top: 4px; 
        box-shadow: 6px 6px 14px rgba(0,0,0,0.05), -6px -6px 14px rgba(255,255,255,0.9); 
        border: 1px solid rgba(255,255,255,0.7);
    }
    
    /* Drill-down Summary (안으로 파인 영역) */
    .drill-down-summary { 
        background: linear-gradient(145deg, #e9ecef, #f4f6f9); padding: 12px 16px; border-radius: 10px; margin-bottom: 12px; font-size: 13.5px; color: #1D1D1F; font-weight: 600;
        box-shadow: inset 3px 3px 8px rgba(0,0,0,0.05), inset -3px -3px 8px rgba(255,255,255,0.9); 
        border: 1px solid rgba(255,255,255,0.4);
    }
    
    /* Inputs */
    div[data-testid="stDateInput"] > div, div[data-testid="stSelectbox"] > div, div[data-testid="stNumberInput"] > div { 
        border: 1px solid #D2D2D7 !important; border-radius: 8px !important; background-color: #FFFFFF !important; 
        box-shadow: inset 1px 1px 4px rgba(0,0,0,0.04) !important; transition: border-color 0.2s ease;
    }
    
    /* Divider */
    hr { border-top: 2px solid #D1D1D6; margin: 20px 0; box-shadow: 0px 1px 1px rgba(255,255,255,0.8); }
    
    /* Empty State Box */
    .empty-state {
        text-align:center; padding: 25px; color:#86868B; background: linear-gradient(145deg, #f0f0f3, #eaeaec); border-radius: 12px; font-size:14px; font-weight:600;
        box-shadow: inset 2px 2px 6px rgba(0,0,0,0.05), inset -2px -2px 6px rgba(255,255,255,0.8);
    }
    
    /* 섹션 헤더 스타일 크기 조정 (24px -> 20px) */
    .section-header {
        color:#1D1D1F; 
        font-size:20px; 
        font-weight:800; 
        margin-top:10px; 
        margin-bottom:10px;
        padding-bottom: 5px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
    }
    
    /* 사이드 패널 내부 요소 여백 정리 크기 조정 (16px -> 14px) */
    .side-panel-header { font-size: 14px; font-weight: 700; color: #1D1D1F; margin-top: 15px; margin-bottom: 8px; border-bottom: 2px solid #D1D1D6; padding-bottom: 4px; }
    </style>
    """, unsafe_allow_html=True)

# 🌐 공통 폰트 지정 (Plotly용)
font_family = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"

machine_list = ["1호기(ENGEL)", "2호기(ENGEL)", "3호기(우진)", "4호기(우진)"]
logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="width: 200px;">' if logo_b64 else "" # 로고 크기 살짝 조정

ui_lang = st.session_state.get('ui_lang', '한국어')

# 타이틀 상단 공백 완벽 제거 및 폰트 사이즈 조정 (40px -> 30px)
st.markdown(f"<div style='text-align:center; padding: 0px 0 10px 0;'>{logo_img_tag}<h1 style='color: #1D1D1F; font-size: 30px; font-weight: 800; letter-spacing: -1.2px; margin-top: 5px; text-shadow: 1px 1px 3px rgba(0,0,0,0.05);'>{T('AI 기반 불량 원인 분석 및 품질 관리 대시보드', ui_lang)}</h1></div>", unsafe_allow_html=True)

FILE_PATH = "0.xlsx" 

# --- [100% 실데이터 연동 엔진] ---
machine_status_dict = {1: "대기중", 2: "대기중", 3: "대기중", 4: "대기중"}
file_loaded = False
full_raw_df = pd.DataFrame()

if os.path.exists(FILE_PATH): 
    try:
        df_dict = pd.read_excel(FILE_PATH, sheet_name=None, header=None) 
        all_data = []
        defect_types = ['스크래치', '오염', '흑점', '작업불량', '색상차이', '조건 조정', '시작불량', '기타']
        
        valid_keywords = ["대기", "가동", "비가동", "수리", "청소", "교체", "정지", "기타"]

        for sheet_name, df in df_dict.items():
            try:
                max_row = min(15, len(df))
                max_col = min(8, len(df.columns))
                
                for r_idx in range(max_row):
                    for c_idx in range(max_col):
                        cell_val = str(df.iloc[r_idx, c_idx]).replace(" ", "")
                        
                        for i in range(1, 5):
                            if f"{i}호기" in cell_val:
                                for offset in range(1, 3):
                                    if c_idx + offset < max_col:
                                        s_val = str(df.iloc[r_idx, c_idx + offset]).strip()
                                        if any(k in s_val for k in valid_keywords) and len(s_val) <= 15:
                                            machine_status_dict[i] = s_val
                                            break
            except: pass

            try:
                start_row = 16 
                for r_idx in range(10, min(25, len(df))):
                    row_vals = [str(x).replace(" ", "") for x in df.iloc[r_idx].values]
                    if "일자" in row_vals or "TIME" in row_vals or "작업조" in row_vals:
                        start_row = r_idx + 1
                        break
                        
                cols = [1, 2, 3, 4, 5, 6] + list(range(8, 21))
                temp = df.iloc[start_row:, cols].copy()
                temp.columns = ['Date', 'Machine', 'Mold', 'Shift', 'Time', 'Worker', 'OK_Qty', 'DefectRate'] + \
                               defect_types + ['TotalDefects', 'UnitPrice', 'LossVND']
                
                temp[['Date', 'Machine', 'Mold', 'Shift']] = temp[['Date', 'Machine', 'Mold', 'Shift']].ffill()
                temp['Machine'] = temp['Machine'].astype(str).str.replace(" ", "")
                
                all_data.append(temp)
            except: pass
        
        full_raw_df = pd.concat(all_data, ignore_index=True)
        full_raw_df = full_raw_df[~full_raw_df['Machine'].astype(str).str.lower().isin(['nan', 'none'])]
        full_raw_df = full_raw_df.dropna(subset=['Time', 'Worker'], how='all')
        
        full_raw_df['Date'] = pd.to_datetime(full_raw_df['Date'], errors='coerce').dt.date
        for c in ['OK_Qty', 'DefectRate', 'TotalDefects', 'UnitPrice', 'LossVND'] + defect_types:
            full_raw_df[c] = pd.to_numeric(full_raw_df[c], errors='coerce').fillna(0)

        def clean_shift(x):
            val = str(x).upper()
            if 'A' in val: return 'A조'
            if 'B' in val: return 'B조'
            return val
        full_raw_df['ShiftName'] = full_raw_df['Shift'].apply(clean_shift)
        file_loaded = True 
    except Exception as e:
        st.error(f"⚠️ 엑셀 읽기 오류: {e}")
else:
    st.error(f"🚨 {FILE_PATH} 파일이 없습니다!")


# =========================================================================
# 🌟 화면 좌우 분할: 메인 대시보드(7.5) / 우측 유틸리티 패널(2.5)
# =========================================================================
main_col, side_col = st.columns([7.5, 2.5], gap="large")

with main_col:
    # --- 상단 필터부 ---
    with st.container():
        # 상단 우측에 있던 다운로드 버튼을 필터창 안으로 이동했으므로 비율 재조정
        col_auto1, col_auto2 = st.columns([1.5, 3.5]) 
        with col_auto1: auto_update = st.toggle(T("⏰ 매일 오전 9시 자동 갱신 활성화", ui_lang), value=True) 
        with col_auto2:
            if auto_update: st.markdown(f"<p style='color: #FF3B30; font-size: 13px; font-weight: bold; margin-top: 8px;'>{T('🚨 매일 아침 8시까지 실적 등록 완료 요망', ui_lang)}</p>", unsafe_allow_html=True)
        
        # 📌 PC 오늘 날짜 기준으로 무조건 초기 7일 셋팅 (데이터 보유 여부와 무관)
        default_end = datetime.today().date()
        default_start = default_end - timedelta(days=7)
            
        with st.expander("⚙️ 검색 필터 및 언어 설정 (Bộ lọc & Ngôn ngữ)", expanded=True):
            row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
            with row1_col1: start_date = st.date_input(T("🗓️ 시작일", ui_lang), default_start)
            with row1_col2: end_date = st.date_input(T("🗓️ 종료일", ui_lang), default_end)
            with row1_col3: target_shift = st.selectbox(T("👥 조 선택", ui_lang), ["전체", "A조", "B조"], format_func=lambda x: T(x, ui_lang))
            with row1_col4: st.selectbox("🌐 언어/Ngôn ngữ", ["한국어", "Tiếng Việt"], key="ui_lang")
            
            # 🌟 버튼들이 들어가는 칸에 가로 여유 공간
            row2_col1, row2_col2, row2_col3, row2_col4 = st.columns([1, 1.2, 1.3, 1.3])
            with row2_col1: target_machine = st.selectbox(T("🖱️ 설비 선택", ui_lang), ["전체"] + machine_list, format_func=lambda x: T(x, ui_lang))
            with row2_col2: target_rate = st.slider(T("🎯 목표 불량률 설정 (%)", ui_lang), 0.5, 5.0, 3.0, 0.1) 
            
            # 📌 3번째, 4번째 칸에 버튼 나란히 배치 (왼쪽: 데이터 조회, 오른쪽: 다운로드)
            with row2_col3: 
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                search_btn = st.button(T("🔍 데이터 조회", ui_lang), use_container_width=True)
            with row2_col4: 
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                st.download_button(T("📥 보고서 다운로드", ui_lang), "Report data", "fursys_report.csv", "text/csv", use_container_width=True)

    # --- 데이터 필터링 ---
    if file_loaded:
        f_df = full_raw_df[(full_raw_df['Date'] >= start_date) & (full_raw_df['Date'] <= end_date)]
        if target_shift != "전체": 
            f_df = f_df[f_df['ShiftName'] == target_shift]
        if target_machine != "전체": 
            m_num = target_machine[0]
            f_df = f_df[f_df['Machine'].str.contains(f"{m_num}\s?호기", na=False)]

    # --- 🚦 실시간 사출기 현황 모니터링 ---
    st.markdown(T("#### 실시간 사출기 현황 모니터링", ui_lang))
    m_cols = st.columns(4)
    display_names = ["1호기 <small>(ENGEL)</small>", "2호기 <small>(ENGEL)</small>", "3호기 <small>(우진)</small>", "4호기 <small>(우진)</small>"]

    for i in range(4):
        real_status = machine_status_dict.get(i+1, "대기중")
        if any(k in real_status for k in ["비가동", "수리", "🚨", "정지"]):
            cls = "status-repair"
            icon = "<span class='blink-icon'>🚨</span>"
        elif any(k in real_status for k in ["계획", "가동", "🟢"]):
            cls = "status-run"
            icon = "🟢"
        elif any(k in real_status for k in ["청소", "교체", "🟡"]):
            cls = "status-change"
            icon = "🟡"
        else:
            cls = "status-stop"
            icon = "⚪"
        
        t_real_status = T(real_status, ui_lang)
        m_cols[i].markdown(f"<div class='machine-status {cls}'>{icon} {display_names[i]}<br><span style='font-size:14px;'>{t_real_status}</span></div>", unsafe_allow_html=True)

    st.write("")

    # KPI 계산
    avg_def = round((f_df['TotalDefects'].sum() / f_df['OK_Qty'].sum()) * 100, 2) if not f_df.empty and f_df['OK_Qty'].sum() > 0 else 0
    total_l = int(f_df['LossVND'].sum())
    rate_diff = round(avg_def - target_rate, 2)

    total_krw = int(total_l / 18.5) if total_l > 0 else 0
    total_l_man = total_l / 10000
    total_krw_man = round(total_krw / 10000)

    if ui_lang == "한국어":
        vnd_str = f"{total_l_man:,.0f}만 ₫"
        krw_str = f"🇰🇷 약 {total_krw_man:,.0f}만 원 (원가 타격)"
    else:
        vnd_str = f"{total_l_man:,.0f} vạn ₫"
        krw_str = f"🇰🇷 Khoảng {total_krw_man:,.0f} vạn Won"

    worst_machine = "-"
    worst_defect_text = T("데이터 없음", ui_lang)
    if not f_df.empty and f_df['OK_Qty'].sum() > 0:
        worst_m_rate = f_df.groupby('Machine').apply(lambda x: (x['TotalDefects'].sum() / x['OK_Qty'].sum() * 100) if x['OK_Qty'].sum() > 0 else 0)
        if not worst_m_rate.empty and worst_m_rate.max() > 0:
            worst_machine = worst_m_rate.idxmax()
            wm_df = f_df[f_df['Machine'] == worst_machine]
            worst_defect = wm_df[defect_types].sum().idxmax()
            worst_defect_text = f"🚨 핵심 불량: {worst_defect}"
        elif not worst_m_rate.empty:
            worst_machine = "전 설비 양호"
            worst_defect_text = "불량 없음"

    worst_date_shift_text = T("데이터 없음", ui_lang)
    if not f_df.empty and f_df['TotalDefects'].sum() > 0:
        daily_shift_defects = f_df.groupby(['Date', 'ShiftName'])['TotalDefects'].sum()
        if not daily_shift_defects.empty and daily_shift_defects.max() > 0:
            max_idx = daily_shift_defects.idxmax()
            worst_date_shift_text = f"🚨 최다 발생: {max_idx[0].strftime('%m월 %d일')} {max_idx[1]}"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(T("기간내 전체 불량율(%)", ui_lang), f"{avg_def}%", f"{abs(rate_diff):.2f}% {'초과' if rate_diff > 0 else '여유'}", "inverse" if rate_diff > 0 else "normal")
    k2.metric(T("기간내 실제 손실 규모 (VND/KRW)", ui_lang), vnd_str, krw_str, "off")
    k3.metric(T("기간내 최악 설비", ui_lang), worst_machine, worst_defect_text, "off")
    k4.metric(T("기간내 불량 합계", ui_lang), f"{int(f_df['TotalDefects'].sum())}개", worst_date_shift_text, "off")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==========================================
    # 1. 종합 생산 지표 섹션
    # ==========================================
    st.markdown(f"<div class='section-header'>📊 {T('종합 생산 지표', ui_lang)}</div>", unsafe_allow_html=True)

    row1_c1, row1_c2, row1_c3 = st.columns(3) # 1:1:1 대칭
    with row1_c1:
        # 차트 제목 크기 조절 (16px -> 15px)
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>📈 {T('**1. A조/B조 불량 실적 추이**', ui_lang)}</h4>", unsafe_allow_html=True)
        all_dates = pd.date_range(start=start_date, end=end_date).date
        
        if not f_df.empty:
            actual_trend = f_df.groupby(['Date', 'ShiftName']).apply(lambda x: (x['TotalDefects'].sum() / x['OK_Qty'].sum() * 100) if x['OK_Qty'].sum() > 0 else 0).reset_index(name='DefectRate')
        else:
            actual_trend = pd.DataFrame(columns=['Date', 'ShiftName', 'DefectRate'])

        template = pd.DataFrame([(d, s) for d in all_dates for s in ['A조', 'B조']], columns=['Date', 'ShiftName'])
        trend = pd.merge(template, actual_trend, on=['Date', 'ShiftName'], how='left').fillna(0)
        
        a_label = "A조"
        b_label = "B조"
        if not f_df.empty:
            a_shifts = f_df[f_df['ShiftName'] == 'A조']['Shift'].dropna().unique()
            b_shifts = f_df[f_df['ShiftName'] == 'B조']['Shift'].dropna().unique()
            if len(a_shifts) > 0: a_label = str(a_shifts[-1])
            if len(b_shifts) > 0: b_label = str(b_shifts[-1])
        
        if ui_lang == "Tiếng Việt":
            tv_a_label = a_label.replace("A조", "Ca A")
            tv_b_label = b_label.replace("B조", "Ca B")
            trend['ShiftName'] = trend['ShiftName'].map({'A조': tv_a_label, 'B조': tv_b_label})
            fig1 = px.line(trend, x='Date', y='DefectRate', color='ShiftName', markers=True, template="plotly_white", color_discrete_map={tv_a_label:'#0066CC', tv_b_label:'#FF3B30'})
        else:
            trend['ShiftName'] = trend['ShiftName'].map({'A조': a_label, 'B조': b_label})
            fig1 = px.line(trend, x='Date', y='DefectRate', color='ShiftName', markers=True, template="plotly_white", color_discrete_map={a_label:'#0066CC', b_label:'#FF3B30'})
        
        # 🌟 3D 입체감 강화 (선 굵게, 부드러운 곡선 적용, 마커 부각)
        fig1.update_traces(line=dict(width=3.5, shape='spline'), marker=dict(size=8, line=dict(width=2, color='white')))
        
        max_trend_y = int(trend["DefectRate"].max()) + 1 if not trend.empty else 2.0
        fig1.update_layout(
            margin=dict(t=20,b=20,l=10,r=10), height=280, legend_title="", 
            yaxis_title="불량율 (%)" if ui_lang=="한국어" else "Tỷ lệ lỗi (%)", xaxis_title="", xaxis=dict(type='category', tickformat="%Y-%m-%d"), 
            yaxis=dict(range=[0, max_trend_y], ticksuffix="%"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family=font_family)
        )
        st.plotly_chart(fig1, use_container_width=True)

    with row1_c2:
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>💸 {T('**2. 불량 유형별 원가 타격**', ui_lang)}</h4>", unsafe_allow_html=True)
        if not f_df.empty:
            type_loss = pd.DataFrame([{'유형': t, '손실': (f_df[t] * f_df['UnitPrice']).sum()} for t in defect_types]).sort_values('손실')
            total_loss_val = type_loss['손실'].sum()
            if total_loss_val > 0:
                type_loss['텍스트'] = type_loss['손실'].apply(lambda x: f"{int(x/10000):,}만 VND ({(x/total_loss_val)*100:.1f}%)" if x > 0 else "")
                fig2 = px.bar(type_loss, x='손실', y='유형', orientation='h', color_discrete_sequence=['#FF3B30'], height=280, text='텍스트')
                
                # 🌟 3D 입체감 강화 (하얀색 테두리 + 약간의 투명도 부여)
                fig2.update_traces(texttemplate='<b>%{text}</b>', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2), opacity=0.9))
                
                max_loss_x = type_loss['손실'].max() * 1.5
                fig2.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="", yaxis_title="",
                    xaxis=dict(range=[0, max_loss_x], showticklabels=False), 
                    margin=dict(t=10, b=10, l=10, r=10), font=dict(family=font_family)
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

    with row1_c3:
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>🔍 {T('**3. 불량 유형 정밀 분석 (비율)**', ui_lang)}</h4>", unsafe_allow_html=True)
        if not f_df.empty:
            type_cnt = f_df[defect_types].sum().reset_index(); type_cnt.columns = ['유형','건수']
            total_cnt = type_cnt['건수'].sum()
            if total_cnt > 0:
                pie_df = type_cnt[type_cnt['건수'] > 0].sort_values('건수', ascending=False).reset_index(drop=True)
                txt_gae = "개" if ui_lang == "한국어" else "cái"
                pie_df['범례라벨'] = pie_df.apply(lambda x: f"{x['유형']} ({int(x['건수']):,}{txt_gae}, {x['건수']/total_cnt*100:.1f}%)", axis=1)
                pie_df['텍스트'] = [f"<b>{row['유형']}</b><br>{int(row['건수']):,}{txt_gae} ({row['건수']/total_cnt*100:.1f}%)" if i < 3 else "" for i, row in pie_df.iterrows()]
                fig3 = px.pie(pie_df, names='범례라벨', values='건수', hole=0.4, height=280)
                
                # 🌟 3D 입체감 강화 (도넛 사이 간격을 벌려서 팝업 효과 추가)
                fig3.update_traces(text=pie_df['텍스트'], textinfo='text', textposition='auto', textfont_size=12, insidetextorientation='horizontal', marker=dict(line=dict(color='#FFFFFF', width=3)))
                
                fig3.update_layout(
                    legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5, title=""), 
                    margin=dict(t=10, b=60, l=10, r=10),
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family=font_family)
                )
                st.plotly_chart(fig3, use_container_width=True)
            else:
                st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

    st.write("")
    r2_c1, r2_c2, r2_c3 = st.columns(3) # 1:1:1 대칭 (가운데 줄 3칸 분할)

    with r2_c1:
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>⚙️ {T('**4. 설비별 불량률 (%)**', ui_lang)}</h4>", unsafe_allow_html=True)
        if not f_df.empty:
            m_rate = f_df.groupby('Machine').apply(lambda x: (x['TotalDefects'].sum() / x['OK_Qty'].sum() * 100) if x['OK_Qty'].sum() > 0 else 0).reset_index(name='DefectRate')
            if not m_rate.empty and m_rate['DefectRate'].max() > 0:
                fig4 = px.bar(m_rate, x='Machine', y='DefectRate', text='DefectRate', color='DefectRate', color_continuous_scale=['#E5F0FF', '#0066CC'])
                
                fig4.update_traces(texttemplate='<b>%{text:.2f}%</b>', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2), opacity=0.9))
                
                max_y = max(m_rate['DefectRate'].max() * 1.3, target_rate * 1.3)
                fig4.update_layout(
                    height=280, yaxis_title="불량률 (%)" if ui_lang=="한국어" else "Tỷ lệ lỗi (%)", xaxis_title="", coloraxis_showscale=False,
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#D1D1D6', range=[0, max_y]), font=dict(family=font_family)
                )
                fig4.add_hline(y=target_rate, line_dash="dot", line_color="#FF3B30", line_width=2.5)
                t_target = "목표" if ui_lang=="한국어" else "Mục tiêu"
                fig4.add_annotation(
                    x=1, y=target_rate, xref="paper", yref="y", text=f"🎯 {t_target} ({target_rate}%)", showarrow=False,
                    xanchor="left", yanchor="top", font=dict(color="#86868B", size=13, weight='bold'), xshift=5, yshift=-2
                )
                fig4.update_layout(margin=dict(r=70, t=20, b=20)) 
                st.plotly_chart(fig4, use_container_width=True)
            else:
                st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

    with r2_c2:
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>🕒 {T('**5. 시간대별 불량 추이 시각화 (%)**', ui_lang)}</h4>", unsafe_allow_html=True)
        if not f_df.empty:
            f_df['TimeStr'] = f_df['Time'].astype(str)
            h_trend = f_df.groupby('TimeStr').apply(lambda x: (x['TotalDefects'].sum() / x['OK_Qty'].sum() * 100) if x['OK_Qty'].sum() > 0 else 0).reset_index(name='DefectRate')
            time_order = ['10:00:00', '12:00:00', '14:00:00', '16:00:00', '18:00:00', '20:00:00', '22:00:00', '00:00:00', '02:00:00', '04:00:00', '06:00:00', '08:00:00']
            time_labels = {
                '10:00:00': 'AM: 10시', '12:00:00': 'PM: 12시', '14:00:00': 'PM: 14시', 
                '16:00:00': 'PM: 16시', '18:00:00': 'PM: 18시', '20:00:00': 'PM: 20시', 
                '22:00:00': 'PM: 22시', '00:00:00': 'AM: 00시', '02:00:00': 'AM: 02시', 
                '04:00:00': 'AM: 04시', '06:00:00': 'AM: 06시', '08:00:00': 'AM: 08시'
            }
            if ui_lang != "한국어": time_labels = {k: v.replace('시', 'h') for k, v in time_labels.items()}
            
            template = pd.DataFrame({'TimeStr': time_order})
            h_trend = pd.merge(template, h_trend, on='TimeStr', how='left').fillna(0)
            h_trend['TimeLabel'] = h_trend['TimeStr'].map(time_labels)
            
            if h_trend['DefectRate'].max() > 0:
                fig5 = px.area(h_trend, x='TimeLabel', y='DefectRate', line_shape='spline', markers=True, color_discrete_sequence=['#34C759'])
                
                fig5.update_traces(hovertemplate="<b>%{x}</b><br>불량률: %{y:.2f}%<extra></extra>", fillcolor='rgba(52, 199, 89, 0.25)', line=dict(width=3.5), marker=dict(size=8, line=dict(width=2, color='white')))
                
                max_y5 = max(h_trend['DefectRate'].max() * 1.3, target_rate * 1.3)
                fig5.update_layout(
                    height=280, xaxis_title="", yaxis_title="불량률 (%)" if ui_lang=="한국어" else "Tỷ lệ lỗi (%)", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(gridcolor='#D1D1D6', range=[0, max_y5], ticksuffix="%"), xaxis=dict(categoryorder='array', categoryarray=h_trend['TimeLabel'].tolist()), font=dict(family=font_family)
                )
                fig5.add_hline(y=target_rate, line_dash="dot", line_color="#FF3B30", line_width=2.5)
                t_target = "목표" if ui_lang=="한국어" else "Mục tiêu"
                fig5.add_annotation(x=1, y=target_rate, xref="paper", yref="y", text=f"🎯 {t_target} ({target_rate}%)", showarrow=False, xanchor="left", yanchor="top", font=dict(color="#86868B", size=13, weight='bold'), xshift=5, yshift=-2)
                fig5.update_layout(margin=dict(r=70, t=20, b=20)) 
                
                peak_idx = h_trend['DefectRate'].idxmax()
                peak_x = h_trend.loc[peak_idx, 'TimeLabel']
                peak_y = h_trend.loc[peak_idx, 'DefectRate']
                t_warn = "🚨 피로도 주의" if ui_lang == "한국어" else "🚨 Chú ý mệt mỏi"
                fig5.add_annotation(x=peak_x, y=peak_y, text=t_warn, showarrow=True, arrowhead=2, arrowsize=1.2, arrowwidth=2, arrowcolor="#FF3B30", ax=0, ay=-30, font=dict(color="#FF3B30", size=12, weight="bold"))
                st.plotly_chart(fig5, use_container_width=True)
            else:
                st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

    with r2_c3:
        # 🌟 새롭게 추가된 6번 지표 (일자별 손실 비용 추이)
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>📉 {T('**6. 일자별 손실 비용 추이**', ui_lang)}</h4>", unsafe_allow_html=True)
        if not f_df.empty and f_df['LossVND'].sum() > 0:
            daily_loss = f_df.groupby('Date')['LossVND'].sum().reset_index()
            daily_loss['Loss_Man'] = daily_loss['LossVND'] / 10000  # 단위: 만 동(VND)
            
            fig6 = px.bar(daily_loss, x='Date', y='Loss_Man', text='Loss_Man', color_discrete_sequence=['#FF9500'])
            
            fig6.update_traces(texttemplate='<b>%{text:,.0f}만</b>', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2), opacity=0.9))
            
            max_y6 = daily_loss['Loss_Man'].max() * 1.3
            fig6.update_layout(
                height=280, xaxis_title="", yaxis_title="손실액 (만 VND)" if ui_lang=="한국어" else "Tổn thất (vạn VND)",
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                yaxis=dict(gridcolor='#D1D1D6', range=[0, max_y6]), font=dict(family=font_family),
                xaxis=dict(type='category', tickformat="%m-%d"), margin=dict(t=20, b=20, l=10, r=10)
            )
            st.plotly_chart(fig6, use_container_width=True)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==========================================
    # 2 & 3. 작업자 및 금형 심층 분석 (좌/우 통합 배치 및 번호 7~10 정리)
    # ==========================================
    def highlight_total(s):
        if s.name == '📌 총 합계' or s.name == '📌 Tổng cộng': return ['background-color: #E6E9EF; font-weight: 800; color: #1D1D1F'] * len(s)
        return [''] * len(s)

    main_left, main_right = st.columns(2, gap="large")

    with main_left:
        st.markdown(f"<div class='section-header'>🧑‍🔧 {T('작업자 상세 분석', ui_lang)}</div>", unsafe_allow_html=True)
        
        if not f_df.empty:
            tot_ok = f_df['OK_Qty'].sum()
            tot_def = f_df['TotalDefects'].sum()
            tot_rate = (tot_def / tot_ok * 100) if tot_ok > 0 else 0
            
            temp_df_w = f_df.copy()
            temp_df_w['Worker'] = temp_df_w['Worker'].fillna('미상')
            # 🌟 [수정됨] 작업자의 소속 '조' 데이터도 함께 추출하여 저장
            worker_perf = temp_df_w.groupby('Worker').agg(
                조=('Shift', lambda x: str(x.dropna().iloc[0]).replace('\\n', ' ').replace('\n', ' ').strip() if len(x.dropna())>0 else '-'),
                양품수량=('OK_Qty', 'sum'), 
                불량수량=('TotalDefects', 'sum')
            ).reset_index()
            worker_perf['불량률(%)'] = (worker_perf['불량수량'] / worker_perf['양품수량'] * 100).fillna(0)
            worker_perf = worker_perf[worker_perf['양품수량'] > 0].sort_values(by='불량률(%)', ascending=False).reset_index(drop=True)
        else:
            worker_perf = pd.DataFrame()

        # ---- [7. 특정 작업자 심층 분석 (위)] ----
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>🔎 {T('**7. 특정 작업자 심층 분석**', ui_lang)}</h4>", unsafe_allow_html=True)
        worker_list = [w for w in worker_perf['Worker'].tolist() if w not in ['📌 총 합계', '📌 Tổng cộng']] if not worker_perf.empty else []
        sel_w = st.selectbox(T("대상 작업자 선택:", ui_lang), worker_list if worker_list else [T("데이터 없음", ui_lang)], key="sel_worker_key")
        
        if sel_w not in [T("데이터 없음", ui_lang), "데이터 없음", "Không có dữ liệu"] and not f_df.empty:
            w_df = f_df[f_df['Worker'] == sel_w]
            w_ok_qty = w_df['OK_Qty'].sum()
            w_def_qty = w_df['TotalDefects'].sum()
            
            w_data = w_df[defect_types].sum().reset_index()
            w_data.columns = ['유형','건수']
            w_data['비율(%)'] = (w_data['건수'] / w_ok_qty * 100).fillna(0) if w_ok_qty > 0 else 0
            
            top3_causes = "없음" if ui_lang == "한국어" else "Không có"
            if w_data['건수'].sum() > 0:
                top3_list = w_data[w_data['건수'] > 0].sort_values('건수', ascending=False).head(3)['유형'].tolist()
                top3_causes = ", ".join(top3_list)
                
            overall_rate = f_df['TotalDefects'].sum() / f_df['OK_Qty'].sum() if f_df['OK_Qty'].sum() > 0 else 0
            w_exp_def = w_ok_qty * overall_rate
            w_diff = w_def_qty - w_exp_def
            diff_color = "#FF3B30" if w_diff > 0 else "#34C759"
            if ui_lang == "한국어":
                diff_text = f"<b style='color:{diff_color};'>{w_diff:+.1f}개</b> ({'초과 발생 🚨' if w_diff > 0 else '우수 🌟'})"
                desc_html = f"<div class='drill-down-summary' style='line-height:1.5;'>👤 <b>{sel_w}</b> 주요 불량 (Top 3): <b style='color:#FF3B30;'>{top3_causes}</b><br>⚖️ <b>편차:</b> 공정 평균 대비 {diff_text}</div>"
            else:
                diff_text = f"<b style='color:{diff_color};'>{w_diff:+.1f} cái</b> ({'Vượt mức 🚨' if w_diff > 0 else 'Tốt 🌟'})"
                desc_html = f"<div class='drill-down-summary' style='line-height:1.5;'>👤 Lỗi chính của <b>{sel_w}</b> (Top 3): <b style='color:#FF3B30;'>{top3_causes}</b><br>⚖️ <b>Đ.chỉnh:</b> So với TB {diff_text}</div>"
            
            st.markdown(desc_html, unsafe_allow_html=True)
            
            w_data_plot = w_data.sort_values('건수').copy()
            if not w_data_plot.empty:
                txt_gae = "개" if ui_lang == "한국어" else "cái"
                w_data_plot['텍스트'] = w_data_plot.apply(lambda x: f"{int(x['건수'])}{txt_gae} ({x['비율(%)']:.2f}%)", axis=1)
                fig7 = px.bar(w_data_plot, x='건수', y='유형', orientation='h', color_discrete_sequence=['#5E5CE6'], height=200, text='텍스트')
                
                fig7.update_traces(texttemplate='<b>%{text}</b>', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2), opacity=0.9))
                max_x = w_data_plot['건수'].max() * 1.3 if w_data_plot['건수'].max() > 0 else 5
                fig7.update_layout(xaxis_title="발생 개수" if ui_lang=="한국어" else "Số lượng phát sinh", yaxis_title="", margin=dict(t=5, b=5, l=5, r=5), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(range=[0, max_x]), font=dict(family=font_family))
                st.plotly_chart(fig7, use_container_width=True, key="fig7_worker_key")
            else:
                st.markdown("<div class='empty-state'>📂<br>발생한 불량이 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

        st.write("") # 섹션 간격 띄우기

        # ---- [8. 작업자별 불량 현황 (아래)] ----
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>🧑‍🔧 {T('**8. 작업자별 불량 현황 (불량률 기준)**', ui_lang)}</h4>", unsafe_allow_html=True)
        if not f_df.empty and not worker_perf.empty:
            wp_display = worker_perf.head(7).copy() 
            txt_gae = "개" if ui_lang == "한국어" else "cái"
            wp_display['양품수량'] = wp_display['양품수량'].astype(int).apply(lambda x: f"{x:,}{txt_gae}")
            wp_display['불량수량'] = wp_display['불량수량'].astype(int).apply(lambda x: f"{x:,}{txt_gae}")
            wp_display['불량률(%)'] = wp_display['불량률(%)'].apply(lambda x: f"{x:.2f}%")
            
            empty_rows_cnt = 7 - len(wp_display)
            if empty_rows_cnt > 0:
                empty_df = pd.DataFrame({'Worker': [' ' * (i+1) for i in range(empty_rows_cnt)], '조': ['-'] * empty_rows_cnt, '양품수량': ['-'] * empty_rows_cnt, '불량수량': ['-'] * empty_rows_cnt, '불량률(%)': ['-'] * empty_rows_cnt})
                wp_display = pd.concat([wp_display, empty_df], ignore_index=True)
            
            sum_row = pd.DataFrame([{'Worker': '📌 총 합계' if ui_lang=="한국어" else '📌 Tổng cộng', '조': '-', '양품수량': f"{int(tot_ok):,}{txt_gae}", '불량수량': f"{int(tot_def):,}{txt_gae}", '불량률(%)': f"{tot_rate:.2f}%"}])
            wp_display = pd.concat([wp_display, sum_row], ignore_index=True).set_index("Worker")
            if ui_lang == "Tiếng Việt": wp_display.columns = ["Ca làm việc", "Số lượng tốt", "Số lượng lỗi", "Tỷ lệ lỗi(%)"]
                
            styled_df = wp_display.style.apply(highlight_total, axis=1)
            st.dataframe(styled_df, use_container_width=True, height=300) 
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)


    with main_right:
        st.markdown(f"<div class='section-header'>🛠️ {T('금형 심층 분석', ui_lang)}</div>", unsafe_allow_html=True)
        
        if not f_df.empty:
            tot_ok_m = f_df['OK_Qty'].sum()
            tot_def_m = f_df['TotalDefects'].sum()
            tot_rate_m = (tot_def_m / tot_ok_m * 100) if tot_ok_m > 0 else 0
            
            temp_df_m = f_df.copy()
            temp_df_m['Mold'] = temp_df_m['Mold'].fillna('미상')
            mold_perf = temp_df_m.groupby('Mold').agg(양품수량=('OK_Qty', 'sum'), 불량수량=('TotalDefects', 'sum')).reset_index()
            mold_perf['불량률(%)'] = (mold_perf['불량수량'] / mold_perf['양품수량'] * 100).fillna(0)
            mold_perf = mold_perf[mold_perf['양품수량'] > 0].sort_values(by='불량률(%)', ascending=False).reset_index(drop=True)
        else:
            mold_perf = pd.DataFrame()

        # ---- [9. 특정 금형 심층 분석 (위)] ----
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>🔬 {T('**9. 특정 금형 심층 분석**', ui_lang)}</h4>", unsafe_allow_html=True)
        if 'Mold' in mold_perf.columns:
            mold_list = [m for m in mold_perf['Mold'].tolist() if m not in ['📌 총 합계', '📌 Tổng cộng'] and pd.notna(m) and str(m).strip() != '']
        else:
            mold_list = []
        sel_m = st.selectbox(T("대상 금형 선택:", ui_lang), mold_list if mold_list else [T("데이터 없음", ui_lang)], key="sel_mold_key")
        
        if sel_m not in [T("데이터 없음", ui_lang), "데이터 없음", "Không có dữ liệu"] and not f_df.empty:
            m_df = f_df[f_df['Mold'] == sel_m]
            m_ok_qty = m_df['OK_Qty'].sum()
            m_def_qty = m_df['TotalDefects'].sum()
            
            m_data = m_df[defect_types].sum().reset_index()
            m_data.columns = ['유형','건수']
            m_data['비율(%)'] = (m_data['건수'] / m_ok_qty * 100).fillna(0) if m_ok_qty > 0 else 0
            
            top3_causes_m = "없음" if ui_lang == "한국어" else "Không có"
            if m_data['건수'].sum() > 0:
                top3_list_m = m_data[m_data['건수'] > 0].sort_values('건수', ascending=False).head(3)['유형'].tolist()
                top3_causes_m = ", ".join(top3_list_m)
                
            overall_rate = f_df['TotalDefects'].sum() / f_df['OK_Qty'].sum() if f_df['OK_Qty'].sum() > 0 else 0
            m_exp_def = m_ok_qty * overall_rate
            m_diff = m_def_qty - m_exp_def
            diff_color = "#FF3B30" if w_diff > 0 else "#34C759"
            if ui_lang == "한국어":
                diff_text = f"<b style='color:{diff_color};'>{m_diff:+.1f}개</b> ({'초과 발생 🚨' if m_diff > 0 else '우수 🌟'})"
                desc_html_m = f"<div class='drill-down-summary' style='line-height:1.5;'>🛠️ <b>{sel_m}</b> 주요 불량 (Top 3): <b style='color:#FF3B30;'>{top3_causes_m}</b><br>⚖️ <b>편차:</b> 공정 평균 대비 {diff_text}</div>"
            else:
                diff_text = f"<b style='color:{diff_color};'>{m_diff:+.1f} cái</b> ({'Vượt mức 🚨' if m_diff > 0 else 'Tốt 🌟'})"
                desc_html_m = f"<div class='drill-down-summary' style='line-height:1.5;'>🛠️ Lỗi chính của khuôn <b>{sel_m}</b> (Top 3): <b style='color:#FF3B30;'>{top3_causes_m}</b><br>⚖️ <b>Đ.chỉnh:</b> So với TB {diff_text}</div>"
            
            st.markdown(desc_html_m, unsafe_allow_html=True)
            
            m_data_plot = m_data.sort_values('건수').copy()
            if not m_data_plot.empty:
                txt_gae = "개" if ui_lang == "한국어" else "cái"
                m_data_plot['텍스트'] = m_data_plot.apply(lambda x: f"{int(x['건수'])}{txt_gae} ({x['비율(%)']:.2f}%)", axis=1)
                fig8 = px.bar(m_data_plot, x='건수', y='유형', orientation='h', color_discrete_sequence=['#FF9500'], height=200, text='텍스트') 
                
                fig8.update_traces(texttemplate='<b>%{text}</b>', textposition='outside', marker=dict(line=dict(color='#FFFFFF', width=2), opacity=0.9))
                max_x = m_data_plot['건수'].max() * 1.3 if m_data_plot['건수'].max() > 0 else 5
                fig8.update_layout(xaxis_title="발생 개수" if ui_lang=="한국어" else "Số lượng phát sinh", yaxis_title="", margin=dict(t=5, b=5, l=5, r=5), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis=dict(range=[0, max_x]), font=dict(family=font_family))
                st.plotly_chart(fig8, use_container_width=True, key="fig8_mold_key")
            else:
                st.markdown("<div class='empty-state'>📂<br>발생한 불량이 없습니다.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

        st.write("") # 섹션 간격 띄우기

        # ---- [10. 금형별 불량 현황 (아래)] ----
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>🛠️ {T('**10. 금형별 불량 현황 (불량률 기준)**', ui_lang)}</h4>", unsafe_allow_html=True)
        if not f_df.empty and not mold_perf.empty:
            mp_display = mold_perf.head(7).copy() 
            txt_gae = "개" if ui_lang == "한국어" else "cái"
            mp_display['양품수량'] = mp_display['양품수량'].astype(int).apply(lambda x: f"{x:,}{txt_gae}")
            mp_display['불량수량'] = mp_display['불량수량'].astype(int).apply(lambda x: f"{x:,}{txt_gae}")
            mp_display['불량률(%)'] = mp_display['불량률(%)'].apply(lambda x: f"{x:.2f}%")
            
            empty_rows_cnt_m = 7 - len(mp_display)
            if empty_rows_cnt_m > 0:
                empty_df_m = pd.DataFrame({'Mold': [' ' * (i+1) for i in range(empty_rows_cnt_m)], '양품수량': ['-'] * empty_rows_cnt_m, '불량수량': ['-'] * empty_rows_cnt_m, '불량률(%)': ['-'] * empty_rows_cnt_m})
                mp_display = pd.concat([mp_display, empty_df_m], ignore_index=True)
            
            sum_row_m = pd.DataFrame([{'Mold': '📌 총 합계' if ui_lang=="한국어" else '📌 Tổng cộng', '양품수량': f"{int(tot_ok_m):,}{txt_gae}", '불량수량': f"{int(tot_def_m):,}{txt_gae}", '불량률(%)': f"{tot_rate_m:.2f}%"}])
            mp_display = pd.concat([mp_display, sum_row_m], ignore_index=True).set_index("Mold")
            if ui_lang == "Tiếng Việt": mp_display.columns = ["Số lượng tốt", "Số lượng lỗi", "Tỷ lệ lỗi(%)"]
            
            styled_df_m = mp_display.style.apply(highlight_total, axis=1)
            st.dataframe(styled_df_m, use_container_width=True, height=300)
        else:
            st.markdown("<div class='empty-state'>📂<br>데이터가 없습니다.</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==========================================
    # 설비 가동 종합 분석 (11, 12번)
    # ==========================================
    st.markdown(f"<div class='section-header'>🏭 {T('설비 가동 종합 분석', ui_lang)}</div>", unsafe_allow_html=True)

    eq_left, eq_right = st.columns(2, gap="large")

    with eq_left:
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>⏳ {T('**11. 설비 시간 가동율 현황**', ui_lang)}</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='empty-state'>🚀<br>{T('추후 업데이트 예정입니다.', ui_lang)}</div>", unsafe_allow_html=True)

    with eq_right:
        st.markdown(f"<h4 style='color:#1D1D1F; font-size:15px; border-bottom: 2px solid #D1D1D6; padding-bottom: 6px;'>⚡ {T('**12. 설비 성능 가동율 현황**', ui_lang)}</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='empty-state'>🚀<br>{T('추후 업데이트 예정입니다.', ui_lang)}</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==========================================
    # 4. FURSYS AI 심층 분석 브리핑 (복원 완벽 반영 & 대칭 맞춤)
    # ==========================================
    st.markdown(f"<div class='section-header'>✨ {T('AI 스마트 업무 코칭 및 가이드', ui_lang)}</div>", unsafe_allow_html=True)

    ai_bullets = []
    copy_text = "데이터가 부족하여 요약할 수 없습니다." if ui_lang=="한국어" else "Không đủ dữ liệu để tóm tắt."

    worst_m = "-"
    top_cost_type = "주요" if ui_lang=="한국어" else "Chính"
    worst_t_label = "특정" if ui_lang=="한국어" else "Cụ thể"
    worst_w = "없음" if ui_lang=="한국어" else "Không có"

    if not f_df.empty and f_df['OK_Qty'].sum() > 0:
        if avg_def > target_rate:
            if ui_lang == "한국어": ai_bullets.append(f"<b>1. [종합 진단]</b> 불량률 {avg_def}% / 목표({target_rate}%) 대비 {abs(rate_diff):.2f}% 초과 🚨")
            else: ai_bullets.append(f"<b>1. [Chẩn đoán]</b> Lỗi {avg_def}% / Vượt mục tiêu {abs(rate_diff):.2f}% 🚨")
        else:
            if ui_lang == "한국어": ai_bullets.append(f"<b>1. [종합 진단]</b> 불량률 {avg_def}% / 목표 달성 ✅")
            else: ai_bullets.append(f"<b>1. [Chẩn đoán]</b> Lỗi {avg_def}% / Đạt mục tiêu ✅")

        type_loss = pd.DataFrame([{'유형': t, '손실': (f_df[t] * f_df['UnitPrice']).sum()} for t in defect_types]).sort_values('손실', ascending=False)
        if type_loss['손실'].sum() > 0:
            top_cost_type = type_loss.iloc[0]['유형']
            top_cost_val = type_loss.iloc[0]['손실']
            top_cost_pct = (top_cost_val / type_loss['손실'].sum()) * 100
            if ui_lang == "한국어": ai_bullets.append(f"<b>2. [비용 타격]</b> 핵심: {top_cost_type} / 손실 {int(top_cost_val/10000):,}만VND ({top_cost_pct:.1f}%)")
            else: ai_bullets.append(f"<b>2. [Chi phí]</b> Lỗi chính: {top_cost_type} / {int(top_cost_val/10000):,}vạnVND ({top_cost_pct:.1f}%)")

        type_cnt = f_df[defect_types].sum().sort_values(ascending=False)
        if type_cnt.sum() > 0:
            top_cnt_type = type_cnt.index[0]
            if ui_lang == "한국어": ai_bullets.append(f"<b>3. [최다 발생]</b> {top_cnt_type} 집중 확인 요망")
            else: ai_bullets.append(f"<b>3. [Nhiều nhất]</b> Kiểm tra lỗi {top_cnt_type}")

        m_rate = f_df.groupby('Machine').apply(lambda x: (x['TotalDefects'].sum() / x['OK_Qty'].sum() * 100) if x['OK_Qty'].sum() > 0 else 0)
        if not m_rate.empty:
            worst_m = m_rate.idxmax()
            if ui_lang == "한국어": ai_bullets.append(f"<b>4. [설비 리스크]</b> 취약: {worst_m} (불량률 {m_rate[worst_m]:.2f}%)")
            else: ai_bullets.append(f"<b>4. [Rủi ro máy]</b> Máy yếu: {worst_m} ({m_rate[worst_m]:.2f}%)")

        f_df['TimeStr'] = f_df['Time'].astype(str)
        h_trend = f_df.groupby('TimeStr').apply(lambda x: (x['TotalDefects'].sum() / x['OK_Qty'].sum() * 100) if x['OK_Qty'].sum() > 0 else 0)
        if not h_trend.empty and h_trend.max() > 0:
            time_labels_map = { '10:00:00': '10시', '12:00:00': '12시', '14:00:00': '14시', '16:00:00': '16시', '18:00:00': '18시', '20:00:00': '20시', '22:00:00': '22시', '00:00:00': '00시', '02:00:00': '02시', '04:00:00': '04시', '06:00:00': '06시', '08:00:00': '08시' }
            worst_t = h_trend.idxmax()
            worst_t_label = time_labels_map.get(worst_t, worst_t)
            if ui_lang == "한국어": ai_bullets.append(f"<b>5. [취약 시간]</b> {worst_t_label} 시간대 집중 점검 요망")
            else: ai_bullets.append(f"<b>5. [Giờ yếu]</b> Cần kiểm tra lúc {worst_t_label}")

        if 'worker_perf' in locals() and not worker_perf.empty and worker_perf.iloc[0]['불량수량'] > 0:
            worst_w = worker_perf.iloc[0]['Worker']
            if ui_lang == "한국어": ai_bullets.append(f"<b>6. [인적 요인]</b> 지도 필요: {worst_w} ({worker_perf.iloc[0]['불량률(%)']})")
            else: ai_bullets.append(f"<b>6. [Nhân sự]</b> Cần hướng dẫn: {worst_w} ({worker_perf.iloc[0]['불량률(%)']})")

        if ui_lang == "한국어":
            copy_text = f"[품질 브리핑] 불량률 {avg_def}% / 집중설비: {worst_m} / 주요불량: {top_cost_type} / 코칭요망: {worst_w}"
        else:
            copy_text = f"[Báo cáo] Tỷ lệ lỗi {avg_def}% / TB trọng tâm: {worst_m} / Lỗi chính: {top_cost_type} / H.dẫn: {worst_w}"
    else:
        ai_bullets.append(T("데이터가 없습니다.", ui_lang))

    bullet_html = "<ul style='line-height: 1.6; margin-bottom: 0; padding-left: 15px; font-size:14px; font-weight: 500;'>"
    for bullet in ai_bullets:
        bullet_html += f"<li style='margin-bottom: 6px;'>{bullet}</li>"
    bullet_html += "</ul>"

    c1 = st.session_state.get('chk1', False); c2 = st.session_state.get('chk2', False)
    c3 = st.session_state.get('chk3', False); c4 = st.session_state.get('chk4', False)
    c5 = st.session_state.get('chk5', False)
    tot_cnt = 5; comp_cnt = sum([c1, c2, c3, c4, c5])
    comp_rate = int((comp_cnt / tot_cnt) * 100) if tot_cnt > 0 else 0

    col_ai, col_todo = st.columns(2, gap="medium") # 좌우 1:1 대칭 맞춤

    with col_ai:
        st.markdown(f"""<div class="ai-box" style="padding:18px;"><div class="ai-title" style="font-size:16px;">{T("✨ FURSYS AI 심층 분석 브리핑 (핵심 요약)", ui_lang)}</div>
        <div class="ai-text">{bullet_html}</div></div>""", unsafe_allow_html=True)
        
        st.write("")
        st.markdown(T("💬 **메신저 공유용 요약**", ui_lang))
        comp_text = "완료" if ui_lang == "한국어" else "Hoàn thành"
        final_copy_text = f"{copy_text} / 진도율: {comp_rate}% {comp_text}"
        
        # 🌟 글씨가 잘리거나 넘어가지 않고 자동 줄바꿈 되도록 커스텀 박스 적용
        st.markdown(f"""
        <div style="background: #F4F5F7; padding: 12px 15px; border-radius: 8px; border: 1px solid #D1D1D6; font-size: 14px; color: #1D1D1F; word-break: keep-all; overflow-wrap: break-word; line-height: 1.5; font-family: monospace; box-shadow: inset 1px 1px 3px rgba(0,0,0,0.05);">
            {final_copy_text}
        </div>
        """, unsafe_allow_html=True)

    with col_todo:
        st.markdown(f"<div class='ai-box' style='padding:18px;'><div class='ai-title' style='font-size:16px;'>{T('✅ 일일 현장 Action Plan', ui_lang)}</div>", unsafe_allow_html=True)
        if ui_lang == "한국어": st.markdown(f"<div style='font-size:14px; font-weight:800; color:#1D1D1F; margin-bottom: 8px;'>📌 과제: {tot_cnt} / 완료: {comp_cnt} ({comp_rate}%)</div>", unsafe_allow_html=True)
        else: st.markdown(f"<div style='font-size:14px; font-weight:800; color:#1D1D1F; margin-bottom: 8px;'>📌 Nhiệm vụ: {tot_cnt} / Xong: {comp_cnt} ({comp_rate}%)</div>", unsafe_allow_html=True)
        st.progress(comp_cnt / tot_cnt)
        st.write("")
        
        if ui_lang == "한국어":
            t1 = f"🚨 [{worst_m}] 조건 점검" if worst_m != "-" else "🚨 설비 점검"
            t2 = f"💸 [{top_cost_type}] 원인 차단"
            t3 = f"🕒 [{worst_t_label}] 순찰 강화" if worst_t_label != "특정" else "🕒 생산라인 순찰"
            t4 = f"👤 [{worst_w}] 교육 진행" if worst_w != "없음" else "👤 작업자 면담"
            t5 = "✨ 표준 작업서 준수 확인"
            lbl_done = "✅완료"; lbl_prog = "⏳진행중"
        else:
            t1 = f"🚨 Kiểm tra [{worst_m}]" if worst_m != "-" else "🚨 Kiểm tra máy"
            t2 = f"💸 Chặn nguyên nhân [{top_cost_type}]"
            t3 = f"🕒 Tuần tra lúc [{worst_t_label}]" if worst_t_label != "Cụ thể" else "🕒 Tuần tra định kỳ"
            t4 = f"👤 Đào tạo [{worst_w}]" if worst_w != "Không có" else "👤 Phỏng vấn công nhân"
            t5 = "✨ Xác nhận tiêu chuẩn"
            lbl_done = "✅Xong"; lbl_prog = "⏳Đang làm"
        
        st.checkbox(f"{t1} **[{lbl_done if c1 else lbl_prog}]**", key="chk1")
        st.checkbox(f"{t2} **[{lbl_done if c2 else lbl_prog}]**", key="chk2")
        st.checkbox(f"{t3} **[{lbl_done if c3 else lbl_prog}]**", key="chk3")
        st.checkbox(f"{t4} **[{lbl_done if c4 else lbl_prog}]**", key="chk4")
        st.checkbox(f"{t5} **[{lbl_done if c5 else lbl_prog}]**", key="chk5")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ==========================================
    # 5. 업무 교대 일지 시스템
    # ==========================================
    st.markdown(f"<div class='section-header'>📝 {T('업무 인수 인계 및 주/야 교대 일지', ui_lang)}</div>", unsafe_allow_html=True)

    LOG_FILE_NAME = "교대일지_누적대장.xlsx"

    with st.container():
        st.markdown("<div style='background: linear-gradient(145deg, #ffffff, #f0f2f5); padding:20px; border-radius:18px; border:1px solid rgba(255,255,255,0.8); margin-bottom: 20px; box-shadow: 5px 5px 15px rgba(0,0,0,0.05), -5px -5px 15px rgba(255,255,255,0.9);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-size:16px; margin-bottom:15px;'>✍️ 신규 작성 (Viết mới)</h4>", unsafe_allow_html=True)
        
        col_log1, col_log2, col_log3 = st.columns(3)
        with col_log1:
            log_date = st.date_input("작성일자 (Ngày)", datetime.today().date())
        with col_log2:
            log_author = st.text_input("작성자 (Người viết)", placeholder="예: 관리자 / 응옥")
        with col_log3:
            log_shift = st.selectbox("교대구분 (Ca làm việc)", ["주간 (A조) ➡️ 야간 (B조)", "야간 (B조) ➡️ 주간 (A조)"])

        log_content = st.text_area("인수인계 내용 (Nội dung bàn giao)", height=80, placeholder="특이사항, 불량 발생 내용, 다음 조 주의사항 등 작성")
        log_remarks = st.text_input("비고 (Ghi chú)", placeholder="기타 필요 사항")

        if st.button("💾 일지 저장 (Lưu nhật ký)"):
            if log_author.strip() == "" or log_content.strip() == "":
                st.warning("⚠️ 작성자와 인수인계 내용을 모두 입력해주세요! (Vui lòng nhập tên và nội dung!)")
            else:
                new_data = pd.DataFrame({
                    "기록시간": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "해당날짜": [log_date.strftime("%Y-%m-%d")],
                    "작성자": [log_author],
                    "교대구분": [log_shift],
                    "교대내용": [log_content],
                    "비고": [log_remarks]
                })
                
                if os.path.exists(LOG_FILE_NAME):
                    try:
                        existing_df = pd.read_excel(LOG_FILE_NAME)
                        updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                    except Exception as e:
                        st.error(f"기존 파일을 읽는 중 오류가 발생했습니다: {e}")
                        updated_df = new_data
                else:
                    updated_df = new_data
                
                try:
                    updated_df.to_excel(LOG_FILE_NAME, index=False)
                    st.success(f"✅ 성공적으로 '{LOG_FILE_NAME}' 파일에 누적 되었습니다!")
                except Exception as e:
                    st.error(f"파일 저장 실패! 오류: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<h4 style='font-size:16px; margin-top:10px;'>📂 저장된 교대 일지 내역 (Lịch sử bàn giao)</h4>", unsafe_allow_html=True)
    if os.path.exists(LOG_FILE_NAME):
        try:
            log_history_df = pd.read_excel(LOG_FILE_NAME)
            log_history_df = log_history_df.sort_values(by="기록시간", ascending=False).reset_index(drop=True)
            st.dataframe(log_history_df, use_container_width=True, height=250)
        except Exception as e:
            st.error(f"일지 내역을 불러올 수 없습니다: {e}")
    else:
        st.info("아직 저장된 교대 일지가 없습니다. 위에서 첫 일지를 작성해보세요!")


# =========================================================================
# 🛠️ 화면 우측 분할: 현장 유틸리티 (Quick Tools) 패널
# =========================================================================
with side_col:
    st.markdown("<div style='background: linear-gradient(145deg, #ffffff, #f0f2f5); padding: 22px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.8); box-shadow: 5px 5px 15px rgba(0,0,0,0.05), -5px -5px 15px rgba(255,255,255,0.9); min-height: 100%;'>", unsafe_allow_html=True)
    
    # 타이틀 크기 조절 (22px -> 18px)
    st.markdown(f"<div style='font-size: 18px; font-weight: 800; color: #1D1D1F; margin-bottom: 20px; text-align: center;'>🛠️ {T('Quick Tools', ui_lang)}</div>", unsafe_allow_html=True)
    
    # 1. 이달의 우수 사원 (맨 위로)
    current_m = datetime.today().month
    st.markdown(f"<div class='side-panel-header'>🏆 {current_m}월 우수 사원 (NV Xuất sắc)</div>", unsafe_allow_html=True)
    
    best_w_name = "데이터 없음"
    best_w_rate = 0.0
    
    if not full_raw_df.empty:
        temp_df = full_raw_df.copy()
        temp_df['Month'] = pd.to_datetime(temp_df['Date']).dt.month
        temp_df['Year'] = pd.to_datetime(temp_df['Date']).dt.year
        current_y = datetime.today().year
        
        month_df = temp_df[(temp_df['Month'] == current_m) & (temp_df['Year'] == current_y)]
        if not month_df.empty:
            w_perf = month_df.groupby('Worker').agg(양품수량=('OK_Qty', 'sum'), 불량수량=('TotalDefects', 'sum')).reset_index()
            w_perf['불량률'] = (w_perf['불량수량'] / w_perf['양품수량'] * 100).fillna(0)
            w_perf = w_perf[w_perf['양품수량'] > 0]
            if not w_perf.empty:
                best_worker = w_perf.loc[w_perf['불량률'].idxmin()]
                best_w_name = best_worker['Worker']
                best_w_rate = best_worker['불량률']
    
    st.markdown(f"""
    <div style="text-align:center; padding: 15px; background: #ffffff; border-radius: 12px; border: 1px solid #E5E5EA; box-shadow: 2px 2px 8px rgba(0,0,0,0.03);">
        <div style="font-size: 40px; margin-bottom: 10px;">🧑‍🔧</div>
        <div style="font-size: 15px; font-weight: 800; color: #1D1D1F;">{best_w_name}</div>
        <div style="font-size: 12px; color: #34C759; font-weight: 700; margin-top: 4px;">불량률: {best_w_rate:.2f}% (이달의 최저)</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # 2. 오늘의 품질 한마디 (우수 사원 바로 아래)
    st.markdown("<div class='side-panel-header'>💡 오늘의 품질 한마디</div>", unsafe_allow_html=True)
    quotes = [
        "품질은 검사에서 나오지 않는다, 과정에서 만들어진다.",
        "품질은 공짜다. 불량이 비싼 것이다.",
        "품질은 우연이 아니라 관리의 결과다.",
        "측정하지 못하면 개선할 수 없다.",
        "데이터 없는 품질은 의견일 뿐이다.",
        "작은 불량 하나가 큰 비용을 만든다.",
        "오늘의 불량은 내일의 손실이다.",
        "품질은 속도가 아니라 정확성에서 시작된다.",
        "문제는 사람보다 시스템에서 나온다.",
        "불량은 기록하는 것이 아니라 원인을 찾아야 한다.",
        "데이터는 거짓말하지 않는다.",
        "품질은 결과가 아니라 과정이다.",
        "보이지 않는 불량이 가장 위험하다.",
        "측정되는 것은 관리되고, 관리되는 것은 개선된다.",
        "품질은 습관이고 불량은 방심이다.",
        "원인을 모르면 개선도 없다.",
        "불량은 숫자지만, 원인은 이야기다.",
        "품질은 비용이 아니라 투자다.",
        "좋은 공장은 불량을 숨기지 않는다, 드러낸다.",
        "데이터는 과거를 기록하고, 분석은 미래를 바꾼다."
    ]
    selected_quote = np.random.choice(quotes)
    st.markdown(f"""
    <div style='background: #F0F8FF; padding: 15px; border-radius: 8px; border-left: 4px solid #007AFF; font-size: 14.5px; font-weight: 700; color: #1D1D1F; line-height: 1.5; box-shadow: 2px 2px 6px rgba(0,0,0,0.04); font-style: italic;'>
        "{selected_quote}"
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # 3. [신규] 관리자 특별 공지사항
    st.markdown("<div class='side-panel-header'>📢 일일 관리자 특별 지시사항</div>", unsafe_allow_html=True)
    st.info("**[공지]** 제품의 중량 편차가 발생하지 않도록, 매 작업 시작 전후로 흑점 및 스크래치 여부를 꼼꼼하게 확인해 주세요.\n\n👉 *Vui lòng kiểm tra kỹ chấm đen và vết xước trước và sau khi làm việc.*")
    st.write("")

    # 4. 한국/베트남 시계
    st.markdown("<div class='side-panel-header'>🕒 현재 시간 (Giờ hiện tại)</div>", unsafe_allow_html=True)
    utc_now = datetime.utcnow()
    vn_time = utc_now + timedelta(hours=7)
    kr_time = utc_now + timedelta(hours=9)
    
    c_time1, c_time2 = st.columns(2)
    c_time1.metric("🇻🇳 VN (Đồng Nai)", vn_time.strftime("%H:%M"))
    c_time2.metric("🇰🇷 KR (Seoul)", kr_time.strftime("%H:%M"))
    st.write("")

    # 5. 미니 달력
    st.markdown("<div class='side-panel-header'>🗓️ 달력 (Lịch)</div>", unsafe_allow_html=True)
    st.date_input("오늘 날짜", datetime.today().date(), label_visibility="collapsed")
    st.write("")
    
    # 6. 퀵 불량률 계산기
    st.markdown("<div class='side-panel-header'>🧮 퀵 불량률 계산기</div>", unsafe_allow_html=True)
    calc_ok = st.number_input("양품 수량 (OK)", min_value=0, value=1000, step=100, key="calc_ok")
    calc_ng = st.number_input("불량 수량 (NG)", min_value=0, value=15, step=1, key="calc_ng")
    if (calc_ok + calc_ng) > 0:
        calc_rate = (calc_ng / (calc_ok + calc_ng)) * 100
        st.info(f"👉 예상 불량률: **{calc_rate:.2f}%**")
    st.write("")

    # 7. [신규] 사이클 타임 기반 생산량 예측기
    st.markdown("<div class='side-panel-header'>⏱️ 생산 완료 시간 예측기</div>", unsafe_allow_html=True)
    ct_sec = st.number_input("사이클 타임 (초/sec)", min_value=0.0, value=35.0, step=1.0, key="ct_sec")
    ct_cavity = st.number_input("캐비티 (Cavity)", min_value=1, value=1, step=1, key="ct_cavity")
    ct_target = st.number_input("남은 생산 목표 (개)", min_value=0, value=1000, step=100, key="ct_target")
    if ct_sec > 0 and ct_target > 0:
        total_seconds = (ct_target / ct_cavity) * ct_sec
        est_hours = int(total_seconds // 3600)
        est_mins = int((total_seconds % 3600) // 60)
        st.success(f"⏳ 예상 소요 시간: **약 {est_hours}시간 {est_mins}분**")
    st.write("")

    # 8. [신규] 원자재(수지) 소요량 계산기
    st.markdown("<div class='side-panel-header'>⚖️ 원료 소요량 예측 (25kg 기준)</div>", unsafe_allow_html=True)
    mat_part = st.number_input("제품 중량 (g)", min_value=0.0, value=150.0, step=10.0, key="mat_part")
    mat_runner = st.number_input("런너 중량 (g)", min_value=0.0, value=15.0, step=1.0, key="mat_runner")
    mat_qty = st.number_input("생산 수량 (개)", min_value=0, value=1000, step=100, key="mat_qty")
    if (mat_part + mat_runner) > 0 and mat_qty > 0:
        total_kg = ((mat_part + mat_runner) * mat_qty) / 1000
        total_bags = total_kg / 25
        st.info(f"📦 필요 원료: **{total_kg:,.1f} kg** (약 **{total_bags:.1f}포대**)")
    st.write("")

    # 9. 환율 계산기 (KRW <-> VND)
    st.markdown("<div class='side-panel-header'>💱 금액 변환 (VND ➡️ KRW)</div>", unsafe_allow_html=True)
    vnd_input = st.number_input("동(VND) 입력", min_value=0, value=1000000, step=100000, key="vnd_in")
    krw_output = int(vnd_input / 18.5)
    st.success(f"🇰🇷 약 **{krw_output:,}** 원")
    st.write("")

    # 10. [신규] 사출 공정 필수 단위 변환기
    st.markdown("<div class='side-panel-header'>🔄 공정 압력 단위 변환</div>", unsafe_allow_html=True)
    conv_mode = st.selectbox("변환 유형", ["kgf/cm² ➡️ MPa", "MPa ➡️ kgf/cm²", "Bar ➡️ MPa"], label_visibility="collapsed", key="conv_mode")
    conv_val = st.number_input("압력 값 입력", value=100.0, key="conv_val")
    if conv_mode == "kgf/cm² ➡️ MPa":
        st.success(f"👉 **{(conv_val * 0.0980665):.2f} MPa**")
    elif conv_mode == "MPa ➡️ kgf/cm²":
        st.success(f"👉 **{(conv_val * 10.1972):.2f} kgf/cm²**")
    elif conv_mode == "Bar ➡️ MPa":
        st.success(f"👉 **{(conv_val * 0.1):.2f} MPa**")
    st.write("")

    # 11. 불량 대처 퀵 가이드
    st.markdown("<div class='side-panel-header'>📖 불량 대처 가이드</div>", unsafe_allow_html=True)
    with st.expander("주요 불량 발생 시 긴급 조치"):
        st.markdown("""
        - **흑점 (Chấm đen):** 스크류 청소 및 온도 하향
        - **미성형 (Thiếu liệu):** 보압 시간 및 사출 압력 증가
        - **스크래치 (Xước):** 취출 로봇 궤적 점검
        - **오염 (Bẩn):** 금형 표면 및 파팅라인 세척
        """)
    st.write("")

    # 12. 현장 핫라인
    st.markdown("<div class='side-panel-header'>📞 긴급 연락처 (Hotline)</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:14px; line-height:1.8;'>
    👨‍🔧 <b>보전팀 (Bảo trì):</b> 090-1234-5678<br>
    👨‍🔬 <b>품질팀 (QC):</b> 090-8765-4321<br>
    🚨 <b>공장장 (GĐ):</b> 091-1111-2222
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # 13. 포스트잇 메모장
    st.markdown("<div class='side-panel-header'>📝 현장 순찰 메모장</div>", unsafe_allow_html=True)
    st.text_area("새로고침 전까지 임시 보관됩니다.", height=120, placeholder="특이사항을 메모하세요...", label_visibility="collapsed")
    st.write("")

    # 14. [신규] 대시보드 모바일 접속 QR 코드
    st.markdown("<div class='side-panel-header'>📱 모바일 대시보드 연결</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;">
        <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://fursys-dashboard.com" style="border-radius: 10px; border: 1px solid #D1D1D6; padding: 5px; background: white;">
        <div style="font-size:12px; color:#6E6E73; margin-top:5px; font-weight: bold;">스마트폰 카메라로 스캔하세요</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)