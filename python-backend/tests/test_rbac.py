"""Tests for RBAC endpoints"""

import pytest


class TestRBAC:
    """RBAC endpoint tests"""
    
    def test_create_role(self, client, auth_headers):
        """Test creating a role"""
        response = client.post("/api/rbac/roles", json={
            "name": "admin",
            "description": "Administrator role"
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "admin"
    
    def test_create_rule(self, client, auth_headers):
        """Test creating a rule"""
        response = client.post("/api/rbac/rules", json={
            "name": "user_read",
            "resource": "users",
            "operation": "read",
            "description": "Read users"
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["resource"] == "users"
        assert data["operation"] == "read"
    
    def test_list_roles(self, client, auth_headers, db):
        """Test listing roles"""
        from app.models import Role
        
        role = Role(name="testrole", description="Test")
        db.add(role)
        db.commit()
        
        response = client.get("/api/rbac/roles", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_assign_role_to_user(self, client, test_user, auth_headers, db):
        """Test assigning role to user"""
        from app.models import Role
        
        role = Role(name="assignrole", description="Test")
        db.add(role)
        db.commit()
        db.refresh(role)
        
        response = client.post(
            f"/api/rbac/users/{test_user.id}/roles/{role.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
    
    def test_get_user_permissions(self, client, test_user, auth_headers):
        """Test getting user permissions"""
        response = client.get(
            f"/api/rbac/users/{test_user.id}/permissions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
