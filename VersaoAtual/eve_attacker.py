import socket
import random
import hmac
import hashlib
from functools import reduce
import operator

# --- Diffie-Hellman Parameters (Challenge 57) ---
p = 7199773997391911030609999317773941274322764333428698921736339643928346453700085358802973900485592910475480089726140708102474957429903531369589969318716771
g = 4565356397095740655436854503483826832136106141639563487732438195343690437606117828318042418238184896212352329118608100083187535033402010599512641674644143
q = 236234353446506858198510045061214171961
j = (p - 1) // q

# --- Helper Cryptographic & Mathematical Functions ---

def compute_mac(K: int, msg: bytes) -> bytes:
    """Computes HMAC-SHA256 of msg using shared secret K as key."""
    key_bytes = K.to_bytes((K.bit_length() + 7) // 8 or 1, byteorder='big')
    return hmac.new(key_bytes, msg, hashlib.sha256).digest()

def find_small_prime_factors(n, limit=65536):
    """Dynamically factors n and returns distinct prime factors below limit."""
    factors = []
    temp = n
    if temp % 2 == 0:
        factors.append(2)
        while temp % 2 == 0:
            temp //= 2
    d = 3
    while d < limit and d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 2
    if 1 < temp < limit:
        factors.append(temp)
    return factors

def extended_gcd(a, b):
    """Extended Euclidean Algorithm to find modular inverse."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a, m):
    """Calculates modular inverse of a modulo m."""
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return x % m

def chinese_remainder_theorem(moduli, remainders):
    """
    Standard Chinese Remainder Theorem implementation.
    Calculates unique x modulo product(moduli).
    """
    total_sum = 0
    total_product = reduce(operator.mul, moduli, 1)
    for n_i, a_i in zip(moduli, remainders):
        p_i = total_product // n_i
        total_sum += a_i * mod_inverse(p_i, n_i) * p_i
    return total_sum % total_product

def generate_subgroup_element(r, p):
    """Generates an element h of order r modulo p (h^r mod p == 1)."""
    h = 1
    while h == 1:
        rand_val = random.randint(2, p - 1)
        h = pow(rand_val, (p - 1) // r, p)
    return h

# --- Main Attacker Logic ---

def run_attacker_eve():
    print("=========================================================")
    print("            EVE - COVERT ATTACKER (DH CRYPTANALYSIS)     ")
    print("=========================================================")

    # Select target Bob server port
    try:
        port_input = input("Select Target Bob's Port (8080 = Vulnerable, 8081 = Secure) [default: 8080]: ").strip()
        port = int(port_input) if port_input else 8080
    except ValueError:
        print("[Eve] Invalid input. Defaulting to port 8080.")
        port = 8080

    print(f"\n[Eve] Preparing attack targeting Bob on port {port}...")

    # Step A: Perform prime factorization of the public cofactor j
    print("[Eve] Factoring group cofactor j offline...")
    factors = find_small_prime_factors(j)
    print(f"[Eve] Small prime factors found: {factors}")

    # Step B: Pick enough factors so their product is greater than q
    factors_to_use = []
    product_accumulated = 1
    for r in factors:
        factors_to_use.append(r)
        product_accumulated *= r
        if product_accumulated > q:
            break

    print(f"[Eve] Selected factors for CRT reconstruction: {factors_to_use}")
    print(f"[Eve] Accumulated product: {product_accumulated}")
    print(f"[Eve] Product > q? {product_accumulated > q} (Safe threshold for perfect recovery)")

    remainders = []
    
    # Step C: For each factor, perform the small subgroup confinement query
    for r in factors_to_use:
        print(f"\n---------------------------------------------------------")
        print(f"[Eve] Target subgroup of order r = {r}")
        
        # 1. Generate malicious public key h belonging to the subgroup of order r
        h = generate_subgroup_element(r, p)
        print(f"[Eve] Generated malicious public key h: {h}")

        # 2. Establish connection and send key
        print(f"[Eve] Sending h to Bob...")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(('127.0.0.1', port))
        except Exception as e:
            print(f"[Eve] [ABORT] Could not connect to Bob's server: {e}")
            return

        client.sendall(f"{h}\n".encode('utf-8'))

        # 3. Receive and parse Response
        response = client.recv(4096).decode('utf-8')
        client.close()

        if not response:
            print("[Eve] [ABORT] Bob closed the connection without response.")
            return

        # Check if Bob's defensive validation blocked us
        if response.startswith("ERROR:"):
            print(f"\n🔴 [Eve] [ATTACK BLOCKED] Bob's server threw an error:")
            print(f"   >>> {response.strip()}")
            print("\n🛡️ SECURITY ALERT: Bob is validating public keys!")
            print("   Bob checked pow(y, q, p) == 1 and rejected our invalid key.")
            print("   Eve cannot recover Bob's private key because Bob refused to generate a MAC.")
            return

        # Parse valid handshake packet
        # Format:
        # BOB_PUB_KEY:<B>
        # MESSAGE:<msg>
        # MAC:<mac_hex>
        lines = response.strip().split('\n')
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

        if received_mac is None or msg is None:
            print("[Eve] [ABORT] Failed to parse response structure.")
            return

        # 4. Perform local offline brute force on the small subgroup of size r
        print(f"[Eve] Bob calculated and returned a MAC. Cracking x mod {r} offline...")
        cracked_mod_r = None
        for test_val in range(r):
            # Compute possible shared secret
            K_test = pow(h, test_val, p)
            # Compare generated MAC with Bob's returned MAC
            if compute_mac(K_test, msg) == received_mac:
                cracked_mod_r = test_val
                print(f"🎉 [Eve] [SUCCESS] Recovered equivalence: x mod {r} = {cracked_mod_r}")
                remainders.append(cracked_mod_r)
                break

        if cracked_mod_r is None:
            print(f"❌ [Eve] [FAILURE] Brute-force failed to find a valid residue. Subgroup size {r} compromised.")
            return

    # Step D: Apply Chinese Remainder Theorem to find the actual private key x
    print("\n=========================================================")
    print("[Eve] Recovered all modular residues. Applying Chinese Remainder Theorem...")
    recovered_bob_x = chinese_remainder_theorem(factors_to_use, remainders)

    print("\n================== ATTACK RESULT ==================")
    print(f"Bob's Recovered Private Key x: {recovered_bob_x}")
    print(f"Recovered Key Bit Length:      {recovered_bob_x.bit_length()} bits")
    print("\n💥 ATTACK COMPLETE: Bob's static private key has been compromised!")
    print("=========================================================")

if __name__ == "__main__":
    run_attacker_eve()
    input("\n[Pressione ENTER para fechar o programa...]")
