import random
import hmac
import hashlib
from functools import reduce
import operator

# --- Parâmetros Oficiais do Desafio 57 ---
p = 7199773997391911030609999317773941274322764333428698921736339643928346453700085358802973900485592910475480089726140708102474957429903531369589969318716771
g = 4565356397095740655436854503483826832136106141639563487732438195343690437606117828318042418238184896212352329118608100083187535033402010599512641674644143
q = 236234353446506858198510045061214171961
j = (p - 1) // q

# --- 1. Bob (O Alvo) ---
# Bob gera sua chave privada secreta 'x' de forma aleatória módulo q
bob_x = random.randint(2, q - 1)

def calcular_mac(K: int, m: bytes) -> bytes:
    """Calcula o HMAC-SHA256 de uma mensagem usando o segredo K como chave."""
    chave_bytes = K.to_bytes((K.bit_length() + 7) // 8 or 1, byteorder='big')
    return hmac.new(chave_bytes, m, hashlib.sha256).digest()

def oraculo_do_bob(chave_publica_recebida: int):
    """Simula o oráculo de Bob recebendo uma chave pública e respondendo com a mensagem e o MAC."""
    K = pow(chave_publica_recebida, bob_x, p)
    m = b"crazy flamboyant for the rap enjoyment"
    t = calcular_mac(K, m)
    return m, t

# --- 2. Algoritmos Auxiliares do Atacante (Eve) ---

def encontrar_fatores_pequenos(n, limite=65536):
    """Encontra os fatores primos de n menores que o limite de forma dinâmica."""
    fatores = []
    temp = n
    if temp % 2 == 0:
        fatores.append(2)
        while temp % 2 == 0:
            temp //= 2
    d = 3
    while d < limite and d * d <= temp:
        if temp % d == 0:
            fatores.append(d)
            while temp % d == 0:
                temp //= d
        d += 2
    if 1 < temp < limite:
        fatores.append(temp)
    return fatores

def mdc_estendido(a, b):
    """Algoritmo de Euclides Estendido para encontrar o inverso modular."""
    if a == 0:
        return b, 0, 1
    mdc, x1, y1 = mdc_estendido(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return mdc, x, y

def inverso_modular(a, m):
    """Calcula o inverso modular de a mod m."""
    mdc, x, _ = mdc_estendido(a, m)
    if mdc != 1:
        raise Exception("Inverso modular não existe")
    return x % m

def teorema_chines_resto(n, a):
    """
    Resolve o sistema de congruências usando o Teorema Chinês do Resto.
    n: lista de módulos coprime (r_i)
    a: lista de restos (x mod r_i)
    Retorna o valor único x mod (produto de todos os r_i).
    """
    soma = 0
    produto = reduce(operator.mul, n, 1)
    for n_i, a_i in zip(n, a):
        p_i = produto // n_i
        soma += a_i * inverso_modular(p_i, n_i) * p_i
    return soma % produto

def gerar_elemento_de_ordem(r, p):
    """Gera um elemento h de ordem r módulo p."""
    h = 1
    while h == 1:
        rand_val = random.randint(2, p - 1)
        h = pow(rand_val, (p - 1) // r, p)
    return h

# --- 3. Execução do Ataque Completo ---

def executar_ataque_completo():
    print("[*] Iniciando ataque completo de reconstrução Diffie-Hellman...")
    print(f"[+] Chave privada real de Bob (secreta): {bob_x}")
    
    # Passo A: Encontrar os fatores primos pequenos de j
    print("[+] Analisando a estrutura matemática do grupo público (fatorando j)...")
    fatores = encontrar_fatores_pequenos(j)
    print(f"[+] Fatores pequenos encontrados (< 2^16): {fatores}")
    
    # Passo B: Selecionar fatores até que o produto supere q
    fatores_usados = []
    acumulado = 1
    for r in fatores:
        fatores_usados.append(r)
        acumulado *= r
        if acumulado > q:
            break
            
    print(f"[+] Fatores selecionados para o ataque: {fatores_usados}")
    print(f"[+] Produto dos fatores selecionados: {acumulado}")
    print(f"[+] O produto é maior que q? {acumulado > q} (Necessário para reconstruir x perfeitamente)")
    
    # Passo C: Atacar cada subgrupo para obter as congruências (bob_x mod r_i)
    restos = []
    for r in fatores_usados:
        print(f"\n[*] Atacando subgrupo de ordem r = {r}...")
        
        # Gerar h de ordem r
        h = gerar_elemento_de_ordem(r, p)
        
        # Consultar o oráculo de Bob
        m, t = oraculo_do_bob(h)
        
        # Força bruta offline no subgrupo
        encontrado = False
        for palpite_v in range(r):
            K_palpite = pow(h, palpite_v, p)
            t_palpite = calcular_mac(K_palpite, m)
            if t_palpite == t:
                print(f"  [SUCESSO] Descoberto: Bob_x mod {r} = {palpite_v}")
                restos.append(palpite_v)
                encontrado = True
                break
        if not encontrado:
            print(f"  [ERRO] Falha ao decifrar módulo {r}")
            return
            
    # Passo D: Reconstruir a chave usando o Teorema Chinês do Resto (CRT)
    print("\n[+] Aplicando o Teorema Chinês do Resto (CRT) para unificar os restos...")
    chave_reconstruida = teorema_chines_resto(fatores_usados, restos)
    
    print("\n================== RESULTADO FINAL ==================")
    print(f"Chave Privada Real de Bob:       {bob_x}")
    print(f"Chave Reconstruída pelo CRT:    {chave_reconstruida}")
    
    if chave_reconstruida == bob_x:
        print("\n🎉 SUCESSO ABSOLUTO! A chave recuperada é 100% IDÊNTICA à chave secreta do Bob!")
    else:
        print("\n⚠ A chave reconstruída difere. Verifique se o produto acumulado superou q.")

if __name__ == "__main__":
    executar_ataque_completo()
    input("\n[Pressione ENTER para fechar o programa...]")