import json

import streamlit as st

from agent.agent_core import run_agent
from agent.llm_client import is_configured, DEFAULT_MODEL
from utils.theme import load_css, section_header, status_badge, CYAN, AMBER, RED

st.set_page_config(
    page_title="AI Analyst Agent",
    page_icon="🕵",
    layout="wide"
)
load_css()

st.title("🕵 AI Analyst Agent")

st.markdown("""
Ask an open-ended question and the agent will decide which analytical
tools to call — data queries, the attack forecaster, or the threat-level
classifier — then synthesize an answer. Powered by a free model via
[OpenRouter](https://openrouter.ai).
""")

agent_configured = is_configured()
if not agent_configured:
    st.warning(
        "No `OPENROUTER_API_KEY` found. Copy `.env.example` to `.env` and add "
        "your free OpenRouter API key to use this page."
    )

status_col1, status_col2 = st.columns([1, 3])
with status_col1:
    status_badge("AGENT ONLINE" if agent_configured else "AGENT OFFLINE", ok=agent_configured)
with status_col2:
    st.caption(f"Model: `{DEFAULT_MODEL}`  ·  Tools: country stats, forecast, threat-level prediction, filtered data query")

# ----------------------------------------------------
# Chat state
# ----------------------------------------------------

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []  # display history: [{"role", "content"}]
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []  # raw history passed back into the LLM

with st.sidebar:
    st.markdown("### 💡 Example questions")
    st.markdown("""
    - "Give me a risk assessment for Nigeria over the next 5 years"
    - "How many bombing incidents happened in Iraq after 2015?"
    - "What's the predicted threat level for a bombing attack in Afghanistan targeting a government building?"
    - "Compare the attack trend in Pakistan vs India"
    """)
    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.agent_history = []
        st.rerun()


# ----------------------------------------------------
# Chat bubble rendering — visually distinct user vs. agent
# ----------------------------------------------------

def render_bubble(role: str, content: str):
    is_user = role == "user"
    align = "flex-end" if is_user else "flex-start"
    bg = "rgba(232,163,61,0.08)" if is_user else "rgba(61,214,198,0.06)"
    border = f"{AMBER}40" if is_user else f"{CYAN}30"
    label = "OPERATOR" if is_user else "ANALYST AGENT"
    label_color = AMBER if is_user else CYAN
    icon = "🧑‍✈️" if is_user else "🕵"

    st.markdown(
        f"""
        <div style="display:flex; justify-content:{align}; margin:8px 0;">
            <div style="max-width:78%; background:{bg}; border:1px solid {border};
                        border-radius:12px; padding:12px 16px;">
                <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem;
                            color:{label_color}; letter-spacing:1px; text-transform:uppercase;
                            margin-bottom:6px;">
                    {icon} {label}
                </div>
                <div style="color:#E8ECF1; font-size:0.92rem; line-height:1.55;">
                    {content}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------
# Operation log rendering — structured trace instead of raw st.json
# ----------------------------------------------------

def render_trace(trace):
    if not trace:
        return

    with st.expander("🗂️ Operation Log"):
        for step in trace:
            event = step.get("event")

            if event == "tool_call":
                args_str = ", ".join(f"{k}={v!r}" for k, v in step.get("arguments", {}).items())
                st.markdown(
                    f"""
                    <div style="border-left:2px solid {CYAN}; padding:6px 12px; margin-bottom:6px;
                                font-family:'JetBrains Mono', monospace; font-size:0.82rem;">
                        <span style="color:#7C8798;">STEP {step.get('step')}</span>
                        <span style="color:{CYAN};"> ▶ CALL</span>
                        <span style="color:#E8ECF1;"> {step.get('tool')}</span>
                        <span style="color:#7C8798;">({args_str})</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            elif event == "tool_result":
                result = step.get("result")
                try:
                    result_str = json.dumps(result, default=str)
                except Exception:
                    result_str = str(result)
                if len(result_str) > 400:
                    result_str = result_str[:400] + " …"
                st.markdown(
                    f"""
                    <div style="border-left:2px solid {AMBER}; padding:6px 12px; margin-bottom:6px;
                                font-family:'JetBrains Mono', monospace; font-size:0.8rem;">
                        <span style="color:#7C8798;">STEP {step.get('step')}</span>
                        <span style="color:{AMBER};"> ◀ RESULT</span>
                        <span style="color:#7C8798;"> from {step.get('tool')}:</span><br>
                        <span style="color:#E8ECF1;">{result_str}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            elif event == "final_answer":
                st.markdown(
                    f"""
                    <div style="border-left:2px solid #3DDC84; padding:6px 12px; margin-bottom:6px;
                                font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:#3DDC84;">
                        ✔ FINAL ANSWER — step {step.get('step')} · {step.get('elapsed_sec', '?')}s
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            elif event == "llm_error":
                st.markdown(
                    f"""
                    <div style="border-left:2px solid {RED}; padding:6px 12px; margin-bottom:6px;
                                font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:{RED};">
                        ✖ ERROR — {step.get('detail')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            elif event == "max_iterations_reached":
                st.markdown(
                    f"""
                    <div style="border-left:2px solid {AMBER}; padding:6px 12px; margin-bottom:6px;
                                font-family:'JetBrains Mono', monospace; font-size:0.8rem; color:{AMBER};">
                        ⚠ MAX ITERATIONS REACHED
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ----------------------------------------------------
# Render existing conversation
# ----------------------------------------------------

for msg in st.session_state.chat_messages:
    render_bubble(msg["role"], msg["content"])
    if msg["role"] == "assistant" and msg.get("trace"):
        render_trace(msg["trace"])

# ----------------------------------------------------
# Chat input
# ----------------------------------------------------

user_input = st.chat_input("Ask the analyst agent a question...")

if user_input:
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    render_bubble("user", user_input)

    with st.spinner("🧠 Agent is reasoning and calling tools..."):
        result = run_agent(user_input, chat_history=st.session_state.agent_history)

    render_bubble("assistant", result["answer"])

    if result["trace"]:
        render_trace(result["trace"])

    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": result["answer"],
        "trace": result["trace"],
    })
    st.session_state.agent_history.append({"role": "user", "content": user_input})
    st.session_state.agent_history.append({"role": "assistant", "content": result["answer"]})
