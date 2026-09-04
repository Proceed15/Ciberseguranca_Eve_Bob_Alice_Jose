import random
import hmac
import hashlib

# --- Parâmetros Oficiais do Desafio 57 ---
p = 7199773997391911030609999317773941274322764333428698921736339643928346453700085358802973900485592910475480089726140708102474957429903531369589969318716771
g = 4565356397095740655436854503483826832136106141639563487732438195343690437606117828318042418238184896212352329118608100083187535033402010599512641674644143
q = 236234353446506858198510045061214171961

# --- 1. Bob (O Alvo) ---
# Bob gera sua chave privada secreta 'x' de forma aleatória módulo q
bob_x = random.randint(2, q - 1)

def calcular_mac(K: int, m: bytes) -> bytes:
    """
    Calcula o HMAC-SHA256 usando o segredo K como chave.
    Converte o número inteiro K em representação de bytes (big-endian).
    """
    chave_K = K.to_bytes((K.bit_length() + 7) // 8 or 1, byteorder='big')
    return hmac.new(chave_K, m, hashlib.sha256).digest()

# O Oráculo de Bob (Simulação local da resposta do servidor de Bob)
def oraculo_do_bob(chave_publica_recebida: int):
    # Bob calcula o segredo K = (chave_recebida ^ x) mod p
    K = pow(chave_publica_recebida, bob_x, p)
    
    # Mensagem padrão do desafio
    m = b"crazy flamboyant for the rap enjoyment"
    t = calcular_mac(K, m)
    
    return m, t

# --- 2. Atacante (Eve) ---
def atacar_fator_r(r: int):
    print(f"\n[*] Iniciando ataque para o fator r = {r}")
    
    # Gerar um elemento h de ordem r (h^r mod p = 1)
    h = 1
    while h == 1:
        rand_val = random.randint(2, p - 1)
        h = pow(rand_val, (p - 1) // r, p)
        
    print(f"[+] Enviando chave pública maliciosa h para o Bob...")
    
    # Envia a chave pública falsa 'h' para o Oráculo de Bob
    m, t = oraculo_do_bob(h)
    
    print(f"[+] Bob retornou o MAC: {t.hex()[:32]}...")
    print(f"[+] Iniciando busca exaustiva offline no subgrupo de tamanho {r}...")
    
    # Força bruta offline: testa todas as r possibilidades possíveis para K
    for palpite_v in range(r):
        # Calcula o palpite para o segredo K: h^palpite mod p
        K_palpite = pow(h, palpite_v, p)
        
        # Calcula o MAC correspondente
        t_palpite = calcular_mac(K_palpite, m)
        
        # Se os MACs coincidirem, descobrimos o resto da divisão (bob_x % r)
        if t_palpite == t:
            print(f"[SUCCESS] Encontrado! Bob_x mod {r} = {palpite_v}")
            # Verificação de segurança (apenas para o teste):
            real_v = bob_x % r
            print(f"          (Chave real de Bob mod {r} e: {real_v})")
            return palpite_v
            
    print("[-] Falha: o valor nao foi encontrado no subgrupo.")
    return None
# Testar o ataque de confinamento de subgrupo para alguns fatores pequenos de j
#fatores_teste = [5-8]
fatores_teste = [2, 3, 5, 109]
for r in fatores_teste:
    atacar_fator_r(r)

# Impede o terminal de fechar imediatamente caso execute por clique duplo
input("\n[Pressione ENTER para fechar o programa...]")