# interface/cli.py

from agent.agent import LabMatcherAgent


def main():
    agent = LabMatcherAgent()

    print("=" * 60)
    print("Cornell Research Lab Matchmaker")
    print("Type 'quit' to exit, 'reset' to start over")
    print("=" * 60)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("Conversation reset.\n")
            continue

        print()  # Blank line before agent response
        response = agent.run(user_input)
        print(f"Agent: {response}")
        print()  # Blank line after agent response


if __name__ == "__main__":
    main()