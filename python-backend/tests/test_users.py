"""Tests for user endpoints"""

import pytest


class TestUsers:
    """User endpoint tests"""
    
    def test_create_user(self, client, auth_headers):
        """Test creating a new user"""
        response = client.post("/api/users", json={
            "name": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "newuser"
        assert data["email"] == "new@example.com"
    
    def test_get_user(self, client, test_user, auth_headers):
        """Test getting a user by ID"""
        response = client.get(f"/api/users/{test_user.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "testuser"
    
    def test_get_user_not_found(self, client, auth_headers):
        """Test getting a nonexistent user"""
        response = client.get("/api/users/99999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_list_users(self, client, test_user, auth_headers):
        """Test listing users"""
        response = client.get("/api/users", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_update_user(self, client, test_user, auth_headers):
        """Test updating a user"""
        response = client.put(f"/api/users/{test_user.id}", json={
            "email": "updated@example.com"
        }, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
    
    def test_delete_user(self, client, auth_headers, db):
        """Test deleting a user"""
        from app.models import User
        from app.utils.auth import hash_password
        
        # Create a user to delete
        user = User(name="todelete", email="delete@example.com", password=hash_password("pass"))
        db.add(user)
        db.commit()
        db.refresh(user)
        
        response = client.delete(f"/api/users/{user.id}", headers=auth_headers)
        
        assert response.status_code == 204
