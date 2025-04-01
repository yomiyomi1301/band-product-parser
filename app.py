
import streamlit as st
import pandas as pd
import re
import io

st.title("📋 밴드 상품 정리표 - 2줄 출력 (2개이상 시 표기, 생략 가능)")

input_text = st.text_area("밴드 게시글 붙여넣기 ✂️", height=300)

if st.button("정리하기"):
    rows = []
    last_item_name = ""

    for line in input_text.splitlines():
        line = line.strip()
        if not line:
            continue

        # 가격 두 개 있는 경우
        price_matches = re.findall(r"(\d{1,3}(?:,\d{3})?원)", line)
        if price_matches:
            # 단가 추출
            price1 = price_matches[0]
            price2 = price_matches[1] if len(price_matches) > 1 else ""

            # 단위 추출
            item_name = last_item_name if last_item_name else "상품명 없음"
            unit_match = re.search(r"(한|\d+)\s*(봉|팩|세트|개|포|단|병|입|줄|통|L|ml|g|장|P|개입|묶음)?(\(.*?\))?", item_name)
            unit = unit_match.group(0) if unit_match else ""

            # 첫 줄: 상품명 + 단가
            rows.append({
                "상품명": item_name,
                "단위": unit,
                "단가": price1,
                "구매수량": "",
                "실수량": ""
            })

            # 두 번째 줄: 2개 이상 가격 (있을 경우만 추가)
            if price2:
                rows.append({
                    "상품명": f"{item_name} (2개이상 시)",
                    "단위": unit,
                    "단가": price2,
                    "구매수량": "",
                    "실수량": ""
                })
            last_item_name = ""
        else:
            last_item_name = re.sub(r"[📣⭕️❇️✴️👉➡️💥🎂🎁🧼👕🍓🧀🌽🍑🥬🥕🍖🚚⭐️🥩🔉🟡🎈🧨]+", "", line).strip()

    if rows:
        df = pd.DataFrame(rows)
        st.success("정리 완료! 아래에서 엑셀로 저장할 수 있어요 ✅")
        st.dataframe(df)

        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        st.download_button(
            label="📥 엑셀로 저장하기 (2줄 조건 출력)",
            data=output.getvalue(),
            file_name="2줄출력_상품정리표_조건형.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("상품명과 가격이 감지되지 않았어요 😢")
