/**
 * script.js
 * ----------
 * Client-side JavaScript for MboaLift.
 *
 * Responsibilities:
 * - Mobile menu toggle
 * - Fare calculation (display only – server recalculates)
 * - Basic form validation
 * - Confirmation dialogs (via HTML onsubmit)
 *
 * IMPORTANT: Never put API keys or secrets in this file.
 */

// ---------- Mobile menu + MboaLift loading state ----------
document.addEventListener("DOMContentLoaded", function () {
    const loader = document.getElementById("appLoader");
    if (loader) {
        window.setTimeout(() => loader.classList.remove("is-visible"), 180);
        window.addEventListener("beforeunload", () => loader.classList.add("is-visible"));
    }
    const toggle = document.getElementById("menuToggle");
    const nav = document.querySelector(".nav");
    if (toggle && nav) {
        toggle.addEventListener("click", function () {
            nav.classList.toggle("open");
        });
    }
});

// Helper to translate strings via i18n
function _t(str) {
    return (window.MboaLiftI18n && window.MboaLiftI18n.t) ? window.MboaLiftI18n.t(str) : str;
}

// ---------- Fare calculator (Request Ride page) ----------
function initFareCalculator() {
    const pickup = document.getElementById("pickup");
    const destination = document.getElementById("destination");
    const fareBox = document.getElementById("fareBox");
    const farePickup = document.getElementById("farePickup");
    const fareDestination = document.getElementById("fareDestination");
    const fareAmount = document.getElementById("fareAmount");
    const fareMode = document.getElementById("fareMode");

    if (!pickup || !destination || !fareBox) return;

    function updateFare() {
        const p = pickup.value.trim();
        const d = destination.value.trim();
        const vehicleInput = document.querySelector('input[name="vehicle_type"]:checked');
        const vehicleType = vehicleInput ? vehicleInput.value : "taxi";

        if (!p || !d) {
            fareBox.style.display = "none";
            return;
        }

        if (p.toLowerCase() === d.toLowerCase()) {
            fareBox.style.display = "block";
            farePickup.textContent = p;
            fareDestination.textContent = d;
            fareAmount.textContent = _t("Invalid (same location)");
            fareAmount.style.color = "#dc3545";
            return;
        }

        // Call the Flask API endpoint for the official fare with vehicle_type
        fetch("/api/fare?pickup=" + encodeURIComponent(p) + "&destination=" + encodeURIComponent(d) + "&vehicle_type=" + encodeURIComponent(vehicleType))
            .then(function (res) { return res.json(); })
            .then(function (data) {
                fareBox.style.display = "block";
                farePickup.textContent = p;
                fareDestination.textContent = d;
                if (fareMode) {
                    fareMode.textContent = data.vehicle_label || (vehicleType === "bendskin" ? "Bendskin 🏍️" : (vehicleType === "comfort" ? "Voiture Confort 🚗" : "Taxi Jaune 🚕"));
                }
                if (data.fare !== null && data.fare !== undefined) {
                    fareAmount.textContent = data.fare + " " + (data.currency || "XAF");
                    fareAmount.style.color = "";
                } else {
                    fareAmount.textContent = _t("Not available");
                    fareAmount.style.color = "#dc3545";
                }
            })
            .catch(function () {
                // Fallback: simple client-side estimate (server will still validate)
                fareBox.style.display = "block";
                farePickup.textContent = p;
                fareDestination.textContent = d;
                var baseEst = 1200;
                if (vehicleType === "bendskin") baseEst = 850;
                else if (vehicleType === "comfort") baseEst = 2200;
                fareAmount.textContent = baseEst + " " + _t("XAF (estimate)");
                fareAmount.style.color = "";
            });
    }

    pickup.addEventListener("change", updateFare);
    pickup.addEventListener("input", updateFare);
    destination.addEventListener("change", updateFare);
    destination.addEventListener("input", updateFare);
    document.querySelectorAll('input[name="vehicle_type"]').forEach(function(radio) {
        radio.addEventListener("change", updateFare);
    });
    window.addEventListener("languageChanged", function() {
        if (fareBox.style.display !== "none") updateFare();
    });
}

// ---------- Client-side validation helpers ----------
function validateRegisterForm() {
    const form = document.getElementById("registerForm");
    if (!form) return true;

    const password = form.querySelector("#password").value;
    const confirm = form.querySelector("#confirm_password").value;

    if (password !== confirm) {
        alert("Passwords do not match.");
        return false;
    }
    if (password.length < 6) {
        alert("Password must be at least 6 characters.");
        return false;
    }
    return true;
}

// Attach validation if form exists
document.addEventListener("DOMContentLoaded", function () {
    const regForm = document.getElementById("registerForm");
    if (regForm) {
        regForm.addEventListener("submit", function (e) {
            if (!validateRegisterForm()) {
                e.preventDefault();
            }
        });
    }

    // Ride form basic check
    const rideForm = document.getElementById("rideForm");
    if (rideForm) {
        rideForm.addEventListener("submit", function (e) {
            const p = document.getElementById("pickup").value;
            const d = document.getElementById("destination").value;
            if (p && d && p === d) {
                e.preventDefault();
                alert("Pickup and destination cannot be the same.");
            }
        });
    }
});


// ============================================================
// Floating AI Chatbot (available on every page)
// ============================================================
document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("chatbotToggle");
    const closeBtn = document.getElementById("chatbotClose");
    const panel = document.getElementById("chatbotPanel");
    const form = document.getElementById("chatbotForm");
    const input = document.getElementById("chatbotInput");
    const messages = document.getElementById("chatbotMessages");

    if (!toggleBtn || !panel || !form) return;

    // Open / close panel
    toggleBtn.addEventListener("click", function () {
        panel.hidden = !panel.hidden;
        if (!panel.hidden) {
            input.focus();
        }
    });

    closeBtn.addEventListener("click", function () {
        panel.hidden = true;
    });

    // Helper: add a message bubble
    function addMessage(text, type) {
        const div = document.createElement("div");
        div.className = "chatbot-msg " + type;
        // Convert simple newlines to <br>
        div.innerHTML = text.replace(/\n/g, "<br>");
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    // Send message
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const text = input.value.trim();
        if (!text) return;

        // Show user message
        addMessage(text, "user");
        input.value = "";

        // Show loading
        const loading = addMessage(_t("Thinking..."), "bot loading");
        const sendBtn = form.querySelector("button");
        sendBtn.disabled = true;

        // Call Flask API (no API key in JavaScript)
        fetch("/api/ai-chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message: text })
        })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            loading.remove();
            addMessage(data.reply || _t("Sorry, I could not answer."), "bot");
        })
        .catch(function () {
            loading.remove();
            addMessage(_t("Sorry, I could not reach the assistant. Please try again."), "bot");
        })
        .finally(function () {
            sendBtn.disabled = false;
            input.focus();
        });
    });
});
