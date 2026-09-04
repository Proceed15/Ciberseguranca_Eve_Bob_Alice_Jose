# Guia de Execução desse Laboratório Prático de Cibersegurança:

## Ataques de Confinamento de Subgrupo e Mitigações no Diffie-Hellman:

Este guia fornece as instruções detalhadas passo a passo para executar os quatro componentes independentes do seu laboratório de testes criptográficos. A arquitetura utiliza sockets TCP locais para simular de forma realista uma rede com três agentes: **Alice (Cliente Legítimo)**, **Bob (Servidor/Alvo)** e **Eve (Atacante)**.

---

## Pré-requisitos:
* **Python 3.8+** instalado no sistema operacional.
* Apenas bibliotecas nativas do Python são utilizadas (`socket`, `random`, `hmac`, `hashlib`, `reduce`, `operator`), garantindo compatibilidade imediata sem necessidade de `pip install`.

---

## Arquitetura dos Arquivos:

O laboratório é composto pelos seguintes programas na Pasta "VersaoAtual":
1. `bob_vulnerable.py` (Servidor vulnerável operando na porta TCP **8080**)
2. `bob_secure.py` (Servidor seguro operando na porta TCP **8081**)
3. `alice_legitimate.py` (Cliente legítimo que realiza a troca de chaves padrão)
4. `eve_attacker.py` (Cliente malicioso que realiza a criptoanálise ativa)

---

## Protocolo de Execução Passo a Passo:

Para realizar a simulação ao vivo de forma dramática e didática, recomenda-se abrir **4 janelas de terminal (Prompt de Comando ou PowerShell no Windows)** lado a lado na tela.

### Passo 1: Inicializar os Servidores (Bob):
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

### Passo 2: Testar Comunicação Legítima (Alice → Bob):
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

### Passo 3: Executar o Ataque (Eve → Bob Vulnerável):
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

### Passo 4: Testar a Resiliência da Defesa (Eve → Bob Seguro):
Por fim, demonstre como as contramedidas criptográficas neutralizam o ataque completamente de início.

* **No Terminal 4 (Eve Atacante):**
  1. Execute o script novamente: `python eve_attacker.py`
  2. Digite `8081` e pressione **Enter**.
  3. *Observe o bloqueio imediato:*
     * Eve tenta enviar a primeira chave maliciosa (de ordem 2).
     * No Terminal 2 (Bob Seguro), aparecerá uma mensagem de aviso de que uma chave inválida fora do subgrupo de ordem $q$ foi detectada e a conexão foi rejeitada.
     * No Terminal 4 (Eve), o programa reportará falha na conexão e explicará matematicamente que o ataque foi mitigado.

---

### Passo 5: Finalização dos Servidores:
Para encerrar os servidores de forma limpa nos Terminais 1 e 2:
1. Vá até o terminal correspondente.
2. Na pergunta `Do you want to stop the server? (yes/no):`, digite `yes` e pressione **Enter** (ou pressione `Ctrl + C`).

---
## Referências

1. Artigo Científico Principal (Estudo de Caso e Medições)
VALENTA, Luke; ADRIAN, David; SANSO, Antonio; COHNEY, Shaanan; FRIED, Joshua; HASTINGS, Marcella; HALDERMAN, J. Alex; HENINGER, Nadia. Measuring Small Subgroup Attacks Against Diffie-Hellman. In: Proceedings of the 24th Annual Network and Distributed System Security Symposium (NDSS). San Diego, CA, EUA, 2017.
Nota: Este artigo também está registrado no repositório de pesquisas criptográficas como: IACR Cryptology ePrint Archive, Report 2016/995.
2. Desafio Prático de Criptoanálise
THE CRYPTOPALS CRYPTOGRAPHY CHALLENGES. Challenge 57: Diffie-Hellman Revisited (Set 8). Disponível em: https://cryptopals.com/sets/8/challenges/57. Acesso em: set. 2026.
3. Normas de Segurança e Recomendações de Mitigação
GILLMOR, Daniel. Negotiated Finite Field Diffie-Hellman Ephemeral Groups for Transport Layer Security (TLS). RFC 7919, Internet Engineering Task Force (IETF), 2016. Disponível em: https://datatracker.ietf.org/doc/html/rfc7919.
Nota: Esta é a especificação que padronizou os grupos de Diffie-Hellman seguros e a obrigatoriedade de validação para mitigar os ataques discutidos no artigo de Valenta et al.
4. Fundamentação Teórica (Ataques de Confinamento e Primos de Lim-Lee)
LIM, Chae Hoon; LEE, Pil Joong. A Key Recovery Attack on Discrete Log-based Schemes using a Small Subgroup. In: Advances in Cryptology — EUROCRYPT '97. Springer, Berlin, Heidelberg, 1997, p. 249-263.
Nota: Este é o artigo seminal que propôs originalmente a matemática dos ataques em subgrupos pequenos utilizando parametrização de chaves públicas maliciosas.
