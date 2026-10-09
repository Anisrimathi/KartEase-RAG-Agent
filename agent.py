import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from policy_tool import search_policies
from tools import get_order_status


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError(
        "GOOGLE_API_KEY not found. Check your .env file."
    )


# ---------------------------------------------------------
# Gemini model
# ---------------------------------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-3.8-flash",
    
)


# ---------------------------------------------------------
# Create LangChain agent
# ---------------------------------------------------------

agent = create_agent(
    model=llm,

    tools=[
        search_policies,
        get_order_status,
    ],

    system_prompt="""
You are the KartEase customer support assistant.

You can help ONLY with:
1. KartEase orders
2. KartEase policies

Available tools:

search_policies:
Use this for questions about KartEase policies such as:
- returns
- refunds
- shipping
- delivery
- warranty
- repairs
- payments
- offers
- coupons
- COD

get_order_status:
Use this when the customer asks about a specific KartEase
order ID such as KE1002 or KE1005.

Rules:

1. For policy questions, use search_policies.

2. For questions about a specific order, use
   get_order_status.

3. If a question requires both order information and policy
   information, use BOTH tools.

4. If the question is unrelated to KartEase orders or
   policies, respond EXACTLY:

Sorry, I can only help with KartEase orders and policies.

5. Never invent KartEase policy information.

6. Never invent order information.

7. Give clear and concise customer-support answers.
"""
)


# ---------------------------------------------------------
# Ask the agent
# ---------------------------------------------------------

def ask_agent(question: str):

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
    )

    return result