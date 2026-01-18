#!/usr/bin/env python
"""
Script to handle Hugging Face login using the Python API
since the CLI command is not working properly.
"""

from huggingface_hub import login
import os
import sys

def main():
    # Check if a token was passed as a command line argument
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        # Get token from environment variable
        token = os.environ.get("HF_TOKEN")

    if not token:
        print("Hugging Face token not provided.")
        print("Usage: python hf_login.py <your_hf_token>")
        print("Or set the HF_TOKEN environment variable.")
        return

    try:
        login(token=token)
        print("Successfully logged in to Hugging Face Hub!")

        # Verify the login worked
        from huggingface_hub import whoami
        user_info = whoami()
        print(f"Logged in as: {user_info['name']}")

    except Exception as e:
        print(f"Error during login: {e}")

if __name__ == "__main__":
    main()