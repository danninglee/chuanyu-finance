import streamlit as st
from dashboard.pages.overview import show as overview_show
from dashboard.pages.company import show as company_show

st.set_page_config(
    page_title="川渝金融舆情分析",
    page_icon="📊",
    layout="wide",
)

pg = st.navigation({
    "川渝金融舆情": [
        st.Page(overview_show, title="市场总览", url_path="overview", default=True),
        st.Page(company_show, title="公司详情", url_path="company"),
    ],
})
pg.run()
