import os
import firebase_admin
from firebase_admin import credentials, db
from collections import Counter
from datetime import datetime, timedelta
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
FIREBASE_KEY_PATH = os.path.join(BASE_DIR, "firebase_key.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL": "https://salonandspa-7b832-default-rtdb.firebaseio.com"
        }
    )


def get_salons_batch(last_key=None, batch_size=10):
    try:
        ref = db.reference("salonandspa/salons")

        query = ref.order_by_key()

        # start after last key (for pagination)
        if last_key:
            query = query.start_at(last_key)

        query = query.limit_to_first(batch_size)

        data = query.get() or {}

        salons = []
        keys = list(data.keys())

        for i, (salon_id, salon) in enumerate(data.items()):
            
            # skip first if it's duplicate of last_key
            if last_key and i == 0:
                continue

            salons.append({
                "id": salon_id,
                "name": salon.get("name", ""),
                "address": salon.get("address", ""),
                "rating": salon.get("rating", 0),
                "price": salon.get("price", 500),
            })

        # next key for next batch
        next_key = keys[-1] if keys else None

        return salons, next_key

    except Exception as e:
        print("❌ Batch fetch error:", e)
        return [], None
        
# ==================================================
# 🏪 GET ALL SALONS FROM FIREBASE
# Path: salonandspa/salons
# ==================================================
# def get_all_salons():
#     """
#     Fetch ALL salons from Firebase Realtime DB
#     Returns consistent data structure
#     """
#     try:
#         ref = db.reference("salonandspa/salons")

#         salons_data = ref.get() or {}
        
#         # print("SALONS:", salons_data.keys())
        
#         salons = []
#         for salon_id, salon in salons_data.items():
#             if not salon.get("name"):
#                 continue
#             # TO THIS (working):
#             address = salon.get("address", "").strip()
#             city = ""
#             if address:
#                 parts = [p.strip() for p in address.split(",") if p.strip()]
#                 if len(parts) >= 3:
#                     city = parts[-3]
#                 elif len(parts) == 2:
#                     city = parts[-2]
#                 elif parts:
#                     city = parts[-1]
                    
#             salon_id_val = salon_id        
#             offers = get_offers_by_salon_id(salon_id_val)  
            
#             salons.append({
#                 "name": salon.get("name", "").strip(),
#                 "address": address,
#                 "city": city,
#                 "rating": salon.get("rating", 0),  # ✅ Use 0 as default, not None
#                 "price": salon.get("price", 500),
#                 "offers": offers,
#             })
        
#         return salons
#     except Exception as e:
#         print(f"❌ Firebase error (get_all_salons): {e}")
#         return []


# ==================================================
# 📍 GET SALONS BY CITY
# ==================================================
def get_salons_by_location(location: str):
    """
    Fetch salons matching city (case-insensitive)
    Location can be a city name or part of address
    """
    if not location or not isinstance(location, str):
        return []
    
    try:
        location_lower = location.lower().strip()
        # all_salons = get_all_salons()
        salons, next_key = get_salons_batch(batch_size=10)
        
        matching = [
            # s for s in all_salons
            s for s in salons
            if (location_lower in s.get("city", "").lower() or
                location_lower in s.get("address", "").lower())
        ]
        
        return matching
    except Exception as e:
        print(f"❌ Firebase error (get_salons_by_location): {e}")
        return []


# ==================================================
# 🔎 GET SALON ID BY NAME (EXACT MATCH)
# ==================================================
def get_salon_id_by_name(salon_name: str):
    """
    Find salon_id in Firebase by exact name match
    Returns salon_id or None
    """
    if not salon_name or not isinstance(salon_name, str):
        return None
    
    try:
        salon_name_lower = salon_name.lower().strip()
        ref = db.reference("salonandspa/salons")
        salons = ref.get() or {}
        
        for salon_id, salon in salons.items():
            if salon.get("name", "").lower().strip() == salon_name_lower:
                return salon_id
        
        return None
    except Exception as e:
        print(f"❌ Firebase error (get_salon_id_by_name): {e}")
        return None




# ==================================================
# 💇 GET SERVICES BY SALON NAME
# Path: salonandspa/salons/{salon_id}/services
# ==================================================
def get_services_by_salon_name(salon_name: str):
    """
    Fetch services for a specific salon
    Must provide exact salon name from Firebase
    """
    if not salon_name or not isinstance(salon_name, str):
        return []
    
    try:
        salon_id = get_salon_id_by_name(salon_name)
        
        if not salon_id:
            return []
        
        ref = db.reference(f"salonandspa/salons/{salon_id}/services")
        services_data = ref.get() or {}
        
        services = []
        for service_id, service in services_data.items():
            if not service.get("name"):
                continue
            
            services.append({
                "service_id": service_id,
                "name": service.get("name", "").strip(),
                "price": service.get("price"),
                "duration": service.get("duration"),
            })
        
        return services
    except Exception as e:
        print(f"❌ Firebase error (get_services_by_salon_name): {e}")
        return []


# ==================================================
# 📅 APPOINTMENTS
# Path: salonandspa/appointments/salon/{salonId}
# ==================================================
def get_all_salon_appointments():
    ref = db.reference("salonandspa/appointments/salon")
    return ref.get() or {}


# ==================================================
# 🔎 GET SALON DETAILS BY NAME
def get_salon_by_name(name: str):
    # salons = get_all_salons()
    salons, next_key = get_salons_batch(batch_size=10)
    name = name.lower().strip()

    for salon in salons:
        if salon["name"].lower() == name:
            return salon

    return None


# ==================================================
# 🔥 TRENDING SALONS
# ==================================================
def get_trending_salons(days: int = 30):
    appointments = get_all_salon_appointments()
    counter = Counter()
    cutoff = datetime.now() - timedelta(days=days)

    for salon_id, salon in appointments.items():
        for appt in salon.values():
            created_at = appt.get("createdAt")
            if not created_at:
                continue

            created = datetime.fromtimestamp(created_at / 1000)
            if created >= cutoff:
                counter[salon_id] += 1

    # salon_map = {s["salon_id"]: s for s in get_all_salons()}
    salon_map = {s["salon_id"]: s for s in get_salons_batch()}

    return [
        salon_map[salon_id]
        for salon_id, _ in counter.most_common(5)
        if salon_id in salon_map
    ]

# ==================================================
# ⭐ TOP RATED SALONS
# ==================================================
def get_top_rated_salons(limit: int = 5):

    # salons = get_all_salons()
    salons, next_key = get_salons_batch(batch_size=10)

    # ✅ keep only rated salons
    filtered = [
        s for s in salons
        if s.get("rating") and s.get("rating") >= 4
    ]

    # ✅ sort by rating
    filtered.sort(
        key=lambda x: x.get("rating", 0),
        reverse=True
    )

    return filtered[:limit]
    
    
# ==================================================
# 🔥 TRENDING SALONS
# ==================================================
def get_trending_salons(limit: int = 5, days: int = 30):
    """
    Return most booked salons in last N days
    """

    try:
        appointments = get_all_salon_appointments()
        counter = Counter()

        cutoff = datetime.now() - timedelta(days=days)

        # count appointments per salon
        for salon_id, salon_data in appointments.items():

            for appt_id, appt in salon_data.items():

                created_at = appt.get("createdAt")

                if not created_at:
                    continue

                created = datetime.fromtimestamp(created_at / 1000)

                if created >= cutoff:
                    counter[salon_id] += 1

        # get all salons
        # salons = get_all_salons()
        salons, next_key = get_salons_batch(batch_size=10)

        # map salon_id → salon data
        salon_map = {}

        for s in salons:
            salon_id = get_salon_id_by_name(s["name"])
            if salon_id:
                salon_map[salon_id] = s

        # return top salons
        result = []

        for salon_id, _ in counter.most_common(limit):
            if salon_id in salon_map:
                result.append(salon_map[salon_id])

        return result

    except Exception as e:
        print("🔥 Trending error:", e)
        return []    
        
def extract_city(message: str):

    words = message.split()

    if "in" in words:
        idx = words.index("in")
        if idx + 1 < len(words):
            return words[idx + 1]

    return None
    
def get_best_salon_in_city(city: str):

    salons = get_salons_by_location(city)

    if not salons:
        return []

    salons = sorted(
        salons,
        key=lambda x: x.get("rating", 0),
        reverse=True
    )

    return salons[:3]        
    
def recommend_service(problem: str):

    problem = problem.lower()

    mapping = {
        "hair fall": ["Hair spa", "Scalp treatment", "Keratin"],
        "dandruff": ["Scalp treatment", "Hair spa"],
        "dry skin": ["Facial", "Skin treatment", "Hydra facial"],
        "acne": ["Acne treatment", "Facial"],
        "frizzy": ["Keratin", "Smoothening", "Hair spa"],
        "hair damage": ["Hair spa", "Protein treatment"],
        "rough hair": ["Hair spa", "Conditioning"],
    }

    for key in mapping:
        if key in problem:
            return mapping[key]

    return ["Hair spa", "Facial"]    
    
    
def get_best_salon_for_service(service_name: str):

    # salons = get_all_salons()
    salons, next_key = get_salons_batch(batch_size=10)

    result = []

    for salon in salons:

        services = salon.get("services", [])

        for s in services:
            if service_name.lower() in s["name"].lower():
                result.append(salon)
                break

    result = sorted(
        result,
        key=lambda x: x.get("rating", 0),
        reverse=True
    )

    return result[:3]    
    
def get_cheapest_salons(limit=5):

    # salons = get_all_salons()
    salons, next_key = get_salons_batch(batch_size=10)

    result = []

    for salon in salons:

        services = salon.get("services", [])

        if not services:
            continue

        prices = []

        for s in services:
            price = s.get("price")
            if price:
                prices.append(price)

        if not prices:
            continue

        min_price = min(prices)

        salon["min_price"] = min_price

        result.append(salon)

    result.sort(key=lambda x: x["min_price"])

    return result[:limit]    
    

def get_open_salons():

    # salons = get_all_salons()
    salons, next_key = get_salons_batch(batch_size=10)

    now = datetime.now().hour

    result = []

    for salon in salons:

        open_time = salon.get("openingHour")
        close_time = salon.get("closingHour")

        if open_time is None or close_time is None:
            continue

        if open_time <= now <= close_time:
            result.append(salon)

    return result    
    
def extract_service_name(message: str):

    services = [
        "haircut",
        "facial",
        "spa",
        "massage",
        "hair spa",
        "keratin",
        "color",
        "wax",
        "nail",
        "makeup",
    ]

    msg = message.lower()

    for s in services:
        if s in msg:
            return s

    return None
    
def get_salons_for_service(service_name):

    # salons = get_all_salons()
    salons, next_key = get_salons_batch(batch_size=10)

    result = []

    for salon in salons:

        services = salon.get("services", [])

        for s in services:

            name = s.get("name", "").lower()

            if service_name.lower() in name:
                result.append(salon)
                break

    return result    

def get_all_services():

    try:
        ref = db.reference("salonandspa/salons")
        salons = ref.get() or {}

        services = set()

        for salon in salons.values():

            salon_services = salon.get("services", {})

            for s in salon_services.values():

                name = s.get("name", "")

                if name:
                    services.add(name.lower())

        return list(services)

    except Exception as e:
        print("❌ Service fetch error:", e)
        return []
        

def recommend_salons(message: str, detected_city=None):
    """
    Recommend salons matching service + budget + location
    
    Location priority:
    1. Extract from message ("in City")
    2. Use detected_city parameter (from request.location or geolocation)
    3. No location filter (return all matching budget/service)
    """
    msg = message.lower()

    budget = None
    service = None
    location = None

    # 💰 Extract budget from message
    m = re.search(r"(\d{2,5})", msg)
    if m:
        budget = int(m.group(1))

    # 🛍️ Extract service from message
    services = get_all_services()
    for s in services:
        if s in msg:
            service = s
            break

    # 📍 Location priority: message → detected_city parameter
    location = extract_city(msg)

    if not location and detected_city:
        # ✅ Use detected city (from geolocation or request.location)
        location = detected_city.lower().strip()

    # salons = get_all_salons()
    salons, next_key = get_salons_batch(batch_size=10)
    results = []

    for s in salons:
        # 📍 Apply location filter if location is specified
        if location:
            salon_city = s.get("city", "").lower().strip()
            address = s.get("address", "").lower()
            
            # Match if detected location is in either:
            # - The extracted city field, OR
            # - The full address (substring match)
            if location not in salon_city and location not in address:
                continue

        # 💰 Apply budget filter if budget is specified
        price = s.get("price", 500)
        if budget and price > budget:
            continue

        results.append(s)

    return results[:3]
    
# ==================================================
# 🎁 GET OFFERS BY SALON ID
# Path: offers/salon/{salonId}
# ==================================================
def get_offers_by_salon_id(salon_id):

    try:
        ref = db.reference(f"salonandspa/offers/salon/{salon_id}")

        data = ref.get() or {}

        offers = []

        for offer_id, offer in data.items():

            status = offer.get("status")
            valid_until = offer.get("validUntil")

            # only approved
            if status != "approved":
                continue

            # check date
            if valid_until:
                today = datetime.now().date()
                try:
                    end = datetime.strptime(valid_until, "%Y-%m-%d").date()
                    if end < today:
                        continue
                except:
                    pass

            offers.append({
                "title": offer.get("title"),
                "discount": offer.get("discount"),
                "description": offer.get("description"),
            })

        return offers

    except Exception as e:
        print("OFFERS ERROR:", e)
        return []
        
# ==================================================
# 🎁 GET ALL ACTIVE OFFERS (ALL SALONS)
# Path: offers/salon
# ==================================================
def get_all_active_offers():
    """
    Fetch all approved offers across all salons
    Returns list of offers with salon_id attached
    """
    try:
        ref = db.reference("salonandspa/offers/salon")
        
        data = ref.get()
        
        # print("OFFERS ROOT:", data)
        all_data = ref.get() or {}

        result = []
        for salon_id, salon_offers in all_data.items():
            if not isinstance(salon_offers, dict):
                continue
            for offer_id, offer in salon_offers.items():
                if offer.get("status") != "approved":
                    continue
                if offer.get("deletedAt"):
                    continue
                result.append({
                    "offer_id": offer_id,
                    "salon_id": salon_id,
                    "title": offer.get("title", ""),
                    "description": offer.get("description", ""),
                    "discount": offer.get("discount", 0),
                    "valid_from": offer.get("validFrom", ""),
                    "valid_until": offer.get("validUntil", ""),
                    "image": offer.get("image", ""),
                })

        return result
    except Exception as e:
        print(f"❌ Firebase error (get_all_active_offers): {e}")
        return []    
        
##################################################################################################


        