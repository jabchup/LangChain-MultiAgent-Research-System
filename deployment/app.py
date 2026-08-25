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
    layout="wide",
)

# ================================
# MINIMAL STYLING
# ================================
st.markdown("""
<style>
.stApp { background: #0b1120; }
.block-container { padding-top: 3rem; max-width: 1100px; }

.label { color:#38bdf8; font-size:.72rem; letter-spacing:.15em; font-weight:700; }

/* gradient run button */
div.stButton > button {
    width: 100%;
    background: linear-gradient(90deg,#38bdf8,#6366f1,#a855f7);
    color: #fff; border: none; border-radius: 12px;
    padding: .7rem; font-weight: 700; font-size: 1rem;
}
div.stButton > button:hover { filter: brightness(1.1); }

/* agent cards */
.card {
    background:#111827; border:1px solid #1f2937; border-radius:14px;
    padding:1rem 1.2rem; margin-bottom:.9rem;
}
.card .num { color:#6366f1; font-weight:700; margin-right:.4rem; }
.card .name { color:#e5e7eb; font-weight:700; font-size:1.05rem; }
.card .desc { color:#94a3b8; font-size:.85rem; margin-top:.25rem; }
.pill { float:right; font-size:.65rem; letter-spacing:.12em; font-weight:700;
        padding:.15rem .5rem; border-radius:6px; }
.waiting { color:#64748b; background:#1e293b; }
.running { color:#0b1120; background:#38bdf8; }
.done    { color:#0b1120; background:#22c55e; }

.hero {
    text-align: center;
    padding: 1.6rem 1rem 2rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #1f2937;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(90deg,#38bdf8,#6366f1,#a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    color: #94a3b8;
    font-size: .95rem;
    margin-top: .4rem;
    letter-spacing: .02em;
}
</style>
""", unsafe_allow_html=True)

# ================================
# AGENT CARD HELPERS
# ================================
AGENTS = [
    ("01", "Search Agent", "Gathers recent web information"),
    ("02", "Reader Agent", "Scrapes &amp; extracts deep content"),
    ("03", "Writer Chain", "Drafts the full research report"),
    ("04", "Critic Chain", "Reviews &amp; scores the report"),
]
STATUS = {"waiting": "WAITING", "running": "RUNNING", "done": "DONE"}


def card_html(num, name, desc, status):
    return f"""
    <div class="card">
        <span class="pill {status}">{STATUS[status]}</span>
        <span class="num">#{num}</span><span class="name">{name}</span>
        <div class="desc">{desc}</div>
    </div>
    """


def render_cards(slot, statuses):
    slot.markdown(
        "".join(card_html(*AGENTS[i], statuses[i]) for i in range(4)),
        unsafe_allow_html=True,
    )

# ================================
# HERO HEADER
# ================================
st.markdown("""
<div class="hero">
    <div class="hero-title">🔍 Multi-Agent Research System</div>
    <div class="hero-sub">Search → Read → Write → Critique &nbsp;·&nbsp; powered by LangChain + LangGraph</div>
</div>
""", unsafe_allow_html=True)

# ================================
# LAYOUT
# ================================
if "topic" not in st.session_state:
    st.session_state.topic = ""

left, right = st.columns([1, 1], gap="large")

with left:
    st.markdown('<div class="label">RESEARCH TOPIC</div>', unsafe_allow_html=True)

    with st.form("research_form"):
        topic = st.text_input(
            "topic", key="topic", label_visibility="collapsed",
            placeholder="e.g. Roadmap for AGI development in next 5 years",
        )
        run = st.form_submit_button("⚡ Run Research Pipeline")

    st.markdown('<div class="label" style="margin-top:1rem;">TRY</div>', unsafe_allow_html=True)
    examples = [
        "Future of LLM in Tech Industry",
        "All Latest AI Agents in 2026",
        "Roadmap for AGI development in next 5 years",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state.topic = ex
            st.rerun()

with right:
    cards_slot = st.empty()
    statuses = ["waiting"] * 4
    render_cards(cards_slot, statuses)

# ================================
# PIPELINE
# ================================
if run:
    state = {}

    def step(i, label, fn):
        statuses[i] = "running"; render_cards(cards_slot, statuses)
        with st.spinner(label):
            fn()
        statuses[i] = "done"; render_cards(cards_slot, statuses)

    def do_search():
        agent = build_search_agent()
        r = agent.invoke({"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]})
        state["search_results"] = r["messages"][-1].content

    def do_read():
        agent = build_reader_agent()
        r = agent.invoke({"messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:5800]}")]})
        state["scraped_content"] = r["messages"][-1].content

    def do_write():
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": f"SEARCH RESULTS:\n{state['scraped_content']}",
        })

    def do_critic():
        state["feedback"] = critic_chain.invoke({"report": state["report"]})

    step(0, "🔍 Search agent is gathering sources...", do_search)
    step(1, "📖 Reader agent is scraping the best source...", do_read)
    step(2, "✍️ Writer is drafting the report...", do_write)
    step(3, "🧐 Critic is reviewing the report...", do_critic)

        # ================================
    # RESULTS
    # ================================
    st.markdown("---")
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