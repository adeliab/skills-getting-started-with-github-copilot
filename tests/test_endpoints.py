"""Tests for all FastAPI endpoints using AAA pattern"""

import pytest


class TestRootEndpoint:
    """Test the root endpoint that redirects to static files"""

    def test_get_root_redirects_to_static_index(self, client):
        # Arrange - no special setup needed

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200
        # FastAPI redirects internally, but TestClient follows redirects by default
        # The response should be the HTML content from index.html
        assert "text/html" in response.headers.get("content-type", "")


class TestActivitiesEndpoint:
    """Test the activities listing endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange - activities are reset by fixture

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 2  # Our test data has 2 activities
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_includes_required_fields(self, client):
        # Arrange - activities are reset by fixture

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""

    def test_signup_successful_for_existing_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@school.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_fails_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@school.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]


class TestRemoveParticipantEndpoint:
    """Test the remove participant endpoint"""

    def test_remove_participant_successful(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "test2@school.edu"  # This email exists in test data

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_fails_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@school.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_remove_participant_fails_for_nonexistent_participant(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@school.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]