---
sidebar_position: 2
---

# Lobby

O lobby é onde você configura os parâmetros da simulação antes de iniciá-la.
É aqui que são definidos tanto os **valores da simulação** quanto **quem tem permissão para controlá-la**.

Esta página explica o que cada campo faz e como eles influenciam a simulação.


![Exemplo de lobby](/img/lobby.png)

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

### Alertas de cobertura dos dados

O lobby confere se os dados guardados cobrem o período escolhido. Os alertas aparecem embaixo das ações e também dentro da janela **Configurações**, ao lado das datas.

**Alerta vermelho: "Sem indicador na data inicial"**

Aparece quando CDI, SELIC ou IPCA não tem dado na data inicial. Ex.: uma data inicial em 1970, ou uma base sem indicadores porque o app nunca conseguiu acessar a internet. Nesse caso, o botão **Iniciar Nova Simulação** fica desabilitado, e o servidor também recusa a partida.

Para resolver, atualize os indicadores na **Central de dados** (botão no lobby) ou escolha uma data inicial mais recente.

**Alerta amarelo: "Período passa do dado real"**

Aparece quando a data final passa do último dado real de alguma série. O alerta lista cada série com a sua última data real. Depois dessa data, a partida repete o último valor conhecido, a mesma regra usada para os preços das ações. Ex.: se o último CDI real é de 30/09/2026 e a partida vai até 31/12/2026, o CDI de outubro a dezembro repete o último valor conhecido.

Este alerta é apenas um aviso: a partida continua podendo ser iniciada.

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

### Impacto de preço das ordens

**O que é:**  
Liga o deslocamento de preço causado pelas ordens dos jogadores. Desligado, os preços seguem exatamente o histórico.

**Influência:**

* Uma compra empurra o preço do ativo para cima nos pregões seguintes, e uma venda empurra para baixo
* O desvio volta sozinho ao preço histórico se ninguém operar de novo naquele ativo
* Vale para todos os jogadores: a ordem de um move o preço que os outros veem
* Fica gravado na simulação, então ela é retomada com a mesma configuração

Ao ligar, aparecem dois campos:

* **Intensidade (k):** quanto uma ordem move o preço. Com o padrão 0,02, comprar 10% do volume médio diário do ativo sobe o preço cerca de 0,63%
* **Volta ao histórico (T):** em quantos pregões o desvio some. O padrão é 20 (cerca de um mês)

O cálculo está detalhado em [Impacto de preço](/como-usar/investimentos/renda-variavel#impacto-de-preço).

---

### Link Compartilhável

**O que é:**  
Link gerado automaticamente para compartilhar a sessão com outros jogadores.

**Características:**

* Exibe o endereço local (`http://seu-ip:8000`) ou túnel público se configurado
* Pode ser copiado com um clique
* Veja mais em [Link Copiável na Interface](/como-usar/multiplayer#link-copiável-na-interface)
