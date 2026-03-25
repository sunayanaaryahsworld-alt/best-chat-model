import re
from app.services.firebase_service import get_all_services

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
    
    #recommender
    services = get_all_services()

    has_service = any(s in msg for s in services)
    has_price = re.search(r"\d{2,5}", msg)
    
    if has_service and has_price:
        print("INTENT CHECK:", msg)
        return "SMART_RECOMMEND"

    # 1️⃣ GREETING - Exact word match only
    if re.fullmatch(r"(hi|hello|hey|hii|hiii|hiii+|start|greetings|begin)", msg):
        return "WELCOME"

    # 2️⃣ APP GUIDE - about Nexsalon / how Nexsalon works
    if re.search(r"(Nexsalon|how.*works)", msg):
        return "APP_GUIDE"
        
            
    # 3️⃣ LOCATION - when user wants salons near them (with OR without "show")
    # This asks for city: "near me", "nearby", "show salons near me", etc
    # if re.search(r"\b(near me|nearby|in my area|closest)\b", msg):
    #     return "LOCATION"
    if re.search(r"\b(near me|nearby|in my area|closest)\b", msg):

        services = get_all_services()
    
        has_service = any(s in msg for s in services)
        has_price = re.search(r"\d{2,5}", msg)
    
        # if service + price → SMART
        if has_service and has_price:
            return "SMART_RECOMMEND"
    
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

    # # 5️⃣ SHOW SERVICES - view/show services
    # if re.search(r"\b(show|view|see|display)\b.*\b(service|services)\b", msg):
    #     return "SHOW_SERVICES"
    if re.search(
    r"\b(show|view|see|display|what|which|list|tell|provide)\b.*\b(service|services)\b",
    msg
):
        return "SHOW_SERVICES"
        
    if re.search(r"\b(service|services)\b", msg):
        return "SHOW_SERVICES"    

    # # 6️⃣ BOOKING - book, appointment, reserve
    # if re.search(r"\b(book|booking|appointment|schedule|reserve)\b", msg):
    #     return "BOOK_SERVICE"

    # PROBLEM BASED SERVICE
 # PROBLEM → SERVICE (only when user wants treatment / salon)
    if re.search(
        r"\b(treatment|service|salon|facial|spa|therapy|appointment)\b.*\b(hair fall|dandruff|dry skin|frizzy|pimple|acne|hair damage|rough hair)\b"
        r"|\b(hair fall|dandruff|dry skin|frizzy|pimple|acne|hair damage|rough hair)\b.*\b(treatment|service|salon|facial|spa|therapy)\b",
        msg,
    ):
        return "PROBLEM_SERVICE"

    # 7️⃣ BEAUTY - beauty, skincare, hair, makeup, etc
    if re.search(
        r"\b(beauty|skin|hair|makeup|care|nail|face|scalp|moistur|sunscreen|glow|pigment|tan|pore|wrinkle|lip|eye|brow|lash|serum|toner|cleanser|shampoo|conditioner|frizz|dandruff|split|growth|strong|damage|dry|oily|acne|pimple|tip|advice|suggest|routine|treatment|how to|what to|remedy|home remedy|natural)\b",
        msg,
    ):
        return "BEAUTY_SUGGESTION"

    
    # 8️⃣ FALLBACK - everything else
    return "FREE_TEXT"
