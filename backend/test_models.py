from  router.config  import (
    GROQ_API_KEY,
    OPENROUTER_API_KEY
)

from models.groq_model import ask_model as call_groq
from models.openrouter_model import call_openrouter


TEST_PROMPT = "Explain AI in one line."


def test_model(name, func, api_key):
    print(f"\n🔹 Testing {name}...")

    if not api_key:
        print(f"❌ {name} API key missing")
        return

    try:
        response = func(TEST_PROMPT)
        print(f"✅ {name} working")
        print(f"Response: {response[:100]}...\n")

    except Exception as e:
        print(f"❌ {name} failed: {str(e)}")


if __name__ == "__main__":
    test_model("Groq", call_groq, GROQ_API_KEY)
    test_model("OpenRouter", call_openrouter, OPENROUTER_API_KEY)