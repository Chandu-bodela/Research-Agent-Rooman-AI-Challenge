"""
pages/4_Analytics.py — Analytics dashboard with Plotly charts.
"""
from __future__ import annotations
from collections import Counter
import streamlit as st
from database.history import get_history, init_db
from frontend.common import configure_page, get_knowledge_base, init_session_state
from frontend.components.footer import render_footer
from frontend.components.sidebar import render_sidebar

configure_page("Analytics", icon="📊")
init_session_state()
init_db()

kb = get_knowledge_base()
render_sidebar(kb)

# ── Navbar ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="rm-navbar rm-animate-fade-in">
        <div class="rm-navbar-brand">📊 Analytics</div>
        <div class="rm-navbar-right">
            <span>Usage insights &amp; trends</span>
            <div class="rm-avatar">R</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

entries = get_history(limit=500)
docs = kb.documents()
stats = kb.stats()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header">📈 Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("💬 Questions Asked",    len(entries))
c2.metric("📄 Documents Indexed",  len(docs))
c3.metric("🧩 Total Chunks",       kb.store.chunk_count())
c4.metric("📎 Total Citations",    sum(len(e.citations) for e in entries))

st.markdown("<br>", unsafe_allow_html=True)

if not entries:
    st.markdown(
        """
        <div class="rm-empty rm-animate-fade-in">
            <span class="rm-empty-icon">📊</span>
            <div class="rm-empty-title">No data yet</div>
            <div class="rm-empty-sub">Ask some questions on the Chat page to see analytics here.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_footer()
    st.stop()

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

# ── Charts ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

# Questions over time
with col_left:
    st.markdown('<div class="rm-section-header" style="font-size:1rem;">📅 Questions Over Time</div>', unsafe_allow_html=True)
    if HAS_PLOTLY:
        dates = [e.created_at[:10] for e in entries]
        date_counts = Counter(dates)
        sorted_dates = sorted(date_counts.keys())
        fig = go.Figure(go.Bar(
            x=sorted_dates,
            y=[date_counts[d] for d in sorted_dates],
            marker_color="#2563EB",
            marker_line_width=0,
        ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
            xaxis=dict(showgrid=False, tickfont=dict(size=11)),
            yaxis=dict(showgrid=True, gridcolor="#F3F4F6", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        dates = [e.created_at[:10] for e in entries]
        date_counts = Counter(dates)
        st.bar_chart(date_counts)

# Provider breakdown
with col_right:
    st.markdown('<div class="rm-section-header" style="font-size:1rem;">🤖 Provider Usage</div>', unsafe_allow_html=True)
    provider_counts = Counter(e.provider for e in entries)
    if HAS_PLOTLY:
        fig2 = go.Figure(go.Pie(
            labels=list(provider_counts.keys()),
            values=list(provider_counts.values()),
            hole=0.5,
            marker_colors=["#2563EB", "#7C3AED", "#14B8A6", "#F59E0B"],
        ))
        fig2.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0),
            height=260,
            showlegend=True,
            legend=dict(font=dict(size=11)),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.bar_chart(provider_counts)

# ── Top Documents by Chunks ───────────────────────────────────────────────────
if docs:
    st.markdown('<div class="rm-section-header" style="font-size:1rem;">📚 Documents by Chunk Count</div>', unsafe_allow_html=True)
    if HAS_PLOTLY:
        sorted_docs = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]
        names = [d[0][:30] + "…" if len(d[0]) > 30 else d[0] for d in sorted_docs]
        values = [d[1] for d in sorted_docs]
        fig3 = go.Figure(go.Bar(
            x=values, y=names, orientation="h",
            marker_color="#7C3AED", marker_line_width=0,
        ))
        fig3.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=0, r=0, t=10, b=0),
            height=max(200, len(names) * 36),
            xaxis=dict(showgrid=True, gridcolor="#F3F4F6"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig3, use_container_width=True)

# ── Recent Questions ──────────────────────────────────────────────────────────
st.markdown('<div class="rm-section-header" style="font-size:1rem;">🕒 Recent Questions</div>', unsafe_allow_html=True)
for entry in entries[:5]:
    st.markdown(
        f"""
        <div class="rm-history-item rm-animate-fade-up">
            <div class="rm-history-q">❓ {entry.question}</div>
            <div class="rm-history-meta">🕐 {entry.created_at} · 🤖 {entry.provider} · 📎 {len(entry.citations)} sources</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

render_footer()
