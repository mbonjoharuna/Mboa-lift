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

    const streetNegotiationCard = document.getElementById("streetNegotiationCard");
    const negotiatedFareInput = document.getElementById("negotiatedFareInput");
    const btnFareMinus100 = document.getElementById("btnFareMinus100");
    const btnFarePlus100 = document.getElementById("btnFarePlus100");
    const negotiationStatusPill = document.getElementById("negotiationStatusPill");
    const negotiationStatusHint = document.getElementById("negotiationStatusHint");
    const bargainChips = document.querySelectorAll(".bargain-chip");

    let currentBaseFare = 0;

    if (!pickup || !destination || !fareBox) return;

    function formatNumber(num) {
        return Math.round(Number(num) || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function updateNegotiationUI() {
        if (!negotiatedFareInput || !currentBaseFare) return;
        const offer = parseFloat(negotiatedFareInput.value) || currentBaseFare;
        const diff = Math.round(offer - currentBaseFare);

        bargainChips.forEach(chip => {
            const delta = chip.getAttribute("data-delta");
            const action = chip.getAttribute("data-action");
            if (action === "reset" && diff === 0) {
                chip.classList.add("active");
            } else if (delta && parseInt(delta, 10) === diff) {
                chip.classList.add("active");
            } else {
                chip.classList.remove("active");
            }
        });

        if (negotiationStatusPill && negotiationStatusHint) {
            if (diff < 0) {
                negotiationStatusPill.className = "negotiation-status-pill status-discount";
                negotiationStatusPill.textContent = "🤝 Offre négociée : " + formatNumber(offer) + " XAF (" + diff + " F)";
                negotiationStatusHint.textContent = "Vous proposez " + Math.abs(diff) + " FCFA de moins que le tarif standard. Les chauffeurs peuvent accepter ou contre-proposer.";
            } else if (diff > 0) {
                negotiationStatusPill.className = "negotiation-status-pill status-tip";
                negotiationStatusPill.textContent = "⚡ Offre prioritaire : " + formatNumber(offer) + " XAF (+" + diff + " F)";
                negotiationStatusHint.textContent = "Bonus de rapidité pour attirer un chauffeur immédiatement en heure de pointe.";
            } else {
                negotiationStatusPill.className = "negotiation-status-pill status-standard";
                negotiationStatusPill.textContent = "Prix standard calculé (" + formatNumber(offer) + " XAF)";
                negotiationStatusHint.textContent = "Tarif équitable normal recommandé pour Douala.";
            }
        }
    }

    function setNegotiatedFare(amount) {
        if (!negotiatedFareInput) return;
        const minFare = Math.max(300, Math.round(currentBaseFare * 0.40));
        const maxFare = Math.round(currentBaseFare * 3.0);
        let clamped = Math.max(minFare, Math.min(maxFare, Math.round(amount)));
        negotiatedFareInput.value = clamped;
        updateNegotiationUI();
    }

    if (btnFareMinus100) {
        btnFareMinus100.addEventListener("click", function() {
            const current = parseFloat(negotiatedFareInput.value) || currentBaseFare;
            setNegotiatedFare(current - 100);
        });
    }

    if (btnFarePlus100) {
        btnFarePlus100.addEventListener("click", function() {
            const current = parseFloat(negotiatedFareInput.value) || currentBaseFare;
            setNegotiatedFare(current + 100);
        });
    }

    if (negotiatedFareInput) {
        negotiatedFareInput.addEventListener("input", updateNegotiationUI);
        negotiatedFareInput.addEventListener("change", function() {
            setNegotiatedFare(parseFloat(this.value) || currentBaseFare);
        });
    }

    bargainChips.forEach(chip => {
        chip.addEventListener("click", function(e) {
            e.preventDefault();
            const action = this.getAttribute("data-action");
            const delta = this.getAttribute("data-delta");
            if (action === "reset") {
                setNegotiatedFare(currentBaseFare);
            } else if (delta) {
                setNegotiatedFare(currentBaseFare + parseInt(delta, 10));
            }
        });
    });

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
            if (streetNegotiationCard) streetNegotiationCard.style.display = "none";
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
                    currentBaseFare = data.fare;
                    if (streetNegotiationCard) {
                        streetNegotiationCard.style.display = "block";
                        const minFare = Math.max(300, Math.round(data.fare * 0.40));
                        if (negotiatedFareInput) {
                            negotiatedFareInput.min = minFare;
                            negotiatedFareInput.max = Math.round(data.fare * 3.0);
                        }
                        setNegotiatedFare(data.fare);
                    }
                } else {
                    fareAmount.textContent = _t("Not available");
                    fareAmount.style.color = "#dc3545";
                    if (streetNegotiationCard) streetNegotiationCard.style.display = "none";
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
                currentBaseFare = baseEst;
                if (streetNegotiationCard) {
                    streetNegotiationCard.style.display = "block";
                    setNegotiatedFare(baseEst);
                }
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
