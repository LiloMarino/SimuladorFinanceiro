---
sidebar_position: 4
---

# Lobby

O lobby é onde você configura os parâmetros da simulação antes de iniciá-la.
É aqui que são definidos tanto os **valores da simulação** quanto **quem tem permissão para controlá-la**.

Esta página explica o que cada campo faz e como eles influenciam a simulação.

---

## Configuração do Host (Obrigatória)

Antes de qualquer simulação — **singleplayer ou multiplayer** — é obrigatório configurar corretamente o **host**.

:::warning Atenção
O host **não é definido automaticamente**  
e **não é necessariamente quem está hospedando o servidor**.
:::

O host funciona como um **administrador da simulação**:

- pode iniciar a simulação
- pode configurar a simulação
- controla a simulação

Se o host não estiver corretamente configurado, a simulação **não poderá ser iniciada**, mesmo simulando sozinho.

---

### O que o Host é (e o que ele NÃO é)

**O host é:**
- Um **papel lógico** dentro da simulação
- Um **admin da sessão**
- Definido manualmente no `config.toml`

**O host NÃO é:**
- Automaticamente quem roda o servidor
- Automaticamente quem cria a sala
- Um conceito exclusivo do multiplayer

👉 Justamente por isso ele precisa ser configurado manualmente.

---

### Como configurar o Host

No arquivo `config.toml`, defina o nickname do host:

```toml
[host]
nickname = "host"
````

Esse nickname deve ser **exatamente o mesmo utilizado pelo jogador** no lobby.

---

### Como funciona internamente

1. O jogador entra no lobby com um nickname.
2. O backend compara esse nickname com `host.nickname` definido no `config.toml`.
3. Se forem diferentes, ações administrativas são bloqueadas.

Essas ações incluem:

* iniciar simulação
* controlar a simulação
* alterar configurações

---

## Campos de Configuração

O formulário do lobby possui os seguintes campos:

### Data Inicial

**O que é:**  
A data de início da simulação no histórico de mercado.

**Influência:**

* Define a partir de qual ponto histórico os dados de preços de ativos serão utilizados
* Permite simular diferentes períodos econômicos e cenários históricos
* Dados históricos geralmente disponíveis de 2000 até hoje

---

### Data Final

**O que é:**  
A data de término da simulação.

**Influência:**

* Define quando a simulação será encerrada automaticamente
* Deve ser posterior à data inicial

---

### Saldo Inicial (R$)

**O que é:**  
O capital inicial disponível para cada jogador na simulação.

**Influência:**

* Determina quanto dinheiro você tem disponível para investir no início
* Em multiplayer, todos os jogadores começam com o mesmo valor
* Valores mais altos permitem diversificar mais rapidamente

---

### Aporte Mensal (R$)

**O que é:**  
Valor adicionado automaticamente ao saldo todo mês simulado.

**Influência:**

* Simula aportes recorrentes 
* Em multiplayer, todos os jogadores recebem o mesmo valor mensalmente
* Pode ser configurado como R$ 0 se não desejar aportes

---

### Link Compartilhável

**O que é:**  
Link gerado automaticamente para compartilhar a sessão com outros jogadores.

**Características:**

* Exibe o endereço local (`http://seu-ip:8000`) ou túnel público se configurado
* Pode ser copiado com um clique
* Veja mais em [Link Copiável na Interface](/como-usar/multiplayer#link-copiável-na-interface)
