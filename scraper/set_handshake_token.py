import os
import sys

def set_token():
    print("Please enter your Handshake authentication token.")
    print("You can find this by:")
    print("1. Log into Handshake")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Application > Cookies > app.joinhandshake.com")
    print("4. Find the 'hss-global' cookie value")
    print("\nEnter token (or press Enter to cancel):")
    
    token = input().strip()
    if not token:
        print("Cancelled.")
        return
    
    # Set environment variable
    os.environ["HANDSHAKE_AUTH_TOKEN"] = token
    print("\nToken set successfully!")
    print("Note: This token will only be valid for this terminal session.")
    print("To make it permanent, add the following to your shell profile (~/.zshrc or ~/.bashrc):")
    print(f'export HANDSHAKE_AUTH_TOKEN="{token}"')

if __name__ == "__main__":
    set_token() 