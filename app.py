
import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="밴드 상품 정리기", layout="wide")

st.title("📦 밴드 상품 정리표 - 프린트용 (A4 현장 수량체크)")
st.caption("밴드 게시글을 붙여넣기 ✂️")

text = st.text_area(" ", height=300)

def extract_products(text):
    lines = text.split("\n")
    products = []
    current_name = ""
    current_unit = ""
    current_price = ""

    for line in lines:
        line = line.strip()

        if "👉" in line:
            items = re.findall(r"(?P<unit>\d+[a-zA-Z가-힣]*)\s*(\([^\)]+\))?\s*[➡→→~]*\s*([\d,]+)원", line)
            if items:
                for item in items:
                    unit = item[0]
                    price = item[2]
                    if current_name:
                        products.append([current_name.strip(), unit.strip(), f"{price}원"])
            continue

        if "➡️" in line and "원" in line:
            # 할인 표기
            parts = re.split(r"[➡→~]", line)
            if len(parts) > 1:
                price_part = parts[-1]
                price_match = re.search(r"(\d{1,3}(,\d{3})*)원", price_part)
                if price_match and current_name:
                    products.append([current_name.strip(), "", price_match.group(1) + "원"])
            continue

        if any(unit in line for unit in ["개", "g", "ml", "KG", "세트", "팩", "병", "단", "송이"]):
            name_line = re.sub(r"^[^가-힣A-Za-z]*", "", line)
            current_name = name_line.strip()

    return pd.DataFrame(products, columns=["상품명", "단위", "단가"])

if st.button("정리하기"):
    if text.strip():
        df = extract_products(text)
        st.success("정리 완료! 아래에서 엑셀로 저장할 수 있어요 ✅")
        st.dataframe(df, use_container_width=True)

        file_path = "/mnt/data/정리된_상품표.xlsx"
        df.to_excel(file_path, index=False)
        with open(file_path, "rb") as f:
            st.download_button(
                label="📥 엑셀로 저장하기",
                data=f,
                file_name="정리된_상품표.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.warning("게시글을 먼저 붙여넣어주세요.")
