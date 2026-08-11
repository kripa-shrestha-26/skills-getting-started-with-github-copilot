"""
Test suite for the Mergington High School Activity Management System API

Uses the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested
- Assert: Verify the results
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """
        GIVEN: The API is running
        WHEN: A GET request is made to /activities
        THEN: All activities should be returned with correct structure
        """
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Basketball Team", "Tennis Club", "Art Studio", 
            "Drama Club", "Science Lab", "Debate Team"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        for activity_name in expected_activities:
            assert activity_name in activities
            assert "description" in activities[activity_name]
            assert "schedule" in activities[activity_name]
            assert "max_participants" in activities[activity_name]
            assert "participants" in activities[activity_name]

    def test_get_activities_includes_participants(self, client):
        """
        GIVEN: Activities with registered participants
        WHEN: A GET request is made to /activities
        THEN: Participants list should be included for each activity
        """
        # Arrange
        # (Activities already have participants from conftest)

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        chess_club = activities["Chess Club"]
        assert isinstance(chess_club["participants"], list)
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """
        GIVEN: A new student email and an available activity
        WHEN: A POST request is made to the signup endpoint
        THEN: The student should be added to participants
        """
        # Arrange
        activity_name = "Chess Club"
        new_student = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {new_student} for {activity_name}"
        
        # Verify participant was added
        verify_response = client.get("/activities")
        assert new_student in verify_response.json()[activity_name]["participants"]

    def test_signup_duplicate_registration_prevented(self, client):
        """
        GIVEN: A student already registered for an activity
        WHEN: The same student tries to sign up again
        THEN: The signup should be rejected with a 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """
        GIVEN: A non-existent activity name
        WHEN: A POST request is made to the signup endpoint
        THEN: A 404 error should be returned
        """
        # Arrange
        nonexistent_activity = "Underwater Basket Weaving"
        student = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": student}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_updates_participant_count(self, client):
        """
        GIVEN: An activity with current participants
        WHEN: A new student signs up
        THEN: The participant count should increase
        """
        # Arrange
        activity_name = "Basketball Team"
        new_student = "newbasketball@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )

        # Assert
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """
        GIVEN: A registered student in an activity
        WHEN: A POST request is made to the unregister endpoint
        THEN: The student should be removed from participants
        """
        # Arrange
        activity_name = "Chess Club"
        student_to_remove = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student_to_remove}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {student_to_remove} from {activity_name}"
        
        # Verify participant was removed
        verify_response = client.get("/activities")
        assert student_to_remove not in verify_response.json()[activity_name]["participants"]

    def test_unregister_not_registered_student(self, client):
        """
        GIVEN: A student not registered for an activity
        WHEN: A POST request is made to unregister them
        THEN: A 400 error should be returned
        """
        # Arrange
        activity_name = "Chess Club"
        unregistered_student = "notregistered@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": unregistered_student}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """
        GIVEN: A non-existent activity name
        WHEN: A POST request is made to the unregister endpoint
        THEN: A 404 error should be returned
        """
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        student = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": student}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_updates_participant_count(self, client):
        """
        GIVEN: An activity with multiple participants
        WHEN: A student unregisters
        THEN: The participant count should decrease
        """
        # Arrange
        activity_name = "Chess Club"
        student = "daniel@mergington.edu"
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])

        # Act
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student}
        )

        # Assert
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])
        assert final_count == initial_count - 1


class TestIntegrationScenarios:
    """End-to-end tests combining multiple operations"""

    def test_signup_then_unregister_workflow(self, client):
        """
        GIVEN: A student and an activity
        WHEN: The student signs up and then unregisters
        THEN: The participant list should reflect both changes
        """
        # Arrange
        activity_name = "Tennis Club"
        student = "integration@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": student}
        )

        # Assert signup
        assert signup_response.status_code == 200
        verify1 = client.get("/activities")
        assert student in verify1.json()[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": student}
        )

        # Assert unregister
        assert unregister_response.status_code == 200
        verify2 = client.get("/activities")
        assert student not in verify2.json()[activity_name]["participants"]

    def test_multiple_students_signup_same_activity(self, client):
        """
        GIVEN: Multiple unique students
        WHEN: They all sign up for the same activity
        THEN: All should appear in the participant list
        """
        # Arrange
        activity_name = "Art Studio"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]

        # Act
        for student in students:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": student}
            )

        # Assert
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for student in students:
            assert student in participants

    def test_cannot_signup_twice_even_after_state_changes(self, client):
        """
        GIVEN: A student who just signed up
        WHEN: They immediately try to sign up again
        THEN: The duplicate signup should be rejected
        """
        # Arrange
        activity_name = "Drama Club"
        new_student = "duplicate@mergington.edu"

        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )

        # Assert first signup succeeded
        assert response1.status_code == 200

        # Act - Attempt duplicate signup
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )

        # Assert second signup rejected
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
