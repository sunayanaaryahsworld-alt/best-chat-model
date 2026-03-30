def detect_intent(message: str) -> str:
    msg = message.lower()

    if any(k in msg for k in ["trending", "latest", "new", "hot"]):
        return "TRENDING"

    if any(k in msg for k in ["popular", "most used", "common"]):
        return "POPULAR"

    if any(k in msg for k in ["how to", "use app", "website", "help", "guide"]):
        return "APP_GUIDE"

    if any(k in msg for k in ["what is", "benefits", "treatment"]):
        return "SERVICE_INFO"

    if any(k in msg for k in ["salon", "near", "location"]):
        return "SALON_INFO"

    return "GENERAL"


