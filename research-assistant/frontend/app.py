import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Multi-Agent Research App",
    layout="centered"
)

st.markdown(
    """
    <style>
    body { background-color: black; color: white; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AI Research Outline Generator")

st.markdown("""
Generate comprehensive research outlines powered by AI agents. Enter any topic and our multi-agent system will search the web, 
scrape relevant sources, and synthesize information into a structured outline with summaries.
""")

# Initialize session state
if "outline" not in st.session_state:
    st.session_state.outline = None
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

st.markdown("""
<style>
div[data-testid="stFormSubmitButton"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

with st.form(key=f"research_form_{st.session_state.form_key}"):
    topic = st.text_input("Enter research topic")
    submit_button = st.form_submit_button("Generate Outline")

if submit_button and topic:
    with st.spinner("Running multi-agent research..."):
        # Local development
        # backend_url = "http://0.0.0.0:8000"
        
        # Railway deployment (uncomment for Railway)
        backend_url = os.getenv("BACKEND_URL", "http://backend:8000")
        
        res = requests.post(
            f"{backend_url}/research",
            json={"topic": topic}
        )
        st.session_state.outline = res.json()["outline"]

if st.session_state.outline:
    st.text_area("Outline", st.session_state.outline, height=400)
    
    if st.button("Clear"):
        st.session_state.outline = None
        st.session_state.form_key += 1
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: #9CA3AF; font-size: 0.875rem; padding: 1rem 0;">
        © {2026} maria c. lima | 
        <a href="mailto:maria.lima.hub@gmail.com" style="color: #9CA3AF; text-decoration: none;">
            📧 maria.lima.hub@gmail.com
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
