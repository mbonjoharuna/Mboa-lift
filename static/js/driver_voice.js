/**
 * driver_voice.js
 * ---------------
 * Driver Voice Announcement Engine for MboaLift Douala.
 * 
 * Uses the Web Speech API (speechSynthesis) to vocally announce new ride requests
 * to bendskin (moto-taxi) riders and cab drivers so they don't have to look at
 * their phone screens while navigating Douala traffic.
 * 
 * Announcement Format (requested):
 * - FR: "Nouvelle course disponible à [Pickup] pour [Fare] FCFA"
 * - EN: "New ride available at [Pickup] for [Fare] FCFA"
 */

(function () {
  'use strict';

  // State
  let isVoiceEnabled = true;
  let isPolling = false;
  let pollingInterval = null;
  const knownRideIds = new Set();
  let isInitialPoll = true;
  let audioContext = null;

  // Configuration
  const POLL_INTERVAL_MS = 6000; // 6 seconds

  // Initialize preference from localStorage
  const savedPref = localStorage.getItem('mboalift_driver_voice_enabled');
  if (savedPref !== null) {
    isVoiceEnabled = savedPref === 'true';
  } else {
    // Default enabled for drivers
    isVoiceEnabled = true;
  }

  // Get current UI language ('fr' or 'en')
  function getCurrentLang() {
    if (window.MboaLiftI18n && typeof window.MboaLiftI18n.getCurrentLanguage === 'function') {
      return window.MboaLiftI18n.getCurrentLanguage() || 'fr';
    }
    const htmlLang = document.documentElement.lang || '';
    if (htmlLang.toLowerCase().startsWith('en')) return 'en';
    return 'fr';
  }

  // Format currency with spaces (e.g. 1 500)
  function formatFare(amount) {
    const val = Math.round(Number(amount) || 0);
    return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }

  // Web Audio Walkie-Talkie / Taxi Radio Chime
  function playRadioChime() {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      if (!audioContext) {
        audioContext = new AudioCtx();
      }
      if (audioContext.state === 'suspended') {
        audioContext.resume();
      }

      const now = audioContext.currentTime;

      // Two-tone dispatch alert (660Hz -> 880Hz)
      const osc = audioContext.createOscillator();
      const gain = audioContext.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(659.25, now); // E5
      osc.frequency.setValueAtTime(880.00, now + 0.12); // A5

      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

      osc.connect(gain);
      gain.connect(audioContext.destination);

      osc.start(now);
      osc.stop(now + 0.35);
    } catch (e) {
      // Audio context might be restricted before user interaction
    }
  }

  // Speak announcement using Web Speech API
  function speakAnnouncement(text, lang) {
    if (!('speechSynthesis' in window)) {
      console.warn('[MboaLift Voice] speechSynthesis not supported in this browser.');
      playRadioChime();
      return;
    }

    try {
      // Cancel previous pending utterances
      window.speechSynthesis.cancel();

      // Play alerting chime first
      playRadioChime();

      setTimeout(() => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === 'fr' ? 'fr-FR' : 'en-US';
        utterance.rate = 1.02; // Clear and brisk for street noise
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Try to select an authentic native voice for the language
        const voices = window.speechSynthesis.getVoices();
        if (voices && voices.length > 0) {
          const targetPrefix = lang === 'fr' ? 'fr' : 'en';
          const match = voices.find(v => v.lang && v.lang.toLowerCase().startsWith(targetPrefix));
          if (match) {
            utterance.voice = match;
          }
        }

        window.speechSynthesis.speak(utterance);
      }, 300);
    } catch (err) {
      console.warn('[MboaLift Voice] Speak error:', err);
    }
  }

  // Announce a specific new ride
  function announceNewRide(ride) {
    if (!ride) return;

    const lang = getCurrentLang();
    const fareFormatted = formatFare(ride.fare);
    const pickup = ride.pickup || 'Douala';
    const isNegotiated = Boolean(ride.is_negotiated || ride.negotiation_status === 'PROPOSED');

    let cargoSuffix = '';
    if (ride.cargo_type === 'market') {
      cargoSuffix = (lang === 'fr') ? ' avec colis de marché' : ' with market goods';
    } else if (ride.cargo_type === 'heavy') {
      cargoSuffix = (lang === 'fr') ? ' avec coffre plein' : ' with full luggage';
    }

    const isScheduled = Boolean(ride.is_scheduled);
    const scheduledTime = ride.scheduled_time || '';
    const scheduledType = ride.scheduled_type || 'standard';

    let speechText = '';
    if (isScheduled) {
      const timePhrase = scheduledTime ? (lang === 'fr' ? `pour le ${scheduledTime}` : `for ${scheduledTime}`) : '';
      if (scheduledType === 'airport') {
        speechText = (lang === 'fr')
          ? `Nouvelle navette aéroport planifiée ${timePhrase} pour ${fareFormatted} FCFA${cargoSuffix}`
          : `New airport shuttle scheduled ${timePhrase} for ${fareFormatted} FCFA${cargoSuffix}`;
      } else if (scheduledType === 'port') {
        speechText = (lang === 'fr')
          ? `Nouvelle navette port planifiée ${timePhrase} pour ${fareFormatted} FCFA${cargoSuffix}`
          : `New port shuttle scheduled ${timePhrase} for ${fareFormatted} FCFA${cargoSuffix}`;
      } else {
        speechText = (lang === 'fr')
          ? `Nouvelle course planifiée ${timePhrase} pour ${fareFormatted} FCFA${cargoSuffix}`
          : `New ride scheduled ${timePhrase} for ${fareFormatted} FCFA${cargoSuffix}`;
      }
    } else if (isNegotiated) {
      if (lang === 'fr') {
        speechText = `Offre négociée reçue à ${fareFormatted} FCFA${cargoSuffix}`;
      } else {
        speechText = `Negotiated offer received at ${fareFormatted} FCFA${cargoSuffix}`;
      }
    } else {
      if (lang === 'fr') {
        speechText = `Nouvelle course disponible à ${pickup} pour ${fareFormatted} FCFA${cargoSuffix}`;
      } else {
        speechText = `New ride available at ${pickup} for ${fareFormatted} FCFA${cargoSuffix}`;
      }
    }

    // Trigger audible speech
    if (isVoiceEnabled) {
      speakAnnouncement(speechText, lang);
    }

    // Display visual toast alert
    showVisualToast(ride, speechText);
  }

  // Show floating top visual alert toast
  function showVisualToast(ride, announcementText) {
    let toast = document.getElementById('driverVoiceToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'driverVoiceToast';
      toast.className = 'driver-voice-toast';
      document.body.appendChild(toast);
    }

    const fareFormatted = formatFare(ride.fare);
    const vIcon = ride.vehicle_type === 'bendskin' ? '🏍️' : (ride.vehicle_type === 'comfort' ? '🚗' : '🚕');
    const isNegotiated = Boolean(ride.is_negotiated || ride.negotiation_status === 'PROPOSED');
    const isScheduled = Boolean(ride.is_scheduled);
    const scheduledType = ride.scheduled_type || 'standard';
    const sIcon = scheduledType === 'airport' ? '✈️' : (scheduledType === 'port' ? '⚓' : '📅');

    let titleText = isNegotiated ? 'Offre négociée reçue !' : 'Nouvelle course détectée !';
    if (isScheduled) {
      titleText = scheduledType === 'airport' ? 'Navette Aéroport planifiée !' : (scheduledType === 'port' ? 'Navette Port planifiée !' : 'Course planifiée !');
    }

    toast.innerHTML = `
      <div class="toast-voice-indicator">
        <span class="toast-voice-wave">${isScheduled ? sIcon : (isNegotiated ? '🤝' : '📢')}</span>
      </div>
      <div class="toast-body">
        <div class="toast-title">
          <span>${vIcon} ${titleText}</span>
          <span class="toast-fare">${fareFormatted} XAF</span>
        </div>
        ${isScheduled && ride.scheduled_time ? `
        <div style="font-size:0.75rem;color:#0369a1;font-weight:600;margin-bottom:2px;text-align:left;">
          ⏰ Départ prévu : ${ride.scheduled_time} (Réservation à l'avance)
        </div>` : ''}
        ${isScheduled && ride.flight_or_shift_notes ? `
        <div style="font-size:0.75rem;background:#f8fafc;color:#334155;padding:2px 6px;border-radius:4px;border:1px solid #e2e8f0;display:inline-block;margin-bottom:4px;text-align:left;">
          📝 ${ride.flight_or_shift_notes}
        </div>` : ''}
        ${isNegotiated && ride.original_fare ? `
        <div style="font-size:0.75rem;color:#64748b;margin-bottom:2px;text-align:left;">
          Tarif initial calculé : <del>${formatFare(ride.original_fare)} XAF</del> (Proposition passager)
        </div>` : ''}
        ${ride.cargo_type === 'market' ? `
        <div style="font-size:0.75rem;background:#fef3c7;color:#92400e;padding:2px 6px;border-radius:4px;display:inline-block;margin-bottom:4px;text-align:left;font-weight:600;">
          🛒 Marchandises de marché (+300 FCFA)
        </div>` : (ride.cargo_type === 'heavy' ? `
        <div style="font-size:0.75rem;background:#f3e8ff;color:#6b21a8;padding:2px 6px;border-radius:4px;display:inline-block;margin-bottom:4px;text-align:left;font-weight:600;">
          🧳 Gros bagages / Coffre plein (+600 FCFA)
        </div>` : '')}
        <div class="toast-route">
          <strong>📍 ${ride.pickup}</strong> ➔ <strong>🎯 ${ride.destination}</strong>
        </div>
        <div class="toast-sub">
          Passager : ${ride.rider_name || 'Passager MboaLift'} (${ride.passengers || 1} pers.)
        </div>
        <div class="toast-actions">
          ${isScheduled ? `
          <form method="POST" action="/driver/ride/${ride.id}/precommit" style="margin:0;">
            <button type="submit" class="btn-toast-accept" style="background:#047857;">🛡️ Pré-réserver cette navette</button>
          </form>` : `
          <form method="POST" action="/driver/ride/${ride.id}/accept" style="margin:0;">
            <button type="submit" class="btn-toast-accept">⚡ Accepter ${isNegotiated ? '(' + fareFormatted + ' F)' : ''}</button>
          </form>`}
          <button type="button" class="btn-toast-counter-toggle" onclick="var b=document.getElementById('toastCounterBox_${ride.id}');if(b){b.style.display=(b.style.display==='none'||!b.style.display)?'flex':'none';}">💬 Contre-proposer</button>
          <button type="button" class="btn-toast-dismiss" title="Refuser l'offre" onclick="this.closest('.driver-voice-toast').classList.remove('active')">✕ Refuser</button>
        </div>
        <div class="toast-counter-box" id="toastCounterBox_${ride.id}" style="display:none;margin-top:8px;padding-top:8px;border-top:1px dashed #cbd5e1;align-items:center;gap:6px;text-align:left;">
          <form method="POST" action="/driver/ride/${ride.id}/counter" style="display:flex;gap:6px;align-items:center;margin:0;width:100%;">
            <span style="font-size:0.75rem;color:#475569;white-space:nowrap;font-weight:600;">Votre prix :</span>
            <input type="number" name="counter_fare" value="${Math.round(ride.fare + 100)}" step="50" min="300" style="width:100px;padding:4px 8px;border:1px solid #cbd5e1;border-radius:6px;font-size:0.8rem;" required>
            <button type="submit" style="padding:4px 10px;background:#0284c7;color:#fff;border:none;border-radius:6px;font-size:0.78rem;font-weight:600;cursor:pointer;">Envoyer l'offre</button>
          </form>
        </div>
      </div>
    `;

    toast.classList.add('active');

    // Auto-dismiss after 16 seconds if not clicked
    if (toast._timer) clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.classList.remove('active');
    }, 16000);
  }

  // Poll driver alerts endpoint
  function pollAlerts() {
    fetch('/api/driver/alerts')
      .then(res => res.json())
      .then(data => {
        if (!data || !data.success || !Array.isArray(data.rides)) return;

        const currentRides = data.rides;

        if (isInitialPoll) {
          // On first load, seed the known set so we don't speak all historical pending rides at once
          currentRides.forEach(r => knownRideIds.add(r.id));
          isInitialPoll = false;
          return;
        }

        // Detect newly posted rides
        const newRides = [];
        currentRides.forEach(r => {
          if (!knownRideIds.has(r.id)) {
            knownRideIds.add(r.id);
            newRides.push(r);
          }
        });

        // Announce the newest ride
        if (newRides.length > 0) {
          // If multiple new rides arrived, announce the most recent one
          announceNewRide(newRides[0]);

          // If there's an active available rides table on page, gently update or notify
          updateAvailableRidesTableBadge(currentRides.length);
        }
      })
      .catch(() => {});
  }

  function updateAvailableRidesTableBadge(count) {
    const badge = document.querySelector('.badge-available-count');
    if (badge) {
      badge.textContent = count;
      badge.classList.add('pulse-highlight');
      setTimeout(() => badge.classList.remove('pulse-highlight'), 2000);
    }
  }

  // Toggle voice on/off
  function setVoiceEnabled(state, userInitiated = true) {
    isVoiceEnabled = Boolean(state);
    localStorage.setItem('mboalift_driver_voice_enabled', isVoiceEnabled ? 'true' : 'false');
    updateUiControls();

    if (userInitiated) {
      const lang = getCurrentLang();
      if (isVoiceEnabled) {
        const msg = lang === 'fr' 
          ? "Annonces vocales chauffeur activées. Vous entendrez les nouvelles courses."
          : "Driver voice alerts activated. New rides will be announced.";
        speakAnnouncement(msg, lang);
      } else {
        if ('speechSynthesis' in window) {
          window.speechSynthesis.cancel();
        }
      }
    }
  }

  // Test voice button handler
  function testVoice() {
    const lang = getCurrentLang();
    // Test with the exact prompt example
    const testText = lang === 'fr'
      ? "Nouvelle course disponible à Akwa pour 1 500 FCFA"
      : "New ride available at Akwa for 1,500 FCFA";

    speakAnnouncement(testText, lang);

    // Show demo toast
    showVisualToast({
      id: 999,
      pickup: 'Akwa (Boulevard de la Liberté)',
      destination: 'Bonanjo (Hôtel de Ville)',
      fare: 1500,
      vehicle_type: 'taxi',
      rider_name: 'Test Démo Chauffeur',
      passengers: 1
    }, testText);
  }

  // Update UI button appearance
  function updateUiControls() {
    const toggleBtns = document.querySelectorAll('.btn-voice-toggle');
    toggleBtns.forEach(btn => {
      const textEl = btn.querySelector('.voice-toggle-text');
      const dotEl = btn.querySelector('.voice-status-dot');

      if (isVoiceEnabled) {
        btn.classList.add('voice-active');
        btn.setAttribute('aria-pressed', 'true');
        if (textEl) {
          textEl.textContent = textEl.getAttribute('data-text-on') || '🔊 Voix Active';
        }
        if (dotEl) dotEl.className = 'voice-status-dot dot-active';
      } else {
        btn.classList.remove('voice-active');
        btn.setAttribute('aria-pressed', 'false');
        if (textEl) {
          textEl.textContent = textEl.getAttribute('data-text-off') || '🔇 Voix Coupée';
        }
        if (dotEl) dotEl.className = 'voice-status-dot dot-inactive';
      }
    });

    // Also update any badge
    const statusBadges = document.querySelectorAll('.driver-voice-badge');
    statusBadges.forEach(b => {
      if (isVoiceEnabled) {
        b.className = 'driver-voice-badge badge-active';
        b.textContent = '🔊 Annonce Vocale ON';
      } else {
        b.className = 'driver-voice-badge badge-inactive';
        b.textContent = '🔇 Annonce Vocale OFF';
      }
    });
  }

  // Setup DOM bindings
  function init() {
    // Check if we are on a driver page or if voice control elements exist
    const isDriverPage = document.querySelector('.driver-voice-card') ||
                         document.getElementById('driverVoiceCard') ||
                         window.location.pathname.startsWith('/driver');

    // Bind all toggle buttons
    document.querySelectorAll('.btn-voice-toggle').forEach(btn => {
      btn.addEventListener('click', () => {
        setVoiceEnabled(!isVoiceEnabled, true);
      });
    });

    // Bind test buttons
    document.querySelectorAll('.btn-voice-test').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        testVoice();
      });
    });

    updateUiControls();

    // Warm up speech synthesis voices
    if ('speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
      };
    }

    // Start polling if on driver views
    if (isDriverPage && !isPolling) {
      isPolling = true;
      // First poll immediately to seed IDs
      pollAlerts();
      pollingInterval = setInterval(pollAlerts, POLL_INTERVAL_MS);
    }
  }

  // Public API
  window.MboaLiftDriverVoice = {
    init: init,
    toggle: () => setVoiceEnabled(!isVoiceEnabled, true),
    test: testVoice,
    announce: announceNewRide,
    isEnabled: () => isVoiceEnabled
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
