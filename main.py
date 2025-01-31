# main.py
from MasterAI import MasterAIOrchestrator

def main():
    user_id = "demo_user"
    master_ai = MasterAIOrchestrator(user_id=user_id, max_context=5)

    print("Welcome to Master AI. Type 'quit' to exit.")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        response = master_ai.handle_user_message(user_input)
        print(f"AI: {response}\n")

    master_ai.close()

if __name__ == "__main__":
    main()
