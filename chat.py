from agent import ask_agent


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


def get_used_tools(result):
    tools_used = []

    for message in result["messages"]:
        tool_calls = getattr(message, "tool_calls", [])

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")

            if tool_name and tool_name not in tools_used:
                tools_used.append(tool_name)

    return tools_used


def main():
    print("=" * 60)
    print("        KartEase Customer Support Agent")
    print("=" * 60)

    print("\nAvailable tools:")
    print("1. search_policies")
    print("2. get_order_status")

    print("\nType 'exit' or 'quit' to end the chat.")
    print("You can ask about KartEase orders and policies.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in ["exit", "quit"]:
            print("\nThank you for contacting KartEase Support!")
            break

        if not question:
            continue

        try:
            result = ask_agent(question)

            answer = get_final_text(result)
            tools_used = get_used_tools(result)

            print("\nKartEase Assistant:")
            print(answer)

            if tools_used:
                print("\nTools used:")
                for tool in tools_used:
                    print(f"- {tool}")
            else:
                print("\nTools used:")
                print("- None")

            print()

        except Exception as error:
            print("\nError:")
            print(error)
            print()


if __name__ == "__main__":
    main()