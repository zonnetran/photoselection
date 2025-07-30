#!/usr/bin/env python3
"""
Gallery Setup Script for Photographers
Usage: python setup_gallery.py <gallery_name> [password]
"""

import os
import sys
import json
import shutil

def setup_gallery(gallery_name, password=None):
    # Create gallery directory
    gallery_path = os.path.join('static', 'galleries', gallery_name)
    os.makedirs(gallery_path, exist_ok=True)
    
    # Set password if provided
    if password:
        passwords_file = 'gallery_passwords.json'
        passwords = {}
        
        if os.path.exists(passwords_file):
            with open(passwords_file, 'r') as f:
                passwords = json.load(f)
        
        passwords[gallery_name] = password
        
        with open(passwords_file, 'w') as f:
            json.dump(passwords, f, indent=2)
        
        print(f"✅ Gallery '{gallery_name}' created with password protection")
    else:
        print(f"✅ Gallery '{gallery_name}' created (no password)")
    
    print(f"📁 Upload your photos to: {gallery_path}")
    print(f"🌐 Gallery URL: http://localhost:8080/gallery/{gallery_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python setup_gallery.py <gallery_name> [password]")
        print("Example: python setup_gallery.py client_smith mypassword123")
        sys.exit(1)
    
    gallery_name = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None
    
    setup_gallery(gallery_name, password)