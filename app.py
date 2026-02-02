import streamlit as st

st.set_page_config(
    page_title="Operar Analysis",
    page_icon="💸",
)

st.write("# Welcome to Operar Analysis! 👋")

st.markdown(
    """
    Select a dashboard from the sidebar to view analysis.
    
    **Available Dashboards:**
    - **CEDEARs Analysis**: Daily performance and correlation with Gold.
    """
)

st.sidebar.success("Select a demo above.")
