/* ======================================================
   DOM REFERENCES
====================================================== */
const chatBox = document.getElementById("chat-box");
const input = document.getElementById("user-input");
const quickActions = document.getElementById("quick-actions");
const form = document.getElementById("chat-form");
const sendBtn = document.getElementById("send-btn");


/* ======================================================
   FRONTEND STATE (STRICT)
====================================================== */
const STATE = {
  sessionId: "session-" + Date.now(),
  currentSalon: null,        // Salon name selected
  awaitingCity: false,       // True when bot asks for city
};


/* ======================================================
   MESSAGE RENDERING
====================================================== */
function addMessage(text, sender) {
  const div = document.createElement("div");
  div.className = `message ${sender}`;
  div.innerHTML = text.replace(/\n/g, "<br>");
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}


/* ======================================================
   CLEAR CARDS (NOT CHAT MESSAGES)
====================================================== */
function clearCards() {
  chatBox.querySelectorAll(".cards-container").forEach(el => el.remove());
}


/* ======================================================
   RENDER SALON CARDS
====================================================== */
function renderSalonCards(salons = []) {
  clearCards();

  if (!Array.isArray(salons) || salons.length === 0) {
    return;
  }

  const container = document.createElement("div");
  container.className = "cards-container";

  salons.forEach(salon => {
    const card = document.createElement("div");
    card.className = "card salon-card";

    const safeAddress = escapeHtml(salon.address || salon.city || "");
    const safeName = escapeHtml(salon.name || "");
    const safeCity = escapeHtml(salon.city || "");

    let ratingHTML = "";
    if (salon.rating && salon.rating > 0) {
      ratingHTML = `<div class="rating-badge"><span class="stars">&#11088;</span> ${salon.rating.toFixed(1)}</div>`;
    }

    card.innerHTML = `
      <div class="card-header">
        <h3 class="salon-name">${safeName}</h3>
        ${ratingHTML}
      </div>
      <div class="card-details">
        <p class="city-badge">&#128205; ${safeCity}</p>
        <p class="address-text">${safeAddress}</p>
      </div>
      <button class="card-btn btn-primary">View services</button>
    `;

    card.querySelector(".card-btn").addEventListener("click", () => {
      STATE.currentSalon = salon.name;
      addMessage("View services", "user");
      sendToBackend("View services");
    });

    container.appendChild(card);
  });

  chatBox.appendChild(container);
}


/* ======================================================
   RENDER SERVICE CARDS
====================================================== */
function renderServiceCards(services = []) {
  clearCards();

  if (!Array.isArray(services) || services.length === 0) {
    return;
  }

  const container = document.createElement("div");
  container.className = "cards-container";

  services.forEach(service => {
    const card = document.createElement("div");
    card.className = "card service-card";

    const safeName = escapeHtml(service.name || "");

    let priceHTML = "";
    if (service.price) {
      priceHTML = `<span class="price-badge">&#128176; &#8377;${service.price}</span>`;
    }

    let durationHTML = "";
    if (service.duration) {
      durationHTML = `<span class="duration-badge">&#9201; ${service.duration} min</span>`;
    }

    card.innerHTML = `
      <div class="card-header">
        <h3 class="service-name">${safeName}</h3>
      </div>
      <div class="card-details">
        <div class="service-specs">
          ${priceHTML}
          ${durationHTML}
        </div>
      </div>
    `;

    container.appendChild(card);
  });

  chatBox.appendChild(container);
}


/* ======================================================
   RENDER QUICK ACTION BUTTONS
====================================================== */
function renderQuickActions(actions = []) {
  quickActions.innerHTML = "";

  if (!Array.isArray(actions)) {
    return;
  }

  actions.forEach(action => {
    const btn = document.createElement("button");
    btn.className = "quick-action-btn";
    btn.innerHTML = `<span>${action}</span>`;

    btn.addEventListener("click", () => {
      addMessage(action, "user");
      sendToBackend(action);
    });

    quickActions.appendChild(btn);
  });
}


/* ======================================================
   HTML ESCAPE (XSS PREVENTION)
====================================================== */
function escapeHtml(text) {
  const div = document.createElement("div");
  div.innerHTML = text.replace(/\n/g, "<br>");
  return div.innerHTML;
}


/* ======================================================
   AUTO DETECT CITY VIA BROWSER GEOLOCATION
====================================================== */
async function detectCity() {
  return new Promise((resolve) => {

    if (!navigator.geolocation) {
      resolve(null);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const { latitude, longitude } = pos.coords;
          const res = await fetch(
            "https://nominatim.openstreetmap.org/reverse?lat=" + latitude + "&lon=" + longitude + "&format=json",
            { headers: { "Accept-Language": "en" } }
          );
          const data = await res.json();
          // Try multiple address fields in order of specificity
          const city =
            data.address?.city ||
            data.address?.town ||
            data.address?.village ||
            data.address?.county ||
            null;
          resolve(city);
        } catch (e) {
          console.error("Reverse geocode error:", e);
          resolve(null);
        }
      },
      (err) => {
        console.warn("Geolocation denied:", err.message);
        resolve(null);
      },
      { timeout: 6000 }
    );
  });
}


/* ======================================================
   SEND MESSAGE TO BACKEND
====================================================== */
async function sendToBackend(message) {
  const typing = document.createElement("div");
  typing.className = "message bot";
  typing.textContent = "Fetching...";
  chatBox.appendChild(typing);

  try {
    const payload = {
      message: message,
      session_id: STATE.sessionId,
      location: null,
      salon_name: STATE.currentSalon,
    };

    // Auto-detect city when user asks for nearby salons
    const locationKeywords = ["near me", "nearby", "near by", "closest", "my location", "around me"];
    const isLocationIntent = locationKeywords.some(kw => message.toLowerCase().includes(kw));

    if (isLocationIntent) {
      typing.textContent = "Detecting your location...";
      const city = await detectCity();
      if (city) {
        payload.location = city;
        // Show detected city as a bot message before the response
        addMessage("Detected your city: " + city, "bot");
      }
      // If detection fails or is denied, backend falls back to asking the user
    }

    // If bot previously asked for city and user typed it manually
    if (STATE.awaitingCity && message.length > 2 && /^[a-zA-Z ]+$/.test(message)) {
      payload.location = message;
    }

    const response = await fetch("http://127.0.0.1:8000/api/chat-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      typing.remove();
      addMessage("Connection error. Please try again.", "bot");
      return;
    }

    typing.remove();

    // Create bot bubble — pre-wrap so \n renders as newlines natively
    const botDiv = document.createElement("div");
    botDiv.className = "message bot";
    const textNode = document.createElement("p");
    textNode.style.margin = "0";
    textNode.style.whiteSpace = "pre-wrap";
    botDiv.appendChild(textNode);
    chatBox.appendChild(botDiv);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const sentinelIdx = buffer.indexOf("\n\n__META__");

      if (sentinelIdx !== -1) {
        // Final text render
        textNode.textContent = buffer.slice(0, sentinelIdx);

        // Parse and render cards + suggestions
        try {
          const meta = JSON.parse(buffer.slice(sentinelIdx + "\n\n__META__".length));

          if (meta.salons && meta.salons.length > 0) {
            renderSalonCards(meta.salons);
          }
          if (meta.services && meta.services.length > 0) {
            renderServiceCards(meta.services);
          }
          if (meta.suggestions && meta.suggestions.length > 0) {
            renderQuickActions(meta.suggestions);
          }
          if (meta.type === "ask_location") {
            STATE.awaitingCity = true;
          } else {
            STATE.awaitingCity = false;
          }
        } catch (e) {
          console.error("Meta parse error:", e);
        }

        break;
      }

      // Live stream — smooth append, no flicker
      textNode.textContent = buffer;
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    chatBox.scrollTop = chatBox.scrollHeight;

  } catch (error) {
    typing.remove();
    addMessage("Server error. Please check connection.", "bot");
    console.error("API Error:", error);
  }
}


/* ======================================================
   USER MESSAGE HANDLER
====================================================== */
function handleUserMessage() {
  const text = input.value.trim();
  if (!text) return;

  addMessage(text, "user");
  input.value = "";

  sendToBackend(text);
}


/* ======================================================
   INITIALIZATION
====================================================== */
window.addEventListener("load", () => {
  addMessage(
    "Hi! I'm Nexsalon Concierge\nI can help you find the perfect salon!",
    "bot"
  );

  renderQuickActions([
    "Show salons near me",
    "Show all salons",
    "Top rated salons",
    "Trending salons",
  //  "Best salons",
    "Beauty tips",
  ]);
});


/* ======================================================
   EVENT LISTENERS
====================================================== */
form.addEventListener("submit", (e) => {
  e.preventDefault();
  handleUserMessage();
});

sendBtn.addEventListener("click", handleUserMessage);

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleUserMessage();
  }
});