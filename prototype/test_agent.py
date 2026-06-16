"""Sample LLM agent to test the portal and security review logic.

Copy-paste this content into the portal textbox or run `python test_agent.py`.
"""

# Simulated agent code where an LLM might run prompts and handle sensitive data

API_KEY = "secret-key-from-env"  # LLM01 risk: secrets in code

def build_prompt(user_input):
    # LLM03 risk: unsafe template concatenation and injection
    prompt = f"You are a helpful assistant. User said: {user_input}\n"
    prompt += "\nRespond concisely."
    return prompt


def call_llm(prompt):
    # LLM05 risk: no output sanitization, may echo user input including payloads
    print("DEBUG: Sending prompt to model:", prompt)
    # (stub response)
    return "Simulated output: ..."


def main():
    user_text = input("Enter a user question: ")
    prompt = build_prompt(user_text)
    result = call_llm(prompt)
    print("Agent response:\n", result)


if __name__ == '__main__':
    main()
