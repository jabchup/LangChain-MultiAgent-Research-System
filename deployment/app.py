import sys
from pathlib import Path

# Put the repo root (parent of the "deployment" folder) on the import path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from deployment.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)

# ================================
# PAGE CONFIG
# ================================
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔍",
    layout="centered",
)

st.title("🔍 Multi-Agent Research System")
st.caption("Search → Read → Write → Critique, powered by LangChain + LangGraph")

# ================================
# INPUT
# ================================
topic = st.text_input(
    "Research topic",
    placeholder="e.g. The impact of AI on renewable energy",
)

run = st.button("Run Research", type="primary", disabled=not topic.strip())

# ================================
# PIPELINE (4 agents, live feedback)
# ================================
if run:
    state = {}

    # ---- Step 01: Search ----
    with st.status("Step 01 — Search agent is gathering sources...", expanded=False) as s:
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = search_result["messages"][-1].content
        s.update(label="Step 01 — Search complete ✅", state="complete")

    # ---- Step 02: Read/Scrape ----
    with st.status("Step 02 — Reader agent is scraping the best source...", expanded=False) as s:
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:5800]}"
            )]
        })
        state["scraped_content"] = reader_result["messages"][-1].content
        s.update(label="Step 02 — Reading complete ✅", state="complete")

    # ---- Step 03: Write ----
    with st.status("Step 03 — Writer is drafting the report...", expanded=False) as s:
        research_combined = f"SEARCH RESULTS:\n{state['scraped_content']}"
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })
        s.update(label="Step 03 — Report drafted ✅", state="complete")

    # ---- Step 04: Critique ----
    with st.status("Step 04 — Critic is reviewing the report...", expanded=False) as s:
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        s.update(label="Step 04 — Review complete ✅", state="complete")

    # ================================
    # RESULTS
    # ================================
    st.success("Research complete!")

    report_tab, critic_tab, raw_tab = st.tabs(["📄 Report", "🧐 Critic", "🔎 Raw research"])

    with report_tab:
        st.markdown(state["report"])
        st.download_button(
            "Download report (.md)",
            data=state["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with critic_tab:
        st.markdown(state["feedback"])

    with raw_tab:
        with st.expander("Search results"):
            st.write(state["search_results"])
        with st.expander("Scraped content"):
            st.write(state["scraped_content"])