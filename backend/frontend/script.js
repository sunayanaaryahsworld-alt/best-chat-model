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

// function renderOffersCards(offers = []) {

//   clearCards();

//   if (!Array.isArray(offers) || offers.length === 0) {
//     return;
//   }

//   const container = document.createElement("div");
//   container.className = "cards-container";

//   offers.forEach(o => {

//     const card = document.createElement("div");
//     card.className = "card offer-card";

//     card.innerHTML = `
//       <div class="card-header">
//         <h3>🎁 ${o.title || "Offer"}</h3>
//       </div>

//       <div class="card-details">
//         <p>${o.description || ""}</p>
//         <p><b>${o.discount || 0}% OFF</b></p>
//       </div>
//     `;

//     container.appendChild(card);

//   });

//   chatBox.appendChild(container);
// }


/* ======================================================
   RENDER SALON CARDS
====================================================== */
// function renderSalonCards(salons = []) {
//   clearCards();

//   if (!Array.isArray(salons) || salons.length === 0) {
//     return;
//   }

//   const container = document.createElement("div");
//   container.className = "cards-container";

//   salons.forEach(salon => {
//     const card = document.createElement("div");
//     card.className = "card salon-card";

//     const safeAddress = escapeHtml(salon.address || salon.city || "");
//     const safeName = escapeHtml(salon.name || "");
//     const safeCity = escapeHtml(salon.city || "");

//     let ratingHTML = "";
//     if (salon.rating && salon.rating > 0) {
//       ratingHTML = `<div class="rating-badge"><span class="stars">&#11088;</span> ${salon.rating.toFixed(1)}</div>`;
//     }

//     // card.innerHTML = `
//     //   <div class="card-header">
//     //     <h3 class="salon-name">${safeName}</h3>
//     //     ${ratingHTML}
//     //   </div>
//     //   <div class="card-details">
//     //     <p class="city-badge">&#128205; ${safeCity}</p>
//     //     <p class="address-text">${safeAddress}</p>
//     //   </div>
//     //   <button class="card-btn btn-primary">View services</button>
//     // `;
//     let offersHTML = "";

// if (salon.offers && salon.offers.length > 0) {

//   offersHTML += `<div class="offers-box">`;

//   salon.offers.forEach(o => {

//     offersHTML += `
//       <div class="offer-item">
//         🎁 ${o.title || "Offer"} 
//         ${o.discount ? "- " + o.discount + "%" : ""}
//       </div>
//     `;

//   });

//   offersHTML += `</div>`;
// }

// // card.innerHTML = `
// //   <div class="card-header">
// //     <h3 class="salon-name">${safeName}</h3>
// //     ${ratingHTML}
// //   </div>

// //   <div class="card-details">
// //     <p class="city-badge">&#128205; ${safeCity}</p>
// //     <p class="address-text">${safeAddress}</p>
// //   </div>

// //   ${offersHTML}

// //   <button class="card-btn btn-primary">View services</button>
// // `;

// let offerButton = "";

// if (salon.offers && salon.offers.length > 0) {
//   offerButton = `
//     <button class="card-btn btn-secondary view-offers-btn">
//       View offers
//     </button>
//   `;
// }

// card.innerHTML = `
//   <div class="card-header">
//     <h3 class="salon-name">${safeName}</h3>
//     ${ratingHTML}
//   </div>

//   <div class="card-details">
//     <p class="city-badge">&#128205; ${safeCity}</p>
//     <p class="address-text">${safeAddress}</p>
//   </div>

//   ${offersHTML}

//   <div class="card-btn-row">
//     <button class="card-btn btn-primary view-services-btn">
//       View services
//     </button>

//     ${offerButton}
//   </div>
// `;

//     // card.querySelector(".card-btn").addEventListener("click", () => {
//     //   STATE.currentSalon = salon.name;
//     //   addMessage("View services", "user");
//     //   sendToBackend("View services");
//     // });
//     card.querySelector(".view-services-btn").addEventListener("click", () => {
//   STATE.currentSalon = salon.name;
//   addMessage("View services", "user");
//   sendToBackend("View services");
// });

// const offerBtn = card.querySelector(".view-offers-btn");

// if (offerBtn) {
//   offerBtn.addEventListener("click", () => {
//     STATE.currentSalon = salon.name;
//     addMessage("Show offers", "user");
//     sendToBackend("show offers for " + salon.name);
//   });
// }

//     container.appendChild(card);
//   });

//   chatBox.appendChild(container);
// }
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
    const safeName    = escapeHtml(salon.name || "");
    const safeCity    = escapeHtml(salon.city || "");
 
    let ratingHTML = "";
    if (salon.rating && salon.rating > 0) {
      ratingHTML = `<div class="rating-badge"><span class="stars">&#11088;</span> ${salon.rating.toFixed(1)}</div>`;
    }
 
    // Only show "View offers" button if this salon actually has offers
    const hasOffers = salon.offers && salon.offers.length > 0;
    const offerBtnHTML = hasOffers
      ? `<button class="card-btn btn-primary view-offers-btn">View offers</button>`
      : "";
 
    card.innerHTML = `
      <div class="card-header">
        <h3 class="salon-name">${safeName}</h3>
        ${ratingHTML}
      </div>
 
      <div class="card-details">
        <p class="city-badge">&#128205; ${safeCity}</p>
        <p class="address-text">${safeAddress}</p>
      </div>
 
      <div class="card-btn-row">
        <button class="card-btn btn-primary view-services-btn">View services</button>
        ${offerBtnHTML}
      </div>
    `;
 
    // View services click
    card.querySelector(".view-services-btn").addEventListener("click", () => {
      STATE.currentSalon = salon.name;
      addMessage("View services", "user");
      sendToBackend("View services");
    });
 
    // View offers click — calls backend with salon name, shows only that salon's offers
    const offerBtn = card.querySelector(".view-offers-btn");
    if (offerBtn) {
      offerBtn.addEventListener("click", () => {
        STATE.currentSalon = salon.name;
        addMessage(`Show offers for ${salon.name}`, "user");
        sendToBackend(`show offers for ${salon.name}`);
      });
    }
 
    container.appendChild(card);
  });
 
  chatBox.appendChild(container);
}

function renderOffersCards(offers = []) {
  clearCards();
 
  if (!Array.isArray(offers) || offers.length === 0) {
    addMessage("No active offers for this salon right now.", "bot");
    return;
  }
 
  const container = document.createElement("div");
  container.className = "cards-container";
 
  offers.forEach(o => {
    const card = document.createElement("div");
    card.className = "card offer-card";
 
    card.innerHTML = `
      <div class="card-header">
        <h3>🎁 ${escapeHtml(o.title || "Offer")}</h3>
      </div>
      <div class="card-details">
        <p>${escapeHtml(o.description || "")}</p>
        ${o.discount ? `<p><b>${o.discount}% OFF</b></p>` : ""}
      </div>
    `;
 
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
          // const city =
          //   data.address?.city ||
          //   data.address?.town ||
          //   data.address?.village ||
          //   data.address?.county ||
          //   null;
          // resolve(city);
         
          // TO THIS:
          let area =
            data.address?.suburb ||
            data.address?.neighbourhood ||
            data.address?.quarter ||
            data.address?.village ||
            data.address?.town ||
            data.address?.city ||
            null;
          
          if (area) {
            // Strip directional suffixes: "Belapur West" → "Belapur"
            area = area
              .replace(/\s+(West|East|North|South|Central|New|Old)$/i, "")
              .trim();
          }
          
          resolve(area);

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


function getLoadingText(message) {

    message = message.toLowerCase();

    if (message.includes("offer")) {
        return "Please wait while we are fetching the best offers for you...";
    }

    if (message.includes("salon")) {
        return "Please wait while we are fetching salons for you...";
    }

    if (message.includes("spa")) {
        return "Please wait while we are fetching spa details for you...";
    }

    if (message.includes("service")) {
        return "Please wait while we are fetching services...";
    }

    if (message.includes("near") || message.includes("location")) {
        return "Please wait while we are finding nearby salons...";
    }

    if (message.includes("best")) {
        return "Please wait while we are finding the best salons for you...";
    }

    return "Please wait while we are fetching data...";
}

/* ======================================================
   SEND MESSAGE TO BACKEND
====================================================== */
async function sendToBackend(message) {
  const typing = document.createElement("div");
  typing.className = "message bot";
  // typing.textContent = "please wait while we are Fetching the data...";
typing.textContent = getLoadingText(message);
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
    let lastRenderedLength = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const sentinelIdx = buffer.indexOf("\n\n__META__");

      if (sentinelIdx !== -1) {
        // Final text render
        const finalText = buffer.slice(0, sentinelIdx);
        textNode.textContent = finalText;

        // Parse and render cards + suggestions
//         try {
//           const meta = JSON.parse(buffer.slice(sentinelIdx + "\n\n__META__".length));
//           console.log("META:", meta)

//           if (meta.salons && meta.salons.length > 0) {
//             renderSalonCards(meta.salons);
//           }
//           if (meta.services && meta.services.length > 0) {
//             renderServiceCards(meta.services);
//           }
//           if (meta.suggestions && meta.suggestions.length > 0) {
//             renderQuickActions(meta.suggestions);
//           }
//           if (meta.offers && meta.offers.length > 0) {
//   // renderOffersCards(meta.offers);
// }
//           if (meta.type === "ask_location") {
//             STATE.awaitingCity = true;
//           } else {
//             STATE.awaitingCity = false;
//           }
//         } catch (e) {
//           console.error("Meta parse error:", e);
//         }
// =====================================================
// Inside sendToBackend(), replace your meta parse block with this.
// The only addition is the `meta.offers` check at the end.
// =====================================================

try {
  const meta = JSON.parse(buffer.slice(sentinelIdx + "\n\n__META__".length));
  console.log("META:", meta);

  if (meta.salons && meta.salons.length > 0) {
    renderSalonCards(meta.salons);
  }
  if (meta.services && meta.services.length > 0) {
    renderServiceCards(meta.services);
  }
  // ✅ NEW: render offer cards only when backend explicitly sends offers
  if (meta.type === "offers" && meta.offers && meta.offers.length > 0) {
    renderOffersCards(meta.offers);
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

      // Live stream — append only new content for smooth word-by-word effect
      const newContent = buffer.slice(lastRenderedLength);
      if (newContent) {
        textNode.textContent = buffer;
        lastRenderedLength = buffer.length;
      }
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
    "Hi! I'm Nexsalon Concierge \n I can help you find the perfect salon!",
    "bot"
  );

  renderQuickActions([
    "Show salons near me",
    "offers near me",
    "Show all salons",
    "Top rated salons",
    "Trending salons",
    "show offers",
    "Beauty tips",
    "Haircut under 500"
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