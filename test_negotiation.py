"""
test_negotiation.py
-------------------
Automated verification tests for Douala Street Fare Negotiation ("Marchandage à la Doualaise").
"""

import unittest
from datetime import datetime
from app import app, get_db, init_db_schema

class TestStreetFareNegotiation(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        init_db_schema()

        # Create test passenger and driver in db
        conn = get_db()
        self.assertIsNotNone(conn, "Database connection failed")
        cur = conn.cursor(dictionary=True)

        # Test Rider
        cur.execute("SELECT id FROM users WHERE email = 'test_rider_neg@mboalift.cm'")
        user = cur.fetchone()
        if not user:
            cur.execute(
                """INSERT INTO users (full_name, phone, email, password_hash, status)
                   VALUES ('Rider Testeur Douala', '+237690000099', 'test_rider_neg@mboalift.cm', 'hashed', 'active')"""
            )
            self.user_id = cur.lastrowid
        else:
            self.user_id = user["id"]

        # Test Driver
        cur.execute("SELECT id FROM drivers WHERE email = 'test_driver_neg@mboalift.cm'")
        driver = cur.fetchone()
        if not driver:
            cur.execute(
                """INSERT INTO drivers (full_name, phone, email, password_hash, vehicle_info, vehicle_type, current_location, availability, status)
                   VALUES ('Chauffeur Bendskin Test', '+237670000088', 'test_driver_neg@mboalift.cm', 'hashed', 'Yamaha Crux LT-990-LT', 'bendskin', 'Akwa', 'free', 'active')"""
            )
            self.driver_id = cur.lastrowid
        else:
            self.driver_id = driver["id"]

        conn.commit()
        cur.close()
        conn.close()

    def test_01_create_ride_with_negotiated_offer(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = self.user_id
            sess["user_name"] = "Rider Testeur Douala"

        # Base fare from Akwa to Ndokoti for taxi is 1200
        # Rider proposes counter-offer of 1000 XAF
        response = self.client.post("/request-ride", data={
            "pickup": "Akwa",
            "destination": "Ndokoti",
            "vehicle_type": "taxi",
            "passengers": "1",
            "negotiated_fare": "1000",
            "preferred_driver": ""
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

        # Verify ride in database
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT id, fare, original_fare, negotiation_status, status
               FROM rides WHERE user_id = %s ORDER BY created_at DESC LIMIT 1""",
            (self.user_id,)
        )
        ride = cur.fetchone()
        cur.close()
        conn.close()

        self.assertIsNotNone(ride)
        self.assertEqual(float(ride["fare"]), 1000.0)
        self.assertEqual(float(ride["original_fare"]), 1200.0)
        self.assertEqual(ride["negotiation_status"], "PROPOSED")
        self.assertEqual(ride["status"], "PENDING")

        ride_id = ride["id"]

        # Test driver alerts API returns negotiated offer flag and amounts
        alert_res = self.client.get("/api/driver/alerts")
        self.assertEqual(alert_res.status_code, 200)
        alert_data = alert_res.get_json()
        self.assertTrue(alert_data["success"])
        matching = [r for r in alert_data["rides"] if r["id"] == ride_id]
        self.assertTrue(len(matching) > 0)
        m_ride = matching[0]
        self.assertEqual(m_ride["fare"], 1000)
        self.assertEqual(m_ride["original_fare"], 1200)
        self.assertTrue(m_ride["is_negotiated"])
        self.assertEqual(m_ride["negotiation_status"], "PROPOSED")

        # Test passenger updates their offer via API
        neg_res = self.client.post(f"/api/ride/{ride_id}/negotiate", json={
            "fare": 1100
        })
        self.assertEqual(neg_res.status_code, 200)
        neg_data = neg_res.get_json()
        self.assertTrue(neg_data["success"])
        self.assertEqual(float(neg_data["fare"]), 1100.0)

        # Test driver submits counter-offer (e.g. 1150 XAF)
        with self.client.session_transaction() as sess:
            sess.clear()
            sess["driver_id"] = self.driver_id
            sess["driver_name"] = "Chauffeur Bendskin Test"

        counter_res = self.client.post(f"/driver/ride/{ride_id}/counter", json={
            "counter_fare": 1150
        })
        self.assertEqual(counter_res.status_code, 200)
        counter_data = counter_res.get_json()
        self.assertTrue(counter_data["success"])
        self.assertEqual(float(counter_data["counter_fare"]), 1150.0)

        # Check ride status API for passenger shows counter-offer
        with self.client.session_transaction() as sess:
            sess.clear()
            sess["user_id"] = self.user_id

        status_res = self.client.get(f"/api/ride-status/{ride_id}")
        self.assertEqual(status_res.status_code, 200)
        status_data = status_res.get_json()
        self.assertEqual(status_data["negotiation_status"], "COUNTERED")
        self.assertEqual(float(status_data["driver_counter_fare"]), 1150.0)

        # Passenger accepts driver's counter offer
        accept_res = self.client.post(f"/api/ride/{ride_id}/accept-counter")
        self.assertEqual(accept_res.status_code, 200)
        accept_data = accept_res.get_json()
        self.assertTrue(accept_data["success"])
        self.assertEqual(float(accept_data["fare"]), 1150.0)

        # Verify ride is now ACCEPTED at 1150 XAF
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT fare, status, negotiation_status, driver_id FROM rides WHERE id = %s", (ride_id,))
        final_ride = cur.fetchone()
        cur.close()
        conn.close()

        self.assertEqual(final_ride["status"], "ACCEPTED")
        self.assertEqual(final_ride["negotiation_status"], "ACCEPTED")
        self.assertEqual(float(final_ride["fare"]), 1150.0)
        self.assertEqual(final_ride["driver_id"], self.driver_id)
        print("\nAll Street Fare Negotiation backend tests PASSED successfully!")


if __name__ == "__main__":
    unittest.main()
