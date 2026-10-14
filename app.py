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
from functools import wraps
from datetime import datetime

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
    """Inject current_lang into all templates."""
    return dict(current_lang=getattr(g, "lang", "en"))


# ============================================================
# DOUALA LOCATIONS & FARE MATRIX (used by both JS and Flask)
# ============================================================
LOCATIONS = [
    "Akwa", "Bonanjo", "Bonamoussadi", "Deido", "Bépanda", "Makepe",
    "Bonapriso", "Bali", "New Bell", "Ndokoti", "Logbessou",
    "Bonabéri", "Aéroport", "Japoma", "Cité des Palmiers"
]

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


def init_admin():
    """Create a default admin if none exists."""
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


@app.route("/driver/dashboard")
@driver_required
def driver_dashboard():
    """Driver dashboard: stats + earnings + quick links."""
    driver_id = session["driver_id"]
    stats = {"available": 0, "my_active": 0, "completed": 0, "total_earned": 0}
    active_mission = None
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
            cur.close()
        except Error:
            flash("Could not load driver stats.", "warning")
        finally:
            conn.close()

    return render_template(
        "driver/dashboard.html",
        stats=stats,
        active_mission=active_mission,
        driver_name=session.get("driver_name")
    )


@app.route("/driver/available-rides")
@driver_required
def driver_available_rides():
    """List PENDING rides that any driver can accept."""
    rides = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.passengers, r.vehicle_type, r.fare,
                       r.status, r.created_at, u.full_name AS rider_name, u.phone AS rider_phone
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE r.status = 'PENDING' AND r.driver_id IS NULL
                ORDER BY r.created_at ASC
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
    """Rides accepted by this driver."""
    driver_id = session["driver_id"]
    rides = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.passengers, r.vehicle_type, r.fare,
                       r.status, r.created_at, u.full_name AS rider_name, u.phone AS rider_phone
                FROM rides r
                JOIN users u ON r.user_id = u.id
                WHERE r.driver_id = %s
                ORDER BY r.created_at DESC
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
    Driver accepts a PENDING ride.
    - Sets driver_id and status = ACCEPTED
    - Other drivers can no longer take this ride
    - Other PENDING rides of the same rider are cancelled
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
            "SELECT id, user_id, status, driver_id FROM rides WHERE id = %s",
            (ride_id,)
        )
        ride = cur.fetchone()
        if not ride:
            flash("Ride not found.", "danger")
            return redirect(url_for("driver_available_rides"))

        if ride["status"] != "PENDING" or ride["driver_id"] is not None:
            flash("This ride was already taken by another driver.", "warning")
            return redirect(url_for("driver_available_rides"))

        # Assign this driver and mark driver as busy
        cur.execute(
            """UPDATE rides
               SET status = 'ACCEPTED', driver_id = %s
               WHERE id = %s AND status = 'PENDING' AND driver_id IS NULL""",
            (driver_id, ride_id)
        )
        if cur.rowcount == 0:
            flash("This ride was already taken by another driver.", "warning")
            conn.rollback()
            return redirect(url_for("driver_available_rides"))

        cur.execute(
            "UPDATE drivers SET availability = 'busy' WHERE id = %s",
            (driver_id,)
        )

        # Cancel other PENDING rides of the same passenger
        cur.execute(
            """UPDATE rides
               SET status = 'CANCELLED'
               WHERE user_id = %s AND status = 'PENDING' AND id != %s""",
            (ride["user_id"], ride_id)
        )
        cancelled = cur.rowcount
        conn.commit()

        msg = "Ride accepted successfully!"
        if cancelled > 0:
            msg += f" {cancelled} other pending request(s) from this rider were cancelled."
        flash(msg, "success")
        cur.close()
    except Error:
        flash("Could not accept ride.", "danger")
    finally:
        conn.close()
    return redirect(url_for("driver_my_rides"))


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
            if availability not in ("free", "busy"):
                availability = "free"
            if not location:
                flash("Please choose a valid Douala location.", "danger")
            else:
                cur.execute(
                    """UPDATE drivers
                       SET current_location = %s, availability = %s
                       WHERE id = %s""",
                    (location, availability, driver_id)
                )
                conn.commit()
                flash("Your location and availability were updated.", "success")

        cur.execute(
            """SELECT full_name, current_location, availability, vehicle_info
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
            # Active ongoing ride (ACCEPTED or IN_PROGRESS)
            cur.execute(
                """
                SELECT r.id, r.pickup, r.destination, r.fare, r.status, r.vehicle_type, r.created_at,
                       d.full_name AS driver_name, d.phone AS driver_phone, d.vehicle_info, d.current_location AS driver_location
                FROM rides r
                LEFT JOIN drivers d ON r.driver_id = d.id
                WHERE r.user_id = %s AND r.status IN ('ACCEPTED', 'IN_PROGRESS')
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
            cur.close()
        except Error:
            flash("Could not load dashboard data.", "warning")
        finally:
            conn.close()

    return render_template(
        "dashboard.html",
        stats=stats,
        recent=recent,
        unpaid=unpaid,
        active_ride=active_ride,
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

        def _reload_form():
            return render_template(
                "request_ride.html",
                locations=LOCATIONS,
                vehicle_types=VEHICLE_TYPES,
                nearby_drivers=nearby_drivers,
                selected_pickup=request.form.get("pickup", ""),
                selected_destination=request.form.get("destination", ""),
                selected_vehicle_type=vehicle_type,
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
            flash("Number of passengers must be between 1 and 4.", "danger")
            return _reload_form()

        # Enforce passenger limit for bendskin moto-taxi
        if vehicle_type == "bendskin" and passengers > 1:
            passengers = 1
            flash("Bendskin moto-taxi is strictly limited to 1 passenger for road safety in Douala.", "info")

        fare = get_fare(pickup, destination, vehicle_type)
        if fare is None:
            flash("Could not calculate fare for this route.", "danger")
            return _reload_form()

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
            if driver_id:
                cur.execute(
                    """SELECT id FROM drivers
                       WHERE id = %s AND status = 'active' AND availability = 'free'""",
                    (driver_id,)
                )
                if cur.fetchone():
                    cur.execute(
                        """INSERT INTO rides
                           (user_id, driver_id, pickup, destination, passengers, vehicle_type, fare, status)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, 'ACCEPTED')""",
                        (session["user_id"], driver_id, pickup, destination, passengers, vehicle_type, fare)
                    )
                    cur.execute(
                        "UPDATE drivers SET availability = 'busy' WHERE id = %s",
                        (driver_id,)
                    )
                    # Cancel other pending rides of this passenger
                    cur.execute(
                        """UPDATE rides SET status = 'CANCELLED'
                           WHERE user_id = %s AND status = 'PENDING'""",
                        (session["user_id"],)
                    )
                    assigned = True
                    flash(
                        f"Ride requested and assigned to your chosen driver! "
                        f"Fare: {fare} XAF. Please pay with MoMo / Orange Money from your dashboard.",
                        "success"
                    )
                else:
                    flash("That driver is no longer available. Ride created as PENDING.", "warning")

            if not assigned:
                cur.execute(
                    """INSERT INTO rides
                       (user_id, pickup, destination, passengers, vehicle_type, fare, status)
                       VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')""",
                    (session["user_id"], pickup, destination, passengers, vehicle_type, fare)
                )
                flash(
                    f"Ride requested successfully ({VEHICLE_TYPES[vehicle_type]['label']})! "
                    f"Estimated fare: {fare} XAF. Waiting for a driver to accept.",
                    "success"
                )

            conn.commit()
            cur.close()
            return redirect(url_for("dashboard"))
        except Error:
            flash("Could not create ride. Please try again.", "danger")
        finally:
            conn.close()

    return render_template(
        "request_ride.html",
        locations=LOCATIONS,
        vehicle_types=VEHICLE_TYPES,
        nearby_drivers=nearby_drivers,
        selected_pickup=selected_pickup,
        selected_destination="",
        selected_vehicle_type="taxi",
    )


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
    """Return fare for a given pickup/destination and optional vehicle_type (JSON)."""
    pickup = normalize_location(request.args.get("pickup", ""))
    destination = normalize_location(request.args.get("destination", ""))
    vehicle_type = request.args.get("vehicle_type", "taxi").lower()
    if vehicle_type not in VEHICLE_TYPES:
        vehicle_type = "taxi"
    if not pickup or not destination or pickup == destination:
        return jsonify({"fare": None, "error": "Invalid locations"})
    fare = get_fare(pickup, destination, vehicle_type)
    v_labels = {
        "bendskin": {"en": "Bendskin (Moto-Taxi) 🏍️", "fr": "Bendskin (Moto-Taxi) 🏍️"},
        "taxi": {"en": "Yellow Taxi (Standard) 🚕", "fr": "Taxi Jaune (Standard) 🚕"},
        "comfort": {"en": "Comfort Car (Private VIP) 🚗", "fr": "Voiture Confort (Privé VIP) 🚗"},
    }
    active_lang = getattr(g, "lang", "en")
    label = v_labels.get(vehicle_type, {}).get(active_lang, VEHICLE_TYPES[vehicle_type]["label"])
    return jsonify({
        "fare": fare,
        "currency": "XAF",
        "vehicle_type": vehicle_type,
        "vehicle_label": label
    })


@app.route("/api/nearby-drivers")
@login_required
def api_nearby_drivers():
    """
    Return free drivers near a pickup location (JSON).
    No GPS – uses driver's selected current_location and NEARBY map.
    """
    pickup = normalize_location(request.args.get("pickup", ""))
    if not pickup:
        return jsonify({"drivers": []})

    nearby = get_nearby_locations(pickup)
    drivers = []
    conn = get_db()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            placeholders = ",".join(["%s"] * len(nearby))
            cur.execute(
                f"""
                SELECT id, full_name, phone, vehicle_info, current_location
                FROM drivers
                WHERE status = 'active'
                  AND availability = 'free'
                  AND current_location IN ({placeholders})
                ORDER BY current_location, full_name
                """,
                tuple(nearby)
            )
            drivers = cur.fetchall()
            cur.close()
        except Error:
            drivers = []
        finally:
            conn.close()
    return jsonify({"drivers": drivers, "pickup": pickup})


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
