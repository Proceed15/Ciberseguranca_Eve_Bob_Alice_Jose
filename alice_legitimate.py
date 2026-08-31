import socket
import random
import hmac
import hashlib

# --- Diffie-Hellman Parameters (Challenge 57) ---
p = 7199773997391911030609999317773941274322764333428698921736339643928346453700085358802973900485592910475480089726140708102474957429903531369589969318716771
g = 4565356397095740655436854503483826832136106141639563487732438195343690437606117828318042418238184896212352329118608100083187535033402010599512641674644143
q = 236234353446506858198510045061214171961

def compute_mac(K: int, msg: bytes) -> bytes:
    """Computes HMAC-SHA256 of msg using shared secret K as key."""
    key_bytes = K.to_bytes((K.bit_length() + 7) // 8 or 1, byteorder='big')
    return hmac.new(key_bytes, msg, hashlib.sha256).digest()

def run_legitimate_alice():
    print("=========================================================")
    print("            ALICE - LEGITIMATE CLIENT CLIENT             ")
    print("=========================================================")

    # Select Bob's server port
    try:
        port_input = input("Select Bob's Port (8080 = Vulnerable, 8081 = Secure) [default: 8080]: ").strip()
        port = int(port_input) if port_input else 8080
    except ValueError:
        print("[Alice] Invalid input. Defaulting to port 8080.")
        port = 8080

    # 1. Alice generates her DH keypair legitimately
    print("\n[Alice] Generating key pair...")
    alice_a = random.randint(2, q - 1)
    # Alice's public key A = g^a mod p
    alice_A = pow(g, alice_a, p)
    print(f"[Alice] Private key a: {alice_a}")
    print(f"[Alice] Public key A:  {alice_A}")

    # 2. Connect to Bob's server
    print(f"\n[Alice] Connecting to Bob on 127.0.0.1:{port}...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', port))
    except Exception as e:
        print(f"[Alice] Failed to connect to Bob's server: {e}")
        return

    # 3. Send Alice's public key A
    print("[Alice] Sending public key A to Bob...")
    client.sendall(f"{alice_A}\n".encode('utf-8'))

    # 4. Receive Bob's response
    response_data = client.recv(4096).decode('utf-8')
    client.close()

    if not response_data:
        print("[Alice] Received no response from Bob.")
        return

    # Check if Bob rejected Alice
    if response_data.startswith("ERROR:"):
        print(f"\n[Alice] Bob rejected the connection! Server returned error:\n{response_data}")
        return

    print("\n[Alice] Received handshake response from Bob!")
    
    # Parse Bob's response:
    # Expected lines:
    # BOB_PUB_KEY:<B>
    # MESSAGE:<msg>
    # MAC:<mac_hex>
    lines = response_data.strip().split('\n')
    bob_B = None
    msg = None
    received_mac = None

    for line in lines:
        if line.startswith("BOB_PUB_KEY:"):
            bob_B = int(line.split("BOB_PUB_KEY:")[1])
        elif line.startswith("MESSAGE:"):
            msg = line.split("MESSAGE:")[1].encode('utf-8')
        elif line.startswith("MAC:"):
            received_mac = bytes.fromhex(line.split("MAC:")[1])

    if bob_B is None or msg is None or received_mac is None:
        print("[Alice] Failed to parse Bob's response packet structure.")
        return

    print(f"[Alice] Bob's Public Key B: {bob_B}")
    print(f"[Alice] Received Message:   '{msg.decode('utf-8')}'")
    print(f"[Alice] Received MAC:       {received_mac.hex()}")

    # 5. Alice computes the shared secret: K_A = B^a mod p
    print("\n[Alice] Computing shared secret key...")
    K_A = pow(bob_B, alice_a, p)
    print(f"[Alice] Computed shared secret K_A: {K_A}")

    # 6. Verify MAC integrity
    computed_mac = compute_mac(K_A, msg)
    print(f"[Alice] Locally computed MAC:        {computed_mac.hex()}")

    if computed_mac == received_mac:
        print("\n💚 SUCCESS: MAC verified! Alice is 100% sure the channel is secure and authentic.")
    else:
        print("\n💔 FAILURE: MAC mismatch! Security compromised!")

if __name__ == "__main__":
    run_legitimate_alice()
    input("\n[Pressione ENTER para fechar o programa...]")
