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

    const cargoRadios = document.querySelectorAll('input[name="cargo_type"]');
    const cargoCards = document.querySelectorAll('.cargo-card');
    const fareCargoRow = document.getElementById("fareCargoRow");
    const fareCargoAmount = document.getElementById("fareCargoAmount");
    const cargoBendskinWarning = document.getElementById("cargoBendskinWarning");
    const marketProximityAlert = document.getElementById("marketProximityAlert");
    const marketProximityText = document.getElementById("marketProximityText");
    const bendskinRadio = document.querySelector('input[name="vehicle_type"][value="bendskin"]');
    const bendskinCard = bendskinRadio ? bendskinRadio.closest(".vehicle-card") : null;
    const taxiRadio = document.querySelector('input[name="vehicle_type"][value="taxi"]');
    const taxiCard = taxiRadio ? taxiRadio.closest(".vehicle-card") : null;

    const MARKET_KEYWORDS = [
        { key: "mboppi", name: "Marché Mboppi (Bépanda)", tip: "Vivres frais, manioc & commerce en gros" },
        { key: "mbopi", name: "Marché Mboppi (Bépanda)", tip: "Vivres frais & commerce en gros" },
        { key: "central", name: "Marché Central (New Bell)", tip: "Textiles, maroquinerie & vivres" },
        { key: "sandaga", name: "Marché Sandaga", tip: "Grossistes vivres & régimes de plantains" },
        { key: "dakar", name: "Marché Dakar (New Bell)", tip: "Vivres frais & friperie" },
        { key: "deido", name: "Marché Deïdo", tip: "Poissons frais du Wouri & vivres" },
        { key: "déïdo", name: "Marché Deïdo", tip: "Poissons frais du Wouri & vivres" },
        { key: "new bell", name: "Secteur Marché Central / Sandaga", tip: "Pôle de commerce & vivres" },
        { key: "newbell", name: "Secteur Marché Central / Sandaga", tip: "Pôle de commerce & vivres" },
        { key: "bonabéri", name: "Marché Bonabéri", tip: "Vivriers provenant du Moungo" },
        { key: "bonaberi", name: "Marché Bonabéri", tip: "Vivriers provenant du Moungo" },
    ];

    function checkMarketProximity(p, d) {
        if (!marketProximityAlert) return;
        const combined = ((p || "") + " " + (d || "")).toLowerCase();
        let matchedMarket = null;
        for (let i = 0; i < MARKET_KEYWORDS.length; i++) {
            if (combined.indexOf(MARKET_KEYWORDS[i].key) !== -1) {
                matchedMarket = MARKET_KEYWORDS[i];
                break;
            }
        }
        if (matchedMarket) {
            marketProximityAlert.style.display = "flex";
            if (marketProximityText) {
                marketProximityText.textContent = "Proximité de " + matchedMarket.name + " (" + matchedMarket.tip + "). Si vous transportez des sacs ou cartons, optez pour l'option Marché (+300 F) pour filtrer un taxi avec coffre ou galerie.";
            }
        } else {
            marketProximityAlert.style.display = "none";
        }
    }

    function handleCargoCompatibility() {
        const checkedCargo = document.querySelector('input[name="cargo_type"]:checked');
        const cargoType = checkedCargo ? checkedCargo.value : "light";

        // Update active class on cargo cards
        cargoCards.forEach(card => {
            const radio = card.querySelector('input[name="cargo_type"]');
            if (radio && radio.checked) {
                card.classList.add("active");
            } else {
                card.classList.remove("active");
            }
        });

        // Bendskin cannot transport market cargo or heavy luggage
        if (cargoType === "market" || cargoType === "heavy") {
            if (cargoBendskinWarning) cargoBendskinWarning.style.display = "flex";
            if (bendskinRadio) {
                bendskinRadio.disabled = true;
                if (bendskinCard) bendskinCard.classList.add("disabled-by-cargo");
            }
            if (bendskinRadio && bendskinRadio.checked && taxiRadio) {
                taxiRadio.checked = true;
                if (bendskinCard) bendskinCard.classList.remove("active");
                if (taxiCard) taxiCard.classList.add("active");
            }
        } else {
            if (cargoBendskinWarning) cargoBendskinWarning.style.display = "none";
            if (bendskinRadio) {
                bendskinRadio.disabled = false;
                if (bendskinCard) bendskinCard.classList.remove("disabled-by-cargo");
            }
        }
    }

    cargoRadios.forEach(radio => {
        radio.addEventListener("change", function() {
            handleCargoCompatibility();
            updateFare();
        });
    });

    function updateFare() {
        const p = pickup.value.trim();
        const d = destination.value.trim();
        const vehicleInput = document.querySelector('input[name="vehicle_type"]:checked');
        const vehicleType = vehicleInput ? vehicleInput.value : "taxi";
        const cargoInput = document.querySelector('input[name="cargo_type"]:checked');
        const cargoType = cargoInput ? cargoInput.value : "light";

        checkMarketProximity(p, d);

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
            if (fareCargoRow) fareCargoRow.style.display = "none";
            if (streetNegotiationCard) streetNegotiationCard.style.display = "none";
            return;
        }

        // Call the Flask API endpoint for the official fare with vehicle_type and cargo_type
        const apiUrl = "/api/fare?pickup=" + encodeURIComponent(p) +
                       "&destination=" + encodeURIComponent(d) +
                       "&vehicle_type=" + encodeURIComponent(vehicleType) +
                       "&cargo_type=" + encodeURIComponent(cargoType);

        fetch(apiUrl)
            .then(function (res) { return res.json(); })
            .then(function (data) {
                fareBox.style.display = "block";
                farePickup.textContent = p;
                fareDestination.textContent = d;
                if (fareMode) {
                    fareMode.textContent = data.vehicle_label || (vehicleType === "bendskin" ? "Bendskin 🏍️" : (vehicleType === "comfort" ? "Voiture Confort 🚗" : "Taxi Jaune 🚕"));
                }

                // Show cargo surcharge row if applicable
                if (fareCargoRow && fareCargoAmount) {
                    if (data.cargo_fee && data.cargo_fee > 0) {
                        fareCargoRow.style.display = "flex";
                        fareCargoAmount.textContent = "+" + formatNumber(data.cargo_fee) + " " + (data.currency || "XAF");
                    } else {
                        fareCargoRow.style.display = "none";
                    }
                }

                if (data.fare !== null && data.fare !== undefined) {
                    fareAmount.textContent = formatNumber(data.fare) + " " + (data.currency || "XAF");
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
                var cargoExtra = (cargoType === "market") ? 300 : ((cargoType === "heavy") ? 600 : 0);
                var totalEst = baseEst + cargoExtra;

                if (fareCargoRow && fareCargoAmount) {
                    if (cargoExtra > 0) {
                        fareCargoRow.style.display = "flex";
                        fareCargoAmount.textContent = "+" + cargoExtra + " XAF";
                    } else {
                        fareCargoRow.style.display = "none";
                    }
                }

                fareAmount.textContent = formatNumber(totalEst) + " " + _t("XAF (estimate)");
                fareAmount.style.color = "";
                currentBaseFare = totalEst;
                if (streetNegotiationCard) {
                    streetNegotiationCard.style.display = "block";
                    setNegotiatedFare(totalEst);
                }
            });
    }

    // Initialize cargo state
    handleCargoCompatibility();

    pickup.addEventListener("change", updateFare);
    pickup.addEventListener("input", updateFare);
    destination.addEventListener("change", updateFare);
    destination.addEventListener("input", updateFare);
    document.querySelectorAll('input[name="vehicle_type"]').forEach(function(radio) {
        radio.addEventListener("change", function() {
            document.querySelectorAll(".vehicle-card").forEach(c => c.classList.remove("active"));
            const parent = this.closest(".vehicle-card");
            if (parent) parent.classList.add("active");
            updateFare();
        });
    });
    window.addEventListener("languageChanged", function() {
        if (fareBox.style.display !== "none") updateFare();
    });
}

// ---------- Scheduled Early-Morning Airport & Port Shuttles ----------
function initScheduledShuttleSystem() {
    const tabModeNow = document.getElementById("tabModeNow");
    const tabModeScheduled = document.getElementById("tabModeScheduled");
    const bookingModeInput = document.getElementById("bookingModeInput");
    const scheduledShuttlePanel = document.getElementById("scheduledShuttlePanel");
    const scheduledTimeInput = document.getElementById("scheduledTimeInput");
    const scheduledTypeSelect = document.getElementById("scheduledTypeSelect");
    const flightNotesInput = document.getElementById("flightNotesInput");
    const submitRideBtn = document.getElementById("submitRide");
    const presetChips = document.querySelectorAll(".shuttle-preset-chip");
    const destinationInput = document.getElementById("destination");

    if (!tabModeNow || !tabModeScheduled || !bookingModeInput) return;

    function toDateTimeLocalString(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    }

    function updateDateBounds() {
        if (!scheduledTimeInput) return;
        const now = new Date();
        const minDate = new Date(now.getTime() + 15 * 60 * 1000);
        const maxDate = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);

        scheduledTimeInput.min = toDateTimeLocalString(minDate);
        scheduledTimeInput.max = toDateTimeLocalString(maxDate);

        if (!scheduledTimeInput.value) {
            const tomorrowMorning = new Date();
            tomorrowMorning.setDate(tomorrowMorning.getDate() + 1);
            tomorrowMorning.setHours(5, 30, 0, 0);
            scheduledTimeInput.value = toDateTimeLocalString(tomorrowMorning);
        }
    }

    function setBookingMode(mode) {
        bookingModeInput.value = mode;
        if (mode === "scheduled") {
            tabModeScheduled.classList.add("active");
            tabModeNow.classList.remove("active");
            if (scheduledShuttlePanel) scheduledShuttlePanel.style.display = "block";
            updateDateBounds();
            if (submitRideBtn) {
                submitRideBtn.innerHTML = (window.MboaLiftI18n && window.MboaLiftI18n.t)
                    ? window.MboaLiftI18n.t("✈️ Réserver ma navette planifiée")
                    : "✈️ Réserver ma navette planifiée";
            }
        } else {
            tabModeNow.classList.add("active");
            tabModeScheduled.classList.remove("active");
            if (scheduledShuttlePanel) scheduledShuttlePanel.style.display = "none";
            if (submitRideBtn) {
                submitRideBtn.innerHTML = (window.MboaLiftI18n && window.MboaLiftI18n.t)
                    ? window.MboaLiftI18n.t("Commander la course")
                    : "Commander la course";
            }
        }
    }

    tabModeNow.addEventListener("click", function() { setBookingMode("now"); });
    tabModeScheduled.addEventListener("click", function() { setBookingMode("scheduled"); });

    presetChips.forEach(function(chip) {
        chip.addEventListener("click", function(e) {
            e.preventDefault();
            presetChips.forEach(function(c) { c.classList.remove("active"); });
            chip.classList.add("active");

            const dest = chip.getAttribute("data-dest");
            const timeStr = chip.getAttribute("data-time");
            const notes = chip.getAttribute("data-notes");
            const type = chip.getAttribute("data-type");

            if (destinationInput && dest) {
                destinationInput.value = dest;
            }
            if (scheduledTypeSelect && type) {
                scheduledTypeSelect.value = type;
            }
            if (flightNotesInput && notes) {
                flightNotesInput.value = notes;
            }

            if (scheduledTimeInput && timeStr) {
                const parts = timeStr.split(":");
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                tomorrow.setHours(parseInt(parts[0], 10), parseInt(parts[1], 10), 0, 0);
                scheduledTimeInput.value = toDateTimeLocalString(tomorrow);
            }

            if (type === "airport") {
                const comfortRadio = document.querySelector('input[name="vehicle_type"][value="comfort"]');
                if (comfortRadio) {
                    comfortRadio.checked = true;
                    document.querySelectorAll(".vehicle-card").forEach(function(c) { c.classList.remove("active"); });
                    const comfortCard = comfortRadio.closest(".vehicle-card");
                    if (comfortCard) comfortCard.classList.add("active");
                }
            }

            if (destinationInput) {
                destinationInput.dispatchEvent(new Event("input"));
                destinationInput.dispatchEvent(new Event("change"));
            }
        });
    });

    if (bookingModeInput.value === "scheduled") {
        setBookingMode("scheduled");
    } else {
        updateDateBounds();
    }
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

    initScheduledShuttleSystem();

    // Ride form basic check
    const rideForm = document.getElementById("rideForm");
    if (rideForm) {
        rideForm.addEventListener("submit", function (e) {
            const p = document.getElementById("pickup").value.trim();
            const d = document.getElementById("destination").value.trim();
            if (p && d && p.toLowerCase() === d.toLowerCase()) {
                e.preventDefault();
                alert(_t("Pickup and destination cannot be the same."));
                return;
            }

            const bookingModeInput = document.getElementById("bookingModeInput");
            if (bookingModeInput && bookingModeInput.value === "scheduled") {
                const scheduledTimeInput = document.getElementById("scheduledTimeInput");
                if (!scheduledTimeInput || !scheduledTimeInput.value) {
                    e.preventDefault();
                    alert(_t("Veuillez sélectionner une date et heure de départ pour votre navette planifiée."));
                    if (scheduledTimeInput) scheduledTimeInput.focus();
                    return;
                }
                const chosen = new Date(scheduledTimeInput.value);
                const minAllowed = new Date(Date.now() + 14 * 60 * 1000);
                if (isNaN(chosen.getTime()) || chosen < minAllowed) {
                    e.preventDefault();
                    alert(_t("La réservation à l'avance doit être fixée au moins 15 minutes dans le futur."));
                    if (scheduledTimeInput) scheduledTimeInput.focus();
                    return;
                }
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
