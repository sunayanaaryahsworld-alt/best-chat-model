import re

def detect_intent(message: str) -> str:
    """
    STRICT Intent Detection - Only explicit intents, no guessing
    
    Priority Order:
    1. GREETING (hi, hello, start)
    2. APP_GUIDE (about Nexsalon / how it works)
    3. LOCATION (near me, nearby, closest)
    4. TRENDING (trending salons, popular salons)
    5. TOP_RATED (top rated, best salons)
    6. SHOW_SALONS (show salons, list salons)
    7. SHOW_SERVICES (show services, view services)
    8. BEAUTY_SUGGESTION (beauty, skin, hair tips)
    9. FREE_TEXT (everything else → AI reply)
        """
    msg = message.lower().strip()

    # 1️⃣ GREETING - Exact word match only
    if re.fullmatch(r"(hi|hello|hey|hii|hiii|hiii+|start|greetings|begin)", msg):
        return "WELCOME"

    # 2️⃣ APP GUIDE - about Nexsalon / how Nexsalon works
    if re.search(r"(Nexsalon|how.*works)", msg):
        return "APP_GUIDE"

    # 3️⃣ LOCATION - when user wants salons near them (with OR without "show")
    # This asks for city: "near me", "nearby", "show salons near me", etc
    if re.search(r"\b(near me|nearby|in my area|closest)\b", msg):
        return "LOCATION"

  # ⭐ TRENDING SALONS
    if re.search(r"\b(trending|popular|hot)\b.*\b(salon|salons)\b", msg):
        return "TRENDING"
        
    if re.search(r"\b(best|top)\b.*\bsalon\b.*\bin\b", msg):
        return "BEST_IN_CITY"    
        
    if re.search(r"\b(top|best|highest)\b.*\b(rated|rating|salon)\b", msg):
        return "TOP_RATED"   
        
    if re.search(r"\b(cheap|budget|low price|affordable)\b.*\b(salon|salons)\b", msg):
        return "CHEAP_SALON"   
        
    if re.search(r"\b(open|open now|currently open)\b.*\b(salon|salons)\b", msg):
        return "OPEN_SALON"    
    if re.search(r"\b(salon for|salon with|find salon for)\b", msg):
        return "SALON_FOR_SERVICE"    
        
    # 4️⃣ SHOW SALONS - show all salons (NOT location-based)
    # Only if they didn't ask for "near me"
    if re.search(r"\b(show|find|list|display)\b.*\bsalon", msg):
        return "SHOW_SALONS"

    # 5️⃣ SHOW SERVICES - view/show services
    if re.search(r"\b(show|view|see|display)\b.*\b(service|services)\b", msg):
        return "SHOW_SERVICES"

    # # 6️⃣ BOOKING - book, appointment, reserve
    # if re.search(r"\b(book|booking|appointment|schedule|reserve)\b", msg):
    #     return "BOOK_SERVICE"

        # PROBLEM BASED SERVICE
    if re.search(
        r"\b(hair fall|dandruff|dry skin|frizzy|pimple|acne|hair damage|rough hair)\b",
        msg,
    ):
        return "PROBLEM_SERVICE"
    # 7️⃣ BEAUTY - beauty, skincare, hair, makeup, etc
    if re.search(
    r"\b(beauty tips|skin tips|hair tips|makeup tips|care tips|suggest tips)\b",
        msg
):
        return "BEAUTY_SUGGESTION"

    # 8️⃣ FALLBACK - everything else
    return "FREE_TEXT"
