import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# Page config
st.set_page_config(
    page_title="DeepResearchMind | AI Research Agent",
    page_icon="D",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS - Full redesign with Source Code Pro + custom palette
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'Source Code Pro', monospace;
    color: #FFFFFF;
}

.stApp {
    background: #000000;
    background-image:
        radial-gradient(ellipse 90% 60% at 15% -15%, rgba(126,59,237,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 85% 105%, rgba(198,255,52,0.05) 0%, transparent 50%),
        radial-gradient(circle 800px at 50% 50%, rgba(126,59,237,0.03) 0%, transparent 100%);
}

/* Subtle dot grid overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: radial-gradient(rgba(126,59,237,0.07) 1px, transparent 1px);
    background-size: 24px 24px;
    pointer-events: none;
    z-index: 0;
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; position: relative; z-index: 1; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    position: relative;
}
.hero-badge {
    display: inline-block;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #C6FF34;
    background: rgba(198,255,52,0.08);
    border: 1px solid rgba(198,255,52,0.2);
    border-radius: 4px;
    padding: 0.4rem 1.2rem;
    margin-bottom: 1.5rem;
}
.hero h1 {
    font-family: 'Source Code Pro', monospace;
    font-size: clamp(2.4rem, 5.5vw, 4.2rem);
    font-weight: 800;
    line-height: 1.05;
    letter-spacing: -0.04em;
    color: #FFFFFF;
    margin: 0 0 1rem;
}
.hero h1 .accent {
    color: #7E3BED;
}
.hero h1 .highlight {
    color: #C6FF34;
}
.hero-sub {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.85rem;
    font-weight: 400;
    color: rgba(255,255,255,0.45);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(126,59,237,0.35) 30%, rgba(198,255,52,0.2) 70%, transparent 100%);
    margin: 2rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(126,59,237,0.04);
    border: 1px solid rgba(126,59,237,0.18);
    border-radius: 8px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.8rem;
    backdrop-filter: blur(12px);
    position: relative;
}
.input-card::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    border-radius: 9px;
    background: linear-gradient(135deg, rgba(126,59,237,0.15), transparent 50%, rgba(198,255,52,0.08));
    z-index: -1;
    opacity: 0.5;
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(126,59,237,0.3) !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
    font-family: 'Source Code Pro', monospace !important;
    font-size: 0.88rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.25s, box-shadow 0.25s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #7E3BED !important;
    box-shadow: 0 0 0 3px rgba(126,59,237,0.15), 0 0 20px rgba(126,59,237,0.08) !important;
}
.stTextInput > div > div > input::placeholder {
    color: rgba(255,255,255,0.25) !important;
    font-family: 'Source Code Pro', monospace !important;
}
.stTextInput > label {
    font-family: 'Source Code Pro', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #7E3BED !important;
    font-weight: 600 !important;
}

/* ── Button ── */
.stButton > button {
    background: #C6FF34 !important;
    color: #000000 !important;
    font-family: 'Source Code Pro', monospace !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.75rem 2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.2s, background 0.2s !important;
    box-shadow: 0 0 20px rgba(198,255,52,0.2), 0 4px 12px rgba(198,255,52,0.15) !important;
    width: 100%;
}
.stButton > button:hover {
    background: #d4ff5c !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 0 30px rgba(198,255,52,0.3), 0 8px 24px rgba(198,255,52,0.2) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 0 15px rgba(198,255,52,0.15) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 6px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}
.step-card.active {
    border-color: rgba(126,59,237,0.5);
    background: rgba(126,59,237,0.06);
    box-shadow: 0 0 25px rgba(126,59,237,0.08);
}
.step-card.done {
    border-color: rgba(198,255,52,0.3);
    background: rgba(198,255,52,0.03);
}

/* Left accent bar */
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    background: rgba(255,255,255,0.06);
    transition: background 0.3s;
}
.step-card.active::before {
    background: #7E3BED;
    box-shadow: 0 0 8px rgba(126,59,237,0.5);
}
.step-card.done::before {
    background: #C6FF34;
    box-shadow: 0 0 8px rgba(198,255,52,0.4);
}

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.step-num {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    color: rgba(126,59,237,0.7);
}
.step-title {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    color: #FFFFFF;
}
.step-desc {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.3);
    margin-top: 0.25rem;
    padding-left: calc(0.62rem + 0.8rem + 1.5ch);
}
.step-status {
    margin-left: auto;
    font-family: 'Source Code Pro', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.12em;
}
.status-waiting  { color: rgba(255,255,255,0.2); }
.status-running  { color: #7E3BED; }
.status-done     { color: #C6FF34; }

/* Running pulse animation */
@keyframes pulse-purple {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
.status-running {
    animation: pulse-purple 1.5s ease-in-out infinite;
}

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 6px;
    padding: 1.5rem 1.8rem;
    margin-top: 0.8rem;
    margin-bottom: 1.2rem;
}
.result-panel-title {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7E3BED;
    margin-bottom: 1rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(126,59,237,0.15);
}
.result-content {
    font-size: 0.82rem;
    line-height: 1.8;
    color: rgba(255,255,255,0.6);
    white-space: pre-wrap;
    font-family: 'Source Code Pro', monospace;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(126,59,237,0.03);
    border: 1px solid rgba(126,59,237,0.2);
    border-radius: 8px;
    padding: 2rem 2.2rem;
    margin-top: 1rem;
    position: relative;
}
.report-panel::before {
    content: '';
    position: absolute;
    top: -1px; left: -1px; right: -1px; bottom: -1px;
    border-radius: 9px;
    background: linear-gradient(135deg, rgba(126,59,237,0.12), transparent 60%);
    z-index: -1;
}
.feedback-panel {
    background: rgba(198,255,52,0.02);
    border: 1px solid rgba(198,255,52,0.15);
    border-radius: 8px;
    padding: 2rem 2.2rem;
    margin-top: 1rem;
}
.panel-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
}
.panel-label.purple {
    color: #7E3BED;
    border-bottom: 1px solid rgba(126,59,237,0.2);
}
.panel-label.lime {
    color: #C6FF34;
    border-bottom: 1px solid rgba(198,255,52,0.15);
}

/* ── Spinner ── */
.stSpinner > div { color: #7E3BED !important; }

/* ── Expander ── */
details summary {
    font-family: 'Source Code Pro', monospace !important;
    font-size: 0.72rem !important;
    color: rgba(255,255,255,0.4) !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: #C6FF34;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin: 2rem 0 1rem;
}

/* ── Example chips ── */
.chip-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 1.5rem;
}
.chip-label {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.62rem;
    font-weight: 600;
    color: rgba(255,255,255,0.2);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.chip {
    background: rgba(126,59,237,0.06);
    border: 1px solid rgba(126,59,237,0.15);
    border-radius: 4px;
    padding: 0.25rem 0.65rem;
    font-size: 0.7rem;
    color: rgba(255,255,255,0.45);
    font-family: 'Source Code Pro', monospace;
    transition: border-color 0.2s, color 0.2s;
}
.chip:hover {
    border-color: rgba(126,59,237,0.4);
    color: rgba(255,255,255,0.65);
}

/* ── Download button ── */
.stDownloadButton > button {
    background: transparent !important;
    color: #C6FF34 !important;
    font-family: 'Source Code Pro', monospace !important;
    font-weight: 600 !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em !important;
    border: 1px solid rgba(198,255,52,0.3) !important;
    border-radius: 6px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}
.stDownloadButton > button:hover {
    background: rgba(198,255,52,0.08) !important;
    border-color: rgba(198,255,52,0.5) !important;
    box-shadow: 0 0 15px rgba(198,255,52,0.1) !important;
}

/* ── Footer ── */
.footer {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.62rem;
    font-weight: 400;
    color: rgba(255,255,255,0.15);
    text-align: center;
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.04);
    letter-spacing: 0.08em;
}
.footer span.dev {
    color: rgba(126,59,237,0.5);
}

/* ── Markdown content styling ── */
.stMarkdown p, .stMarkdown li {
    font-family: 'Source Code Pro', monospace;
    font-size: 0.85rem;
    line-height: 1.75;
    color: rgba(255,255,255,0.7);
}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Source Code Pro', monospace;
    color: #FFFFFF;
}
.stMarkdown h2 {
    color: #7E3BED;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}
.stMarkdown strong {
    color: #FFFFFF;
    font-weight: 700;
}
.stMarkdown a {
    color: #C6FF34;
    text-decoration: none;
}
.stMarkdown a:hover {
    text-decoration: underline;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #000000; }
::-webkit-scrollbar-thumb { background: rgba(126,59,237,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(126,59,237,0.5); }
</style>
""", unsafe_allow_html=True)


# Helper: render a step card
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("--  IDLE", "status-waiting"),
        "running": (">>  ACTIVE", "status-running"),
        "done":    ("OK  DONE", "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    desc_html = f'<div class="step-desc">{desc}</div>' if desc else ""
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {desc_html}
    </div>
    """, unsafe_allow_html=True)


# Session state init
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# Hero
st.markdown("""
<div class="hero">
    <div class="hero-badge">Multi-Agent AI System</div>
    <h1>Deep<span class="accent">Research</span><span class="highlight">Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate &mdash; searching, scraping, writing
        and critiquing &mdash; to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# Layout: input left, pipeline right
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    chips_html = '<div class="chip-row"><span class="chip-label">Try:</span>'
    for ex in examples:
        chips_html += f'<span class="chip">{ex}</span>'
    chips_html += '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline Status</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        if step in r:
            return "done"
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes and extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews and scores the report")


# Run pipeline
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # Step 1: Search
    with st.spinner("Search Agent is working..."):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    # Step 2: Reader
    with st.spinner("Reader Agent is scraping top resources..."):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # Step 3: Writer
    with st.spinner("Writer is drafting the report..."):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # Step 4: Critic
    with st.spinner("Critic is reviewing the report..."):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# Results display
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("Search Results (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("Scraped Content (raw)", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label purple">Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label lime">Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# Footer
st.markdown("""
<div class="footer">
    DeepResearchMind  //  Powered by LangChain Multi-Agent Pipeline  //  Built with Streamlit  //  <span class="dev">Developed by Akram</span>
</div>
""", unsafe_allow_html=True)