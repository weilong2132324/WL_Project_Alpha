"""Tests for utility functions"""

import pytest
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    extract_token_from_header
)


class TestPasswordHashing:
    """Password hashing tests"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50
    
    def test_verify_correct_password(self):
        """Test verifying correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self):
        """Test verifying incorrect password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False


class TestJWT:
    """JWT token tests"""
    
    def test_create_token(self):
        """Test creating JWT token"""
        token = create_access_token(1, "testuser")
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100
    
    def test_verify_valid_token(self):
        """Test verifying valid token"""
        token = create_access_token(1, "testuser")
        token_data = verify_token(token)
        
        assert token_data is not None
        assert token_data.user_id == 1
        assert token_data.username == "testuser"
    
    def test_verify_invalid_token(self):
        """Test verifying invalid token"""
        token_data = verify_token("invalid.token.here")
        
        assert token_data is None
    
    def test_extract_token_from_header(self):
        """Test extracting token from Authorization header"""
        header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        token = extract_token_from_header(header)
        
        assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
    
    def test_extract_token_missing_bearer(self):
        """Test extracting token without Bearer prefix"""
        token = extract_token_from_header("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test")
        
        assert token is None
    
    def test_extract_token_none(self):
        """Test extracting token from None"""
        token = extract_token_from_header(None)
        
        assert token is None
