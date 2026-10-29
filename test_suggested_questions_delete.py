import unittest
from fastapi.testclient import TestClient
from main import app, get_db, create_token

class TestSuggestedQuestionsDelete(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.user1_id = 99991
        self.user2_id = 99992

        with get_db() as conn:
            # Clean up first
            conn.execute("DELETE FROM chat_sessions WHERE user_id IN (?, ?)", (self.user1_id, self.user2_id))
            conn.execute("DELETE FROM users WHERE id IN (?, ?)", (self.user1_id, self.user2_id))

            # Insert test users
            conn.execute(
                "INSERT INTO users (id, email, password_hash, full_name, role, is_active, token_version) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user1_id, "user1@test.com", "hash1", "User 1", "user", 1, 1)
            )
            conn.execute(
                "INSERT INTO users (id, email, password_hash, full_name, role, is_active, token_version) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.user2_id, "user2@test.com", "hash2", "User 2", "user", 1, 1)
            )

            # Insert chat_sessions
            conn.execute(
                "INSERT INTO chat_sessions (user_id, prompt_question, ai_response) VALUES (?, ?, ?)",
                (self.user1_id, "cau hoi nhay cam 1", "phan hoi 1")
            )
            conn.execute(
                "INSERT INTO chat_sessions (user_id, prompt_question, ai_response) VALUES (?, ?, ?)",
                (self.user1_id, "cau hoi nhay cam 2", "phan hoi 2")
            )
            conn.execute(
                "INSERT INTO chat_sessions (user_id, prompt_question, ai_response) VALUES (?, ?, ?)",
                (self.user1_id, "thang sau chi tieu the nao", "phan hoi 3")
            )
            conn.execute(
                "INSERT INTO chat_sessions (user_id, prompt_question, ai_response) VALUES (?, ?, ?)",
                (self.user2_id, "cau hoi user 2", "phan hoi user 2")
            )

        self.token1 = create_token(user_id=self.user1_id, email="user1@test.com", role="user", token_version=1)
        self.token2 = create_token(user_id=self.user2_id, email="user2@test.com", role="user", token_version=1)
        self.headers1 = {"Authorization": f"Bearer {self.token1}"}
        self.headers2 = {"Authorization": f"Bearer {self.token2}"}

    def tearDown(self):
        with get_db() as conn:
            conn.execute("DELETE FROM chat_sessions WHERE user_id IN (?, ?)", (self.user1_id, self.user2_id))
            conn.execute("DELETE FROM users WHERE id IN (?, ?)", (self.user1_id, self.user2_id))

    def test_get_suggested_questions(self):
        res = self.client.get("/api/chat/suggested-questions", headers=self.headers1)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("cau hoi nhay cam 1", data)
        self.assertIn("cau hoi nhay cam 2", data)
        self.assertIn("thang sau chi tieu the nao", data)
        self.assertEqual(len(data), 3)

    def test_delete_single_suggested_question(self):
        res = self.client.delete(
            "/api/chat/suggested-questions",
            params={"question": "cau hoi nhay cam 1"},
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)

        # Check user 1's suggestions
        res = self.client.get("/api/chat/suggested-questions", headers=self.headers1)
        data = res.json()
        self.assertNotIn("cau hoi nhay cam 1", data)
        self.assertIn("cau hoi nhay cam 2", data)
        self.assertIn("thang sau chi tieu the nao", data)

        # Ensure user 2 was unaffected
        res2 = self.client.get("/api/chat/suggested-questions", headers=self.headers2)
        self.assertIn("cau hoi user 2", res2.json())

    def test_delete_all_suggested_questions(self):
        res = self.client.delete(
            "/api/chat/suggested-questions",
            headers=self.headers1
        )
        self.assertEqual(res.status_code, 200)

        # Check user 1's suggestions is empty
        res = self.client.get("/api/chat/suggested-questions", headers=self.headers1)
        data = res.json()
        self.assertEqual(len(data), 0)

        # Ensure user 2 was unaffected
        res2 = self.client.get("/api/chat/suggested-questions", headers=self.headers2)
        self.assertIn("cau hoi user 2", res2.json())

if __name__ == "__main__":
    unittest.main()
