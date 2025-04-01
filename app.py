
import streamlit as st
import re
import pandas as pd
from io import BytesIO

st.set_page_config(layout="wide")
st.title("📦 밴드 상품 정리표 - 프린트용 (A4 현장 수량체크)")

text_input = st.text_area("밴드 게시글 붙여넣기 ✂️", height=300)

# 단위 후보 리스트
UNITS = ["한세트", "1세트", "2세트", "세트", "개", "병", "팩", "봉", "줄", "망", "통", "단", "g", "kg", "KG", "ml", "L", "포", "장"]

# 단위 패턴 생성
unit_pattern = r"(\d+\s*(?:{}))".format("|".join(map(re.escape, UNITS)))

def extract_price(text):
    match = re.search(r"[➡→]\s*.*?(\d{1,3}(,\d{3})*)원", text)
    if not match:
        match = re.search(r"(\d{1,3}(,\d{3})*)원", text)
    return match.group(1) + "원" if match else ""

def extract_unit_and_name(name):
    unit = ""
    for u in UNITS:
        if u in name:
            unit = u
            name = name.replace(u, "").strip()
            break
    return name.strip(), unit

def parse_products(text):
    lines = text.split("\n")
    products = []
    current_name = ""
    for line in lines:
        if not line.strip():
            continue
        price = extract_price(line)
        if price:
            name_line = current_name
            name_line, unit = extract_unit_and_name(name_line)
            products.append({"상품명": name_line, "단위": unit, "단가": price})
        else:
            current_name = re.sub(r"^[\W\d]+", "", line).strip()
    return products

if text_input:
    product_data = parse_products(text_input)
    df = pd.DataFrame(product_data)
    df["주문수량"] = ""
    df["실수량"] = ""

    st.success("정리 완료! 아래에서 엑셀로 저장할 수 있어요 ✅")
    st.dataframe(df, use_container_width=True)

    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    excel_data = convert_df_to_excel(df)
    st.download_button(
        label="📥 엑셀로 저장하기 (2줄 조건 출력)",
        data=excel_data,
        file_name="정리된_상품표.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.divider()
    st.button("정리하기")
