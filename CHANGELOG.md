# Changelog

Mudanças de cada versão do Simulador Financeiro, da mais nova para a mais antiga.
O número segue o [SemVer](https://semver.org/lang/pt-BR/): a versão maior avisa quando algo
deixa de funcionar para quem atualiza, a menor traz novidade e a de correção conserta bug.

## 2.3.0 (24/10/2026)

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Adicionada ordenação em todas as tabelas de dados
- Adicionada a exclusão de ativos na Central de dados
- Adicionado o crédito com nota de risco, empréstimos e parcelas
- Atalhos de valor da renda fixa somando ao campo
- Adicionado o modo automático com estratégias por jogador
- Adicionado o aviso de quando as estatísticas atualizam
- Adicionada a renda fixa com liquidez diária e resgate em qualquer pregão
- Adicionadas as estratégias prontas de comprar e segurar, rebalanceamento, IFR, rompimento e momentum
- Adicionados os bots na sala
- Adicionado o gráfico da nota ao longo da partida
- Adicionado o gráfico de ações que acompanha o preço
- Adicionada a lembrança da última configuração da partida
- Adicionada a classe cripto com quantidade fracionária
- Adicionado o seletor de período da partida com linha do tempo
- Adicionados os presets de partida
- Adicionados os indicadores técnicos
- Voltado o quadrado da marca no cabeçalho da sala
- Adicionado o link de ajuda para quando os amigos não entram na sala
- Adicionada a compra a mercado por valor e ajustada ao caixa
- Adicionado o total gasto no retorno da ordem
- Adicionada a compra a mercado por valor e o botão Tudo na boleta
- Adicionado o modo backtest para testar estratégias sem esperar o jogo
- Adicionada a correção de erros de dado do yfinance na importação e na Central de dados

### Correções

- Corrigidas a pausa e a sincronização das operações de investimento
- Canceladas as ordens abertas ao parar ou terminar a partida
- Corrigido o gráfico das estratégias para acompanhar o dia da partida
- Corrigidos ícones e textos do crédito para bater com o desenho
- Corrigida a contagem de ordens abertas ao ligar o automático
- Corrigido o encerramento do loop com pregão travado ou erro no meio da partida
- Movida a chave de correção de erros de dado para o painel de importação

## 2.2.0 (22/10/2026)

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Adicionada a gravação automática de demonstrações com zoom automático
- Adicionado o proxy do Vite na porta do config.toml
- Adicionado o botão de excluir partida salva no lobby
- Permitido importar ações diferentes com o mesmo nome
- Guardado o ticker da B3 sem o .SA e acrescentado só ao consultar o yfinance
- Adicionadas as conquistas com catálogo declarativo, tela, aviso e entradas
- Unificada a conversão entre as regras da partida e o formulário do lobby
- Adicionados os testes das contas feitas no frontend, com o Vitest
- Adicionados os testes da conexão em tempo real, do loop e da carga da partida
- Adicionado o Modo Especialista, que esconde as ajudas da renda fixa
- Adicionadas as screenshots que faltavam na demonstração e o download das imagens no build dos docs
- Adicionado o logo do simulador
- Adicionada a atividade de cada jogador na sala
- Trocada a marca do app pelo logo do simulador
- Otimizadas as consultas de cotações e a reutilização do catálogo na partida

### Correções

- Regenerado o openapi na versão 2.1.0
- Corrigido o teste de configurações para usar o banco descartável
- Corrigida a barra do topo das conquistas fora da partida para seguir o design

## 2.1.0 (21/10/2026)

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Adicionado o modo debug
- Adicionado o painel de desempenho
- Adicionado o fallback de polling ao Socket.IO
- Adicionado o modo em equipes ao backend e ao lobby
- Adicionado o modo em equipes às estatísticas
- Adicionado o modo em equipes ao fechamento da partida
- Completado o modo em equipes com esqueleto, placar vazio, legenda e coluna na média
- Completado o modo em equipes com legenda única, leitura do risco e nomes longos
- Registradas as requisições HTTP nos arquivos de log no modo debug
- Adicionado o modo corrida à meta
- Adicionado o modo viver de renda
- Adicionado o gerador de séries sintéticas
- Adicionados o encaixe de nível e o choque de inflação ao gerador de séries
- Adicionada a geração de dados futuros na Central de dados

### Correções

- Corrigidos os avisos e o título do painel de desempenho
- Ajustados textos do modo em equipes conforme o design
- Ajustado o convite do lobby para ocupar uma vaga e a linha toda no modo em equipes
- Alinhado o nome das equipes nas regras da partida ao design
- Adicionados os ícones do modo de jogo nas regras da partida
- Corrigidas as regras do lobby que voltavam com o nome da partida anterior
- Corrigida a saída do jogador da sala ao fechar uma de duas abas abertas

## 2.0.0 (17/10/2026)

**Acesso antecipado.** A primeira versão desde a 1.0.0, de fevereiro de 2026. Muita coisa mudou, em resumo:

- **Visual novo** em todas as telas, com um design system próprio.
- **Várias partidas salvas**, comparação entre elas e fechamento de partida com pódio e vencedor.
- **Multiplayer mais completo**: cor por jogador, entrada no meio da partida e status online e offline.
- **Estatísticas por abas**, com nota geral decomposta em eixos e métricas de risco.
- **Renda fixa com indicadores reais do Banco Central**, imposto de renda na venda de ações, setores na carteira e ferramenta de correlação entre ativos.
- **Central de dados** para importar ativos fora da partida, com sugestão de código ao digitar.
- **Postgres embarcado** no executável do Windows: não precisa instalar banco.

**Atenção: as partidas salvas da 1.0.0 não abrem nesta versão.** O banco de dados mudou de estrutura e não há migração dos dados antigos. A partir da 2.0.0, as atualizações aplicam as mudanças do banco nas partidas salvas sozinhas.


### Novidades

- Implementado tipagem automática a partir da openapi
- Implementado one start
- Implementado displayMoneyCompact
- Implementado tabela de Status dos Ativos
- Adicionado novas opções no lobby
- Implementado feat de múltiplas simulações/saves
- Melhorado tipagem de eventos WS
- Atualizado visual
- Adicionado modo only nos scripts
- Serializado Decimal como string e unificado cálculo de renda fixa no backend
- Adicionado comparação entre simulações com ranking calculado no backend
- Adicionado impacto de preço das ordens configurável por partida
- Alterado snapshot para diário com renda fixa lida do motor
- Adicionado métricas de risco do desempenho
- Adicionado migrations com Alembic no lugar do create_all
- Adicionado diagrama do banco gerado dos models na documentação
- Adicionado indicadores reais do Banco Central na renda fixa
- Adicionado Central de dados fora da partida
- Adicionado geração do OpenAPI dos docs a partir das rotas
- Alterado tipos do frontend para serem gerados do OpenAPI dos docs
- Adicionado IR na venda de renda variável
- Adicionado setores e segmentos com visão por setor na carteira
- Adicionado estatísticas em abas por dimensão
- Adicionado nota geral decomposta por eixo
- Adicionado fechamento de partida com pódio e critério de vitória
- Adicionado ferramenta de correlação entre ativos
- Adicionados os tokens e as fontes do visual novo
- Adicionadas as variantes do visual novo no design system
- Redesenhados a barra lateral e o topo do app
- Redesenhados o carregamento, a página não encontrada e os avisos
- Redesenhado o login com o aviso de nickname existente no próprio card
- Redesenhado o lobby com regras em painel lateral e simulações salvas com status e vencedor
- Redesenhada a Central de dados com importação, situação e classificação na própria tela
- Redesenhada a carteira com resumo, aportado no gráfico, setores e régua de isenção do IR
- Redesenhada a lista de renda variável como tabela de mercado com faixa do dia e 30 dias
- Redesenhado o detalhe da ação com boleta, prévia da ordem, IR estimado e livro da sala
- Redesenhada a renda fixa com tabela comparável, taxa do dia e boleta com projeção
- Redesenhadas as estatísticas com destaque da colocação, nota por eixo e mapas de calor
- Redesenhado o fim de partida com vencedor, pódio e destaques da sala
- Redesenhada a comparação de simulações com letra e cor por partida, você contra você e eixo desde o início
- Redesenhada a correlação com ativos por setor, meia matriz, par fixado e destaques
- Redesenhadas as configurações e a página de estratégias em desenvolvimento
- Ajustados diálogos, painéis, topo e barra lateral ao design revisado
- Ajustados lobby, regras da partida e simulações salvas ao design revisado
- Usado o tipo do yFinance para definir a classe do ativo importado
- Ajustada a Central de dados ao design revisado
- Incluídos o nome da empresa na posição e a colocação do jogador nas simulações salvas
- Ajustada a carteira ao design revisado com evolução em faixas por classe
- Ajustadas as listas de renda variável e renda fixa ao design revisado
- Ajustados o detalhe da ação, a boleta e o livro de ofertas ao design revisado
- Incluídos os meses fechados no ranking das estatísticas
- Ajustadas as abas das estatísticas ao design revisado
- Ajustado o fim de partida com o relatório e as abas no mesmo cabeçalho
- Mantidos os atalhos da correlação à vista e unificada a escala de cor dos destaques
- Ajustada a comparação de simulações com resumo, ranking e você contra você
- Ajustados o 404, os avisos empilhados e as configurações ao design revisado
- Redesenhada a página de Estratégias com prévias ilustradas
- Separados os logs por assunto, com error.log só dos erros
- Traduzidas para português as mensagens de erro do backend
- Adicionado o diagrama do banco navegável nos docs
- Adicionada a cor exclusiva por jogador na partida com seleção da partida salva
- Adicionado o seletor de cor, a sigla de duas letras e a seleção da partida salva no lobby
- Adicionada a entrada no meio da partida e a lotação da partida salva no lobby
- Travadas as regras da partida salva selecionada
- Adicionada a bolinha de status online e offline dos jogadores
- Adicionada a faixa de nova partida ao diálogo de escolha e o aviso de lotação em Alert
- Adicionados os estados do card de partida salva: carregando, erro, vazio e regras em só leitura
- Trocado o atalho da última salva pelo botão de escolher partida e o selo no diálogo
- Adicionado o Postgres oficial embarcado no executável do Windows
- Adicionados a sugestão de código ao digitar o ativo e o cache do perfil do yfinance

### Correções

- Clean de lazy imports por conta de import circular
- Feito name ser obrigatório
- Corrigido bug ao criar simulações
- Corrigido gráfico do TradingView não funcionando
- Adicionado lock para as operações de posição e saldo
- Pequenas correções
- Corrigido erro 500 na compra de renda fixa sem saldo
- Corrigido trava de migration que recusava remover tabela vazia
- Restringido abertura automática do navegador ao executável
- Ajustados a leitura do par na correlação e a cor do avatar no perfil
- Traduzida para o português a linha técnica dos erros da API
- Corrigidos o recuo dos links, os rótulos do gráfico da carteira e os meses repetidos no eixo
- Ajustados os detalhes de estatísticas, comparação e resumo da carteira após a validação
- Simplificada a mensagem de partida lotada
- Invertida a ordem entre iniciar nova simulação e o atalho da última salva
