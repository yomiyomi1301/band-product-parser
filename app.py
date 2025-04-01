
import streamlit as st
import pandas as pd
import re
import io

st.title("📋 밴드 상품 정리표 - 프린트용 (A4 현장 수량체크)")

input_text = st.text_area("밴드 게시글 붙여넣기 ✂️", height=300)

if st.button("정리하기"):
    data = []
    last_item_name = ""

    for line in input_text.splitlines():
        line = line.strip()
        if not line:
            continue

        price_matches = re.findall(r"(\d{1,3}(?:,\d{3})?원)", line)
        if price_matches:
            price = price_matches[-1] if "행사" in line or "➡️" in line or "할인" in line or "💥" in line else price_matches[0]
            item_name = last_item_name if last_item_name else "상품명 없음"
            unit_match = re.search(r"(\d+\s*[a-zA-Z가-힣\(\)]+)", item_name)
            unit = unit_match.group(1) if unit_match else ""

            data.append({
                "상품명": item_name,
                "단위": unit,
                "단가": price,
                "주문수량": "",
                "실수량": ""
            })
            last_item_name = ""
        else:
            last_item_name = re.sub(r"[📣⭕️❇️✴️👉➡️💥🎂🎁🧼👕🍓🧀🌽🍑🥬🥕🍖🚚]+", "", line).strip()

    if data:
        df = pd.DataFrame(data)
        st.success("정리 완료! A4 인쇄용 표가 완성됐어요 ✅")
        st.dataframe(df)

        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 엑셀로 저장하기 (프린트용)",
            data=output.getvalue(),
            file_name="모닝특가_공구_수량체크표.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("상품명과 가격이 감지되지 않았어요 😢")
