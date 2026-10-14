"""
ai_service.py
-------------
Intelligent urban transportation assistant for MboaLift in Douala, Cameroon.

The AI assistant:
- Answers questions in English, French, or Cameroonian Camfranglais.
- Guides users through Douala transportation realities:
  * Traffic hotspots: Pont sur le Wouri (Nouveau & Ancien Pont), Rond-Point Deido,
    Carrefour Ndokoti, PK8-PK14, Carrefour Agip.
  * Vehicle options: Bendskin (Moto-Taxi) vs. Taxi Jaune (Yellow shared cab) vs. Confort.
  * Payment tips: MTN Mobile Money (*126#) and Orange Money (*150#).
- NEVER changes ride status or payment status directly.
- NEVER exposes passwords or API keys.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "")


def get_ai_response(user_message, user_context=None):
    """
    Send a message to the AI and return the reply.

    Parameters:
        user_message (str): What the user typed
        user_context (dict or None): Safe info about the current user
            Example:
            {
                "name": "Eitel",
                "current_ride": "Akwa -> Bonanjo",
                "fare": "800 XAF",
                "vehicle_type": "taxi",
                "ride_status": "ACCEPTED",
                "payment_status": "SUCCESSFUL"
            }

    Returns:
        str: The AI's answer
    """
    if not user_message or not user_message.strip():
        return "Bonjour ! Posez-moi une question sur vos trajets à Douala (tarifs, bendskin, taxi, MoMo, trafic)."

    # If no real AI API is configured, use built-in rich Douala assistant
    if not AI_API_KEY or AI_API_KEY == "your_ai_api_key" or not AI_BASE_URL:
        return _local_douala_assistant(user_message, user_context)

    # Real AI API call
    system_prompt = (
        "You are 'MboaBot', the smart urban mobility AI assistant for MboaLift in Douala, Cameroon. "
        "You are knowledgeable about Douala's geography, neighborhoods (Akwa, Bonanjo, Deido, Bonamoussadi, "
        "Bépanda, Ndokoti, Bonabéri, New Bell, Makepe, Logbessou, Japoma, Aéroport), transportation modes "
        "(Bendskin moto-taxis, Taxi Jaune shared cabs, and Confort private cars), and payment methods "
        "(MTN Mobile Money and Orange Money). "
        "Respond warmly and helpfully in English or French depending on the user language, with natural Cameroonian friendliness. "
        "Explain Douala traffic hotspots (e.g. Pont sur le Wouri rush hours, Ndokoti market choke points). "
        "Never invent fake database updates. Keep answers concise and practical."
    )

    context_text = ""
    if user_context:
        parts = []
        for k, v in user_context.items():
            if v:
                parts.append(f"{k}: {v}")
        if parts:
            context_text = "Current user context:\n" + "\n".join(parts)

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "default",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": (context_text + "\n\n" + user_message) if context_text else user_message},
        ],
        "max_tokens": 400,
        "temperature": 0.6,
    }

    try:
        response = requests.post(AI_BASE_URL, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            data = response.json()
            answer = (
                data.get("choices", [{}])[0].get("message", {}).get("content")
                or data.get("response")
                or data.get("answer")
            )
            if answer:
                return answer.strip()
    except requests.exceptions.RequestException:
        pass

    # Seamless fallback to local expert assistant
    return _local_douala_assistant(user_message, user_context)


def _local_douala_assistant(message, context=None):
    """
    Intelligent local rule-based assistant specialized for Douala urban mobility.
    Bilingual (English / French) + Camfranglais friendly.
    """
    msg = message.lower().strip()
    name = context.get("name", "there") if context else "there"

    # Weather & Rain / Monsoon Advisories
    if any(w in msg for w in ["météo", "meteo", "pluie", "rain", "orage", "inondation", "saison des pluies", "weather", "averse", "déluge", "mouillé"]):
        return (
            "🌧️ **Météo & Saison des Pluies à Douala** :\n"
            "• **Précautions Bendskin (Moto)** : En cas d'averse torrentielle, les moto-taxis s'abritent sous les vérandas pour votre sécurité. Privilégiez un **Taxi Jaune** ou une **Voiture Confort** fermée et climatisée.\n"
            "• **Zones inondables fréquentes** : Carrefour Ndokoti, Bépanda Omnisports, Rond-Point Deido et accès Bonabéri. Prévoyez 20 à 30 minutes de marge supplémentaire.\n"
            "• **Astuce MboaLift** : Utilisez la réservation anticipée ou le covoiturage pour éviter de rester bloqué sous la pluie !"
        )

    # Airport & Business Trips
    if any(w in msg for w in ["aéroport", "aeroport", "airport", "vol", "flight", "bonanjo", "valise", "bagage", "affaires"]):
        return (
            "✈️ **Trajets Aéroport de Douala & Centre d'Affaires Bonanjo** :\n"
            "• **Aéroport International de Douala** : Pour vos valises et vols de nuit, le mode **Voiture Confort 🚗** (~2 000 – 2 500 XAF) offre un coffre spacieux et la climatisation.\n"
            "• **Bonanjo (Quartier Administratif & Banques)** : Très accessible en **Taxi Jaune 🚕** depuis Akwa (~800 XAF) ou Bonapriso (~800 XAF).\n"
            "• **Paiement MoMo / OM** : Réglez directement avec votre téléphone à l'arrivée !"
        )

    # Camfranglais & Douala Urban Slang
    if any(w in msg for w in ["on dit quoi", "le dos", "le ndjem", "waka", "clando", "le benskin", "tarot", "le tarot"]):
        return (
            "🇨🇲 **On est ensemble ! Bienvenue sur MboaLift Douala** :\n"
            "• **Le Waka au calme** : Pas besoin de te battre au carrefour Ndokoti ou à Deido. Tu commandes ta moto (Bendskin) ou ton taxi jaune directement sur ton phone.\n"
            "• **Le Dos / Le Tarot** : Pas de problème de monnaie avec le chauffeur ! Tu paies le ndjem par MTN MoMo (*126#) ou Orange Money (*150#).\n"
            "• Pose-moi toutes tes questions sur les prix ou les raccourcis !"
        )

    # Traffic & Bridge (Pont du Wouri)
    if any(w in msg for w in ["wouri", "pont", "bridge", "bonaberi", "bonabéri", "embouteillage", "traffic", "bouchon", "retard"]):
        return (
            "🚦 **Douala Traffic Guide — Le Pont du Wouri & Carrefours**:\n"
            "• **Pont du Wouri (Bonabéri <-> Akwa/Deido)**: Heavy rush hour 06:30–09:00 (direction Akwa) and 16:30–20:00 (direction Bonabéri). Choose a **Bendskin (Moto)** to weave through, or book a shared cab early.\n"
            "• **Carrefour Ndokoti & Rond-Point Deido**: Major crossroads prone to market and truck slowdowns.\n"
            "• **Conseil MboaLift**: En cas de gros bouchons, réservez un Bendskin pour gagner jusqu'à 45 minutes !"
        )

    # Bendskin vs Taxi vs Confort
    if any(w in msg for w in ["bendskin", "moto", "bike", "taxi", "confort", "comfort", "jaune", "véhicule", "vehicle", "clando"]):
        return (
            "🚗 **Choisir votre véhicule sur MboaLift**:\n"
            "1. 🏍️ **Bendskin (Moto-Taxi)**: Idéal pour 1 personne pressée. Tarif économique (-30%), slalome dans les embouteillages de Ndokoti et Deido.\n"
            "2. 🚕 **Taxi Jaune (Standard)**: Le classique de Douala. Jusqu'à 4 passagers, parfait pour vos courses ou trajets partagés.\n"
            "3. 🚗 **Voiture Confort (Privé)**: Véhicule climatisé avec chauffeur privé dédié, recommandé pour l'Aéroport, les rendez-vous d'affaires à Bonanjo ou les sorties de nuit."
        )

    # Fare & Pricing
    if any(w in msg for w in ["fare", "price", "cost", "how much", "combien", "tarif", "prix", "dépôt", "depot"]):
        if context and context.get("fare"):
            return f"Pour votre trajet actuel, le tarif estimé est de **{context['fare']}**."
        return (
            "💰 **Exemples de tarifs MboaLift à Douala**:\n"
            "• **Akwa <-> Bonanjo**: ~800 XAF (Taxi) | ~500 XAF (Bendskin)\n"
            "• **Akwa <-> Bonamoussadi**: ~1500 XAF (Taxi) | ~1050 XAF (Bendskin)\n"
            "• **Deido <-> Bépanda**: ~700 XAF (Taxi) | ~500 XAF (Bendskin)\n"
            "• **Akwa <-> Bonabéri (traversée pont)**: ~1800 XAF (Taxi)\n"
            "• **Bonapriso <-> Aéroport**: ~1200 XAF (Taxi) | ~2000 XAF (Confort)\n"
            "Rendez-vous sur la page **Demander un trajet** pour obtenir le tarif exact avec votre type de véhicule !"
        )

    # Payment (MoMo / Orange Money)
    if any(w in msg for w in ["pay", "payment", "momo", "orange", "money", "payer", "paiement"]):
        return (
            "💳 **Paiement Mobile Money sur MboaLift**:\n"
            "• Nous supportons **MTN MoMo** et **Orange Money** directement dans l'application.\n"
            "• Dès qu'un chauffeur accepte votre course, cliquez sur **Payer avec MoMo** dans votre tableau de bord ou 'Mes trajets'.\n"
            "• Vous recevrez un prompt USSD sur votre téléphone pour valider avec votre code secret personnel.\n"
            "🔒 **Sécurité**: MboaLift ne vous demandera JAMAIS votre code PIN secret."
        )

    # Requesting ride
    if any(w in msg for w in ["request", "book", "order", "demander", "commander", "course"]):
        return (
            "📍 **Comment demander une course sur MboaLift**:\n"
            "1. Allez sur **Demander un trajet** dans le menu.\n"
            "2. Indiquez votre point de départ (ex: Akwa) et votre destination (ex: Bonamoussadi).\n"
            "3. Choisissez votre véhicule : **Bendskin 🏍️**, **Taxi Jaune 🚕** ou **Confort 🚗**.\n"
            "4. Vérifiez le tarif instantané et validez. Un chauffeur à proximité prendra en charge votre course !"
        )

    # Shared Rides (Covoiturage urbain)
    if any(w in msg for w in ["shared", "join", "partager", "rejoindre", "covoiturage"]):
        return (
            "🤝 **Trajets Partagés (Shared Rides)**:\n"
            "• Le covoiturage permet de réduire les embouteillages et le coût du transport à Douala.\n"
            "• Allez sur la page **Trajets Partagés** pour voir les courses en attente créées par d'autres passagers sur votre itinéraire.\n"
            "• Cliquez sur 'Rejoindre' pour voyager ensemble et économiser !"
        )

    # Safety & SOS
    if any(w in msg for w in ["safety", "securite", "sécurité", "sos", "urgence", "police", "danger", "perdu"]):
        return (
            "🛡️ **Sécurité MboaLift à Douala**:\n"
            "• Tous nos chauffeurs sont enregistrés avec identité et immatriculation vérifiées.\n"
            "• Pendant votre trajet, utilisez l'option **Partager mon trajet** pour envoyer par WhatsApp ou SMS le numéro de course et l'identité du chauffeur à vos proches.\n"
            "• En cas d'urgence à Douala : Police Secours (117) | Gendarmerie (119)."
        )

    # Cancellation
    if any(w in msg for w in ["cancel", "annuler"]):
        return (
            "Vous pouvez annuler directement votre demande de trajet depuis la page **Mes trajets** tant que la course est encore **PENDING** (en attente d'un chauffeur)."
        )

    # Status
    if any(w in msg for w in ["status", "statut", "etat", "état", "where"]):
        if context and context.get("ride_status"):
            return f"Le statut de votre trajet en cours est : **{context['ride_status']}**."
        return (
            "Consultez l'onglet **Mes trajets** pour suivre l'avancement : PENDING (en recherche) → ACCEPTED (chauffeur en route) → IN_PROGRESS (en course) → COMPLETED (terminé)."
        )

    # Greetings
    if any(w in msg for w in ["hello", "hi", "bonjour", "salut", "bonsoir", "on dit quoi"]):
        return (
            f"Bonjour {name} ! Bienvenue sur **MboaLift — La mobilité réinventée pour Douala** 🇨🇲.\n"
            "Je suis là pour vous aider avec vos trajets, tarifs, Bendskins, taxis et paiements MoMo/Orange Money. Que puis-je faire pour vous ?"
        )

    # Default
    return (
        "Je suis votre assistant MboaLift pour la ville de Douala. Vous pouvez me poser des questions sur :\n"
        "• Les tarifs et le choix du véhicule (Bendskin moto vs Taxi Jaune)\n"
        "• Le trafic routier et le Pont du Wouri\n"
        "• Les paiements MTN MoMo et Orange Money\n"
        "• Comment réserver ou rejoindre un trajet partagé"
    )
