#!/usr/bin/env python3
"""
API Tests

Tests for the FastAPI backend.
"""

import os
import sys
import pytest

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient


def test_api_imports():
    """Test that API modules can be imported."""
    print("\n=== Test 1: API Imports ===")

    try:
        from api.main import app
        from api.config import settings
        from api.schemas import CreateSessionRequest, SessionResponse
        from api.services import get_workflow_service, get_video_service
        from api.routers import sessions, videos
        from api.websocket import handler

        print("✓ All API modules imported successfully")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False


def test_health_endpoint():
    """Test the health check endpoint."""
    print("\n=== Test 2: Health Endpoint ===")

    try:
        from api.main import app

        client = TestClient(app)
        response = client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data

        print(f"✓ Health check passed: {data}")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Health check error: {e}")
        traceback.print_exc()
        return False


def test_config_endpoint():
    """Test the config endpoint."""
    print("\n=== Test 3: Config Endpoint ===")

    try:
        from api.main import app

        client = TestClient(app)
        response = client.get("/api/config")

        assert response.status_code == 200
        data = response.json()
        assert "available_platforms" in data
        assert "available_genres" in data
        assert "kling" in data["available_platforms"]
        assert "drama" in data["available_genres"]

        print(f"✓ Config endpoint passed")
        print(f"  Platforms: {data['available_platforms']}")
        print(f"  Genres: {data['available_genres'][:5]}...")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Config endpoint error: {e}")
        traceback.print_exc()
        return False


def test_sessions_list():
    """Test listing sessions."""
    print("\n=== Test 4: Sessions List ===")

    try:
        from api.main import app

        client = TestClient(app)
        response = client.get("/api/sessions")

        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert isinstance(data["sessions"], list)

        print(f"✓ Sessions list passed: {data['total']} sessions")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Sessions list error: {e}")
        traceback.print_exc()
        return False


def test_session_not_found():
    """Test 404 for non-existent session."""
    print("\n=== Test 5: Session Not Found ===")

    try:
        from api.main import app

        client = TestClient(app)
        response = client.get("/api/sessions/non-existent-id")

        assert response.status_code == 404

        print("✓ Session not found returns 404")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Session not found error: {e}")
        traceback.print_exc()
        return False


def test_create_session_validation():
    """Test session creation validation."""
    print("\n=== Test 6: Session Creation Validation ===")

    try:
        from api.main import app

        client = TestClient(app)

        # Test missing required field
        response = client.post("/api/sessions", json={})
        assert response.status_code == 422  # Validation error

        # Test invalid values
        response = client.post("/api/sessions", json={
            "idea": "test",
            "num_episodes": 100,  # Too many
        })
        assert response.status_code == 422

        print("✓ Session creation validation works")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Validation error: {e}")
        traceback.print_exc()
        return False


def test_schemas():
    """Test Pydantic schemas."""
    print("\n=== Test 7: Pydantic Schemas ===")

    try:
        from api.schemas import (
            CreateSessionRequest,
            SessionResponse,
            SessionDetailResponse,
            VideoTaskResponse,
        )

        # Test CreateSessionRequest
        req = CreateSessionRequest(idea="Test story")
        assert req.idea == "Test story"
        assert req.genre == "drama"
        assert req.num_episodes == 1

        # Test with custom values
        req2 = CreateSessionRequest(
            idea="Sci-fi adventure",
            genre="sci-fi",
            num_episodes=3,
            num_characters=5,
        )
        assert req2.genre == "sci-fi"
        assert req2.num_episodes == 3

        print("✓ Pydantic schemas work correctly")
        return True

    except Exception as e:
        import traceback
        print(f"✗ Schema error: {e}")
        traceback.print_exc()
        return False


def test_websocket_manager():
    """Test WebSocket connection manager."""
    print("\n=== Test 8: WebSocket Manager ===")

    try:
        from api.websocket.handler import ConnectionManager

        manager = ConnectionManager()

        # Test basic structure
        assert hasattr(manager, 'subscriptions')
        assert hasattr(manager, 'connections')
        assert hasattr(manager, 'subscribe')
        assert hasattr(manager, 'unsubscribe')
        assert hasattr(manager, 'broadcast')

        print("✓ WebSocket manager structure correct")
        return True

    except Exception as e:
        import traceback
        print(f"✗ WebSocket manager error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("API Test Suite")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("API Imports", test_api_imports()))
    results.append(("Health Endpoint", test_health_endpoint()))
    results.append(("Config Endpoint", test_config_endpoint()))
    results.append(("Sessions List", test_sessions_list()))
    results.append(("Session Not Found", test_session_not_found()))
    results.append(("Session Validation", test_create_session_validation()))
    results.append(("Pydantic Schemas", test_schemas()))
    results.append(("WebSocket Manager", test_websocket_manager()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = 0
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    return passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
