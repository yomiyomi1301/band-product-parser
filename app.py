
import streamlit as st
import re
import pandas as pd

st.set_page_config(page_title="밴드 상품 정리기", layout="wide")
st.title("📦 밴드 상품 붙여넣기 자동 정리기")

text = st.text_area("밴드 게시글 복사해서 붙여넣기 ✂️", height=400)
process = st.button("✅ 정리하기")

def split_unit_from_name(name):
    unit_keywords = ["한송이", "한봉", "한팩", "한단", "1개", "1봉", "1팩", "1단", "1병", "2병", 
                     "1세트", "한세트", "KG", "kg", "g", "ml", "인분"]
    for keyword in unit_keywords:
        if keyword in name:
            return name.replace(keyword, "").strip(), keyword
    # 괄호 안 단위 추출 시도
    match = re.search(r"(\(.*?\))", name)
    if match:
        return name.replace(match.group(1), "").strip(), match.group(1)
    return name.strip(), ""

def parse_product_lines(lines):
    data = []
    current_name = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "👉" not in line and any(char.isalpha() or '\uac00' <= char <= '\ud7a3' for char in line):
            current_name = re.sub(r"^[^가-힣a-zA-Z]*", "", line)
        elif "👉" in line:
            line = line.replace(",", "").replace("→", "➡")
            discount_price_match = re.search(r"➡.*?(\d+[,.]?\d*)원", line)
            if discount_price_match:
                prices = [discount_price_match.group(1)]
            else:
                prices = re.findall(r"(\d+[,.]?\d*)원", line)
            units = re.findall(r"(1[개봉병팩단세트줄]+|2[개봉병팩단세트줄]+|한[개봉병팩단세트줄]+|\d+g|\d+ml|\d+KG|\d+인분)", line)
            name_only, extracted_unit = split_unit_from_name(current_name)
            if prices:
                price = f"{int(float(prices[-1].replace(',', ''))):,}원"  # 할인 가격만 사용
                unit = units[0] if units else extracted_unit
                data.append([name_only, unit, price, "", ""])
    return data

if process and text:
    lines = text.split("\n")
    parsed = parse_product_lines(lines)
    if parsed:
        df = pd.DataFrame(parsed, columns=["상품명", "단위", "단가", "주문수량", "실수량"])
        st.success("✅ 정리 완료! 아래에서 복사하거나 다운로드하세요.")
        st.dataframe(df, use_container_width=True, height=len(df) * 35 + 50)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 엑셀로 다운로드", csv, file_name="band_products.csv", mime="text/csv")
    else:
        st.warning("상품 정보가 정상적으로 감지되지 않았어요. 다시 확인해 주세요.")
