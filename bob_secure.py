import socket
import random
import hmac
import hashlib

# --- Diffie-Hellman Parameters (Challenge 57) ---
p = 7199773997391911030609999317773941274322764333428698921736339643928346453700085358802973900485592910475480089726140708102474957429903531369589969318716771
g = 4565356397095740655436854503483826832136106141639563487732438195343690437606117828318042418238184896212352329118608100083187535033402010599512641674644143
q = 236234353446506858198510045061214171961

# --- Bob's Internal Private State ---
# Bob generates a secure random private key 'x' modulo q
bob_x = random.randint(2, q - 1)
# Bob's public key B = g^x mod p
bob_B = pow(g, bob_x, p)

def compute_mac(K: int, msg: bytes) -> bytes:
    """Computes HMAC-SHA256 of msg using shared secret K as key."""
    key_bytes = K.to_bytes((K.bit_length() + 7) // 8 or 1, byteorder='big')
    return hmac.new(key_bytes, msg, hashlib.sha256).digest()

def validate_public_key(y: int) -> bool:
    """
    Performs critical subgroup validation.
    Checks:
    1. 1 < y < p-1
    2. y^q mod p == 1 (Ensures the key belongs to the secure subgroup of order q)
    """
    if not (1 < y < p - 1):
        print(f"[Bob] [SECURITY FAILURE] Public key {y} is out of bounds!")
        return False
    if pow(y, q, p) != 1:
        print(f"[Bob] [SECURITY FAILURE] Public key does not belong to the correct subgroup of prime order q!")
        return False
    return True

def run_secure_bob():
    print("=========================================================")
    print("           BOB - SECURE DH SERVER (PORT 8081)           ")
    print("=========================================================")
    print(f"[Bob] Private key x: {bob_x}")
    print(f"[Bob] Public key B:  {bob_B}\n")

    # Bind the socket to port 8081 on localhost
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(('127.0.0.1', 8081))
    except Exception as e:
        print(f"[Bob] Error binding to port 8081: {e}")
        return

    server.listen(5)
    print("[Bob] Listening for connections on 127.0.0.1:8081...")

    while True:
        try:
            print("\n[Bob] Waiting for next client connection...")
            conn, addr = server.accept()
            print(f"[Bob] Connection established with {addr}")

            # Receive client's public key (A or h)
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                print("[Bob] Received empty data. Closing connection.")
                conn.close()
                continue

            y = int(data)
            print(f"[Bob] Received public key y: {y}")

            # --- SUBGROUP VALIDATION (DEFENSE AT WORK) ---
            if not validate_public_key(y):
                print("[Bob] [REJECTED] Terminating connection due to invalid public key.")
                conn.sendall(b"ERROR: Invalid public key (subgroup validation failed)!\n")
                conn.close()
                continue

            print("[Bob] [VALID] Public key verified successfully. Proceeding...")
            # Secure calculation of shared secret
            K = pow(y, bob_x, p)
            print(f"[Bob] Calculated shared secret K: {K}")

            # Prepare message and HMAC
            msg = b"crazy flamboyant for the rap enjoyment"
            mac = compute_mac(K, msg)

            # Send response packet back to the client
            response = f"BOB_PUB_KEY:{bob_B}\nMESSAGE:crazy flamboyant for the rap enjoyment\nMAC:{mac.hex()}\n"
            conn.sendall(response.encode('utf-8'))
            print("[Bob] Handshake completed and MAC sent.")
            conn.close()

        except Exception as e:
            print(f"[Bob] Error handling request: {e}")
            try:
                conn.close()
            except:
                pass

        # Check if the user wants to terminate the server loop
        # The program will stop ONLY if the user types 'yes' when prompted
        choice = input("\n[Bob] Keep waiting for connections? (type 'yes' to EXIT/STOP, press Enter to continue): ").strip().lower()
        if choice == 'yes':
            print("[Bob] Stopping secure server.")
            break

    server.close()

if __name__ == "__main__":
    run_secure_bob()
