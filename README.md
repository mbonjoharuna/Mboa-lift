# MboaLift — Douala Mobility 🇨🇲

<p align="center">
  <img src="static/icons/mboalift-full-logo.svg" alt="MboaLift Logo" width="460">
  <br>
  <strong>Theme:</strong> Re-invent Douala's Ride | <strong>Challenge:</strong> School Coding Challenge (Team of 5)
</p>

---

## 🌟 1. Project Vision: Re-inventing Douala's Ride

In **Douala, Cameroon**, urban mobility is unique, fast-paced, and fraught with daily challenges:
- **Dense Traffic Bottlenecks:** Pont sur le Wouri (crossing between Bonabéri and the city center), Carrefour Ndokoti, Rond-Point Deido, and PK8–14.
- **Two Dominant Modes of Transport:**
  1. 🏍️ **Bendskin (Moto-Taxis):** Fast, nimble, slaloms through stalled car traffic, ideal for urgent solo trips.
  2. 🚕 **Taxi Jaune (Shared Yellow Cabs):** The cultural staple of Douala for multi-passenger trips and shopping, but vulnerable to gridlock.
  3. 🚗 **Voiture Confort (VIP Privé):** For business in Bonanjo, airport shuttles, and night travel.
- **Cash & Payment Realities:** Cameroon runs on **MTN Mobile Money (MoMo)** and **Orange Money**. Physical cash haggling ("discussion de monnaie") causes frequent conflicts.
- **Passenger Safety:** Unregistered vehicles and night rides carry safety concerns for riders.

**MboaLift** ("Mboa" = *Homeland / Cameroon* in local parlance) reinvents Douala's urban transport by digitizing local taxi and bendskin culture with:
1. **Multi-Mode Booking:** Riders toggle between **Bendskin Moto (-30% econ)**, **Taxi Jaune**, and **Voiture Confort**.
2. **15 Authentic Douala Hubs:** Covering Akwa, Bonanjo, Bonabéri, Ndokoti, Deido, Bonapriso, Aéroport, Japoma, and more.
3. **Dual Mobile Money Gateway:** Native support for both **MTN MoMo** (*126#) and **Orange Money** (*150#) with auto-detection.
4. **Safety & Social Innovation:** One-click **"Partager mon trajet"** (WhatsApp trip sharing) sending driver identity and live ride ID to relatives.
5. **Urban Carpooling (Shared Rides):** Real-time passenger matching for shared yellow cabs along identical routes.
6. **Local AI Mobility Assistant:** Fluent in English, French, and local Camfranglais, advising on Douala traffic, bridge rush hours, and fares.

---

## 🛠️ 2. Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.8+ / Flask** | Lightweight backend, route controllers, session handling |
| **MySQL (MariaDB)** | Relational data persistence with foreign keys and unique constraints |
| **HTML5 & CSS3** | Custom mobile-responsive UI (pure CSS, no heavy frameworks) |
| **Vanilla JavaScript** | Instant dynamic fare calculator, operator detection, asynchronous chatbot |
| **MTN MoMo & Orange Money** | Integrated Cameroon Mobile Money gateway service |
| **MboaBot AI Assistant** | Local rule-based AI with Douala traffic knowledge + optional LLM API fallback |
| **Werkzeug Security** | High-security PBKDF2 password hashing |

---

## 📂 3. Project Structure

```
Mboa lift/
├── app.py                      # Core Flask application (all routes, validation & business logic)
├── database.sql                # Complete MySQL schema & tables
├── requirements.txt            # Python dependencies
├── .env.example                # Configuration template
├── .env                        # Local environment configuration
├── README.md                   # This project guide
│
├── services/
│   ├── payment_service.py      # Dual MTN MoMo & Orange Money gateway service
│   └── ai_service.py           # Douala mobility AI assistant (traffic, routes, fares)
│
├── templates/
│   ├── base.html               # Shared layout, navigation, brand mark, floating chatbot
│   ├── index.html              # Landing page featuring Douala transport modes & logo
│   ├── register.html           # Passenger registration
│   ├── login.html              # Passenger authentication
│   ├── dashboard.html          # Rider dashboard with pending MoMo/OM payment triggers
│   ├── request_ride.html       # Ride request with Bendskin/Taxi picker & traffic alerts
│   ├── shared_rides.html       # Carpooling / shared rides matching
│   ├── my_rides.html           # Rider ride history, WhatsApp safety share, cancellation
│   ├── payment.html            # Mobile Money checkout (MTN & Orange operator switcher)
│   ├── payments.html           # Transaction ledger with gateway status verification
│   ├── ai_assistant.html       # Dedicated urban mobility assistant page
│   ├── rate_ride.html          # 1-to-5 star rating and feedback
│   ├── profile.html            # User account details
│   ├── admin/
│   │   ├── login.html          # Admin secure portal login
│   │   ├── dashboard.html      # Fleet statistics, revenue, and ride tracking
│   │   ├── users.html          # Rider user management
│   │   ├── rides.html          # Dispatch and ride status controls
│   │   └── payments.html       # Mobile Money payment supervision
│   └── driver/
│       ├── register.html       # Driver onboarding with vehicle category selection
│       ├── login.html          # Driver authentication
│       ├── dashboard.html      # Driver earnings (XAF) and active trips overview
│       ├── available_rides.html# Direct dispatch board for free drivers
│       ├── my_rides.html       # Accepted trips management (Start, Complete, Cancel)
│       └── status.html         # Location and free/busy availability toggle
│
└── static/
    ├── css/style.css           # Pure responsive stylesheet & Douala theme
    ├── js/script.js            # Real-time fare calculation, form validation & chat UI
    ├── js/i18n.js              # Bilingual English / French client-side switcher
    ├── images/
    │   └── mboalift_logo.jpg   # Official high-resolution brand logo
    └── icons/
        ├── mboalift-mark.svg   # Scalable vector app icon squircle
        ├── mboalift-full-logo.svg # Horizontal full vector branding
        └── favicon.svg         # Crisp browser tab icon
```

---

## ⚡ 4. Setup & Installation

### 4.1 Prerequisites
- Python 3.8 or higher (`py` launcher on Windows or `python3`)
- MySQL Server (XAMPP, WampServer, or native MySQL 5.7/8.x)

### 4.2 Installation

```bash
# 1. Clone or navigate into the directory
cd "Mboa lift"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file (auto-configured for local MySQL)
cp .env.example .env

# 4. Initialize Database
# MboaLift auto-provisions the database on first run if MySQL is running!
# Or manually import:
mysql -u root -p < database.sql

# 5. Run the application
py app.py       # (or: python app.py)
```

Open your browser at: **http://127.0.0.1:5000**

Default Administrator Credentials:
- **Username:** `admin`
- **Password:** `admin123`

---

## 🚖 5. Douala Transportation Modes & Fares

MboaLift calculates transparent fares based on Douala's geography and chosen vehicle:

| Mode | Vehicle | Capacity | Rate Factor | Ideal Scenario |
|------|---------|----------|-------------|----------------|
| **Bendskin** | Moto-Taxi (Bajaj, Sanili) | 1 Passenger | **0.7x** (-30%) | Rush hours, crossing Pont du Wouri, avoiding Ndokoti gridlock |
| **Taxi Jaune** | Shared Yellow Cab | 1–4 Passengers | **1.0x** (Standard) | Standard intra-city trips, market runs, shared rides |
| **Voiture Confort** | Private AC Car | 1–4 Passengers | **1.8x** (VIP) | Airport shuttles, business meetings in Bonanjo, night rides |

*All fares are automatically rounded to the nearest 50 XAF to mirror authentic cash and MoMo transactions.*

---

## 💳 6. Mobile Money Flow (Cameroon)

1. Rider requests a ride and selects vehicle type.
2. An available driver accepts the ride.
3. Rider clicks **Payer MoMo / OM** on their dashboard.
4. The app auto-detects the operator based on the telephone prefix:
   - **MTN MoMo:** `67X XXX XXX`, `68X XXX XXX`, `650-654 XXX XXX`
   - **Orange Money:** `69X XXX XXX`, `655-659 XXX XXX`
5. The payment service initiates an USSD push simulation / gateway call.
6. A unique transaction reference (`TXN-MBOA-XXXX`) is assigned.
7. Rider or Admin clicks **Vérifier** on the Payments page to confirm gateway settlement into `SUCCESSFUL`.
8. Driver receives credited earnings upon trip completion.

---

## 👥 7. Team of 5 — Defense & Responsibilities

| Student | Dedicated Role | Focus Areas |
|---------|----------------|-------------|
| **Student 1** | **Backend Architecture & Routes** | `app.py`, Session decorators, Route controllers, Status transitions |
| **Student 2** | **Database & Data Modeling** | `database.sql`, Schema migrations, Foreign keys, Auto-provisioning |
| **Student 3** | **Frontend UI & Responsive Design** | `templates/`, `static/css/style.css`, Vehicle mode cards, Mobile PWA |
| **Student 4** | **JavaScript & Real-time Logic** | `script.js`, Live fare calculator, Operator detection, Bilingual i18n |
| **Student 5** | **Services, Security & Testing** | `payment_service.py`, `ai_service.py`, Safety trip sharing, Test suite |

---

## 🎓 8. Teacher & Jury Defense Cheat Sheet (Q&A)

**Q: How does MboaLift specifically solve Douala's mobility crisis?**  
*A: Unlike generic taxi apps, MboaLift integrates the Bendskin moto-taxi culture directly alongside yellow cabs, allowing commuters to dodge legendary traffic jams on the Wouri Bridge and at Ndokoti, while providing transparent fixed pricing and digital Mobile Money payment to eliminate currency disputes.*

**Q: Why don't you use Google Maps GPS tracking?**  
*A: Mobile data in Douala can be intermittent and battery-intensive. By organizing Douala into known popular hubs (Akwa, Bonanjo, Deido, Bonabéri, etc.) with verified driver availability, MboaLift runs ultra-fast, offline-resilient, and costs 0 CFA in third-party map API fees.*

**Q: How do you protect against payment fraud?**  
*A: The customer's mobile PIN is never requested or stored by MboaLift. Transactions are handled via server-side asynchronous status checks, and a transaction is never marked SUCCESSFUL without gateway confirmation.*

**Q: How does the AI Assistant assist Douala commuters?**  
*A: MboaBot understands Douala traffic patterns (e.g. rush hours on the Wouri Bridge), explains price differences between Bendskins and Yellow Cabs, understands local Camfranglais terms ("dépôt", "tronçon", "bendskin"), and guides users on safety.*

**Q: What is the safety innovation for passengers?**  
*A: The "Partager mon trajet" feature generates an instant WhatsApp message with the ride ID, driver name, phone number, and route, enabling riders to reassure their loved ones immediately upon entering the vehicle.*

---

&copy; 2026 **MboaLift Team** — Reinventing Douala's Ride 🇨🇲
