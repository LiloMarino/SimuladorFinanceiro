# Changelog

Mudanças de cada versão do Simulador Financeiro, da mais nova para a mais antiga.
O número segue o [SemVer](https://semver.org/lang/pt-BR/): a versão maior avisa quando algo
deixa de funcionar para quem atualiza, a menor traz novidade e a de correção conserta bug.

## 3.5.0 Federações e Estados (07/11/2026)

A política ganha geografia: um mapa do Brasil por região e por estado mostra quem lidera, a aprovação do presidente e onde vive cada grupo de eleitores, e a pesquisa sai também por estado. Partidos podem se unir em federações para escapar da barreira e somar votos no Congresso, pagando com o candidato próprio e a rejeição do parceiro. O acordo de base passa a valer até o fim do mandato, e as bancadas cobram mais quando o governo fica fraco.

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Adicionado o acordo de base até o fim do mandato
- Adicionado o mapa do Brasil por região e por estado
- Adicionadas as federações partidárias

## 3.4.0 Juros e Tesouro (07/11/2026)

O governo ganha a SELIC nas mãos, e o Tesouro ganha tela própria, com marcação a mercado e resgate automático da renda fixa para cobrir despesas. A economia fica interligada: PIB, desemprego, juros e bolsa passam a se influenciar na partida, e o gerador de futuro troca o choque de inflação por nível e surtos.

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Adicionada a evolução do patrimônio por tipo de renda variável
- Adicionadas as séries de PIB e desemprego na Central de dados
- Adicionada a economia interligada
- Adicionadas as parcelas da economia interligada no painel da Economia
- Adicionada a SELIC nas mãos do governo
- Adicionados a tela do Tesouro, a marcação a mercado e o resgate automático de renda fixa
- Adicionado o ícone próprio do Tesouro e a convenção de ícones personalizados
- Trocado o choque de inflação por nível e surtos no gerador de futuro
- Adicionados o PIB e o desemprego à prévia do futuro gerado
- Adicionada à Central a legenda do PIB e do desemprego calculados na partida
- Adicionado o primário que estabiliza a dívida no painel da Economia
- Adicionada a SELIC do presidente livre até 3 pontos por reunião
- Garantida a SELIC da história dentro da janela da reunião do presidente

### Correções

- Separadas as cores dos jogadores das cores dos gráficos
- Calculado o juro do mês sobre a dívida anterior
- Apontado o profile_match para o banco de teste
- Alargado o log das ordens do bot e quebradas as colunas de texto
- Mantido o item Pendências na barra lateral mesmo sem pendências
- Reduzido o selo de pausa a Pausado, com o motivo na dica
- Adicionados avatar e marca nos selects de candidato, vice e rival
- Adicionado o radar do perfil na aba Partido da preparação
- Feito o jornal rolar a página inteira com o arquivo fixo na lateral
- Dimensionadas as compras das estratégias pelo preço de venda do book
- Feito o governo do computador eleito propor com a fila vazia
- Mostrada a mensagem de erro do servidor nos logs do bot e da estratégia
- Removidas as explicações internas do card de novo empréstimo
- Removidas as explicações internas do card do partido
- Removidas as explicações internas das telas de eleição e orientação do partido
- Removida a explicação interna da tela de governo antes da posse
- Atualizado o yfinance para eliminar o aviso do pandas no terminal
- Revertida a atualização do yfinance e filtrado o aviso do pandas no terminal
- Descontada a inflação da bolsa no alvo do crescimento do PIB
- Ajustada a bolsa do futuro gerado para reagir ao juro real e acompanhar a inflação do nível
- Atualizada a leitura dos surtos com o ano de pregões do futuro gerado
- Medida a credibilidade do Banco Central contra o juro real da história
- Corrigido o desemprego da partida que volta devagar ao normal da época

## 3.3.0 Preparação no lobby (04/11/2026)

Cada jogador agora se prepara antes de a partida começar: no lobby, um dialog com abas guarda no perfil o Meu partido, a contribuição ao partido e os parâmetros das estratégias, e o desafio da vela sai da partida para virar uma atividade do lobby, com o placar de cada um. Fundar, filiar-se e sair do partido ficam liberados desde o 1º dia, e a paleta de jogadores e partidos troca para 13 cores que se distinguem também para daltônicos, com o partido já marcado na cor de quem o funda. A Eleição ganha a corrida entre partidos redesenhada e a campanha reorganizada; o Congresso mostra o placar da votação; as contas do governo, o jornal, a carteira, a comparação de partidas e o crédito (com o custo inteiro do empréstimo antes de assinar e o aviso de parcela em atraso) são redesenhados. Partidas longas ficam mais rápidas no fechamento do dia e nas Estatísticas, o modo debug ganha perfil de rota e do motor e o painel de desempenho mede cada etapa do dia, e as tabelas passam a caber na tela com texto de no mínimo 12 px. Os resumos do mês saem, e fica a retrospectiva do ano.

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Adicionado o desafio da vela no lobby, em janela de atividade, e removido o da partida
- Adicionada a preparação de cada jogador no lobby, com o Meu partido salvo no perfil
- Adicionados avatar e nome de cada jogador ao seletor do vice
- Adicionado o filtro Na carteira independente da classe na renda variável
- Removida a ordenação pelos cabeçalhos da matriz de correlação
- Removidos os selos a sala vê e marcado com ícone o que só o partido vê
- Removido do diálogo de nova medida o bloco Quem tem esses ativos
- Removidas das telas as curvas do prêmio de risco pela dívida e da escala do investimento
- Reordenados os cartões das configurações, com o tutorial ao lado da posição do jornal e a zona de perigo por último
- Movido o log das ordens do bot para um drawer lateral
- Passado o período do backtest para o seletor de período da sala
- Mostrado o aviso de atualização das Estatísticas também com a partida pausada
- Adicionado um log por boot do servidor, com os anteriores numerados
- Adicionada a contagem acumulada dos eventos do Socket.IO ao painel de desempenho
- Adicionada a medida por etapa do dia ao painel de desempenho
- Adicionados o perfil de rota e o perfil do motor ao modo debug
- Adicionados o py-spy e o script de rodadas do motor
- Trocado o cProfile pelo yappi, com perfil só da rota ou só do motor
- Mantidas as 3 requisições mais lentas de cada rota no perfil das rotas
- Carregadas sozinhas as próximas páginas dos logs ao rolar
- Adicionado o aviso de parcela em atraso no topo do crédito e atualizado o valor do atraso a cada dia
- Mostrada a consequência inteira das pendências com o Pagar em destaque
- Ajustada a tabela da Central de dados para caber no cartão sem rolagem lateral
- Ajustado o formulário do período do backtest para caber na coluna
- Ajustadas as tabelas para caber na tela e o texto para no mínimo 12 px
- Reorganizada a aba da campanha da eleição
- Redesenhada a corrida entre partidos da Eleição
- Adicionado placar e acesso à casa eleita na votação do Congresso
- Ajustado o jornal ao desenho aprovado com histórico paginado por mês
- Adicionada a fonte IBM Plex Serif nas manchetes do jornal
- Adicionado o bloco com o custo inteiro do empréstimo antes de assinar
- Ajustada a carteira com a base dos percentuais, alturas iguais e meta fora da escala
- Ajustada a comparação de partidas com os eixos em grade e o ranking sem barra de retorno
- Redesenhadas as contas do governo em uma coluna, com impostos e receita juntos
- Liberados fundar, filiar-se e sair do partido desde o 1º dia da partida
- Adicionada a contribuição do partido salva no perfil, com pendência do mês não pago
- Adicionados os parâmetros das estratégias salvos no perfil
- Redesenhada a preparação do lobby num dialog com abas
- Trocada a paleta de jogadores e partidos por 13 cores que se distinguem também para daltônicos

### Correções

- Corrigida a chapa do fundador que concorre sem vice na preparação do lobby
- Corrigida a leitura dos eventos do segundo turno, que quebrava o resumo do mês, as estatísticas e as conquistas
- Limitado o crescimento do PIB e reduzido o peso da bolsa nele, que derrubava partidas longas
- Corrigida a alavancagem sem patrimônio, que aparecia como traço no crédito
- Corrigido o tooltip das séries da Economia, que mostrava a data no lugar do nome
- Adicionado o estado de erro na tela de resultado, que ficava no esqueleto
- Corrigido o ranking velho das Estatísticas, que não era refeito ao voltar à tela
- Arredondados os pontos da nota de risco, que saíam do cartão do crédito
- Corrigida a mensagem de erro das páginas de Governo, Eleição, Economia e Crédito, que dizia que a conexão caiu
- Corrigido o jornal, que ficava no esqueleto quando as preferências falhavam
- Corrigido o diálogo de promessas, que misturava a falha da prévia com a regra e deixava anunciar
- Corrigida a janela de notícias, que dizia que o tempo corria com a partida pausada
- Corrigido o plural dos pontos indecisos no aviso de apoio do 2º turno
- Corrigido o plural da projeção das promessas quando a chapa só tem uma
- Corrigido o cartão de promessas do Governo, que deixava colunas vazias com uma ou duas promessas
- Corrigido o plural de compras e vendas na aba de operações quando há só uma
- Corrigido o texto do prêmio de risco, que escrevia ponto(s) em vez de concordar com o valor
- Corrigido o cabeçalho do desafio da vela, que escrevia o número da pergunta no fim da frase
- Corrigidos os nomes cortados do lobby, que ficavam sem dica e sem espaço ao lado do seletor de cor
- Corrigida a estratégia do bot nas tabelas de estatísticas, que ficava cortada sem dica
- Corrigidos os cartões de partido da eleição, que cortavam o nome sem dica
- Corrigida a faixa do dia da renda variável, que colava mínimo e máximo em preços longos
- Corrigido o relatório final, que dizia o que faltava para a meta e para o 1º depois de a partida acabar
- Corrigidos os cartões de pesquisa e eleitorado, que anunciavam uma primeira pesquisa depois de a campanha acabar
- Corrigido o diálogo da votação, que abria com uma dica aberta e a tabela rolada
- Corrigida a janela do desafio da vela, que passava de 768 px de altura e escondia os botões de voto
- Corrigida a cor dos partidos do computador, que ficavam cinza na Eleição e coloridos no Congresso
- Corrigida a Eleição entre os turnos, que mostrava a pesquisa do 1º turno já apurado ao lado da do 2º
- Corrigida a tabela de transferência do 2º turno, que chamava de exatos votos que são estimativa
- Corrigido o arredondamento da transferência do 2º turno, que fazia as partes de uma linha não somarem o total
- Corrigido o diálogo do resultado do turno, que só abria ao vivo e não voltava após recarregar a página
- Corrigida a data da posse, que mostrava o primeiro pregão do ano em vez de 1º de janeiro
- Corrigida a prévia de promessas, que seguia com números da lista anterior e deixava anunciar enquanto recalculava
- Corrigida a nota de crédito, que ignorava parcela vencida e sem pagar depois de 12 meses
- Corrigido o painel final do desafio da vela, que comemorava mesmo com 0 acertos
- Corrigido o cartão do desafio da vela, que sumia enquanto carregava e quando falhava
- Corrigida a coluna Quando das ordens abertas, que mostrava a hora real em vez do dia da partida
- Centralizados na vertical os selos da barra lateral
- Alinhados à linha os algarismos do jornal
- Igualado o tamanho dos botões da estratégia
- Aberta pelo teclado e pelo toque a dica dos padrões de vela
- Limitada à altura da tela a janela de nova medida e esticado o seletor de mudança
- Posta em coluna própria a ação dos alertas
- Mantida à vista a proposta anterior ao trocar de bancada na negociação
- Limpo o cache de consultas ao sair e ao encerrar a conta
- Mostrado o nome da série no tooltip do gráfico do backtest
- Desenhada a linha do Ibovespa que chega depois no backtest
- Contida na borda a tabela do cartão de risco da nota
- Trocado por seletor de ano o campo até quando do gerador de futuro
- Explicado na dica do rótulo o retorno sobre o aportado dos rankings
- Migrados para o lugar da ação do alerta os botões encaixados à mão
- Ajustados os tipos das estratégias ao pandas 3.1
- Adicionados o voto de cada jogador, a posição no cabeçalho e o nome do padrão no desafio da vela
- Adicionado o nome do padrão sob as velas também na pergunta do desafio da vela

### Desempenho

- Calculado uma vez só o fator de impacto de cada dia no histórico dos bots
- Gravado o snapshot do dia só com o balanço, sem montar a carteira da tela
- Removidos os resumos do mês e mantida só a retrospectiva do ano
- Montada a janela de preços dos bots em arrays, sem passar pelo pandas
- Limitado o fechamento do crédito aos snapshots da janela da nota
- Gravados os snapshots do dia numa consulta só para todos os jogadores
- Descontada a duração do dia na espera entre os pregões
- Calculado o volume médio do impacto numa consulta por ativo
- Calculado o histórico da nota numa passada só pela partida
- Lido o histórico das Estatísticas só com as colunas usadas
- Planejada cada consulta do banco com os valores dela

## 3.2.0 Orçamento e Congresso (29/10/2026)

O governo passa a ter contas: a receita vem das alíquotas, o gasto e os juros pesam no resultado, a dívida cresce com o déficit e o prêmio de risco encarece os títulos novos do Tesouro. As medidas de gasto público mexem na inflação, na SELIC e na bolsa, e o painel da economia ganha PIB, desemprego e dívida. O Congresso é eleito por cadeiras, cada bancada segue a orientação do líder do partido, o impeachment é votado e o governo negocia apoio por emendas clicando no hemiciclo. A campanha e o segundo turno ganham avisos, toasts e resultado por grupo; o jornal ganha manchetes do Congresso e dos acordos; o partido do computador que assume sem vice passa a propor medidas; e os cartões de Governo, Eleição e Economia mostram esqueleto e erro próprios.

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Adicionados o orçamento do governo, a dívida pública, o prêmio de risco do Tesouro e o PIB e o desemprego no painel da economia
- Adicionadas as medidas de gasto público com o efeito na inflação, na SELIC e na bolsa
- Adicionados o Congresso eleito por cadeiras, as bancadas orientadas pelo líder e o impeachment votado
- Adicionados os acordos de apoio por emenda com as bancadas, negociados pelo hemiciclo
- Adicionado o governo do partido do computador que assume sem vice e propõe medidas pelos eleitores dele
- Adicionadas as manchetes da posse do Congresso, do acordo fechado, da medida de gasto, da virada e da volta atrás, a janela do jornal limitada a uma por pregão e o aviso de caixa negativo só como pendência
- Adicionados os avisos de apoio e da véspera, os toasts dos resultados, o cabeçalho e o cartão do 1º turno e o resultado do 2º turno com barra, selo, virada e grupos
- Adicionados o passo do rival desabilitado, o alcance da TV, a linha dos extremos do comício, o alerta de repetição com quem fez a 1ª, o cartão de quem não é filiado e o botão Ver nos toasts da campanha
- Adicionados os pontos de aviso de Governo e Eleição no menu, a explicação de quando cada pendência some, o aviso do acordo na aba Congresso e o botão Ver nos toasts dos acordos
- Adicionado o cartão com esqueleto e erro próprios, aplicado à base, às contas, às ações de campanha e à proposta de acordo

## 3.1.0 Eleição disputada (29/10/2026)

A eleição agora é uma disputa de verdade: o eleitorado se divide em grupos, cada um com a sua opinião sobre os partidos, e a campanha tem ações (TV, evento, comício e ataque) decididas com o dado. As promessas de campanha são cobradas no fim do mandato, o segundo turno tem disputa com virada possível, e a aprovação do governo passa a depender da satisfação de cada grupo. O painel da economia mostra a SELIC, o IPCA e a meta de inflação, e o jornal da partida traz manchetes de economia, empresas e marcos históricos, com as pendências ao lado do menu. Também entram a evolução do patrimônio redesenhada, a compra de cripto em fração para estratégias e bots, o filtro Na carteira na renda fixa e o selo de partida pausada.

Suas partidas salvas e o `config.toml` continuam valendo.


### Novidades

- Ajustado o layout da aba Expansões, da sigla do partido e da rentabilidade por jogador
- Desligar o automático direto no aviso das boletas travadas
- Adicionado o filtro Na carteira à renda fixa
- Adicionado o aviso de abertura da campanha com lembretes das chapas e da véspera do 1º turno
- Acelerada a abertura das estatísticas em partida longa
- Convite de vice para qualquer jogador da sala
- Host remove jogador da sala no lobby
- Adicionado o botão para abrir a pasta de configurações e a de logs
- Adicionadas oito conquistas sobre IR, setores, impacto de preço, Especialista, equipes, mercado gerado e nota geral
- Ajustados os acabamentos das telas de estatísticas, lobby, correlação, ajustes e indicadores
- Adicionada a caixa de entrada com o resumo do mês e a retrospectiva do ano
- Removidos código e dependências sem uso e adicionados o Knip e o deptry à checagem
- Ligado o plugin de acessibilidade do oxlint e corrigidos os achados
- Ligado o modo strict do pyright em config, routes e main.py
- Marcados como obrigatórios os campos com valor padrão nas respostas da API
- Ligado o noUncheckedIndexedAccess no frontend e tratados os itens ausentes
- Ligado o exactOptionalPropertyTypes no frontend e tratadas as props opcionais
- Ligada a regra no-unnecessary-condition no oxlint e removidas as condições desnecessárias
- Adicionado o selo de partida pausada com o motivo e o destaque da velocidade máxima na barra da partida
- Adicionada a contagem de imprevistos ao fim da partida de viver de renda
- Adicionada a compra e venda fracionária de cripto às estratégias e aos bots
- Redesenhados a evolução do patrimônio e a distribuição na carteira
- Adicionados os grupos de eleitores com bandeiras, apoio, rejeição e pesquisa com margem de erro
- Adicionado o painel da economia com a SELIC, o IPCA, o juro real, a meta de inflação e as mudanças do Copom
- Adicionada a aprovação do governo pela satisfação de cada grupo de eleitores, com alvo, carência e contagem do impeachment
- Adicionadas as ações de campanha com o dado: TV, evento, comício e ataque, com histórico e verba de base
- Adicionadas as promessas de campanha cobradas no fim do mandato, com rendimento por grupo e balanço
- Adicionado o segundo turno com disputa por grupo de eleitores, declaração de apoio, contribuição e pesquisa semanal
- Adicionado o jornal da partida com manchetes por tipo, página de histórico, resumos em Estatísticas e avisos configuráveis
- Adicionadas as pendências da partida com lista ao lado do menu, aviso ao nascer e ação que resolve cada uma
- Adicionado o noticiário da partida com manchetes de economia, empresas e marcos históricos e o filtro de ativos da carteira

### Correções

- Removida a notificação de saída dos bots ao iniciar a partida
- Alavancagem sem limite quando o patrimônio não é positivo
- Nome do presidente eleito no aviso da posse e no resultado
- Corrigido o layout estreito do destaque da renda fixa, do cabeçalho da eleição e do cartão das pastas do app
- Reiniciado o formulário de empréstimo depois de assinar o contrato
- Ocultado o 0% de pesquisa no convite de vice antes da primeira pesquisa

## 3.0.0 Governo & Política (25/10/2026)

- A expansão Governo & Política: os jogadores fundam partidos, disputam eleições em dois turnos, governam por mandatos de quatro anos, propõem medidas de imposto ao Congresso e acompanham a aprovação do governo.
- As dicas de análise técnica no gráfico: padrões de vela reconhecidos, legendas dos indicadores e o desafio da vela.
- A janela Como jogar, com os tópicos de compra, tipos de ordem e alavancagem.
- O guia para escrever um bot pela API, com um bot de exemplo.
- As conquistas passam a ser guardadas mesmo quando a partida em que saíram é excluída.

As partidas salvas da 2.3 abrem direto; da 2.0 à 2.2, abra uma vez na 2.3 antes.

**Atenção, esta versão quebra a compatibilidade:** algo que funcionava deixa de funcionar para quem atualiza.

### Quebras

- Exigida a 2.3 para atualizar as partidas salvas da 2.0, 2.1 e 2.2


### Novidades

- Adicionada a eleição por partidos na expansão Governo & Política
- Adicionados os detalhes que faltavam na eleição da expansão Governo & Política
- Adicionado o governo com impostos, Congresso e aprovação
- Adicionado o guia do bot pela API com bot de exemplo
- Adicionada a janela Como jogar com os tópicos de compra, tipos de ordem e alavancagem
- Adicionadas as dicas de análise técnica com padrões de vela, legendas dos indicadores e o desafio da vela

### Correções

- Corrigido o tópico de Alavancagem para a métrica do app e movido o núcleo do tutorial para shared
- Corrigidas as datas lidas do índice do pandas para o pyright não depender da inferência
- Corrigidos o Voltar ao lobby duplicado e o botão Remover na configuração do backtest
- Mantidas as conquistas quando a partida em que saíram é excluída

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
