# test_router.py

from router import route_prompt

prompt = "Explain AI in one line"

response = route_prompt(prompt)

print("\nFinal Response:")
print(response)