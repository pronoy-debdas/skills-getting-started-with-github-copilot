import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_structure():
    """Test that activities have the correct structure"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/activities")
    data = response.json()
    
    # Assert
    for activity_name, activity in data.items():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
        assert isinstance(activity["max_participants"], int)


def test_signup_success():
    """Test successful signup"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_activity_not_found():
    """Test signup with non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "Nonexistent"
    
    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_email():
    """Test signup with already registered email"""
    # Arrange
    email = "michael@mergington.edu"  # Already in Chess Club
    activity_name = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_activity_full():
    """Test signup when activity is at capacity"""
    # Arrange
    activity_name = "Programming Class"
    
    # Get current state
    response = client.get("/activities")
    activities = response.json()
    current_count = len(activities[activity_name]["participants"])
    max_count = activities[activity_name]["max_participants"]
    
    # Fill to capacity
    for i in range(max_count - current_count):
        email = f"fill{i}@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act - Try to add one more
    response = client.post(f"/activities/{activity_name}/signup?email=overflow@mergington.edu")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "full" in data["detail"]


def test_delete_participant():
    """Test successful participant deletion"""
    # Arrange
    email = "todelete@mergington.edu"
    activity_name = "Chess Club"
    
    # Add the participant first
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_delete_not_signed_up():
    """Test deleting a non-participant"""
    # Arrange
    email = "notsigned@mergington.edu"
    activity_name = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_delete_activity_not_found():
    """Test deleting from non-existent activity"""
    # Arrange
    email = "test@mergington.edu"
    invalid_activity = "Nonexistent"
    
    # Act
    response = client.delete(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test root endpoint redirects to static content"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/")
    
    # Assert
    assert response.status_code == 200
    # TestClient follows redirects by default
