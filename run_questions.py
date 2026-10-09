from agent import ask_agent


TEST_QUESTIONS = [
    "How many days do I have to return a phone?",
    "Can I return earbuds if I just don't like them?",
    "What is the delivery charge on a ₹350 order?",
    "If I order at 4 PM, when will it be dispatched?",
    "Can I use a coupon together with a bank offer?",
    "How long does Extended Protection last and when can I buy it?",
    "Can I pay cash on delivery for a ₹12,000 order?",
    "Where is my order KE1002?",
    "What is the status of ke1005?",
    "What is the status of KE9999?",
    "My order KE1006 was picked up for return. When will I get my refund?",
    "I paid cash for KE1009. If I return it, how will I get my refund?",
    "Who is the CEO of Google?",
    "Write a poem about Diwali.",
]


def get_final_text(result):
    message = result["messages"][-1]
    content = message.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict) and "text" in item:
                text_parts.append(str(item["text"]))

        return "\n".join(text_parts)

    return str(content)


def run_tests():

    for number, question in enumerate(TEST_QUESTIONS, start=1):

        print("=" * 70)
        print(f"Question {number}")
        print("=" * 70)
        print(question)

        try:
            result = ask_agent(question)
            answer = get_final_text(result)

            print("\nAnswer:")
            print(answer)

        except Exception as error:

            print("\nERROR:")
            print(error)

        print("\n")


if __name__ == "__main__":
    run_tests()