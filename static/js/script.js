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
        if (window.refreshSplitMath) {
            window.refreshSplitMath(clamped);
        }
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

    initSplitFareEngine();
}

// ---------- Carpool Split-Fare Engine ("Partage de Frais entre Passagers") ----------
function initSplitFareEngine() {
    const splitSection = document.getElementById("splitFareSection");
    if (!splitSection) return;

    const toggle = document.getElementById("splitFareToggle");
    const body = document.getElementById("splitFareBody");
    const countInput = document.getElementById("splitCountInput");
    const countPills = document.querySelectorAll(".split-count-pill");
    const presetChips = document.querySelectorAll(".split-preset-chip");
    const paxRow3 = document.getElementById("paxRow3");
    const paxRow4 = document.getElementById("paxRow4");
    const totalDisplay = document.getElementById("splitTotalDisplay");
    const countDisplay = document.getElementById("splitCountDisplay");
    const perPersonDisplay = document.getElementById("splitPerPersonDisplay");
    const savingText = document.getElementById("splitSavingText");
    const sharePill1 = document.getElementById("sharePill1");
    const sharePill2 = document.getElementById("sharePill2");
    const sharePill3 = document.getElementById("sharePill3");
    const sharePill4 = document.getElementById("sharePill4");

    const copaxName2 = document.getElementById("copaxName2");
    const copaxName3 = document.getElementById("copaxName3");
    const copaxName4 = document.getElementById("copaxName4");
    const passengersInput = document.getElementById("passengers");

    let activeSplitFare = 0;

    function formatNumber(num) {
        return Math.round(Number(num) || 0).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    function setCount(count) {
        count = Math.max(2, Math.min(4, parseInt(count, 10) || 2));
        if (countInput) countInput.value = count;

        countPills.forEach(pill => {
            const c = parseInt(pill.getAttribute("data-count"), 10);
            if (c === count) pill.classList.add("active");
            else pill.classList.remove("active");
        });

        if (paxRow3) paxRow3.style.display = (count >= 3) ? "flex" : "none";
        if (paxRow4) paxRow4.style.display = (count >= 4) ? "flex" : "none";

        if (passengersInput && parseInt(passengersInput.value, 10) < count) {
            passengersInput.value = count;
        }

        refreshMath(activeSplitFare);
    }

    function refreshMath(fare) {
        if (fare !== undefined && fare !== null) activeSplitFare = fare;
        const total = Math.round(Number(activeSplitFare) || 0);
        const count = countInput ? parseInt(countInput.value, 10) || 2 : 2;

        if (total <= 0) {
            if (totalDisplay) totalDisplay.textContent = "-";
            if (countDisplay) countDisplay.textContent = count + " pers.";
            if (perPersonDisplay) perPersonDisplay.textContent = "- FCFA / personne";
            if (sharePill1) sharePill1.textContent = "- XAF";
            if (sharePill2) sharePill2.textContent = "- XAF";
            if (sharePill3) sharePill3.textContent = "- XAF";
            if (sharePill4) sharePill4.textContent = "- XAF";
            return;
        }

        const perPerson = Math.round(total / count);
        const p1Share = total - (perPerson * (count - 1));
        const savingPct = Math.round(((count - 1) / count) * 100);

        if (totalDisplay) totalDisplay.textContent = formatNumber(total) + " FCFA";
        if (countDisplay) countDisplay.textContent = count + " pers.";
        if (perPersonDisplay) perPersonDisplay.textContent = formatNumber(perPerson) + " FCFA / personne";
        if (savingText) {
            const tpl = _t("Chaque passager économise {pct}% sur ce trajet !");
            savingText.textContent = tpl.replace("{pct}", savingPct);
        }

        if (sharePill1) sharePill1.textContent = formatNumber(p1Share) + " XAF";
        if (sharePill2) sharePill2.textContent = formatNumber(perPerson) + " XAF";
        if (sharePill3) sharePill3.textContent = (count >= 3) ? formatNumber(perPerson) + " XAF" : "-";
        if (sharePill4) sharePill4.textContent = (count >= 4) ? formatNumber(perPerson) + " XAF" : "-";
    }

    window.refreshSplitMath = refreshMath;

    if (toggle && body) {
        toggle.addEventListener("change", function () {
            if (this.checked) {
                body.style.display = "block";
                // Enforce non-bendskin vehicle
                const bendskinRadio = document.querySelector('input[name="vehicle_type"][value="bendskin"]');
                if (bendskinRadio && bendskinRadio.checked) {
                    const taxiRadio = document.querySelector('input[name="vehicle_type"][value="taxi"]');
                    if (taxiRadio) {
                        taxiRadio.checked = true;
                        taxiRadio.dispatchEvent(new Event("change"));
                    }
                }
                const count = countInput ? parseInt(countInput.value, 10) || 2 : 2;
                if (passengersInput && parseInt(passengersInput.value, 10) < count) {
                    passengersInput.value = count;
                }
                refreshMath(activeSplitFare);
            } else {
                body.style.display = "none";
            }
        });
    }

    countPills.forEach(pill => {
        pill.addEventListener("click", function () {
            const count = parseInt(this.getAttribute("data-count"), 10);
            setCount(count);
        });
    });

    presetChips.forEach(chip => {
        chip.addEventListener("click", function () {
            const count = parseInt(this.getAttribute("data-count"), 10) || 2;
            const p2 = this.getAttribute("data-pax2") || "";
            const p3 = this.getAttribute("data-pax3") || "";
            const p4 = this.getAttribute("data-pax4") || "";

            setCount(count);

            if (copaxName2 && p2) copaxName2.value = p2;
            if (copaxName3 && p3) copaxName3.value = p3;
            if (copaxName4 && p4) copaxName4.value = p4;

            presetChips.forEach(c => c.classList.remove("active"));
            this.classList.add("active");
        });
    });

    // Initial check
    if (toggle && toggle.checked) {
        if (body) body.style.display = "block";
        const initialCount = countInput ? parseInt(countInput.value, 10) || 2 : 2;
        setCount(initialCount);
    }
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

// ============================================================
// Feature #5: 🎙️ Voice Search & Douala Landmark Recognition
// ============================================================
function initVoiceSearchAndLandmarks() {
    const pickupInput = document.getElementById("pickup");
    const destInput = document.getElementById("destination");
    const voiceBtnPickup = document.getElementById("voiceBtnPickup");
    const voiceBtnDest = document.getElementById("voiceBtnDestination");
    const pickupStatus = document.getElementById("pickupVoiceStatus");
    const destStatus = document.getElementById("destVoiceStatus");
    const pickupBadge = document.getElementById("pickupLandmarkBadge");
    const destBadge = document.getElementById("destLandmarkBadge");
    const pickupSuggestions = document.getElementById("pickupSuggestions");
    const destSuggestions = document.getElementById("destSuggestions");
    const slangChips = document.querySelectorAll(".slang-chip");

    if (!pickupInput && !destInput) return;

    let activeRecognition = null;
    let activeTargetField = null;

    // Check Speech Recognition support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    function getSpeechLang() {
        const lang = (window.MboaLiftI18n && window.MboaLiftI18n.getCurrentLanguage)
            ? window.MboaLiftI18n.getCurrentLanguage()
            : 'fr';
        return lang === 'en' ? 'en-US' : 'fr-FR';
    }

    function setStatus(targetField, text, isListening, isError) {
        const statusEl = (targetField === 'pickup') ? pickupStatus : destStatus;
        if (!statusEl) return;
        const textSpan = statusEl.querySelector('.voice-status-text');
        if (textSpan) textSpan.textContent = text;
        if (isListening) {
            statusEl.classList.add('listening');
            statusEl.classList.remove('error');
        } else if (isError) {
            statusEl.classList.remove('listening');
            statusEl.classList.add('error');
        } else {
            statusEl.classList.remove('listening', 'error');
        }
    }

    function setBadge(targetField, landmarkName, canonicalArea, icon) {
        const badgeEl = (targetField === 'pickup') ? pickupBadge : destBadge;
        if (!badgeEl) return;
        if (!landmarkName) {
            badgeEl.style.display = 'none';
            badgeEl.innerHTML = '';
            return;
        }

        const iconStr = icon || '📍';
        badgeEl.style.display = 'flex';
        badgeEl.innerHTML = `
            <span class="badge-icon">${iconStr}</span>
            <div class="badge-text-group">
                <span class="badge-sub">${_t("Repère identifié :")}</span>
                <strong class="badge-title">${landmarkName}</strong>
            </div>
            <span class="badge-arrow">➔</span>
            <span class="badge-canonical">${canonicalArea}</span>
        `;
    }

    function processVoiceResult(targetField, transcript) {
        if (!transcript) return;
        const inputEl = (targetField === 'pickup') ? pickupInput : destInput;
        if (!inputEl) return;

        // Strip conversational prefixes: "dépose-moi à", "je vais à", etc.
        const cleaned = transcript.replace(/^(dépose[- ]moi\s+(à|au|vers|a)?|je\s+vais\s+(à|au|vers|a)?|amène[- ]moi\s+(à|au|vers|a)?|direction\s+|au\s+niveau\s+de\s+|à\s+la\s+|à\s+|au\s+|a\s+la\s+|a\s+)/gi, '').trim();

        // Call backend landmark matching API
        fetch('/api/landmarks/search?q=' + encodeURIComponent(cleaned || transcript))
            .then(res => res.json())
            .then(data => {
                let targetArea = data.matched_area;
                let landmarkObj = (data.landmarks && data.landmarks.length > 0) ? data.landmarks[0] : null;

                if (!targetArea && landmarkObj) {
                    targetArea = landmarkObj.area;
                }

                if (targetArea) {
                    inputEl.value = targetArea;
                    const matchedName = landmarkObj ? landmarkObj.name : targetArea;
                    const icon = landmarkObj ? landmarkObj.icon : '✨';
                    setBadge(targetField, matchedName, targetArea, icon);
                    if (window.focusDoualaLandmark) {
                        window.focusDoualaLandmark(landmarkObj || targetArea, targetField);
                    }
                } else {
                    inputEl.value = cleaned || transcript;
                    setBadge(targetField, cleaned || transcript, cleaned || transcript, '🎙️');
                }

                inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                inputEl.dispatchEvent(new Event('change', { bubbles: true }));
                setStatus(targetField, _t("Reconnu : ") + (targetArea || cleaned || transcript), false, false);
            })
            .catch(() => {
                inputEl.value = cleaned || transcript;
                inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                inputEl.dispatchEvent(new Event('change', { bubbles: true }));
            });
    }

    function startVoiceRecognition(targetField) {
        const btn = (targetField === 'pickup') ? voiceBtnPickup : voiceBtnDest;
        const inputEl = (targetField === 'pickup') ? pickupInput : destInput;

        if (!SpeechRecognition) {
            setStatus(targetField, _t("Micro non supporté - Utilisez les repères express"), false, true);
            if (inputEl) inputEl.focus();
            showLandmarkSuggestions(targetField, '');
            return;
        }

        if (activeRecognition) {
            try { activeRecognition.stop(); } catch (e) {}
            activeRecognition = null;
        }

        try {
            const recognition = new SpeechRecognition();
            recognition.lang = getSpeechLang();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.onstart = function () {
                activeRecognition = recognition;
                activeTargetField = targetField;
                if (btn) btn.classList.add('listening');
                setStatus(targetField, _t("Écoute en cours... Parlez (ex: Total Ndokoti)"), true, false);
            };

            recognition.onresult = function (event) {
                if (event.results && event.results[0] && event.results[0][0]) {
                    const transcript = event.results[0][0].transcript;
                    processVoiceResult(targetField, transcript);
                }
            };

            recognition.onerror = function (event) {
                console.warn('Speech recognition error:', event.error);
                if (btn) btn.classList.remove('listening');
                if (event.error === 'not-allowed') {
                    setStatus(targetField, _t("Micro bloqué. Autorisez l'accès micro."), false, true);
                } else if (event.error === 'no-speech') {
                    setStatus(targetField, _t("Aucune voix détectée. Réessayez."), false, true);
                } else {
                    setStatus(targetField, _t("Erreur de détection vocale."), false, true);
                }
                activeRecognition = null;
            };

            recognition.onend = function () {
                if (btn) btn.classList.remove('listening');
                activeRecognition = null;
                setTimeout(() => {
                    setStatus(targetField, _t("Micro prêt"), false, false);
                }, 3500);
            };

            recognition.start();
        } catch (err) {
            console.warn('SpeechRecognition start failed:', err);
            if (btn) btn.classList.remove('listening');
            setStatus(targetField, _t("Erreur micro. Utilisez les repères express."), false, true);
        }
    }

    if (voiceBtnPickup) {
        voiceBtnPickup.addEventListener('click', function (e) {
            e.preventDefault();
            startVoiceRecognition('pickup');
        });
    }

    if (voiceBtnDest) {
        voiceBtnDest.addEventListener('click', function (e) {
            e.preventDefault();
            startVoiceRecognition('destination');
        });
    }

    // Auto-suggest landmarks as user types
    function showLandmarkSuggestions(targetField, query) {
        const container = (targetField === 'pickup') ? pickupSuggestions : destSuggestions;
        if (!container) return;

        fetch('/api/landmarks/search?q=' + encodeURIComponent(query || ''))
            .then(res => res.json())
            .then(data => {
                const list = (data.landmarks || []).slice(0, 6);
                if (list.length === 0) {
                    container.style.display = 'none';
                    container.innerHTML = '';
                    return;
                }

                container.innerHTML = `
                    <div class="landmark-suggestions-header">
                        <span>📍 ${_t("Repères Douala recommandés :")}</span>
                        <button type="button" class="btn-close-suggestions" title="Fermer">✕</button>
                    </div>
                    <div class="landmark-suggestions-list">
                        ${list.map(lm => `
                            <div class="landmark-suggestion-item" data-landmark="${lm.name}" data-area="${lm.area}" data-lat="${lm.lat}" data-lng="${lm.lng}">
                                <span class="suggestion-icon">${lm.icon}</span>
                                <div class="suggestion-info">
                                    <strong class="suggestion-name">${lm.name}</strong>
                                    <span class="suggestion-tip">${lm.tip}</span>
                                </div>
                                <span class="suggestion-area-badge">${lm.area}</span>
                            </div>
                        `).join('')}
                    </div>
                `;
                container.style.display = 'block';

                container.querySelectorAll('.landmark-suggestion-item').forEach(item => {
                    item.addEventListener('click', function () {
                        const lmName = this.getAttribute('data-landmark');
                        const lmArea = this.getAttribute('data-area');
                        const lat = parseFloat(this.getAttribute('data-lat'));
                        const lng = parseFloat(this.getAttribute('data-lng'));
                        const icon = this.querySelector('.suggestion-icon').textContent;

                        const inputEl = (targetField === 'pickup') ? pickupInput : destInput;
                        if (inputEl) {
                            inputEl.value = lmArea;
                            inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                            inputEl.dispatchEvent(new Event('change', { bubbles: true }));
                        }

                        setBadge(targetField, lmName, lmArea, icon);
                        if (window.focusDoualaLandmark) {
                            window.focusDoualaLandmark({ name: lmName, area: lmArea, lat: lat, lng: lng, icon: icon }, targetField);
                        }
                        container.style.display = 'none';
                    });
                });

                const closeBtn = container.querySelector('.btn-close-suggestions');
                if (closeBtn) {
                    closeBtn.addEventListener('click', function () {
                        container.style.display = 'none';
                    });
                }
            })
            .catch(() => {
                container.style.display = 'none';
            });
    }

    let searchDebouncePickup = null;
    let searchDebounceDest = null;

    if (pickupInput) {
        pickupInput.addEventListener('input', function () {
            const val = this.value.trim();
            if (searchDebouncePickup) clearTimeout(searchDebouncePickup);
            searchDebouncePickup = setTimeout(() => {
                if (val.length >= 2) {
                    showLandmarkSuggestions('pickup', val);
                } else if (pickupSuggestions) {
                    pickupSuggestions.style.display = 'none';
                }
            }, 180);
        });
    }

    if (destInput) {
        destInput.addEventListener('input', function () {
            const val = this.value.trim();
            if (searchDebounceDest) clearTimeout(searchDebounceDest);
            searchDebounceDest = setTimeout(() => {
                if (val.length >= 2) {
                    showLandmarkSuggestions('destination', val);
                } else if (destSuggestions) {
                    destSuggestions.style.display = 'none';
                }
            }, 180);
        });
    }

    // Hide suggestions on click outside
    document.addEventListener('click', function (e) {
        if (pickupSuggestions && !pickupSuggestions.contains(e.target) && e.target !== pickupInput && e.target !== voiceBtnPickup) {
            pickupSuggestions.style.display = 'none';
        }
        if (destSuggestions && !destSuggestions.contains(e.target) && e.target !== destInput && e.target !== voiceBtnDest) {
            destSuggestions.style.display = 'none';
        }
    });

    // Wire up Slang Bar quick chips
    slangChips.forEach(chip => {
        chip.addEventListener('click', function () {
            const landmark = this.getAttribute('data-landmark');
            const area = this.getAttribute('data-area');
            const lat = parseFloat(this.getAttribute('data-lat'));
            const lng = parseFloat(this.getAttribute('data-lng'));
            const icon = this.querySelector('.chip-icon') ? this.querySelector('.chip-icon').textContent : '📍';

            let targetField = 'destination';
            if (!pickupInput.value.trim()) {
                targetField = 'pickup';
            }

            const inputEl = (targetField === 'pickup') ? pickupInput : destInput;
            if (inputEl) {
                inputEl.value = area;
                inputEl.dispatchEvent(new Event('input', { bubbles: true }));
                inputEl.dispatchEvent(new Event('change', { bubbles: true }));
            }

            setBadge(targetField, landmark, area, icon);

            if (window.focusDoualaLandmark) {
                window.focusDoualaLandmark({ name: landmark, area: area, lat: lat, lng: lng, icon: icon }, targetField);
            }
        });
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

    initScheduledShuttleSystem();
    initVoiceSearchAndLandmarks();

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
