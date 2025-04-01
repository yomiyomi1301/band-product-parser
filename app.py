
import streamlit as st
import re
import pandas as pd

st.set_page_config(page_title="밴드 상품 정리기", layout="wide")
st.title("📦 밴드 상품 붙여넣기 자동 정리기")

text = st.text_area("밴드 게시글 복사해서 붙여넣기 ✂️", height=400)
process = st.button("✅ 정리하기")

def split_unit_from_name(name):
    unit_keywords = ["한송이", "한봉", "한팩", "한단", "1개", "1봉", "1팩", "1단", "1세트", "한세트"]
    for keyword in unit_keywords:
        if keyword in name:
            return name.replace(keyword, "").strip(), keyword
    return name.strip(), ""

def parse_product_lines(lines):
    data = []
    current_name = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if "👉" not in line and re.search(r"[가-힣]", line):
            current_name = re.sub(r"^[^가-힣]*", "", line)
        elif "👉" in line:
            prices = re.findall(r"(\d+[,.]?\d*)원", line.replace(",", ""))
            units = re.findall(r"(\d+[개봉팩단통세트송이]+|한[개봉팩단통세트송이]+)", line)
            name_only, extracted_unit = split_unit_from_name(current_name)
            if prices:
                if len(prices) == 1:
                    price = f"{int(float(prices[0])):,}원"
                    unit = units[0] if units else extracted_unit
                    data.append([name_only, unit, price, "", ""])
                elif len(prices) >= 2:
                    price1 = f"{int(float(prices[0])):,}원"
                    price2 = f"{int(float(prices[1])):,}원"
                    unit1 = units[0] if len(units) >= 1 else extracted_unit
                    unit2 = units[1] if len(units) >= 2 else unit1
                    data.append([name_only, unit1, price1, "", ""])
                    data.append([name_only, unit2 + " (2개이상 시)", price2, "", ""])
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
