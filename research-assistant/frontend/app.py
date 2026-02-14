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
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = ""

# Suggested topics
st.markdown("**Try these examples:**")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Climate Change Effects", use_container_width=True):
        st.session_state.selected_topic = "climate change effects on polar bears"
        st.session_state.auto_submit = True
        st.rerun()
        
with col2:
    if st.button("Quantum Computing", use_container_width=True):
        st.session_state.selected_topic = "latest developments in quantum computing"
        st.session_state.auto_submit = True
        st.rerun()
        
with col3:
    if st.button("Mediterranean Diet", use_container_width=True):
        st.session_state.selected_topic = "benefits of Mediterranean diet"
        st.session_state.auto_submit = True
        st.rerun()

st.markdown("""
<style>
div[data-testid="stFormSubmitButton"] {
    display: none;
}
.footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 0.875rem;
    padding: 1rem 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}
.footer a {
    color: #9CA3AF;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}
.footer svg {
    width: 1rem;
    height: 1rem;
}
</style>
""", unsafe_allow_html=True)

with st.form(key=f"research_form_{st.session_state.form_key}"):
    topic = st.text_input("Enter research topic", value=st.session_state.selected_topic)
    submit_button = st.form_submit_button("Generate Outline")

# Auto-submit if button was clicked
if st.session_state.get("auto_submit", False):
    st.session_state.auto_submit = False
    topic = st.session_state.selected_topic
    submit_button = True

if submit_button and topic:
    st.session_state.selected_topic = ""
    with st.spinner("Running multi-agent research..."):
        backend_url = os.getenv("BACKEND_URL", "http://0.0.0.0:8000")
        
        res = requests.post(
            f"{backend_url}/research",
            json={"topic": topic}
        )
        st.session_state.outline = res.json()["outline"]

if st.session_state.outline:
    st.markdown(st.session_state.outline)
    
    if st.button("Clear"):
        st.session_state.outline = None
        st.session_state.form_key += 1
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div class="footer">
        <span>© {2026} maria c. lima</span>
        <span>|</span>
        <a href="mailto:maria.lima.hub@gmail.com">
            <svg fill="currentColor" viewBox="0 0 24 24">
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
            </svg>
            <span>maria.lima.hub@gmail.com</span>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)
