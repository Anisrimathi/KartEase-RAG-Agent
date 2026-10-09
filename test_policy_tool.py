from policy_tool import search_policies


questions = [
    "How many days do I have to return a phone?",
    "Can I return earbuds if I just don't like them?",
    "What is the delivery charge on a ₹350 order?",
    "Who is the CEO of Google?",
]


for question in questions:

    print("\n" + "=" * 70)
    print(f"Question: {question}")
    print("=" * 70)

    answer = search_policies(question)

    print(answer)