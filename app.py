
import streamlit as st
import re
import pandas as pd

st.set_page_config(page_title="밴드 상품 정리기", layout="wide")

st.title("📦 밴드 상품 붙여넣기 자동 정리기")

text = st.text_area("밴드 게시글 복사해서 붙여넣기 ✂️", height=400)

def parse_product_lines(lines):
    data = []
    current_name = ""
    for i, line in enumerate(lines):
        line = line.strip()
        # 상품명 추출
        if not line:
            continue
        if "👉" not in line and re.search(r"[가-힣]", line):
            current_name = re.sub(r"^[^가-힣]*", "", line)
        # 단가 줄
        elif "👉" in line:
            prices = re.findall(r"(\d+[,.]?\d*)원", line.replace(",", ""))
            units = re.findall(r"(\d+[개봉팩단통세트송이]+|한[개봉팩단통세트송이]+)", line)
            if prices:
                if len(prices) == 1:
                    price = f"{int(float(prices[0])):,}원"
                    unit = units[0] if units else ""
                    data.append([current_name.strip(), unit, price])
                elif len(prices) >= 2:
                    price1 = f"{int(float(prices[0])):,}원"
                    price2 = f"{int(float(prices[1])):,}원"
                    unit1 = units[0] if len(units) >= 1 else ""
                    unit2 = units[1] if len(units) >= 2 else unit1
                    data.append([current_name.strip(), unit1, price1])
                    data.append([current_name.strip(), unit2 + " (2개이상 시)", price2])
    return data

if text:
    lines = text.split("\n")
    parsed = parse_product_lines(lines)
    if parsed:
        df = pd.DataFrame(parsed, columns=["상품명", "단위", "단가"])
        st.success("✅ 정리 완료! 아래에서 복사하거나 다운로드하세요.")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("📥 엑셀로 다운로드", csv, file_name="band_products.csv", mime="text/csv")
    else:
        st.warning("상품 정보가 정상적으로 감지되지 않았어요. 다시 확인해 주세요.")
