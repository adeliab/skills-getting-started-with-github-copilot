"""Tests for participant removal functionality and state verification"""

import pytest


class TestRemoveParticipantValidation:
    """Test participant removal validation"""

    def test_remove_participant_successful(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "test2@school.edu"  # Exists in test data

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
        activity_name = "Fake Activity"
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
        email = "missing@school.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]


class TestRemoveParticipantStateChanges:
    """Test that participant removal correctly modifies application state"""

    def test_remove_participant_decreases_count(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "test2@school.edu"

        # Get initial count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity_name]["participants"])

        # Act
        client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        final_response = client.get("/activities")
        final_data = final_response.json()
        final_count = len(final_data[activity_name]["participants"])
        assert final_count == initial_count - 1
        assert email not in final_data[activity_name]["participants"]

    def test_remove_participant_persists_across_requests(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "test3@school.edu"

        # Act - remove participant
        client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert - check in separate request
        response = client.get("/activities")
        data = response.json()
        assert email not in data[activity_name]["participants"]

    def test_remove_participant_allows_resignup(self, client):
        # Arrange
        activity_name = "Programming Class"
        email = "test2@school.edu"

        # Act - remove then re-signup
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - re-signup should succeed
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]


class TestParticipantEdgeCases:
    """Test edge cases for participant management"""

    def test_remove_participant_case_sensitive_email(self, client):
        # Arrange
        activity_name = "Chess Club"
        original_email = "test1@school.edu"
        wrong_case_email = "Test1@School.Edu"

        # Act - try to remove with different case
        response = client.delete(f"/activities/{activity_name}/participants/{wrong_case_email}")

        # Assert - should fail because email matching is case-sensitive
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_remove_last_participant(self, client):
        # Arrange - add a participant to an activity with only one, then remove
        activity_name = "Chess Club"
        email = "only@school.edu"

        # First signup
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act - remove the participant
        response = client.delete(f"/activities/{activity_name}/participants/{email}")

        # Assert
        assert response.status_code == 200
        # Verify participant was removed
        final_response = client.get("/activities")
        final_data = final_response.json()
        assert email not in final_data[activity_name]["participants"]

    def test_remove_participant_from_empty_activity_fails(self, client):
        # Arrange - create activity with no participants (modify test data)
        from src.app import activities
        activities["Empty Activity"] = {
            "description": "Test activity",
            "schedule": "Never",
            "max_participants": 10,
            "participants": []
        }

        # Act
        response = client.delete("/activities/Empty%20Activity/participants/fake@school.edu")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]