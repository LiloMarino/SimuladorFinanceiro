---
sidebar_position: 1
---

# Renda Variável

Aprenda a investir em ações, FIIs e ETFs no simulador.

![Exemplo de tela de renda variável](/img/renda-variavel.png)

## O que é Renda Variável?

**Renda Variável** são investimentos cujo retorno não é fixo e varia conforme o desempenho do mercado. No Brasil, os principais ativos de renda variável são:

- **Ações:** Partes de uma empresa negociadas na bolsa (ex: VALE3, PETR4, BBAS3)
- **FIIs (Fundos Imobiliários):** Fundos que investem em imóveis ou títulos imobiliários (ex: XPML11, HGLG11)
- **ETFs (Exchange Traded Funds):** Fundos que replicam índices de mercado (ex: BOVA11 replica o Ibovespa)

**Características:**
- 💹 Retorno varia conforme mercado
- 📊 Maior potencial de ganho
- ⚠️ Maior risco (volatilidade)
- 💰 Possibilidade de dividendos/proventos

<!-- Espaço reservado para screenshot da tela de renda variável -->

---

## Sistema de Ordens

O simulador utiliza um sistema realista de ordens para compra e venda de ativos de renda variável.

![Exemplo de tela de ordens](/img/ordens.png)

### Tipos de Ordem

#### Ordem a Mercado

Uma **ordem a mercado** é executada imediatamente ao **melhor preço disponível** no momento.

**Quando usar:**
- Quando você quer garantir a execução imediata
- Quando o preço não é tão importante quanto a velocidade
- Em ativos com alta liquidez

**Como funciona:**
1. Você coloca uma ordem de compra/venda a mercado
2. O sistema busca a melhor oferta disponível no livro de ofertas
3. A ordem é executada instantaneamente ao preço da melhor oferta

**Vantagens:**
- ✅ Execução garantida (se houver liquidez)
- ✅ Imediata

**Desvantagens:**
- ⚠️ Você não controla o preço exato
- ⚠️ Pode ser executada a um preço pior que o esperado em ativos com baixa liquidez

**Exemplo:**
```
Ativo: VALE3
Melhor oferta de venda: R$ 65,50
Sua ordem: Comprar 100 VALE3 a mercado
Resultado: Compra executada a R$ 65,50 (ou próximo)
```

---

#### Ordem Limitada

Uma **ordem limitada** só é executada se o preço atingir o valor **especificado por você** (ou melhor).

**Quando usar:**
- Quando você quer controlar o preço máximo de compra (ou mínimo de venda)
- Quando você não tem pressa e pode esperar o preço ideal
- Para aproveitar movimentos de preço específicos

**Como funciona:**
1. Você especifica um preço limite
2. A ordem fica no livro de ofertas aguardando
3. Só é executada quando há uma contrapartida ao seu preço (ou melhor)

**Vantagens:**
- ✅ Controle total sobre o preço
- ✅ Pode conseguir preços melhores
- ✅ Não há surpresas

**Desvantagens:**
- ⚠️ Pode nunca ser executada se o preço não for atingido
- ⚠️ Pode ser executada apenas parcialmente, deixando você com uma posição incompleta

:::info
**Execução parcial** significa que apenas parte da quantidade solicitada é negociada.

Exemplo:  
Você envia uma ordem para comprar 100 ações a R$ 10,00, mas só existem 30 ações disponíveis nesse preço.  
Resultado: você compra 30 ações e as outras 70 ficam aguardando no livro de ofertas.

Isso pode exigir ajustes manuais e impactar sua estratégia.
:::

**Exemplo:**
```
Ativo: VALE3
Preço atual: R$ 65,50
Sua ordem: Comprar 100 VALE3 com limite de R$ 65,00
Resultado: Ordem aguarda no livro até VALE3 cair para R$ 65,00 ou menos
```

---

### Diferenças Entre Ordem a Mercado e Ordem Limitada

| Característica           | Ordem a Mercado           | Ordem Limitada                |
| ------------------------ | ------------------------- | ----------------------------- |
| **Execução**             | Imediata                  | Quando preço atingir o limite |
| **Controle de Preço**    | Não                       | Sim                           |
| **Garantia de Execução** | Alta (se houver liquidez) | Não garantida                 |
| **Melhor para**          | Urgência, ativos líquidos | Controle de preço, estratégia |

---

### Impacto de Preço

Quando o host liga o **Impacto de preço das ordens** no [lobby](/como-usar/lobby#impacto-de-preço-das-ordens), as ordens dos jogadores passam a mover o preço dos pregões seguintes, como no mercado real: comprar muito de um ativo pouco negociado encarece esse ativo. Desligado, os preços seguem exatamente o histórico.

**Quanto o preço se move:**

```
impacto = k × √(quantidade líquida do dia ÷ volume médio diário)
```

- **Quantidade líquida do dia:** compras menos vendas de todos os jogadores naquele ativo, naquele dia. Comprar sobe o preço; vender desce.
- **Volume médio diário:** a média de ações negociadas por dia nos últimos 20 pregões. Serve de régua: 1.000 ações é muito para um ativo que negocia 5.000 por dia e quase nada para um que negocia 50 milhões.
- **k (intensidade):** configurado no lobby; o padrão é 0,02, próximo do que se mede no mercado real.

Exemplos com k = 0,02 num ativo com volume médio de 1.000.000 de ações por dia:

| Compra no dia | Parcela do volume médio | Preço no pregão seguinte |
| ------------- | ----------------------- | ------------------------ |
| 100 ações     | 0,01%                   | +0,02%                   |
| 100.000 ações | 10%                     | +0,63%                   |
| 1.000.000     | 100%                    | +2,00%                   |

A raiz quadrada faz o impacto crescer menos que a ordem: quadruplicar a compra só dobra o impacto. E como a conta usa o total do dia, dividir uma ordem em várias menores no mesmo dia dá o mesmo resultado; se um jogador vende para outro a mesma quantidade, uma ordem anula a outra.

**Como o preço volta ao histórico:**

A ordem não mexe no preço do próprio dia, onde o custo dela já aparece ao consumir as ofertas do livro. O impacto vale cheio no pregão seguinte e diminui pela curva (1 − t/T)², em que t conta os pregões a partir desse primeiro (que tem t = 0) e T é o valor configurado no lobby (padrão 20):

| Pregão depois da ordem | 1º   | 5º  | 10º | 15º | 20º  | 21º |
| ---------------------- | ---- | --- | --- | --- | ---- | --- |
| Impacto que resta      | 100% | 64% | 30% | 9%  | 0,3% | 0%  |

Impactos de dias diferentes se somam, cada um sumindo no seu ritmo. Se ninguém operar mais o ativo, o preço converge de volta ao histórico: o efeito de uma ordem dura T pregões.

O preço com impacto é o mesmo em toda a simulação: na lista de ativos, no gráfico, no livro de ofertas, na carteira e no ranking.

---

## Operações Básicas

### Abrir um ativo e enviar ordens

1. Acesse **Renda Variável** para ver a lista de ativos.
2. Encontre o ticker desejado e clique em **Ver**.
3. Na tela de detalhes do ativo, use o card **Nova Ordem** para:
   - Escolher **Tipo de Operação**: Compra ou Venda.
   - Escolher **Tipo de Ordem**: À Mercado ou Limitada.
   - Informar a **Quantidade** (use **Máx** para preencher o limite disponível).
   - Informar **Preço desejado** quando a ordem for **Limitada**.
4. Clique em **Executar Compra** ou **Executar Venda**.

### Vender ações

A venda é feita no mesmo card **Nova Ordem**. Ao selecionar **Venda**, o botão **Máx** considera apenas a quantidade que você já possui na posição.

### Acompanhar posição e ordens

Na tela de detalhes do ativo, você encontra:
- **Resumo**: quantidade em carteira, preço médio, preço atual, saldo em conta e P&L.
- **Ordens Pendentes**: lista de ordens abertas, com status e opção de cancelar quando estiverem pendentes.

---

## Estratégias Comuns Suportadas

### Buy and Hold
Compre e mantenha o investimento por longo prazo. Ideal para quem acredita no crescimento da empresa.

### Swing Trade
Mantém posições por alguns dias/semanas para capturar tendências de médio prazo.

---

## Próximos Passos

- [Renda Fixa](./renda-fixa) - Investimentos de menor risco
- [Carteira](../carteira) - Acompanhe seu portfólio
