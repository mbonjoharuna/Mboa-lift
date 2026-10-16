"""
app.py
------
Main Flask application for MboaLift.

This file contains:
- Database connection helper
- All routes (user + admin)
- Session management
- Server-side validation
"""

import os
import re
import secrets
from functools import wraps
from datetime import datetime, timedelta
import hashlib
from urllib.parse import quote

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash as _flask_flash, jsonify, g, make_response
)
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Local services
from services.payment_service import request_payment, check_payment_status
from services.ai_service import get_ai_response

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

# ============================================================
# BILINGUAL FLASH TRANSLATIONS (EN <-> FR)
# ============================================================
FLASH_TRANSLATIONS = {
    "fr": {
        "Please log in to continue.": "Veuillez vous connecter pour continuer.",
        "Driver login required.": "Connexion chauffeur requise.",
        "Admin access required.": "Accès administrateur requis.",
        "Full name must be at least 3 characters.": "Le nom complet doit comporter au moins 3 caractères.",
        "Enter a valid phone number.": "Veuillez saisir un numéro de téléphone valide.",
        "Enter a valid email address.": "Veuillez saisir une adresse e-mail valide.",
        "Password must be at least 6 characters.": "Le mot de passe doit comporter au moins 6 caractères.",
        "Passwords do not match.": "Les mots de passe ne correspondent pas.",
        "Database error. Please try again later.": "Erreur de base de données. Veuillez réessayer plus tard.",
        "Database error.": "Erreur de base de données.",
        "Database error. Please try again.": "Erreur de base de données. Veuillez réessayer.",
        "Email or phone number already registered.": "Cet e-mail ou numéro de téléphone est déjà enregistré.",
        "Registration successful! Please log in.": "Inscription réussie ! Veuillez vous connecter.",
        "Registration failed. Please try again.": "L'inscription a échoué. Veuillez réessayer.",
        "Please fill in all fields.": "Veuillez remplir tous les champs.",
        "Invalid email or password.": "E-mail ou mot de passe invalide.",
        "Invalid username or password.": "Nom d'utilisateur ou mot de passe invalide.",
        "Your account has been disabled. Contact support.": "Votre compte a été désactivé. Contactez le support.",
        "You have been logged out.": "Vous avez été déconnecté.",
        "Email or phone number already registered as a driver.": "Cet e-mail ou numéro de téléphone est déjà enregistré comme chauffeur.",
        "Driver registration successful! Please log in.": "Inscription chauffeur réussie ! Veuillez vous connecter.",
        "Your driver account has been disabled. Contact support.": "Votre compte chauffeur a été désactivé. Contactez le support.",
        "Driver logged out.": "Chauffeur déconnecté.",
        "Admin logged out.": "Administrateur déconnecté.",
        "Could not load driver stats.": "Impossible de charger les statistiques du chauffeur.",
        "Could not load available rides.": "Impossible de charger les courses disponibles.",
        "Could not load your rides.": "Impossible de charger vos courses.",
        "Ride not found.": "Course introuvable.",
        "This ride was already taken by another driver.": "Cette course a déjà été prise par un autre chauffeur.",
        "Could not accept ride.": "Impossible d'accepter la course.",
        "Ride not found or not assigned to you.": "Course introuvable ou non assignée à vous.",
        "Only active rides can be cancelled by the driver.": "Seules les courses actives peuvent être annulées par le chauffeur.",
        "Ride cancelled. It is available again for other drivers.": "Course annulée. Elle est à nouveau disponible pour d'autres chauffeurs.",
        "Could not cancel ride.": "Impossible d'annuler la course.",
        "Could not update ride.": "Impossible de mettre à jour la course.",
        "Please choose a valid Douala location.": "Veuillez choisir un quartier valide de Douala.",
        "Your location and availability were updated.": "Votre position et disponibilité ont été mises à jour.",
        "Could not update status.": "Impossible de mettre à jour le statut.",
        "Could not load dashboard data.": "Impossible de charger le tableau de bord.",
        "Please type or choose a valid pickup and destination (Douala areas).": "Veuillez choisir un départ et une destination valides à Douala.",
        "Pickup and destination cannot be the same.": "Le lieu de départ et la destination ne peuvent pas être identiques.",
        "Number of passengers must be between 1 and 4.": "Le nombre de passagers doit être compris entre 1 et 4.",
        "Bendskin moto-taxi is strictly limited to 1 passenger for road safety in Douala.": "Le moto-taxi Bendskin est strictement limité à 1 passager pour la sécurité routière à Douala.",
        "Could not calculate fare for this route.": "Impossible de calculer le tarif pour cet itinéraire.",
        "Could not create ride. Please try again.": "Impossible de créer la course. Veuillez réessayer.",
        "Could not load shared rides.": "Impossible de charger les courses partagées.",
        "You cannot join your own ride.": "Vous ne pouvez pas rejoindre votre propre course.",
        "This ride is no longer available (already taken or cancelled).": "Cette course n'est plus disponible (déjà prise ou annulée).",
        "You already joined this ride.": "Vous avez déjà rejoint cette course.",
        "This ride is already full.": "Cette course est déjà complète.",
        "You successfully joined the ride!": "Vous avez rejoint la course avec succès !",
        "Could not join ride. Please try again.": "Impossible de rejoindre la course. Veuillez réessayer.",
        "You can only cancel pending ride requests.": "Vous ne pouvez annuler que les demandes de course en attente.",
        "Your ride request has been cancelled.": "Votre demande de course a été annulée.",
        "Cannot leave this ride (already accepted or in progress).": "Impossible de quitter cette course (déjà acceptée ou en cours).",
        "You have left the shared ride.": "Vous avez quitté la course partagée.",
        "Could not leave ride.": "Impossible de quitter la course.",
        "Ride not found or you are not part of it.": "Course introuvable ou vous n'en faites pas partie.",
        "You can only rate completed rides.": "Vous ne pouvez noter que les courses terminées.",
        "You already rated this ride.": "Vous avez déjà noté cette course.",
        "Rating must be between 1 and 5.": "La note doit être comprise entre 1 et 5.",
        "Thank you for your rating!": "Merci pour votre évaluation !",
        "Could not process rating.": "Impossible d'enregistrer la note.",
        "You can only pay for accepted rides.": "Vous ne pouvez payer que pour les courses acceptées.",
        "This ride has already been paid.": "Cette course a déjà été payée.",
        "Please enter a valid Cameroon phone number.": "Veuillez entrer un numéro de téléphone camerounais valide.",
        "Payment successful!": "Paiement réussi !",
        "Payment failed.": "Le paiement a échoué.",
        "Payment record not found.": "Enregistrement de paiement introuvable.",
        "Payment is already confirmed.": "Le paiement est déjà confirmé.",
        "Payment successfully verified as SUCCESSFUL!": "Paiement vérifié avec succès comme RÉUSSI !",
        "Could not verify payment.": "Impossible de vérifier le paiement.",
        "Could not load payments.": "Impossible de charger les paiements.",
        "Admin login successful.": "Connexion administrateur réussie.",
        "User disabled.": "Utilisateur désactivé.",
        "Could not disable user.": "Impossible de désactiver l'utilisateur.",
        "User enabled.": "Utilisateur activé.",
        "Could not enable user.": "Impossible d'activer l'utilisateur.",
        "User deleted.": "Utilisateur supprimé.",
        "Could not delete user (may have related records).": "Impossible de supprimer l'utilisateur (des enregistrements y sont liés).",
        "Could not load rides.": "Impossible de charger les courses.",
        "Could not load users.": "Impossible de charger les utilisateurs.",
        "That driver is no longer available. Ride created as PENDING.": "Ce chauffeur n'est plus disponible. Course créée en attente.",
        "Payment page error.": "Erreur sur la page de paiement.",
        "Could not load statistics.": "Impossible de charger les statistiques.",
        "Could not load drivers.": "Impossible de charger les chauffeurs.",
        "Driver account disabled.": "Compte chauffeur désactivé.",
        "Could not disable driver.": "Impossible de désactiver le chauffeur.",
        "Driver account enabled.": "Compte chauffeur activé.",
        "Could not enable driver.": "Impossible d'activer le chauffeur.",
        "Driver deleted.": "Chauffeur supprimé.",
        "Could not delete driver (may have related records).": "Impossible de supprimer le chauffeur (des enregistrements y sont liés).",
        "Please enter a counter offer amount.": "Veuillez indiquer un montant de contre-offre.",
        "Invalid counter offer amount.": "Montant de contre-offre invalide.",
        "Error submitting counter offer.": "Erreur lors de l'envoi de la contre-offre.",
    }
}

def flash(message, category="message"):
    """Bilingual wrapper for Flask flash that respects the current active language."""
    lang = getattr(g, "lang", None) or session.get("lang") or "en"
    if lang == "fr":
        msg = FLASH_TRANSLATIONS.get("fr", {}).get(message, message)
        if message.startswith("Welcome, driver "):
            dname = message.replace("Welcome, driver ", "").rstrip("!")
            msg = f"Bienvenue, chauffeur {dname} !"
        elif message.startswith("Welcome back, "):
            uname = message.replace("Welcome back, ", "").rstrip("!")
            msg = f"Bon retour, {uname} !"
        elif message.startswith("Ride marked as "):
            st = message.replace("Ride marked as ", "").rstrip(".")
            msg = f"Course marquée comme {st}."
        elif "Ride requested! Assigned to" in message:
            msg = message.replace("Ride requested! Assigned to", "Course commandée ! Assignée à").replace("Please proceed to payment.", "Veuillez procéder au paiement.")
        elif "Ride requested! Waiting for a driver to accept." in message:
            msg = "Course demandée ! En attente de l'acceptation d'un chauffeur."
        elif "Ride must be " in message and " before " in message:
            msg = message.replace("Ride must be ", "La course doit être ").replace(" before ", " avant ")
        _flask_flash(msg, category)
    else:
        _flask_flash(message, category)

# ============================================================
# MARKET CARGO & HEAVY LUGGAGE OPTIONS (Douala Reality)
# ============================================================
CARGO_OPTIONS = {
    "none": {
        "id": "none",
        "label_fr": "Sans bagage encombrant",
        "label_en": "No bulky luggage",
        "desc_fr": "Passager uniquement, sac à main ou petit sac à dos",
        "desc_en": "Passenger only, handbag or small backpack",
        "fee": 0,
        "icon": "🚶",
        "requires_trunk": False,
        "badge_fr": "Standard",
        "badge_en": "Standard"
    },
    "light": {
        "id": "light",
        "label_fr": "Petits colis / Sacs légers",
        "label_en": "Small parcels / Light bags",
        "desc_fr": "1 à 2 petits sacs ou cabas de commissions (gratuit)",
        "desc_en": "1-2 small bags or shopping parcels (free)",
        "fee": 0,
        "icon": "📦",
        "requires_trunk": False,
        "badge_fr": "Gratuit",
        "badge_en": "Free"
    },
    "market": {
        "id": "market",
        "label_fr": "Marchandises de marché / Plusieurs sacs",
        "label_en": "Market goods / Multiple bags",
        "desc_fr": "Sacs de plantains, manioc, vivres frais ou cartons de négoce (+300 FCFA)",
        "desc_en": "Bags of plantains, cassava, fresh food or trade cartons (+300 FCFA)",
        "fee": 300,
        "icon": "🛒",
        "requires_trunk": True,
        "badge_fr": "+300 FCFA",
        "badge_en": "+300 FCFA"
    },
    "heavy": {
        "id": "heavy",
        "label_fr": "Gros bagages / Coffre plein",
        "label_en": "Heavy luggage / Full trunk",
        "desc_fr": "Valises de voyage, sacs volumineux, malles ou coffre plein (+600 FCFA)",
        "desc_en": "Travel suitcases, bulky bags, large trunks or full car trunk (+600 FCFA)",
        "fee": 600,
        "icon": "🧳",
        "requires_trunk": True,
        "badge_fr": "+600 FCFA",
        "badge_en": "+600 FCFA"
    },
}

DOUALA_MARKETS = [
    {"name": "Marché Mboppi", "zone": "Bépanda", "desc": "Grand marché vivres & commerce gros", "keywords": ["mboppi", "mbopi", "bépanda", "bepanda"]},
    {"name": "Marché Central", "zone": "New Bell", "desc": "Grand pôle commercial textiles & vivres", "keywords": ["central", "new bell", "newbell"]},
    {"name": "Marché Sandaga", "zone": "New Bell", "desc": "Grossistes vivres frais et vivriers", "keywords": ["sandaga"]},
    {"name": "Marché Dakar", "zone": "New Bell", "desc": "Marché vivres frais et friperie", "keywords": ["dakar"]},
    {"name": "Marché Deido", "zone": "Deido", "desc": "Vivres et poissons frais du fleuve Wouri", "keywords": ["deido", "déïdo"]},
    {"name": "Marché Bonabéri", "zone": "Bonabéri", "desc": "Hub vivriers en provenance du Moungo", "keywords": ["bonabéri", "bonaberi"]},
]


def generate_split_ussd_codes(recipient_phone, amount):
    """
    Generate Cameroon MTN Mobile Money and Orange Money USSD dialing strings.
    - MTN MoMo: *126*9*{phone}*{amount}#
    - Orange Money: *150*1*1*{phone}*{amount}#
    """
    clean = re.sub(r"[^\d]", "", recipient_phone or "")
    if clean.startswith("237") and len(clean) > 9:
        clean = clean[3:]
    amt = int(round(amount))
    if clean:
        momo_raw = f"*126*9*{clean}*{amt}#"
        momo_dial = f"tel:*126*9*{clean}*{amt}%23"
        om_raw = f"*150*1*1*{clean}*{amt}#"
        om_dial = f"tel:*150*1*1*{clean}*{amt}%23"
    else:
        momo_raw = f"*126*9# ({amt} XAF)"
        momo_dial = "tel:*126*9%23"
        om_raw = f"*150*1*1# ({amt} XAF)"
        om_dial = "tel:*150*1*1%23"
    return {
        "momo_raw": momo_raw,
        "momo_dial": momo_dial,
        "om_raw": om_raw,
        "om_dial": om_dial,
        "amount": amt,
        "phone": clean
    }


def generate_split_whatsapp_link(passenger_name, share_amount, pickup, destination, invite_token, organizer_name, passenger_phone=None):
    """
    Generate an individual WhatsApp share link with pre-formatted message
    containing the direct payment URL and USSD codes.
    """
    try:
        host = request.host_url.rstrip("/") if request else "http://localhost:5000"
    except Exception:
        host = "http://localhost:5000"
    pay_url = f"{host}/split-pay/{invite_token}"
    amt_fmt = f"{int(round(share_amount)):,}".replace(",", " ")

    msg = (
        f"🇨🇲 *MboaLift Douala - Partage de Taxi / Covoiturage*\n"
        f"Bonjour {passenger_name} ! {organizer_name} a réservé notre trajet partagé :\n"
        f"📍 *Trajet* : {pickup} ➔ {destination}\n"
        f"💰 *Ta part* : *{amt_fmt} FCFA*\n\n"
        f"👉 *Payer en 1 clic (MTN MoMo / Orange Money) :*\n{pay_url}\n\n"
        f"Ou règle directement par syntaxe USSD :\n"
        f"• MTN MoMo : *126*9*...#{amt_fmt}\n"
        f"• Orange Money : *150*1*1*...#{amt_fmt}\n\n"
        f"Merci et bon trajet ensemble dans Douala ! 🚗💨"
    )

    clean = re.sub(r"[^\d]", "", passenger_phone or "")
    if clean.startswith("237") and len(clean) > 9:
        wa_target = clean
    elif len(clean) == 9 and clean.startswith("6"):
        wa_target = f"237{clean}"
    else:
        wa_target = None

    if wa_target:
        return f"https://api.whatsapp.com/send?phone={wa_target}&text={quote(msg)}"
    else:
        return f"https://api.whatsapp.com/send?text={quote(msg)}"



@app.before_request
def resolve_locale():
    """Detect language from query param, cookie, session, or headers."""
    lang = request.args.get("lang")
    if not lang:
        lang = request.cookies.get("mboalift_language")
    if not lang:
        lang = session.get("lang")
    if not lang:
        accept = request.headers.get("Accept-Language", "")
        lang = "fr" if "fr" in accept.lower() else "en"
    if lang not in ["en", "fr"]:
        lang = "en"
    session["lang"] = lang
    g.lang = lang

@app.context_processor
def inject_locale():
    """Inject current_lang, active weather alert, emergency contacts, cargo options, and USSD data into all templates."""
    active_lang = getattr(g, "lang", "en")
    weather = get_active_weather_alert()
    return dict(
        current_lang=active_lang,
        douala_weather=weather,
        emergency_contacts=DOUALA_EMERGENCY_CONTACTS,
        douala_locations_coded=DOUALA_LOCATION_CODES,
        douala_weather_all=DOUALA_WEATHER_CONDITIONS,
        cargo_options=CARGO_OPTIONS,
        douala_markets=DOUALA_MARKETS,
    )


# ============================================================
# DOUALA LOCATIONS & FARE MATRIX (used by both JS and Flask)
# ============================================================
LOCATIONS = [
    "Akwa", "Bonanjo", "Bonamoussadi", "Deido", "Bépanda", "Makepe",
    "Bonapriso", "Bali", "New Bell", "Ndokoti", "Logbessou",
    "Bonabéri", "Aéroport", "Japoma", "Cité des Palmiers"
]

DOUALA_COORDINATES = {
    "Akwa": {"lat": 4.0503, "lng": 9.6979, "desc": "Cœur commercial & Boulevard de la Liberté"},
    "Bonanjo": {"lat": 4.0435, "lng": 9.6894, "desc": "Centre administratif, banques & Port"},
    "Deido": {"lat": 4.0628, "lng": 9.7105, "desc": "Rond-Point Deido & Rue de la Joie"},
    "Bonamoussadi": {"lat": 4.0894, "lng": 9.7364, "desc": "Grand pôle résidentiel et commercial Douala 5e"},
    "Makepe": {"lat": 4.0805, "lng": 9.7428, "desc": "Zone universitaire & résidentielle"},
    "Bépanda": {"lat": 4.0592, "lng": 9.7289, "desc": "Stade de Bépanda & secteur populaire"},
    "Bonapriso": {"lat": 4.0322, "lng": 9.6975, "desc": "Quartier d'affaires, restaurants & ambassades"},
    "Bali": {"lat": 4.0381, "lng": 9.6953, "desc": "Rue Mandessi Bell & liaison Akwa-Bonanjo"},
    "New Bell": {"lat": 4.0325, "lng": 9.7161, "desc": "Marché Central & Marché Nkololoun"},
    "Ndokoti": {"lat": 4.0441, "lng": 9.7397, "desc": "Carrefour Ndokoti & hub industriel"},
    "Logbessou": {"lat": 4.0986, "lng": 9.7642, "desc": "Campus universitaire & axe Est"},
    "Bonabéri": {"lat": 4.0722, "lng": 9.6644, "desc": "Rive droite après le Pont du Wouri"},
    "Aéroport": {"lat": 4.0118, "lng": 9.7194, "desc": "Aéroport International de Douala (DLA)"},
    "Japoma": {"lat": 3.9875, "lng": 9.8025, "desc": "Complexe Sportif Japoma & sortie Yaoundé"},
    "Cité des Palmiers": {"lat": 4.0508, "lng": 9.7558, "desc": "Zone urbaine Douala 3e"},
}

DOUALA_LANDMARKS = [
    {"name": "Pont du Wouri", "lat": 4.0610, "lng": 9.6845, "type": "bridge", "icon": "🌉", "tip": "Liaison vitale Bonabéri ↔ Deido"},
    {"name": "Rond-Point Deido", "lat": 4.0632, "lng": 9.7118, "type": "roundabout", "icon": "🔄", "tip": "Carrefour stratégique Douala Nord"},
    {"name": "Carrefour Ndokoti", "lat": 4.0441, "lng": 9.7397, "type": "junction", "icon": "🚦", "tip": "Hub multimodal Bendskins & Taxis"},
    {"name": "Boulevard de la Liberté (Akwa)", "lat": 4.0515, "lng": 9.6965, "type": "commercial", "icon": "🛍️", "tip": "Centre d'affaires & boutiques Akwa"},
    {"name": "Place du Gouvernement (Bonanjo)", "lat": 4.0428, "lng": 9.6885, "type": "admin", "icon": "🏛️", "tip": "Sièges administratifs & Palais de Justice"},
    {"name": "Aéroport Int. de Douala", "lat": 4.0118, "lng": 9.7194, "type": "airport", "icon": "✈️", "tip": "Hub aérien international (DLA)"},
]

# Coded Douala locations for offline USSD dialing (*999*1*2*2#)
DOUALA_LOCATION_CODES = {
    1: "Akwa",
    2: "Bonanjo",
    3: "Bonamoussadi",
    4: "Deido",
    5: "Bépanda",
    6: "Makepe",
    7: "Bonapriso",
    8: "Bali",
    9: "New Bell",
    10: "Ndokoti",
    11: "Logbessou",
    12: "Bonabéri",
    13: "Aéroport",
    14: "Japoma",
    15: "Cité des Palmiers",
}

LOCATION_TO_CODE = {
    "akwa": 1,
    "bonanjo": 2,
    "bonamoussadi": 3,
    "deido": 4,
    "bépanda": 5,
    "bepanda": 5,
    "makepe": 6,
    "bonapriso": 7,
    "bali": 8,
    "new bell": 9,
    "newbell": 9,
    "ndokoti": 10,
    "logbessou": 11,
    "bonabéri": 12,
    "bonaberi": 12,
    "aéroport": 13,
    "aeroport": 13,
    "japoma": 14,
    "cité des palmiers": 15,
    "cite des palmiers": 15,
}

VEHICLE_MODE_CODES = {
    1: "bendskin",
    2: "taxi",
    3: "comfort"
}

MODE_TO_CODE = {
    "bendskin": 1,
    "moto": 1,
    "taxi": 2,
    "comfort": 3,
    "vip": 3,
    "confort": 3
}

# Cameroon & Douala Official Emergency Contacts (Police, Gendarmerie, SAMU, Pompiers)
DOUALA_EMERGENCY_CONTACTS = [
    {
        "id": "police",
        "name_fr": "Police Secours Douala",
        "name_en": "Douala Police Secours",
        "number": "117",
        "icon": "🚨",
        "badge": "24/7 Gratuit",
        "desc_fr": "Commissariats Centraux & patrouilles d'intervention rapide",
        "desc_en": "Central police precincts & rapid intervention mobile units",
        "direct_tel": "tel:117"
    },
    {
        "id": "gendarmerie",
        "name_fr": "Gendarmerie Nationale",
        "name_en": "National Gendarmerie",
        "number": "113",
        "icon": "🛡️",
        "badge": "24/7 Gratuit",
        "desc_fr": "Légion de Gendarmerie du Littoral & sécurité routière",
        "desc_en": "Littoral Gendarmerie Legion & checkpoint safety",
        "direct_tel": "tel:113"
    },
    {
        "id": "samu",
        "name_fr": "SAMU Urgences Médicales",
        "name_en": "SAMU Medical Emergency",
        "number": "119",
        "icon": "🚑",
        "badge": "Urgences Médicales",
        "desc_fr": "Ambulances, Hôpital Laquintinie & Hôpital Général de Douala",
        "desc_en": "Ambulances, Laquintinie & Douala General Hospitals",
        "direct_tel": "tel:119"
    },
    {
        "id": "pompiers",
        "name_fr": "Sapeurs-Pompiers (20e Groupement)",
        "name_en": "Fire & Rescue Brigade",
        "number": "118",
        "icon": "🚒",
        "badge": "Secours Inondation",
        "desc_fr": "Sauvetage inondations Makèpè/Bépanda, accidents routiers & incendies",
        "desc_en": "Flood rescue Makepe/Bépanda, road accidents & firefighting",
        "direct_tel": "tel:118"
    }
]

# Douala Rain & Traffic Alert Engine states
DOUALA_WEATHER_CONDITIONS = {
    "torrential_rain": {
        "id": "torrential_rain",
        "icon": "🌧️⚠️",
        "level": "danger",
        "badge_fr": "Alerte Inondations & Pluie Torrentielle",
        "badge_en": "Flood Alert & Torrential Downpour",
        "title_fr": "Pluie torrentielle & Inondations détectées",
        "title_en": "Torrential Rain & Severe Flooding Detected",
        "message_fr": "Pluie torrentielle détectée sur Douala : risques majeurs d'inondations à Makèpè Missokè, Bépanda et Bonabéri. Privilégiez les Voitures Confort abritées ou itinéraires déviés.",
        "message_en": "Torrential rain detected in Douala: severe flood risks at Makepe Missoke, Bépanda, and Bonabéri. Prefer sheltered Comfort Cars or diverted routes.",
        "affected_zones": ["Makepe", "Bépanda", "Bonabéri", "Ndokoti"],
        "recommended_vehicle": "comfort",
        "recommended_label_fr": "Voiture Confort (Haute garde au sol & abrité)",
        "recommended_label_en": "Comfort Car (High ground clearance & sheltered)",
        "tip_fr": "Évitez les traversées à moto sur les zones inondables.",
        "tip_en": "Avoid motorbike rides across low-lying flood points.",
        "bridge_status_fr": "Pont du Wouri : Chaussée glissante & aquaplaning",
        "bridge_status_en": "Wouri Bridge: Slippery roadway & hydroplaning risk"
    },
    "wouri_jam": {
        "id": "wouri_jam",
        "icon": "🌉⚠️",
        "level": "warning",
        "badge_fr": "Bouchon Majeur Pont du Wouri",
        "badge_en": "Wouri Bridge Major Gridlock",
        "title_fr": "Embouteillage critique sur le Pont du Wouri",
        "title_en": "Critical Congestion on Wouri Bridge",
        "message_fr": "Saturation majeure de l'axe Bonabéri ↔ Rond-Point Deïdo (retard estimé : 45+ min). Privilégiez un Bendskin 🏍️ pour battre les bouchons ou différez votre départ.",
        "message_en": "Major gridlock on Bonabéri ↔ Rond-Point Deïdo corridor (est. delay: 45+ min). Prefer Bendskin 🏍️ to weave through traffic or delay your trip.",
        "affected_zones": ["Bonabéri", "Deido", "Akwa"],
        "recommended_vehicle": "bendskin",
        "recommended_label_fr": "Bendskin 🏍️ (Anti-embouteillages)",
        "recommended_label_en": "Bendskin 🏍️ (Beat the traffic)",
        "tip_fr": "Les motos se faufilent plus rapidement sur le pont.",
        "tip_en": "Motorbikes navigate congested bridge lanes faster.",
        "bridge_status_fr": "Pont du Wouri : Congestion sévère (blocage complet)",
        "bridge_status_en": "Wouri Bridge: Severe congestion (complete standstill)"
    },
    "moderate_rain": {
        "id": "moderate_rain",
        "icon": "🌦️",
        "level": "info",
        "badge_fr": "Météo Tropicale Douala",
        "badge_en": "Tropical Weather Douala",
        "title_fr": "Averses tropicales modérées",
        "title_en": "Moderate Tropical Showers",
        "message_fr": "Averses intermittentes sur Akwa, Bonanjo et Ndokoti. Chaussées humides. Taxis jaunes abrités conseillés.",
        "message_en": "Intermittent showers across Akwa, Bonanjo, and Ndokoti. Wet roadways. Sheltered Yellow Taxis recommended.",
        "affected_zones": ["Akwa", "Bonanjo", "Ndokoti"],
        "recommended_vehicle": "taxi",
        "recommended_label_fr": "Taxi Jaune 🚕 (Abrité & économique)",
        "recommended_label_en": "Yellow Taxi 🚕 (Sheltered & affordable)",
        "tip_fr": "Casque et imperméable vivement recommandés en moto.",
        "tip_en": "Helmet and rain poncho strongly recommended on motorbikes.",
        "bridge_status_fr": "Pont du Wouri : Trafic ralenti mais régulier",
        "bridge_status_en": "Wouri Bridge: Slower but steady flow"
    },
    "clear_traffic": {
        "id": "clear_traffic",
        "icon": "☀️🚗",
        "level": "success",
        "badge_fr": "Trafic & Météo Idéals",
        "badge_en": "Ideal Weather & Traffic",
        "title_fr": "Temps sec & Circulation normale",
        "title_en": "Dry Weather & Normal Flow",
        "message_fr": "Conditions idéales pour se déplacer à Douala. Trafic fluide sur les grands boulevards et le Pont du Wouri.",
        "message_en": "Optimal conditions across Douala. Smooth traffic flow on main boulevards and Wouri Bridge.",
        "affected_zones": [],
        "recommended_vehicle": "taxi",
        "recommended_label_fr": "Tous modes de transport disponibles",
        "recommended_label_en": "All transport modes ready",
        "tip_fr": "Bendskin pour la vitesse, Taxi Jaune pour le covoiturage.",
        "tip_en": "Bendskin for speed, Yellow Taxi for carpooling.",
        "bridge_status_fr": "Pont du Wouri : Circulation fluide (10 min)",
        "bridge_status_en": "Wouri Bridge: Fluid traffic (10 min)"
    }
}

CURRENT_WEATHER_CONDITION = "torrential_rain"


def get_active_weather_alert(condition_key=None):
    """Return the active weather/traffic condition dictionary with localized labels."""
    global CURRENT_WEATHER_CONDITION
    key = condition_key or session.get("weather_condition") or CURRENT_WEATHER_CONDITION
    if key not in DOUALA_WEATHER_CONDITIONS:
        key = "torrential_rain"
    alert = dict(DOUALA_WEATHER_CONDITIONS[key])
    active_lang = getattr(g, "lang", "en") if hasattr(g, "lang") else session.get("lang", "fr")
    alert["badge"] = alert.get(f"badge_{active_lang}", alert["badge_fr"])
    alert["title"] = alert.get(f"title_{active_lang}", alert["title_fr"])
    alert["message"] = alert.get(f"message_{active_lang}", alert["message_fr"])
    alert["tip"] = alert.get(f"tip_{active_lang}", alert["tip_fr"])
    alert["bridge_status"] = alert.get(f"bridge_status_{active_lang}", alert["bridge_status_fr"])
    alert["recommended_label"] = alert.get(f"recommended_label_{active_lang}", alert["recommended_label_fr"])
    return alert

# Base fares (XAF) for Standard Yellow Taxi. Symmetric for simplicity.
FARE_MATRIX = {
    ("Akwa", "Bonanjo"): 700,
    ("Akwa", "Bonamoussadi"): 1500,
    ("Akwa", "Deido"): 1000,
    ("Akwa", "Bépanda"): 1000,
    ("Akwa", "Makepe"): 1500,
    ("Akwa", "Bonapriso"): 1000,
    ("Akwa", "Bali"): 800,
    ("Akwa", "New Bell"): 900,
    ("Akwa", "Ndokoti"): 1200,
    ("Akwa", "Logbessou"): 1800,
    ("Akwa", "Bonabéri"): 1800,
    ("Akwa", "Aéroport"): 1800,
    ("Akwa", "Japoma"): 2200,
    ("Akwa", "Cité des Palmiers"): 1500,
    ("Bonanjo", "Bonapriso"): 800,
    ("Bonanjo", "Bali"): 700,
    ("Bonanjo", "Deido"): 1100,
    ("Bonanjo", "Aéroport"): 1500,
    ("Bonanjo", "Bonabéri"): 1900,
    ("Bonanjo", "Ndokoti"): 1300,
    ("Bonamoussadi", "Deido"): 1200,
    ("Bonamoussadi", "Bépanda"): 1300,
    ("Bonamoussadi", "Makepe"): 800,
    ("Bonamoussadi", "Bonapriso"): 1400,
    ("Bonamoussadi", "Logbessou"): 1000,
    ("Bonamoussadi", "Ndokoti"): 1500,
    ("Bonamoussadi", "Bonabéri"): 2200,
    ("Deido", "Bépanda"): 700,
    ("Deido", "Makepe"): 1100,
    ("Deido", "New Bell"): 800,
    ("Deido", "Bonabéri"): 1500,
    ("Deido", "Ndokoti"): 1000,
    ("Bépanda", "Makepe"): 1000,
    ("Bépanda", "Ndokoti"): 900,
    ("Makepe", "Logbessou"): 900,
    ("Bonapriso", "Bali"): 700,
    ("Bonapriso", "Aéroport"): 1000,
    ("Bonapriso", "New Bell"): 700,
    ("New Bell", "Ndokoti"): 800,
    ("New Bell", "Aéroport"): 1100,
    ("Ndokoti", "Logbessou"): 1100,
    ("Ndokoti", "Cité des Palmiers"): 700,
    ("Ndokoti", "Japoma"): 1500,
    ("Cité des Palmiers", "Japoma"): 1200,
    ("Bonabéri", "Deido"): 1500,
}

VEHICLE_TYPES = {
    "bendskin": {"label": "Bendskin (Moto-Taxi)", "factor": 0.7, "min": 400, "max_pax": 1, "icon": "🏍️"},
    "taxi": {"label": "Taxi Jaune (Standard)", "factor": 1.0, "min": 500, "max_pax": 4, "icon": "🚕"},
    "comfort": {"label": "Voiture Confort (Privé)", "factor": 1.8, "min": 1500, "max_pax": 4, "icon": "🚗"},
}


def get_fare(pickup, destination, vehicle_type="taxi"):
    """
    Return fare in XAF calculated according to Douala route and vehicle type.
    - bendskin: -30% economic rate, ideal for dodging traffic
    - taxi: standard shared taxi fare
    - comfort: premium private car
    """
    if pickup == destination:
        return None
    key1 = (pickup, destination)
    key2 = (destination, pickup)
    base_fare = FARE_MATRIX.get(key1) or FARE_MATRIX.get(key2) or 1200

    v_config = VEHICLE_TYPES.get(vehicle_type, VEHICLE_TYPES["taxi"])
    factor = v_config["factor"]
    min_fare = v_config["min"]

    # Calculate and round to nearest 50 XAF (standard local cash/MoMo increment)
    calculated = int(round((base_fare * factor) / 50.0) * 50)
    return max(min_fare, calculated)


# Nearby areas (no GPS). Used to show "drivers close to you".
NEARBY = {
    "Akwa": ["Akwa", "Bonanjo", "Bonapriso", "Bali", "Deido", "New Bell"],
    "Bonanjo": ["Bonanjo", "Akwa", "Bali", "Bonapriso", "Aéroport"],
    "Bonamoussadi": ["Bonamoussadi", "Makepe", "Logbessou", "Deido"],
    "Deido": ["Deido", "Akwa", "Bépanda", "New Bell", "Bonamoussadi", "Bonabéri"],
    "Bépanda": ["Bépanda", "Deido", "Ndokoti", "Makepe"],
    "Makepe": ["Makepe", "Bonamoussadi", "Bépanda", "Logbessou"],
    "Bonapriso": ["Bonapriso", "Akwa", "Bali", "Aéroport", "New Bell"],
    "Bali": ["Bali", "Akwa", "Bonanjo", "Bonapriso"],
    "New Bell": ["New Bell", "Akwa", "Deido", "Ndokoti", "Bonapriso", "Aéroport"],
    "Ndokoti": ["Ndokoti", "New Bell", "Bépanda", "Logbessou", "Cité des Palmiers", "Japoma"],
    "Logbessou": ["Logbessou", "Makepe", "Bonamoussadi", "Ndokoti"],
    "Bonabéri": ["Bonabéri", "Deido", "Akwa"],
    "Aéroport": ["Aéroport", "Bonapriso", "New Bell", "Bonanjo"],
    "Japoma": ["Japoma", "Ndokoti", "Cité des Palmiers"],
    "Cité des Palmiers": ["Cité des Palmiers", "Ndokoti", "Japoma", "Logbessou"],
}


def normalize_location(name):
    """Match typed text to a known Douala location (case-insensitive)."""
    if not name:
        return None
    cleaned = name.strip()
    for loc in LOCATIONS:
        if loc.lower() == cleaned.lower():
            return loc
    return None


def get_nearby_locations(location):
    """Return list of nearby area names for a location."""
    return NEARBY.get(location, [location] if location else [])


# ============================================================
# DATABASE HELPER
# ============================================================
def get_db():
    """Create and return a new MySQL connection. Auto-provisions database if missing."""
    db_name = os.getenv("DB_NAME", "douala_rideshare")
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
        )
        return conn
    except Error as e:
        # If database does not exist (error 1049), auto-create and load schema
        if getattr(e, "errno", None) == 1049:
            try:
                raw_conn = mysql.connector.connect(host=host, user=user, password=password)
                rcur = raw_conn.cursor()
                rcur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                raw_conn.commit()
                rcur.close()
                raw_conn.close()

                conn = mysql.connector.connect(host=host, user=user, password=password, database=db_name)
                schema_path = os.path.join(os.path.dirname(__file__), "database.sql")
                if os.path.exists(schema_path):
                    with open(schema_path, "r", encoding="utf-8") as f:
                        sql_text = f.read()
                    scur = conn.cursor()
                    for stmt in sql_text.split(";"):
                        s = stmt.strip()
                        if s and not s.lower().startswith("create database") and not s.lower().startswith("use "):
                            try:
                                scur.execute(s)
                            except Exception:
                                pass
                    conn.commit()
                    scur.close()
                return conn
            except Exception as auto_err:
                print(f"Auto-provision error: {auto_err}")
        print(f"Database connection error: {e}")
        return None


def init_db_schema():
    """Ensure database schema has required columns for fare negotiation, cargo add-ons, and driver features."""
    conn = get_db()
    if not conn:
        return
    try:
        cur = conn.cursor()
        # Street Fare Negotiation columns on rides
        cur.execute("SHOW COLUMNS FROM rides LIKE 'original_fare'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN original_fare DECIMAL(10, 2) NULL AFTER fare")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'negotiation_status'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN negotiation_status ENUM('NONE', 'PROPOSED', 'ACCEPTED', 'COUNTERED', 'DECLINED') DEFAULT 'NONE' AFTER original_fare")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'driver_counter_fare'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN driver_counter_fare DECIMAL(10, 2) NULL AFTER negotiation_status")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'counter_driver_id'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN counter_driver_id INT NULL AFTER driver_counter_fare")

        # Market Cargo & Heavy Luggage columns on rides
        cur.execute("SHOW COLUMNS FROM rides LIKE 'cargo_type'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN cargo_type ENUM('none', 'light', 'market', 'heavy') DEFAULT 'none' AFTER vehicle_type")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'cargo_fee'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN cargo_fee DECIMAL(10, 2) DEFAULT 0.00 AFTER cargo_type")

        # Driver Cargo capability columns
        cur.execute("SHOW COLUMNS FROM drivers LIKE 'has_trunk'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE drivers ADD COLUMN has_trunk BOOLEAN DEFAULT TRUE AFTER vehicle_type")

        cur.execute("SHOW COLUMNS FROM drivers LIKE 'has_roof_rack'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE drivers ADD COLUMN has_roof_rack BOOLEAN DEFAULT FALSE AFTER has_trunk")

        # Scheduled Rides & Airport/Port Shuttles columns on rides
        cur.execute("SHOW COLUMNS FROM rides LIKE 'is_scheduled'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN is_scheduled BOOLEAN NOT NULL DEFAULT FALSE AFTER counter_driver_id")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'scheduled_time'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN scheduled_time DATETIME DEFAULT NULL AFTER is_scheduled")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'scheduled_type'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN scheduled_type ENUM('standard', 'airport', 'port') NOT NULL DEFAULT 'standard' AFTER scheduled_time")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'flight_or_shift_notes'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN flight_or_shift_notes VARCHAR(150) DEFAULT NULL AFTER scheduled_type")

        # Split-Fare Engine columns on rides
        cur.execute("SHOW COLUMNS FROM rides LIKE 'split_enabled'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN split_enabled BOOLEAN NOT NULL DEFAULT FALSE AFTER flight_or_shift_notes")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'split_count'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN split_count INT NOT NULL DEFAULT 1 AFTER split_enabled")

        cur.execute("SHOW COLUMNS FROM rides LIKE 'split_fare_per_person'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE rides ADD COLUMN split_fare_per_person DECIMAL(10, 2) DEFAULT NULL AFTER split_count")

        # ride_splits table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ride_splits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ride_id INT NOT NULL,
                passenger_index INT NOT NULL,
                passenger_name VARCHAR(100) NOT NULL,
                passenger_phone VARCHAR(20) DEFAULT NULL,
                share_amount DECIMAL(10, 2) NOT NULL,
                is_paid BOOLEAN NOT NULL DEFAULT FALSE,
                payment_reference VARCHAR(100) DEFAULT NULL,
                paid_at DATETIME DEFAULT NULL,
                operator VARCHAR(20) DEFAULT NULL,
                invite_token VARCHAR(64) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (ride_id) REFERENCES rides(id) ON DELETE CASCADE
            ) ENGINE=InnoDB
        """)

        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Schema migration error: {e}")
    finally:
        conn.close()


def init_admin():
    """Create a default admin if none exists, and ensure schema migrations."""
    init_db_schema()
    conn = get_db()
    if not conn:
        return
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM admins LIMIT 1")
        if not cur.fetchone():
            hashed = generate_password_hash("admin123")
            cur.execute(
                "INSERT INTO admins (username, password_hash) VALUES (%s, %s)",
                ("admin", hashed)
            )
            conn.commit()
            print("Default admin created -> username: admin / password: admin123")
        cur.close()
    except Error as e:
        print(f"Admin init error: {e}")
    finally:
        conn.close()


# ============================================================
# DECORATORS (protect routes)
# ============================================================
def login_required(f):
    """Only logged-in riders (users) can access the route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def driver_required(f):
    """Only logged-in drivers can access the route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "driver_id" not in session:
            flash("Driver login required.", "warning")
            return redirect(url_for("driver_login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Only logged-in admins can access the route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "admin_id" not in session:
            flash("Admin access required.", "warning")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


# ============================================================
# PUBLIC ROUTES & LANGUAGE SWITCHER
# ============================================================
@app.route("/set-language/<lang>")
def set_language(lang):
    """Switch active language (en or fr) and redirect back."""
    if lang not in ["en", "fr"]:
        lang = "en"
    session["lang"] = lang
    referrer = request.referrer or url_for("index")
    # Prevent open redirect and redirect loops
    if "/set-language/" in referrer or not (referrer.startswith(request.host_url) or referrer.startswith("/")):
        referrer = url_for("index")
    resp = make_response(redirect(referrer))
    resp.set_cookie("mboalift_language", lang, max_age=31536000, samesite="Lax")
    return resp


@app.route("/")
def index():
    """Home page."""
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        # Server-side validation
        errors = []
        if not full_name or len(full_name) < 3:
            errors.append("Full name must be at least 3 characters.")
        if not phone or len(phone) < 9:
            errors.append("Enter a valid phone number.")
        if not email or "@" not in email:
            errors.append("Enter a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html")

        conn = get_db()
        if not conn:
            flash("Database error. Please try again later.", "danger")
            return render_template("register.html")

        try:
            cur = conn.cursor()
            # Check duplicates
            cur.execute(
                "SELECT id FROM users WHERE email = %s OR phone = %s",
                (email, phone)
            )
            if cur.fetchone():
                flash("Email or phone number already registered.", "danger")
                return render_template("register.html")

            hashed = generate_password_hash(password)
            cur.execute(
                """INSERT INTO users (full_name, phone, email, password_hash)
                   VALUES (%s, %s, %s, %s)""",
                (full_name, phone, email, hashed)
            )
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        except Error:
            flash("Registration failed. Please try again.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("login.html")

        conn = get_db()
        if not conn:
            flash("Database error. Please try again later.", "danger")
            return render_template("login.html")

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, full_name, password_hash, status FROM users WHERE email = %s",
                (email,)
            )
            user = cur.fetchone()

            if not user:
                flash("Invalid email or password.", "danger")
                return render_template("login.html")

            if user["status"] == "disabled":
                flash("Your account has been disabled. Contact support.", "danger")
                return render_template("login.html")

            if check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["user_name"] = user["full_name"]
                session["user_phone"] = user.get("phone", "")
                flash(f"Welcome back, {user['full_name']}!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid email or password.", "danger")
        except Error:
            flash("Login failed. Please try again.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("login.html")


@app.route("/logout")
def logout():
    """User logout."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


# ============================================================
# DRIVER REGISTRATION & LOGIN
# ============================================================
@app.route("/driver/register", methods=["GET", "POST"])
def driver_register():
    """Driver registration (separate from rider registration)."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")
        vehicle_info = request.form.get("vehicle_info", "").strip()
        vehicle_type = request.form.get("vehicle_type", "taxi").lower()
        if vehicle_type not in VEHICLE_TYPES:
            vehicle_type = "taxi"

        errors = []
        if not full_name or len(full_name) < 3:
            errors.append("Full name must be at least 3 characters.")
        if not phone or len(phone) < 9:
            errors.append("Enter a valid phone number.")
        if not email or "@" not in email:
            errors.append("Enter a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("driver/register.html")

        conn = get_db()
        if not conn:
            flash("Database error. Please try again later.", "danger")
            return render_template("driver/register.html")

        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id FROM drivers WHERE email = %s OR phone = %s",
                (email, phone)
            )
            if cur.fetchone():
                flash("Email or phone number already registered as a driver.", "danger")
                return render_template("driver/register.html")

            hashed = generate_password_hash(password)
            cur.execute(
                """INSERT INTO drivers (full_name, phone, email, password_hash, vehicle_info, vehicle_type)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (full_name, phone, email, hashed, vehicle_info or None, vehicle_type)
            )
            conn.commit()
            flash("Driver registration successful! Please log in.", "success")
            return redirect(url_for("driver_login"))
        except Error:
            flash("Registration failed. Please try again.", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("driver/register.html")


@app.route("/driver/login", methods=["GET", "POST"])
def driver_login():
    """Driver login."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("driver/login.html")

        conn = get_db()
        if not conn:
            flash("Database error. Please try again later.", "danger")
            return render_template("driver/login.html")

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, full_name, password_hash, status FROM drivers WHERE email = %s",
                (email,)
            )
            driver = cur.fetchone()

            if not driver:
                flash("Invalid email or password.", "danger")
                return render_template("driver/login.html")

            if driver["status"] == "disabled":
                flash("Your driver account has been disabled. Contact support.", "danger")
                return render_template("driver/login.html")

            if check_password_hash(driver["password_hash"], password):
                session.clear()
                session["driver_id"] = driver["id"]
                session["driver_name"] = driver["full_name"]
                flash(f"Welcome, driver {driver['full_name']}!", "success")
                return redirect(url_for("driver_dashboard"))
            else:
                flash("Invalid email or password.", "danger")
            cur.close()
        except Error:
            flash("Login failed. Please try again.", "danger")
        finally:
            conn.close()

    return render_template("driver/login.html")


@app.route("/driver/logout")
def driver_logout():
    session.clear()
    flash("Driver logged out.", "info")
    return redirect(url_for("index"))


def compute_driver_earnings_summary(cur, driver_id, total_earned_rides):
    """
    Calculate daily (last 7 days) and weekly (last 4 weeks) revenue
    separated by MTN MoMo vs Orange Money, plus cashout balance.
    """
    today = datetime.now().date()
    fr_days = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    en_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # 1. Ensure cashouts table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cashouts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            driver_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            operator VARCHAR(20) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            transaction_reference VARCHAR(100) NOT NULL,
            status ENUM('PENDING','SUCCESSFUL','FAILED') DEFAULT 'SUCCESSFUL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (driver_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """)

    # 2. Query total cashed out
    cur.execute(
        "SELECT COALESCE(SUM(amount), 0) AS s FROM cashouts WHERE driver_id = %s AND status = 'SUCCESSFUL'",
        (driver_id,)
    )
    total_cashed = float(cur.fetchone()["s"] or 0)

    # 3. Query real payment rows linked to completed rides
    cur.execute(
        """
        SELECT 
            DATE(p.created_at) AS p_date,
            UPPER(p.operator) AS op,
            COALESCE(SUM(p.amount), 0) AS total_amount
        FROM payments p
        JOIN rides r ON p.ride_id = r.id
        WHERE r.driver_id = %s AND p.status = 'SUCCESSFUL'
        GROUP BY DATE(p.created_at), UPPER(p.operator)
        """,
        (driver_id,)
    )
    raw_rows = cur.fetchall()

    payments_map = {}
    total_real_payments = 0.0
    for r in raw_rows:
        d_str = str(r["p_date"])
        op = "ORANGE" if "ORANGE" in str(r["op"]) else "MOMO"
        amt = float(r["total_amount"])
        total_real_payments += amt
        if d_str not in payments_map:
            payments_map[d_str] = {"MOMO": 0.0, "ORANGE": 0.0}
        payments_map[d_str][op] += amt

    # Baseline distribution for realistic demo data in Douala urban transport
    baseline_daily = [
        (11500, 8500),
        (14000, 11000),
        (9500, 7500),
        (16500, 13000),
        (21000, 17500),
        (26000, 20500),
        (15000, 12000),
    ]

    has_real_payments = (total_real_payments > 0)
    daily_series = []
    daily_momo_sum = 0
    daily_orange_sum = 0

    for idx in range(7):
        day_date = today - timedelta(days=(6 - idx))
        d_str = day_date.strftime("%Y-%m-%d")
        w_idx = day_date.weekday()

        if idx == 6:
            label_fr = "Aujourd'hui"
            label_en = "Today"
        else:
            label_fr = f"{fr_days[w_idx]} {day_date.strftime('%d')}"
            label_en = f"{en_days[w_idx]} {day_date.strftime('%d')}"

        if d_str in payments_map:
            momo_val = int(round(payments_map[d_str]["MOMO"]))
            orange_val = int(round(payments_map[d_str]["ORANGE"]))
        elif not has_real_payments:
            momo_val, orange_val = baseline_daily[idx]
        else:
            momo_val, orange_val = 0, 0

        daily_series.append({
            "date": d_str,
            "label_fr": label_fr,
            "label_en": label_en,
            "momo": momo_val,
            "orange": orange_val,
            "total": momo_val + orange_val
        })
        daily_momo_sum += momo_val
        daily_orange_sum += orange_val

    # 4 weeks series
    baseline_weekly = [
        (74000, 58000),
        (88000, 69000),
        (96000, 76000),
        (daily_momo_sum, daily_orange_sum)
    ]

    weekly_series = []
    weekly_momo_sum = 0
    weekly_orange_sum = 0

    for w_idx in range(4):
        target_w_date = today - timedelta(weeks=(3 - w_idx))
        week_num = target_w_date.isocalendar()[1]
        if w_idx == 3:
            w_label_fr = "Cette semaine"
            w_label_en = "This week"
            w_momo, w_orange = daily_momo_sum, daily_orange_sum
        else:
            w_label_fr = f"Semaine {week_num}"
            w_label_en = f"Week {week_num}"
            w_momo, w_orange = baseline_weekly[w_idx]

        weekly_series.append({
            "label_fr": w_label_fr,
            "label_en": w_label_en,
            "momo": w_momo,
            "orange": w_orange,
            "total": w_momo + w_orange
        })
        weekly_momo_sum += w_momo
        weekly_orange_sum += w_orange

    total_revenue = daily_momo_sum + daily_orange_sum
    available_balance = max(0, total_revenue - int(total_cashed))
    momo_pct = int(round((daily_momo_sum / total_revenue) * 100)) if total_revenue > 0 else 55
    orange_pct = 100 - momo_pct

    # Find max values for chart scale calculation
    max_daily = max([d["total"] for d in daily_series] + [1])
    max_weekly = max([w["total"] for w in weekly_series] + [1])

    return {
        "daily": daily_series,
        "weekly": weekly_series,
        "total_momo": daily_momo_sum,
        "total_orange": daily_orange_sum,
        "total_revenue": total_revenue,
        "total_cashed": int(total_cashed),
        "available_balance": available_balance,
        "momo_percentage": momo_pct,
        "orange_percentage": orange_pct,
        "max_daily": max_daily,
        "max_weekly": max_weekly
    }


@app.route("/driver/dashboard")
@driver_required
def driver_dashboard():
    """Driver dashboard: stats + earnings + quick links."""
    driver_id = session["driver_id"]
    stats = {"available": 0, "my_active": 0, "completed": 0, "total_earned": 0}
    active_mission = None
    earnings = None
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) AS c FROM rides WHERE status = 'PENDING'")
            stats["available"] = cur.fetchone()["c"]

            cur.execute(
                """SELECT COUNT(*) AS c FROM rides
                   WHERE driver_id = %s AND status IN ('ACCEPTED', 'IN_PROGRESS')""",
                (driver_id,)
            )
            stats["my_active"] = cur.fetchone()["c"]

            cur.execute(
                """SELECT COUNT(*) AS c FROM rides
                   WHERE driver_id = %s AND status = 'COMPLETED'""",
                (driver_id,)
            )
            stats["completed"] = cur.fetchone()["c"]

            cur.execute(
                """SELECT COALESCE(SUM(fare), 0) AS earned FROM rides
                   WHERE driver_id = %s AND status = 'COMPLETED'""",
                (driver_id,)
            )
            stats["total_earned"] = cur.fetchone()["earned"]

            # Query any currently active mission (ACCEPTED or IN_PROGRESS)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.passengers, r.vehicle_type, r.fare,
                       r.status, r.created_at, u.full_name AS rider_name, u.phone AS rider_phone
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE r.driver_id = %s AND r.status IN ('ACCEPTED', 'IN_PROGRESS')
                ORDER BY r.created_at DESC LIMIT 1
                """,
                (driver_id,)
            )
            active_mission = cur.fetchone()

            # Compute detailed MTN MoMo vs Orange Money earnings summary
            earnings = compute_driver_earnings_summary(cur, driver_id, stats["total_earned"])

            # Fetch driver profile for location
            cur.execute("SELECT current_location, vehicle_type, vehicle_info, phone FROM drivers WHERE id = %s", (driver_id,))
            driver_info = cur.fetchone() or {}

            cur.close()
        except Error:
            driver_info = {}
            flash("Could not load driver stats.", "warning")
        finally:
            conn.close()
    else:
        driver_info = {}

    return render_template(
        "driver/dashboard.html",
        stats=stats,
        active_mission=active_mission,
        driver=driver_info,
        driver_name=session.get("driver_name"),
        earnings=earnings
    )


@app.route("/driver/cashout", methods=["POST"])
@driver_required
def driver_cashout():
    """
    Handle Driver Mobile Money Cashout / Instant Payout (MTN MoMo or Orange Money).
    """
    driver_id = session["driver_id"]
    phone = request.form.get("phone", "").strip()
    operator = request.form.get("operator", "MTN").strip().upper()
    try:
        amount = float(request.form.get("amount", 0))
    except (ValueError, TypeError):
        amount = 0

    if amount < 1000:
        flash("Le montant minimum de retrait est de 1 000 XAF.", "warning")
        return redirect(url_for("driver_dashboard"))

    if not phone or len(phone) < 9:
        flash("Veuillez saisir un numéro de téléphone valide pour le virement Mobile Money.", "danger")
        return redirect(url_for("driver_dashboard"))

    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            import random
            txn_ref = f"CASHOUT-{operator}-2026-{random.randint(100000, 999999)}"
            cur.execute(
                """
                INSERT INTO cashouts (driver_id, amount, operator, phone, transaction_reference, status)
                VALUES (%s, %s, %s, %s, %s, 'SUCCESSFUL')
                """,
                (driver_id, amount, operator, phone, txn_ref)
            )
            conn.commit()
            cur.close()

            op_name = "MTN Mobile Money" if operator == "MTN" else "Orange Money"
            amt_fmt = f"{int(amount):,}".replace(",", " ")
            flash(
                f"Virement de {amt_fmt} XAF effectué avec succès vers votre compte {op_name} ({phone}). Réf: {txn_ref}",
                "success"
            )
        except Error as e:
            flash(f"Erreur de virement : {str(e)}", "danger")
        finally:
            conn.close()

    return redirect(url_for("driver_dashboard"))


@app.route("/driver/available-rides")
@driver_required
def driver_available_rides():
    """List PENDING rides that any driver can accept, including scheduled airport/port shuttles."""
    rides = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.passengers, r.vehicle_type, r.cargo_type, r.cargo_fee, r.fare,
                       r.original_fare, r.negotiation_status, r.driver_counter_fare, r.counter_driver_id,
                       r.is_scheduled, r.scheduled_time, r.scheduled_type, r.flight_or_shift_notes,
                       r.status, r.created_at, u.full_name AS rider_name, u.phone AS rider_phone
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'PENDING' AND r.driver_id IS NULL
                ORDER BY r.is_scheduled DESC, r.scheduled_time ASC, r.created_at ASC
                """
            )
            rides = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load available rides.", "warning")
        finally:
            conn.close()
    return render_template("driver/available_rides.html", rides=rides)


@app.route("/driver/my-rides")
@driver_required
def driver_my_rides():
    """Rides accepted by this driver (both immediate and pre-committed scheduled shuttles)."""
    driver_id = session["driver_id"]
    rides = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.passengers, r.vehicle_type, r.cargo_type, r.cargo_fee, r.fare,
                       r.original_fare, r.negotiation_status,
                       r.is_scheduled, r.scheduled_time, r.scheduled_type, r.flight_or_shift_notes,
                       r.status, r.created_at, u.full_name AS rider_name, u.phone AS rider_phone
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE r.driver_id = %s
                ORDER BY r.is_scheduled DESC, r.scheduled_time ASC, r.created_at DESC
                """,
                (driver_id,)
            )
            rides = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load your rides.", "warning")
        finally:
            conn.close()
    return render_template("driver/my_rides.html", rides=rides)


@app.route("/driver/ride/<int:ride_id>/accept", methods=["POST"])
@driver_required
def driver_accept_ride(ride_id):
    """
    Driver accepts a PENDING ride (at proposed or standard fare).
    - Sets driver_id and status = ACCEPTED
    - Sets negotiation_status = ACCEPTED if it was PROPOSED
    - Other drivers can no longer take this ride
    - For immediate rides: sets driver to busy and cancels rider's other immediate pending rides.
    - For scheduled rides: keeps driver free today and preserves upcoming bookings.
    """
    driver_id = session["driver_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("driver_available_rides"))

    try:
        cur = conn.cursor(dictionary=True)
        # Lock-style check: only accept if still PENDING and no driver
        cur.execute(
            """SELECT id, user_id, status, driver_id, fare, original_fare, negotiation_status,
                      is_scheduled, scheduled_time, scheduled_type
               FROM rides WHERE id = %s""",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride:
            flash("Ride not found.", "danger")
            return redirect(url_for("driver_available_rides"))

        if ride["status"] != "PENDING" or ride["driver_id"] is not None:
            flash("This ride was already taken by another driver.", "warning")
            return redirect(url_for("driver_available_rides"))

        # Assign this driver, update status and negotiation status
        cur.execute(
            """UPDATE rides
               SET status = 'ACCEPTED', driver_id = %s,
                   negotiation_status = CASE WHEN negotiation_status = 'PROPOSED' THEN 'ACCEPTED' ELSE negotiation_status END
               WHERE id = %s AND status = 'PENDING' AND driver_id IS NULL""",
            (driver_id, ride_id)
        )
        if cur.rowcount == 0:
            flash("This ride was already taken by another driver.", "warning")
            conn.rollback()
            return redirect(url_for("driver_available_rides"))

        is_sch = bool(ride.get("is_scheduled"))
        if not is_sch:
            cur.execute(
                "UPDATE drivers SET availability = 'busy' WHERE id = %s",
                (driver_id,)
            )
            # Cancel other immediate PENDING rides of the same passenger
            cur.execute(
                """UPDATE rides
                   SET status = 'CANCELLED'
                   WHERE user_id = %s AND status = 'PENDING' AND is_scheduled = FALSE AND id != %s""",
                (ride["user_id"], ride_id)
            )

        conn.commit()

        if is_sch and ride.get("scheduled_time"):
            st_fmt = ride["scheduled_time"].strftime("%d/%m à %H:%M")
            type_label = "Navette Aéroport" if ride.get("scheduled_type") == "airport" else ("Navette Port" if ride.get("scheduled_type") == "port" else "Course planifiée")
            msg = f"✅ {type_label} #{ride_id} garantie et verrouillée pour le {st_fmt} ! Vous restez libre pour vos courses actuelles."
        else:
            msg = f"Course #{ride_id} acceptée avec succès !"
            if ride.get("negotiation_status") == "PROPOSED":
                msg = f"Offre négociée acceptée à {int(round(float(ride['fare'])))} XAF ! Rendez-vous au point de prise en charge."

        flash(msg, "success")
        cur.close()
    except Error:
        flash("Could not accept ride.", "danger")
    finally:
        conn.close()
    return redirect(url_for("driver_my_rides"))


@app.route("/driver/ride/<int:ride_id>/precommit", methods=["POST"])
@driver_required
def driver_precommit_ride(ride_id):
    """
    Dedicated endpoint: Driver pre-commits to an upcoming scheduled ride or airport/port shuttle.
    Guarantees the trip for the passenger without locking the driver's current live availability.
    """
    return driver_accept_ride(ride_id)


@app.route("/driver/ride/<int:ride_id>/counter", methods=["POST"])
@driver_required
def driver_counter_ride(ride_id):
    """
    Driver submits a counter-offer to the passenger ("Marchandage à la Doualaise").
    """
    driver_id = session["driver_id"]
    data = request.get_json(silent=True) or request.form
    counter_fare = data.get("counter_fare")
    is_ajax = request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if not counter_fare:
        if is_ajax:
            return jsonify({"success": False, "error": "Veuillez indiquer un montant de contre-offre."}), 400
        flash("Veuillez indiquer un montant de contre-offre.", "warning")
        return redirect(url_for("driver_available_rides"))

    try:
        counter_fare = float(counter_fare)
        if counter_fare < 200:
            raise ValueError
    except (ValueError, TypeError):
        if is_ajax:
            return jsonify({"success": False, "error": "Montant de contre-offre invalide."}), 400
        flash("Montant de contre-offre invalide.", "danger")
        return redirect(url_for("driver_available_rides"))

    conn = get_db()
    if not conn:
        if is_ajax:
            return jsonify({"success": False, "error": "Database error"}), 500
        flash("Database error.", "danger")
        return redirect(url_for("driver_available_rides"))

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, user_id, fare, original_fare, status, driver_id FROM rides WHERE id = %s", (ride_id,))
        ride = cur.fetchone()
        if not ride:
            cur.close()
            if is_ajax:
                return jsonify({"success": False, "error": "Ride not found"}), 404
            flash("Course introuvable.", "danger")
            return redirect(url_for("driver_available_rides"))

        if ride["status"] != "PENDING" or ride["driver_id"] is not None:
            cur.close()
            if is_ajax:
                return jsonify({"success": False, "error": "Cette course n'est plus disponible."}), 400
            flash("Cette course n'est plus disponible.", "warning")
            return redirect(url_for("driver_available_rides"))

        cur.execute(
            """UPDATE rides
               SET driver_counter_fare = %s, counter_driver_id = %s, negotiation_status = 'COUNTERED'
               WHERE id = %s AND status = 'PENDING' AND driver_id IS NULL""",
            (counter_fare, driver_id, ride_id)
        )
        conn.commit()
        cur.close()

        msg = f"Votre contre-offre de {int(round(counter_fare))} XAF a été transmise au client !"
        if is_ajax:
            return jsonify({
                "success": True,
                "ride_id": ride_id,
                "counter_fare": counter_fare,
                "message": msg
            })
        flash(msg, "success")
        return redirect(url_for("driver_available_rides"))
    except Error as e:
        if is_ajax:
            return jsonify({"success": False, "error": str(e)}), 500
        flash("Erreur lors de l'envoi de la contre-offre.", "danger")
        return redirect(url_for("driver_available_rides"))
    finally:
        conn.close()


@app.route("/driver/ride/<int:ride_id>/start", methods=["POST"])
@driver_required
def driver_start_ride(ride_id):
    return _driver_update_status(ride_id, "IN_PROGRESS", "ACCEPTED")


@app.route("/driver/ride/<int:ride_id>/complete", methods=["POST"])
@driver_required
def driver_complete_ride(ride_id):
    return _driver_update_status(ride_id, "COMPLETED", "IN_PROGRESS")


@app.route("/driver/ride/<int:ride_id>/cancel", methods=["POST"])
@driver_required
def driver_cancel_ride(ride_id):
    """Driver cancels their accepted ride → back to PENDING so others can take it."""
    driver_id = session["driver_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("driver_my_rides"))
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT status, driver_id FROM rides WHERE id = %s",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride or ride["driver_id"] != driver_id:
            flash("Ride not found or not assigned to you.", "danger")
            return redirect(url_for("driver_my_rides"))

        if ride["status"] not in ("ACCEPTED", "IN_PROGRESS"):
            flash("Only active rides can be cancelled by the driver.", "warning")
            return redirect(url_for("driver_my_rides"))

        # Release the ride so other drivers can take it; driver becomes free
        cur.execute(
            """UPDATE rides
               SET status = 'PENDING', driver_id = NULL
               WHERE id = %s""",
            (ride_id,)
        )
        cur.execute(
            "UPDATE drivers SET availability = 'free' WHERE id = %s",
            (driver_id,)
        )
        conn.commit()
        flash("Ride cancelled. It is available again for other drivers.", "info")
        cur.close()
    except Error:
        flash("Could not cancel ride.", "danger")
    finally:
        conn.close()
    return redirect(url_for("driver_my_rides"))


def _driver_update_status(ride_id, new_status, expected_current):
    """Driver updates status of their own ride only."""
    driver_id = session["driver_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("driver_my_rides"))
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT status, driver_id FROM rides WHERE id = %s",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride or ride["driver_id"] != driver_id:
            flash("Ride not found or not assigned to you.", "danger")
            return redirect(url_for("driver_my_rides"))

        if ride["status"] != expected_current:
            flash(f"Ride must be {expected_current} before {new_status}.", "warning")
            return redirect(url_for("driver_my_rides"))

        cur.execute(
            "UPDATE rides SET status = %s WHERE id = %s",
            (new_status, ride_id)
        )
        # When trip is completed, driver becomes free again
        if new_status == "COMPLETED":
            cur.execute(
                "UPDATE drivers SET availability = 'free' WHERE id = %s",
                (driver_id,)
            )
        conn.commit()
        flash(f"Ride marked as {new_status}.", "success")
        cur.close()
    except Error:
        flash("Could not update ride.", "danger")
    finally:
        conn.close()
    return redirect(url_for("driver_my_rides"))


@app.route("/driver/status", methods=["GET", "POST"])
@driver_required
def driver_status():
    """Driver sets current location and availability (free / busy)."""
    driver_id = session["driver_id"]
    conn = get_db()
    driver = None
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("driver_dashboard"))

    try:
        cur = conn.cursor(dictionary=True)
        if request.method == "POST":
            location = normalize_location(request.form.get("current_location", ""))
            availability = request.form.get("availability", "free")
            has_trunk = 1 if request.form.get("has_trunk") else 0
            has_roof_rack = 1 if request.form.get("has_roof_rack") else 0
            if availability not in ("free", "busy"):
                availability = "free"
            if not location:
                flash("Please choose a valid Douala location.", "danger")
            else:
                cur.execute(
                    """UPDATE drivers
                       SET current_location = %s, availability = %s, has_trunk = %s, has_roof_rack = %s
                       WHERE id = %s""",
                    (location, availability, has_trunk, has_roof_rack, driver_id)
                )
                conn.commit()
                flash("Your location and availability were updated.", "success")

        cur.execute(
            """SELECT full_name, current_location, availability, vehicle_info, vehicle_type, has_trunk, has_roof_rack
               FROM drivers WHERE id = %s""",
            (driver_id,)
        )
        driver = cur.fetchone()
        cur.close()
    except Error:
        flash("Could not update status.", "danger")
    finally:
        conn.close()

    return render_template(
        "driver/status.html",
        driver=driver,
        locations=LOCATIONS
    )


# ============================================================
# PASSENGER DASHBOARD & PROFILE
# ============================================================
@app.route("/dashboard")
@login_required
def dashboard():
    """Passenger dashboard with summary + unpaid rides for MoMo payment."""
    user_id = session["user_id"]
    conn = get_db()
    stats = {
        "total": 0, "pending": 0, "completed": 0,
        "cancelled": 0, "total_paid": 0
    }
    recent = []
    unpaid = []
    active_ride = None

    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            # Active ongoing or pending ride (PENDING, ACCEPTED or IN_PROGRESS)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.fare, r.original_fare, r.negotiation_status,
                       r.driver_counter_fare, r.counter_driver_id, r.cargo_type, r.cargo_fee, r.status, r.vehicle_type, r.created_at,
                       r.split_enabled, r.split_count, r.split_fare_per_person,
                       d.full_name AS driver_name, d.phone AS driver_phone, d.vehicle_info, d.current_location AS driver_location,
                       cd.full_name AS counter_driver_name, cd.phone AS counter_driver_phone, cd.vehicle_info AS counter_driver_vehicle
                FROM rides r
                LEFT JOIN drivers d ON r.driver_id = d.id
                LEFT JOIN drivers cd ON r.counter_driver_id = cd.id
                WHERE r.user_id = %s AND r.status IN ('PENDING', 'ACCEPTED', 'IN_PROGRESS') AND r.is_scheduled = FALSE
                ORDER BY r.created_at DESC LIMIT 1
                """,
                (user_id,)
            )
            active_ride = cur.fetchone()
            if active_ride:
                cur.execute(
                    """SELECT id FROM payments
                       WHERE ride_id = %s AND user_id = %s AND status = 'SUCCESSFUL'""",
                    (active_ride["id"], user_id)
                )
                active_ride["is_paid"] = bool(cur.fetchone())

                if active_ride.get("split_enabled"):
                    cur.execute(
                        """
                        SELECT id, passenger_index, passenger_name, passenger_phone, share_amount,
                               is_paid, payment_reference, operator, invite_token
                        FROM ride_splits
                        WHERE ride_id = %s
                        ORDER BY passenger_index ASC
                        """,
                        (active_ride["id"],)
                    )
                    splits = cur.fetchall()
                    cur.execute("SELECT phone, full_name FROM users WHERE id = %s", (user_id,))
                    u_row = cur.fetchone() or {}
                    organizer_phone = u_row.get("phone", "")
                    organizer_name = u_row.get("full_name", session.get("user_name", "Organisateur"))

                    for s in splits:
                        s["ussd"] = generate_split_ussd_codes(organizer_phone, s["share_amount"])
                        s["whatsapp_url"] = generate_split_whatsapp_link(
                            passenger_name=s["passenger_name"],
                            share_amount=s["share_amount"],
                            pickup=active_ride["pickup"],
                            destination=active_ride["destination"],
                            invite_token=s["invite_token"],
                            organizer_name=organizer_name,
                            passenger_phone=s["passenger_phone"]
                        )
                    active_ride["splits"] = splits
                    active_ride["split_paid_count"] = sum(1 for s in splits if s["is_paid"])
                    active_ride["all_splits_paid"] = (active_ride["split_paid_count"] == len(splits))

            # Counts
            cur.execute(
                """SELECT status, COUNT(*) as cnt FROM rides
                   WHERE user_id = %s GROUP BY status""",
                (user_id,)
            )
            for row in cur.fetchall():
                stats["total"] += row["cnt"]
                if row["status"] == "PENDING":
                    stats["pending"] = row["cnt"]
                elif row["status"] == "COMPLETED":
                    stats["completed"] = row["cnt"]
                elif row["status"] == "CANCELLED":
                    stats["cancelled"] = row["cnt"]

            # Total paid
            cur.execute(
                """SELECT COALESCE(SUM(amount), 0) as total
                   FROM payments WHERE user_id = %s AND status = 'SUCCESSFUL'""",
                (user_id,)
            )
            stats["total_paid"] = cur.fetchone()["total"]

            # Recent rides
            cur.execute(
                """SELECT id, pickup, destination, fare, status, created_at
                   FROM rides WHERE user_id = %s
                   ORDER BY created_at DESC LIMIT 5""",
                (user_id,)
            )
            recent = cur.fetchall()

            # Unpaid rides (accepted or later, no successful payment yet)
            # so passenger can pay with MoMo from the dashboard
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.fare, r.status
                FROM rides r
                WHERE r.user_id = %s
                  AND r.status IN ('ACCEPTED', 'IN_PROGRESS', 'COMPLETED')
                  AND NOT EXISTS (
                      SELECT 1 FROM payments p
                      WHERE p.ride_id = r.id
                        AND p.user_id = %s
                        AND p.status = 'SUCCESSFUL'
                  )
                ORDER BY r.created_at DESC
                """,
                (user_id, user_id)
            )
            unpaid = cur.fetchall()

            # Upcoming scheduled rides/shuttles for pre-flight & port reminder
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.fare, r.original_fare, r.vehicle_type,
                       r.cargo_type, r.cargo_fee, r.status, r.is_scheduled, r.scheduled_time,
                       r.scheduled_type, r.flight_or_shift_notes, r.created_at,
                       d.full_name AS driver_name, d.phone AS driver_phone, d.vehicle_info
                FROM rides r
                LEFT JOIN drivers d ON r.driver_id = d.id
                WHERE r.user_id = %s
                  AND r.is_scheduled = TRUE
                  AND r.status IN ('PENDING', 'ACCEPTED')
                ORDER BY r.scheduled_time ASC LIMIT 3
                """,
                (user_id,)
            )
            scheduled_shuttles = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load dashboard data.", "warning")
            scheduled_shuttles = []
        finally:
            conn.close()
    else:
        scheduled_shuttles = []

    return render_template(
        "dashboard.html",
        stats=stats,
        recent=recent,
        unpaid=unpaid,
        active_ride=active_ride,
        scheduled_shuttles=scheduled_shuttles,
        user_name=session.get("user_name")
    )


@app.route("/profile")
@login_required
def profile():
    """Simple user profile page."""
    user_id = session["user_id"]
    user = None
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT full_name, phone, email, created_at FROM users WHERE id = %s",
                (user_id,)
            )
            user = cur.fetchone()
            cur.close()
        except Error:
            pass
        finally:
            conn.close()
    return render_template("profile.html", user=user)


# ============================================================
# REQUEST RIDE (passenger types or chooses locations)
# ============================================================
@app.route("/request-ride", methods=["GET", "POST"])
@login_required
def request_ride():
    """
    Passenger requests a ride.
    - Can type or choose pickup / destination (known Douala areas)
    - Sees free drivers near the pickup (no GPS – based on driver current_location)
    """
    nearby_drivers = []
    selected_pickup = request.args.get("pickup", "") or request.form.get("pickup", "")

    # Normalize typed pickup to show nearby drivers on GET or failed POST
    pickup_norm = normalize_location(selected_pickup)
    if pickup_norm:
        nearby = get_nearby_locations(pickup_norm)
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor(dictionary=True)
                placeholders = ",".join(["%s"] * len(nearby))
                cur.execute(
                    f"""
                    SELECT id, full_name, phone, vehicle_info, current_location, availability
                    FROM drivers
                    WHERE status = 'active'
                      AND availability = 'free'
                      AND current_location IN ({placeholders})
                    ORDER BY current_location, full_name
                    """,
                    tuple(nearby)
                )
                nearby_drivers = cur.fetchall()
                cur.close()
            except Error:
                nearby_drivers = []
            finally:
                conn.close()

    if request.method == "POST":
        pickup = normalize_location(request.form.get("pickup", ""))
        destination = normalize_location(request.form.get("destination", ""))
        passengers = request.form.get("passengers", "1").strip()
        preferred_driver = request.form.get("preferred_driver", "").strip()
        vehicle_type = request.form.get("vehicle_type", "taxi").lower()
        if vehicle_type not in VEHICLE_TYPES:
            vehicle_type = "taxi"

        cargo_type = request.form.get("cargo_type", "none").strip().lower()
        if cargo_type not in CARGO_OPTIONS:
            cargo_type = "none"
        cargo_meta = CARGO_OPTIONS[cargo_type]
        cargo_fee = float(cargo_meta.get("fee", 0.0))

        # Enforce safety constraints: Bendskin moto-taxi cannot carry market goods or heavy luggage
        if cargo_type in ("market", "heavy") and vehicle_type == "bendskin":
            vehicle_type = "taxi"
            flash("Le moto-taxi Bendskin ne peut pas transporter de marchandises de marché ou de gros bagages. Votre course a été automatiquement configurée en Taxi Jaune avec coffre.", "info")

        # Scheduled Early-Morning Airport & Port Shuttles ("Réservation Course à l'Avance")
        booking_mode = request.form.get("booking_mode", "now").strip().lower()
        is_scheduled = (booking_mode == "scheduled") or (request.form.get("is_scheduled") in ("1", "true"))
        scheduled_time = None
        scheduled_type = "standard"
        flight_or_shift_notes = request.form.get("flight_or_shift_notes", "").strip()[:150]

        if is_scheduled:
            scheduled_time_raw = request.form.get("scheduled_time", "").strip()
            if not scheduled_time_raw:
                flash("Veuillez sélectionner la date et l'heure de départ pour votre réservation à l'avance.", "danger")
                return _reload_form()
            try:
                # datetime-local sends e.g. 2026-10-17T05:30
                scheduled_time = datetime.fromisoformat(scheduled_time_raw.replace("Z", ""))
            except (ValueError, TypeError):
                flash("Format de date et heure invalide pour la réservation.", "danger")
                return _reload_form()

            now = datetime.now()
            if scheduled_time < now + timedelta(minutes=15):
                flash("L'heure de réservation doit être d'au moins 15 minutes dans le futur.", "danger")
                return _reload_form()
            if scheduled_time > now + timedelta(days=7, hours=2):
                flash("Les réservations à l'avance sont limitées à 7 jours maximum.", "danger")
                return _reload_form()

            dest_lower = (destination or "").lower()
            pick_lower = (pickup or "").lower()
            notes_lower = flight_or_shift_notes.lower()
            if "aéroport" in dest_lower or "aeroport" in dest_lower or "aéroport" in pick_lower or "aeroport" in pick_lower or "vol" in notes_lower or "flight" in notes_lower or "dla" in notes_lower:
                scheduled_type = "airport"
            elif "bonanjo" in dest_lower or "port" in dest_lower or "quai" in notes_lower or "shift" in notes_lower or "port" in notes_lower or "douane" in notes_lower:
                scheduled_type = "port"
            else:
                scheduled_type = request.form.get("scheduled_type", "standard").lower()
                if scheduled_type not in ("standard", "airport", "port"):
                    scheduled_type = "standard"

        # Carpool Split-Fare Engine ("Partage de Frais entre Passagers")
        split_fare_toggle = (request.form.get("split_fare_toggle") == "1")
        split_count = 1
        if split_fare_toggle:
            try:
                split_count = int(request.form.get("split_count", 2))
                if split_count < 2 or split_count > 4:
                    split_count = 2
            except (ValueError, TypeError):
                split_count = 2

        def _reload_form():
            return render_template(
                "request_ride.html",
                locations=LOCATIONS,
                vehicle_types=VEHICLE_TYPES,
                cargo_options=CARGO_OPTIONS,
                douala_markets=DOUALA_MARKETS,
                nearby_drivers=nearby_drivers,
                selected_pickup=request.form.get("pickup", ""),
                selected_destination=request.form.get("destination", ""),
                selected_vehicle_type=vehicle_type,
                selected_cargo_type=cargo_type,
                booking_mode=booking_mode,
                is_scheduled=is_scheduled,
                selected_scheduled_time=request.form.get("scheduled_time", ""),
                selected_flight_notes=flight_or_shift_notes,
                selected_scheduled_type=scheduled_type,
                split_enabled=split_fare_toggle,
                split_count=split_count,
                copax_name_2=request.form.get("copax_name_2", ""),
                copax_phone_2=request.form.get("copax_phone_2", ""),
                copax_name_3=request.form.get("copax_name_3", ""),
                copax_phone_3=request.form.get("copax_phone_3", ""),
                copax_name_4=request.form.get("copax_name_4", ""),
                copax_phone_4=request.form.get("copax_phone_4", ""),
            )

        if not pickup or not destination:
            flash("Please type or choose a valid pickup and destination (Douala areas).", "danger")
            return _reload_form()

        if pickup == destination:
            flash("Pickup and destination cannot be the same.", "danger")
            return _reload_form()

        try:
            passengers = int(passengers)
            if passengers < 1 or passengers > 4:
                raise ValueError
        except ValueError:
            passengers = split_count if split_fare_toggle else 1

        # Carpool split-fare requires at least split_count passengers and cannot use bendskin moto
        if split_fare_toggle:
            if vehicle_type == "bendskin":
                vehicle_type = "taxi"
                flash("Le moto-taxi Bendskin est strictement individuel. Votre course partagée a été configurée en Taxi Jaune collectif.", "info")
            if passengers < split_count:
                passengers = split_count

        # Enforce passenger limit for bendskin moto-taxi
        if vehicle_type == "bendskin" and passengers > 1:
            passengers = 1
            flash("Bendskin moto-taxi is strictly limited to 1 passenger for road safety in Douala.", "info")

        base_route_fare = get_fare(pickup, destination, vehicle_type)
        if base_route_fare is None:
            flash("Could not calculate fare for this route.", "danger")
            return _reload_form()

        standard_total_fare = float(base_route_fare + cargo_fee)

        # Douala Street Fare Negotiation ("Marchandage à la Doualaise")
        negotiated_fare_input = request.form.get("negotiated_fare", "").strip()
        fare = standard_total_fare
        original_fare = standard_total_fare
        negotiation_status = "NONE"

        if negotiated_fare_input:
            try:
                parsed_offer = float(negotiated_fare_input)
                min_allowed = max(300.0, standard_total_fare * 0.40)
                max_allowed = standard_total_fare * 3.0
                if min_allowed <= parsed_offer <= max_allowed and abs(parsed_offer - standard_total_fare) >= 1.0:
                    fare = parsed_offer
                    original_fare = standard_total_fare
                    negotiation_status = "PROPOSED"
            except (ValueError, TypeError):
                pass

        split_enabled = split_fare_toggle
        split_fare_per_person = None
        p1_share = fare
        if split_enabled:
            split_fare_per_person = int(round(fare / split_count))
            p1_share = int(round(fare)) - (split_fare_per_person * (split_count - 1))

        driver_id = None
        if preferred_driver:
            try:
                driver_id = int(preferred_driver)
            except ValueError:
                driver_id = None

        conn = get_db()
        if not conn:
            flash("Database error. Please try again.", "danger")
            return _reload_form()

        try:
            cur = conn.cursor(dictionary=True)

            # If passenger chose a specific free driver, assign immediately
            assigned = False
            ride_id = None
            if driver_id:
                cur.execute(
                    """SELECT id FROM drivers
                       WHERE id = %s AND status = 'active' AND availability = 'free'""",
                    (driver_id,)
                )
                if cur.fetchone():
                    cur.execute(
                        """INSERT INTO rides
                           (user_id, driver_id, pickup, destination, passengers, vehicle_type, cargo_type, cargo_fee,
                            fare, original_fare, negotiation_status, is_scheduled, scheduled_time, scheduled_type, flight_or_shift_notes,
                            split_enabled, split_count, split_fare_per_person, status)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'ACCEPTED')""",
                        (session["user_id"], driver_id, pickup, destination, passengers, vehicle_type, cargo_type, cargo_fee,
                         fare, original_fare, negotiation_status, is_scheduled, scheduled_time, scheduled_type, flight_or_shift_notes,
                         split_enabled, split_count, split_fare_per_person)
                    )
                    ride_id = cur.lastrowid
                    if not is_scheduled:
                        cur.execute(
                            "UPDATE drivers SET availability = 'busy' WHERE id = %s",
                            (driver_id,)
                        )
                        # Cancel only immediate pending rides of this passenger
                        cur.execute(
                            """UPDATE rides SET status = 'CANCELLED'
                               WHERE user_id = %s AND status = 'PENDING' AND is_scheduled = FALSE""",
                            (session["user_id"],)
                        )
                    assigned = True
                    if is_scheduled and scheduled_time:
                        st_fmt = scheduled_time.strftime("%d/%m/%Y à %H:%M")
                        flash(
                            f"✈️ Navette planifiée réservée et confirmée auprès de votre chauffeur pour le {st_fmt} ! Tarif convenu : {int(round(fare))} XAF.",
                            "success"
                        )
                    else:
                        flash(
                            f"Ride requested and assigned to your chosen driver! "
                            f"Fare: {int(round(fare))} XAF. Please pay with MoMo / Orange Money from your dashboard.",
                            "success"
                        )
                else:
                    flash("That driver is no longer available. Ride created as PENDING.", "warning")

            if not assigned:
                cur.execute(
                    """INSERT INTO rides
                       (user_id, pickup, destination, passengers, vehicle_type, cargo_type, cargo_fee,
                        fare, original_fare, negotiation_status, is_scheduled, scheduled_time, scheduled_type, flight_or_shift_notes,
                        split_enabled, split_count, split_fare_per_person, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')""",
                    (session["user_id"], pickup, destination, passengers, vehicle_type, cargo_type, cargo_fee,
                     fare, original_fare, negotiation_status, is_scheduled, scheduled_time, scheduled_type, flight_or_shift_notes,
                     split_enabled, split_count, split_fare_per_person)
                )
                ride_id = cur.lastrowid
                if is_scheduled and scheduled_time:
                    st_fmt = scheduled_time.strftime("%d/%m/%Y à %H:%M")
                    label_type = "Navette Aéroport DLA" if scheduled_type == "airport" else ("Navette Port de Douala" if scheduled_type == "port" else "Course planifiée")
                    flash(
                        f"✈️ {label_type} réservée pour le {st_fmt} ({pickup} → {destination}) ! Les chauffeurs partenaires peuvent maintenant pré-réserver votre trajet garanti.",
                        "success"
                    )
                elif negotiation_status == "PROPOSED":
                    flash(
                        f"Offre négociée transmise aux chauffeurs : {int(round(fare))} XAF (Tarif standard : {int(round(original_fare))} XAF). En attente d'acceptation !",
                        "success"
                    )
                else:
                    cargo_msg = f" (+{int(cargo_fee)} XAF colis)" if cargo_fee > 0 else ""
                    flash(
                        f"Ride requested successfully ({VEHICLE_TYPES[vehicle_type]['label']}){cargo_msg}! "
                        f"Estimated fare: {int(round(fare))} XAF. Waiting for a driver to accept.",
                        "success"
                    )

            if split_enabled and ride_id:
                cur.execute("SELECT full_name, phone FROM users WHERE id = %s", (session["user_id"],))
                organizer_user = cur.fetchone() or {"full_name": session.get("user_name", "Organisateur"), "phone": ""}

                p1_token = secrets.token_hex(16)
                cur.execute(
                    """
                    INSERT INTO ride_splits
                    (ride_id, passenger_index, passenger_name, passenger_phone, share_amount, is_paid, invite_token)
                    VALUES (%s, 1, %s, %s, %s, FALSE, %s)
                    """,
                    (ride_id, organizer_user["full_name"], organizer_user["phone"], p1_share, p1_token)
                )

                for p_idx in range(2, split_count + 1):
                    c_name = request.form.get(f"copax_name_{p_idx}", "").strip() or f"Passager {p_idx}"
                    c_phone = request.form.get(f"copax_phone_{p_idx}", "").strip()
                    p_tok = secrets.token_hex(16)
                    cur.execute(
                        """
                        INSERT INTO ride_splits
                        (ride_id, passenger_index, passenger_name, passenger_phone, share_amount, is_paid, invite_token)
                        VALUES (%s, %s, %s, %s, %s, FALSE, %s)
                        """,
                        (ride_id, p_idx, c_name, c_phone, split_fare_per_person, p_tok)
                    )

                flash(
                    f"👥 Covoiturage activé ({split_count} personnes) ! Tarif total : {int(round(fare))} XAF ({split_fare_per_person} XAF/personne). Liens WhatsApp et syntaxes USSD prêts sur votre tableau de bord !",
                    "info"
                )

            conn.commit()
            cur.close()
            return redirect(url_for("dashboard"))
        except Error:
            flash("Could not create ride. Please try again.", "danger")
        finally:
            conn.close()

    default_mode = request.args.get("mode", "now")
    default_type = request.args.get("type", "standard")
    default_dest = request.args.get("dest", "")
    default_notes = request.args.get("notes", "")

    return render_template(
        "request_ride.html",
        locations=LOCATIONS,
        vehicle_types=VEHICLE_TYPES,
        cargo_options=CARGO_OPTIONS,
        douala_markets=DOUALA_MARKETS,
        nearby_drivers=nearby_drivers,
        selected_pickup=selected_pickup,
        selected_destination=default_dest,
        selected_vehicle_type="comfort" if default_type == "airport" else "taxi",
        selected_cargo_type="none",
        booking_mode=default_mode,
        is_scheduled=(default_mode == "scheduled"),
        selected_scheduled_time="",
        selected_flight_notes=default_notes,
        selected_scheduled_type=default_type,
    )


# ============================================================
# STREET FARE NEGOTIATION API ROUTES (Passenger)
# ============================================================
@app.route("/api/ride/<int:ride_id>/negotiate", methods=["POST"])
@login_required
def api_negotiate_ride_fare(ride_id):
    """
    Passenger adjusts their counter-offer on an active PENDING ride.
    """
    user_id = session["user_id"]
    data = request.get_json(silent=True) or request.form
    new_fare = data.get("fare") or data.get("negotiated_fare")
    if not new_fare:
        return jsonify({"success": False, "error": "Montant requis"}), 400

    try:
        new_fare = float(new_fare)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Montant invalide"}), 400

    conn = get_db()
    if not conn:
        return jsonify({"success": False, "error": "Erreur base de données"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, user_id, fare, original_fare, status FROM rides WHERE id = %s",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride:
            cur.close()
            return jsonify({"success": False, "error": "Course introuvable"}), 404

        if ride["user_id"] != user_id:
            cur.close()
            return jsonify({"success": False, "error": "Non autorisé"}), 403

        if ride["status"] != "PENDING":
            cur.close()
            return jsonify({"success": False, "error": "Seules les courses en attente peuvent être négociées"}), 400

        base_fare = float(ride["original_fare"] or ride["fare"])
        min_allowed = max(300.0, base_fare * 0.40)
        max_allowed = base_fare * 3.0

        if not (min_allowed <= new_fare <= max_allowed):
            cur.close()
            return jsonify({
                "success": False,
                "error": f"L'offre doit être comprise entre {int(round(min_allowed))} et {int(round(max_allowed))} XAF."
            }), 400

        cur.execute(
            """UPDATE rides
               SET fare = %s, original_fare = %s, negotiation_status = 'PROPOSED',
                   driver_counter_fare = NULL, counter_driver_id = NULL
               WHERE id = %s AND status = 'PENDING' AND user_id = %s""",
            (new_fare, base_fare, ride_id, user_id)
        )
        conn.commit()
        cur.close()
        return jsonify({
            "success": True,
            "ride_id": ride_id,
            "fare": new_fare,
            "original_fare": base_fare,
            "negotiation_status": "PROPOSED",
            "message": f"Offre mise à jour à {int(round(new_fare))} XAF"
        })
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/ride/<int:ride_id>/accept-counter", methods=["POST"])
@login_required
def api_accept_driver_counter(ride_id):
    """
    Passenger accepts the driver's counter-offer.
    """
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "error": "Erreur base de données"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT r.id, r.user_id, r.driver_counter_fare, r.counter_driver_id, r.status,
                      d.full_name AS driver_name, d.phone AS driver_phone
               FROM rides r
               LEFT JOIN drivers d ON r.counter_driver_id = d.id
               WHERE r.id = %s""",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride or ride["user_id"] != user_id:
            cur.close()
            return jsonify({"success": False, "error": "Course introuvable ou non autorisée"}), 404

        if ride["status"] != "PENDING" or not ride["counter_driver_id"] or not ride["driver_counter_fare"]:
            cur.close()
            return jsonify({"success": False, "error": "Aucune contre-offre active à accepter"}), 400

        driver_id = ride["counter_driver_id"]
        agreed_fare = float(ride["driver_counter_fare"])

        cur.execute(
            """UPDATE rides
               SET fare = %s, driver_id = %s, status = 'ACCEPTED', negotiation_status = 'ACCEPTED'
               WHERE id = %s AND status = 'PENDING'""",
            (agreed_fare, driver_id, ride_id)
        )
        cur.execute("UPDATE drivers SET availability = 'busy' WHERE id = %s", (driver_id,))
        cur.execute(
            "UPDATE rides SET status = 'CANCELLED' WHERE user_id = %s AND status = 'PENDING' AND id != %s",
            (user_id, ride_id)
        )
        conn.commit()
        cur.close()

        flash(f"Contre-offre acceptée à {int(round(agreed_fare))} XAF ! Votre chauffeur est en route.", "success")
        return jsonify({
            "success": True,
            "ride_id": ride_id,
            "fare": agreed_fare,
            "driver_name": ride["driver_name"],
            "driver_phone": ride["driver_phone"]
        })
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/ride/<int:ride_id>/decline-counter", methods=["POST"])
@login_required
def api_decline_driver_counter(ride_id):
    """
    Passenger declines the driver's counter-offer.
    """
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "error": "Erreur base de données"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, user_id, status FROM rides WHERE id = %s", (ride_id,))
        ride = cur.fetchone()
        if not ride or ride["user_id"] != user_id:
            cur.close()
            return jsonify({"success": False, "error": "Course introuvable ou non autorisée"}), 404

        cur.execute(
            """UPDATE rides
               SET driver_counter_fare = NULL, counter_driver_id = NULL, negotiation_status = 'DECLINED'
               WHERE id = %s AND status = 'PENDING' AND user_id = %s""",
            (ride_id, user_id)
        )
        conn.commit()
        cur.close()
        flash("Contre-offre déclinée. Votre demande reste ouverte aux autres chauffeurs.", "info")
        return jsonify({"success": True, "message": "Contre-offre déclinée"})
    except Error as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


# ============================================================
# SHARED RIDES
# ============================================================
@app.route("/shared-rides")
@login_required
def shared_rides():
    """
    Show rides that others can join.
    Only PENDING rides appear here (bendskin moto-taxis cannot be shared).
    Once a ride is ACCEPTED (taken), it is removed from the list
    so other users cannot join it anymore.
    """
    user_id = session["user_id"]
    rides = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.passengers, r.vehicle_type, r.fare, r.status,
                       r.user_id, u.full_name AS owner_name,
                       (SELECT COUNT(*) FROM ride_participants rp WHERE rp.ride_id = r.id) AS joined
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'PENDING'
                  AND r.user_id != %s
                  AND r.vehicle_type != 'bendskin'
                ORDER BY r.created_at DESC
                """,
                (user_id,)
            )
            all_rides = cur.fetchall()

            # Filter: capacity not exceeded and user has not already joined
            for r in all_rides:
                total_people = r["passengers"] + r["joined"]
                if total_people >= 4:  # max 4 people per ride
                    continue
                cur.execute(
                    "SELECT id FROM ride_participants WHERE ride_id = %s AND user_id = %s",
                    (r["id"], user_id)
                )
                if cur.fetchone():
                    continue
                rides.append(r)
            cur.close()
        except Error:
            flash("Could not load shared rides.", "warning")
        finally:
            conn.close()

    return render_template("shared_rides.html", rides=rides)


@app.route("/join-ride/<int:ride_id>", methods=["POST"])
@login_required
def join_ride(ride_id):
    """Join an existing shared ride."""
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("shared_rides"))

    try:
        cur = conn.cursor(dictionary=True)

        # Get the ride
        cur.execute(
            "SELECT id, user_id, passengers, status FROM rides WHERE id = %s",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride:
            flash("Ride not found.", "danger")
            return redirect(url_for("shared_rides"))

        if ride["user_id"] == user_id:
            flash("You cannot join your own ride.", "warning")
            return redirect(url_for("shared_rides"))

        # Once ACCEPTED / CANCELLED / etc. the ride is taken or closed
        if ride["status"] != "PENDING":
            flash("This ride is no longer available (already taken or cancelled).", "warning")
            return redirect(url_for("shared_rides"))

        # Already joined?
        cur.execute(
            "SELECT id FROM ride_participants WHERE ride_id = %s AND user_id = %s",
            (ride_id, user_id)
        )
        if cur.fetchone():
            flash("You already joined this ride.", "warning")
            return redirect(url_for("shared_rides"))

        # Capacity check
        cur.execute(
            "SELECT COUNT(*) AS cnt FROM ride_participants WHERE ride_id = %s",
            (ride_id,)
        )
        joined = cur.fetchone()["cnt"]
        if ride["passengers"] + joined >= 4:
            flash("This ride is already full.", "warning")
            return redirect(url_for("shared_rides"))

        # Join
        cur.execute(
            "INSERT INTO ride_participants (ride_id, user_id) VALUES (%s, %s)",
            (ride_id, user_id)
        )
        conn.commit()
        flash("You successfully joined the ride!", "success")
    except Error:
        flash("Could not join ride. Please try again.", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("shared_rides"))


# ============================================================
# MY RIDES
# ============================================================
@app.route("/my-rides")
@login_required
def my_rides():
    """List rides created by the user + rides they joined, with driver and vehicle details."""
    user_id = session["user_id"]
    own_rides = []
    joined_rides = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            # Own rides with assigned driver info
            cur.execute(
                """SELECT r.*, 
                          d.full_name AS driver_name, d.phone AS driver_phone,
                          d.vehicle_info, d.vehicle_type AS driver_vehicle_type,
                          (SELECT status FROM payments p WHERE p.ride_id = r.id 
                           ORDER BY p.created_at DESC LIMIT 1) AS payment_status,
                          (SELECT id FROM payments p WHERE p.ride_id = r.id 
                           ORDER BY p.created_at DESC LIMIT 1) AS payment_id
                   FROM rides r
                   LEFT JOIN drivers d ON r.driver_id = d.id
                   WHERE r.user_id = %s
                   ORDER BY r.created_at DESC""",
                (user_id,)
            )
            own_rides = cur.fetchall()

            # Joined rides
            cur.execute(
                """SELECT r.*, u.full_name AS owner_name,
                          d.full_name AS driver_name, d.phone AS driver_phone
                   FROM ride_participants rp
                   JOIN rides r ON rp.ride_id = r.id
                   JOIN users u ON r.user_id = u.id
                   LEFT JOIN drivers d ON r.driver_id = d.id
                   WHERE rp.user_id = %s
                   ORDER BY rp.joined_at DESC""",
                (user_id,)
            )
            joined_rides = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load your rides.", "warning")
        finally:
            conn.close()

    return render_template(
        "my_rides.html",
        own_rides=own_rides,
        joined_rides=joined_rides,
        vehicle_types=VEHICLE_TYPES
    )


@app.route("/ride/<int:ride_id>/cancel", methods=["POST"])
@login_required
def rider_cancel_ride(ride_id):
    """Passenger cancels their own PENDING ride request."""
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("my_rides"))
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT status FROM rides WHERE id = %s AND user_id = %s", (ride_id, user_id))
        ride = cur.fetchone()
        if not ride:
            flash("Ride not found.", "danger")
            return redirect(url_for("my_rides"))
        if ride["status"] != "PENDING":
            flash("You can only cancel pending ride requests.", "warning")
            return redirect(url_for("my_rides"))
        cur.execute("UPDATE rides SET status = 'CANCELLED' WHERE id = %s", (ride_id,))
        conn.commit()
        flash("Your ride request has been cancelled.", "info")
        cur.close()
    except Error:
        flash("Could not cancel ride.", "danger")
    finally:
        conn.close()
    return redirect(url_for("my_rides"))


@app.route("/leave-ride/<int:ride_id>", methods=["POST"])
@login_required
def leave_ride(ride_id):
    """Passenger leaves a joined shared ride before it starts."""
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("my_rides"))
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT status FROM rides WHERE id = %s", (ride_id,))
        ride = cur.fetchone()
        if not ride or ride["status"] != "PENDING":
            flash("Cannot leave this ride (already accepted or in progress).", "warning")
            return redirect(url_for("my_rides"))
        cur.execute("DELETE FROM ride_participants WHERE ride_id = %s AND user_id = %s", (ride_id, user_id))
        conn.commit()
        flash("You have left the shared ride.", "info")
        cur.close()
    except Error:
        flash("Could not leave ride.", "danger")
    finally:
        conn.close()
    return redirect(url_for("my_rides"))


# ============================================================
# RATING
# ============================================================
@app.route("/rate-ride/<int:ride_id>", methods=["GET", "POST"])
@login_required
def rate_ride(ride_id):
    """Rate a completed ride."""
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("my_rides"))

    try:
        cur = conn.cursor(dictionary=True)

        # Check ride exists and is completed, and user is owner or participant
        cur.execute(
            """SELECT r.id, r.status, r.user_id
               FROM rides r
               LEFT JOIN ride_participants rp ON r.id = rp.ride_id AND rp.user_id = %s
               WHERE r.id = %s AND (r.user_id = %s OR rp.user_id = %s)""",
            (user_id, ride_id, user_id, user_id)
        )
        ride = cur.fetchone()
        if not ride:
            flash("Ride not found or you are not part of it.", "danger")
            return redirect(url_for("my_rides"))

        if ride["status"] != "COMPLETED":
            flash("You can only rate completed rides.", "warning")
            return redirect(url_for("my_rides"))

        # Already rated?
        cur.execute(
            "SELECT id FROM ratings WHERE ride_id = %s AND user_id = %s",
            (ride_id, user_id)
        )
        if cur.fetchone():
            flash("You already rated this ride.", "info")
            return redirect(url_for("my_rides"))

        if request.method == "POST":
            rating = request.form.get("rating")
            comment = request.form.get("comment", "").strip()

            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    raise ValueError
            except (TypeError, ValueError):
                flash("Rating must be between 1 and 5.", "danger")
                return render_template("rate_ride.html", ride_id=ride_id)

            cur.execute(
                """INSERT INTO ratings (ride_id, user_id, rating, comment)
                   VALUES (%s, %s, %s, %s)""",
                (ride_id, user_id, rating, comment)
            )
            conn.commit()
            flash("Thank you for your rating!", "success")
            return redirect(url_for("my_rides"))

        cur.close()
    except Error:
        flash("Could not process rating.", "danger")
        return redirect(url_for("my_rides"))
    finally:
        conn.close()

    return render_template("rate_ride.html", ride_id=ride_id)


# ============================================================
# PAYMENT
# ============================================================
@app.route("/payment/<int:ride_id>", methods=["GET", "POST"])
@login_required
def payment(ride_id):
    """Pay for a ride using MTN MoMo or Orange Money."""
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("my_rides"))

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM rides WHERE id = %s AND user_id = %s",
            (ride_id, user_id)
        )
        ride = cur.fetchone()
        if not ride:
            flash("Ride not found.", "danger")
            return redirect(url_for("my_rides"))

        if ride["status"] not in ("ACCEPTED", "IN_PROGRESS", "COMPLETED"):
            flash("You can only pay for accepted rides.", "warning")
            return redirect(url_for("my_rides"))

        # Check if already paid successfully
        cur.execute(
            """SELECT id FROM payments
               WHERE ride_id = %s AND user_id = %s AND status = 'SUCCESSFUL'""",
            (ride_id, user_id)
        )
        if cur.fetchone():
            flash("This ride has already been paid.", "info")
            return redirect(url_for("payments"))

        if request.method == "POST":
            phone = request.form.get("momo_phone", "").strip()
            operator = request.form.get("operator", "").strip() or None
            if not phone or len(phone) < 9:
                flash("Please enter a valid Cameroon phone number.", "danger")
                return render_template("payment.html", ride=ride)

            # Call payment service
            result = request_payment(
                amount=float(ride["fare"]),
                phone_number=phone,
                ride_id=ride_id,
                user_id=user_id,
                operator=operator
            )

            detected_op = result.get("operator", "MOMO")

            # Store the transaction
            cur.execute(
                """INSERT INTO payments
                   (ride_id, user_id, transaction_reference, amount, phone, operator, status, gateway_response)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    ride_id,
                    user_id,
                    result.get("transaction_reference"),
                    ride["fare"],
                    phone,
                    detected_op,
                    result.get("status", "FAILED"),
                    str(result.get("gateway_response")),
                )
            )
            conn.commit()

            if result.get("success") and result.get("status") == "PENDING":
                gw_msg = result.get("message", "Approve the payment on your phone.")
                flash(
                    f"✅ {gw_msg} "
                    f"Reference: {result.get('transaction_reference')}. "
                    f"Check your phone for the {detected_op} confirmation prompt / USSD.",
                    "success"
                )
            elif result.get("status") == "SUCCESSFUL":
                flash("Payment successful!", "success")
            else:
                flash(result.get("message", "Payment failed."), "danger")

            return redirect(url_for("payments"))

        # Pre-fill phone from user profile
        cur.execute("SELECT phone FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        default_phone = user["phone"] if user else ""
        cur.close()
    except Error:
        flash("Payment page error.", "danger")
        return redirect(url_for("my_rides"))
    finally:
        conn.close()

    return render_template("payment.html", ride=ride, default_phone=default_phone)


@app.route("/payment/<int:payment_id>/verify", methods=["POST"])
@login_required
def verify_payment(payment_id):
    """Verify and confirm a PENDING payment with the gateway."""
    user_id = session["user_id"]
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("payments"))
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, ride_id, transaction_reference, status FROM payments WHERE id = %s AND user_id = %s",
            (payment_id, user_id)
        )
        pay = cur.fetchone()
        if not pay:
            flash("Payment record not found.", "danger")
            return redirect(url_for("payments"))

        if pay["status"] == "SUCCESSFUL":
            flash("Payment is already confirmed.", "info")
            return redirect(url_for("payments"))

        check = check_payment_status(pay["transaction_reference"])
        if check.get("success") and check.get("status") == "SUCCESSFUL":
            cur.execute("UPDATE payments SET status = 'SUCCESSFUL' WHERE id = %s", (payment_id,))
            conn.commit()
            flash("Payment successfully verified as SUCCESSFUL!", "success")
        else:
            flash(check.get("message", "Payment is still pending on your phone."), "warning")
        cur.close()
    except Error:
        flash("Could not verify payment.", "danger")
    finally:
        conn.close()
    return redirect(url_for("payments"))


@app.route("/payments")
@login_required
def payments():
    """Payment history for the logged-in user."""
    user_id = session["user_id"]
    payment_list = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """SELECT p.*, r.pickup, r.destination
                   FROM payments p
                   JOIN rides r ON p.ride_id = r.id
                   WHERE p.user_id = %s
                   ORDER BY p.created_at DESC""",
                (user_id,)
            )
            payment_list = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load payments.", "warning")
        finally:
            conn.close()
    return render_template("payments.html", payments=payment_list)


# ============================================================
# CARPOOL SPLIT-FARE DIRECT PAYMENT ROUTE (Co-Passengers)
# ============================================================
@app.route("/split-pay/<token>", methods=["GET", "POST"])
def split_pay(token):
    """
    Public co-passenger payment portal for split-fare carpooling.
    Allows co-passengers to pay their individual share via MTN MoMo,
    Orange Money, or USSD strings without requiring a full account.
    """
    conn = get_db()
    if not conn:
        flash("Erreur de base de données. Veuillez réessayer.", "danger")
        return redirect(url_for("home"))

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT s.*, r.pickup, r.destination, r.fare AS total_fare, r.vehicle_type, r.status AS ride_status,
                   r.split_count, r.user_id AS organizer_id, u.full_name AS organizer_name, u.phone AS organizer_phone
            FROM ride_splits s
            JOIN rides r ON s.ride_id = r.id
            JOIN users u ON r.user_id = u.id
            WHERE s.invite_token = %s
            """,
            (token,)
        )
        split = cur.fetchone()
        if not split:
            flash("Lien de paiement de covoiturage introuvable ou expiré.", "warning")
            return redirect(url_for("home"))

        # Fetch all splits for this ride to show group progress
        cur.execute(
            """
            SELECT passenger_index, passenger_name, passenger_phone, share_amount, is_paid, operator,
                   DATE_FORMAT(paid_at, '%d/%m/%Y à %H:%i') AS paid_at_fmt
            FROM ride_splits
            WHERE ride_id = %s
            ORDER BY passenger_index ASC
            """,
            (split["ride_id"],)
        )
        all_splits = cur.fetchall()
        paid_count = sum(1 for s in all_splits if s["is_paid"])

        if request.method == "POST":
            if split["is_paid"]:
                flash("Cette part de course a déjà été réglée !", "info")
                return redirect(url_for("split_pay", token=token))

            operator = request.form.get("operator", "MTN").strip().upper()
            if operator not in ("MTN", "ORANGE"):
                operator = "MTN"
            phone = request.form.get("phone", "").strip()

            clean_digits = re.sub(r"[^\d]", "", phone)
            if len(clean_digits) == 9 and clean_digits.startswith("6"):
                pass
            elif len(clean_digits) == 12 and clean_digits.startswith("2376"):
                clean_digits = clean_digits[3:]
            else:
                flash("Veuillez saisir un numéro MTN ou Orange Money valide à 9 chiffres (ex: 671234567 ou 691234567).", "danger")
                ussd = generate_split_ussd_codes(split["organizer_phone"], split["share_amount"])
                return render_template(
                    "split_pay.html",
                    split=split,
                    all_splits=all_splits,
                    paid_count=paid_count,
                    ussd=ussd
                )

            import random
            txn_ref = f"{operator}-SPLIT-2026-{random.randint(100000, 999999)}"
            cur.execute(
                """
                UPDATE ride_splits
                SET is_paid = TRUE, payment_reference = %s, paid_at = NOW(), operator = %s, passenger_phone = %s
                WHERE id = %s
                """,
                (txn_ref, operator, clean_digits, split["id"])
            )
            conn.commit()

            # Check if all splits for this ride are now paid
            cur.execute(
                "SELECT COUNT(*) AS unpaid FROM ride_splits WHERE ride_id = %s AND is_paid = FALSE",
                (split["ride_id"],)
            )
            unpaid_row = cur.fetchone()
            if unpaid_row and unpaid_row["unpaid"] == 0:
                cur.execute(
                    "SELECT id FROM payments WHERE ride_id = %s AND status = 'SUCCESSFUL'",
                    (split["ride_id"],)
                )
                if not cur.fetchone():
                    cur.execute(
                        """
                        INSERT INTO payments
                        (ride_id, user_id, transaction_reference, amount, phone, operator, status, gateway_response)
                        VALUES (%s, %s, %s, %s, %s, %s, 'SUCCESSFUL', 'All carpool co-passengers settled their individual shares')
                        """,
                        (
                            split["ride_id"],
                            split["organizer_id"],
                            f"SPLIT-ALL-{split['ride_id']}-{random.randint(1000, 9999)}",
                            split["total_fare"],
                            split["organizer_phone"],
                            "MOMO/OM SPLIT"
                        )
                    )
                    conn.commit()

            flash(
                f"✅ Part de {int(round(split['share_amount']))} FCFA réglée avec succès via {operator} Money ! Réf: {txn_ref}",
                "success"
            )
            return redirect(url_for("split_pay", token=token))

        ussd = generate_split_ussd_codes(split["organizer_phone"], split["share_amount"])
        return render_template(
            "split_pay.html",
            split=split,
            all_splits=all_splits,
            paid_count=paid_count,
            ussd=ussd
        )
    except Error as e:
        flash(f"Erreur lors du traitement du paiement partagé : {str(e)}", "danger")
        return redirect(url_for("home"))
    finally:
        conn.close()


@app.route("/api/ride/<int:ride_id>/split-status")
def api_ride_split_status(ride_id):
    """JSON endpoint for real-time polling of ride split payments."""
    conn = get_db()
    if not conn:
        return jsonify({"error": "Database error"}), 500
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT id, fare, split_enabled, split_count, split_fare_per_person
               FROM rides WHERE id = %s""",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride or not ride["split_enabled"]:
            return jsonify({"split_enabled": False})

        cur.execute(
            """
            SELECT id, passenger_index, passenger_name, passenger_phone, share_amount,
                   is_paid, payment_reference, operator, invite_token,
                   DATE_FORMAT(paid_at, '%d/%m/%Y à %H:%i') AS paid_at_formatted
            FROM ride_splits
            WHERE ride_id = %s
            ORDER BY passenger_index ASC
            """,
            (ride_id,)
        )
        splits = cur.fetchall()
        paid_count = sum(1 for s in splits if s["is_paid"])
        return jsonify({
            "split_enabled": True,
            "ride_id": ride_id,
            "split_count": ride["split_count"],
            "total_fare": float(ride["fare"]),
            "per_person": float(ride["split_fare_per_person"] or 0),
            "paid_count": paid_count,
            "all_paid": (paid_count == len(splits)),
            "splits": splits
        })
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# ============================================================
# DIGITAL PDF / PRINTABLE RECEIPT WITH QR CODE
# ============================================================
@app.route("/receipt/<int:ride_id>")
def ride_receipt(ride_id):
    """
    Generate a clean, printable official trip receipt with QR code
    for business expense reimbursement (Bonanjo/Akwa commuters).
    """
    user_id = session.get("user_id")
    driver_id = session.get("driver_id")
    admin_id = session.get("admin_id")

    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("my_rides") if user_id else url_for("index"))

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT r.*,
                   u.full_name AS rider_name, u.phone AS rider_phone, u.email AS rider_email,
                   d.full_name AS driver_name, d.phone AS driver_phone, d.vehicle_info,
                   d.vehicle_type AS driver_vtype
            FROM rides r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN drivers d ON r.driver_id = d.id
            WHERE r.id = %s
            """,
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride:
            cur.close()
            flash("Ride not found.", "danger")
            return redirect(url_for("my_rides") if user_id else url_for("index"))

        # Access check: rider, driver, admin, or guest token
        token = request.args.get("token")
        is_owner = (user_id and ride["user_id"] == user_id)
        is_driver = (driver_id and ride["driver_id"] == driver_id)
        is_admin = bool(admin_id)

        expected_token = hashlib.sha256(f"mboareceipt:{ride['id']}:{ride['fare']}".encode("utf-8")).hexdigest()[:12]
        if not (is_owner or is_driver or is_admin or token == expected_token):
            cur.close()
            if not (user_id or driver_id or admin_id):
                flash("Please log in to view this receipt.", "warning")
                return redirect(url_for("login"))
            flash("Unauthorized access to this receipt.", "danger")
            return redirect(url_for("my_rides"))

        # Fetch payment record (if any)
        cur.execute(
            """
            SELECT * FROM payments
            WHERE ride_id = %s
            ORDER BY (status = 'SUCCESSFUL') DESC, created_at DESC
            LIMIT 1
            """,
            (ride_id,)
        )
        payment_record = cur.fetchone()
        cur.close()

        # If no payment record exists yet, provide default fallback metadata
        if not payment_record:
            payment_record = {
                "transaction_reference": f"MOMO-237-DLA-{ride['id']:05d}",
                "operator": "MOMO",
                "phone": ride["rider_phone"],
                "status": "SUCCESSFUL" if ride["status"] == "COMPLETED" else "PENDING",
                "amount": ride["fare"],
                "created_at": ride["created_at"]
            }

        # Calculate fare breakdown
        vtype = ride["vehicle_type"] or "taxi"
        v_meta = VEHICLE_TYPES.get(vtype, VEHICLE_TYPES["taxi"])
        fare_total = float(ride["fare"])
        cargo_fee = float(ride.get("cargo_fee") or 0.0)
        fare_before_cargo = max(0.0, fare_total - cargo_fee)

        base_standard = int(round(fare_before_cargo / v_meta["factor"])) if v_meta["factor"] > 0 else int(fare_before_cargo)
        mode_adjustment = int(fare_before_cargo - base_standard)

        # Generate Verification URL and QR Code SVG
        verify_url = request.host_url.rstrip("/") + url_for("receipt_verify", ride_id=ride["id"], token=expected_token)
        qr_svg = ""
        try:
            import qrcode
            import qrcode.image.svg
            img = qrcode.make(verify_url, image_factory=qrcode.image.svg.SvgPathImage, box_size=8, border=2)
            qr_svg = img.to_string().decode("utf-8") if isinstance(img.to_string(), bytes) else img.to_string()
        except Exception:
            qr_svg = ""

        # Security digital signature
        security_hash = hashlib.sha256(
            f"MBOALIFT:{ride['id']}:{payment_record['transaction_reference']}:{fare_total}:{ride['created_at']}".encode("utf-8")
        ).hexdigest().upper()

        receipt_number = f"MBOA-DLA-REC-2026-{ride['id']:05d}"

        return render_template(
            "receipt.html",
            ride=ride,
            payment=payment_record,
            receipt_number=receipt_number,
            verify_url=verify_url,
            qr_svg=qr_svg,
            security_hash=security_hash,
            base_standard=base_standard,
            mode_adjustment=mode_adjustment,
            cargo_fee=cargo_fee,
            fare_total=fare_total,
            vehicle_meta=v_meta,
            expected_token=expected_token
        )
    except Error:
        flash("Could not generate receipt.", "danger")
        return redirect(url_for("my_rides") if user_id else url_for("index"))
    finally:
        conn.close()


@app.route("/receipt/verify/<int:ride_id>")
def receipt_verify(ride_id):
    """
    Public digital verification endpoint for employers, accountants, or auditors
    who scan the receipt QR code with their mobile device.
    """
    conn = get_db()
    if not conn:
        return render_template("receipt_verify.html", valid=False, error="Database connection error")

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT r.*,
                   u.full_name AS rider_name,
                   d.full_name AS driver_name, d.vehicle_info,
                   (SELECT transaction_reference FROM payments WHERE ride_id = r.id AND status = 'SUCCESSFUL' LIMIT 1) AS txn_ref,
                   (SELECT operator FROM payments WHERE ride_id = r.id AND status = 'SUCCESSFUL' LIMIT 1) AS operator,
                   (SELECT created_at FROM payments WHERE ride_id = r.id AND status = 'SUCCESSFUL' LIMIT 1) AS pay_time
            FROM rides r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN drivers d ON r.driver_id = d.id
            WHERE r.id = %s
            """,
            (ride_id,)
        )
        ride = cur.fetchone()
        cur.close()

        if not ride:
            return render_template("receipt_verify.html", valid=False, error="Course ou reçu introuvable")

        receipt_number = f"MBOA-DLA-REC-2026-{ride['id']:05d}"
        txn_ref = ride["txn_ref"] or f"MOMO-237-DLA-{ride['id']:05d}"
        v_meta = VEHICLE_TYPES.get(ride["vehicle_type"], VEHICLE_TYPES["taxi"])

        return render_template(
            "receipt_verify.html",
            valid=True,
            ride=ride,
            receipt_number=receipt_number,
            txn_ref=txn_ref,
            vehicle_meta=v_meta
        )
    except Error:
        return render_template("receipt_verify.html", valid=False, error="Erreur de vérification")
    finally:
        conn.close()


# ============================================================
# AI ASSISTANT
# ============================================================
@app.route("/ai-assistant", methods=["GET", "POST"])
@login_required
def ai_assistant():
    """Chat with the AI transportation assistant."""
    reply = None
    user_message = ""

    # Build safe context for the AI
    context = {"name": session.get("user_name")}
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """SELECT pickup, destination, fare, status
                   FROM rides WHERE user_id = %s
                   ORDER BY created_at DESC LIMIT 1""",
                (session["user_id"],)
            )
            last_ride = cur.fetchone()
            if last_ride:
                context["current_ride"] = f"{last_ride['pickup']} → {last_ride['destination']}"
                context["fare"] = f"{last_ride['fare']} XAF"
                context["ride_status"] = last_ride["status"]

            cur.execute(
                """SELECT status FROM payments
                   WHERE user_id = %s ORDER BY created_at DESC LIMIT 1""",
                (session["user_id"],)
            )
            last_pay = cur.fetchone()
            if last_pay:
                context["payment_status"] = last_pay["status"]
            cur.close()
        except Error:
            pass
        finally:
            conn.close()

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        if user_message:
            reply = get_ai_response(user_message, context)
        else:
            reply = "Please type a question."

    return render_template(
        "ai_assistant.html",
        reply=reply,
        user_message=user_message,
        context=context
    )


# ============================================================
# ADMIN ROUTES
# ============================================================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please fill in all fields.", "danger")
            return render_template("admin/login.html")

        conn = get_db()
        if not conn:
            flash("Database error.", "danger")
            return render_template("admin/login.html")

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, username, password_hash FROM admins WHERE username = %s",
                (username,)
            )
            admin = cur.fetchone()
            if admin and check_password_hash(admin["password_hash"], password):
                session.clear()
                session["admin_id"] = admin["id"]
                session["admin_name"] = admin["username"]
                flash("Admin login successful.", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid username or password.", "danger")
            cur.close()
        except Error:
            flash("Login error.", "danger")
        finally:
            conn.close()

    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("Admin logged out.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin overview statistics."""
    stats = {
        "users": 0, "drivers": 0, "rides": 0, "pending": 0, "accepted": 0,
        "completed": 0, "cancelled": 0,
        "pay_success": 0, "pay_pending": 0, "pay_failed": 0,
        "total_money": 0
    }
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT COUNT(*) AS c FROM users")
            stats["users"] = cur.fetchone()["c"]

            cur.execute("SELECT COUNT(*) AS c FROM drivers")
            stats["drivers"] = cur.fetchone()["c"]

            cur.execute("SELECT status, COUNT(*) AS c FROM rides GROUP BY status")
            for row in cur.fetchall():
                stats["rides"] += row["c"]
                if row["status"] == "PENDING":
                    stats["pending"] = row["c"]
                elif row["status"] == "ACCEPTED":
                    stats["accepted"] = row["c"]
                elif row["status"] == "COMPLETED":
                    stats["completed"] = row["c"]
                elif row["status"] == "CANCELLED":
                    stats["cancelled"] = row["c"]

            cur.execute("SELECT status, COUNT(*) AS c FROM payments GROUP BY status")
            for row in cur.fetchall():
                if row["status"] == "SUCCESSFUL":
                    stats["pay_success"] = row["c"]
                elif row["status"] == "PENDING":
                    stats["pay_pending"] = row["c"]
                elif row["status"] == "FAILED":
                    stats["pay_failed"] = row["c"]

            cur.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE status = 'SUCCESSFUL'"
            )
            stats["total_money"] = cur.fetchone()["total"]
            cur.close()
        except Error:
            flash("Could not load statistics.", "warning")
        finally:
            conn.close()

    return render_template("admin/dashboard.html", stats=stats)


@app.route("/admin/users")
@admin_required
def admin_users():
    """List and search users."""
    search = request.args.get("q", "").strip()
    users = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            if search:
                cur.execute(
                    """SELECT id, full_name, phone, email, status, created_at
                       FROM users
                       WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s
                       ORDER BY created_at DESC""",
                    (f"%{search}%", f"%{search}%", f"%{search}%")
                )
            else:
                cur.execute(
                    """SELECT id, full_name, phone, email, status, created_at
                       FROM users ORDER BY created_at DESC"""
                )
            users = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load users.", "warning")
        finally:
            conn.close()
    return render_template("admin/users.html", users=users, search=search)


@app.route("/admin/user/<int:user_id>/disable", methods=["POST"])
@admin_required
def admin_disable_user(user_id):
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET status = 'disabled' WHERE id = %s",
                (user_id,)
            )
            conn.commit()
            flash("User disabled.", "success")
            cur.close()
        except Error:
            flash("Could not disable user.", "danger")
        finally:
            conn.close()
    return redirect(url_for("admin_users"))


@app.route("/admin/user/<int:user_id>/enable", methods=["POST"])
@admin_required
def admin_enable_user(user_id):
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE users SET status = 'active' WHERE id = %s",
                (user_id,)
            )
            conn.commit()
            flash("User enabled.", "success")
            cur.close()
        except Error:
            flash("Could not enable user.", "danger")
        finally:
            conn.close()
    return redirect(url_for("admin_users"))


@app.route("/admin/user/<int:user_id>/delete", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            flash("User deleted.", "success")
            cur.close()
        except Error:
            flash("Could not delete user (may have related records).", "danger")
        finally:
            conn.close()
    return redirect(url_for("admin_users"))


@app.route("/admin/drivers")
@admin_required
def admin_drivers():
    """List and search drivers."""
    search = request.args.get("q", "").strip()
    vehicle_filter = request.args.get("vehicle_type", "").strip()
    status_filter = request.args.get("status", "").strip()
    drivers = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            sql = """
                SELECT id, full_name, phone, email, vehicle_info, vehicle_type,
                       current_location, availability, status, created_at,
                       (SELECT COUNT(*) FROM rides r WHERE r.driver_id = drivers.id AND r.status = 'COMPLETED') AS completed_rides
                FROM drivers
                WHERE 1=1
            """
            params = []
            if search:
                sql += " AND (full_name LIKE %s OR email LIKE %s OR phone LIKE %s OR vehicle_info LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])
            if vehicle_filter:
                sql += " AND vehicle_type = %s"
                params.append(vehicle_filter)
            if status_filter:
                sql += " AND status = %s"
                params.append(status_filter)
            sql += " ORDER BY created_at DESC"
            cur.execute(sql, params)
            drivers = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load drivers.", "warning")
        finally:
            conn.close()
    return render_template(
        "admin/drivers.html",
        drivers=drivers,
        search=search,
        vehicle_filter=vehicle_filter,
        status_filter=status_filter
    )


@app.route("/admin/driver/<int:driver_id>/disable", methods=["POST"])
@admin_required
def admin_disable_driver(driver_id):
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE drivers SET status = 'disabled' WHERE id = %s",
                (driver_id,)
            )
            conn.commit()
            flash("Driver account disabled.", "success")
            cur.close()
        except Error:
            flash("Could not disable driver.", "danger")
        finally:
            conn.close()
    return redirect(url_for("admin_drivers"))


@app.route("/admin/driver/<int:driver_id>/enable", methods=["POST"])
@admin_required
def admin_enable_driver(driver_id):
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "UPDATE drivers SET status = 'active' WHERE id = %s",
                (driver_id,)
            )
            conn.commit()
            flash("Driver account enabled.", "success")
            cur.close()
        except Error:
            flash("Could not enable driver.", "danger")
        finally:
            conn.close()
    return redirect(url_for("admin_drivers"))


@app.route("/admin/driver/<int:driver_id>/delete", methods=["POST"])
@admin_required
def admin_delete_driver(driver_id):
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM drivers WHERE id = %s", (driver_id,))
            conn.commit()
            flash("Driver deleted.", "success")
            cur.close()
        except Error:
            flash("Could not delete driver (may have related records).", "danger")
        finally:
            conn.close()
    return redirect(url_for("admin_drivers"))


@app.route("/admin/rides")
@admin_required
def admin_rides():
    """List and search rides."""
    search = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    rides = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            sql = """
                SELECT r.*, u.full_name, u.phone
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE 1=1
            """
            params = []
            if search:
                sql += " AND (u.full_name LIKE %s OR r.pickup LIKE %s OR r.destination LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            if status_filter:
                sql += " AND r.status = %s"
                params.append(status_filter)
            sql += " ORDER BY r.created_at DESC"
            cur.execute(sql, params)
            rides = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load rides.", "warning")
        finally:
            conn.close()
    return render_template(
        "admin/rides.html",
        rides=rides,
        search=search,
        status_filter=status_filter
    )


@app.route("/admin/ride/<int:ride_id>/accept", methods=["POST"])
@admin_required
def admin_accept_ride(ride_id):
    return _update_ride_status(ride_id, "ACCEPTED", "PENDING")


@app.route("/admin/ride/<int:ride_id>/cancel", methods=["POST"])
@admin_required
def admin_cancel_ride(ride_id):
    return _update_ride_status(ride_id, "CANCELLED", None)


@app.route("/admin/ride/<int:ride_id>/start", methods=["POST"])
@admin_required
def admin_start_ride(ride_id):
    return _update_ride_status(ride_id, "IN_PROGRESS", "ACCEPTED")


@app.route("/admin/ride/<int:ride_id>/complete", methods=["POST"])
@admin_required
def admin_complete_ride(ride_id):
    return _update_ride_status(ride_id, "COMPLETED", "IN_PROGRESS")


def _update_ride_status(ride_id, new_status, expected_current=None):
    """
    Helper to change ride status safely.

    Extra rule (simple ride-hailing behaviour):
    When a ride is ACCEPTED, all other PENDING rides from the same user
    are automatically CANCELLED. This way only one ride is "taken"
    and the rest are freed / cancelled for others.
    """
    conn = get_db()
    if not conn:
        flash("Database error.", "danger")
        return redirect(url_for("admin_rides"))
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, user_id, status FROM rides WHERE id = %s",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride:
            flash("Ride not found.", "danger")
            return redirect(url_for("admin_rides"))

        if expected_current and ride["status"] != expected_current:
            flash(
                f"Ride must be {expected_current} before changing to {new_status}.",
                "warning"
            )
            return redirect(url_for("admin_rides"))

        # Update the selected ride
        cur.execute(
            "UPDATE rides SET status = %s WHERE id = %s",
            (new_status, ride_id)
        )

        # If this ride was just ACCEPTED → cancel the user's other PENDING rides
        cancelled_count = 0
        if new_status == "ACCEPTED":
            cur.execute(
                """UPDATE rides
                   SET status = 'CANCELLED'
                   WHERE user_id = %s
                     AND status = 'PENDING'
                     AND id != %s""",
                (ride["user_id"], ride_id)
            )
            cancelled_count = cur.rowcount

        conn.commit()

        if new_status == "ACCEPTED" and cancelled_count > 0:
            flash(
                f"Ride marked as ACCEPTED. "
                f"{cancelled_count} other pending ride(s) for this user were automatically cancelled.",
                "success"
            )
        else:
            flash(f"Ride marked as {new_status}.", "success")
        cur.close()
    except Error:
        flash("Could not update ride.", "danger")
    finally:
        conn.close()
    return redirect(url_for("admin_rides"))


@app.route("/admin/payments")
@admin_required
def admin_payments():
    """Monitor all payments."""
    search = request.args.get("q", "").strip()
    payments_list = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            sql = """
                SELECT p.*, u.full_name, r.pickup, r.destination
                FROM payments p
                JOIN users u ON p.user_id = u.id
                JOIN rides r ON p.ride_id = r.id
                WHERE 1=1
            """
            params = []
            if search:
                sql += " AND (p.transaction_reference LIKE %s OR u.full_name LIKE %s OR p.phone LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            sql += " ORDER BY p.created_at DESC"
            cur.execute(sql, params)
            payments_list = cur.fetchall()
            cur.close()
        except Error:
            flash("Could not load payments.", "warning")
        finally:
            conn.close()
    return render_template("admin/payments.html", payments=payments_list, search=search)


# ============================================================
# API endpoint for fare calculation (used by JavaScript)
# ============================================================
@app.route("/api/fare")
def api_fare():
    """Return fare for a given pickup/destination, optional vehicle_type, and optional cargo_type (JSON)."""
    pickup = normalize_location(request.args.get("pickup", ""))
    destination = normalize_location(request.args.get("destination", ""))
    vehicle_type = request.args.get("vehicle_type", "taxi").lower()
    cargo_type = request.args.get("cargo_type", "none").strip().lower()

    if vehicle_type not in VEHICLE_TYPES:
        vehicle_type = "taxi"

    if cargo_type not in CARGO_OPTIONS:
        cargo_type = "none"

    # Enforce safety constraints: Bendskin cannot carry market goods or heavy luggage
    if cargo_type in ("market", "heavy") and vehicle_type == "bendskin":
        vehicle_type = "taxi"

    if not pickup or not destination or pickup == destination:
        return jsonify({"fare": None, "error": "Invalid locations"})

    base_fare = get_fare(pickup, destination, vehicle_type)
    cargo_meta = CARGO_OPTIONS.get(cargo_type, CARGO_OPTIONS["none"])
    cargo_fee = int(cargo_meta.get("fee", 0))
    total_fare = (base_fare + cargo_fee) if base_fare is not None else None

    v_labels = {
        "bendskin": {"en": "Bendskin (Moto-Taxi) 🏍️", "fr": "Bendskin (Moto-Taxi) 🏍️"},
        "taxi": {"en": "Yellow Taxi (Standard) 🚕", "fr": "Taxi Jaune (Standard) 🚕"},
        "comfort": {"en": "Comfort Car (Private VIP) 🚗", "fr": "Voiture Confort (Privé VIP) 🚗"},
    }
    active_lang = getattr(g, "lang", "en")
    label = v_labels.get(vehicle_type, {}).get(active_lang, VEHICLE_TYPES[vehicle_type]["label"])

    return jsonify({
        "fare": total_fare,
        "base_fare": base_fare,
        "cargo_fee": cargo_fee,
        "cargo_type": cargo_type,
        "cargo_label": cargo_meta.get(f"label_{active_lang}", cargo_meta["label_fr"]),
        "currency": "XAF",
        "vehicle_type": vehicle_type,
        "vehicle_label": label
    })


@app.route("/api/nearby-drivers")
@login_required
def api_nearby_drivers():
    """
    Return free drivers near a pickup location (JSON).
    Filters by cargo compatibility if cargo_type is 'market' or 'heavy' (requires trunk or roof rack).
    """
    pickup = normalize_location(request.args.get("pickup", ""))
    cargo_type = request.args.get("cargo_type", "none").strip().lower()

    if not pickup:
        return jsonify({"drivers": []})

    nearby = get_nearby_locations(pickup)
    drivers = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            placeholders = ",".join(["%s"] * len(nearby))
            sql = f"""
                SELECT id, full_name, phone, vehicle_info, vehicle_type, current_location, has_trunk, has_roof_rack
                FROM drivers
                WHERE status = 'active'
                  AND availability = 'free'
                  AND current_location IN ({placeholders})
            """
            params = list(nearby)
            if cargo_type in ("market", "heavy"):
                sql += " AND vehicle_type != 'bendskin' AND (has_trunk = 1 OR has_roof_rack = 1 OR vehicle_type IN ('taxi', 'comfort'))"

            sql += " ORDER BY current_location, full_name"
            cur.execute(sql, tuple(params))
            drivers = cur.fetchall()
            cur.close()
        except Error:
            drivers = []
        finally:
            conn.close()
    return jsonify({"drivers": drivers, "pickup": pickup, "cargo_type": cargo_type})


@app.route("/api/map-data")
def api_map_data():
    """
    Return Douala coordinates, landmarks, active nearby free drivers,
    and pending available rides (for drivers) in JSON for the interactive map.
    """
    conn = get_db()
    active_drivers = []
    available_rides = []
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            # Free active drivers
            cur.execute(
                """SELECT id, full_name, phone, vehicle_info, vehicle_type, current_location
                   FROM drivers
                   WHERE status = 'active' AND availability = 'free' AND current_location IS NOT NULL"""
            )
            for d in cur.fetchall():
                loc = d.get("current_location")
                coords = DOUALA_COORDINATES.get(loc)
                if coords:
                    active_drivers.append({
                        "id": d["id"],
                        "name": d["full_name"],
                        "phone": d["phone"],
                        "vehicle_type": d["vehicle_type"],
                        "vehicle_info": d["vehicle_info"] or "",
                        "location": loc,
                        "lat": coords["lat"],
                        "lng": coords["lng"]
                    })

            # Pending rides for drivers
            cur.execute(
                """SELECT r.id, r.pickup, r.destination, r.fare, r.vehicle_type, u.full_name AS rider_name
                   FROM rides r
                   JOIN users u ON r.user_id = u.id
                   WHERE r.status = 'PENDING'
                   ORDER BY r.created_at DESC LIMIT 10"""
            )
            for r in cur.fetchall():
                p_coords = DOUALA_COORDINATES.get(r["pickup"])
                d_coords = DOUALA_COORDINATES.get(r["destination"])
                available_rides.append({
                    "id": r["id"],
                    "pickup": r["pickup"],
                    "destination": r["destination"],
                    "fare": float(r["fare"]),
                    "vehicle_type": r["vehicle_type"],
                    "rider_name": r["rider_name"],
                    "pickup_lat": p_coords["lat"] if p_coords else None,
                    "pickup_lng": p_coords["lng"] if p_coords else None,
                    "dest_lat": d_coords["lat"] if d_coords else None,
                    "dest_lng": d_coords["lng"] if d_coords else None,
                })
            cur.close()
        except Error:
            pass
        finally:
            conn.close()

    return jsonify({
        "center": {"lat": 4.0511, "lng": 9.7150},
        "coordinates": DOUALA_COORDINATES,
        "landmarks": DOUALA_LANDMARKS,
        "active_drivers": active_drivers,
        "available_rides": available_rides
    })


@app.route("/api/driver/alerts")
def api_driver_alerts():
    """
    Lightweight real-time endpoint for Driver Voice Announcements.
    Returns latest pending available rides in Douala for speech synthesis alerts,
    including street negotiation counter-offers.
    """
    conn = get_db()
    rides = []
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.fare, r.original_fare, r.negotiation_status,
                       r.driver_counter_fare, r.vehicle_type, r.cargo_type, r.cargo_fee, r.passengers,
                       r.created_at, u.full_name AS rider_name,
                       r.is_scheduled, r.scheduled_time, r.scheduled_type, r.flight_or_shift_notes
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'PENDING' AND r.driver_id IS NULL
                ORDER BY r.is_scheduled DESC, r.created_at DESC LIMIT 15
                """
            )
            for r in cur.fetchall():
                orig_fare = float(r["original_fare"]) if r.get("original_fare") is not None else float(r["fare"])
                cur_fare = float(r["fare"])
                neg_status = r.get("negotiation_status") or "NONE"
                is_neg = (neg_status == "PROPOSED") or (abs(orig_fare - cur_fare) >= 1.0)
                rides.append({
                    "id": r["id"],
                    "pickup": r["pickup"],
                    "destination": r["destination"],
                    "fare": int(round(cur_fare)),
                    "original_fare": int(round(orig_fare)),
                    "negotiation_status": neg_status,
                    "is_negotiated": is_neg,
                    "driver_counter_fare": int(round(float(r["driver_counter_fare"]))) if r.get("driver_counter_fare") else None,
                    "vehicle_type": r["vehicle_type"],
                    "cargo_type": r.get("cargo_type") or "none",
                    "cargo_fee": int(round(float(r.get("cargo_fee") or 0))),
                    "passengers": r["passengers"],
                    "rider_name": r["rider_name"],
                    "is_scheduled": bool(r.get("is_scheduled")),
                    "scheduled_time": r["scheduled_time"].strftime("%d/%m %H:%M") if r.get("scheduled_time") else None,
                    "scheduled_type": r.get("scheduled_type") or "standard",
                    "flight_or_shift_notes": r.get("flight_or_shift_notes") or "",
                    "created_at": r["created_at"].isoformat() if r["created_at"] else None
                })
            cur.close()
        except Error:
            pass
        finally:
            conn.close()

    return jsonify({
        "success": True,
        "count": len(rides),
        "rides": rides,
        "server_time": datetime.now().isoformat()
    })


@app.route("/api/ride-status/<int:ride_id>")
def api_ride_status(ride_id):
    """
    Return real-time live status, driver assignment, street negotiation status, and ETA progress for a ride.
    """
    user_id = session.get("user_id")
    driver_id = session.get("driver_id")
    admin_id = session.get("admin_id")

    conn = get_db()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT r.id, r.user_id, r.driver_id, r.pickup, r.destination, r.passengers,
                   r.vehicle_type, r.cargo_type, r.cargo_fee, r.fare, r.original_fare, r.negotiation_status, r.driver_counter_fare, r.counter_driver_id,
                   r.status, r.created_at,
                   u.full_name AS rider_name, u.phone AS rider_phone,
                   d.full_name AS driver_name, d.phone AS driver_phone,
                   d.vehicle_info, d.current_location AS driver_location,
                   cd.full_name AS counter_driver_name, cd.phone AS counter_driver_phone, cd.vehicle_info AS counter_driver_vehicle,
                   (SELECT status FROM payments p WHERE p.ride_id = r.id ORDER BY p.created_at DESC LIMIT 1) AS payment_status,
                   (SELECT id FROM payments p WHERE p.ride_id = r.id ORDER BY p.created_at DESC LIMIT 1) AS payment_id
            FROM rides r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN drivers d ON r.driver_id = d.id
            LEFT JOIN drivers cd ON r.counter_driver_id = cd.id
            WHERE r.id = %s
            """,
            (ride_id,)
        )
        ride = cur.fetchone()
        cur.close()
        if not ride:
            return jsonify({"error": "Ride not found"}), 404

        # Security check: must be logged in as rider, driver, or admin
        if not (admin_id or (user_id and ride["user_id"] == user_id) or (driver_id and (ride["driver_id"] == driver_id or ride["counter_driver_id"] == driver_id))):
            return jsonify({"error": "Unauthorized"}), 403

        status = ride["status"]
        step = 1
        label = "Recherche d'un chauffeur disponible..."
        eta = "1-3 min"

        if status == "PENDING":
            step = 1
            if ride.get("negotiation_status") == "COUNTERED":
                c_amt = int(round(float(ride["driver_counter_fare"]))) if ride.get("driver_counter_fare") else 0
                label = f"Contre-offre reçue d'un chauffeur : {c_amt} XAF"
            elif ride.get("negotiation_status") == "PROPOSED":
                label = f"Offre négociée soumise ({int(round(float(ride['fare'])))} XAF) · En attente d'un chauffeur..."
            else:
                label = "Recherche d'un chauffeur à proximité..."
            eta = "1-3 min"
        elif status == "ACCEPTED":
            step = 2
            dname = ride["driver_name"] or "assigné"
            label = f"Chauffeur {dname} en route vers {ride['pickup']}"
            eta = "2-4 min"
        elif status == "IN_PROGRESS":
            step = 3
            label = f"Course en cours vers {ride['destination']}"
            eta = "En route"
        elif status == "COMPLETED":
            step = 4
            label = "Arrivé à destination ! Course terminée."
            eta = "Arrivé"
        elif status == "CANCELLED":
            step = 0
            label = "Course annulée"
            eta = "Annulé"

        p_coords = DOUALA_COORDINATES.get(ride["pickup"])
        d_coords = DOUALA_COORDINATES.get(ride["destination"])
        drv_coords = DOUALA_COORDINATES.get(ride["driver_location"])

        orig_fare = float(ride["original_fare"]) if ride.get("original_fare") is not None else float(ride["fare"])
        cur_fare = float(ride["fare"])
        neg_status = ride.get("negotiation_status") or "NONE"

        return jsonify({
            "id": ride["id"],
            "status": status,
            "step": step,
            "label": label,
            "eta": eta,
            "pickup": ride["pickup"],
            "destination": ride["destination"],
            "pickup_coords": p_coords,
            "dest_coords": d_coords,
            "driver_coords": drv_coords,
            "fare": cur_fare,
            "original_fare": orig_fare,
            "negotiation_status": neg_status,
            "is_negotiated": (neg_status == "PROPOSED") or (abs(orig_fare - cur_fare) >= 1.0),
            "driver_counter_fare": float(ride["driver_counter_fare"]) if ride.get("driver_counter_fare") else None,
            "counter_driver_id": ride.get("counter_driver_id"),
            "counter_driver_name": ride.get("counter_driver_name"),
            "counter_driver_phone": ride.get("counter_driver_phone"),
            "counter_driver_vehicle": ride.get("counter_driver_vehicle"),
            "vehicle_type": ride["vehicle_type"],
            "rider_name": ride["rider_name"],
            "rider_phone": ride["rider_phone"],
            "driver_name": ride["driver_name"],
            "driver_phone": ride["driver_phone"],
            "vehicle_info": ride["vehicle_info"],
            "driver_location": ride["driver_location"],
            "payment_status": ride["payment_status"],
            "payment_id": ride["payment_id"],
            "is_paid": ride["payment_status"] == "SUCCESSFUL"
        })
    except Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/weather-traffic", methods=["GET", "POST"])
def api_weather_traffic():
    """
    Get or change the active Douala weather & traffic alert condition.
    GET: returns active condition and list of available conditions.
    POST: updates condition (key in query or JSON: 'torrential_rain', 'wouri_jam', 'moderate_rain', 'clear_traffic').
    """
    global CURRENT_WEATHER_CONDITION
    cond = request.args.get("condition")
    if not cond and request.is_json:
        cond = (request.get_json(silent=True) or {}).get("condition")

    if cond and cond in DOUALA_WEATHER_CONDITIONS:
        CURRENT_WEATHER_CONDITION = cond
        session["weather_condition"] = cond

    active_alert = get_active_weather_alert()
    active_lang = getattr(g, "lang", "en") if hasattr(g, "lang") else session.get("lang", "fr")

    conditions_summary = []
    for k, v in DOUALA_WEATHER_CONDITIONS.items():
        conditions_summary.append({
            "id": k,
            "icon": v["icon"],
            "level": v["level"],
            "badge": v.get(f"badge_{active_lang}", v["badge_fr"]),
            "title": v.get(f"title_{active_lang}", v["title_fr"]),
            "message": v.get(f"message_{active_lang}", v["message_fr"]),
            "is_active": k == active_alert["id"]
        })

    return jsonify({
        "active": active_alert,
        "all_conditions": conditions_summary,
        "current_id": active_alert["id"]
    })


@app.route("/api/ussd-simulate", methods=["POST"])
def api_ussd_simulate():
    """
    Simulate an offline Douala USSD dial string (*999*...#) or SMS booking format.
    Calculates exact fare, validates locations, generates native dialer URL and SMS body.
    If requested and passenger is logged in, optionally provisions the ride in DB.
    """
    data = request.get_json(silent=True) or {}
    pickup_in = str(data.get("pickup", "")).strip()
    dest_in = str(data.get("destination", "")).strip()
    v_type_in = str(data.get("vehicle_type", "taxi")).strip().lower()
    ussd_raw = str(data.get("ussd_string", "")).strip()
    create_ride = bool(data.get("create_ride", False))

    # Parse USSD string if provided in format *999*...#
    if ussd_raw:
        clean_u = ussd_raw.replace("#", "").replace("*", " ").strip().split()
        if len(clean_u) >= 3 and clean_u[0] == "999":
            p_arg = clean_u[1]
            d_arg = clean_u[2]
            m_arg = clean_u[3] if len(clean_u) > 3 else "2"

            if p_arg.isdigit() and int(p_arg) in DOUALA_LOCATION_CODES:
                pickup_in = DOUALA_LOCATION_CODES[int(p_arg)]
            else:
                pickup_in = normalize_location(p_arg) or pickup_in

            if d_arg.isdigit() and int(d_arg) in DOUALA_LOCATION_CODES:
                dest_in = DOUALA_LOCATION_CODES[int(d_arg)]
            else:
                dest_in = normalize_location(d_arg) or dest_in

            if m_arg.isdigit() and int(m_arg) in VEHICLE_MODE_CODES:
                v_type_in = VEHICLE_MODE_CODES[int(m_arg)]
            elif m_arg.lower() in MODE_TO_CODE:
                v_type_in = VEHICLE_MODE_CODES[MODE_TO_CODE[m_arg.lower()]]

    # Normalize locations
    pickup = normalize_location(pickup_in) or "Akwa"
    destination = normalize_location(dest_in) or "Bonanjo"
    if pickup == destination:
        destination = "Bonanjo" if pickup != "Bonanjo" else "Akwa"

    if v_type_in not in VEHICLE_TYPES:
        v_type_in = "taxi"

    fare = get_fare(pickup, destination, v_type_in)
    v_info = VEHICLE_TYPES[v_type_in]

    p_code = LOCATION_TO_CODE.get(pickup.lower(), 1)
    d_code = LOCATION_TO_CODE.get(destination.lower(), 2)
    m_code = MODE_TO_CODE.get(v_type_in, 2)

    generated_ussd = f"*999*{p_code}*{d_code}*{m_code}#"
    mnemonic_ussd = f"*999*{pickup.upper()}*{destination.upper()}#"
    sms_body = f"MBOA {pickup.upper()} {destination.upper()} {v_type_in.upper()}"
    dial_url = f"tel:%2A999%2A{p_code}%2A{d_code}%2A{m_code}%23"
    sms_url = f"sms:8800?body={sms_body.replace(' ', '%20')}"

    ride_id = None
    if create_ride and session.get("user_id"):
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO rides
                       (user_id, pickup, destination, passengers, vehicle_type, fare, status)
                       VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')""",
                    (session["user_id"], pickup, destination, 1, v_type_in, fare)
                )
                conn.commit()
                ride_id = cur.lastrowid
                cur.close()
            except Error:
                pass
            finally:
                conn.close()

    screen_lines = [
        "==============================",
        "  MBOALIFT USSD SERVICE 237   ",
        "==============================",
        "✓ Course confirmée !",
        f"• Départ : {pickup}",
        f"• Arrivée : {destination}",
        f"• Mode : {v_info['label']}",
        f"• Tarif garanti : {fare} XAF",
        "------------------------------",
        "Chauffeur assigné sous 2-4 min.",
        "Paiement à l'arrivée (Cash/MoMo).",
        "Pour annuler, composez *999*0#"
    ]

    return jsonify({
        "success": True,
        "pickup": pickup,
        "destination": destination,
        "pickup_code": p_code,
        "dest_code": d_code,
        "vehicle_type": v_type_in,
        "vehicle_label": v_info["label"],
        "fare": fare,
        "currency": "XAF",
        "ussd_code": generated_ussd,
        "ussd_mnemonic": mnemonic_ussd,
        "dial_url": dial_url,
        "sms_body": sms_body,
        "sms_number": "8800",
        "sms_url": sms_url,
        "screen_text": "\n".join(screen_lines),
        "screen_lines": screen_lines,
        "ride_id": ride_id
    })


@app.route("/api/ai-chat", methods=["POST"])
def api_ai_chat():
    """
    Simple JSON endpoint used by the floating chatbot on every page.
    Expects: { "message": "user question" }
    Returns: { "reply": "assistant answer" }
    """
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a question."})

    # Build safe context if the user is logged in
    context = {}
    if session.get("user_id"):
        context["name"] = session.get("user_name")
        conn = get_db()
        if conn:
            try:
                cur = conn.cursor(dictionary=True)
                cur.execute(
                    """SELECT pickup, destination, fare, status
                       FROM rides WHERE user_id = %s
                       ORDER BY created_at DESC LIMIT 1""",
                    (session["user_id"],)
                )
                last_ride = cur.fetchone()
                if last_ride:
                    context["current_ride"] = f"{last_ride['pickup']} → {last_ride['destination']}"
                    context["fare"] = f"{last_ride['fare']} XAF"
                    context["ride_status"] = last_ride["status"]

                cur.execute(
                    """SELECT status FROM payments
                       WHERE user_id = %s ORDER BY created_at DESC LIMIT 1""",
                    (session["user_id"],)
                )
                last_pay = cur.fetchone()
                if last_pay:
                    context["payment_status"] = last_pay["status"]
                cur.close()
            except Error:
                pass
            finally:
                conn.close()

    reply = get_ai_response(user_message, context if context else None)
    return jsonify({"reply": reply})


# ============================================================
# ERROR HANDLERS
# ============================================================
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    # Create default admin on first run
    init_admin()
    app.run(debug=True, host="0.0.0.0", port=5000)
