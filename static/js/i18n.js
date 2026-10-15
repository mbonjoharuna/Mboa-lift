/**
 * i18n.js
 * -------
 * Complete bidirectional client-side internationalization engine for MboaLift.
 * Supports:
 * - English (en) and French (fr)
 * - Complete coverage of every page, modal, card, table, badge, and form
 * - Full translation of input placeholders, select options, button texts, titles, aria-labels
 * - Seamless bidirectional switching (EN <-> FR) with original string caching
 * - Dynamic pattern matching for rides, drivers, passengers, fares, dates, and locations
 * - Auto-translation of newly inserted elements via MutationObserver (AI chat, live fare, nearby drivers)
 * - Auto-translation of window.alert and window.confirm dialogs
 */

(function () {
  'use strict';

  // ============================================================
  // MASTER DICTIONARY
  // ============================================================
  const translations = {
    // English -> French
    fr: {
      // Brand & Navigation
      'MboaLift': 'MboaLift',
      'Douala Mobility': 'Mobilité Douala',
      'Dashboard': 'Tableau de bord',
      'Request Ride': 'Demander une course',
      'Shared Rides': 'Courses partagées',
      'My Rides': 'Mes courses',
      'Payments': 'Paiements',
      'AI Assistant': 'Assistant IA',
      'Profile': 'Profil',
      'Logout': 'Déconnexion',
      'Driver Dashboard': 'Tableau de bord chauffeur',
      'Available Rides': 'Courses disponibles',
      'My Status': 'Mon statut',
      'Admin Dashboard': 'Tableau de bord admin',
      'Users': 'Utilisateurs',
      'Drivers': 'Chauffeurs',
      'Rides': 'Courses',
      'Home': 'Accueil',
      'Passenger Login': 'Connexion passager',
      'Passenger Register': 'Inscription passager',
      'Driver Login': 'Connexion chauffeur',
      'Driver Register': 'Inscription chauffeur',
      'Admin': 'Administration',
      'Preparing your ride…': 'Préparation de votre trajet…',
      'MboaLift — Re-invent Douala\'s Ride © 2026': 'MboaLift — Réinventons les déplacements à Douala © 2026',
      'School coding challenge project': 'Projet de défi de programmation scolaire',

      // Hero & Landing
      'Reinventing Douala\'s Ride': 'Réinventer le transport à Douala',
      'Re-invent Douala\'s Ride': 'Réinventons les déplacements à Douala',
      'Move faster. Ride with MboaLift.': 'Déplacez-vous plus vite. Voyagez avec MboaLift.',
      'The urban mobility platform custom-built for Douala.': 'La plateforme de mobilité urbaine conçue sur-mesure pour Douala.',
      'Choose between Bendskin (Moto-Taxi) to beat traffic jams, Yellow Taxi for shared trips, or Comfort Car.': 'Choisissez entre Bendskin (Moto-Taxi) pour battre les embouteillages, Taxi Jaune pour vos trajets partagés, ou Voiture Confort.',
      'Pay safely with MTN MoMo and Orange Money.': 'Payez en toute sécurité par MTN MoMo et Orange Money.',
      'Request a Ride': 'Demander une course',
      'Urban Carpooling': 'Covoiturage urbain',
      'Find Shared Rides': 'Trouver des courses partagées',
      'How it works': 'Comment ça fonctionne ?',
      'How it works?': 'Comment ça fonctionne ?',
      'Already registered?': 'Déjà inscrit ?',
      'Rider Login': 'Connexion Passager',
      'Douala Mobility Platform': 'Plateforme de Mobilité Douala',
      'Built for Douala': 'Pensé pour Douala',
      'Bendskin & Yellow Cabs': 'Bendskin & Taxis Jaunes',
      'MTN MoMo & Orange Money': 'MTN MoMo & Orange Money',
      'Local AI Assistant': 'Assistant IA Local',
      'Ride Safety Sharing': 'Partage Trajet Sécurité',
      'The 3 MboaLift ride modes': 'Les 3 modes de transport MboaLift',
      'Bendskin (Moto-Taxi)': 'Bendskin (Moto-Taxi)',
      'Yellow Taxi (Standard)': 'Taxi Jaune (Standard)',
      'Comfort Car (Private VIP)': 'Voiture Confort (Privé VIP)',
      'Simple registration': 'Inscription simple',
      'Request or Share': 'Demandez ou Partagez',
      'MoMo / Orange Payment': 'Paiement MoMo / Orange',
      'Ride safely & Rate': 'Roulez en sécurité & Notez',
      'Locations & Neighborhoods served in Douala': 'Lieux & Quartiers desservis à Douala',
      'Popular locations in Douala': 'Lieux populaires à Douala',
      'The lifesaver of Douala traffic jams. Weaves through Ndokoti Junction and Wouri Bridge. Ideal for 1 person in a hurry (-30% economic).': 'Le sauveur des embouteillages de Douala. Slalome au Carrefour Ndokoti et sur le Pont du Wouri. Idéal pour 1 personne pressée (-30% économique).',
      'The icon of Douala streets. Up to 4 passengers, perfect for everyday trips, market shopping, and shared rides.': 'L\'icône des rues de Douala. Jusqu\'à 4 passagers, parfait pour les trajets quotidiens, les emplettes au marché et le covoiturage partagé.',
      'Air-conditioned private vehicle with dedicated driver. Recommended for Douala Airport, Bonanjo business meetings, and night events.': 'Véhicule privé climatisé avec chauffeur attitré. Recommandé pour l\'Aéroport de Douala, les réunions à Bonanjo et les soirées.',

      // Passenger Dashboard
      'Passenger Dashboard': 'Tableau de bord passager',
      'Passenger dashboard — request rides and pay with MoMo': 'Tableau de bord passager — demandez des courses et payez avec MoMo',
      'Total Rides': 'Total des courses',
      'Pending': 'En attente',
      'Completed': 'Terminées',
      'Cancelled': 'Annulées',
      'Total Paid (XAF)': 'Total payé (XAF)',
      'Recent Rides': 'Courses récentes',
      'View All': 'Tout voir',
      'ID': 'ID',
      'Route': 'Itinéraire',
      'Fare': 'Tarif',
      'Status': 'Statut',
      'Date': 'Date',
      'Action': 'Action',
      'Actions': 'Actions',
      'Course': 'Course',
      'Ride': 'Course',
      'Amount': 'Montant',
      'Montant': 'Montant',
      'No rides yet.': 'Aucune course pour le moment.',
      'No rides yet. Request your first ride.': 'Aucune course pour le moment. Demander votre première course.',
      'Request your first ride': 'Demander votre première course',
      'Payment History': 'Historique des paiements',
      'Ask AI Assistant': 'Demander à l\'assistant IA',

      // Request Ride Form
      'Choose your Douala destination and vehicle mode. Fast, transparent fares with MoMo & Orange Money.': 'Choisissez votre destination et votre mode de transport à Douala. Tarifs rapides et transparents avec MoMo et Orange Money.',
      'Douala Traffic Tip:': 'Conseil Trafic Douala :',
      'During rush hours on the Wouri Bridge, Ndokoti or Deido roundabout, pick a Bendskin 🏍️ to dodge traffic jams!': 'Aux heures de pointe sur le Pont du Wouri, Ndokoti ou Rond-Point Deido, choisissez un Bendskin 🏍️ pour éviter les embouteillages !',
      'Transport mode': 'Type de transport',
      'Type de transport': 'Type de transport',
      'Bendskin (Moto)': 'Bendskin (Moto)',
      'Traffic-dodger • 1 passenger max': 'Anti-bouchons • 1 passager max',
      'Eco (-30%)': 'Éco (-30%)',
      'Éco (-30%)': 'Éco (-30%)',
      'Taxi Jaune': 'Taxi Jaune',
      'Yellow Taxi': 'Taxi Jaune',
      'Douala classic • 1 to 4 passengers': 'Classique Douala • 1 à 4 passagers',
      'Popular': 'Populaire',
      'Populaire': 'Populaire',
      'Voiture Confort': 'Voiture Confort',
      'Comfort Car': 'Voiture Confort',
      'Air-conditioned • Private / Airport': 'Climatisé • Privé / Aéroport',
      'VIP': 'VIP',
      'Pickup location (Départ)': 'Lieu de départ (Pickup)',
      'Destination (Arrivée)': 'Lieu d\'arrivée (Destination)',
      'Choose from major Douala neighborhoods.': 'Choisissez parmi les quartiers majeurs de Douala.',
      'Number of passengers': 'Nombre de passagers',
      'Standard Taxi accepts up to 4 passengers. Bendskin accepts 1.': 'Le Taxi standard accepte jusqu\'à 4 passagers. Le Bendskin accepte 1 passager.',
      'Bendskin moto-taxi: strictly 1 passenger for your safety.': 'Bendskin moto-taxi : 1 seul passager pour votre sécurité.',
      'Capacity: up to 4 passengers.': 'Capacité : jusqu\'à 4 passagers.',
      'Route:': 'Trajet :',
      'Mode:': 'Mode :',
      'Estimated Fare:': 'Tarif estimé :',
      'Transparent fare guaranteed before departure. Payment via MTN MoMo or Orange Money.': 'Tarif transparent garanti avant le départ. Paiement par MTN MoMo ou Orange Money.',
      'Available nearby drivers': 'Chauffeurs disponibles à proximité',
      'Chauffeurs disponibles à proximité': 'Chauffeurs disponibles à proximité',
      'Specify your pickup location to see free nearby drivers.': 'Indiquez votre lieu de départ pour voir les chauffeurs libres à proximité.',
      'Any available driver (first to accept)': 'N\'importe quel chauffeur disponible (premier à accepter)',
      'All available drivers': 'Tous les chauffeurs disponibles',
      'Availability area based on the driver\'s declared active location.': 'Zone de disponibilité basée sur la présence active déclarée du chauffeur.',
      'Request Ride': 'Commander la course',
      'Commander la course': 'Commander la course',

      // My Rides & Shared Rides
      'Mes Trajets': 'Mes Trajets',
      'My Rides': 'Mes courses',
      'Track your rides in real time, pay with Mobile Money, and share your trips for safety.': 'Suivez vos courses en temps réel, payez par Mobile Money et partagez vos trajets pour votre sécurité.',
      'Rides I requested': 'Courses que j\'ai demandées',
      '+ New ride': '+ Nouvelle course',
      '+ Nouvelle course': '+ Nouvelle course',
      'Passenger': 'Passager',
      'Driver': 'Chauffeur',
      'Payment': 'Paiement',
      'Actions & Safety': 'Actions & Sécurité',
      'Searching...': 'En recherche...',
      'Paid ✅': 'Payé ✅',
      'Pending ⏳': 'En attente ⏳',
      'Unpaid': 'Non payé',
      'Cancel': 'Annuler',
      'Share': 'Partager',
      'Pay MoMo/OM': 'Payer MoMo/OM',
      'Rate ⭐': 'Noter ⭐',
      'Rate': 'Noter',
      'Leave': 'Quitter',
      'You haven\'t requested any rides yet.': 'Vous n\'avez pas encore demandé de courses.',
      'Request your first ride.': 'Demandez votre premier trajet.',
      'Shared rides joined': 'Trajets partagés rejoints',
      'View shared rides': 'Voir les covoiturages',
      'Owner': 'Propriétaire',
      'You haven\'t joined any shared rides yet.': 'Vous n\'avez rejoint aucun trajet partagé pour le moment.',
      'Join a ride going the same way and share the cost': 'Rejoignez une course allant dans la même direction et partagez le coût',
      'Join Ride': 'Rejoindre la course',
      'No compatible shared rides available right now.': 'Aucune course partagée compatible disponible pour le moment.',
      'Request your own ride instead.': 'Demandez votre propre course à la place.',

      // Payment & Payments History
      'Mobile Money Payment (MoMo / Orange Money)': 'Paiement Mobile Money (MoMo / Orange Money)',
      'Payment for your ride': 'Paiement de votre course',
      'Pay for your ride securely with MTN MoMo or Orange Money.': 'Réglez votre trajet en toute sécurité avec MTN MoMo ou Orange Money.',
      'Vehicle type:': 'Type de véhicule :',
      'Amount to pay:': 'Montant à régler :',
      'Mobile Money Operator': 'Opérateur Mobile Money',
      'Phone number (Cameroon)': 'Numéro de téléphone (Cameroun)',
      'Enter your 9-digit number. You will receive a USSD prompt to confirm with your secret PIN.': 'Entrez votre numéro à 9 chiffres. Vous recevrez un prompt USSD pour valider avec votre code secret.',
      'Absolute security: We NEVER ask for your secret PIN on this website. Confirmation is done directly on your phone.': 'Sécurité absolue : Nous ne vous demandons JAMAIS votre code PIN secret sur ce site. La confirmation se fait directement sur votre téléphone.',
      'Demo tip: a phone ending with 0 simulates failure/cancellation; any other number confirms payment.': 'Astuce démo : un numéro se terminant par 0 simule un échec/annulation, tout autre numéro déclenche la confirmation.',
      'Payment History': 'Historique des Paiements',
      'View and verify your MTN Mobile Money and Orange Money transactions.': 'Consultez et vérifiez vos transactions MTN Mobile Money et Orange Money.',
      'Reference': 'Référence',
      'Phone': 'Téléphone',
      'Verify': 'Vérifier',
      'Confirmed': 'Validé',
      'No payments recorded yet.': 'Aucun paiement enregistré pour l\'instant.',

      // Driver Pages
      'Douala Driver Space': 'Espace Chauffeur Douala',
      'View live ride requests in Douala and track your Mobile Money earnings.': 'Consultez les demandes de courses disponibles à Douala et suivez vos gains Mobile Money.',
      'Available rides': 'Courses disponibles',
      'Active rides': 'Courses actives',
      'Completed rides': 'Courses terminées',
      'Total Earnings (XAF)': 'Total Gains (XAF)',
      'View available rides': 'Voir les courses disponibles',
      'My rides': 'Mes courses',
      'Update my location / status': 'Modifier ma position / statut',
      'Accept a pending ride in Douala. Once accepted, the ride is exclusively assigned to you.': 'Acceptez une course en attente à Douala. Dès que vous acceptez, la course vous est exclusivement assignée.',
      'Requested at': 'Demandée à',
      'Accept Ride': 'Accepter la course',
      'No pending rides right now. Verify that your status is set to "free" in your profile.': 'Aucune course en attente pour le moment. Vérifiez que votre statut est bien défini sur "free" dans votre profil.',
      'My Accepted Rides': 'Mes Courses Prises en Charge',
      'Manage your accepted rides, start the trip, and complete it to receive your earnings.': 'Gérez vos trajets acceptés, démarrez la course et validez la fin du trajet pour percevoir vos gains.',
      'Start Ride': 'Démarrer trajet',
      'Complete Ride ✅': 'Terminer course ✅',
      'Completed': 'Terminée',
      'You don\'t have any assigned rides yet.': 'Vous n\'avez pas encore de courses assignées.',
      'Browse available rides': 'Consulter les courses disponibles',
      'Driver Registration': 'Inscription Chauffeur',
      'Drive in Douala (Yellow Taxi, Bendskin Moto, or Comfort Car)': 'Conduisez à Douala (Taxi Jaune, Moto Bendskin ou Voiture Confort)',
      'Full Name': 'Nom complet',
      'Phone Number': 'Numéro de téléphone',
      'Email Address': 'Adresse e-mail',
      'Vehicle Category': 'Catégorie de véhicule',
      'Yellow Taxi (Standard shared cab)': 'Taxi Jaune (Voiture partagée standard)',
      'Bendskin Moto-Taxi': 'Bendskin Moto-Taxi',
      'Comfort Car (AC / Private)': 'Voiture Confort (Climatisée / Privée)',
      'Vehicle details & license plate': 'Détails du véhicule & immatriculation',
      'Password': 'Mot de passe',
      'Confirm Password': 'Confirmer le mot de passe',
      'Register as Driver': 'S\'inscrire comme Chauffeur',
      'Already a driver?': 'Déjà chauffeur ?',
      'Are you a rider?': 'Vous êtes passager ?',
      'Rider Registration': 'Inscription Passager',
      'My Location & Availability': 'Ma position et disponibilité',
      'Set where you are in Douala so passengers can see you as a free nearby driver.': 'Indiquez où vous êtes à Douala pour que les passagers vous voient comme chauffeur disponible.',
      'Current area': 'Quartier actuel',
      '-- Select your area --': '-- Sélectionnez votre quartier --',
      'Availability': 'Disponibilité',
      'Free (can accept rides)': 'Disponible (peut accepter des courses)',
      'Busy (on a trip)': 'Occupé (en course)',
      'Save Status': 'Enregistrer le statut',
      'No GPS is used. Passengers see you when their pickup is in the same or nearby area.': 'Aucun GPS n\'est utilisé. Les passagers vous voient lorsque leur départ est dans la même zone ou à proximité.',

      // Admin Pages
      'Admin Dashboard': 'Tableau de bord administrateur',
      'Overview of MboaLift activity': 'Vue d\'ensemble de l\'activité MboaLift',
      'Total Users': 'Total des utilisateurs',
      'Total Drivers': 'Total des chauffeurs',
      'Pending Rides': 'Courses en attente',
      'Accepted': 'Acceptées',
      'Successful Payments': 'Paiements réussis',
      'Pending Payments': 'Paiements en attente',
      'Failed Payments': 'Paiements échoués',
      'Total Collected (XAF)': 'Total collecté (XAF)',
      'Manage Rides': 'Gérer les courses',
      'Manage Users': 'Gérer les utilisateurs',
      'Manage Drivers': 'Gérer les chauffeurs',
      'View Payments': 'Voir les paiements',
      'Gestion des Chauffeurs': 'Gestion des chauffeurs',
      'Supervisez les chauffeurs de Bendskin (moto-taxis), Taxis Jaunes et Voitures Confort.': 'Supervisez les chauffeurs de Bendskin (moto-taxis), Taxis Jaunes et Voitures Confort.',
      'Aucun chauffeur trouvé.': 'Aucun chauffeur trouvé.',
      'Gestion des Courses': 'Gestion des courses',
      'Search by name, pickup, or destination...': 'Recherche par nom, départ ou destination...',
      'All statuses': 'Tous les statuts',
      'Filter': 'Filtrer',
      'Filtrer': 'Filtrer',
      'Accepter': 'Accepter',
      'Démarrer': 'Démarrer',
      'Suivi des Paiements': 'Suivi des paiements',
      'Payment Tracking': 'Suivi des paiements',
      'Supervision of MTN Mobile Money and Orange Money transactions.': 'Supervision des transactions MTN Mobile Money et Orange Money.',
      'Search by transaction, name or phone...': 'Recherche par transaction, nom ou téléphone...',
      'Search by name, email or phone...': 'Recherche par nom, e-mail ou téléphone...',
      'Search': 'Rechercher',
      'Rechercher': 'Rechercher',
      'Disable': 'Désactiver',
      'Enable': 'Activer',
      'Delete': 'Supprimer',
      'Joined': 'Inscrit le',
      'No users found.': 'Aucun utilisateur trouvé.',
      'Admin Login': 'Connexion administrateur',
      'Restricted access': 'Accès restreint',
      'Username': 'Nom d\'utilisateur',
      'Login as Admin': 'Se connecter comme administrateur',

      // Profile & Rating
      'My Profile': 'Mon profil',
      'Member since': 'Membre depuis',
      'Could not load profile.': 'Impossible de charger le profil.',
      'Rate Your Ride': 'Évaluer votre course',
      'Rating (1–5)': 'Note (1–5)',
      'Comment (optional)': 'Commentaire (facultatif)',
      'Submit Rating': 'Envoyer la note',

      // AI Assistant Page & Chatbot
      'Ask questions about rides, fares, payments and more': 'Posez des questions sur les courses, les tarifs, les paiements et plus encore',
      'Context used by the assistant:': 'Contexte utilisé par l\'assistant :',
      'Name:': 'Nom :',
      'Current ride:': 'Course actuelle :',
      'Fare:': 'Tarif :',
      'Ride status:': 'Statut de la course :',
      'Payment status:': 'Statut du paiement :',
      'You:': 'Vous :',
      'Assistant:': 'Assistant :',
      'Your question': 'Votre question',
      'Send': 'Envoyer',
      'Example questions': 'Exemples de questions',
      'How much is my estimated fare?': 'Quel est mon tarif estimé ?',
      'How do I request a ride?': 'Comment demander une course ?',
      'How do I join a shared ride?': 'Comment rejoindre une course partagée ?',
      'What is the status of my ride?': 'Quel est le statut de ma course ?',
      'How do I make a MoMo payment?': 'Comment effectuer un paiement MoMo ?',
      'My payment failed, what should I do?': 'Mon paiement a échoué, que dois-je faire ?',
      'How can I rate a ride?': 'Comment évaluer une course ?',
      'The AI is only an assistant. It cannot change ride or payment status.': 'L\'IA est un simple assistant. Elle ne peut pas modifier le statut d\'une course ou d\'un paiement.',
      'Hello! I am your MboaLift assistant.': 'Bonjour ! Je suis votre assistant MboaLift.',
      'Ask me about fares, requesting rides, shared rides, MoMo payments, or ride status.': 'Posez-moi des questions sur les tarifs, la demande de course, le covoiturage, les paiements MoMo ou le statut de votre course.',
      'Thinking...': 'Réflexion en cours...',
      'Sorry, I could not answer.': 'Désolé, je n\'ai pas pu répondre.',
      'Sorry, I could not reach the assistant. Please try again.': 'Désolé, impossible de contacter l\'assistant. Veuillez réessayer.',

      // Auth (Login / Register)
      'Welcome Back': 'Bon retour',
      'Login to your MboaLift account': 'Connectez-vous à votre compte MboaLift',
      'Email': 'E-mail',
      'Login': 'Se connecter',
      'Don\'t have an account?': 'Pas encore de compte ?',
      'Register as Rider': 'S\'inscrire comme Passager',
      'Are you a driver?': 'Vous êtes chauffeur ?',
      'Create Account': 'Créer un compte',
      'Join MboaLift today': 'Rejoignez MboaLift aujourd\'hui',
      'Register': 'S\'inscrire',
      'Already have an account?': 'Vous avez déjà un compte ?',
      'Want to drive?': 'Vous voulez conduire ?',
      'New driver?': 'Nouveau chauffeur ?',
      'Rider?': 'Passager ?',
      'Access your driver account': 'Accédez à votre compte chauffeur',
      'Login as Driver': 'Se connecter comme chauffeur',

      // Fare Calculator & Validations
      'Invalid (same location)': 'Invalide (même lieu)',
      'Not available': 'Non disponible',
      'XAF (estimate)': 'XAF (estimation)',
      'Passwords do not match.': 'Les mots de passe ne correspondent pas.',
      'Password must be at least 6 characters.': 'Le mot de passe doit comporter au moins 6 caractères.',
      'Pickup and destination cannot be the same.': 'Le lieu de départ et la destination ne peuvent pas être identiques.',
      'Join this shared ride?': 'Rejoindre cette course partagée ?',
      'Disable this user?': 'Désactiver cet utilisateur ?',
      'DELETE this user permanently?': 'Supprimer définitivement cet utilisateur ?',
      'Annuler cette course ?': 'Annuler cette course ?',
      'Accepter cette course ?': 'Accepter cette course ?',
      'Quitter ce trajet partagé ?': 'Quitter ce trajet partagé ?',
      'Annuler et libérer cette course pour un autre chauffeur ?': 'Annuler et libérer cette course pour un autre chauffeur ?',

      // Interactive Douala Map & Tracker
      'Douala Urban Route Map': 'Carte Urbaine & Itinéraire Douala',
      'Live Traffic & Drivers': 'Trafic & Chauffeurs en direct',
      'Demand & Driver Location Map': 'Carte de la Demande & Position Chauffeur',
      'Declared Area:': 'Secteur déclaré :',
      'Landmarks:': 'Repères :',
      'Pickup Point': 'Point de départ',
      'Live Ride Tracking': 'Suivi Course en direct',
      'Searching for an available driver... ⏳': 'Recherche d\'un chauffeur disponible... ⏳',
      'Driver on the way to': 'Chauffeur en route vers',
      'Trip in progress to': 'Course en cours vers',
      'Arrived at destination! Ride completed ✅': 'Arrivé à destination ! Course terminée ✅',
      '1. Request': '1. Demande',
      '2. Driver': '2. Chauffeur',
      '3. En route': '3. En course',
      '4. Arrival': '4. Arrivée',
      'My ride details': 'Détails de mes courses',

      // Status values
      'PENDING': 'En attente',
      'ACCEPTED': 'Acceptée',
      'IN_PROGRESS': 'En cours',
      'COMPLETED': 'Terminée',
      'CANCELLED': 'Annulée',
      'SUCCESSFUL': 'Réussi',
      'FAILED': 'Échoué',
      'active': 'actif',
      'disabled': 'désactivé',

      // Placeholders
      'your@email.com': 'votre@email.com',
      'Your password': 'Votre mot de passe',
      'e.g. Jean Mbarga': 'ex. Jean Mbarga',
      'e.g. 670000000': 'ex. 670000000',
      'e.g. jean@example.com': 'ex. jean@example.com',
      'At least 6 characters': 'Au moins 6 caractères',
      'Repeat password': 'Répétez le mot de passe',
      'Type or choose (e.g. Akwa, Bonanjo, Bonabéri)': 'Saisissez ou choisissez (ex. Akwa, Bonanjo, Bonabéri)',
      'Type or choose (e.g. Bonamoussadi, Aéroport, Ndokoti)': 'Saisissez ou choisissez (ex. Bonamoussadi, Aéroport, Ndokoti)',
      '6XX XXX XXX (ex: 671234567)': '6XX XXX XXX (ex. 671234567)',
      'ex: Jean-Paul Mbarga': 'ex. Jean-Paul Mbarga',
      'ex: 671234567': 'ex. 671234567',
      'ex: chauffeur@mboalift.cm': 'ex. chauffeur@mboalift.cm',
      'ex: Toyota Corolla LT-123-AB ou Bajaj Boxer 150': 'ex. Toyota Corolla LT-123-AB ou Bajaj Boxer 150',
      'Type your question...': 'Saisissez votre question...',
      'Share your experience...': 'Partagez votre expérience...',
      'e.g. How do I request a ride? How much is the fare from Akwa to Deido?': 'ex. Comment demander une course ? Quel est le tarif de Akwa à Deido ?',
      'Search by name, email or phone...': 'Recherche par nom, e-mail ou téléphone...',
      'Recherche par nom, départ ou destination...': 'Recherche par nom, départ ou destination...',
      'Recherche par transaction, nom ou téléphone...': 'Recherche par transaction, nom ou téléphone...',
      'Driver on the way': 'Chauffeur en route',
      'Trip in progress': 'Course en cours',
      'Assigned driver': 'Chauffeur assigné',
      'Share safety on WhatsApp': 'Partager ma sécurité WhatsApp',
      'Payment confirmed ✅': 'Paiement validé ✅',
      'Details': 'Détails',
      'Active mission': 'Mission en cours',
      'Active Mission': 'Mission en cours',
      'Assigned active ride': 'Course en cours assignée',
      'Call passenger': 'Appeler passager',
      'Start trip ▶': 'Démarrer le trajet ▶',
      'Confirm payment': 'Valider le paiement',
      'USSD prompt received on your phone...': 'Prompt USSD reçu sur votre téléphone...',
      'Secret PIN code:': 'Code PIN secret :',
      'Approve the transfer of': 'Approuver le transfert de',
      'Please enter a valid 9-digit phone number.': 'Veuillez entrer un numéro de téléphone valide à 9 chiffres.',

      // Weather & Traffic Alert Engine
      'Douala Rain & Traffic Alert Engine': 'Météo Pluie & Inondations Douala',
      'Flood Alert & Torrential Downpour': 'Alerte Inondations & Pluie Torrentielle',
      'Wouri Bridge Major Gridlock': 'Bouchon Majeur Pont du Wouri',
      'Tropical Weather Douala': 'Météo Tropicale Douala',
      'Ideal Weather & Traffic': 'Trafic & Météo Idéals',
      'Torrential Rain & Severe Flooding Detected': 'Pluie torrentielle & Inondations détectées',
      'Critical Congestion on Wouri Bridge': 'Embouteillage critique sur le Pont du Wouri',
      'Moderate Tropical Showers': 'Averses tropicales modérées',
      'Dry Weather & Normal Flow': 'Temps sec & Circulation normale',
      'Torrential rain detected in Douala: severe flood risks at Makepe Missoke, Bépanda, and Bonabéri. Prefer sheltered Comfort Cars or diverted routes.': 'Pluie torrentielle détectée sur Douala : risques majeurs d\'inondations à Makèpè Missokè, Bépanda et Bonabéri. Privilégiez les Voitures Confort abritées ou itinéraires déviés.',
      'Major gridlock on Bonabéri ↔ Rond-Point Deïdo corridor (est. delay: 45+ min). Prefer Bendskin 🏍️ to weave through traffic or delay your trip.': 'Saturation majeure de l\'axe Bonabéri ↔ Rond-Point Deïdo (retard estimé : 45+ min). Privilégiez un Bendskin 🏍️ pour battre les bouchons ou différez votre départ.',
      'Intermittent showers across Akwa, Bonanjo, and Ndokoti. Wet roadways. Sheltered Yellow Taxis recommended.': 'Averses intermittentes sur Akwa, Bonanjo et Ndokoti. Chaussées humides. Taxis jaunes abrités conseillés.',
      'Optimal conditions across Douala. Smooth traffic flow on main boulevards and Wouri Bridge.': 'Conditions idéales pour se déplacer à Douala. Trafic fluide sur les grands boulevards et le Pont du Wouri.',
      'Zones under watch :': 'Zones sous surveillance :',
      'Zones d\'alerte :': 'Zones d\'alerte :',
      'No flooded zones': 'Aucune zone inondée',
      'Test live conditions :': 'Tester les conditions en direct :',
      'Torrential rain & floods': 'Pluie torrentielle & Inondations',
      'Wouri Bridge jam': 'Bouchon Pont Wouri',
      'Moderate showers': 'Averses modérées',
      'Clear & smooth': 'Ciel dégagé & Fluide',
      'Weather :': 'Météo :',
      'Immediate Flood Alert : ': 'Alerte Inondation Immédiate : ',
      'Wouri Bridge crossing saturated !': 'Traversée du Pont du Wouri saturée !',
      'Sheltered': 'Abrité Météo',
      'Beat-traffic': 'Anti-Bouchon',

      // Emergency SOS Center
      'Emergency SOS': 'SOS Urgence',
      'SOS Urgence Douala': 'SOS Urgence Douala',
      'Douala Emergency & Safety Center': 'Centre d\'Urgence & Sécurité Douala',
      'Direct access to official Cameroon emergency numbers & distress broadcast.': 'Accès direct aux numéros d\'urgence officiels du Cameroun & alerte de détresse géolocalisée.',
      'Douala Police Secours': 'Police Secours Douala',
      'National Gendarmerie': 'Gendarmerie Nationale',
      'SAMU Medical Emergency': 'SAMU Urgences Médicales',
      'Fire & Rescue Brigade': 'Sapeurs-Pompiers (20e Groupement)',
      'Central police precincts & rapid intervention mobile units': 'Commissariats Centraux & patrouilles d\'intervention rapide',
      'Littoral Gendarmerie Legion & checkpoint safety': 'Légion de Gendarmerie du Littoral & sécurité routière',
      'Ambulances, Laquintinie & Douala General Hospitals': 'Ambulances, Hôpital Laquintinie & Hôpital Général de Douala',
      'Flood rescue Makepe/Bépanda, road accidents & firefighting': 'Sauvetage inondations Makèpè/Bépanda, accidents routiers & incendies',
      'Instant Distress Location Broadcast (Douala GPS)': 'Diffusion d\'Urgence Immédiate (GPS Douala)',
      'SOS WhatsApp': 'SOS WhatsApp',
      'SOS SMS (117)': 'SOS SMS (117)',
      'Copy message': 'Copier le message',
      'Visual Strobe Beacon': 'Balise Visuelle Flash',
      'Touch the screen to stop the strobe': 'Touchez l\'écran pour arrêter la balise',

      // Offline USSD & SMS Booking
      'Offline Booking without Internet (USSD & SMS)': 'Réservation sans Internet (USSD & SMS)',
      'No mobile data connection? Dial direct USSD code or send a free SMS.': 'Pas de connexion données mobiles ? Composez le code direct ou envoyez un SMS gratuit.',
      'Pickup area (Douala)': 'Lieu de départ (Douala)',
      'Destination (Douala)': 'Destination (Douala)',
      'Transport mode': 'Mode de transport',
      'Direct USSD code to dial (no internet needed) :': 'Code USSD Direct à composer (sans internet) :',
      'Free 2G/3G/4G': 'Gratuit 2G/3G/4G',
      'Dial USSD code': 'Composer le code USSD',
      'Send via free SMS': 'Envoyer par SMS gratuit',
      'Simulate USSD screen (2G phone)': 'Simuler l\'écran USSD (Téléphone 2G)',
      'No mobile data or unstable network in Douala?': 'Pas de forfait internet ou réseau instable à Douala ?',
      'Book immediately via free direct USSD code *999# or SMS to 8800 on any 2G/3G/4G phone.': 'Réservez immédiatement par code USSD gratuit direct *999# ou par SMS au 8800 sur n\'importe quel téléphone 2G/3G/4G.',
      'Book via USSD (*999#)': 'Réserver par USSD (*999#)',
      'No internet connection?': 'Pas de connexion internet ?',
      'Book for free with no mobile data via USSD (*999#) or SMS.': 'Réservez gratuitement sans données mobiles via USSD (*999#) ou SMS.',

      // Digital Trip Receipt & Tax Verification
      'Official Trip Receipt': 'Reçu Officiel de Course',
      'Official Receipt': 'Reçu Officiel Acquitté',
      'Official Receipt Certified Compliant': 'Reçu Officiel Certifié Conforme',
      'Back to my rides': 'Retour à mes courses',
      'Payment history': 'Historique paiements',
      'Print / Save as PDF (A4)': 'Imprimer / Enregistrer en PDF (A4)',
      'Print / Save in PDF (A4)': 'Imprimer / Enregistrer en PDF (A4)',
      'Certified multimodal urban transport platform Douala': 'Plateforme agréée de transport urbain multimodal Douala',
      'Tax Proof & Expense Reimbursement Voucher': 'Justificatif Fiscal & Remboursement Note de Frais',
      'Tax Proof & Expense Voucher': 'Justificatif Fiscal & Remboursement Note de Frais',
      'Issued on': 'Émis le',
      'Trip completed in Douala :': 'Trajet effectué à Douala :',
      'Passenger / Beneficiary Employee': 'Passager / Collaborateur Bénéficiaire',
      'Certified Transport Provider': 'Prestataire de Transport Assermenté',
      'Professional commute Douala (Akwa / Bonanjo)': 'Déplacement professionnel Douala (Akwa / Bonanjo)',
      'Certified Urban Vehicle': 'Véhicule Agréé Urbain',
      'MboaLift Douala Certified Network Fleet': 'Flotte MboaLift Douala Réseau Certifié',
      'Service Description': 'Désignation de la prestation',
      'Service Type': 'Type de service',
      'Amount (XAF)': 'Montant (XAF)',
      'Urban ride Douala': 'Course urbaine Douala',
      'Safe urban pickup and transit': 'Prise en charge et acheminement urbain sécurisé',
      'Standard Ride': 'Trajet Standard',
      'Transport mode adjustment': 'Ajustement mode de transport',
      'Mode Adjustment': 'Ajustement Mode',
      'Air-conditioned VIP comfort option with private driver': 'Option confort VIP climatisé et chauffeur privé',
      'Economic Bendskin traffic-beating pricing (-30%)': 'Tarification économique Bendskin anti-bouchons (-30%)',
      'Total Excluding Tax (HT)': 'Total Hors Taxes (HT)',
      'Taxable base': 'Base imposable',
      'Value Added Tax (VAT)': 'Taxe sur la Valeur Ajoutée (TVA)',
      'Urban passenger transport exemption scheme (CGI Cameroon)': 'Régime d\'exonération transport urbain de personnes (CGI Cameroun)',
      'VAT 0%': 'TVA 0%',
      'Net Paid (TTC) :': 'Net Payé (TTC) :',
      'Net Paid (TTC)': 'Net Payé (TTC)',
      'Payment confirmed via Orange Money Cameroon': 'Paiement validé via Orange Money Cameroun',
      'Payment confirmed via MTN Mobile Money (MoMo)': 'Paiement validé via MTN Mobile Money (MoMo)',
      'Transaction Ref. :': 'Réf. Transaction :',
      'Debited account :': 'Compte débité :',
      'VALIDATED & SETTLED': 'VALIDÉ & ACQUITTÉ',
      '✓ VALIDATED & SETTLED': '✓ VALIDÉ & ACQUITTÉ',
      'Digital Certification & Expense Voucher': 'Certification Numérique & Note de Frais',
      'Scan this QR Code to verify the authenticity of this receipt on MboaLift server.': 'Scannez ce QR Code pour vérifier l\'authenticité de cette facture sur le serveur MboaLift.',
      'Receipt Authenticity Verification': 'Vérification d\'Authenticité du Reçu',
      'Tax Certification & Audit Trail': 'Certification & Traçabilité Fiscale',
      'Digital verification system for business expense vouchers and receipts in Douala.': 'Système de contrôle numérique des notes de frais et reçus professionnels MboaLift Douala.',
      'OFFICIAL RECEIPT CERTIFIED COMPLIANT': 'REÇU OFFICIEL CERTIFIÉ CONFORME',
      'This document was generated and settled on the MboaLift Douala platform. Legal proof for corporate expense reimbursement.': 'Ce document a été généré et acquitté sur la plateforme MboaLift Douala. Pièce justificative légale pour remboursement de note de frais.',
      'Receipt Number :': 'Numéro de Reçu :',
      'Urban Trip :': 'Trajet Urbain :',
      'Passenger / Employee :': 'Passager / Collaborateur :',
      'Provider Driver :': 'Chauffeur Prestataire :',
      'Total Amount Settled :': 'Montant Total Acquitté :',
      'Mobile Money Transaction Reference :': 'Référence Transaction Mobile Money :',
      'Timestamp :': 'Horodatage :',
      'View Printable Receipt (PDF)': 'Voir le Reçu Imprimable (PDF)',
      'Printable Receipt': 'Reçu Imprimable',
      'PDF Receipt': 'Reçu PDF',
      'PDF Receipt & QR Code': 'Reçu PDF & QR Code',
      'Invalid or Not Found Receipt': 'Reçu Non Valide ou Introuvable',
      'Back to home': 'Retour à l\'accueil',
      'MboaLift Home': 'Accueil MboaLift',

      // Driver Voice Announcements
      'Driver Voice Announcements (Bendskin & Taxis)': 'Annonces Vocales Chauffeur (Bendskin & Taxis)',
      'Keep your eyes on the road: incoming rides are announced out loud.': 'Ne quittez pas la route des yeux : vos courses en direct sont lues à voix haute.',
      'Voice Alerts ON': 'Voix Active',
      'Voice Alerts OFF': 'Voix Coupée',
      'Test voice': 'Tester la voix',
      'Test speaker': 'Tester le haut-parleur',
      'Voice Alert ON': 'Annonce Vocale ON',
      'Voice Alert OFF': 'Annonce Vocale OFF',
      'New ride detected!': 'Nouvelle course détectée !',
      'Accept': 'Accepter',
      'MboaLift Passenger': 'Passager MboaLift',

      // Driver Daily Earnings & Cashout
      'Mobile Money Revenue & Cashout': 'Revenus & Retraits Mobile Money',
      'Live tracking of revenue collected via MTN MoMo and Orange Money (Douala).': 'Suivi en direct des recettes encaissées via MTN MoMo et Orange Money (Douala).',
      'Last 7 Days': '7 Derniers Jours',
      'Last 4 Weeks': '4 Dernières Semaines',
      'Cumulative MoMo earnings': 'Recettes cumulées MoMo',
      'Cumulative OM earnings': 'Recettes cumulées OM',
      'Total Collected': 'Total Encaissé',
      'Rides turnover': 'Chiffre d\'affaires courses',
      'Available Balance': 'Solde Disponible',
      'Available balance for cashout :': 'Solde disponible au retrait :',
      'Cashout earnings (Mobile Money)': 'Retirer mes gains (Cashout)',
      'Instant Mobile Money Cashout': 'Retrait Instantané Mobile Money',
      'Destination operator :': 'Opérateur de destination :',
      'Mobile Money number (9 digits) :': 'Numéro Mobile Money (9 chiffres) :',
      'Amount to transfer (XAF) :': 'Montant à virer (XAF) :',
      'Full balance': 'Tout le solde',
      'Confirm payout transfer': 'Confirmer le virement',
      'Daily revenue (last 7 days)': 'Revenus quotidiens (7 derniers jours)',
      'Weekly revenue (last 4 weeks)': 'Revenus hebdomadaires (4 dernières semaines)',
      'Payment share :': 'Part des paiements :',
      'This week': 'Cette semaine',
      'Today': 'Aujourd\'hui',
    },

    // French -> English (allows flawless switching back to English on French templates!)
    en: {
      'Accueil': 'Home',
      'Tableau de bord': 'Dashboard',
      'Demander une course': 'Request Ride',
      'Courses partagées': 'Shared Rides',
      'Mes courses': 'My Rides',
      'Paiements': 'Payments',
      'Assistant IA': 'AI Assistant',
      'Profil': 'Profile',
      'Déconnexion': 'Logout',
      'Tableau de bord chauffeur': 'Driver Dashboard',
      'Courses disponibles': 'Available Rides',
      'Mon statut': 'My Status',
      'Tableau de bord admin': 'Admin Dashboard',
      'Tableau de bord administrateur': 'Admin Dashboard',
      'Utilisateurs': 'Users',
      'Chauffeurs': 'Drivers',
      'Connexion passager': 'Passenger Login',
      'Inscription passager': 'Passenger Register',
      'Connexion chauffeur': 'Driver Login',
      'Inscription chauffeur': 'Driver Register',
      'Administration': 'Admin',
      'Préparation de votre trajet…': 'Preparing your ride…',
      'MboaLift — Réinventons les déplacements à Douala © 2026': 'MboaLift — Re-invent Douala\'s Ride © 2026',
      'Projet de défi de programmation scolaire': 'School coding challenge project',
      'Réinventer le transport à Douala 🇨🇲': 'Reinventing Douala\'s Ride 🇨🇲',
      'Déplacez-vous plus vite.': 'Move faster.',
      'Voyagez avec MboaLift.': 'Ride with MboaLift.',
      'La plateforme de mobilité urbaine conçue sur-mesure pour Douala.': 'The urban mobility platform custom-built for Douala.',
      'Choisissez entre': 'Choose between',
      'pour battre les embouteillages,': 'to beat traffic jams,',
      'pour vos trajets partagés, ou': 'for shared trips, or',
      'Payez en toute sécurité par': 'Pay safely with',
      'Commander une course': 'Request a Ride',
      'Covoiturage urbain': 'Urban Carpooling',
      'Passager : Inscription': 'Passenger Register',
      'Chauffeur : Inscription': 'Driver Register',
      'Déjà inscrit ?': 'Already registered?',
      'Connexion Passager': 'Passenger Login',
      'Connexion Chauffeur': 'Driver Login',
      'Pensé pour Douala': 'Built for Douala',
      'Bendskin & Taxis Jaunes': 'Bendskin & Yellow Cabs',
      'Assistant IA Local': 'Local AI Assistant',
      'Partage Trajet Sécurité': 'Ride Safety Sharing',
      'Les 3 modes de transport MboaLift': 'The 3 MboaLift ride modes',
      'Le sauveur des embouteillages de Douala. Slalome au Carrefour Ndokoti et sur le Pont du Wouri. Idéal pour 1 personne pressée (-30% économique).': 'The lifesaver of Douala traffic jams. Weaves through Ndokoti Junction and Wouri Bridge. Ideal for 1 person in a hurry (-30% economic).',
      'L\'icône des rues de Douala. Jusqu\'à 4 passagers, parfait pour les trajets quotidiens, les emplettes au marché et le covoiturage partagé.': 'The icon of Douala streets. Up to 4 passengers, perfect for everyday trips, market shopping, and shared rides.',
      'Véhicule privé climatisé avec chauffeur attitré. Recommandé pour l\'Aéroport de Douala, les réunions à Bonanjo et les soirées.': 'Air-conditioned private vehicle with dedicated driver. Recommended for Douala Airport, Bonanjo business meetings, and night events.',
      'Comment ça fonctionne ?': 'How it works',
      'Inscription simple': 'Simple registration',
      'Créez un compte Passager pour commander, ou un compte Chauffeur pour accepter des courses.': 'Create a Passenger account to book, or a Driver account to accept rides.',
      'Demandez ou Partagez': 'Request or Share',
      'Choisissez vos quartiers (Akwa, Bonamoussadi, Bonabéri, etc.) et visualisez le tarif transparent calculé par le serveur.': 'Choose your neighborhoods (Akwa, Bonamoussadi, Bonabéri, etc.) and view the transparent server-calculated fare.',
      'Paiement MoMo / Orange': 'MoMo / Orange Payment',
      'Dès l\'acceptation par le chauffeur, validez votre paiement sécurisé directement par USSD sur votre téléphone.': 'Once accepted by the driver, confirm your secure payment directly via USSD on your phone.',
      'Roulez en sécurité & Notez': 'Ride safely & Rate',
      'Partagez les coordonnées de votre chauffeur avec vos proches par WhatsApp et attribuez une note à l\'arrivée.': 'Share your driver details with relatives via WhatsApp and rate at arrival.',
      'Lieux & Quartiers desservis à Douala': 'Locations & Neighborhoods served in Douala',
      'Tableau de bord passager — demandez des courses et payez avec MoMo': 'Passenger dashboard — request rides and pay with MoMo',
      'Total des courses': 'Total Rides',
      'En attente': 'Pending',
      'Terminées': 'Completed',
      'Annulées': 'Cancelled',
      'Total payé (XAF)': 'Total Paid (XAF)',
      'Paiement Mobile Money (MoMo / Orange Money)': 'Mobile Money Payment (MoMo / Orange Money)',
      'Ces courses sont acceptées ou terminées et prêtes à être réglées. Vous validerez la transaction par prompt USSD sur votre téléphone avec votre code secret personnel.': 'These rides are accepted or completed and ready to be paid. You will validate the transaction via USSD prompt on your phone with your personal secret PIN.',
      'Payer par MoMo / OM': 'Pay via MoMo / OM',
      'Courses récentes': 'Recent Rides',
      'Tout voir': 'View All',
      'Itinéraire': 'Route',
      'Montant': 'Amount',
      'Statut': 'Status',
      'Action': 'Action',
      'Actions': 'Actions',
      'Course': 'Ride',
      'Aucune course pour le moment.': 'No rides yet.',
      'Demander votre première course': 'Request your first ride',
      'Historique des paiements': 'Payment History',
      'Demander à l\'assistant IA': 'Ask AI Assistant',
      'Conseil Trafic Douala :': 'Douala Traffic Tip:',
      'Aux heures de pointe sur le Pont du Wouri, Ndokoti ou Rond-Point Deido, choisissez un Bendskin 🏍️ pour éviter les embouteillages !': 'During rush hours on the Wouri Bridge, Ndokoti or Deido roundabout, pick a Bendskin 🏍️ to dodge traffic jams!',
      'Type de transport': 'Transport mode',
      'Anti-bouchons • 1 passager max': 'Traffic-dodger • 1 passenger max',
      'Éco (-30%)': 'Eco (-30%)',
      'Classique Douala • 1 à 4 passagers': 'Douala classic • 1 to 4 passengers',
      'Populaire': 'Popular',
      'Climatisé • Privé / Aéroport': 'Air-conditioned • Private / Airport',
      'Lieu de départ (Pickup)': 'Pickup location (Départ)',
      'Lieu d\'arrivée (Destination)': 'Destination (Arrivée)',
      'Choisissez parmi les quartiers majeurs de Douala.': 'Choose from major Douala neighborhoods.',
      'Nombre de passagers': 'Number of passengers',
      'Le Taxi standard accepte jusqu\'à 4 passagers. Le Bendskin accepte 1 passager.': 'Standard Taxi accepts up to 4 passengers. Bendskin accepts 1.',
      'Bendskin moto-taxi : 1 seul passager pour votre sécurité.': 'Bendskin moto-taxi: strictly 1 passenger for your safety.',
      'Capacité : jusqu\'à 4 passagers.': 'Capacity: up to 4 passengers.',
      'Trajet :': 'Route:',
      'Mode :': 'Mode:',
      'Tarif estimé :': 'Estimated Fare:',
      'Tarif transparent garanti avant le départ. Paiement par MTN MoMo ou Orange Money.': 'Transparent fare guaranteed before departure. Payment via MTN MoMo or Orange Money.',
      'Chauffeurs disponibles à proximité': 'Available nearby drivers',
      'Indiquez votre lieu de départ pour voir les chauffeurs libres à proximité.': 'Specify your pickup location to see free nearby drivers.',
      'N\'importe quel chauffeur disponible (premier à accepter)': 'Any available driver (first to accept)',
      'Tous les chauffeurs disponibles': 'All available drivers',
      'Zone de disponibilité basée sur la présence active déclarée du chauffeur.': 'Availability area based on the driver\'s declared active location.',
      'Commander la course': 'Request Ride',
      'Mes Trajets': 'My Rides',
      'Suivez vos courses en temps réel, payez par Mobile Money et partagez vos trajets pour votre sécurité.': 'Track your rides in real time, pay with Mobile Money, and share your trips for safety.',
      'Courses que j\'ai demandées': 'Rides I requested',
      '+ Nouvelle course': '+ New ride',
      'Passager': 'Passenger',
      'Passagers': 'Passengers',
      'Chauffeur': 'Driver',
      'Paiement': 'Payment',
      'Actions & Sécurité': 'Actions & Safety',
      'En recherche...': 'Searching...',
      'Payé ✅': 'Paid ✅',
      'En attente ⏳': 'Pending ⏳',
      'Non payé': 'Unpaid',
      'Annuler': 'Cancel',
      'Partager': 'Share',
      'Payer MoMo/OM': 'Pay MoMo/OM',
      'Noter ⭐': 'Rate ⭐',
      'Noter': 'Rate',
      'Quitter': 'Leave',
      'Vous n\'avez pas encore demandé de courses.': 'You haven\'t requested any rides yet.',
      'Demandez votre premier trajet': 'Request your first ride',
      'Trajets partagés rejoints': 'Shared rides joined',
      'Voir les covoiturages': 'View shared rides',
      'Créateur': 'Owner',
      'Propriétaire': 'Owner',
      'Vous n\'avez rejoint aucun trajet partagé pour le moment.': 'You haven\'t joined any shared rides yet.',
      'Rejoindre la course': 'Join Ride',
      'Aucune course partagée compatible disponible pour le moment.': 'No compatible shared rides available right now.',
      'Demandez votre propre course à la place.': 'Request your own ride instead.',
      'Paiement de votre course': 'Payment for your ride',
      'Réglez votre trajet en toute sécurité avec MTN MoMo ou Orange Money.': 'Pay for your ride securely with MTN MoMo or Orange Money.',
      'Type de véhicule :': 'Vehicle type:',
      'Montant à régler :': 'Amount to pay:',
      'Opérateur Mobile Money': 'Mobile Money Operator',
      'Numéro de téléphone (Cameroun)': 'Phone number (Cameroon)',
      'Entrez votre numéro à 9 chiffres. Vous recevrez un prompt USSD pour valider avec votre code secret.': 'Enter your 9-digit number. You will receive a USSD prompt to confirm with your secret PIN.',
      'Sécurité absolue : Nous ne vous demandons JAMAIS votre code PIN secret sur ce site. La confirmation se fait directement sur votre téléphone.': 'Absolute security: We NEVER ask for your secret PIN on this website. Confirmation is done directly on your phone.',
      'Astuce démo : un numéro se terminant par 0 simule un échec/annulation, tout autre numéro déclenche la confirmation.': 'Demo tip: a phone ending with 0 simulates failure/cancellation; any other number confirms payment.',
      'Historique des Paiements': 'Payment History',
      'Consultez et vérifiez vos transactions MTN Mobile Money et Orange Money.': 'View and verify your MTN Mobile Money and Orange Money transactions.',
      'Référence': 'Reference',
      'Téléphone': 'Phone',
      'Vérifier': 'Verify',
      'Validé': 'Confirmed',
      'Aucun paiement enregistré pour l\'instant.': 'No payments recorded yet.',
      'Espace Chauffeur Douala': 'Douala Driver Space',
      'Consultez les demandes de courses disponibles à Douala et suivez vos gains Mobile Money.': 'View live ride requests in Douala and track your Mobile Money earnings.',
      'Total Gains (XAF)': 'Total Earnings (XAF)',
      'Voir les courses disponibles': 'View available rides',
      'Modifier ma position / statut': 'Update my location / status',
      'Acceptez une course en attente à Douala. Dès que vous acceptez, la course vous est exclusivement assignée.': 'Accept a pending ride in Douala. Once accepted, the ride is exclusively assigned to you.',
      'Demandée à': 'Requested at',
      'Accepter la course': 'Accept Ride',
      'Aucune course en attente pour le moment. Vérifiez que votre statut est bien défini sur "free" dans votre profil.': 'No pending rides right now. Verify that your status is set to "free" in your profile.',
      'Mes Courses Prises en Charge': 'My Accepted Rides',
      'Gérez vos trajets acceptés, démarrez la course et validez la fin du trajet pour percevoir vos gains.': 'Manage your accepted rides, start the trip, and complete it to receive your earnings.',
      'Démarrer trajet': 'Démarrer trajet',
      'Terminer course ✅': 'Complete Ride ✅',
      'Terminée': 'Completed',
      'Vous n\'avez pas encore de courses assignées.': 'You don\'t have any assigned rides yet.',
      'Consulter les courses disponibles': 'Browse available rides',
      'Inscription Chauffeur': 'Driver Registration',
      'Conduisez à Douala (Taxi Jaune, Moto Bendskin ou Voiture Confort)': 'Drive in Douala (Yellow Taxi, Bendskin Moto, or Comfort Car)',
      'Nom complet': 'Full Name',
      'Numéro de téléphone': 'Phone Number',
      'Adresse email': 'Email Address',
      'Catégorie de véhicule': 'Vehicle Category',
      'Taxi Jaune (Voiture partagée standard)': 'Yellow Taxi (Standard shared cab)',
      'Bendskin Moto-Taxi': 'Bendskin Moto-Taxi',
      'Voiture Confort (Climatisée / Privée)': 'Comfort Car (AC / Private)',
      'Détails du véhicule & immatriculation': 'Vehicle details & license plate',
      'Mot de passe': 'Password',
      'Confirmer le mot de passe': 'Confirm Password',
      'S\'inscrire comme Chauffeur': 'Register as Driver',
      'Déjà chauffeur ?': 'Already a driver?',
      'Vous êtes passager ?': 'Are you a rider?',
      'Inscription Passager': 'Rider Registration',
      'Ma position et disponibilité': 'My Location & Availability',
      'Indiquez où vous êtes à Douala pour que les passagers vous voient comme chauffeur disponible.': 'Set where you are in Douala so passengers can see you as a free nearby driver.',
      'Quartier actuel': 'Current area',
      '-- Sélectionnez votre quartier --': '-- Select your area --',
      'Disponibilité': 'Availability',
      'Disponible (peut accepter des courses)': 'Free (can accept rides)',
      'Occupé (en course)': 'Busy (on a trip)',
      'Enregistrer le statut': 'Save Status',
      'Aucun GPS n\'est utilisé. Les passagers vous voient lorsque leur départ est dans la même zone ou à proximité.': 'No GPS is used. Passengers see you when their pickup is in the same or nearby area.',
      'Gestion des courses': 'Manage Rides',
      'Gestion des Courses': 'Manage Rides',
      'Recherche par nom, départ ou destination...': 'Search by name, pickup, or destination...',
      'Tous les statuts': 'All statuses',
      'Total des chauffeurs': 'Total Drivers',
      'Gérer les chauffeurs': 'Manage Drivers',
      'Gestion des chauffeurs': 'Manage Drivers',
      'Gestion des Chauffeurs': 'Manage Drivers',
      'Supervisez les chauffeurs de Bendskin (moto-taxis), Taxis Jaunes et Voitures Confort.': 'Supervise Bendskin (moto-taxi), Yellow Taxi, and Comfort Car drivers.',
      'Aucun chauffeur trouvé.': 'No drivers found.',
      'Filtrer': 'Filter',
      'Accepter': 'Accept',
      'Démarrer': 'Start',
      'Suivi des paiements': 'Payment Tracking',
      'Suivi des Paiements': 'Payment Tracking',
      'Supervision des transactions MTN Mobile Money et Orange Money.': 'Supervision of MTN Mobile Money and Orange Money transactions.',
      'Recherche par transaction, nom ou téléphone...': 'Search by transaction, name or phone...',
      'Recherche par nom, e-mail ou téléphone...': 'Search by name, email or phone...',
      'Rechercher': 'Search',
      'Désactiver': 'Disable',
      'Activer': 'Enable',
      'Supprimer': 'Delete',
      'Aucun utilisateur trouvé.': 'No users found.',

      // Map & Tracker
      'Carte Urbaine & Itinéraire Douala': 'Douala Urban Route Map',
      'Carte Urbaine &amp; Itinéraire Douala': 'Douala Urban Route Map',
      'Trafic & Chauffeurs en direct': 'Live Traffic & Drivers',
      'Trafic &amp; Chauffeurs en direct': 'Live Traffic & Drivers',
      'Carte de la Demande & Position Chauffeur': 'Demand & Driver Location Map',
      'Carte de la Demande &amp; Position Chauffeur': 'Demand & Driver Location Map',
      'Secteur déclaré :': 'Declared Area:',
      'Repères :': 'Landmarks:',
      'Point de départ': 'Pickup Point',
      'Suivi Course en direct': 'Live Ride Tracking',
      'Recherche d\'un chauffeur disponible... ⏳': 'Searching for an available driver... ⏳',
      'Chauffeur en route vers': 'Driver on the way to',
      'Course en cours vers': 'Trip in progress to',
      'Arrivé à destination ! Course terminée ✅': 'Arrived at destination! Ride completed ✅',
      '1. Demande': '1. Request',
      'Recherche chauffeur': 'Searching driver',
      '2. Chauffeur': '2. Driver',
      'En route vers vous': 'On the way to you',
      '3. En course': '3. En route',
      'Trajet en cours': 'Trip in progress',
      '4. Arrivée': '4. Arrival',
      'Paiement & Avis': 'Payment & Review',
      'Paiement &amp; Avis': 'Payment & Review',
      'Détails de mes courses': 'My ride details',
      'Votre présence est visible aux passagers de votre secteur.': 'Your presence is visible to nearby passengers in your area.',
      'Repères oranges : demandes de courses en attente à accepter immédiatement.': 'Orange markers: pending ride requests available to accept immediately.',

      'Connexion administrateur': 'Admin Login',
      'Accès restreint': 'Restricted access',
      'Nom d\'utilisateur': 'Username',
      'Se connecter comme administrateur': 'Login as Admin',
      'Mon profil': 'My Profile',
      'Membre depuis': 'Member since',
      'Impossible de charger le profil.': 'Could not load profile.',
      'Évaluer votre course': 'Rate Your Ride',
      'Note (1–5)': 'Rating (1–5)',
      'Commentaire (facultatif)': 'Comment (optional)',
      'Envoyer la note': 'Submit Rating',
      'Posez des questions sur les courses, les tarifs, les paiements et plus encore': 'Ask questions about rides, fares, payments and more',
      'Contexte utilisé par l\'assistant :': 'Context used by the assistant:',
      'Nom :': 'Name:',
      'Course actuelle :': 'Current ride:',
      'Tarif :': 'Fare:',
      'Statut de la course :': 'Ride status:',
      'Statut du paiement :': 'Payment status:',
      'Vous :': 'You:',
      'Assistant :': 'Assistant:',
      'Votre question': 'Your question',
      'Envoyer': 'Send',
      'Exemples de questions': 'Example questions',
      'Quel est mon tarif estimé ?': 'How much is my estimated fare?',
      'Comment demander une course ?': 'How do I request a ride?',
      'Comment rejoindre une course partagée ?': 'How do I join a shared ride?',
      'Quel est le statut de ma course ?': 'What is the status of my ride?',
      'Comment effectuer un paiement MoMo ?': 'How do I make a MoMo payment?',
      'Mon paiement a échoué, que dois-je faire ?': 'My payment failed, what should I do?',
      'Comment évaluer une course ?': 'How can I rate a ride?',
      'L\'IA est un simple assistant. Elle ne peut pas modifier le statut d\'une course ou d\'un paiement.': 'The AI is only an assistant. It cannot change ride or payment status.',
      'Bonjour ! Je suis votre assistant MboaLift.': 'Hello! I am your MboaLift assistant.',
      'Posez-moi des questions sur les tarifs, la demande de course, le covoiturage, les paiements MoMo ou le statut de votre course.': 'Ask me about fares, requesting rides, shared rides, MoMo payments, or ride status.',
      'Réflexion en cours...': 'Thinking...',
      'Désolé, je n\'ai pas pu répondre.': 'Sorry, I could not answer.',
      'Désolé, impossible de contacter l\'assistant. Veuillez réessayer.': 'Sorry, I could not reach the assistant. Please try again.',
      'Bon retour': 'Welcome Back',
      'Connectez-vous à votre compte MboaLift': 'Login to your MboaLift account',
      'E-mail': 'Email',
      'Se connecter': 'Login',
      'Pas encore de compte ?': 'Don\'t have an account?',
      'S\'inscrire comme Passager': 'Register as Rider',
      'Vous êtes chauffeur ?': 'Are you a driver?',
      'Créer un compte': 'Create Account',
      'Rejoignez MboaLift aujourd\'hui': 'Join MboaLift today',
      'S\'inscrire': 'Register',
      'Vous avez déjà un compte ?': 'Already have an account?',
      'Vous voulez conduire ?': 'Want to drive?',
      'Nouveau chauffeur ?': 'New driver?',
      'Passager ?': 'Rider?',
      'Accédez à votre compte chauffeur': 'Access your driver account',
      'Se connecter comme chauffeur': 'Login as Driver',
      'Invalide (même lieu)': 'Invalid (same location)',
      'Non disponible': 'Not available',
      'XAF (estimation)': 'XAF (estimate)',
      'Les mots de passe ne correspondent pas.': 'Passwords do not match.',
      'Le mot de passe doit comporter au moins 6 caractères.': 'Password must be at least 6 characters.',
      'Le lieu de départ et la destination ne peuvent pas être identiques.': 'Pickup and destination cannot be the same.',
      'Rejoindre cette course partagée ?': 'Join this shared ride?',
      'Désactiver cet utilisateur ?': 'Disable this user?',
      'Supprimer définitivement cet utilisateur ?': 'DELETE this user permanently?',
      'Quitter ce trajet partagé ?': 'Leave this shared ride?',
      'Voulez-vous vraiment annuler cette demande de course ?': 'Are you sure you want to cancel this ride request?',
      'Annuler et libérer cette course pour un autre chauffeur ?': 'Cancel and release this ride for another driver?',
      'En attente': 'Pending',
      'Acceptée': 'Accepted',
      'En cours': 'In Progress',
      'Terminée': 'Completed',
      'Annulée': 'Cancelled',
      'Réussi': 'Successful',
      'Échoué': 'Failed',
      'votre@email.com': 'your@email.com',
      'Votre mot de passe': 'Your password',
      'ex. Jean Mbarga': 'e.g. Jean Mbarga',
      'ex. 670000000': 'e.g. 670000000',
      'ex. jean@example.com': 'e.g. jean@example.com',
      'Au moins 6 caractères': 'At least 6 characters',
      'Répétez le mot de passe': 'Repeat password',
      'Saisissez ou choisissez (ex. Akwa, Bonanjo, Bonabéri)': 'Type or choose (e.g. Akwa, Bonanjo, Bonabéri)',
      'Saisissez ou choisissez (ex. Bonamoussadi, Aéroport, Ndokoti)': 'Type or choose (e.g. Bonamoussadi, Aéroport, Ndokoti)',
      'Saisissez votre question...': 'Type your question...',
      'Partagez votre expérience...': 'Share your experience...',
      'Chauffeur en route': 'Driver on the way',
      'Course en cours': 'Trip in progress',
      'Chauffeur assigné': 'Assigned driver',
      'Partager ma sécurité WhatsApp': 'Share safety on WhatsApp',
      'Paiement validé ✅': 'Payment confirmed ✅',
      'Détails': 'Details',
      'Mission en cours': 'Active mission',
      'Course en cours assignée': 'Assigned active ride',
      'Appeler passager': 'Call passenger',
      'Démarrer le trajet ▶': 'Start trip ▶',
      'Terminer la course ✅': 'Complete ride ✅',
      'Valider le paiement': 'Confirm payment',
      'Prompt USSD reçu sur votre téléphone...': 'USSD prompt received on your phone...',
      'Code PIN secret :': 'Secret PIN code:',
      'Approuver le transfert de': 'Approve the transfer of',
      'Véhicule :': 'Vehicle:',
      'Chauffeur :': 'Driver:',
      'Contact :': 'Contact:',
      'Tarif :': 'Fare:',
      'Passager :': 'Passenger:',
      'passager(s)': 'passenger(s)',
      'Veuillez entrer un numéro de téléphone valide à 9 chiffres.': 'Please enter a valid 9-digit phone number.',

      // Weather & Traffic Alert Engine
      'Météo Pluie & Inondations Douala': 'Douala Rain & Traffic Alert Engine',
      'Alerte Inondations & Pluie Torrentielle': 'Flood Alert & Torrential Downpour',
      'Bouchon Majeur Pont du Wouri': 'Wouri Bridge Major Gridlock',
      'Météo Tropicale Douala': 'Tropical Weather Douala',
      'Trafic & Météo Idéals': 'Ideal Weather & Traffic',
      'Pluie torrentielle & Inondations détectées': 'Torrential Rain & Severe Flooding Detected',
      'Embouteillage critique sur le Pont du Wouri': 'Critical Congestion on Wouri Bridge',
      'Averses tropicales modérées': 'Moderate Tropical Showers',
      'Temps sec & Circulation normale': 'Dry Weather & Normal Flow',
      'Pluie torrentielle détectée sur Douala : risques majeurs d\'inondations à Makèpè Missokè, Bépanda et Bonabéri. Privilégiez les Voitures Confort abritées ou itinéraires déviés.': 'Torrential rain detected in Douala: severe flood risks at Makepe Missoke, Bépanda, and Bonabéri. Prefer sheltered Comfort Cars or diverted routes.',
      'Saturation majeure de l\'axe Bonabéri ↔ Rond-Point Deïdo (retard estimé : 45+ min). Privilégiez un Bendskin 🏍️ pour battre les bouchons ou différez votre départ.': 'Major gridlock on Bonabéri ↔ Rond-Point Deïdo corridor (est. delay: 45+ min). Prefer Bendskin 🏍️ to weave through traffic or delay your trip.',
      'Averses intermittentes sur Akwa, Bonanjo et Ndokoti. Chaussées humides. Taxis jaunes abrités conseillés.': 'Intermittent showers across Akwa, Bonanjo, and Ndokoti. Wet roadways. Sheltered Yellow Taxis recommended.',
      'Conditions idéales pour se déplacer à Douala. Trafic fluide sur les grands boulevards et le Pont du Wouri.': 'Optimal conditions across Douala. Smooth traffic flow on main boulevards and Wouri Bridge.',
      'Zones sous surveillance :': 'Zones under watch :',
      'Zones d\'alerte :': 'Alert zones :',
      'Aucune zone inondée': 'No flooded zones',
      'Tester les conditions en direct :': 'Test live conditions :',
      'Pluie torrentielle & Inondations': 'Torrential rain & floods',
      'Bouchon Pont Wouri': 'Wouri Bridge jam',
      'Averses modérées': 'Moderate showers',
      'Ciel dégagé & Fluide': 'Clear & smooth',
      'Météo :': 'Weather :',
      'Alerte Inondation Immédiate : ': 'Immediate Flood Alert : ',
      'Traversée du Pont du Wouri saturée !': 'Wouri Bridge crossing saturated !',
      'Abrité Météo': 'Sheltered',
      'Anti-Bouchon': 'Beat-traffic',

      // Emergency SOS Center
      'SOS Urgence': 'Emergency SOS',
      'SOS Urgence Douala': 'SOS Urgence Douala',
      'Centre d\'Urgence & Sécurité Douala': 'Douala Emergency & Safety Center',
      'Accès direct aux numéros d\'urgence officiels du Cameroun & alerte de détresse géolocalisée.': 'Direct access to official Cameroon emergency numbers & distress broadcast.',
      'Police Secours Douala': 'Douala Police Secours',
      'Gendarmerie Nationale': 'National Gendarmerie',
      'SAMU Urgences Médicales': 'SAMU Medical Emergency',
      'Sapeurs-Pompiers (20e Groupement)': 'Fire & Rescue Brigade',
      'Commissariats Centraux & patrouilles d\'intervention rapide': 'Central police precincts & rapid intervention mobile units',
      'Légion de Gendarmerie du Littoral & sécurité routière': 'Littoral Gendarmerie Legion & checkpoint safety',
      'Ambulances, Hôpital Laquintinie & Hôpital Général de Douala': 'Ambulances, Laquintinie & Douala General Hospitals',
      'Sauvetage inondations Makèpè/Bépanda, accidents routiers & incendies': 'Flood rescue Makepe/Bépanda, road accidents & firefighting',
      'Diffusion d\'Urgence Immédiate (GPS Douala)': 'Instant Distress Location Broadcast (Douala GPS)',
      'SOS WhatsApp': 'SOS WhatsApp',
      'SOS SMS (117)': 'SOS SMS (117)',
      'Copier le message': 'Copy message',
      'Balise Visuelle Flash': 'Visual Strobe Beacon',
      'Touchez l\'écran pour arrêter la balise': 'Touch the screen to stop the strobe',

      // Offline USSD & SMS Booking
      'Réservation sans Internet (USSD & SMS)': 'Offline Booking without Internet (USSD & SMS)',
      'Pas de connexion données mobiles ? Composez le code direct ou envoyez un SMS gratuit.': 'No mobile data connection? Dial direct USSD code or send a free SMS.',
      'Lieu de départ (Douala)': 'Pickup area (Douala)',
      'Destination (Douala)': 'Destination (Douala)',
      'Mode de transport': 'Transport mode',
      'Code USSD Direct à composer (sans internet) :': 'Direct USSD code to dial (no internet needed) :',
      'Gratuit 2G/3G/4G': 'Free 2G/3G/4G',
      'Composer le code USSD': 'Dial USSD code',
      'Envoyer par SMS gratuit': 'Send via free SMS',
      'Simuler l\'écran USSD (Téléphone 2G)': 'Simulate USSD screen (2G phone)',
      'Pas de forfait internet ou réseau instable à Douala ?': 'No mobile data or unstable network in Douala?',
      'Réservez immédiatement par code USSD gratuit direct *999# ou par SMS au 8800 sur n\'importe quel téléphone 2G/3G/4G.': 'Book immediately via free direct USSD code *999# or SMS to 8800 on any 2G/3G/4G phone.',
      'Réserver par USSD (*999#)': 'Book via USSD (*999#)',
      'Pas de connexion internet ?': 'No internet connection?',
      'Réservez gratuitement sans données mobiles via USSD (*999#) ou SMS.': 'Book for free with no mobile data via USSD (*999#) or SMS.',

      // Digital Trip Receipt & Tax Verification
      'Reçu Officiel de Course': 'Official Trip Receipt',
      'Reçu Officiel Acquitté': 'Official Receipt',
      'Reçu Officiel Certifié Conforme': 'Official Receipt Certified Compliant',
      '← Retour à mes courses': '← Back to my rides',
      'Retour à mes courses': 'Back to my rides',
      'Historique paiements': 'Payment history',
      '🖨️ Imprimer / Enregistrer en PDF (A4)': '🖨️ Print / Save as PDF (A4)',
      'Imprimer / Enregistrer en PDF (A4)': 'Print / Save as PDF (A4)',
      'Plateforme agréée de transport urbain multimodal Douala': 'Certified multimodal urban transport platform Douala',
      'Justificatif Fiscal & Remboursement Note de Frais': 'Tax Proof & Expense Reimbursement Voucher',
      'Justificatif Fiscal & Note de Frais': 'Tax Proof & Expense Voucher',
      'Émis le': 'Issued on',
      'Trajet effectué à Douala :': 'Trip completed in Douala :',
      'Passager / Collaborateur Bénéficiaire': 'Passenger / Beneficiary Employee',
      'Prestataire de Transport Assermenté': 'Certified Transport Provider',
      'Déplacement professionnel Douala (Akwa / Bonanjo)': 'Professional commute Douala (Akwa / Bonanjo)',
      'Véhicule Agréé Urbain': 'Certified Urban Vehicle',
      'Flotte MboaLift Douala Réseau Certifié': 'MboaLift Douala Certified Network Fleet',
      'Désignation de la prestation': 'Service Description',
      'Type de service': 'Service Type',
      'Montant (XAF)': 'Amount (XAF)',
      'Prise en charge et acheminement urbain sécurisé': 'Safe urban pickup and transit',
      'Trajet Standard': 'Standard Ride',
      'Ajustement mode de transport': 'Transport mode adjustment',
      'Ajustement Mode': 'Mode Adjustment',
      'Option confort VIP climatisé et chauffeur privé': 'Air-conditioned VIP comfort option with private driver',
      'Tarification économique Bendskin anti-bouchons (-30%)': 'Economic Bendskin traffic-beating pricing (-30%)',
      'Total Hors Taxes (HT)': 'Total Excluding Tax (HT)',
      'Base imposable': 'Taxable base',
      'Taxe sur la Valeur Ajoutée (TVA)': 'Value Added Tax (VAT)',
      'Régime d\'exonération transport urbain de personnes (CGI Cameroun)': 'Urban passenger transport exemption scheme (CGI Cameroon)',
      'TVA 0%': 'VAT 0%',
      'Net Payé (TTC) :': 'Net Paid (TTC) :',
      'Net Payé (TTC)': 'Net Paid (TTC)',
      'Paiement validé via Orange Money Cameroun': 'Payment confirmed via Orange Money Cameroon',
      'Paiement validé via MTN Mobile Money (MoMo)': 'Payment confirmed via MTN Mobile Money (MoMo)',
      'Réf. Transaction :': 'Transaction Ref. :',
      'Compte débité :': 'Debited account :',
      'VALIDÉ & ACQUITTÉ': 'VALIDATED & SETTLED',
      '✓ VALIDÉ & ACQUITTÉ': '✓ VALIDATED & SETTLED',
      'Certification Numérique & Note de Frais': 'Digital Certification & Expense Voucher',
      'Scannez ce QR Code pour vérifier l\'authenticité de cette facture sur le serveur MboaLift.': 'Scan this QR Code to verify the authenticity of this receipt on MboaLift server.',
      'Vérification d\'Authenticité du Reçu': 'Receipt Authenticity Verification',
      'Certification & Traçabilité Fiscale': 'Tax Certification & Audit Trail',
      'Système de contrôle numérique des notes de frais et reçus professionnels MboaLift Douala.': 'Digital verification system for business expense vouchers and receipts in Douala.',
      'REÇU OFFICIEL CERTIFIÉ CONFORME': 'OFFICIAL RECEIPT CERTIFIED COMPLIANT',
      'Ce document a été généré et acquitté sur la plateforme MboaLift Douala. Pièce justificative légale pour remboursement de note de frais.': 'This document was generated and settled on the MboaLift Douala platform. Legal proof for corporate expense reimbursement.',
      'Numéro de Reçu :': 'Receipt Number :',
      'Trajet Urbain :': 'Urban Trip :',
      'Passager / Collaborateur :': 'Passenger / Employee :',
      'Chauffeur Prestataire :': 'Provider Driver :',
      'Montant Total Acquitté :': 'Total Amount Settled :',
      'Référence Transaction Mobile Money :': 'Mobile Money Transaction Reference :',
      'Horodatage :': 'Timestamp :',
      '📄 Voir le Reçu Imprimable (PDF)': '📄 View Printable Receipt (PDF)',
      'Voir le Reçu Imprimable (PDF)': 'View Printable Receipt (PDF)',
      '📄 Reçu PDF': '📄 PDF Receipt',
      'Reçu PDF': 'PDF Receipt',
      '📄 Reçu PDF & QR Code': '📄 PDF Receipt & QR Code',
      'Reçu PDF & QR Code': 'PDF Receipt & QR Code',
      '❌ Reçu Non Valide ou Introuvable': '❌ Invalid or Not Found Receipt',
      'Reçu Non Valide ou Introuvable': 'Invalid or Not Found Receipt',
      'Retour à l\'accueil': 'Back to home',
      'Accueil MboaLift': 'MboaLift Home',
      'Ce reçu dématérialisé est émis conformément aux dispositions légales régissant le transport urbain et la facturation électronique au Cameroun. Il vaut justificatif de dépense professionnelle auprès des services comptables et fiscaux d\'entreprise. Pour toute réclamation, contactez le service d\'assistance MboaLift Douala : support@mboalift.cm / (+237) 233 42 04 04.': 'This electronic receipt is issued in compliance with legal regulations governing urban transport and electronic invoicing in Cameroon. It serves as official proof of business travel expenses for corporate accounting and tax filing. For inquiries, contact MboaLift Douala support: support@mboalift.cm / (+237) 233 42 04 04.',

      // Driver Voice Announcements
      'Annonces Vocales Chauffeur (Bendskin & Taxis)': 'Driver Voice Announcements (Bendskin & Taxis)',
      'Annonces Vocales Chauffeur (Bendskin &amp; Taxis)': 'Driver Voice Announcements (Bendskin & Taxis)',
      'Ne quittez pas la route des yeux : vos courses en direct sont lues à voix haute.': 'Keep your eyes on the road: incoming rides are announced out loud.',
      '🔊 Voix Active': '🔊 Voice Alerts ON',
      'Voix Active': 'Voice Alerts ON',
      '🔇 Voix Coupée': '🔇 Voice Alerts OFF',
      'Voix Coupée': 'Voice Alerts OFF',
      '⚡ Tester la voix': '⚡ Test voice',
      'Tester la voix': 'Test voice',
      'Tester le haut-parleur': 'Test speaker',
      '🔊 Annonce Vocale ON': '🔊 Voice Alert ON',
      'Annonce Vocale ON': 'Voice Alert ON',
      '🔇 Annonce Vocale OFF': '🔇 Voice Alert OFF',
      'Annonce Vocale OFF': 'Voice Alert OFF',
      'Nouvelle course détectée !': 'New ride detected!',
      '⚡ Accepter': '⚡ Accept',
      'Passager MboaLift': 'MboaLift Passenger',

      // Driver Daily Earnings & Cashout
      'Revenus & Retraits Mobile Money': 'Mobile Money Revenue & Cashout',
      'Revenus &amp; Retraits Mobile Money': 'Mobile Money Revenue & Cashout',
      'Suivi en direct des recettes encaissées via MTN MoMo et Orange Money (Douala).': 'Live tracking of revenue collected via MTN MoMo and Orange Money (Douala).',
      '📅 7 Derniers Jours': '📅 Last 7 Days',
      '7 Derniers Jours': 'Last 7 Days',
      '📆 4 Dernières Semaines': '📆 Last 4 Weeks',
      '4 Dernières Semaines': 'Last 4 Weeks',
      'Recettes cumulées MoMo': 'Cumulative MoMo earnings',
      'Recettes cumulées OM': 'Cumulative OM earnings',
      'Total Encaissé': 'Total Collected',
      'Chiffre d\'affaires courses': 'Rides turnover',
      'Solde Disponible': 'Available Balance',
      'Solde disponible au retrait :': 'Available balance for cashout :',
      '💸 Retirer mes gains (Cashout)': '💸 Cashout earnings (Mobile Money)',
      'Retirer mes gains (Cashout)': 'Cashout earnings (Mobile Money)',
      '💸 Retrait Instantané Mobile Money': '💸 Instant Mobile Money Cashout',
      'Retrait Instantané Mobile Money': 'Instant Mobile Money Cashout',
      'Opérateur de destination :': 'Destination operator :',
      'Numéro Mobile Money (9 chiffres) :': 'Mobile Money number (9 digits) :',
      'Montant à virer (XAF) :': 'Amount to transfer (XAF) :',
      'Tout le solde': 'Full balance',
      '⚡ Confirmer le virement': '⚡ Confirm payout transfer',
      'Confirmer le virement': 'Confirm payout transfer',
      'Revenus quotidiens (7 derniers jours)': 'Daily revenue (last 7 days)',
      'Revenus hebdomadaires (4 dernières semaines)': 'Weekly revenue (last 4 weeks)',
      'Part des paiements :': 'Payment share :',
      'Cette semaine': 'This week',
      'Aujourd\'hui': 'Today',
    }
  };

  let currentLang = 'en';

  // Normalize string for consistent dictionary matching
  function normalize(str) {
    if (!str) return '';
    return str.replace(/\s+/g, ' ').trim();
  }

  // Dynamic pattern translation (handles variables, IDs, names, fares, dates)
  function translatePatterns(text, lang) {
    if (!text) return text;
    let out = text;

    if (lang === 'fr') {
      out = out.replace(/\bRide #(\d+)\b/gi, 'Course n° $1');
      out = out.replace(/\bDriver:\s*/gi, 'Chauffeur : ');
      out = out.replace(/\bOwner:\s*/gi, 'Propriétaire : ');
      out = out.replace(/\bPassengers:\s*(\d+)\s*\+\s*(\d+)\s*joined/gi, 'Passagers : $1 + $2 rejoints');
      out = out.replace(/\bPassengers:\s*/gi, 'Passagers : ');
      out = out.replace(/\bFare:\s*/gi, 'Tarif : ');
      out = out.replace(/\bRoute:\s*/gi, 'Itinéraire : ');
      out = out.replace(/\bAmount:\s*/gi, 'Montant : ');
      out = out.replace(/\bStatus:\s*/gi, 'Statut : ');
      out = out.replace(/\bHello,\s*([^\s👋🚗]+)/gi, 'Bonjour, $1');
      out = out.replace(/\bWelcome, driver\s*([^!]+)!/gi, 'Bienvenue, chauffeur $1 !');
      out = out.replace(/\bRide marked as\s*([^.]+)\./gi, 'Course marquée comme $1.');
      out = out.replace(/No free drivers near\s*([^\n.]+)\s*right now/gi, 'Aucun chauffeur disponible près de $1 pour le moment');
      out = out.replace(/\bPay\s+([\d\s]+)\s+XAF\b/gi, 'Payer $1 XAF');
      out = out.replace(/(\d+)\s+passenger\(s\)/gi, '$1 passager(s)');
      out = out.replace(/\bTotal Rides:\s*(\d+)/gi, 'Total des courses : $1');
      out = out.replace(/\bTotal Users:\s*(\d+)/gi, 'Total des utilisateurs : $1');
      out = out.replace(/\bMember since\s*/gi, 'Membre depuis ');
      out = out.replace(/\bSearching\.\.\./gi, 'En recherche...');
      out = out.replace(/\bOfficial Trip Receipt\s*-\s*([A-Z0-9-]+)\b/gi, 'Reçu Officiel de Course - $1');
      out = out.replace(/\bIssued on\s*(\d{2}\/\d{2}\/\d{4})/gi, 'Émis le $1');
      out = out.replace(/\bUrban ride Douala\s*:\s*(.+?)➔(.+)/gi, 'Course urbaine Douala : $1 ➔ $2');
      out = out.replace(/\bUrban ride Douala\s*:\s*(.+?)→(.+)/gi, 'Course urbaine Douala : $1 → $2');
      out = out.replace(/\bTransport mode adjustment\s*\((.+?)\)/gi, 'Ajustement mode de transport ($1)');
      out = out.replace(/\bNew ride available at\s*(.+?)\s*for\s*([\d\s]+)\s*(?:FCFA|XAF)\b/gi, 'Nouvelle course disponible à $1 pour $2 FCFA');
    } else {
      out = out.replace(/\bCourse n°\s*(\d+)\b/gi, 'Ride #$1');
      out = out.replace(/\bCourse #(\d+)\b/gi, 'Ride #$1');
      out = out.replace(/\bChauffeur\s*:\s*/gi, 'Driver: ');
      out = out.replace(/\bPropriétaire\s*:\s*/gi, 'Owner: ');
      out = out.replace(/\bCréateur\s*:\s*/gi, 'Owner: ');
      out = out.replace(/\bPassagers\s*:\s*(\d+)\s*\+\s*(\d+)\s*rejoints/gi, 'Passengers: $1 + $2 joined');
      out = out.replace(/\bPassagers\s*:\s*/gi, 'Passengers: ');
      out = out.replace(/\bTarif\s*:\s*/gi, 'Fare: ');
      out = out.replace(/\bItinéraire\s*:\s*/gi, 'Route: ');
      out = out.replace(/\bMontant\s*:\s*/gi, 'Amount: ');
      out = out.replace(/\bStatut\s*:\s*/gi, 'Status: ');
      out = out.replace(/\bBonjour,\s*([^\s👋🚗]+)/gi, 'Hello, $1');
      out = out.replace(/\bBienvenue,\s*chauffeur\s*([^!]+)!/gi, 'Welcome, driver $1!');
      out = out.replace(/\bCourse marquée comme\s*([^.]+)\./gi, 'Ride marked as $1.');
      out = out.replace(/Aucun chauffeur disponible près de\s*([^\n.]+)\s*pour le moment/gi, 'No free drivers near $1 right now');
      out = out.replace(/\bPayer\s+([\d\s]+)\s+XAF\b/gi, 'Pay $1 XAF');
      out = out.replace(/(\d+)\s+passager\(s\)/gi, '$1 passenger(s)');
      out = out.replace(/\bTotal des courses\s*:\s*(\d+)/gi, 'Total Rides: $1');
      out = out.replace(/\bTotal des utilisateurs\s*:\s*(\d+)/gi, 'Total Users: $1');
      out = out.replace(/\bMembre depuis\s*/gi, 'Member since ');
      out = out.replace(/\bEn recherche\.\.\./gi, 'Searching...');
      out = out.replace(/\bReçu Officiel de Course\s*-\s*([A-Z0-9-]+)\b/gi, 'Official Trip Receipt - $1');
      out = out.replace(/\bÉmis le\s*(\d{2}\/\d{2}\/\d{4})/gi, 'Issued on $1');
      out = out.replace(/\bCourse urbaine Douala\s*:\s*(.+?)➔(.+)/gi, 'Urban ride Douala : $1 ➔ $2');
      out = out.replace(/\bCourse urbaine Douala\s*:\s*(.+?)→(.+)/gi, 'Urban ride Douala : $1 → $2');
      out = out.replace(/\bAjustement mode de transport\s*\((.+?)\)/gi, 'Transport mode adjustment ($1)');
      out = out.replace(/\bNouvelle course disponible à\s*(.+?)\s*pour\s*([\d\s]+)\s*(?:FCFA|XAF)\b/gi, 'New ride available at $1 for $2 FCFA');
    }
    return out;
  }

  // Translate a phrase using dictionary and pattern fallbacks
  function translatePhrase(raw, lang) {
    if (!raw) return raw;
    const clean = normalize(raw);
    if (!clean) return raw;

    const dict = translations[lang] || {};
    if (dict[clean]) {
      return raw.replace(clean, dict[clean]);
    }

    // Try case-insensitive lookup
    const lowerClean = clean.toLowerCase();
    for (const key of Object.keys(dict)) {
      if (key.toLowerCase() === lowerClean) {
        return raw.replace(clean, dict[key]);
      }
    }

    // Apply regex pattern rules
    return translatePatterns(raw, lang);
  }

  // Concise navigation translations to keep the top navbar compact and prevent wrapping
  const navTranslations = {
    fr: {
      'Dashboard': 'Tableau de bord',
      'Request Ride': 'Commander',
      'Shared Rides': 'Covoiturage',
      'My Rides': 'Mes courses',
      'Payments': 'Paiements',
      'AI Assistant': 'Assistant IA',
      'Profile': 'Profil',
      'Logout': 'Déconnexion',
      'Driver Dashboard': 'Espace Chauffeur',
      'Available Rides': 'Disponibles',
      'My Status': 'Mon statut',
      'Admin Dashboard': 'Admin',
      'Users': 'Utilisateurs',
      'Rides': 'Courses',
      'Home': 'Accueil',
      'Passenger Login': 'Connexion',
      'Passenger Register': 'Inscription',
      'Driver Login': 'Chauffeur Login',
      'Driver Register': 'Devenir Chauffeur',
      'Admin': 'Admin'
    },
    en: {
      'Tableau de bord': 'Dashboard',
      'Commander': 'Request Ride',
      'Demander une course': 'Request Ride',
      'Covoiturage': 'Shared Rides',
      'Courses partagées': 'Shared Rides',
      'Mes courses': 'My Rides',
      'Paiements': 'Payments',
      'Assistant IA': 'AI Assistant',
      'Profil': 'Profile',
      'Déconnexion': 'Logout',
      'Espace Chauffeur': 'Driver Dashboard',
      'Tableau de bord chauffeur': 'Driver Dashboard',
      'Disponibles': 'Available Rides',
      'Courses disponibles': 'Available Rides',
      'Mon statut': 'My Status',
      'Utilisateurs': 'Users',
      'Courses': 'Rides',
      'Accueil': 'Home',
      'Connexion': 'Passenger Login',
      'Inscription': 'Passenger Register',
      'Chauffeur Login': 'Driver Login',
      'Devenir Chauffeur': 'Driver Register',
      'Admin': 'Admin'
    }
  };

  // Translate a single text node preserving its canonical original
  function translateNode(node, lang) {
    if (!node || node.nodeType !== Node.TEXT_NODE) return;
    if (!node.nodeValue.trim()) return;
    const parent = node.parentElement;
    if (parent && ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(parent.tagName)) return;

    if (node.__mboaOriginal === undefined) {
      node.__mboaOriginal = node.nodeValue;
    }

    const base = node.__mboaOriginal;
    let translated = null;

    // If inside navbar, use concise nav translations to prevent overflow/wrap
    if (parent && parent.closest && parent.closest('.nav')) {
      const clean = normalize(base);
      if (navTranslations[lang] && navTranslations[lang][clean]) {
        translated = base.replace(clean, navTranslations[lang][clean]);
      }
    }

    if (!translated) {
      translated = translatePhrase(base, lang);
    }

    if (translated !== node.nodeValue) {
      node.nodeValue = translated;
    }
  }

  // Translate element attributes (placeholder, title, button text, select options)
  function translateAttributes(el, lang) {
    if (!el || el.nodeType !== Node.ELEMENT_NODE) return;

    // Placeholders
    if (el.hasAttribute('placeholder')) {
      if (el.__mboaOrigPlaceholder === undefined) {
        el.__mboaOrigPlaceholder = el.getAttribute('placeholder');
      }
      el.placeholder = translatePhrase(el.__mboaOrigPlaceholder, lang);
    }

    // Titles
    if (el.hasAttribute('title')) {
      if (el.__mboaOrigTitle === undefined) {
        el.__mboaOrigTitle = el.getAttribute('title');
      }
      el.title = translatePhrase(el.__mboaOrigTitle, lang);
    }

    // Aria-label
    if (el.hasAttribute('aria-label')) {
      if (el.__mboaOrigAria === undefined) {
        el.__mboaOrigAria = el.getAttribute('aria-label');
      }
      el.setAttribute('aria-label', translatePhrase(el.__mboaOrigAria, lang));
    }

    // Inputs of type submit or button
    if (el.tagName === 'INPUT' && ['submit', 'button'].includes((el.type || '').toLowerCase())) {
      if (el.__mboaOrigValue === undefined) {
        el.__mboaOrigValue = el.value;
      }
      el.value = translatePhrase(el.__mboaOrigValue, lang);
    }

    // Select options
    if (el.tagName === 'OPTION') {
      if (el.__mboaOrigText === undefined) {
        el.__mboaOrigText = el.textContent;
      }
      el.textContent = translatePhrase(el.__mboaOrigText, lang);
    }
  }

  // Full tree walker for translation
  function translateElementTree(root, lang) {
    if (!root) return;

    // 1. Traverse and translate text nodes
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) {
      textNodes.push(walker.currentNode);
    }
    for (let i = 0; i < textNodes.length; i++) {
      translateNode(textNodes[i], lang);
    }

    // 2. Translate attributes on all elements within root
    const elements = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (let i = 0; i < elements.length; i++) {
      translateAttributes(elements[i], lang);
    }
    if (root.nodeType === Node.ELEMENT_NODE) {
      translateAttributes(root, lang);
    }
  }

  // Main language application entry
  function applyLanguage(lang) {
    if (!['en', 'fr'].includes(lang)) lang = 'en';
    currentLang = lang;
    document.documentElement.lang = lang;
    localStorage.setItem('mboalift_language', lang);
    document.cookie = 'mboalift_language=' + lang + ';path=/;max-age=31536000;SameSite=Lax';

    // Translate DOM
    translateElementTree(document.body, lang);

    // Keep switcher select in sync
    const select = document.getElementById('languageSwitcher');
    if (select && select.value !== lang) {
      select.value = lang;
    }

    // Dispatch global event for active scripts
    window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
  }

  // Wrap window.alert and window.confirm to guarantee translated dialogs
  if (typeof window !== 'undefined') {
    const origAlert = window.alert;
    window.alert = function (msg) {
      try {
        return origAlert(translatePhrase(String(msg), currentLang));
      } catch (e) {
        return origAlert(msg);
      }
    };

    const origConfirm = window.confirm;
    window.confirm = function (msg) {
      try {
        return origConfirm(translatePhrase(String(msg), currentLang));
      } catch (e) {
        return origConfirm(msg);
      }
    };
  }

  // MutationObserver to automatically translate newly added DOM nodes (AI chat, fare box, drivers)
  let observerDebounce = null;
  const observer = new MutationObserver(function (mutations) {
    if (observerDebounce) clearTimeout(observerDebounce);
    observerDebounce = setTimeout(function () {
      mutations.forEach(function (m) {
        m.addedNodes.forEach(function (node) {
          if (node.nodeType === Node.ELEMENT_NODE || node.nodeType === Node.TEXT_NODE) {
            translateElementTree(node, currentLang);
          }
        });
      });
    }, 40);
  });

  // Initialization
  function init() {
    const select = document.getElementById('languageSwitcher');
    
    // Priority: localStorage -> cookie -> html lang / server lang -> browser language
    let saved = localStorage.getItem('mboalift_language');
    if (!saved) {
      const match = document.cookie.match(/(?:^|;\s*)mboalift_language=([^;]+)/);
      if (match) saved = match[1];
    }
    if (!saved) {
      const bodyServerLang = document.body ? document.body.getAttribute('data-server-lang') : null;
      if (bodyServerLang) saved = bodyServerLang;
    }
    if (!saved && navigator.language && navigator.language.toLowerCase().startsWith('fr')) {
      saved = 'fr';
    }
    if (!saved) saved = 'en';

    if (select) {
      select.value = saved;
      select.addEventListener('change', function () {
        applyLanguage(select.value);
      });
    }

    applyLanguage(saved);

    // Start observer once DOM is ready
    if (document.body) {
      observer.observe(document.body, { childList: true, subtree: true });
    }
  }

  // Public API
  window.MboaLiftI18n = {
    applyLanguage: applyLanguage,
    t: function (text) {
      return translatePhrase(text, currentLang);
    },
    getCurrentLanguage: function () {
      return currentLang;
    },
    translations: translations
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
