import os
import json
import logging
from Crypto.Cipher import AES, DES3, Blowfish
from Crypto.Util.Padding import pad, unpad
import base64
import hashlib

# Logging configuration
logging.basicConfig(
    filename='admin_environment.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Paths and files
ADMIN_KEYS_FILE = 'admin_keys.json'
ADMIN_CODES_FILE = 'admin_codes.json'

# Security keys
KEY1 = os.getenv('ENCRYPTION_KEY1', get_random_bytes(16))
KEY2 = os.getenv('ENCRYPTION_KEY2', get_random_bytes(24))
KEY3 = os.getenv('ENCRYPTION_KEY3', get_random_bytes(32))

def multi_stage_encryption(data):
    """Encrypt data in 8 stages using different encryption protocols."""
    try:
        key1 = KEY1
        key2 = KEY2
        key3 = KEY3

        # Stage 1: AES
        cipher = AES.new(key1, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv1 = base64.b64encode(cipher.iv).decode('utf-8')
        ct1 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 2: DES3
        cipher = DES3.new(key2, DES3.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct1.encode(), DES3.block_size))
        iv2 = base64.b64encode(cipher.iv).decode('utf-8')
        ct2 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 3: Blowfish
        cipher = Blowfish.new(key3, Blowfish.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct2.encode(), Blowfish.block_size))
        iv3 = base64.b64encode(cipher.iv).decode('utf-8')
        ct3 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 4: AES again
        cipher = AES.new(key1, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct3.encode(), AES.block_size))
        iv4 = base64.b64encode(cipher.iv).decode('utf-8')
        ct4 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 5: DES3 again
        cipher = DES3.new(key2, DES3.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct4.encode(), DES3.block_size))
        iv5 = base64.b64encode(cipher.iv).decode('utf-8')
        ct5 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 6: Blowfish again
        cipher = Blowfish.new(key3, Blowfish.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct5.encode(), Blowfish.block_size))
        iv6 = base64.b64encode(cipher.iv).decode('utf-8')
        ct6 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 7: AES again
        cipher = AES.new(key1, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct6.encode(), AES.block_size))
        iv7 = base64.b64encode(cipher.iv).decode('utf-8')
        ct7 = base64.b64encode(ct_bytes).decode('utf-8')

        # Stage 8: DES3 again
        cipher = DES3.new(key2, DES3.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(ct7.encode(), DES3.block_size))
        iv8 = base64.b64encode(cipher.iv).decode('utf-8')
        ct8 = base64.b64encode(ct_bytes).decode('utf-8')

        return {
            'iv1': iv1, 'ct1': ct1,
            'iv2': iv2, 'ct2': ct2,
            'iv3': iv3, 'ct3': ct3,
            'iv4': iv4, 'ct4': ct4,
            'iv5': iv5, 'ct5': ct5,
            'iv6': iv6, 'ct6': ct6,
            'iv7': iv7, 'ct7': ct7,
            'iv8': iv8, 'ct8': ct8
        }
    except Exception as e:
        logging.error(f"Error in multi-stage encryption: {e}")
        raise

def generate_admin_code(username):
    """Generate an admin code with multi-stage encryption based on username."""
    try:
        admin_code = f"ADMIN_CODE_{username}"
        encrypted_code = multi_stage_encryption(admin_code)
        return encrypted_code
    except Exception as e:
        logging.error(f"Error generating admin code: {e}")
        raise

def save_admin_code(encrypted_code):
    """Save the encrypted admin code to a file."""
    with open(ADMIN_CODES_FILE, 'w') as f:
        json.dump(encrypted_code, f)
    logging.info("Admin code saved.")

def load_admin_code():
    """Load the encrypted admin code from a file."""
    try:
        with open(ADMIN_CODES_FILE, 'r') as f:
            encrypted_code = json.load(f)
        return encrypted_code
    except FileNotFoundError:
        logging.error("Admin code file not found.")
        return None

def verify_admin_code(encrypted_code, username):
    """Verify the admin code based on the username."""
    try:
        decrypted_code = multi_stage_decryption(encrypted_code)
        expected_code = f"ADMIN_CODE_{username}"
        return decrypted_code == expected_code
    except Exception as e:
        logging.error(f"Error verifying admin code: {e}")
        return False

def admin_menu():
    """Display the admin menu and handle admin operations."""
    print("Admin Menu:")
    print("1. Generate Admin Code")
    print("2. Verify Admin Code")
    choice = input("Enter your choice: ")

    if choice == "1":
        username = input("Enter admin username: ")
        encrypted_code = generate_admin_code(username)
        save_admin_code(encrypted_code)
        print("Admin code generated and saved successfully.")
    elif choice == "2":
        username = input("Enter admin username: ")
        encrypted_code = load_admin_code()
        if encrypted_code:
            if verify_admin_code(encrypted_code, username):
                print("Admin code is valid.")
            else:
                print("Admin code is invalid.")
        else:
            print("No admin code found.")
    else:
        print("Invalid choice.")

if __name__ == '__main__':
    admin_menu()