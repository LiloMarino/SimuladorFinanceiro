---
sidebar_position: 2
---

# Renda Fixa

Aprenda a investir em títulos de renda fixa no simulador.

![Exemplo de tela de renda fixa](/img/renda-fixa.png)

## O que é Renda Fixa?

**Renda Fixa** são investimentos em que você empresta dinheiro e recebe de volta o valor inicial mais juros.
As **regras de remuneração são definidas no momento do investimento**, o que torna esse tipo de ativo mais previsível do que a renda variável.

**Características:**
- 💰 Regras de retorno conhecidas
- 📉 Menor volatilidade que renda variável
- 🛡️ Menor risco de mercado
- 📅 Prazos definidos ou estimáveis

<!-- Espaço reservado para screenshot da tela de renda fixa -->

## Tipos de Renda Fixa

No simulador, esses ativos seguem as mesmas **regras básicas de funcionamento e tributação** do mundo real, permitindo testar estratégias e entender os efeitos do tempo, da taxa e do Imposto de Renda.

---

### CDB (Certificado de Depósito Bancário)

**O que é:**
Um CDB é um título emitido por bancos para captar recursos. Ao investir, você está emprestando dinheiro ao banco, que se compromete a devolver o valor investido acrescido de juros.

**Características no mundo real:**

* Emitido por bancos comerciais
* Pode ser **prefixado**, **pós-fixado** (ex: % do CDI) ou híbrido
* Pode ter liquidez diária ou vencimento definido
* Conta com proteção do **FGC (Fundo Garantidor de Créditos)** até R$ 250.000 por CPF e por instituição financeira, respeitando o limite global do FGC.
* **Tributação:** Imposto de Renda regressivo sobre os rendimentos

**No simulador:**

* Você pode investir em CDBs de diferentes bancos
* A rentabilidade varia conforme o banco e o prazo
* O IR é aplicado automaticamente conforme o tempo de permanência

---

### LCI (Letra de Crédito Imobiliário)

**O que é:**
A LCI é um título emitido por bancos para financiar o setor imobiliário. Os recursos captados são direcionados para empréstimos e financiamentos imobiliários.

**Características no mundo real:**

* Lastreada em operações do setor imobiliário
* **Isenta de Imposto de Renda para pessoa física**
* Geralmente possui **prazo mínimo de carência** (não pode ser resgatada antes)
* Protegida pelo **FGC até R$ 250.000**

**No simulador:**

* Apresenta rentabilidade nominal menor que CDBs equivalentes
* Pode gerar **retorno líquido competitivo** por conta da isenção de IR
* Ideal para simular estratégias focadas em eficiência tributária

---

### LCA (Letra de Crédito do Agronegócio)

**O que é:**
A LCA funciona de forma semelhante à LCI, mas os recursos captados são destinados ao financiamento do agronegócio.

**Características no mundo real:**

* Lastreada em operações do setor agrícola
* **Isenta de Imposto de Renda para pessoa física**
* Normalmente possui prazo mínimo de carência
* Protegida pelo **FGC até R$ 250.000**

**No simulador:**

* Comportamento similar ao da LCI
* Permite comparar estratégias entre ativos tributados e isentos
* Útil para observar o impacto do IR no longo prazo

---

### Tesouro Direto

**O que é:**
São títulos públicos emitidos pelo **Governo Federal** para financiar a dívida pública. Ao investir, você empresta dinheiro ao governo.

**Características no mundo real:**

* Considerados os investimentos de **menor risco de crédito** no Brasil
* Possuem liquidez diária, mas o valor de venda pode variar antes do vencimento devido à marcação a mercado.
* **Tributação:** Imposto de Renda regressivo sobre os rendimentos
* Podem sofrer marcação a mercado

**Principais tipos:**

* **Tesouro Selic:** acompanha a taxa Selic (baixo risco de oscilação)
* **Tesouro Prefixado:** taxa fixa definida na compra
* **Tesouro IPCA+:** inflação (IPCA) + taxa fixa, protegendo o poder de compra

**No simulador:**

* Cada tipo segue sua lógica de rentabilidade
* O IR é aplicado conforme o tempo de investimento
* Ideal para testar cenários de curto, médio e longo prazo

---

## Tributação – Imposto de Renda

No Brasil, a maioria dos investimentos de renda fixa é tributada pelo **Imposto de Renda regressivo**, onde a alíquota diminui conforme o tempo que o dinheiro permanece investido.

### Tabela de IR Regressivo

| Prazo do investimento | Alíquota |
| --------------------- | -------- |
| Até 180 dias          | 22,5%    |
| 181 a 360 dias        | 20%      |
| 361 a 720 dias        | 17,5%    |
| Acima de 720 dias     | 15%      |

* O imposto incide **somente sobre os rendimentos**, não sobre o valor total investido.
* **LCI e LCA são isentas de IR** para pessoa física, o que pode torná-las mais vantajosas mesmo com taxas menores.

---

## Prefixado vs Pós-fixado

### Prefixado

**O que é:** A taxa de retorno é definida no momento da contratação.

**Exemplo:** CDB prefixado de 10% ao ano
- Se você investir R$ 10.000, sabe que terá R$ 11.000 ao final de 1 ano (antes de IR e considerando que o investimento seja mantido até o vencimento)

**Vantagens:**
- ✅ Previsibilidade total
- ✅ Ideal quando você acredita que os juros vão cair

**Desvantagens:**
- ⚠️ Se os juros subirem, você perde rentabilidade relativa
- ⚠️ Pode ter perda em resgate antecipado (marcação a mercado)

---

### Pós-fixado

**O que é:** A taxa de retorno acompanha um índice (geralmente CDI ou Selic).

**Exemplo:** CDB pós-fixado de 100% do CDI
- Se o CDI estiver em 10% ao ano, você ganha 10% ao ano
- Se o CDI subir para 12%, você passa a ganhar 12%

**Vantagens:**
- ✅ Acompanha variações da economia
- ✅ Proteção contra alta de juros

**Desvantagens:**
- ⚠️ Não sabe exatamente quanto vai ganhar
- ⚠️ Se juros caírem, rentabilidade diminui

---

### Inflação (IPCA+)

**O que é:** Rentabilidade = Inflação (IPCA) + taxa prefixada.

**Exemplo:** Tesouro IPCA+ 2030 com taxa de IPCA + 5% ao ano
- Se a inflação for 4%, você ganha 9% (4% + 5%)
- Se a inflação for 6%, você ganha 11% (6% + 5%)

**Vantagens:**
- ✅ Protege seu poder de compra
- ✅ Ideal para longo prazo

**Desvantagens:**
- ⚠️ Rentabilidade pode ser baixa se a inflação estiver baixa
- ⚠️ Pode ter perda em resgate antecipado (marcação a mercado)


---

## Como o rendimento é calculado

No simulador, CDI, SELIC e IPCA são as **taxas reais publicadas pelo Banco Central**, e não números fixos. Cada título rende com a taxa do dia (ou do mês) em que o dinheiro estava aplicado.

### CDI e SELIC (taxa por dia)

Essas taxas são publicadas **por dia**, em % ao dia. Ex.: uma taxa de 0,0551% em um dia faz R$ 1.000 virarem R$ 1.000,55 na noite.

- Um título de **110% do CDI** rende 1,1 vez a taxa do dia. Ex.: 1,1 × 0,0551% = 0,06061% naquele dia.
- A taxa de um dia útil vale para a noite até o próximo dia útil. O fim de semana não conta: a taxa da sexta-feira rende uma única vez, de sexta para segunda.
- Em **feriados** (dias em que o Banco Central não publica CDI nem SELIC), o título não rende nada.

### IPCA (taxa por mês)

O IPCA é publicado **por mês**, em % ao mês. O simulador espalha a inflação de cada mês pelos dias úteis daquele mês, de forma que o mês inteiro soma exatamente a inflação publicada. Ex.: se o IPCA do mês é 0,5%, um título atrelado ao IPCA rende 0,5% no mês inteiro.

Títulos **IPCA+** e **SELIC+** somam uma parte fixa (o *spread*, combinado na compra) por cima do índice. Ex.: IPCA + 5% a.a. (a.a. quer dizer "ao ano") rende a inflação do período mais 5% ao ano, proporcionalmente ao tempo.

### Depois do último dado real

Depois do último dia com dado real, o simulador repete o último valor conhecido. É a mesma regra usada para os preços das ações.

### Projeção na compra

Ao comprar, a projeção mostrada assume que o indexador (CDI, SELIC ou IPCA) continua no valor que se conhece no dia da compra. Como essas taxas mudam com o tempo, o resultado real pode ser diferente.

### Exemplo conferido

Um CDB de 100% do CDI comprado em 02/01/2020 e resgatado em 31/12/2020 rende **2,750141%** antes do IR. Ou seja, R$ 1.000 viram R$ 1.027,50 antes do imposto. Esse é exatamente o resultado da "Calculadora do Cidadão", do Banco Central, para o mesmo período.

---

## Como Funciona no Simulador

### Investir em Renda Fixa

1. Acesse **Renda Fixa** para ver a lista de ativos disponíveis.
2. No card do ativo, clique em **Adicionar** para abrir os detalhes.
3. Em **Investir neste ativo**, informe o **Valor do investimento** (use **MÁX** para preencher o limite do saldo).
4. Clique em **Investir agora**.

### Simulação e detalhes do investimento

Na tela de detalhes do ativo, você acompanha:
- **Resumo da Operação** com valor investido, rendimento bruto, imposto (IR) e valor de resgate projetado.
- **Detalhamento do cálculo** e **Tabela de IR** para entender a projeção até o vencimento.

### Acompanhar investimentos

1. Acesse **Carteira**.
2. Veja seus investimentos em **Renda Fixa** na tabela da carteira.
3. Clique em **Detalhes** para retornar à tela do ativo.

:::warning Atenção ao IR
O simulador calcula automaticamente e desconta o Imposto de Renda sobre o resgate, seguindo a tabela regressiva.
:::

---

## Estratégias Comuns

### Reserva de Emergência
Use Tesouro Selic ou CDBs com liquidez diária para ter dinheiro acessível rapidamente.

### Objetivo de Médio/Longo Prazo
Use prefixados ou IPCA+ para objetivos futuros (casa, aposentadoria).

### Diversificação
Combine renda fixa e variável para equilibrar risco e retorno do portfólio.

---

## Próximos Passos

- [Renda Variável](./renda-variavel) - Investimentos de maior risco/retorno
- [Carteira](../carteira) - Acompanhe todo seu portfólio
