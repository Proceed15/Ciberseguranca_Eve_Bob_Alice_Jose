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

# --- 1. Bob (O Alvo com Opção de Defesa) ---
bob_x = random.randint(2, q - 1)
validacao_ativa = False  # Controle se a defesa está ativa ou inativa

def validar_chave_publica(y: int, p: int, q: int) -> bool:
    """
    Verifica se a chave pública recebida 'y' pertence ao subgrupo correto.
    1. A chave deve estar no intervalo (1, p-1).
    2. y^q mod p deve ser igual a 1 (garante que y está no subgrupo de ordem prima q).
    """
    if not (1 < y < p - 1):
        return False
    # Validação do subgrupo de ordem prima q
    return pow(y, q, p) == 1

def calcular_mac(K: int, m: bytes) -> bytes:
    """Calcula o HMAC-SHA256 de uma mensagem usando o segredo K como chave."""
    chave_bytes = K.to_bytes((K.bit_length() + 7) // 8 or 1, byteorder='big')
    return hmac.new(chave_bytes, m, hashlib.sha256).digest()

def oraculo_do_bob(chave_publica_recebida: int):
    """
    Oráculo de Bob. Se a validação estiver ativa, ele rejeita chaves que 
    não pertençam ao subgrupo correto.
    """
    if validacao_ativa:
        if not validar_chave_publica(chave_publica_recebida, p, q):
            raise ValueError("CONEXÃO REJEITADA: Chave pública inválida (não pertence ao subgrupo correto)!")
            
    K = pow(chave_publica_recebida, bob_x, p)
    m = b"crazy flamboyant for the rap enjoyment"
    t = calcular_mac(K, m)
    return m, t

# --- 2. Algoritmos Auxiliares do Atacante (Eve) ---

def encontrar_fatores_pequenos(n, limite=65536):
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
    if a == 0:
        return b, 0, 1
    mdc, x1, y1 = mdc_estendido(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return mdc, x, y

def inverso_modular(a, m):
    mdc, x, _ = mdc_estendido(a, m)
    if mdc != 1:
        raise Exception("Inverso modular não existe")
    return x % m

def teorema_chines_resto(n, a):
    soma = 0
    produto = reduce(operator.mul, n, 1)
    for n_i, a_i in zip(n, a):
        p_i = produto // n_i
        soma += a_i * inverso_modular(p_i, n_i) * p_i
    return soma % produto

def gerar_elemento_de_ordem(r, p):
    h = 1
    while h == 1:
        rand_val = random.randint(2, p - 1)
        h = pow(rand_val, (p - 1) // r, p)
    return h

# --- 3. Execução do Ataque (Com Trata-Erro para quando Bob se Defende) ---

def executar_ataque():
    # Passo A: Fatorar j
    fatores = encontrar_fatores_pequenos(j)
    
    # Passo B: Selecionar fatores até que o produto supere q
    fatores_usados = []
    acumulado = 1
    for r in fatores:
        fatores_usados.append(r)
        acumulado *= r
        if acumulado > q:
            break
            
    # Passo C: Atacar cada subgrupo
    restos = []
    for r in fatores_usados:
        h = gerar_elemento_de_ordem(r, p)
        
        try:
            # Tenta consultar o oráculo de Bob
            m, t = oraculo_do_bob(h)
        except ValueError as e:
            # Se Bob lançar o erro de validação, o ataque é interrompido!
            print(f"  [BLOQUEADO] Bob detectou a chave maliciosa de ordem {r} e encerrou a conexão.")
            raise e
        
        # Força bruta offline no subgrupo
        encontrado = False
        for palpite_v in range(r):
            K_palpite = pow(h, palpite_v, p)
            t_palpite = calcular_mac(K_palpite, m)
            if t_palpite == t:
                restos.append(palpite_v)
                encontrado = True
                break
        if not encontrado:
            raise Exception("Falha ao quebrar subgrupo offline.")
            
    # Passo D: CRT
    chave_reconstruida = teorema_chines_resto(fatores_usados, restos)
    return chave_reconstruida

if __name__ == "__main__":
    print("=================================================================")
    print("DEMONSTRAÇÃO DE ATAQUE VS DEFESA NO DIFFIE-HELLMAN")
    print("=================================================================\n")
    
    # --- CASO 1: SEM VALIDAÇÃO DE SUBGRUPO (SISTEMA VULNERÁVEL) ---
    print("[TESTE 1] Iniciando ataque com a DEFESA DESATIVADA (Bob vulnerável)...")
    validacao_ativa = False
    try:
        chave_rec_vulneravel = executar_ataque()
        print(f"[+] Chave de Bob Real:        {bob_x}")
        print(f"[+] Chave Recuperada:         {chave_rec_vulneravel}")
        if chave_rec_vulneravel == bob_x:
            print("🔴 SUCESSO DO ATACANTE: Bob estava vulnerável e a chave foi completamente roubada!\n")
    except Exception as e:
        print(f"❌ Erro inesperado no teste 1: {e}\n")
        
    print("-" * 65 + "\n")
    
    # --- CASO 2: COM VALIDAÇÃO DE SUBGRUPO (SISTEMA SEGURO) ---
    print("[TESTE 2] Iniciando ataque com a DEFESA ATIVADA (Bob seguro)...")
    validacao_ativa = True
    try:
        chave_rec_segura = executar_ataque()
        print("❌ FALHA NA DEFESA: O atacante de alguma forma conseguiu burlar a validação!")
    except ValueError as e:
        print(f"\n🟢 SUCESSO DA DEFESA: O ataque foi frustrado!")
        print(f"   Motivo da interrupção: {e}")
        print("   Bob validou a chave pública maliciosa, percebeu que ela não pertencia ao")
        print("   subgrupo de ordem prima q, e recusou-se a realizar a operação de MAC.")
        
    print("\n=================================================================")
    try:
        input("[Pressione ENTER para fechar o programa...]")
    except EOFError:
        pass
