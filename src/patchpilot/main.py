
from patchpilot.llm_client import LLMClient


def main():
    llm = LLMClient()

    messages = [
        {
            "role": "system",
            "content": "You are PatchPilot, a concise coding assistant."
        },
        {
            "role": "user",
            "content": "Explain what a Python decorator is in 3 sentences."
        }
    ]

    result = llm.generate(messages)

    print("\nPatchPilot Response:\n")
    print(result)


if __name__ == "__main__":
    main()
