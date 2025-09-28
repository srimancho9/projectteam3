import streamlit as st
from agents.summarize_agent import SummarizeTool
from agents.writer_agent import write_research_paragraph
from agents.redactor_agent import redact_phi

st.set_page_config(page_title="Multi-Agent AI App", page_icon="🤖", layout="wide")
st.title("🤖 Multi-Agent AI App")

tab1, tab2, tab3 = st.tabs(["Summarizer", "Research Writer", "PHI/PII Redactor"])

with tab1:
    st.subheader("Summarize Medical Text")
    txt = st.text_area("Paste medical text:", height=200, key="sum_text")
    uploaded_file = st.file_uploader("Or upload a PDF", type=["pdf"])
    if st.button("Summarize"):
        tool = SummarizeTool()
        if uploaded_file is not None:
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.read())
            out = tool.execute_pdf("temp.pdf")
        elif txt.strip():
            out = tool.execute(txt)
        else:
            out = "Please provide text or upload a PDF."
        st.markdown(out)

with tab2:
    st.subheader("Research Writer")
    topic = st.text_input("Topic", value="Impact of AI on healthcare")
    refs_hint = st.text_input("Optional refs hint", value="")
    if st.button("Generate"):
        out = write_research_paragraph(topic, refs_hint)
        st.markdown(out)

with tab3:
    st.subheader("PHI/PII Redactor")
    raw = st.text_area("Paste text:", height=200, key="phi_text")
    if st.button("Redact"):
        st.code(redact_phi(raw), language="text")
