import pytest
import copy
from fastapi.testclient import TestClient
from src.app import app, activities

# Test data - a subset of activities for faster testing
TEST_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["test1@school.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["test2@school.edu", "test3@school.edu"]
    }
}


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to test data before each test"""
    # Clear and reset the global activities dict with a deep copy
    activities.clear()
    activities.update(copy.deepcopy(TEST_ACTIVITIES))
    yield
    # Cleanup after test if needed
    activities.clear()
    activities.update(copy.deepcopy(TEST_ACTIVITIES))