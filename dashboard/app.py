import streamlit as st

st.set_page_config(
    page_title="川渝金融舆情分析",
    page_icon="📊",
    layout="wide",
)

pg = st.navigation({
    "川渝金融舆情": [
        st.Page("pages/overview.py", title="市场总览", default=True),
        st.Page("pages/company.py", title="公司详情"),
    ],
})
pg.run()
