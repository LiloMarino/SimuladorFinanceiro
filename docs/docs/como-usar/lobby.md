---
sidebar_position: 2
---

# Lobby

O lobby é onde você configura os parâmetros da simulação antes de iniciá-la.
É aqui que são definidos tanto os **valores da simulação** quanto **quem tem permissão para controlá-la**.

Esta página explica o que cada campo faz e como eles influenciam a simulação.

Na aba **Expansões** das regras, o host pode ativar [Governo e eleições](governo.md)
para uma partida de ao menos cinco anos. A participação política de cada jogador é opcional.


![O lobby, com as regras da partida e o convite para a sala](/demo/screens/lobby.png)

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

As regras ficam na janela **Regras da partida**, aberta pelo botão **Editar regras** (para quem não é host, **Ver regras**). Os campos são:

### Início

**O que é:**  
A data de início da simulação no histórico de mercado.

**Influência:**

* Define a partir de qual ponto histórico os dados de preços de ativos serão utilizados
* Permite simular diferentes períodos econômicos e cenários históricos
* Dados históricos geralmente disponíveis de 2000 até hoje

---

### Fim

**O que é:**  
A data de término da simulação.

**Influência:**

* Define quando a simulação será encerrada automaticamente
* Deve ser posterior à data inicial

### Alertas de cobertura dos dados

O lobby confere se os dados guardados cobrem o período escolhido. Os alertas aparecem embaixo das ações e também dentro da janela **Regras da partida**, ao lado das datas.

**Alerta vermelho: "Não dá pra começar em" uma data**

Aparece quando CDI, SELIC ou IPCA não tem dado na data inicial. Ex.: uma data inicial em 1970, ou uma base sem indicadores porque o app nunca conseguiu acessar a internet. O alerta diz quais séries não têm dado e, quando existe, a primeira data coberta. Nesse caso, o botão **Iniciar nova simulação** fica desabilitado, e o servidor também recusa a partida.

Para resolver, use **Mudar a data**, ou **Abrir Central de dados** para atualizar os indicadores.

**Alerta amarelo: "Depois de" uma data "não há preço real"**

Aparece quando a data final passa do último dado real de alguma série. O alerta cita a data e as séries que passam a repetir o último valor conhecido, a mesma regra usada para os preços das ações. Ex.: se o último CDI real é de 30/09/2026 e a partida vai até 31/12/2026, o CDI de outubro a dezembro repete o último valor conhecido. O link **Ver séries** abre a Central de dados.

Este alerta é apenas um aviso: a partida continua podendo ser iniciada.

---

### Saldo inicial

**O que é:**  
O capital inicial disponível para cada jogador na simulação.

**Influência:**

* Determina quanto dinheiro você tem disponível para investir no início
* Em multiplayer, todos os jogadores começam com o mesmo valor
* Valores mais altos permitem diversificar mais rapidamente

---

### Aporte mensal

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

O impacto tem quatro modos:

* **Desligado** (padrão): os preços seguem o histórico
* **Realista:** k = 0,02 e T = 20
* **Forte:** k = 0,05 e T = 40
* **Personalizado:** libera os dois campos abaixo

Os campos aparecem no modo **Personalizado**:

* **Intensidade (k):** quanto uma ordem move o preço. Com 0,02, comprar 10% do volume médio diário do ativo sobe o preço cerca de 0,63%
* **Volta ao histórico (T, em pregões):** em quantos pregões o desvio some. Com 20, o desvio some em cerca de um mês

O cálculo está detalhado em [Impacto de preço](/como-usar/investimentos/renda-variavel#impacto-de-preço).

---

### Modo de jogo

**O que é:**
Como a sala compete. É uma regra da partida, e só o host muda, nas regras (**Editar regras › Modo de jogo**).

**Opções:**

* **Todos contra todos** (padrão): cada um por si, vence a melhor carteira.
* **Em equipes:** cada um opera a própria carteira, mas o placar é da equipe e vence a equipe com a melhor média dos membros.

Em equipes:

* Cada jogador escolhe a equipe no próprio card, numa lista de 10 equipes, ao lado da cor. A equipe tem cor própria (escudo e faixa), e a cor do jogador continua sendo a dele.
* Ao ligar o modo, todo mundo começa **sem equipe** e o botão **Iniciar** fica travado. O host tem **Distribuir quem falta**, que põe cada um sem equipe na equipe com menos gente.
* A partida precisa de pelo menos duas equipes. Equipes desiguais valem, com um aviso: a equipe maior não ganha por somar mais, porque o que conta é a **média**.
* O valor da equipe em cada critério de vitória é a média simples dos membros. Quem ainda não tem o valor no critério (ex.: a nota antes de 63 pregões) fica fora daquela média, e a equipe mostra "2 de 3". Se duas equipes empatam, vence a de maior patrimônio médio. Equipe de uma pessoa vale o valor dela.
* **Nome das equipes** muda só o rótulo: pelo nome da cor (Índigo, Carmim, Floresta...) ou pelo número (Equipe 1, Equipe 2...).
* Numa partida salva, quem já jogou não troca de equipe. Quem é novo, ou entra com a partida rodando, escolhe a equipe antes de entrar.
* Voltar para **Todos contra todos** apaga as equipes: nada foi jogado ainda.

---

### Tipo de partida

**O que é:**
Como a partida se decide. A partida pode terminar na data final, decidida pelo critério de vitória, ou quando alguém chega a uma meta de patrimônio. A escolha fica gravada na simulação.

#### Clássica

É o jogo de sempre: a partida vai até a **data final**, e quem vence é decidido pelo [critério de vitória](#critério-de-vitória) escolhido. Esse critério só existe na Clássica: nas outras duas modalidades a vitória vem da meta.

#### Corrida à meta

Vence quem chega primeiro a um **patrimônio-alvo**, a meta. O host escolhe a meta com atalhos de **5×, 10× e 20× o saldo inicial** (o padrão é 10×). Ex.: com saldo inicial de R$ 10.000 e meta de 10×, a meta é R$ 100.000. A meta precisa ser maior que o saldo inicial.

- A partida termina sozinha no dia em que alguém chega à meta.
- Se dois chegam no mesmo dia, vence o maior patrimônio.
- Se ninguém chega até a data final, vence quem ficou mais perto, ou seja, quem tem o maior **% da meta** (patrimônio ÷ meta). Ex.: meta de R$ 100.000 e patrimônio de R$ 62.000 dão 62%, e falta R$ 38.000.

Em equipes, conta a média do patrimônio dos membros: a equipe chega à meta quando a média chega. O aporte mensal continua valendo.

Na **topbar** aparece a trilha da corrida, com um marcador por jogador (ou um escudo por equipe) e o seu percentual. Clicar nela abre a lista. No menu, a página [Meta](./meta.md) mostra o seu progresso e a corrida de todos.

#### Viver de renda

É uma corrida à meta em que a meta é a **independência financeira**: ter um patrimônio que paga a sua despesa do ano retirando só uma fração dele por ano.

**Como a meta é calculada:** meta = 12 × despesa mensal ÷ taxa de retirada.

A **taxa de retirada** é a porcentagem do patrimônio que você tira por ano (padrão 4%, aceita de 1% a 10%). Ex.: despesa de R$ 5.000 por mês são R$ 60.000 por ano. Com taxa de 4%, a meta é R$ 1.500.000 (25× a despesa anual). Com taxa de 3%, a meta sobe para R$ 2.000.000 (cerca de 33× a despesa anual). Taxa menor deixa a meta maior e mais segura.

:::info A regra dos 4%
Ela vem do estudo **Trinity**, feito com dados dos EUA. O estudo viu que retirar 4% do patrimônio no primeiro ano, e corrigir essa retirada pela inflação nos anos seguintes, durou 30 anos na maior parte dos períodos analisados. É uma referência histórica, não uma garantia.
:::

**Sem aporte.** Nesta modalidade o host define o **salário** e a **despesa** mensais (padrão R$ 8.000 e R$ 5.000). No primeiro pregão de cada mês, o salário entra e a despesa sai; a sobra é o que dá para investir. Despesa maior que o salário é permitida, só aparece um aviso.

**Imprevistos.** Eles são sorteados iguais para todos os jogadores, nos mesmos dias. A frequência define quantos imprevistos caem em cada ano:

| Frequência | Quantos por ano |
| --- | --- |
| Nenhum | 0 |
| Raros | 1 |
| Normais (padrão) | 3 |
| Frequentes | 6 |

Os tipos são:

- **Conserto do carro:** 1× a despesa mensal.
- **Despesa de saúde:** 2× a despesa mensal.
- **Demissão:** o salário do mês seguinte não entra.

Cada imprevisto aparece num aviso na tela.

**Caixa negativo.** Se o caixa ficar no negativo, ele cai no **cheque especial**: juros de 8% ao mês, cobrados a cada pregão, até o caixa voltar ao positivo. Ex.: R$ 1.000 no vermelho custam cerca de R$ 80 por mês em juros. Para sair, venda ou resgate algo.

**Correção pelo IPCA (opcional).** O IPCA é o índice oficial de inflação: mede a alta média dos preços para o consumidor. Quando a correção está ligada, uma vez por ano, no aniversário da partida, salário e despesa sobem pela inflação dos 12 meses anteriores, como um reajuste, e a meta sobe junto. Ex.: inflação de 5% no ano faz o salário de R$ 8.000 virar R$ 8.400 e a despesa de R$ 5.000 virar R$ 5.250. Desligada, tudo fica nos reais do início.

**Retorno.** Salário, despesa e imprevistos contam como dinheiro que você colocou ou tirou (o **capital aportado**), e não como ganho ou perda dos investimentos. Já os juros do cheque especial contam como perda.

**A página [Meta](./meta.md)** mostra:

- **Vida financeira:** salário, despesa e sobra do mês, e a **reserva de emergência**, que é quantos meses de despesa o seu caixa cobre. Ex.: despesa de R$ 5.000 e caixa de R$ 15.000 dão uma reserva de 3 meses. Zero é ruim, 3 é razoável e 6 ou mais é confortável.
- **Histórico:** imprevistos, demissões, entrada e saída do cheque especial e os juros de cada mês, com a data na partida e o seu caixa depois de cada evento. Dá para filtrar por tipo.

---

### Critério de vitória

**O que é:**
O que decide quem vence a partida [Clássica](#clássica). Ordena o ranking durante a partida e o pódio do fechamento. Na Corrida à meta e no Viver de renda o campo some: quem vence é quem chega à meta.

**Opções:**

* **Nota geral** (padrão): retorno, risco, consistência e eficiência num número só (ver [Como a nota é calculada](./estatisticas#como-a-nota-é-calculada)). Quem ainda não tem nota, nos primeiros 63 pregões, fica atrás
* **Rentabilidade:** o maior retorno sobre o capital aportado, sem olhar o risco
* **Patrimônio final:** o maior patrimônio no último dia. Com aportes iguais para todos, dá o mesmo resultado que a rentabilidade
* **Índice de Sharpe:** o maior retorno acima do CDI por unidade de oscilação. Premia ganhar sem sobressaltos

Em todos, o retorno desempata. O critério fica gravado na simulação.

---

### Assistências (Modo Especialista)

**O que é:**
Ajudas da interface que já dão a resposta. Ligar o **Modo Especialista** esconde todas e obriga o jogador a fazer as próprias contas. É uma regra da partida: só o host muda, vale para todos da sala, e a pausa e a visão dos outros jogadores seguem como no modo normal.

**Opções** (em **Editar regras › Assistências**):

* **Modo Especialista:** o interruptor esconde todas as ajudas de uma vez. Em **Ajustar uma a uma**, cada ajuda tem o próprio interruptor; com só parte delas escondida, o modo aparece como **Personalizado**
* **Esconder taxa equivalente:** some a coluna e o card **Equivale hoje** (a taxa por ano de cada título, já combinada com CDI e IPCA do dia). A lista de [Renda fixa](./investimentos/renda-fixa) passa a ser ordenada por vencimento
* **Esconder projeção no vencimento:** some o bloco **Quanto R$ X viram no vencimento** e o **Resgate líquido** da boleta de investimento. Ficam a rentabilidade, o vencimento, o IR e a tabela de IR por prazo

Durante a partida, o menu lateral mostra o selo **Especialista** sob o nome da partida. Os números escondidos não saem do servidor, então abrir as ferramentas do navegador não os revela. As ajudas ficam gravadas na simulação, que é retomada com a mesma configuração.

---

### Simulações salvas

O card **Simulações salvas** lista as partidas salvas. Na sala, o host também tem **Escolher partida salva** (e **Trocar partida**, depois de escolher uma). Em cada partida da lista:

* **Resultado** abre a tela de fechamento daquela partida, com o pódio e as estatísticas. Qualquer jogador pode abrir
* **Selecionar** escolhe a partida para continuar, e depois **Continuar** retoma de onde parou. Só o host pode fazer isso. Se a sala não tem vaga para todos os jogadores da partida, o botão vira **Indisponível**

---

### Correlação entre ativos

O card **Correlação entre ativos** mede o quanto os ativos importados andam juntos, em qualquer período com dado. Ver [Correlação entre Ativos](./correlacao).

---

### Comparar simulações

O card **Comparar simulações** põe partidas lado a lado, com o mesmo relatório das [Estatísticas](./estatisticas).

---

### Central de dados

O card **Central de dados** importa ações e atualiza os indicadores. Ver [Importação de Ativos](./importacao-ativos).

---

### Conquistas

O botão **Conquistas** do cabeçalho abre a lista de [Conquistas](./conquistas), com o total já desbloqueado.

---

### Link Compartilhável

**O que é:**  
O cabeçalho do lobby, em **Convide pelo link**, mostra o endereço da sala para compartilhar com outros jogadores.

**Características:**

* Exibe o endereço da rede local (`http://seu-ip:8000`)
* Pode ser copiado com o botão **Copiar**
* Veja mais em [Link Copiável na Interface](/como-usar/multiplayer#link-copiável-na-interface)
