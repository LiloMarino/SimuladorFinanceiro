# Design do FinSim

## Princípios

### O FinSim é para leigos, e a tela continua limpa

O simulador existe para quem não entende de finanças aprender jogando. A tela traz o
mínimo para decidir; a explicação completa mora no tutorial, que ensina desenhando.

- **Termo, métrica ou sigla** (alavancagem, volatilidade, spread, Ibovespa, Tabela
  Price…) ganha uma descrição curta ao lado e uma dica com a definição, um exemplo com
  números e o que é valor bom e ruim.
- **Parâmetro mostra o efeito dele:** um número como "20% do caixa por compra" vem com o
  exemplo em reais do dia, e o gráfico que a tela já tem daquilo se redesenha quando o
  parâmetro muda, antes de salvar.
- **Decisão com custo** mostra o custo antes do clique: quanto se paga de juro, o que
  acontece com as ordens abertas, o que muda na nota.
- **Percentual vem com o tamanho da amostra:** "100% de 3" não é "100% de 80".
- **Explicação que passa de uma frase é tópico do tutorial**, no molde das Dicas e
  truques do Factorio: abas por tópico, ilustração no mínimo e animação quando o
  movimento é o que ensina. Cada bloco na tela responde uma pergunta de quem está
  decidindo ali; o resto vai para o tópico.

### A topbar é das informações de toda partida

A topbar mostra o que toda partida tem (data, velocidade, caixa) e o que os modos e as
expansões ligados na partida acrescentam. O estado de uma feature do jogador (estratégia
ligada, parcela chegando) vive no item dela no menu lateral e nos toasts.

## Identidade visual

- Tokens de cor, fonte e raio: `frontend/index.css`.
- Componentes: `frontend/shared/components/ui/`. Quando falta uma forma, ela nasce como
  variante do componente.
- No canvas de design, o `<helmet>` dos boards traz as mesmas cores e classes; board novo
  começa copiando o de um board existente.
