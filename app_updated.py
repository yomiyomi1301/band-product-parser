
import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="밴드 상품 정리표 - 프린트용 (A4 현장 수량체크)", layout="wide")

st.title("📋 밴드 상품 정리표 - 프린트용 (A4 현장 수량체크)")

text_input = st.text_area("밴드 게시글 붙여넣기 ✂", height=400)

unit_keywords = ["세트", "줄", "개", "병", "팩", "봉", "묶음", "kg", "g", "ml", "L", "통", "단", "묶음", "포", "판", "미", "입"]
unit_pattern = "|".join(unit_keywords)

def extract_price_and_unit(line):
    # 할인 가격 추출
    discount_match = re.search(r"➡️.*?([\d,]+)원", line)
    if discount_match:
        price = discount_match.group(1).replace(",", "")
    else:
        price_match = re.search(r"👉.*?([\d,]+)원", line)
        price = price_match.group(1).replace(",", "") if price_match else None

    # 단위 추출
    unit_match = re.search(r"(\d+\s*(" + unit_pattern + r"))", line, re.IGNORECASE)
    unit = unit_match.group(1).strip() if unit_match else ""

    return price, unit

def clean_name(name):
    name = re.sub(r"\d+\s*(" + unit_pattern + r")", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\([^)]*\)", "", name)  # 괄호 안 제거
    name = re.sub(r"\d+g|\d+ml|\d+KG|\d+L", "", name, flags=re.IGNORECASE)
    return name.strip(" :-👉➡️💥")

def parse_entries(text):
    lines = text.split("\n")
    data = []

    for i, line in enumerate(lines):
        if "👉" in line:
            previous_lines = lines[max(0, i - 3):i]
            possible_name = ""
            for pl in reversed(previous_lines):
                if any(c.isalpha() for c in pl):
                    possible_name = pl
                    break
            price, unit = extract_price_and_unit(line)
            name = clean_name(possible_name)

            if not name:
                continue  # 이름 없으면 건너뛰기
            if not price:
                continue  # 가격 없으면 건너뛰기

            data.append({
                "상품명": name,
                "단위": unit,
                "단가": f"{int(price):,}원",
                "주문수량": "",
                "실수량": ""
            })

    return pd.DataFrame(data)

if st.button("정리하기"):
    if text_input.strip():
        df = parse_entries(text_input)
        st.success("정리 완료! 아래에서 A4 인쇄용 표가 완성됐어요 ✅")
        st.dataframe(df, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="📥 엑셀로 저장하기 (2줄 조건 출력)",
            data=output.getvalue(),
            file_name="정리된_상품표.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("게시글을 붙여넣어주세요!")
