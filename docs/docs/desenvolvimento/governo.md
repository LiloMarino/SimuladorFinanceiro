---
sidebar_position: 13
---

# Expansão de governo

O domínio está em `backend/features/government`: `politics.py` faz transições
determinísticas por data, `economy.py` calcula contrafactuais e `runtime.py` integra
o motor, as rotas e o livro de ofertas. As três rotas são `GET /api/government`,
`POST /api/government/actions` e `POST /api/government/preview`.

## Estado, transações e datas

As regras de criação ficam em `simulations.government_rules`. Partidas antigas
recebem `{}` e mantêm a expansão desligada. Ao iniciar, perfis empresariais são
copiados para o estado da partida: alterações posteriores no cadastro de setores
não reescrevem a economia já simulada.

Cada transição gera um registro imutável em `government_event`, com revisão única
por partida e o resultado completo. Sorteios de pesquisa, eleição e Congresso
derivam de SHA-256 da semente da partida e da identidade do evento. Retomar carrega
os resultados persistidos; não sorteia nem cobra novamente dias já processados.

O lock da simulação cobre tick, consultas e comandos. A persistência também trava
a linha da partida e verifica a revisão esperada. O evento político e os fluxos
`CAMPAIGN` são gravados na mesma transação. `request_id`, UUID por comando, impede
que uma repetição de rede cobre outra doação. Gastos políticos têm sinal negativo
no caixa e não são tratados como retiradas de capital ao calcular rentabilidade.

O runtime percorre as datas corridas entre pregões, processando abertura/fechamento
mensal, turnos, posse, reuniões autônomas e vigências. Uma medida aprovada não muda
imposto ou preço antes da data efetiva. Programas aprovados reservam orçamento e
o consomem uma vez na execução. A receita pública soma DARFs pagos e o campo
`event_fixed_income.withheld_tax`; o valor líquido do resgate não é descontado de
novo. O último pregão também concilia o recolhimento daquele dia.

## Camadas econômicas

O modelo `government-v1` preserva as séries armazenadas. Preços recebem o fator
de ordens e o fator de governo uma única vez sobre a referência de cada dia.
Uma política permanente do mesmo tipo e alvo substitui a anterior; investimentos
públicos são programas independentes. O fator total fica entre 0,1 e 3.

Para uma tarifa `t`, cada exposição empresarial contribui:

```text
receita = participação_da_receita × concorrência_doméstica × t
custo = participação_do_custo_importado × t × (1 − repasse)
efeito_empresarial = 0,20 × (receita − custo) / margem
```

Programas públicos acrescentam `0,005 × valor / 100 milhões`, com meia-vida de
365 dias, ao canal empresarial. Depois de 30 dias, acrescentam
`0,01 × valor / 100 milhões` à inflação anual, com o mesmo decaimento.
O canal monetário da ação é `−2,9 × diferença_de_SELIC × beta`.
Perfis demonstrativos têm margem de 15%, beta 1, concorrência doméstica 30% e
repasse 40%; as participações dependem do setor. A API aceita perfis explícitos
nas regras. Sem exposição cadastrada, não inventa participação de produtos.

A SELIC autônoma recebe 1,5 vez a inflação adicional. A decisão manual fixa a meta
de SELIC/CDI e registra a taxa histórica de referência no dia da decisão. O último
diferencial que já cumpriu 90 dias altera a inflação pelo coeficiente 0,25.
O adicional anual de inflação fica entre −10 e +50 pontos percentuais. CDI/SELIC
não caem abaixo de zero. O IPCA diário usa a razão dos fatores anuais com e sem
o adicional, preservando a distribuição mensal da referência.

A prévia mantém os preços de referência de `as_of` e informa seu horizonte:
vigência para tributos/tarifas e 30 dias de execução para gasto público.
É uma hipótese estática de aprovação, sem previsão de futuras cotações.

Renda fixa, projeções e reconstrução leem o mesmo provedor de indexadores e a
tributação efetiva na data do resgate. A renda variável usa a alíquota vigente
na venda e preserva os conjuntos de compensação de prejuízo. Quando houver
alíquotas diferentes no mesmo conjunto mensal, o lucro tributável após compensação
usa a média das alíquotas ponderada pelos resultados positivos. O teto de isenção
mensal é o vigente no fechamento do mês. Esses são critérios do jogo.

## Integração e desempenho

`GovernmentPriceImpact` atende cotação, histórico e estatísticas. O mini gráfico
transforma os fechamentos em uma consulta em lote. Os benchmarks monetários usam
a mesma partida por `using_simulation`; comparar partidas não mistura indexadores.
O benchmark IBOV recebe o canal monetário agregado, com beta 1; não é uma cesta
recalculada das empresas do catálogo.

A carteira presidencial é bloqueada no servidor em compras de títulos e ordens
de ações. A posse cancela ordens anteriores antes do matching. Uma decisão manual
de SELIC atualiza cotações, livro e snapshots sob o mesmo lock, mesmo na pausa.

A visão pública é compartilhada em cache por data, revisão e snapshots; os
campos de identidade e permissão são personalizados em cada resposta. Consultas
repetidas por outro jogador não repetem SQL para montar a mesma visão. A expansão
desligada não carrega seu diário. O frontend consulta o estado a cada 2,5 segundos
enquanto a partida está ativa e invalida dados financeiros ao observar nova revisão,
inclusive quando a decisão veio de outro jogador.

Os resultados financeiros preservam o ranking individual e adicionam partidos.
O critério selecionado também orienta o resultado salvo e as conquistas de vitória.

## Verificação

Os testes de governo cobrem consentimento, campanha limitada ao caixa, reeleição,
turnos sem candidatos restantes, Congresso, reserva de orçamento, impeachment,
SELIC, atraso e decaimento, sinal do impacto sobre produtores/importadores e
isolamento entre partidas. Os testes com PostgreSQL verificam as rotas reais,
prévia sem escrita, repetição de comando, rollback atômico, retomada, carteira
congelada, preço consistente na pausa e cache sem vazamento de permissões.

Os parâmetros são iniciais. A calibragem de equilíbrio depende de partidas jogadas;
uma alteração deve ganhar versão própria e preservar as regras dos jogos salvos.
