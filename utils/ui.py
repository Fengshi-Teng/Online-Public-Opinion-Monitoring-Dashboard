import streamlit as st

def load_custom_css(css_file_path: str):
    """
    Load custom CSS from a local file and inject it into the Streamlit app.
    """
    with open(css_file_path, "r") as f:
        css_content = f.read()
    
    # Inject the CSS into the Streamlit page
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)