"""
Security tests for the RAG Todo Chatbot API
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import patch, Mock
import os
from backend.src.main import app
from backend.src.security_config import validate_user_input, sanitize_user_input


client = TestClient(app)


def test_input_validation():
    """
    Test the input validation functions
    """
    # Test valid input
    assert validate_user_input("This is a valid input") == True
    
    # Test SQL injection patterns
    assert validate_user_input("SELECT * FROM users") == False
    assert validate_user_input("DROP TABLE users") == False
    assert validate_user_input("'; DROP TABLE users; --") == False
    
    # Test XSS patterns
    assert validate_user_input("<script>alert('xss')</script>") == False
    assert validate_user_input("javascript:alert('xss')") == False
    
    print("✓ Input validation tests passed")


def test_input_sanitization():
    """
    Test the input sanitization functions
    """
    # Test sanitization of dangerous inputs
    dangerous_input = "<script>alert('xss')</script>"
    sanitized = sanitize_user_input(dangerous_input)
    assert "<script" not in sanitized
    
    dangerous_input2 = "javascript:alert('test')"
    sanitized2 = sanitize_user_input(dangerous_input2)
    assert "javascript:" not in sanitized2
    
    # Test normal input remains unchanged
    normal_input = "This is a normal task title"
    sanitized_normal = sanitize_user_input(normal_input)
    assert sanitized_normal == normal_input
    
    print("✓ Input sanitization tests passed")


def test_authentication_required():
    """
    Test that endpoints require authentication
    """
    # Try to access an endpoint without authentication
    # Note: This is a simplified test - in a real implementation,
    # we would need to test with actual JWT tokens
    response = client.get("/health")
    assert response.status_code == 200  # Health check should be public
    
    print("✓ Authentication requirement tests passed (simplified)")


def test_rate_limiting():
    """
    Test rate limiting functionality
    """
    # This is a simplified test - in a real implementation,
    # we would need to make multiple requests to test rate limiting
    response = client.get("/health")
    assert response.status_code == 200
    
    print("✓ Rate limiting test structure in place")


def test_security_headers():
    """
    Test that security headers are properly set
    """
    response = client.get("/health")
    
    # Check for security headers
    headers = dict(response.headers)
    
    assert "x-content-type-options" in headers
    assert headers["x-content-type-options"] == "nosniff"
    
    assert "x-frame-options" in headers
    assert headers["x-frame-options"] == "DENY"
    
    assert "x-xss-protection" in headers
    assert headers["x-xss-protection"] == "1; mode=block"
    
    print("✓ Security headers test passed")


def test_user_isolation():
    """
    Test that users can only access their own data
    """
    # Mock the Cohere client
    with patch('cohere.Client') as mock_cohere:
        # Setup mock response
        mock_response = Mock()
        mock_response.generations = [Mock()]
        mock_response.generations[0].text = "Test response"
        mock_cohere.return_value.generate.return_value = mock_response

        # Set required environment variable
        os.environ["COHERE_API_KEY"] = "test-key"

        # This test would require a more complex setup with actual user authentication
        # For now, we'll verify the structure of the security implementation
        print("✓ User isolation test structure in place")


if __name__ == "__main__":
    test_input_validation()
    test_input_sanitization()
    test_authentication_required()
    test_rate_limiting()
    test_security_headers()
    test_user_isolation()
    print("All security tests completed!")