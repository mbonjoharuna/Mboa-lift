/**
 * ride_tracker.js
 * ---------------
 * Real-time Live Ride Status Tracker for MboaLift.
 *
 * Responsibilities:
 * - Polls /api/ride-status/<ride_id> every 3.5 seconds for active rides.
 * - Dynamically updates the 4-step progress stepper:
 *     Step 1: En recherche de chauffeur ⏳ (PENDING)
 *     Step 2: Chauffeur en route (2 min) 🚗 (ACCEPTED)
 *     Step 3: Course en cours 📍 (IN_PROGRESS)
 *     Step 4: Arrivé à destination ✅ (COMPLETED)
 * - Transitions smoothly in the UI without forcing page reloads.
 * - Plays an audio notification chime via Web Audio API when a driver accepts the ride.
 * - Displays driver contact info (one-tap call), WhatsApp safety share, and MoMo pay button.
 */

(function () {
  'use strict';

  let pollTimer = null;
  let previousStatus = null;

  document.addEventListener('DOMContentLoaded', function () {
    const trackerContainer = document.querySelector('[data-active-ride-id]');
    if (!trackerContainer) return;

    const rideId = trackerContainer.getAttribute('data-active-ride-id');
    const initialStatus = trackerContainer.getAttribute('data-active-ride-status') || 'PENDING';
    previousStatus = initialStatus;

    // Start live status polling if ride is active
    if (['PENDING', 'ACCEPTED', 'IN_PROGRESS'].includes(initialStatus)) {
      startLiveTracker(rideId, trackerContainer);
    }
  });

  function startLiveTracker(rideId, container) {
    if (pollTimer) clearInterval(pollTimer);

    // Initial immediate fetch
    checkStatus(rideId, container);

    // Poll every 3.5 seconds
    pollTimer = setInterval(function () {
      checkStatus(rideId, container);
    }, 3500);
  }

  function checkStatus(rideId, container) {
    fetch('/api/ride-status/' + rideId)
      .then(function (res) {
        if (!res.ok) throw new Error('Status fetch failed');
        return res.json();
      })
      .then(function (data) {
        if (!data || data.error) return;

        updateTrackerUI(container, data);

        // Chime alert when ride is accepted
        if (previousStatus === 'PENDING' && data.status === 'ACCEPTED') {
          playNotificationChime();
        }

        previousStatus = data.status;

        // Stop polling if completed or cancelled
        if (data.status === 'COMPLETED' || data.status === 'CANCELLED') {
          clearInterval(pollTimer);
          pollTimer = null;
        }
      })
      .catch(function (err) {
        console.debug('Polling note:', err);
      });
  }

  function updateTrackerUI(container, ride) {
    const statusTextEl = container.querySelector('.tracker-main-status');
    const etaBadgeEl = container.querySelector('.tracker-eta-badge');
    const lineFillEl = container.querySelector('.stepper-line-fill');
    const driverRibbonEl = container.querySelector('.tracker-driver-ribbon');
    const actionsEl = container.querySelector('.tracker-actions');

    // Update Card State Class
    container.className = 'live-tracker-card status-' + ride.status.toLowerCase();

    // Stepper Step Progress
    const steps = container.querySelectorAll('.stepper-step');
    const labels = container.querySelectorAll('.stepper-label-item');

    let fillPercentage = '0%';
    if (ride.step === 1) fillPercentage = '12%';
    else if (ride.step === 2) fillPercentage = '40%';
    else if (ride.step === 3) fillPercentage = '75%';
    else if (ride.step === 4) fillPercentage = '100%';

    if (lineFillEl) {
      lineFillEl.style.width = fillPercentage;
    }

    steps.forEach(function (el, idx) {
      const stepNum = idx + 1;
      el.classList.remove('active', 'completed');
      if (stepNum < ride.step) {
        el.classList.add('completed');
        el.innerHTML = '✓';
      } else if (stepNum === ride.step) {
        el.classList.add('active');
        el.innerHTML = stepNum;
      } else {
        el.innerHTML = stepNum;
      }
    });

    labels.forEach(function (el, idx) {
      const stepNum = idx + 1;
      if (stepNum === ride.step) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });

    // Update Status Text & ETA
    if (statusTextEl) {
      statusTextEl.textContent = ride.label || ride.status;
    }

    if (etaBadgeEl) {
      if (ride.eta) {
        etaBadgeEl.style.display = 'inline-flex';
        etaBadgeEl.innerHTML = `⏱️ ${ride.eta}`;
      } else {
        etaBadgeEl.style.display = 'none';
      }
    }

    // Dynamic Negotiation UI update ("Marchandage à la Doualaise")
    const negBox = container.querySelector('#trackerNegotiationBox');
    if (negBox) {
      const counterSec = negBox.querySelector('#counterOfferSection');
      const proposedSec = negBox.querySelector('#proposedOfferSection');
      const acceptedSec = negBox.querySelector('#acceptedOfferSection');
      const fareBadgeEl = container.querySelector('.fare-badge');

      if (fareBadgeEl && ride.fare) {
        fareBadgeEl.textContent = Math.round(ride.fare) + ' XAF';
      }

      if (ride.negotiation_status === 'COUNTERED' && ride.driver_counter_fare) {
        negBox.style.display = 'block';
        if (counterSec) {
          counterSec.style.display = 'block';
          const cAmt = Math.round(ride.driver_counter_fare);
          const cText = counterSec.querySelector('.counter-fare-text');
          if (cText) cText.textContent = cAmt + ' XAF';
          const cBtn = counterSec.querySelector('#btnAcceptCounter');
          if (cBtn) cBtn.textContent = '⚡ Accepter la contre-offre (' + cAmt + ' XAF)';
          const dNameEl = counterSec.querySelector('#counterDriverName');
          if (dNameEl && ride.counter_driver_name) dNameEl.textContent = ride.counter_driver_name;
        }
        if (proposedSec) proposedSec.style.display = 'none';
        if (acceptedSec) acceptedSec.style.display = 'none';

        // Alert chime if counter offer freshly arrived
        if (!negBox._hasChimedCounter) {
          playNotificationChime();
          negBox._hasChimedCounter = true;
        }
      } else if (ride.negotiation_status === 'PROPOSED') {
        negBox.style.display = 'block';
        if (counterSec) counterSec.style.display = 'none';
        if (proposedSec) {
          proposedSec.style.display = 'block';
          const curOfferText = proposedSec.querySelector('#currentNegotiatedFareText');
          if (curOfferText) curOfferText.textContent = Math.round(ride.fare) + ' XAF';
        }
        if (acceptedSec) acceptedSec.style.display = 'none';
      } else if (ride.negotiation_status === 'ACCEPTED' && ride.status !== 'PENDING') {
        negBox.style.display = 'block';
        if (counterSec) counterSec.style.display = 'none';
        if (proposedSec) proposedSec.style.display = 'none';
        if (acceptedSec) acceptedSec.style.display = 'block';
      } else {
        if (ride.status !== 'PENDING') {
          negBox.style.display = 'none';
        }
      }
    }

    // Driver Details Ribbon
    if (driverRibbonEl) {
      if (ride.driver_name) {
        driverRibbonEl.style.display = 'flex';
        const dName = driverRibbonEl.querySelector('.driver-name-text');
        const dVehicle = driverRibbonEl.querySelector('.driver-vehicle-text');
        const dPhoneLink = driverRibbonEl.querySelector('.driver-phone-link');

        if (dName) dName.textContent = ride.driver_name;
        if (dVehicle) dVehicle.textContent = `${ride.vehicle_info || 'Chauffeur MboaLift'} · ${ride.driver_location || 'Douala'}`;
        if (dPhoneLink && ride.driver_phone) {
          dPhoneLink.href = 'tel:' + ride.driver_phone;
          dPhoneLink.textContent = '📞 ' + ride.driver_phone;
          dPhoneLink.style.display = 'inline-block';
        }
      } else {
        driverRibbonEl.style.display = 'none';
      }
    }

    // Update Pay / Actions Buttons
    if (actionsEl) {
      let payBtn = actionsEl.querySelector('.btn-pay-action');
      let receiptBtn = actionsEl.querySelector('.btn-receipt-action');
      let paidBadge = actionsEl.querySelector('.paid-status-badge');

      if (ride.status !== 'PENDING' && !ride.is_paid) {
        if (!payBtn) {
          payBtn = document.createElement('a');
          payBtn.className = 'btn-primary btn-sm btn-pay-action';
          payBtn.href = '/payment/' + ride.id;
          payBtn.textContent = '💳 Payer par MoMo / OM (' + Math.round(ride.fare) + ' XAF)';
          actionsEl.appendChild(payBtn);
        }
      } else if (ride.is_paid) {
        if (payBtn) payBtn.remove();
        if (!paidBadge && !actionsEl.querySelector('.badge-success')) {
          paidBadge = document.createElement('span');
          paidBadge.className = 'badge badge-success paid-status-badge';
          paidBadge.textContent = 'Paiement validé ✅';
          actionsEl.appendChild(paidBadge);
        }
        if (!receiptBtn && !actionsEl.querySelector('a[href*="/receipt/"]')) {
          receiptBtn = document.createElement('a');
          receiptBtn.className = 'btn-outline btn-sm btn-receipt-action';
          receiptBtn.href = '/receipt/' + ride.id;
          receiptBtn.target = '_blank';
          receiptBtn.innerHTML = '📄 Reçu PDF & QR Code';
          actionsEl.appendChild(receiptBtn);
        }
      }
    }
  }

  // Native Web Audio chime (no external MP3 needed)
  function playNotificationChime() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();

      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
      osc.frequency.setValueAtTime(880.00, ctx.currentTime + 0.15); // A5

      gain.gain.setValueAtTime(0.2, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.45);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start();
      osc.stop(ctx.currentTime + 0.45);
    } catch (e) {
      // Audio context might be restricted before user gesture
    }
  }

  // Global actions for Passenger Street Fare Bargaining
  window.acceptDriverCounter = function (rideId) {
    if (!confirm("Accepter cette contre-offre et confirmer votre course ?")) return;
    fetch('/api/ride/' + rideId + '/accept-counter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          window.location.reload();
        } else {
          alert(data.error || "Impossible d'accepter la contre-offre.");
        }
      })
      .catch(() => alert("Erreur réseau. Veuillez réessayer."));
  };

  window.declineDriverCounter = function (rideId) {
    if (!confirm("Refuser la contre-offre du chauffeur ? Votre demande reste ouverte.")) return;
    fetch('/api/ride/' + rideId + '/decline-counter', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          window.location.reload();
        } else {
          alert(data.error || "Impossible de refuser.");
        }
      })
      .catch(() => alert("Erreur réseau. Veuillez réessayer."));
  };

  window.submitAdjustOffer = function (rideId) {
    const input = document.getElementById('inputNewOffer');
    if (!input) return;
    const fare = parseFloat(input.value);
    if (!fare || fare < 300) {
      alert("Veuillez saisir un montant valide (minimum 300 XAF).");
      return;
    }

    fetch('/api/ride/' + rideId + '/negotiate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fare: fare })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const form = document.getElementById('adjustOfferForm');
          if (form) form.style.display = 'none';
          const trackerContainer = document.querySelector('[data-active-ride-id]');
          if (trackerContainer) checkStatus(rideId, trackerContainer);
        } else {
          alert(data.error || "Impossible de mettre à jour l'offre.");
        }
      })
      .catch(() => alert("Erreur réseau."));
  };

  window.MboaLiftTracker = {
    start: startLiveTracker
  };

})();
