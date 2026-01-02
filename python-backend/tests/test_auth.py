"""Tests for authentication endpoints"""

import pytest


class TestAuth:
    """Authentication endpoint tests"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post("/api/auth/register", json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["name"] == "newuser"
        assert data["user"]["email"] == "new@example.com"
    
    def test_register_duplicate_username(self, client, test_user):
        """Test registration with duplicate username"""
        response = client.post("/api/auth/register", json={
            "username": test_user.name,
            "email": "another@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password"""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post("/api/auth/login", json={
            "username": "nonexistent",
            "password": "password123"
        })
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "testuser"
    
    def test_get_current_user_no_auth(self, client):
        """Test getting current user without authentication"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
