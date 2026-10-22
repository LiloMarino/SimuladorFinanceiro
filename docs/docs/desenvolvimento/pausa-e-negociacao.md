# Pausa e negociação

A pausa é confirmada depois de terminar o dia em processamento. O início do próximo
tick confere a velocidade novamente sob o mesmo lock usado pelas operações e
consultas da simulação. Assim, preço, data, livro, caixa e posições pertencem a um
pregão completo. O controlador também limpa a sinalização da partida anterior ao iniciar.

O motor recebe a data nova antes de atualizar o livro: ordens antigas executadas
pela liquidez do dia novo registram eventos nessa data. Compras, vendas e
cancelamentos persistem seus eventos sem depender de outro tick, inclusive quando
a submissão executou parcialmente antes de devolver erro.

## Renda fixa

A vitrine continua sendo renovada mensalmente. Uma oferta que já estava aberta
no navegador permanece consultável e comprável durante a partida até seu
vencimento, mesmo depois de sair da vitrine. O catálogo guarda essas ofertas em
memória e remove as vencidas; títulos comprados continuam persistidos no banco.

A checagem do vencimento ocorre sob o lock da compra. A projeção também recusa
títulos vencidos. A tela distingue oferta indisponível, vencimento real e falha
de conexão; taxas e projeções são renovadas com a data e o caixa.

## Renda variável e sincronização

Ao receber a pausa, cada cliente cancela leituras antigas e confere estado, renda
fixa, renda variável, carteira e indicadores. O autor da pausa faz a mesma
conferência depois da resposta HTTP. Reconectar também renova os dados e refaz
as assinaturas do Socket.IO, mesmo se os nomes dos eventos forem iguais.

Prévia, reservas, posição, caixa, livro e histórico são renovados depois das
operações, sem exigir que o jogo volte a correr. A prévia também acompanha eventos
de caixa, posição e livro. A boleta aguarda a prévia da ação e quantidade digitadas,
em vez de liberar uma venda com a resposta de uma compra anterior.

Ordens parcialmente executadas podem ser canceladas: somente o restante reservado
volta a ficar disponível. Liquidez e saldo continuam sendo limites reais da ordem;
a pausa não cria volume de negociação ilimitado.

O detalhe e o gráfico usam o mesmo histórico. Eventos não fabricam um detalhe
incompleto antes da resposta inicial, não duplicam o dia e não fazem a cotação
regredir se chegarem atrasados. Um refetch na pausa atualiza o gráfico sem esperar
outra mensagem de preço.

Leituras HTTP têm prazo de 30 segundos, incluindo o recebimento da resposta.
Falhas terminam em estado de erro com tentativa manual. Compras e outras escritas
não recebem esse timeout nem repetição automática: perder a resposta não prova
que a operação não aconteceu.

## Verificação

```bash
uv run pytest tests/test_paused_trading.py tests/test_simulation_loop.py tests/test_broker.py
pnpm run front:test
```

Os testes HTTP usam PostgreSQL descartável e dois jogadores reais de teste. Cobrem
compra e venda com velocidade zero, histórico imediatamente consultável, troca do
catálogo no mês, vencimento, pausa concorrente com tick, leitura que aguarda o dia
completo e data de execução de ordem pendente. Os testes do livro conferem a
liberação de reservas após execução parcial. No frontend, os testes exercitam o
cache do React Query, resposta antiga cancelada, reconstrução do histórico,
timeout e reinscrição na reconexão.

Na validação local desta alteração, a instalação do lockfile atual do frontend foi
recusada pela idade mínima de publicação configurada no pnpm. Os testes, a tipagem,
o lint React e o build foram executados em uma cópia do código com o lockfile
anterior aprovado (revisão `16eaa880`, TypeScript 6.0.3 e Vite 8.3.4); o projeto
continua com suas dependências atuais. Isso não substitui a validação com o
lockfile atual, TypeScript 7 e oxlint quando essas dependências forem permitidas.
O check da raiz também encontra violações no trabalho separado em `.plugin-build`.
