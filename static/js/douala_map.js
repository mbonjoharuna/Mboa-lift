/**
 * douala_map.js
 * -------------
 * Interactive Douala Route Map powered by Leaflet.js and OpenStreetMap.
 * Designed for the "Reinvent Douala's Ride" Urban Mobility Challenge.
 *
 * Features:
 * - Real geographic coordinates for all 15 Douala zones and iconic landmarks
 *   (Pont du Wouri, Rond-Point Deido, Carrefour Ndokoti, Akwa, Bonanjo, Aéroport).
 * - Smooth dynamic route polylines connecting pickup and destination.
 * - Animated vehicle marker (Bendskin moto 🏍️, Taxi Jaune 🚕, Confort 🚗) gliding along the route.
 * - Live nearby free driver markers fetched from /api/map-data.
 * - Interactive 1-click landmark shortcut pills.
 * - Click-to-set pickup / destination popups.
 * - Offline-resilient SVG radar fallback if tiles or external CDN cannot be reached.
 */

(function () {
  'use strict';

  // Master Douala Coordinates Map
  const DOUALA_COORDS = {
    'Akwa': [4.0503, 9.6979],
    'Bonanjo': [4.0435, 9.6894],
    'Deido': [4.0628, 9.7105],
    'Bonamoussadi': [4.0894, 9.7364],
    'Makepe': [4.0805, 9.7428],
    'Bépanda': [4.0592, 9.7289],
    'Bonapriso': [4.0322, 9.6975],
    'Bali': [4.0381, 9.6953],
    'New Bell': [4.0325, 9.7161],
    'Ndokoti': [4.0441, 9.7397],
    'Logbessou': [4.0986, 9.7642],
    'Bonabéri': [4.0722, 9.6644],
    'Aéroport': [4.0118, 9.7194],
    'Japoma': [3.9875, 9.8025],
    'Cité des Palmiers': [4.0508, 9.7558]
  };

  const DOUALA_LANDMARKS = [
    { name: 'Total Énergie Ndokoti', area: 'Ndokoti', coords: [4.0435, 9.7428], icon: '⛽', tip: 'Carrefour & Station Ndokoti · Grand hub Bendskin & Taxis' },
    { name: 'Ancien Dalip (Akwa)', area: 'Akwa', coords: [4.0532, 9.6968], icon: '🏛️', tip: 'Repère historique Akwa · Boulevard de la Liberté' },
    { name: 'Mobil Guinness (Bépanda)', area: 'Bépanda', coords: [4.0620, 9.7285], icon: '🏭', tip: 'Axe Guinness Cameroun & Carrefour Bépanda' },
    { name: 'Carrefour Deux Églises (Bépanda)', area: 'Bépanda', coords: [4.0688, 9.7321], icon: '⛪', tip: 'Repère célèbre carrefour Deux Églises Bépanda' },
    { name: 'Rond-Point Deïdo', area: 'Deido', coords: [4.0635, 9.7125], icon: '🔄', tip: 'Statue du Centenaire & Nœud stratégique de Deïdo' },
    { name: 'Douche Municipale (Akwa)', area: 'Akwa', coords: [4.0485, 9.6952], icon: '🚿', tip: 'Repère central carrefour Douche · Boulevard de la Liberté' },
    { name: 'Boulangerie Zepol (Akwa)', area: 'Akwa', coords: [4.0515, 9.6990], icon: '🥖', tip: 'Point de rencontre mythique 24h/24 Akwa' },
    { name: 'Gare de Bessengue (Camrail)', area: 'Deido', coords: [4.0560, 9.7130], icon: '🚉', tip: 'Gare ferroviaire centrale Camrail Douala' },
    { name: 'Pont du Wouri (Côté Bonabéri)', area: 'Bonabéri', coords: [4.0725, 9.6780], icon: '🌉', tip: 'Tête du pont · Sortie Ouest & Grand Ouest' },
    { name: 'Carrefour Mutzig (Bonabéri)', area: 'Bonabéri', coords: [4.0780, 9.6620], icon: '🍻', tip: 'Carrefour commercial et populaire de Bonabéri' },
    { name: 'Quatre Étages (Bonabéri)', area: 'Bonabéri', coords: [4.0815, 9.6540], icon: '🏢', tip: 'Repère des Quatre Étages Bonabéri' },
    { name: 'Marché Mboppi', area: 'Bépanda', coords: [4.0478, 9.7225], icon: '🛒', tip: 'Plus grand marché de gros d\'Afrique Centrale' },
    { name: 'Aéroport Int. de Douala (DLA)', area: 'Aéroport', coords: [4.0118, 9.7194], icon: '✈️', tip: 'Hub aérien international (DLA)' },
    { name: 'Rond-Point Maetur (Bonamoussadi)', area: 'Bonamoussadi', coords: [4.0882, 9.7345], icon: '🔄', tip: 'Cœur résidentiel et commerces de Bonamoussadi' },
    { name: 'Carrefour Denver (Bonamoussadi)', area: 'Bonamoussadi', coords: [4.0921, 9.7388], icon: '🚦', tip: 'Secteur branché et résidentiel de Douala 5e' },
    { name: 'Université de Douala (ESSEC / Ange Raphaël)', area: 'Makepe', coords: [4.0782, 9.7410], icon: '🎓', tip: 'Campus universitaire et école de commerce ESSEC' },
    { name: 'Hôpital Général de Douala (Makepe)', area: 'Makepe', coords: [4.0845, 9.7455], icon: '🏥', tip: 'Hôpital de référence et urgences Douala Nord' },
    { name: 'Marché Central (New Bell)', area: 'New Bell', coords: [4.0325, 9.7161], icon: '🛍️', tip: 'Grand pôle commercial textiles & vivres' },
    { name: 'Marché Sandaga (New Bell)', area: 'New Bell', coords: [4.0362, 9.7115], icon: '🥬', tip: 'Grossistes vivriers et légumes frais' },
    { name: 'Carrefour Agip (New Bell)', area: 'New Bell', coords: [4.0392, 9.7198], icon: '🚦', tip: 'Carrefour reliant New Bell à Ndokoti' },
    { name: 'Clinique Soppo Priso (Bonapriso)', area: 'Bonapriso', coords: [4.0315, 9.6962], icon: '🏥', tip: 'Quartier résidentiel et médical de Bonapriso' },
    { name: 'Rue Mandessi Bell (Bali)', area: 'Bali', coords: [4.0381, 9.6953], icon: '🛣️', tip: 'Liaison historique Akwa-Bonanjo vers Koumassi' },
    { name: 'Complexe Sportif Japoma', area: 'Japoma', coords: [3.9875, 9.8025], icon: '🏟️', tip: 'Grand stade omnisports Japoma & sortie Yaoundé' },
    { name: 'Carrefour Cité des Palmiers', area: 'Cité des Palmiers', coords: [4.0508, 9.7558], icon: '🌴', tip: 'Zone urbaine Douala 3e & carrefour Bille' }
  ];

  let mapInstance = null;
  let routePolyline = null;
  let pickupMarker = null;
  let destinationMarker = null;
  let glidingVehicleMarker = null;
  let driverLayerGroup = null;
  let animationInterval = null;

  // Initialize interactive map when DOM is loaded
  document.addEventListener('DOMContentLoaded', function () {
    const mapElement = document.getElementById('doualaMap') || document.getElementById('driverMap');
    if (!mapElement) return;

    if (typeof L === 'undefined') {
      renderSvgRadarFallback(mapElement);
      return;
    }

    try {
      initLeafletMap(mapElement);
    } catch (err) {
      console.warn('Leaflet init fallback:', err);
      renderSvgRadarFallback(mapElement);
    }
  });

  function initLeafletMap(container) {
    const isDriverMap = container.id === 'driverMap';
    const center = [4.0511, 9.7150]; // Douala Center

    mapInstance = L.map(container.id, {
      center: center,
      zoom: 12,
      scrollWheelZoom: false,
      zoomControl: true
    });

    // OpenStreetMap Clean Tile Layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap contributors | MboaLift Douala'
    }).addTo(mapInstance);

    // Layer group for drivers
    driverLayerGroup = L.layerGroup().addTo(mapInstance);

    // Plot iconic Douala landmarks
    plotLandmarks();

    // Fetch active drivers and pending rides
    fetchLiveMapData(isDriverMap);

    // If Passenger Request Ride form exists, wire up inputs
    if (!isDriverMap) {
      setupPassengerRideMap();
    } else {
      setupDriverMap();
    }

    // Fix map sizing in hidden tabs/resizes
    window.setTimeout(() => mapInstance.invalidateSize(), 300);
  }

  // Plot landmarks
  function plotLandmarks() {
    DOUALA_LANDMARKS.forEach(function (lm) {
      const icon = L.divIcon({
        className: 'custom-leaflet-pin',
        html: `<div class="douala-pin pin-landmark" title="${lm.name}">${lm.icon}</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const safeName = lm.name.replace(/'/g, "\\'");
      L.marker(lm.coords, { icon: icon })
        .addTo(mapInstance)
        .bindPopup(`
          <div class="douala-map-landmark-popup" style="text-align:left;min-width:190px;">
            <div style="font-weight:700;font-size:0.92rem;color:#0f172a;display:flex;align-items:center;gap:6px;">
              <span>${lm.icon}</span> <span>${lm.name}</span>
            </div>
            <div style="font-size:0.75rem;color:#64748b;margin:4px 0 8px 0;">${lm.tip}</div>
            <div style="display:flex;gap:6px;">
              <button type="button" class="btn-popup-pin" onclick="window.focusDoualaLandmark('${safeName}', 'pickup')" style="flex:1;background:#2563eb;color:#fff;border:none;border-radius:6px;padding:4px 6px;font-size:0.75rem;font-weight:600;cursor:pointer;">📍 Départ</button>
              <button type="button" class="btn-popup-pin" onclick="window.focusDoualaLandmark('${safeName}', 'destination')" style="flex:1;background:#dc2626;color:#fff;border:none;border-radius:6px;padding:4px 6px;font-size:0.75rem;font-weight:600;cursor:pointer;">🎯 Arrivée</button>
            </div>
          </div>
        `);
    });
  }

  // Fetch live drivers and demand hotspots from Flask API
  function fetchLiveMapData(isDriverMap) {
    fetch('/api/map-data')
      .then(res => res.json())
      .then(data => {
        if (!data) return;

        // Plot active nearby free drivers
        if (data.active_drivers && Array.isArray(data.active_drivers)) {
          driverLayerGroup.clearLayers();
          data.active_drivers.forEach(d => {
            const vIcon = d.vehicle_type === 'bendskin' ? '🏍️' : (d.vehicle_type === 'comfort' ? '🚗' : '🚕');
            const dMarker = L.divIcon({
              className: 'custom-driver-pin',
              html: `<div class="douala-pin pin-driver" title="${d.name}">${vIcon}</div>`,
              iconSize: [30, 30],
              iconAnchor: [15, 15]
            });

            const marker = L.marker([d.lat, d.lng], { icon: dMarker });
            marker.bindPopup(`
              <strong>${d.name}</strong> · <span class="badge badge-success">Libre</span><br>
              <small>📍 ${d.location} | ${d.vehicle_info || d.vehicle_type}</small><br>
              <small>📞 ${d.phone}</small>
            `);
            driverLayerGroup.addLayer(marker);
          });
        }

        // For driver dashboard, plot pending ride requests
        if (isDriverMap && data.available_rides && Array.isArray(data.available_rides)) {
          data.available_rides.forEach(r => {
            if (r.pickup_lat && r.pickup_lng) {
              const rIcon = L.divIcon({
                className: 'custom-demand-pin',
                html: `<div class="douala-pin pin-destination" style="background:#f59e0b;" title="Demande #${r.id}">📍</div>`,
                iconSize: [28, 28],
                iconAnchor: [14, 14]
              });

              L.marker([r.pickup_lat, r.pickup_lng], { icon: rIcon })
                .addTo(mapInstance)
                .bindPopup(`
                  <strong>Demande de Course #${r.id}</strong><br>
                  <span>📍 ${r.pickup} → ${r.destination}</span><br>
                  <strong>${r.fare} XAF</strong> (${r.vehicle_type})<br>
                  <form method="POST" action="/driver/ride/${r.id}/accept" style="margin-top:6px;">
                    <button type="submit" class="btn-primary btn-sm" style="padding:4px 8px;font-size:0.75rem;">Accepter</button>
                  </form>
                `);
            }
          });
        }
      })
      .catch(() => {});
  }

  // Passenger Booking Map interactions
  function setupPassengerRideMap() {
    const pickupInput = document.getElementById('pickup');
    const destInput = document.getElementById('destination');

    function updateMapRoute() {
      const pVal = normalizeLoc(pickupInput ? pickupInput.value : '');
      const dVal = normalizeLoc(destInput ? destInput.value : '');

      const pCoords = DOUALA_COORDS[pVal];
      const dCoords = DOUALA_COORDS[dVal];

      // Remove existing route elements
      if (routePolyline) {
        mapInstance.removeLayer(routePolyline);
        routePolyline = null;
      }
      if (pickupMarker) {
        mapInstance.removeLayer(pickupMarker);
        pickupMarker = null;
      }
      if (destinationMarker) {
        mapInstance.removeLayer(destinationMarker);
        destinationMarker = null;
      }
      if (glidingVehicleMarker) {
        mapInstance.removeLayer(glidingVehicleMarker);
        glidingVehicleMarker = null;
      }
      if (animationInterval) {
        clearInterval(animationInterval);
        animationInterval = null;
      }

      // Plot pickup marker
      if (pCoords) {
        const pIcon = L.divIcon({
          className: 'custom-pickup-pin',
          html: `<div class="douala-pin pin-pickup">📍<span class="pulse-ring"></span></div>`,
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        });
        pickupMarker = L.marker(pCoords, { icon: pIcon }).addTo(mapInstance);
        pickupMarker.bindPopup(`<strong>Point de départ</strong><br>${pVal}`).openPopup();
      }

      // Plot destination marker
      if (dCoords) {
        const dIcon = L.divIcon({
          className: 'custom-dest-pin',
          html: `<div class="douala-pin pin-destination">🎯</div>`,
          iconSize: [32, 32],
          iconAnchor: [16, 16]
        });
        destinationMarker = L.marker(dCoords, { icon: dIcon }).addTo(mapInstance);
        destinationMarker.bindPopup(`<strong>Destination</strong><br>${dVal}`);
      }

      // Both selected: Draw curved animated route polyline
      if (pCoords && dCoords && (pVal !== dVal)) {
        const routePoints = generateRoutePoints(pCoords, dCoords);

        routePolyline = L.polyline(routePoints, {
          color: '#2563eb',
          weight: 5,
          opacity: 0.85,
          dashArray: '8, 8',
          lineCap: 'round'
        }).addTo(mapInstance);

        // Fit map bounds to view both points
        const bounds = L.latLngBounds([pCoords, dCoords]);
        mapInstance.fitBounds(bounds, { padding: [60, 60], maxZoom: 14 });

        // Start gliding vehicle animation
        animateVehicleOnRoute(routePoints);
      } else if (pCoords) {
        mapInstance.setView(pCoords, 13, { animate: true });
      } else if (dCoords) {
        mapInstance.setView(dCoords, 13, { animate: true });
      }
    }

    if (pickupInput) {
      pickupInput.addEventListener('change', updateMapRoute);
      pickupInput.addEventListener('input', updateMapRoute);
    }
    if (destInput) {
      destInput.addEventListener('change', updateMapRoute);
      destInput.addEventListener('input', updateMapRoute);
    }

    // Vehicle radio change updates the animated icon
    document.querySelectorAll('input[name="vehicle_type"]').forEach(r => {
      r.addEventListener('change', updateMapRoute);
    });

    // Wire landmark shortcut pills
    document.querySelectorAll('.landmark-pill').forEach(btn => {
      btn.addEventListener('click', function () {
        const loc = this.getAttribute('data-location') || this.textContent.trim();
        if (!pickupInput.value) {
          pickupInput.value = loc;
        } else if (!destInput.value) {
          destInput.value = loc;
        } else {
          destInput.value = loc;
        }
        updateMapRoute();
        // Trigger existing fare calculator update
        pickupInput.dispatchEvent(new Event('change'));
      });
    });

    // Allow user to click anywhere on map to set pickup or destination
    mapInstance.on('click', function (e) {
      const nearest = findNearestDoualaLocation(e.latlng.lat, e.latlng.lng);
      if (!nearest) return;

      const popupContent = `
        <div style="font-size:0.85rem;line-height:1.4;">
          <strong>Quartier : ${nearest.name}</strong><br>
          <small style="color:#64748b;">Choisir pour votre course :</small>
          <div style="display:flex;gap:6px;margin-top:8px;">
            <button type="button" class="btn-primary btn-sm" id="setPickupBtn" style="padding:4px 8px;font-size:0.75rem;">Départ 📍</button>
            <button type="button" class="btn-outline btn-sm" id="setDestBtn" style="padding:4px 8px;font-size:0.75rem;">Arrivée 🎯</button>
          </div>
        </div>
      `;

      const popup = L.popup()
        .setLatLng(nearest.coords)
        .setContent(popupContent)
        .openOn(mapInstance);

      setTimeout(() => {
        const pBtn = document.getElementById('setPickupBtn');
        const dBtn = document.getElementById('setDestBtn');
        if (pBtn) {
          pBtn.onclick = () => {
            pickupInput.value = nearest.name;
            updateMapRoute();
            pickupInput.dispatchEvent(new Event('change'));
            mapInstance.closePopup();
          };
        }
        if (dBtn) {
          dBtn.onclick = () => {
            destInput.value = nearest.name;
            updateMapRoute();
            destInput.dispatchEvent(new Event('change'));
            mapInstance.closePopup();
          };
        }
      }, 50);
    });

    // Initial check in case values are pre-filled
    updateMapRoute();
  }

  // Driver map setup
  function setupDriverMap() {
    const driverLocEl = document.getElementById('driverCurrentArea');
    if (driverLocEl) {
      const loc = normalizeLoc(driverLocEl.textContent.trim());
      const coords = DOUALA_COORDS[loc];
      if (coords) {
        mapInstance.setView(coords, 13);
        const myIcon = L.divIcon({
          className: 'custom-driver-pos',
          html: `<div class="douala-pin pin-driver" style="background:#10b981;">🚗<span class="pulse-ring"></span></div>`,
          iconSize: [36, 36],
          iconAnchor: [18, 18]
        });
        L.marker(coords, { icon: myIcon })
          .addTo(mapInstance)
          .bindPopup(`<strong>Votre position actuelle</strong><br>${loc} (Disponible)`)
          .openPopup();
      }
    }
  }

  // Smooth vehicle glide animation along the route
  function animateVehicleOnRoute(points) {
    if (!points || points.length < 2) return;

    const vehicleTypeInput = document.querySelector('input[name="vehicle_type"]:checked');
    const vType = vehicleTypeInput ? vehicleTypeInput.value : 'taxi';
    const vEmoji = vType === 'bendskin' ? '🏍️' : (vType === 'comfort' ? '🚗' : '🚕');

    const vIcon = L.divIcon({
      className: 'gliding-vehicle',
      html: `<div style="font-size:24px;filter:drop-shadow(0 3px 6px rgba(0,0,0,0.3));">${vEmoji}</div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });

    glidingVehicleMarker = L.marker(points[0], { icon: vIcon }).addTo(mapInstance);

    let stepIndex = 0;
    const totalSteps = points.length;

    animationInterval = setInterval(() => {
      stepIndex = (stepIndex + 1) % totalSteps;
      const targetPos = points[stepIndex];
      glidingVehicleMarker.setLatLng(targetPos);
    }, 280);
  }

  // Interpolate intermediate waypoints between pickup and destination for realistic curved trajectory
  function generateRoutePoints(start, end) {
    const points = [];
    const steps = 14;

    // Slight curvature simulating Douala road grid
    const midLat = (start[0] + end[0]) / 2 + (start[1] - end[1]) * 0.08;
    const midLng = (start[1] + end[1]) / 2 + (end[0] - start[0]) * 0.08;

    for (let i = 0; i <= steps; i++) {
      const t = i / steps;
      // Quadratic Bezier interpolation
      const lat = (1 - t) * (1 - t) * start[0] + 2 * (1 - t) * t * midLat + t * t * end[0];
      const lng = (1 - t) * (1 - t) * start[1] + 2 * (1 - t) * t * midLng + t * t * end[1];
      points.push([lat, lng]);
    }
    return points;
  }

  // Helper to find nearest known Douala neighborhood from map click
  function findNearestDoualaLocation(lat, lng) {
    let nearest = null;
    let minDist = Infinity;

    for (const [name, coords] of Object.entries(DOUALA_COORDS)) {
      const dLat = coords[0] - lat;
      const dLng = coords[1] - lng;
      const dist = dLat * dLat + dLng * dLng;
      if (dist < minDist) {
        minDist = dist;
        nearest = { name, coords };
      }
    }
    return nearest;
  }

  function normalizeLoc(str) {
    if (!str) return '';
    const clean = str.trim().toLowerCase();
    for (const k of Object.keys(DOUALA_COORDS)) {
      if (k.toLowerCase() === clean) return k;
    }
    // Partial search
    for (const k of Object.keys(DOUALA_COORDS)) {
      if (clean.includes(k.toLowerCase()) || k.toLowerCase().includes(clean)) return k;
    }
    return str;
  }

  // SVG Radar Fallback for isolated offline environments
  function renderSvgRadarFallback(container) {
    container.innerHTML = `
      <div class="map-fallback-banner">
        <span>🗺️ <strong>Carte Urbaine Douala</strong> (Mode déconnecté autonome)</span>
      </div>
      <svg viewBox="0 0 600 360" style="width:100%;height:100%;background:#0f172a;border-radius:0 0 16px 16px;">
        <!-- Wouri Estuary River Path -->
        <path d="M 0,220 Q 180,190 280,120 T 600,60 L 600,0 L 0,0 Z" fill="#1e293b" opacity="0.6" />
        <path d="M 120,240 Q 240,160 320,110 T 520,30" stroke="#38bdf8" stroke-width="8" fill="none" opacity="0.4" />
        
        <!-- Pont du Wouri -->
        <line x1="230" y1="165" x2="260" y2="140" stroke="#f59e0b" stroke-width="6" stroke-dasharray="4,2" />
        <text x="210" y="195" fill="#f59e0b" font-size="11" font-weight="bold">Pont du Wouri 🌉</text>

        <!-- Landmarks & Zones -->
        <g fill="#ffffff" font-size="11" font-family="sans-serif">
          <!-- Bonabéri (Left bank) -->
          <circle cx="160" cy="180" r="6" fill="#3b82f6" />
          <text x="140" y="170">Bonabéri</text>

          <!-- Deido -->
          <circle cx="280" cy="130" r="6" fill="#10b981" />
          <text x="290" y="130">Deido 🔄</text>

          <!-- Akwa -->
          <circle cx="260" cy="210" r="7" fill="#ef4444" />
          <text x="272" y="215" font-weight="bold">Akwa 🛍️</text>

          <!-- Bonanjo -->
          <circle cx="230" cy="240" r="6" fill="#6366f1" />
          <text x="242" y="245">Bonanjo 🏛️</text>

          <!-- Ndokoti -->
          <circle cx="380" cy="210" r="7" fill="#f59e0b" />
          <text x="392" y="215" font-weight="bold">Ndokoti 🚦</text>

          <!-- Bonamoussadi -->
          <circle cx="340" cy="80" r="6" fill="#10b981" />
          <text x="352" y="85">Bonamoussadi</text>

          <!-- Aéroport -->
          <circle cx="340" cy="310" r="6" fill="#ec4899" />
          <text x="352" y="315">Aéroport (DLA) ✈️</text>
        </g>
      </svg>
    `;
  }

  // Focus Douala Landmark with animated pan and pulsing pin
  let landmarkHighlightMarker = null;

  function focusDoualaLandmark(landmarkInput, targetField) {
    if (!landmarkInput) return;

    let targetCoords = null;
    let landmarkObj = null;
    let landmarkName = '';
    let canonicalArea = '';

    if (typeof landmarkInput === 'object') {
      targetCoords = [
        landmarkInput.lat || (landmarkInput.coords && landmarkInput.coords[0]),
        landmarkInput.lng || (landmarkInput.coords && landmarkInput.coords[1])
      ];
      landmarkName = landmarkInput.name || '';
      canonicalArea = landmarkInput.area || landmarkName;
      landmarkObj = landmarkInput;
    } else {
      const query = String(landmarkInput).trim().toLowerCase();
      // Search in DOUALA_LANDMARKS
      for (let i = 0; i < DOUALA_LANDMARKS.length; i++) {
        const lm = DOUALA_LANDMARKS[i];
        if (lm.name.toLowerCase() === query || lm.name.toLowerCase().includes(query) || query.includes(lm.name.toLowerCase())) {
          targetCoords = lm.coords;
          landmarkName = lm.name;
          canonicalArea = lm.area || lm.name;
          landmarkObj = lm;
          break;
        }
      }
      // Search in DOUALA_COORDS
      if (!targetCoords) {
        for (const loc in DOUALA_COORDS) {
          if (loc.toLowerCase() === query || loc.toLowerCase().includes(query)) {
            targetCoords = DOUALA_COORDS[loc];
            landmarkName = loc;
            canonicalArea = loc;
            landmarkObj = { name: loc, area: loc, icon: '📍', tip: 'Zone de Douala' };
            break;
          }
        }
      }
    }

    // Set input field if requested
    if (targetField && canonicalArea) {
      const field = document.getElementById(targetField);
      if (field) {
        field.value = canonicalArea;
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }

    // Leaflet map flyTo and pulse highlight
    if (mapInstance && targetCoords && targetCoords[0] && targetCoords[1]) {
      try {
        mapInstance.flyTo(targetCoords, 15, {
          animate: true,
          duration: 1.2
        });

        if (landmarkHighlightMarker) {
          mapInstance.removeLayer(landmarkHighlightMarker);
          landmarkHighlightMarker = null;
        }

        const iconHtml = (landmarkObj && landmarkObj.icon) ? landmarkObj.icon : '📍';
        const pulseIcon = L.divIcon({
          className: 'custom-pulse-pin-wrapper',
          html: `
            <div class="landmark-pulse-container">
              <span class="landmark-pulse-ring"></span>
              <div class="landmark-pulse-core">${iconHtml}</div>
            </div>
          `,
          iconSize: [44, 44],
          iconAnchor: [22, 22]
        });

        landmarkHighlightMarker = L.marker(targetCoords, { icon: pulseIcon }).addTo(mapInstance);
        const tipText = (landmarkObj && landmarkObj.tip) ? landmarkObj.tip : 'Repère Douala sélectionné';
        landmarkHighlightMarker.bindPopup(`
          <div style="text-align:left;padding:2px;">
            <strong style="color:#0f172a;font-size:0.92rem;">${landmarkName || canonicalArea}</strong><br>
            <span style="font-size:0.75rem;color:#64748b;">${tipText}</span>
          </div>
        `).openPopup();

        setTimeout(() => {
          if (landmarkHighlightMarker) {
            mapInstance.removeLayer(landmarkHighlightMarker);
            landmarkHighlightMarker = null;
          }
        }, 12000);
      } catch (e) {
        console.warn('Map focus error:', e);
      }
    }
  }

  // Export functions to window
  window.focusDoualaLandmark = focusDoualaLandmark;
  window.MboaLiftMap = {
    coords: DOUALA_COORDS,
    landmarks: DOUALA_LANDMARKS,
    focusLandmark: focusDoualaLandmark
  };

})();
