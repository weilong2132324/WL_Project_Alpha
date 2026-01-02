"""Tests for group endpoints"""

import pytest


class TestGroups:
    """Group endpoint tests"""
    
    def test_create_group(self, client, auth_headers):
        """Test creating a new group"""
        response = client.post("/api/groups", json={
            "name": "testgroup",
            "description": "A test group"
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "testgroup"
        assert data["description"] == "A test group"
    
    def test_create_duplicate_group(self, client, auth_headers):
        """Test creating duplicate group"""
        client.post("/api/groups", json={
            "name": "duplicategroup",
            "description": "First group"
        }, headers=auth_headers)
        
        response = client.post("/api/groups", json={
            "name": "duplicategroup",
            "description": "Second group"
        }, headers=auth_headers)
        
        assert response.status_code == 400
    
    def test_get_group(self, client, auth_headers, db):
        """Test getting a group by ID"""
        from app.models import Group
        
        group = Group(name="getgroup", description="Test")
        db.add(group)
        db.commit()
        db.refresh(group)
        
        response = client.get(f"/api/groups/{group.id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "getgroup"
    
    def test_list_groups(self, client, auth_headers, db):
        """Test listing groups"""
        from app.models import Group
        
        group = Group(name="listgroup", description="Test")
        db.add(group)
        db.commit()
        
        response = client.get("/api/groups", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_group(self, client, auth_headers, db):
        """Test updating a group"""
        from app.models import Group
        
        group = Group(name="updategroup", description="Original")
        db.add(group)
        db.commit()
        db.refresh(group)
        
        response = client.put(f"/api/groups/{group.id}", json={
            "description": "Updated"
        }, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated"
    
    def test_delete_group(self, client, auth_headers, db):
        """Test deleting a group"""
        from app.models import Group
        
        group = Group(name="deletegroup", description="To delete")
        db.add(group)
        db.commit()
        db.refresh(group)
        
        response = client.delete(f"/api/groups/{group.id}", headers=auth_headers)
        
        assert response.status_code == 204
