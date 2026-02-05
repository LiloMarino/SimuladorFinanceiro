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
- ⚠️ Execução parcial (nem todas as ações podem ser negociadas)

**Exemplo:**
```
Ativo: VALE3
Preço atual: R$ 65,50
Sua ordem: Comprar 100 VALE3 com limite de R$ 65,00
Resultado: Ordem aguarda no livro até VALE3 cair para R$ 65,00 ou menos
```

---

### Diferenças Entre Ordem a Mercado e Ordem Limitada

| Característica | Ordem a Mercado | Ordem Limitada |
|----------------|-----------------|----------------|
| **Execução** | Imediata | Quando preço atingir o limite |
| **Controle de Preço** | Não | Sim |
| **Garantia de Execução** | Alta (se houver liquidez) | Não garantida |
| **Melhor para** | Urgência, ativos líquidos | Controle de preço, estratégia |

---

## Operações Básicas

### Comprar Ações

1. Acesse **Mercado** → **Renda Variável**
2. Procure o ticker desejado (ex: `VALE3`)
3. Clique em **Comprar**
4. Configure:
   - **Quantidade:** Número de ações
   - **Tipo de Ordem:** Mercado ou Limitada
   - **Preço Limite:** (apenas para ordem limitada)
5. Confirme a ordem

### Vender Ações

1. Acesse **Portfólio/Carteira**
2. Encontre o ativo que deseja vender
3. Clique em **Vender**
4. Configure quantidade e tipo de ordem
5. Confirme

### Acompanhar Posições

No **Portfólio**, você pode ver:
- Quantidade de cada ativo
- Preço médio de compra
- Preço atual de mercado
- Lucro/Prejuízo (P&L)
- Percentual de ganho/perda

---

## Estratégias Comuns

### Buy and Hold
Compre e mantenha o investimento por longo prazo. Ideal para quem acredita no crescimento da empresa.

### Day Trade
Compre e venda no mesmo dia simulado. Aproveita volatilidade de curto prazo.

### Swing Trade
Mantém posições por alguns dias/semanas para capturar tendências de médio prazo.

---

## Próximos Passos

- [Renda Fixa](./renda-fixa) - Investimentos de menor risco
- [Carteira](../carteira) - Acompanhe seu portfólio
