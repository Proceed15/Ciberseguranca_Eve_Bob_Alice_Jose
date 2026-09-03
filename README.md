# Guia de Execução: Laboratório Prático de Cibersegurança
## Ataques de Confinamento de Subgrupo e Mitigações no Diffie-Hellman

Este guia fornece as instruções detalhadas passo a passo para executar os quatro componentes independentes do seu laboratório de testes criptográficos. A arquitetura utiliza sockets TCP locais para simular de forma realista uma rede com três agentes: **Alice (Cliente Legítimo)**, **Bob (Servidor/Alvo)** e **Eve (Atacante)**.

---

## Pré-requisitos
* **Python 3.8+** instalado no sistema operacional.
* Apenas bibliotecas nativas do Python são utilizadas (`socket`, `random`, `hmac`, `hashlib`, `reduce`, `operator`), garantindo compatibilidade imediata sem necessidade de `pip install`.

---

## Arquitetura dos Arquivos

O laboratório é composto pelos seguintes programas:
1. `bob_vulnerable.py` (Servidor vulnerável operando na porta TCP **8080**)
2. `bob_secure.py` (Servidor seguro operando na porta TCP **8081**)
3. `alice_legitimate.py` (Cliente legítimo que realiza a troca de chaves padrão)
4. `eve_attacker.py` (Cliente malicioso que realiza a criptoanálise ativa)

---

## Protocolo de Execução Passo a Passo

Para realizar a simulação ao vivo de forma dramática e didática, recomenda-se abrir **4 janelas de terminal (Prompt de Comando ou PowerShell no Windows)** lado a lado na tela.

### Passo 1: Inicializar os Servidores (Bob)
Nos dois primeiros terminais, coloque os servidores do Bob no ar. Eles permanecerão em execução em loop, aguardando conexões.

* **No Terminal 1 (Bob Vulnerável):**
  ```bash
  python bob_vulnerable.py
  ```
  *O console exibirá que o Bob Vulnerável gerou sua chave privada `x` e está escutando na porta `8080`.*

* **No Terminal 2 (Bob Seguro):**
  ```bash
  python bob_secure.py
  ```
  *O console exibirá que o Bob Seguro gerou sua chave privada `x` e está escutando na porta `8081`.*

---

### Passo 2: Testar Comunicação Legítima (Alice → Bob)
Neste teste, você demonstrará que a proteção de segurança não quebra a usabilidade de clientes honestos que seguem o protocolo corretamente.

* **No Terminal 3 (Alice Legítima):**
  ```bash
  python alice_legitimate.py
  ```
  1. O programa perguntará: `Enter Bob's server port (8080 for Vulnerable, 8081 for Secure):`
  2. Digite `8080` e pressione **Enter**.
  3. *Verifique que a conexão foi bem-sucedida, o segredo foi compartilhado e o MAC foi validado.*
  
* **No mesmo Terminal 3 (Alice Legítima):**
  1. Execute o script novamente: `python alice_legitimate.py`
  2. Digite `8081` e pressione **Enter**.
  3. *Verifique que Alice também se conecta com sucesso ao Bob Seguro, pois a chave pública dela pertence ao subgrupo correto.*

---

### Passo 3: Executar o Ataque (Eve → Bob Vulnerável)
Agora você demonstrará o ataque de confinamento de subgrupo sendo bem-sucedido contra o alvo desprotegido.

* **No Terminal 4 (Eve Atacante):**
  ```bash
  python eve_attacker.py
  ```
  1. O programa perguntará: `Enter the target port to attack (8080 or 8081):`
  2. Digite `8080` e pressione **Enter**.
  3. *Observe o ataque em tempo real:*
     * Eve descobre dinamicamente os fatores primos de $j$.
     * Eve gera chaves maliciosas de ordem pequena ($h$) e as envia.
     * Bob Vulnerável responde com os MACs sem validar as chaves.
     * Eve quebra os resíduos módulo $r_i$ offline em milissegundos.
     * O Teorema Chinês do Resto (CRT) é executado e imprime a chave privada roubada, idêntica à chave real de Bob exibida no Terminal 1!

---

### Passo 4: Testar a Resiliência da Defesa (Eve → Bob Seguro)
Por fim, demonstre como as contramedidas criptográficas neutralizam o ataque completamente de início.

* **No Terminal 4 (Eve Atacante):**
  1. Execute o script novamente: `python eve_attacker.py`
  2. Digite `8081` e pressione **Enter**.
  3. *Observe o bloqueio imediato:*
     * Eve tenta enviar a primeira chave maliciosa (de ordem 2).
     * No Terminal 2 (Bob Seguro), aparecerá uma mensagem de aviso de que uma chave inválida fora do subgrupo de ordem $q$ foi detectada e a conexão foi rejeitada.
     * No Terminal 4 (Eve), o programa reportará falha na conexão e explicará matematicamente que o ataque foi mitigado.

---

### Passo 5: Finalização dos Servidores
Para encerrar os servidores de forma limpa nos Terminais 1 e 2:
1. Vá até o terminal correspondente.
2. Na pergunta `Do you want to stop the server? (yes/no):`, digite `yes` e pressione **Enter** (ou pressione `Ctrl + C`).

---

## Conceitos Criptográficos Demonstrados na Apresentação

Ao apresentar este laboratório, certifique-se de associar as execuções de tela aos conceitos teóricos:

1. **Ausência de Validação de Subgrupos:** Mostre no Terminal 1 que o Bob Vulnerável calcula segredos compartilhados para qualquer entrada, o que viola as diretrizes do padrão DSA e abre margem para o ataque de confinamento (Lim-Lee).
2. **Algoritmo de Pohlig-Hellman Simplificado:** Explique que a Eve encontra cada resto da chave privada resolvendo logaritmos discretos em subgrupos de ordem muito pequena de forma exaustiva offline.
3. **Teorema Chinês do Resto (CRT):** Destaque como Eve utiliza o Algoritmo de Euclides Estendido para juntar os restos fracionados módulo $r_i$ e reconstruir o segredo completo.
4. **Validação de Subgrupo Ativa:** Destaque no Terminal 2 que a contramedida de Bob valida se a entrada $y$ satisfaz:
   * $1 < y < p-1$
   * $y^q \equiv 1 \pmod p$
   Isso garante matematicamente que $y$ pertence ao subgrupo cíclico seguro de ordem prima $q$, mitigando o ataque na origem.
