
import re
import streamlit as st

from agent import ask_agent
from tools import get_order_status


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="KartEase Support",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    .stApp {
        background: #f5f7fc !important;
        color: #172554 !important;
    }

    [data-testid="stHeader"] {
        background: #f5f7fc !important;
    }

    [data-testid="stSidebar"] {
        background: #edf2ff !important;
        border-right: 1px solid #dbe4f5;
    }

    [data-testid="stSidebar"] * {
        color: #1e3155;
    }

    .brand {
        font-size: 30px;
        font-weight: 800;
        color: #245de0 !important;
        padding-top: 10px;
    }

    .brand-caption {
        font-size: 13px;
        color: #526581 !important;
        margin-bottom: 25px;
    }

    .hero {
        padding: 30px;
        border-radius: 20px;
        background: linear-gradient(120deg, #e3edff, #eef7ff);
        border: 1px solid #d8e5ff;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: #172e59 !important;
        font-size: 30px;
        margin: 0 0 8px;
    }

    .hero p {
        color: #425878 !important;
        font-size: 16px;
        margin: 0;
    }

    .section-heading {
        font-size: 19px;
        font-weight: 700;
        color: #24395f !important;
        margin: 20px 0 12px;
    }

    .status-card {
        background: #ffffff;
        padding: 16px;
        border: 1px solid #dce5f4;
        border-radius: 15px;
        margin-top: 20px;
        color: #203454 !important;
    }

    .stButton > button {
        background: #ffffff !important;
        color: #1e3a68 !important;
        border: 1px solid #dce5f4 !important;
        border-radius: 12px !important;
        min-height: 46px;
        font-weight: 600;
    }

    .stButton > button:hover {
        background: #eaf1ff !important;
        border-color: #3974ec !important;
        color: #174ea6 !important;
    }

    [data-testid="stChatMessage"] {
        background: #ffffff !important;
        border: 1px solid #e0e7f3 !important;
        border-radius: 16px !important;
        padding: 15px !important;
        margin-bottom: 12px;
    }

    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] strong {
        color: #172554 !important;
        line-height: 1.65;
    }

    [data-testid="stChatInput"] {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 14px !important;
    }

    [data-testid="stChatInput"] > div {
        background: #ffffff !important;
    }

    [data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        color: #172554 !important;
        -webkit-text-fill-color: #172554 !important;
        caret-color: #172554 !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }

    [data-testid="stChatInput"] button {
        background: #2563eb !important;
        color: #ffffff !important;
        border-radius: 10px !important;
    }

    .tool-badge {
        display: inline-block;
        background: #e2f7e9;
        color: #17643b !important;
        border: 1px solid #c6ecd3;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 12px;
        margin-top: 8px;
    }

    .source-badge {
        display: inline-block;
        background: #e6efff;
        color: #174ea6 !important;
        border: 1px solid #d4e3ff;
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 12px;
        margin-top: 8px;
    }

    [data-testid="stMarkdownContainer"] {
        overflow-wrap: anywhere;
    }

    #MainMenu, footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# =========================================================
# RESPONSE HELPERS
# =========================================================
def extract_answer(result):
    """Extract the final assistant response from the agent."""
    messages = result.get("messages", [])

    for message in reversed(messages):
        if getattr(message, "type", None) != "ai":
            continue

        # Skip intermediate messages that only call tools.
        if getattr(message, "tool_calls", []):
            continue

        content = getattr(message, "content", "")

        if isinstance(content, str) and content.strip():
            return content.strip()

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict) and item.get("text"):
                    parts.append(str(item["text"]))

            answer = "\n".join(parts).strip()

            if answer:
                return answer

    return "The agent did not return a readable final answer."


def extract_tools(result):
    """Extract unique tool names used by the agent."""
    names = []

    for message in result.get("messages", []):
        for call in getattr(message, "tool_calls", []):
            name = call.get("name")

            if name and name not in names:
                names.append(name)

    return names


def generate_answer(question):
    """
    Use local order lookup for recognizable order questions.
    Use the LangChain agent for other questions.
    """
    question_lower = question.lower()

    # Find an order ID such as KE1002.
    order_match = re.search(
        r"\bKE\d{4}\b",
        question,
        re.IGNORECASE,
    )

    order_keywords = (
        "order",
        "track",
        "status",
        "where is",
        "delivery status",
    )

    # Local order lookup does not require a Gemini API request.
    if order_match and any(
        keyword in question_lower for keyword in order_keywords
    ):
        order_id = order_match.group(0)

        try:
            answer = get_order_status(order_id)

            return {
                "content": answer,
                "tools": ["get_order_status (local fallback)"],
                "error": None,
                "source": "orders.csv",
            }

        except Exception as exc:
            print("Local order lookup error:", repr(exc))

            return {
                "content": (
                    "Unable to read the order data. "
                    "Please check data/orders.csv."
                ),
                "tools": [],
                "error": str(exc),
                "source": None,
            }

    # Other questions use the existing LangChain agent.
    try:
        result = ask_agent(question)

        answer = extract_answer(result)
        tools = extract_tools(result)

        return {
            "content": answer,
            "tools": tools,
            "error": None,
            "source": None,
        }

    except Exception as exc:
        print("\nKartEase backend error:")
        print(repr(exc))

        error_text = str(exc)
        lower = error_text.lower()

        if "429" in error_text or "resource_exhausted" in lower:
            answer = (
                "Gemini's API quota has been reached. "
                "Order lookups are still available locally. "
                "Try asking: Where is my order KE1002?"
            )
        elif "404" in error_text or "not_found" in lower:
            answer = (
                "The configured Gemini model is unavailable. "
                "Check its name in agent.py and policy_tool.py."
            )
        elif "503" in error_text or "unavailable" in lower:
            answer = (
                "Gemini is temporarily unavailable. Please try later."
            )
        else:
            answer = (
                "The request failed. Expand Technical Error Details "
                "to inspect the error."
            )

        return {
            "content": answer,
            "tools": [],
            "error": error_text,
            "source": None,
        }


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown(
        '<div class="brand">🛒 KartEase</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="brand-caption">CUSTOMER SUPPORT</div>',
        unsafe_allow_html=True,
    )

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown("### 💬 Chat History")

    previous_questions = [
        message["content"]
        for message in st.session_state.messages
        if message["role"] == "user"
    ]

    if previous_questions:
        for index, previous_question in enumerate(
            previous_questions, start=1
        ):
            label = previous_question

            if len(label) > 40:
                label = label[:37] + "..."

            st.caption(f"{index}. {label}")
    else:
        st.caption("Your conversations will appear here.")

    st.markdown("---")

    st.markdown(
        """
        <div class="status-card">
            🟢 <b>KartEase Assistant</b><br>
            <span style="font-size:13px;color:#526581">
                LangChain · Gemini · ChromaDB
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()


# =========================================================
# MAIN HEADER
# =========================================================
st.markdown(
    """
    <div class="hero">
        <h1>Welcome to KartEase Support! 👋</h1>
        <p>
            Your shopping assistant for orders, returns, delivery,
            warranties, payments and offers.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">What can we help you with?</div>',
    unsafe_allow_html=True,
)


# =========================================================
# QUICK ACTIONS
# =========================================================
actions = [
    ("📦", "Track an Order", "Where is my order KE1002?"),
    (
        "↩️",
        "Return Policy",
        "How many days do I have to return a phone?",
    ),
    (
        "🚚",
        "Delivery Charges",
        "What is the delivery charge on a ₹350 order?",
    ),
    (
        "🏷️",
        "Offers & Coupons",
        "Can I use a coupon together with a bank offer?",
    ),
]

columns = st.columns(4)

for column, (emoji, label, prompt) in zip(columns, actions):
    with column:
        if st.button(
            f"{emoji}  {label}",
            key=f"action_{label}",
            use_container_width=True,
        ):
            st.session_state.pending_prompt = prompt
            st.rerun()


# =========================================================
# DISPLAY CONVERSATION
# =========================================================
st.markdown("---")

for item in st.session_state.messages:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

        if item["role"] == "assistant":
            tools = item.get("tools", [])

            if tools:
                st.markdown(
                    '<div class="tool-badge">🔧 Tools used: '
                    + ", ".join(tools)
                    + "</div>",
                    unsafe_allow_html=True,
                )

            source = item.get("source")

            if source:
                st.markdown(
                    '<div class="source-badge">📄 Source: '
                    + source
                    + "</div>",
                    unsafe_allow_html=True,
                )

            if item.get("error"):
                with st.expander("Technical Error Details"):
                    st.code(item["error"])


# =========================================================
# CHAT INPUT
# =========================================================
typed_question = st.chat_input(
    "Ask about your KartEase orders or policies..."
)

question = typed_question

if not question and st.session_state.pending_prompt:
    question = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if question:
    # Save and display the user message once.
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Generate the response.
    with st.chat_message("assistant"):
        with st.spinner("KartEase Assistant is thinking..."):
            response = generate_answer(question)

        st.markdown(response["content"])

        if response["tools"]:
            st.markdown(
                '<div class="tool-badge">🔧 Tools used: '
                + ", ".join(response["tools"])
                + "</div>",
                unsafe_allow_html=True,
            )

        if response["source"]:
            st.markdown(
                '<div class="source-badge">📄 Source: '
                + response["source"]
                + "</div>",
                unsafe_allow_html=True,
            )

        if response["error"]:
            with st.expander("Technical Error Details"):
                st.code(response["error"])

    # Save the assistant message once.
    st.session_state.messages.append({
        "role": "assistant",
        "content": response["content"],
        "tools": response["tools"],
        "error": response["error"],
        "source": response["source"],
    })




