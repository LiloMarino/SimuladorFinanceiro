---
sidebar_position: 1
---

# Renda Variável

Aprenda a investir em ações, FIIs e ETFs no simulador.

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
