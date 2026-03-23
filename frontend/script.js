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
  currentSalon: null,        // ✅ Salon name selected
  awaitingCity: false,       // ✅ True when bot asks for city
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

    // Safe HTML escaping
    const safeAddress = escapeHtml(salon.address || salon.city || "");
    const safeName = escapeHtml(salon.name || "");
    const safeCity = escapeHtml(salon.city || "");
    
    // Show rating properly
    let ratingHTML = "";
    if (salon.rating && salon.rating > 0) {
      ratingHTML = `<div class="rating-badge"><span class="stars">⭐</span> ${salon.rating.toFixed(1)}</div>`;
    }

    card.innerHTML = `
      <div class="card-header">
        <h3 class="salon-name">${safeName}</h3>
        ${ratingHTML}
      </div>
      <div class="card-details">
        <p class="city-badge">📍 ${safeCity}</p>
        <p class="address-text">${safeAddress}</p>
      </div>
      <button class="card-btn btn-primary">View services</button>
    `;

    // ✅ When user clicks "View services"
    card.querySelector(".card-btn").addEventListener("click", () => {
      STATE.currentSalon = salon.name;  // ✅ Save salon name
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
      priceHTML = `<span class="price-badge">💰 ₹${service.price}</span>`;
    }
    
    let durationHTML = "";
    if (service.duration) {
      durationHTML = `<span class="duration-badge">⏱️ ${service.duration} min</span>`;
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
    // Wrap text in span for z-index layering over the ::before gradient
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
   SEND MESSAGE TO BACKEND
====================================================== */
async function sendToBackend(message) {
  // Show typing indicator
  const typing = document.createElement("div");
  typing.className = "message bot";
  typing.textContent = "Fetching…";
  chatBox.appendChild(typing);

  try {
    // ✅ Build payload with strict state
    const payload = {
      message: message,
      session_id: STATE.sessionId,
      location: STATE.awaitingCity ? null : null,  // Reset city intent
      salon_name: STATE.currentSalon,
    };

    // ✅ If bot asked for city and user provided text, send as city
    if (STATE.awaitingCity && message.length > 2 && /^[a-zA-Z ]+$/.test(message)) {
      payload.location = message;
    }
    const response = await fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      addMessage("❌ Connection error. Please try again.", "bot");
      return;
    }

    const reader = response.body.getReader()

    typing.remove()
    
    let botDiv = document.createElement("div")
    botDiv.className = "message bot"
    chatBox.appendChild(botDiv)
    
    while (true) {
    
      const { done, value } = await reader.read()
    
      if (done) break
    
      const text = new TextDecoder().decode(value)
    
      botDiv.innerHTML += text
await new Promise(r => setTimeout(r, 15))
      
      chatBox.scrollTop = chatBox.scrollHeight   // ✅ add this
    
    }
    
    STATE.awaitingCity = false

  } catch (error) {
    typing.remove();
    addMessage("❌ Server error. Please check connection.", "bot");
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
  // Show welcome message
  addMessage(
    "👋 Hi! I'm Nexsalon Concierge ✨\n\nI can help you find the perfect salon!",
    "bot"
  );

  // Show quick actions
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