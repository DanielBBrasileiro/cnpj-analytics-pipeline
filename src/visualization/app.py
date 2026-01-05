import streamlit as st
import plotly.express as px
from queries import get_total_cnaes, get_cnaes_by_sector, search_cnae

# Page Configuration
st.set_page_config(page_title="CNPJ Analytics", layout="wide")

# Header
st.title("CNPJ Data Lakehouse Analytics")
st.markdown("Exploration of public data from the Federal Revenue Service (Gold Layer).")

# Metrics (KPIs)
col1, col2, col3 = st.columns(3)
total = get_total_cnaes()
col1.metric("Total Activities (CNAEs)", f"{total:,}".replace(",", "."))

st.divider()

# Sector Chart
st.subheader("Top 10 Sectors (Grouped by Prefix)")
df_sector = get_cnaes_by_sector()

# Bar Chart with Plotly
fig = px.bar(
    df_sector, 
    x='setor', 
    y='quantidade', 
    title='Distribution of Activities by Group',
    labels={'setor': 'CNAE Prefix', 'quantidade': 'Activity Count'},
    color='quantidade'
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Search Tool
st.subheader("Activity Search")
termo = st.text_input("Enter an activity (e.g., Cultivation, Software, Data)")

if termo:
    df_search = search_cnae(termo)
    if not df_search.empty:
        st.dataframe(df_search, use_container_width=True, hide_index=True)
    else:
        st.warning("No activities found with this term.")
