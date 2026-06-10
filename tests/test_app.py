from fastapi.testclient import TestClient
import importlib


def reset_app():
    """Arrange: reload the app module to ensure a fresh in-memory state."""
    import src.app as app_module
    importlib.reload(app_module)
    return app_module.app, app_module.activities


def test_root_redirect():
    # Arrange
    app, activities = reset_app()
    client = TestClient(app)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities():
    # Arrange
    app, activities = reset_app()
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success_and_duplicate():
    # Arrange
    app, activities = reset_app()
    client = TestClient(app)
    activity = "Art Club"
    email = "testuser@example.com"
    assert email not in activities[activity]["participants"]

    # Act (successful signup)
    resp1 = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert (successful)
    assert resp1.status_code == 200
    assert email in activities[activity]["participants"]
    assert resp1.json()["message"] == f"Signed up {email} for {activity}"

    # Act (duplicate signup)
    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert (duplicate error)
    assert resp2.status_code == 400
    assert "already signed up" in resp2.json().get("detail", "").lower()


def test_unregister_success_and_not_registered():
    # Arrange
    app, activities = reset_app()
    client = TestClient(app)
    activity = "Programming Class"
    email = "tempuser@example.com"

    # Ensure the user is registered first
    activities[activity]["participants"].append(email)
    assert email in activities[activity]["participants"]

    # Act (successful unregister)
    resp1 = client.post(f"/activities/{activity}/unregister", params={"email": email})

    # Assert (successful)
    assert resp1.status_code == 200
    assert email not in activities[activity]["participants"]
    assert resp1.json()["message"] == f"Unregistered {email} from {activity}"

    # Act (unregister not registered)
    resp2 = client.post(f"/activities/{activity}/unregister", params={"email": email})

    # Assert (not-registered error)
    assert resp2.status_code == 400
    assert "not registered" in resp2.json().get("detail", "").lower()


def test_missing_activity_returns_404():
    # Arrange
    app, activities = reset_app()
    client = TestClient(app)
    missing = "Nonexistent Club"
    email = "x@y.com"

    # Act (signup missing)
    resp_signup = client.post(f"/activities/{missing}/signup", params={"email": email})
    # Act (unregister missing)
    resp_unreg = client.post(f"/activities/{missing}/unregister", params={"email": email})

    # Assert
    assert resp_signup.status_code == 404
    assert resp_unreg.status_code == 404
