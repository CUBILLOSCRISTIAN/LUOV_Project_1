from keygen import generate_private_seed, generate_keys
from sign import Sign
from utils_for_verify import verify_signature
import traceback
import numpy as np


def validate_key_generation_and_signature():
    print("Starting validation process...\n")

    try:
        # Step 1: Generate private seed
        private_seed = generate_private_seed()
        print(f"Private Seed: {private_seed.hex()}")

        # Step 2: Generate public and private keys
        public_key, private_key = generate_keys(private_seed)
        public_seed, Q2 = public_key

        # Serialize public key to strings
        public_seed_str = public_seed.hex()
        print(f"Public Seed (Hex): {public_seed_str}")
        print(f"Q2 (Shape): {Q2.shape}")

        # Verify the structure and properties of the generated keys
        print("Validating key generation...")
        if len(public_seed) != 32:
            print("Error: Invalid public seed length!")
            return
        print("Key generation validation passed.")

        # Step 3: Prepare a message
        message = "Test message for validation.".encode("utf-8")
        print(f"Message: {message.decode('utf-8')}")

        # Step 4: Sign the message
        print("\nSigning the message...")
        try:
            signature, salt = Sign(private_key, message)
            print(f"Signature (length {len(signature)}): {signature[:10]}... (truncated)")
            print(f"Salt (Hex): {salt.hex()}")
        except ValueError as ve:
            print(f"Error during signing: {ve}")
            traceback.print_exc()
            return

        # Convert signature and salt into compatible types for verification
        try:
            # Convert signature to integers if needed
            if np.issubdtype(signature.dtype, np.floating):
                print("Converting signature from float to int...")
                signature = signature.astype(np.int64)

            # Combine signature and salt into a single bytes object
            combined_signature = np.concatenate([signature, np.frombuffer(salt, dtype=np.uint8)]).tobytes()
            print(f"Combined Signature + Salt (Bytes): {combined_signature[:50]}... (truncated)")
        except Exception as e:
            print(f"Error during signature conversion: {e}")
            traceback.print_exc()
            return

        # Step 5: Verify the signature
        print("\nVerifying signature...")
        try:
            is_valid = verify_signature(public_key, message, combined_signature)
            print(f"Verification Result: {'Valid' if is_valid else 'Invalid'}")
        except Exception as e:
            print(f"Error during signature verification: {e}")
            traceback.print_exc()
            return

        # Final result
        if is_valid:
            print("\nValidation process completed successfully.")
        else:
            print("\nValidation process failed. Check implementation.")

    except Exception as e:
        print(f"An unexpected error occurred during validation: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    validate_key_generation_and_signature()
