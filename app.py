
import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.title("📦 밴드 상품 정리기 - 모닝특가 & 공구")

input_text = st.text_area("밴드 게시물 복사해서 여기에 붙여넣기 ✂️", height=300)

if st.button("정리하기"):
    data = []

    # 날짜 패턴
    reserve_date = re.search(r"예약.*?(\d{1,2})[\uC6D4\.\/]\s*(\d{1,2})\D*?([오전오후]*\s*\d{1,2}(?::\d{2})?)?", input_text)
    receive_date = re.search(r"수령.*?(\d{1,2})[\uC6D4\.\/]\s*(\d{1,2})", input_text)

    for line in input_text.splitlines():
        match = re.search(r"([\w\s\(\)]+)\s*(\d+(?:,\d+)?원)", line)
        if match:
            item_name = match.group(1).strip()
            price = match.group(2).strip()
            qty_match = re.search(r"(\d+\s*[a-zA-Z가-힣]+)?", item_name)
            qty = qty_match.group(1) if qty_match else ""

            data.append({
                "상품명": item_name,
                "가격": price,
                "수량/단위": qty,
                "예약마감": f"2025-{reserve_date.group(1).zfill(2)}-{reserve_date.group(2).zfill(2)} {reserve_date.group(3) if reserve_date and reserve_date.lastindex == 3 else ''}" if reserve_date else "",
                "수령일": f"2025-{receive_date.group(1).zfill(2)}-{receive_date.group(2).zfill(2)} 오후" if receive_date else "",
                "비고": ""
            })

    if data:
        df = pd.DataFrame(data)
        st.success("정리 완료! 아래에서 엑셀로 저장할 수 있어요 ✅")
        st.dataframe(df)

        # 엑셀 다운로드
        def convert_df(df):
            return df.to_excel(index=False, engine='openpyxl')

        st.download_button(
            label="📥 엑셀로 저장하기",
            data=convert_df(df),
            file_name="상품정리결과.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("상품과 가격 정보가 감지되지 않았어요 😢")
