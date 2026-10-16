"""
test_voice_landmarks.py
-----------------------
Unit and integration tests for Feature #5:
Voice Search & Douala Landmark Recognition ("Recherche Vocale aux Repères")
"""

import unittest
from app import app, normalize_location, DOUALA_LANDMARKS, LOCATIONS


class VoiceLandmarksTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()

    def test_douala_landmarks_structure(self):
        """Verify each landmark in the database has all required keys and valid canonical area."""
        self.assertGreater(len(DOUALA_LANDMARKS), 15)
        for lm in DOUALA_LANDMARKS:
            self.assertIn("name", lm)
            self.assertIn("area", lm)
            self.assertIn("lat", lm)
            self.assertIn("lng", lm)
            self.assertIn("icon", lm)
            self.assertIn("tip", lm)
            self.assertIn(lm["area"], LOCATIONS, f"Landmark area '{lm['area']}' not in official LOCATIONS")

    def test_colloquial_speech_normalization(self):
        """Verify spoken phrases with Douala conversational prefixes normalize accurately."""
        test_cases = [
            ("Dépose-moi à Total Énergie Ndokoti", "Ndokoti"),
            ("je vais à Mobil Guinness", "Bépanda"),
            ("amène-moi vers Carrefour Deux Églises", "Bépanda"),
            ("Ancien Dalip Akwa", "Akwa"),
            ("Boulangerie Zepol", "Akwa"),
            ("Gare de Bessengue", "Deido"),
            ("Aéroport DLA", "Aéroport"),
            ("Marché Mboppi", "Bépanda"),
            ("Marché Central New Bell", "New Bell"),
            ("Marché Sandaga", "New Bell"),
            ("Pont du Wouri", "Bonabéri"),
            ("Carrefour Mutzig", "Bonabéri"),
            ("Quatre Étages Bonabéri", "Bonabéri"),
            ("Université ESSEC", "Makepe"),
            ("Hôpital Général", "Makepe"),
            ("Clinique Soppo Priso", "Bonapriso"),
            ("Complexe Sportif Japoma", "Japoma"),
            ("Carrefour Denver", "Bonamoussadi"),
            ("Rond-Point Maetur", "Bonamoussadi"),
            ("Cité des Palmiers", "Cité des Palmiers")
        ]
        for phrase, expected_area in test_cases:
            matched = normalize_location(phrase)
            self.assertEqual(matched, expected_area, f"Failed matching phrase: '{phrase}' -> got '{matched}', expected '{expected_area}'")

    def test_api_landmarks_search_query(self):
        """Test GET /api/landmarks/search with various queries."""
        # Query 1: Total Ndokoti
        res = self.client.get("/api/landmarks/search?q=Total%20Ndokoti")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["matched_area"], "Ndokoti")
        self.assertGreater(data["total"], 0)
        self.assertIn("Ndokoti", data["landmarks"][0]["name"])

        # Query 2: Deux Églises
        res2 = self.client.get("/api/landmarks/search?q=Deux%20Eglises")
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(data2["matched_area"], "Bépanda")

        # Query 3: Empty query returns full catalog
        res3 = self.client.get("/api/landmarks/search")
        self.assertEqual(res3.status_code, 200)
        data3 = res3.get_json()
        self.assertEqual(data3["total"], len(DOUALA_LANDMARKS))

    def test_request_ride_page_has_voice_and_landmarks(self):
        """Test request-ride page renders voice inputs, mic buttons, and slang chips."""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["user_name"] = "Douala Passenger"
            sess["role"] = "passenger"

        res = self.client.get("/request-ride")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("voiceBtnPickup", html)
        self.assertIn("voiceBtnDestination", html)
        self.assertIn("doualaSlangBar", html)
        self.assertIn("Total Énergie Ndokoti", html)
        self.assertIn("Ancien Dalip (Akwa)", html)
        self.assertIn("Mobil Guinness (Bépanda)", html)
        self.assertIn("pickupLandmarkBadge", html)
        self.assertIn("destLandmarkBadge", html)


if __name__ == "__main__":
    unittest.main()
