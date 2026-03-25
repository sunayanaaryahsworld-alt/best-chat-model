from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import StreamingResponse
import asyncio

from app.services.intent_service import detect_intent
from app.services.groq_service import generate_ai_reply, generate_ai_reply_stream
from app.services.firebase_service import (
    get_all_salons,
    get_salons_by_location,
    get_services_by_salon_name,
    get_salon_id_by_name,
   get_top_rated_salons,
    get_trending_salons,
    extract_city,
    get_best_salon_in_city,
    recommend_service,
    get_best_salon_for_service,    
     get_cheapest_salons,
     get_open_salons,
     get_salons_for_service,
extract_service_name,
)

router = APIRouter(prefix="/api")


# =========================================================
# Request Schema
# =========================================================
class ChatRequest(BaseModel):
    message: str
    session_id: str
    location: Optional[str] = None
    salon_name: Optional[str] = None

ALL_SALONS_CACHE = None

# =========================================================
# Safe Firebase Wrapper
# =========================================================
def safe_firebase(fn, default):
    """Safely execute Firebase calls, return default on error"""
    try:
        return fn()
    except Exception as e:
        print(f"🔥 Firebase error: {e}")
        return default



# =====================================================
# STREAM CHAT (ChatGPT style)
# =====================================================
@router.post("/chat-stream")
async def chat_stream(request: ChatRequest):

    import json

    response = await chat(request)

    # ✅ safety check
    if not response:
        response = {"reply_text": "Sorry, something went wrong."}

    reply = response.get("reply_text", "No reply")

    async def generate():
        yield reply

        metadata = {k: v for k, v in response.items() if k != "reply_text"}
        yield "\n\n__META__" + json.dumps(metadata)

    return StreamingResponse(generate(), media_type="text/plain")

# =========================================================
# Chat Endpoint - STRICT FLOW
# =========================================================
@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Production-ready chat endpoint with STRICT flow control
    
    FLOW ORDER (NON-NEGOTIABLE):
    1. Exact salon name match
    2. Intent detection
    3. Welcome greeting
    4. Location request (if user asks for nearby salons)
    5. Search by city
    6. Show all salons
    7. Show services (requires salon selected)
    8. Book service (requires salon selected)
    9. Beauty tips (AI only)
    10. Free text (AI fallback only)
    """
    
    global ALL_SALONS_CACHE
    raw_message = request.message.strip()
    message = raw_message.lower()
    
    # =====================================================
    # 1️⃣ EXACT SALON NAME MATCH (highest priority)
    # =====================================================
    # Check if user typed exact salon name
    global ALL_SALONS_CACHE
    
    if ALL_SALONS_CACHE is None:
        ALL_SALONS_CACHE = safe_firebase(get_all_salons, [])
    
    all_salons = ALL_SALONS_CACHE
    
    salon = next(
        (s for s in all_salons if s["name"].lower() == raw_message.lower()),
        None
    )
    
    if salon:
        return {
            "reply_text": f"✨ Found: {salon['name']}",
            "type": "salon_list",
            "salons": [salon],
            "suggestions": [
                "View services",
                "How Nexsalon works",
            ],
        }
    
    # =====================================================
    # 2️⃣ INTENT DETECTION
    # =====================================================
    intent = detect_intent(message)
        
        # =====================================================
        # 3️⃣ WELCOME / GREETING
        # =====================================================
    if intent == "WELCOME":
        return {
            "reply_text": (
            "👋 Hi! I'm Nexsalon Concierge ✨\n\n"
            "I can help you:\n"
            "• Find salons near you\n"
            "• Browse services & prices\n"
            "• Get beauty advice\n"
                ),
                "type": "welcome",
                "suggestions": [
                    "Show salons near me",
                    "Show all salons",
                    "How Nexsalon works",
                ],
            }

    # =====================================================
    # 4️⃣ LOCATION - ASK FOR CITY (near me / nearby)
    # =====================================================
    if intent == "LOCATION" and not request.location:
        # User said "near me", "nearby", "show salons near me", etc
        # Ask for city
        return {
            "reply_text": "📍 Which city are you looking for salons in?",
            "type": "ask_location",
            "suggestions": ["Show all salons", "How Nexsalon works"],
        }

    # =====================================================
    # 5️⃣ SEARCH SALONS BY CITY
    # =====================================================
    if request.location:
        city = request.location.strip()
        
        salons = get_salons_by_location(city)

        if not salons:
            return {
                "reply_text": f"❌ No salons found in {city} yet.",
                "type": "empty",
                "suggestions": [
                    "Show all salons",
                    "How Nexsalon works",
                ],
            }

        return {
            "reply_text": f"📍 Salons in {city}:",
            "type": "salon_list",
            "salons": salons,
            "suggestions": ["View services", "How Nexsalon works"],
        }
  
    # =====================================================
    # 6️⃣ SHOW ALL SALONS
    # =====================================================
    if intent == "SHOW_SALONS":

        if ALL_SALONS_CACHE is None:
            ALL_SALONS_CACHE = safe_firebase(get_all_salons, [])

        salons = ALL_SALONS_CACHE

        if not salons:
            return {
                "reply_text": "No salons available right now.",
                "type": "empty",
                "suggestions": ["How Nexsalon works"],
            }

        return {
            "reply_text": "All available salons:",
            "type": "salon_list",
            "salons": salons,
            "suggestions": ["View services", "How Nexsalon works"],
        }
        
    # =====================================================
    # ⭐ TOP RATED SALONS
    # =====================================================
    if intent == "TOP_RATED":
    
        salons = get_top_rated_salons()
    
        if not salons:
            return {
                "reply_text": "No salons found.",
                "type": "empty",
                "suggestions": ["Show all salons"],
            }
    
        return {
            "reply_text": "⭐ Top rated salons:",
            "type": "salon_list",
            "salons": salons,
            "suggestions": ["View services", "Show all salons"],
        }
        
    # =====================================================
    # 🔥 TRENDING SALONS
    # =====================================================
    if intent == "TRENDING":
    
        salons = get_trending_salons()
    
        if not salons:
            return {
                "reply_text": "No trending salons yet.",
                "type": "empty",
                "suggestions": ["Show all salons"],
            }
    
        return {
            "reply_text": "🔥 Trending salons:",
            "type": "salon_list",
            "salons": salons,
            "suggestions": ["View services"],
        }
        
    # =====================================================
    # ⭐ BEST SALON IN CITY
    # =====================================================
    if intent == "BEST_IN_CITY":
    
        city = extract_city(message)
    
        if not city:
            return {
                "reply_text": "Which city?",
                "type": "ask_location",
            }
    
        salons = safe_firebase(
            lambda: get_best_salon_in_city(city),
            []
        )
    
        if not salons:
            return {
                "reply_text": f"No salons found in {city}",
                "type": "empty",
            }
    
        return {
            "reply_text": f"⭐ Best salons in {city}",
            "type": "salon_list",
            "salons": salons,
        }
        
    # =====================================
    # CHEAP SALONS
    # =====================================
    
    if intent == "CHEAP_SALON":
    
        salons = get_cheapest_salons()
    
        text = "Affordable salons:\n"
    
        for s in salons:
            price = s.get("min_price", "")
            name = s.get("name", "")
    
            text += f"• {name} – ₹{price}\n"
    
        return {
            "reply_text": text,
            "type": "salon_list",
            "salons": salons,
            "suggestions": ["Top rated salons", "Trending salons"],
        }
        
    # =====================================
    # OPEN SALONS
    # =====================================
    
    if intent == "OPEN_SALON":
    
        salons = get_open_salons()
    
        if not salons:
            return {
                "reply_text": "No salons open right now",
                "type": "text",
            }
    
        return {
            "reply_text": "Salons open now:",
            "type": "salon_list",
            "salons": salons,
            "suggestions": ["Top rated salons", "Cheap salons"],
        }
    
    # =====================================
    # SALON FOR SERVICE
    # =====================================
    
    if intent == "SALON_FOR_SERVICE":
    
        service = extract_service_name(message)
    
        if not service:
            return {
                "reply_text": "Please tell service name",
                "type": "text",
            }
    
        salons = get_salons_for_service(service)
    
        if not salons:
            return {
                "reply_text": f"No salons found for {service}",
                "type": "text",
            }
    
        return {
            "reply_text": f"Salons for {service}:",
            "type": "salon_list",
            "salons": salons,
            "suggestions": ["Top rated salons", "Cheap salons"],
        }

    # =====================================================
    # 7️⃣ SHOW SERVICES (requires salon selected)
    # =====================================================
    if intent == "SHOW_SERVICES":
        if not request.salon_name:
            return {
                "reply_text": "🏪 Please select a salon first.",
                "type": "error",
                "suggestions": ["Show all salons", "How Nexsalon works"],
            }

        services = safe_firebase(
            lambda: get_services_by_salon_name(request.salon_name),
            []
        )

        if not services:
            return {
                "reply_text": f"No services available for {request.salon_name}.",
                "type": "empty",
                "suggestions": ["Show all salons", "How Nexsalon works"],
            }

        return {
            "reply_text": f"💇 Services at {request.salon_name}:",
            "type": "service_list",
            "services": services,
            "suggestions": [
                "How Nexsalon works",
            ],
        }

    # # =====================================================
    # # 8️⃣ BOOK SERVICE (requires salon selected)
    # # =====================================================
    # if intent == "BOOK_SERVICE":
    #     if not request.salon_name:
    #         return {
    #             "reply_text": "🏪 Please select a salon first.",
    #             "type": "error",
    #             "suggestions": ["Show all salons", "How Nexsalon works"],
    #         }

    #     return {
    #         "reply_text": (
    #             f"📅 Booking at {request.salon_name}\n\n"
    #             "Steps:\n"
    #             "1. Choose a service\n"
    #             "2. Pick date & time\n"
    #             "3. Confirm & pay"
                
    #         ),
    #         "type": "booking",
    #         "suggestions": ["View services", "How Nexsalon works"],
    #     }

    # =====================================================
    # PROBLEM → SERVICE RECOMMEND
    # =====================================================
    if intent == "PROBLEM_SERVICE":
    
        services = recommend_service(message)
    
        text = "Recommended services:\n"
    
        text = "Recommended services:\n" + "\n".join(
            [f"• {s}" for s in services]
)
    
        best_salons = get_best_salon_for_service(services[0])
    
        return {
            "reply_text": text,
            "type": "service_suggestion",
            "salons": best_salons,
            "suggestions": ["Show salons", "Beauty tips"],
        }
   
    # =====================================================
    # 9️⃣ BEAUTY TIPS (AI only)
    # =====================================================
    if intent == "BEAUTY_SUGGESTION":
    
        try:
            ai_reply = generate_ai_reply(raw_message)
    
        except Exception as e:
            print("❌ GROQ ERROR:", e)
            ai_reply = (
                "✨ Beauty tips:\n"
                "• Stay hydrated\n"
                "• Use gentle products\n"
                "• Avoid excess heat"
            )
    
        return {
            "reply_text": ai_reply,
            "type": "beauty_tip",
            "suggestions": ["Show all salons", "How Nexsalon works"],
        }

    # =====================================================
    # 🔟 APP GUIDE
    # =====================================================
    if intent == "APP_GUIDE":
        return {
            "reply_text": (
                "📱 About Nexsalon\n\n"
                "Nexsalon connects you with the best salons & spas:\n"
                "• Discover salons near you\n"
                "• Browse all available services\n"
                "• View prices & ratings\n"
                "• Get beauty & wellness tips"
            ),
            "type": "app_guide",
            "suggestions": ["Show all salons", "Beauty tips"],
        }

    # =====================================================
    # 1️⃣1️⃣ FREE TEXT (AI fallback only)
    # =====================================================
    else:

        # try DB first
    
        if ALL_SALONS_CACHE is None:
            ALL_SALONS_CACHE = safe_firebase(get_all_salons, [])
    
        salons = ALL_SALONS_CACHE
    
        if salons:
            return {
                "reply_text": "Use buttons below",
                "type": "text",
                "suggestions": ["Show all salons", "Beauty tips"]
            }
    
        ai_reply = generate_ai_reply(raw_message)
    
        return {
            "reply_text": ai_reply,
            "type": "free_text",
            "suggestions": ["Show all salons", "Beauty tips"]
        }