import os

KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "knowledge_base",
    "Nexsalon.md"
)

def answer_from_firebase(message: str, session_id: str) -> str | None:
    """
    Simple RAG-style lookup from Nexsalon.md.
    Returns short matched lines only.
    """

    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        return None

    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    msg_words = message.lower().split()

    matches = []

    for line in lines:
        line_lower = line.lower()

        if any(word in line_lower for word in msg_words):
            matches.append(line.strip())

        if len(matches) >= 3:   # limit answer size
            break

    if not matches:
        return None

    result = "\n".join(matches)

    result = result.replace("**", "")
    result = result.replace("##", "")
    result = result.replace("###", "")
    result = result.replace("- ", "• ")
    
    return result