"""
Test script to check if there are any import errors in the auth module
"""
import sys
import os

# Add the backend/src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    from api.routes import auth
    print("✓ Auth module imported successfully")
    
    # Try to access the sign_in function
    if hasattr(auth, 'sign_in'):
        print("✓ sign_in function exists")
    else:
        print("✗ sign_in function does not exist")
        
    # Try to access the sign_up function
    if hasattr(auth, 'sign_up'):
        print("✓ sign_up function exists")
    else:
        print("✗ sign_up function does not exist")
        
    print("✓ No import errors in auth module")
    
except ImportError as e:
    print(f"✗ Import error in auth module: {e}")
    
except Exception as e:
    print(f"✗ Error testing auth module: {e}")