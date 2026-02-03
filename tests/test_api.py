"""Tests for the FastAPI activities endpoints."""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert "Basketball" in data
        assert "Tennis Club" in data
        assert "Art Club" in data
        assert len(data) == 9

    def test_get_activities_contains_activity_details(self, client, reset_activities):
        """Test that activities contain all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Basketball"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_contains_participants(self, client, reset_activities):
        """Test that activities include participant list."""
        response = client.get("/activities")
        data = response.json()
        
        basketball = data["Basketball"]
        assert isinstance(basketball["participants"], list)
        assert "alex@mergington.edu" in basketball["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant."""
        email = "newstudent@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Basketball/signup?email={email}")
        
        # Verify
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signup fails if student already registered."""
        email = "alex@mergington.edu"
        response = client.post(f"/activities/Basketball/signup?email={email}")
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test that signup fails for nonexistent activity."""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities."""
        email = "newstudent@mergington.edu"
        
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        response2 = client.post(f"/activities/Tennis Club/signup?email={email}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]
        assert email in data["Tennis Club"]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregister from an activity."""
        email = "alex@mergington.edu"
        response = client.post(f"/activities/Basketball/unregister?email={email}")
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant."""
        email = "alex@mergington.edu"
        
        # Verify participant exists
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]
        
        # Unregister
        client.post(f"/activities/Basketball/unregister?email={email}")
        
        # Verify removal
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Basketball"]["participants"]

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test that unregister fails for nonexistent activity."""
        response = client.post(
            "/activities/NonexistentActivity/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_not_registered(self, client, reset_activities):
        """Test that unregister fails if student is not registered."""
        response = client.post(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_and_signup_again(self, client, reset_activities):
        """Test that student can sign up again after unregistering."""
        email = "alex@mergington.edu"
        
        # Unregister
        client.post(f"/activities/Basketball/unregister?email={email}")
        
        # Sign up again
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200
        
        # Verify
        response = client.get("/activities")
        data = response.json()
        assert email in data["Basketball"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
