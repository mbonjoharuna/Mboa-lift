/**
 * douala_weather_sos.js
 * ---------------------
 * Client-side engine for:
 * 1. Douala Rain & Traffic Alert Engine ("Météo Pluie & Inondations")
 * 2. Emergency SOS Safety Center ("Bouton Sécurité Urgence")
 * 3. Offline USSD Fast-Ride Booking ("Réservation sans connexion internet")
 *
 * Fully bilingual (EN / FR), left-aligned, self-contained.
 */

(function () {
  'use strict';

  // State
  let activeWeather = null;
  let activeGpsCoords = null;
  let strobeInterval = null;
  let audioCtx = null;

  function _t(key) {
    return (window.MboaLiftI18n && window.MboaLiftI18n.t) ? window.MboaLiftI18n.t(key) : key;
  }

  // ============================================================
  // 1. WEATHER & TRAFFIC ALERT ENGINE
  // ============================================================
  function initWeatherEngine() {
    // Condition switcher buttons (homepage / request ride)
    const switchBtns = document.querySelectorAll('.weather-switch-btn');
    switchBtns.forEach(btn => {
      btn.addEventListener('click', function () {
        const condId = this.getAttribute('data-condition');
        if (!condId) return;
        setWeatherCondition(condId);
      });
    });

    // Initial weather state fetch or read from dataset
    const weatherCard = document.querySelector('.douala-weather-alert-card');
    if (weatherCard) {
      const initialId = weatherCard.getAttribute('data-weather-id');
      if (initialId) {
        checkRouteHazards();
      }
    }

    // Monitor pickup & destination on request_ride.html
    const pickupInput = document.getElementById('pickup');
    const destInput = document.getElementById('destination');
    if (pickupInput && destInput) {
      pickupInput.addEventListener('input', checkRouteHazards);
      pickupInput.addEventListener('change', checkRouteHazards);
      destInput.addEventListener('input', checkRouteHazards);
      destInput.addEventListener('change', checkRouteHazards);
    }
  }

  function setWeatherCondition(conditionId) {
    fetch('/api/weather-traffic?condition=' + encodeURIComponent(conditionId))
      .then(res => res.json())
      .then(data => {
        if (!data || !data.active) return;
        activeWeather = data.active;
        applyWeatherToDom(data.active, data.all_conditions);
        checkRouteHazards();
      })
      .catch(() => {});
  }

  function applyWeatherToDom(weather, allConditions) {
    const cards = document.querySelectorAll('.douala-weather-alert-card');
    cards.forEach(card => {
      card.setAttribute('data-weather-id', weather.id);
      card.className = 'douala-weather-alert-card level-' + weather.level;
      
      const iconEl = card.querySelector('.weather-alert-icon');
      if (iconEl) iconEl.textContent = weather.icon;

      const titleEl = card.querySelector('.weather-alert-title');
      if (titleEl) titleEl.textContent = _t(weather.title);

      const badgeEl = card.querySelector('.weather-badge');
      if (badgeEl) badgeEl.textContent = _t(weather.badge);

      const msgEl = card.querySelector('.weather-advisory-text');
      if (msgEl) msgEl.textContent = _t(weather.message);

      const recEl = card.querySelector('.weather-recommendation-pill');
      if (recEl) recEl.textContent = '🛡️ ' + _t('Recommandation : ') + _t(weather.recommended_label);

      // Affected zones
      const zonesContainer = card.querySelector('.weather-affected-zones');
      if (zonesContainer) {
        zonesContainer.innerHTML = '';
        if (weather.affected_zones && weather.affected_zones.length > 0) {
          weather.affected_zones.forEach(zone => {
            const span = document.createElement('span');
            span.className = 'zone-hazard-tag';
            span.innerHTML = '⚠️ ' + zone;
            zonesContainer.appendChild(span);
          });
        }
      }
    });

    // Update active pill in switcher
    const switchBtns = document.querySelectorAll('.weather-switch-btn');
    switchBtns.forEach(btn => {
      if (btn.getAttribute('data-condition') === weather.id) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update vehicle card recommendation highlights on request_ride.html
    updateVehicleRecommendations(weather);
  }

  function updateVehicleRecommendations(weather) {
    const cards = document.querySelectorAll('.vehicle-card');
    cards.forEach(card => {
      card.classList.remove('rain-recommended');
      const oldBadge = card.querySelector('.vehicle-rain-badge');
      if (oldBadge) oldBadge.remove();

      const radio = card.querySelector('input[type="radio"]');
      if (radio && radio.value === weather.recommended_vehicle) {
        card.classList.add('rain-recommended');
        const badge = document.createElement('span');
        badge.className = 'vehicle-rain-badge';
        badge.textContent = weather.id === 'wouri_jam' ? '⚡ ' + _t('Anti-Bouchon') : '🛡️ ' + _t('Abrité Météo');
        card.appendChild(badge);
      }
    });
  }

  function checkRouteHazards() {
    const pickupInput = document.getElementById('pickup');
    const destInput = document.getElementById('destination');
    const hazardCallout = document.getElementById('routeHazardCallout');
    if (!pickupInput || !destInput || !hazardCallout) return;

    const p = (pickupInput.value || '').trim();
    const d = (destInput.value || '').trim();
    if (!p && !d) {
      hazardCallout.style.display = 'none';
      return;
    }

    const card = document.querySelector('.douala-weather-alert-card');
    const weatherId = card ? card.getAttribute('data-weather-id') : 'torrential_rain';

    let affectedList = [];
    if (weatherId === 'torrential_rain') {
      affectedList = ['Makepe', 'Bépanda', 'Bonabéri', 'Ndokoti'];
    } else if (weatherId === 'wouri_jam') {
      affectedList = ['Bonabéri', 'Deido', 'Akwa'];
    } else if (weatherId === 'moderate_rain') {
      affectedList = ['Akwa', 'Bonanjo', 'Ndokoti'];
    }

    const matchP = affectedList.find(zone => p.toLowerCase().includes(zone.toLowerCase()));
    const matchD = affectedList.find(zone => d.toLowerCase().includes(zone.toLowerCase()));

    // Check Wouri crossing specifically
    const isWouriCrossing = (p.toLowerCase().includes('bonabéri') || p.toLowerCase().includes('bonaberi')) !==
                            (d.toLowerCase().includes('bonabéri') || d.toLowerCase().includes('bonaberi'));

    if (weatherId === 'torrential_rain' && (matchP || matchD)) {
      const hitZone = matchP || matchD;
      hazardCallout.style.display = 'flex';
      hazardCallout.innerHTML =
        '<span class="route-hazard-icon">🌊⚠️</span>' +
        '<div><strong>' + _t('Alerte Inondation Immédiate : ') + hitZone + '</strong><br>' +
        _t('Zone à fort risque d\'accumulation d\'eau et chaussée submergée. Privilégiez une Voiture Confort haute ou évitez les bas-côtés en moto.') +
        '</div>';
    } else if (weatherId === 'wouri_jam' && isWouriCrossing) {
      hazardCallout.style.display = 'flex';
      hazardCallout.innerHTML =
        '<span class="route-hazard-icon">🌉⚠️</span>' +
        '<div><strong>' + _t('Traversée du Pont du Wouri saturée !') + '</strong><br>' +
        _t('Forts ralentissements entre Bonabéri et la rive gauche. Prévoyez +45 min ou optez pour un Bendskin moto 🏍️ pour vous faufiler.') +
        '</div>';
    } else {
      hazardCallout.style.display = 'none';
    }
  }

  // ============================================================
  // 2. EMERGENCY SOS SAFETY CENTER ("Bouton Sécurité Urgence")
  // ============================================================
  function initSosCenter() {
    const triggers = [
      document.getElementById('headerSosBtn'),
      document.getElementById('floatingSosBtn'),
      document.getElementById('activeRideSosBtn')
    ].filter(Boolean);

    const modal = document.getElementById('mboaSosModal');
    const closeBtn = document.getElementById('mboaSosClose');

    triggers.forEach(trigger => {
      trigger.addEventListener('click', openSosModal);
    });

    if (closeBtn && modal) {
      closeBtn.addEventListener('click', closeSosModal);
    }

    if (modal) {
      modal.addEventListener('click', function (e) {
        if (e.target === modal) closeSosModal();
      });
    }

    // Copy distress message button
    const copyBtn = document.getElementById('sosCopyBtn');
    if (copyBtn) {
      copyBtn.addEventListener('click', copyDistressMessage);
    }

    // Strobe flasher toggle
    const strobeBtn = document.getElementById('sosStrobeBtn');
    const strobeOverlay = document.getElementById('sosStrobeOverlay');
    if (strobeBtn && strobeOverlay) {
      strobeBtn.addEventListener('click', function () {
        closeSosModal();
        startStrobeBeacon();
      });
      strobeOverlay.addEventListener('click', stopStrobeBeacon);
    }
  }

  function openSosModal() {
    const modal = document.getElementById('mboaSosModal');
    if (!modal) return;
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');

    // Trigger geolocation acquisition
    acquireGeolocation();
  }

  function closeSosModal() {
    const modal = document.getElementById('mboaSosModal');
    if (!modal) return;
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
  }

  function acquireGeolocation() {
    const locDisplay = document.getElementById('sosLocationCoords');
    const textPreview = document.getElementById('sosTextPreview');
    const waLink = document.getElementById('sosWaLink');
    const smsLink = document.getElementById('sosSmsLink');

    // Default fallback text
    let contextArea = 'Douala, Cameroun';
    const pickupInput = document.getElementById('pickup');
    if (pickupInput && pickupInput.value) {
      contextArea = pickupInput.value.trim() + ', Douala';
    }

    // Check active ride on dashboard
    let rideContext = '';
    const activeTracker = document.querySelector('.live-tracker-card');
    if (activeTracker) {
      const rideId = activeTracker.getAttribute('data-active-ride-id');
      const startPt = activeTracker.querySelector('.route-point.start');
      const endPt = activeTracker.querySelector('.route-point.end');
      const dName = activeTracker.querySelector('.driver-name-text');
      if (rideId) rideContext += ' [Course #' + rideId + ']';
      if (startPt && endPt) rideContext += ' ' + startPt.textContent.trim() + ' ➔ ' + endPt.textContent.trim();
      if (dName && dName.textContent.trim()) rideContext += ' (Chauffeur: ' + dName.textContent.trim() + ')';
    }

    let defaultMsg = '🚨 ALERTE URGENCE MboaLift Douala ! J\'ai besoin d\'une assistance immédiate.' +
      (rideContext ? ' En course :' + rideContext + '.' : '') +
      ' Position : ' + contextArea + '. Merci d\'intervenir en urgence !';

    if (textPreview) textPreview.textContent = defaultMsg;
    if (waLink) waLink.href = 'https://wa.me/?text=' + encodeURIComponent(defaultMsg);
    if (smsLink) smsLink.href = 'sms:117?body=' + encodeURIComponent(defaultMsg);

    if ('geolocation' in navigator) {
      if (locDisplay) locDisplay.textContent = '📍 ' + _t('Recherche des coordonnées GPS Douala en direct...');
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          const lat = pos.coords.latitude.toFixed(5);
          const lng = pos.coords.longitude.toFixed(5);
          activeGpsCoords = { lat: lat, lng: lng };
          const mapsUrl = 'https://maps.google.com/?q=' + lat + ',' + lng;

          if (locDisplay) {
            locDisplay.innerHTML = '📍 <strong>GPS : ' + lat + ', ' + lng + '</strong> <span style="color:#059669;">(Précision ~' + Math.round(pos.coords.accuracy) + 'm)</span>';
          }

          const distressMsg = '🚨 URGENCE MBOALIFT DOUALA ! Besoin d\'aide immédiate.' +
            (rideContext ? ' En course :' + rideContext + '.' : '') +
            ' Coordonnées GPS : ' + lat + ',' + lng + ' (' + mapsUrl + '). Merci d\'intervenir immédiatement !';
          if (textPreview) textPreview.textContent = distressMsg;
          if (waLink) waLink.href = 'https://wa.me/?text=' + encodeURIComponent(distressMsg);
          if (smsLink) smsLink.href = 'sms:117?body=' + encodeURIComponent(distressMsg);
        },
        function () {
          if (locDisplay) {
            locDisplay.innerHTML = '📍 <em>' + _t('Position approximative : Douala Urbain (GPS désactivé ou indisponible).') + '</em>';
          }
        },
        { enableHighAccuracy: true, timeout: 6000, maximumAge: 60000 }
      );
    }
  }

  function copyDistressMessage() {
    const textPreview = document.getElementById('sosTextPreview');
    const copyBtn = document.getElementById('sosCopyBtn');
    if (!textPreview) return;

    navigator.clipboard.writeText(textPreview.textContent)
      .then(() => {
        if (copyBtn) {
          const orig = copyBtn.textContent;
          copyBtn.textContent = '✓ ' + _t('Copié !');
          setTimeout(() => { copyBtn.textContent = orig; }, 2000);
        }
      })
      .catch(() => {
        alert(_t('Message d\'urgence copié dans le presse-papier.'));
      });
  }

  function startStrobeBeacon() {
    const strobe = document.getElementById('sosStrobeOverlay');
    if (!strobe) return;
    strobe.classList.add('active');

    // Beep sound with Web Audio API for nighttime distress
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      playSosBeep();
      strobeInterval = setInterval(playSosBeep, 1200);
    } catch (e) {}
  }

  function playSosBeep() {
    if (!audioCtx) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(880, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.3);
    } catch (e) {}
  }

  function stopStrobeBeacon() {
    const strobe = document.getElementById('sosStrobeOverlay');
    if (strobe) strobe.classList.remove('active');
    if (strobeInterval) {
      clearInterval(strobeInterval);
      strobeInterval = null;
    }
  }

  // ============================================================
  // 3. OFFLINE USSD FAST-RIDE BOOKING ("Réservation sans internet")
  // ============================================================
  const LOCATION_CODES = {
    "Akwa": 1, "Bonanjo": 2, "Bonamoussadi": 3, "Deido": 4, "Bépanda": 5,
    "Makepe": 6, "Bonapriso": 7, "Bali": 8, "New Bell": 9, "Ndokoti": 10,
    "Logbessou": 11, "Bonabéri": 12, "Aéroport": 13, "Japoma": 14, "Cité des Palmiers": 15
  };

  const VEHICLE_CODES = {
    "bendskin": 1,
    "taxi": 2,
    "comfort": 3
  };

  function initUssdBooking() {
    const openBtns = document.querySelectorAll('.btn-open-ussd, #headerUssdBtn');
    const modal = document.getElementById('ussdBookingModal');
    const closeBtn = document.getElementById('ussdModalClose');

    openBtns.forEach(btn => {
      btn.addEventListener('click', openUssdModal);
    });

    if (closeBtn && modal) {
      closeBtn.addEventListener('click', closeUssdModal);
    }

    if (modal) {
      modal.addEventListener('click', function (e) {
        if (e.target === modal) closeUssdModal();
      });
    }

    // USSD Form changes
    const pSel = document.getElementById('ussdPickup');
    const dSel = document.getElementById('ussdDestination');
    const vSel = document.getElementById('ussdVehicle');

    if (pSel && dSel && vSel) {
      pSel.addEventListener('change', updateUssdString);
      dSel.addEventListener('change', updateUssdString);
      vSel.addEventListener('change', updateUssdString);
    }

    // USSD Simulation Button
    const simBtn = document.getElementById('ussdSimulateBtn');
    if (simBtn) {
      simBtn.addEventListener('click', runUssdSimulation);
    }

    // Initial USSD string render
    updateUssdString();
  }

  function openUssdModal() {
    const modal = document.getElementById('ussdBookingModal');
    if (!modal) return;
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');

    // Sync selected pickup from main form if available
    const mainPickup = document.getElementById('pickup');
    const mainDest = document.getElementById('destination');
    const pSel = document.getElementById('ussdPickup');
    const dSel = document.getElementById('ussdDestination');

    if (mainPickup && mainPickup.value && pSel) {
      pSel.value = mainPickup.value;
    }
    if (mainDest && mainDest.value && dSel) {
      dSel.value = mainDest.value;
    }

    updateUssdString();
  }

  function closeUssdModal() {
    const modal = document.getElementById('ussdBookingModal');
    if (!modal) return;
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
  }

  function updateUssdString() {
    const pSel = document.getElementById('ussdPickup');
    const dSel = document.getElementById('ussdDestination');
    const vSel = document.getElementById('ussdVehicle');
    const codeDisplay = document.getElementById('ussdCodeDisplay');
    const dialBtn = document.getElementById('ussdDialBtn');
    const smsBtn = document.getElementById('ussdSmsBtn');
    const smsFormat = document.getElementById('ussdSmsFormat');

    const pickup = pSel ? pSel.value : 'Akwa';
    const destination = dSel ? dSel.value : 'Bonanjo';
    const vehicle = vSel ? vSel.value : 'taxi';

    const pCode = LOCATION_CODES[pickup] || 1;
    const dCode = LOCATION_CODES[destination] || 2;
    const vCode = VEHICLE_CODES[vehicle] || 2;

    const ussdString = '*999*' + pCode + '*' + dCode + '*' + vCode + '#';
    const smsText = 'MBOA ' + pickup.toUpperCase() + ' ' + destination.toUpperCase() + ' ' + vehicle.toUpperCase();

    if (codeDisplay) {
      codeDisplay.textContent = ussdString;
    }

    if (dialBtn) {
      dialBtn.href = 'tel:%2A999%2A' + pCode + '%2A' + dCode + '%2A' + vCode + '%23';
    }

    if (smsBtn) {
      smsBtn.href = 'sms:8800?body=' + encodeURIComponent(smsText);
    }

    if (smsFormat) {
      smsFormat.innerHTML = _t('Ou envoyez par SMS au ') + '<strong>8800</strong> : <code>' + smsText + '</code>';
    }
  }

  function runUssdSimulation() {
    const pSel = document.getElementById('ussdPickup');
    const dSel = document.getElementById('ussdDestination');
    const vSel = document.getElementById('ussdVehicle');
    const nokiaScreen = document.getElementById('nokiaUssdScreen');
    const simBtn = document.getElementById('ussdSimulateBtn');

    const pickup = pSel ? pSel.value : 'Akwa';
    const destination = dSel ? dSel.value : 'Bonanjo';
    const vehicle = vSel ? vSel.value : 'taxi';

    if (simBtn) simBtn.textContent = '⏳ ' + _t('Connexion réseau GSM 2G...');

    fetch('/api/ussd-simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pickup: pickup,
        destination: destination,
        vehicle_type: vehicle
      })
    })
      .then(res => res.json())
      .then(data => {
        if (simBtn) simBtn.textContent = '📱 ' + _t('Simuler l\'écran USSD (Téléphone 2G)');
        if (nokiaScreen && data.screen_text) {
          nokiaScreen.textContent = data.screen_text;
          nokiaScreen.classList.add('active');
        }
      })
      .catch(() => {
        if (simBtn) simBtn.textContent = '📱 ' + _t('Simuler l\'écran USSD (Téléphone 2G)');
        if (nokiaScreen) {
          nokiaScreen.textContent =
            '==============================\n' +
            '  MBOALIFT USSD SERVICE 237   \n' +
            '==============================\n' +
            '✓ Course validée sans internet\n' +
            '• ' + pickup + ' -> ' + destination + '\n' +
            '• Mode : ' + vehicle + '\n' +
            'Chauffeur en route. Payez cash.';
          nokiaScreen.classList.add('active');
        }
      });
  }

  // ============================================================
  // GLOBAL INITIALIZATION
  // ============================================================
  function init() {
    initWeatherEngine();
    initSosCenter();
    initUssdBooking();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose API
  window.DoualaWeatherSos = {
    setWeatherCondition: setWeatherCondition,
    openSosModal: openSosModal,
    closeSosModal: closeSosModal,
    openUssdModal: openUssdModal,
    closeUssdModal: closeUssdModal
  };
})();
