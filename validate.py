# validate.py
from keygen import generate_private_seed, generate_keys
from sign import Sign
from utils_for_verify import verify_signature

def validate_key_generation_and_signature():
    print("Starting validation process...\n")

    # Step 1: Generate private seed
    private_seed = generate_private_seed()
    print(f"Private Seed: {private_seed.hex()}")

    # Step 2: Generate public and private keys
    public_key, private_key = generate_keys(private_seed)
    public_seed, Q2 = public_key
    print(f"Public Seed: {public_seed.hex()}")
    print(f"Q2 (first 5 rows):\n{Q2[:5]}")

    # Verify the structure and properties of the generated keys
    print("Validating key generation...")
    if len(public_seed) != 32:
        print("Invalid public seed length!")
    elif Q2.shape != (57, ((197 * (197 + 1)) // 2) + (197 * 57)):
        print("Invalid Q2 dimensions!")
    else:
        print("Key generation validation passed.")

    # Step 3: Prepare a message
    message = "Test message for validation.".encode("utf-8")
    print(f"Message: {message.decode('utf-8')}")

    # Step 4: Sign the message
    signature, salt = Sign(private_key, message)
    print(f"Signature (first 32 bytes): {signature[:32]}")
    print(f"Salt: {salt.hex()}")

    # Step 5: Verify the signature
    print("Verifying signature...")
    is_valid = verify_signature(public_key, message, signature + salt)
    print(f"Verification Result: {'Valid' if is_valid else 'Invalid'}")

    # Final result
    if is_valid:
        print("\nValidation process completed successfully.")
    else:
        print("\nValidation process failed. Check implementation.")

if __name__ == "__main__":
    validate_key_generation_and_signature()
