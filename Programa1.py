import random
from functools import reduce
import operator

# --- Parâmetros Oficiais do Desafio 57 ---
p = 7199773997391911030609999317773941274322764333428698921736339643928346453700085358802973900485592910475480089726140708102474957429903531369589969318716771
g = 4565356397095740655436854503483826832136106141639563487732438195343690437606117828318042418238184896212352329118608100083187535033402010599512641674644143
q = 236234353446506858198510045061214171961
j = (p - 1) // q

# --- 1. Encontrar Fatores Primos de j < 2^16 ---
def encontrar_fatores_pequenos(n, limite=65536):
    fatores = []
    temp = n
    
    # Testar o fator 2
    if temp % 2 == 0:
        fatores.append(2)
        while temp % 2 == 0:
            temp //= 2        
    # Testar fatores ímpares
    d = 3
    while d < limite and d * d <= temp:
        if temp % d == 0:
            fatores.append(d)
            while temp % d == 0:
                temp //= d
        d += 2
        
    # Se sobrar um fator que também esteja abaixo do limite
    if 1 < temp < limite:
        fatores.append(temp)
        
    return fatores

fatores = encontrar_fatores_pequenos(j)
print(f"[*] Fatores primos encontrados (< 2^16): {fatores}")
print(f"[*] Quantidade de fatores: {len(fatores)}")

# --- 2. Verificar Prerrequisito do CRT ---
produto_fatores = reduce(operator.mul, fatores, 1)
print(f"[*] Produto de todos os fatores: {produto_fatores}")
print(f"[*] Produto é maior que q? {produto_fatores > q}")

# --- 3. Gerar Elementos h de ordem r ---
def gerar_elemento_de_ordem(r, p):
    """
    Gera um elemento h tal que h^r = 1 mod p
    Utiliza h = rand(1, p)^((p-1)/r) mod p
    """
    h = 1
    while h == 1:
        # Escolhe um valor aleatório no grupo multiplicativo
        rand_val = random.randint(2, p - 1)
        h = pow(rand_val, (p - 1) // r, p)
    return h

print("\n--- Exemplos de Geradores h para os primeiros fatores ---")
for r in fatores[:4]:
    h = gerar_elemento_de_ordem(r, p)
    print(f"Para r = {r}:")
    print(f"  h = {h}")
    # Verificação matemática: h^r mod p deve ser igual a 1
    verificacao = pow(h, r, p)
    print(f"  Verificação (h^{r} mod p) = {verificacao}")
    print("-" * 50)