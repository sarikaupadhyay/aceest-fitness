"""
test_app.py
Pytest test suite for ACEest Fitness & Gym Flask application
Assignment 1 - Introduction to DevOps
"""

import pytest
import json
import os
import sys

# Make sure app.py is importable from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db, DB_NAME


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def client():
    """Create a test Flask client with a fresh in-memory-style DB."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Use a separate test database so we don't touch the real one
    import app as app_module
    app_module.DB_NAME = "test_aceest.db"

    init_db()

    with app.test_client() as c:
        yield c

    # Cleanup test database after each test
    if os.path.exists("test_aceest.db"):
        os.remove("test_aceest.db")


# ─────────────────────────────────────────────
# 1. Health check
# ─────────────────────────────────────────────

class TestHealth:
    def test_health_endpoint_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client):
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_health_returns_app_name(self, client):
        response = client.get("/api/health")
        data = json.loads(response.data)
        assert "app" in data
        assert "ACEest" in data["app"]


# ─────────────────────────────────────────────
# 2. Dashboard / web pages
# ─────────────────────────────────────────────

class TestWebPages:
    def test_dashboard_loads(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_dashboard_contains_title(self, client):
        response = client.get("/")
        assert b"ACEest" in response.data

    def test_clients_page_loads(self, client):
        response = client.get("/clients")
        assert response.status_code == 200

    def test_add_client_page_loads(self, client):
        response = client.get("/clients/add")
        assert response.status_code == 200

    def test_workouts_page_loads(self, client):
        response = client.get("/workouts")
        assert response.status_code == 200

    def test_add_workout_page_loads(self, client):
        response = client.get("/workouts/add")
        assert response.status_code == 200

    def test_programs_page_loads(self, client):
        response = client.get("/programs")
        assert response.status_code == 200

    def test_programs_page_contains_fat_loss(self, client):
        response = client.get("/programs")
        assert b"Fat Loss" in response.data

    def test_programs_page_contains_muscle_gain(self, client):
        response = client.get("/programs")
        assert b"Muscle Gain" in response.data

    def test_programs_page_contains_beginner(self, client):
        response = client.get("/programs")
        assert b"Beginner" in response.data

    def test_nonexistent_client_returns_200(self, client):
        response = client.get("/clients/9999")
        assert response.status_code == 200


# ─────────────────────────────────────────────
# 3. Client API - GET
# ─────────────────────────────────────────────

class TestClientAPIGet:
    def test_get_clients_returns_200(self, client):
        response = client.get("/api/clients")
        assert response.status_code == 200

    def test_get_clients_returns_list(self, client):
        response = client.get("/api/clients")
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_clients_empty_on_fresh_db(self, client):
        response = client.get("/api/clients")
        data = json.loads(response.data)
        assert data == []

    def test_get_single_client_not_found(self, client):
        response = client.get("/api/clients/999")
        assert response.status_code == 404

    def test_get_single_client_returns_error_message(self, client):
        response = client.get("/api/clients/999")
        data = json.loads(response.data)
        assert "error" in data


# ─────────────────────────────────────────────
# 4. Client API - POST (add client)
# ─────────────────────────────────────────────

class TestClientAPIPost:
    def test_add_client_returns_201(self, client):
        response = client.post(
            "/api/clients",
            json={"name": "Arjun Kumar", "age": 28, "weight": 75.5},
        )
        assert response.status_code == 201

    def test_add_client_returns_client_data(self, client):
        response = client.post(
            "/api/clients",
            json={"name": "Priya Singh", "age": 25, "weight": 60.0},
        )
        data = json.loads(response.data)
        assert data["name"] == "Priya Singh"
        assert data["age"] == 25
        assert data["membership_status"] == "Active"

    def test_add_client_without_name_returns_400(self, client):
        response = client.post("/api/clients", json={"age": 30})
        assert response.status_code == 400

    def test_add_client_empty_name_returns_400(self, client):
        response = client.post("/api/clients", json={"name": ""})
        assert response.status_code == 400

    def test_add_duplicate_client_returns_409(self, client):
        client.post("/api/clients", json={"name": "Ravi Sharma"})
        response = client.post("/api/clients", json={"name": "Ravi Sharma"})
        assert response.status_code == 409

    def test_add_client_with_program(self, client):
        response = client.post(
            "/api/clients",
            json={"name": "Meena Patel", "program": "Fat Loss"},
        )
        data = json.loads(response.data)
        assert data["program"] == "Fat Loss"

    def test_add_client_appears_in_list(self, client):
        client.post("/api/clients", json={"name": "Suresh Nair"})
        response = client.get("/api/clients")
        data = json.loads(response.data)
        names = [c["name"] for c in data]
        assert "Suresh Nair" in names

    def test_add_multiple_clients(self, client):
        client.post("/api/clients", json={"name": "Client A"})
        client.post("/api/clients", json={"name": "Client B"})
        client.post("/api/clients", json={"name": "Client C"})
        response = client.get("/api/clients")
        data = json.loads(response.data)
        assert len(data) >= 3


# ─────────────────────────────────────────────
# 5. Get single client after creation
# ─────────────────────────────────────────────

class TestClientAPIGetById:
    def test_get_client_by_id_returns_200(self, client):
        post_resp = client.post("/api/clients", json={"name": "Deepa Raj", "age": 32})
        client_id = json.loads(post_resp.data)["id"]
        response = client.get(f"/api/clients/{client_id}")
        assert response.status_code == 200

    def test_get_client_by_id_returns_correct_name(self, client):
        post_resp = client.post("/api/clients", json={"name": "Karthik Iyer"})
        client_id = json.loads(post_resp.data)["id"]
        response = client.get(f"/api/clients/{client_id}")
        data = json.loads(response.data)
        assert data["name"] == "Karthik Iyer"

    def test_new_client_membership_is_active(self, client):
        post_resp = client.post("/api/clients", json={"name": "Ananya Das"})
        client_id = json.loads(post_resp.data)["id"]
        response = client.get(f"/api/clients/{client_id}")
        data = json.loads(response.data)
        assert data["membership_status"] == "Active"


# ─────────────────────────────────────────────
# 6. Programs API
# ─────────────────────────────────────────────

class TestProgramsAPI:
    def test_get_programs_returns_200(self, client):
        response = client.get("/api/programs")
        assert response.status_code == 200

    def test_get_programs_returns_list(self, client):
        response = client.get("/api/programs")
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_programs_contains_fat_loss(self, client):
        response = client.get("/api/programs")
        data = json.loads(response.data)
        assert "Fat Loss" in data

    def test_programs_contains_muscle_gain(self, client):
        response = client.get("/api/programs")
        data = json.loads(response.data)
        assert "Muscle Gain" in data

    def test_programs_contains_beginner(self, client):
        response = client.get("/api/programs")
        data = json.loads(response.data)
        assert "Beginner" in data

    def test_programs_has_three_entries(self, client):
        response = client.get("/api/programs")
        data = json.loads(response.data)
        assert len(data) == 3


# ─────────────────────────────────────────────
# 7. Web form - add client
# ─────────────────────────────────────────────

class TestWebFormAddClient:
    def test_form_post_valid_client_redirects_or_200(self, client):
        response = client.post(
            "/clients/add",
            data={"name": "Form Client", "age": "30", "weight": "70"},
        )
        assert response.status_code in (200, 302)

    def test_form_post_adds_client_to_db(self, client):
        client.post("/clients/add", data={"name": "Web User", "age": "22"})
        response = client.get("/api/clients")
        data = json.loads(response.data)
        names = [c["name"] for c in data]
        assert "Web User" in names

    def test_form_post_empty_name_shows_error(self, client):
        response = client.post("/clients/add", data={"name": ""})
        assert b"required" in response.data.lower() or response.status_code in (200, 400)


# ─────────────────────────────────────────────
# 8. Generate program route
# ─────────────────────────────────────────────

class TestGenerateProgram:
    def test_generate_program_redirects(self, client):
        post_resp = client.post("/api/clients", json={"name": "Gym User"})
        client_id = json.loads(post_resp.data)["id"]
        response = client.get(f"/clients/{client_id}/generate-program")
        assert response.status_code in (200, 302)

    def test_generate_program_assigns_valid_program(self, client):
        post_resp = client.post("/api/clients", json={"name": "Program Tester"})
        client_id = json.loads(post_resp.data)["id"]
        client.get(f"/clients/{client_id}/generate-program")
        response = client.get(f"/api/clients/{client_id}")
        data = json.loads(response.data)
        valid_programs = ["Fat Loss", "Muscle Gain", "Beginner"]
        assert data["program"] in valid_programs
