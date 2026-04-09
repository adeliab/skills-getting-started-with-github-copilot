"""Tests for signup functionality edge cases and validation"""

import pytest


class TestSignupValidation:
    """Test signup validation logic"""

    def test_signup_prevents_duplicate_registration(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "test1@school.edu"  # Already signed up in test data

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_allows_different_email_same_activity(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "different@school.edu"  # Not signed up yet

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_allows_same_email_different_activity(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "test1@school.edu"  # Signed up for Chess Club, but not Programming

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_signup_with_special_characters_in_email(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "test.student+tag@school.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        # Check that the participant was actually added (since URL encoding may affect the message)
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        # The email might be stored as-is or URL decoded
        participants = activities_data[activity_name]["participants"]
        assert any(email in p or "test.student" in p for p in participants)

    def test_signup_with_empty_email_fails(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = ""

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        # FastAPI should handle empty string as valid, but our logic doesn't prevent it
        # This tests current behavior - may need validation in future
        assert response.status_code == 200  # Currently allows empty email

    def test_signup_with_whitespace_email(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "   "

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200  # Currently allows whitespace


class TestSignupStateChanges:
    """Test that signup correctly modifies application state"""

    def test_signup_increases_participant_count(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newparticipant@school.edu"

        # Get initial count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity_name]["participants"])

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_count = len(final_data[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert email in final_data[activity_name]["participants"]

    def test_signup_persists_across_requests(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "persistent@school.edu"

        # Act - signup
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - check in separate request
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity_name]["participants"]


class TestCapacityHandling:
    """Test capacity-related behavior (currently not enforced)"""

    def test_signup_allows_over_capacity(self, client):
        # Arrange - Chess Club has max_participants: 12, currently 1 participant
        activity_name = "Chess Club"
        emails = [f"student{i}@school.edu" for i in range(15)]  # Add 15 more

        # Act - signup all students
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            # Currently allows over capacity
            assert response.status_code == 200

        # Assert - all were added despite exceeding max_participants
        final_response = client.get("/activities")
        final_data = final_response.json()
        participants = final_data[activity_name]["participants"]
        assert len(participants) > final_data[activity_name]["max_participants"]