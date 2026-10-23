---
sidebar_position: 7
---

# Importação de Ativos

O simulador permite importar dados históricos de ativos para usar na simulação. Esta funcionalidade é essencial para ter acesso a ações, FIIs e ETFs com dados reais de mercado.

## Como Funciona

O sistema de importação carrega **dados históricos OHLCV** (Open, High, Low, Close, Volume) de ativos e os armazena no banco de dados para uso nas simulações.

**OHLCV significa:**
- **Open (Abertura)** - Preço na abertura do dia
- **High (Máxima)** - Preço mais alto do dia
- **Low (Mínima)** - Preço mais baixo do dia
- **Close (Fechamento)** - Preço no fechamento do dia
- **Volume** - Quantidade de ações negociadas no dia

Estes dados são usados para simular o movimento realista do mercado durante a simulação.

![A Central de dados, com o painel de importação e a tabela das séries da base](/demo/screens/import-assets.png)

---

## Central de dados

A **Central de dados** é a tela onde você importa ações e acompanha quais séries estão guardadas no banco. Ela substitui a antiga tela "Importar Ativos" e é aberta pelo botão **Central de dados** no lobby.

Ela só pode ser aberta **fora de uma partida**: durante uma partida, o sistema leva você de volta para a tela principal.

A tela tem duas partes: o painel **Adicionar ativo** (explicado em [Métodos de importação](#métodos-de-importação)) e a tabela **Séries da base**.

### Séries da base

A tabela lista todas as séries guardadas no banco: primeiro os indicadores econômicos (CDI, SELIC, IPCA e Ibovespa) e depois cada ativo importado. O filtro **Todas** / **Precisam de atenção** deixa só as séries que pedem uma olhada (sem dado real, desatualizadas ou sem classificação). Em cada linha:

- **Série**: nome do indicador ou do ticker.
- **Setor · segmento**: a classificação da ação (ver abaixo). Indicadores mostram "—".
- **Linha do tempo**: barra com o período coberto. O trecho com dado real aparece em uma cor e, depois dele, o trecho gerado em outra cor. Todas as barras usam a mesma régua de tempo, então dá para comparar visualmente quais séries cobrem mais anos. Passe o mouse sobre a barra para ver as datas: "Real: início → fim · gerado até …". Séries sem futuro gravado não têm trecho gerado, e depois do fim do dado gerado a partida repete o último valor da série (ver "Gerar dados futuros", abaixo).
- **Situação**: se a série está em dia ou parou de atualizar. Uma ação que parou mostra o selo **Parou em** com a data do último preço.
- **Ações**: o botão **Atualizar** da linha e, nas ações, a **classe do ativo** (ex.: Ação).
- **Apagar** (lixeira, só nos ativos): remove o ativo da base com os preços, o perfil e a classificação, depois de uma confirmação. É a saída para um ativo importado com dado errado. Um ativo negociado em alguma partida salva não pode ser apagado: a Central avisa em quantas partidas ele aparece, e é preciso excluir essas partidas no lobby antes. Depois de apagar, o futuro gerado passa a pedir recálculo.

### Setor e segmento das ações

Cada ação pertence a um **setor** (ex.: Financeiro) e, dentro dele, a um **segmento** (ex.: Bancos). A carteira mostra quanto da renda variável está em cada setor, e as estatísticas comparam os setores entre os jogadores.

- **Sugestão automática:** ao importar uma ação pelo Yahoo Finance (ou ao atualizar uma que ainda não tem classificação), o setor e a indústria que o Yahoo informa viram a sugestão. O setor chega traduzido para os nomes da B3 (ex.: *Financial Services* → Financeiro); o segmento chega como o Yahoo escreve (ex.: *Banks - Regional*).
- **Editar:** o botão **Classificar** (para uma ação ainda sem setor) ou o próprio setor e segmento da linha abre a edição ali mesmo. Escolha um setor e, se quiser, um segmento da lista, ou digite nomes novos, e use **Salvar**. **Tirar classificação** deixa a ação como "Sem setor", e **Cancelar** fecha sem mudar nada.
- Uma classificação feita à mão não é trocada pela sugestão nas próximas atualizações.

### Indicadores econômicos

- **CDI**: taxa de juros dos empréstimos entre bancos, publicada por dia. Serve de base para muitos CDBs. Ex.: um CDI de 0,0551% em um dia quer dizer que R$ 1.000 viram R$ 1.000,55 na noite.
- **SELIC**: taxa básica de juros da economia, definida pelo Banco Central e também publicada por dia.
- **IPCA**: inflação oficial, medida por mês. Ex.: um IPCA de 0,5% no mês significa que os preços subiram 0,5% naquele mês.
- **Ibovespa**: índice que acompanha o desempenho das ações mais negociadas da B3, a bolsa brasileira. Ex.: de 100.000 para 101.000 pontos é uma alta de 1%.

**Fontes:** CDI, SELIC e IPCA vêm do Banco Central, pelo sistema SGS (Sistema Gerenciador de Séries Temporais), nas séries 12 (CDI diário), 11 (SELIC diária) e 433 (IPCA mensal). O Ibovespa vem do Yahoo Finance (ticker `^BVSP`).

### Gerar dados futuros

Serve para continuar jogando depois do último dia com dado real. O futuro é montado com trechos reais da bolsa desde 2000 e fica gravado como dado gerado; as partidas o leem como leem o histórico. A explicação completa de como ele é montado está em [Como o futuro é gerado](./futuro-gerado.md).

O botão **Gerar dados futuros** (depois da primeira geração, **Gerar outro futuro**) abre um diálogo com os controles à esquerda e a prévia à direita.

**Controles:**

- **"Até quando"**: cada série continua do dia útil seguinte ao seu último dado real.
- **"Semente"**: um número que fixa o sorteio. A mesma semente com os mesmos controles gera sempre o mesmo futuro. "Sortear" escolhe outra semente, e outro futuro igualmente plausível.
- **"Temperatura"**, de 0 a 3, padrão 1. Mede o quanto o futuro se parece com as piores crises do histórico. Em 1, o futuro respeita o histórico como foi. Em 2, a maior queda do Ibovespa dentro de um ano (do topo até o fundo) passa de 30% em 64 de cada 100 anos; uma queda assim leva, por exemplo, de 100.000 para 65.000 pontos. Em 3, é crise permanente.
- **"Começar em"**: hoje, calmaria, normal ou crise. É o clima do primeiro trimestre do futuro. Com "Hoje", ele é o clima em que o mercado real está.
- **"Choque de inflação"**, de −5 a +20 pontos, padrão 0. Soma pontos à inflação de 12 meses, isto é, quanto os preços subiram nos últimos 12 meses: 4% quer dizer que algo que custava R$ 100 passou a custar R$ 104. Com +10, a inflação de 12 meses chega a uns 14% e a SELIC a 28% ao ano.

**Prévia.** Gera o futuro sem gravar nada. Mostra o Ibovespa e um ativo à escolha, SELIC e inflação, além de quatro números:

- **Quanto o Ibovespa termina acima ou abaixo de hoje.** Ex.: de 100.000 para 120.000 pontos é uma alta de 20%.
- **A maior queda do pico ao fundo.** A maior queda do Ibovespa entre o ponto mais alto e o ponto mais baixo que vem depois dele. Ex.: sobe de 100.000 para 120.000 e depois cai para 90.000; a queda é de 25% (de 120.000 para 90.000).
- **A SELIC no pico.** A taxa mais alta que chega no futuro. Ex.: hoje ela está em 13,65% ao ano e no pico chega a 28%.
- **A inflação de 12 meses no pico.** A mais alta do futuro. Ex.: 14% quer dizer que, em 12 meses, os preços subiram 14%.

O botão "Gerar e gravar" grava o futuro de todas as séries. Gravar de novo pede a confirmação "Trocar e gravar" e substitui o futuro anterior: não há como apagar o futuro sem gerar outro. Cancelar no meio, ou um erro, não muda nada na base.

Depois de gravar, a Central mostra o card "Futuro gerado", com a semente e os controles usados. O botão "Gerar de novo" abre o diálogo com esses valores.

**Partidas salvas.** Quem já jogou dias do futuro gerado guarda a própria cópia deles antes de qualquer troca. Por isso, uma partida salva continua igual ao que foi jogado.

### Atualização

- **Atualizar** (em um indicador) busca esse indicador na fonte na hora.
- **Atualizar desatualizadas** atualiza as ações cujo último preço tem mais de 2 dias. O número entre parênteses diz quantas são.
- Uma ação com dados desatualizados aparece com o nome em **vermelho** e o selo **Parou em**.

Quando o dado real chega (pelo "Atualizar" de uma série ou pela atualização automática dos indicadores ao abrir o app), ele ocupa o lugar do gerado nos dias que cobre, e um aviso diz quantos pregões entraram. O gerado que sobra continua do ponto antigo, então pode haver um salto no dia da emenda. O card "Futuro gerado" passa a avisar até onde o real chegou e sugere "Gerar de novo" com os mesmos controles, o que emenda todas as séries a partir do real novo.

Ao iniciar, o app também busca os indicadores sozinho, no máximo uma vez a cada 6 horas. Sem internet, os dados já guardados continuam valendo e o app segue funcionando normalmente.

---

## Métodos de Importação

### 1. Yahoo Finance (yfinance)

O simulador pode buscar dados diretamente do **Yahoo Finance** usando a biblioteca `yfinance`.

**Como importar:**

1. Acesse a **Central de dados** (botão no lobby)
2. No painel **Adicionar ativo**, deixe a fonte em **yFinance**
3. Informe o **Código do ativo** (ex: `PETR4`, `VALE3`, `BTC-USD`)
4. (Opcional) Marque **Substituir o que já existe**
5. Clique em **Importar**

**Exemplos de tickers brasileiros:**
- Ações: `VALE3`, `PETR4`, `BBAS3`, `ITUB4`
- FIIs: `XPML11`, `HGLG11`, `MXRF11`
- ETFs: `BOVA11` (Ibovespa), `SMAL11` (Small Caps)

O campo sugere os códigos da B3 enquanto você digita. O simulador guarda o código da B3 sem o sufixo `.SA` do Yahoo Finance e o acrescenta sozinho ao buscar; se você digitar `PETR4.SA`, ele vira `PETR4`. Cripto e ativos de outras bolsas (`BTC-USD`, `AAPL`) seguem como o Yahoo Finance os conhece.

:::warning Limitações do Yahoo Finance
A importação via Yahoo Finance depende da **API externa** deles, que pode ter:
- **Limitações de requisições** - Muitas requisições simultâneas podem ser bloqueadas
- **Indisponibilidade** - O serviço pode estar fora do ar temporariamente
- **Dados incompletos** - Alguns ativos podem não ter dados para todos os períodos
- **Atrasos** - Dados podem estar desatualizados (geralmente 1 dia de atraso)

Se você encontrar problemas, tente novamente mais tarde ou use a importação via CSV.
:::

---

### 2. Arquivo CSV Customizado

Você pode importar dados de qualquer fonte usando um **arquivo CSV** no formato aceito.

**Como importar:**

1. Prepare seu arquivo CSV no formato correto (veja abaixo)
2. Acesse a **Central de dados** (botão no lobby)
3. No painel **Adicionar ativo**, troque a fonte para **Arquivo CSV**
4. Arraste o arquivo para a área de upload ou escolha-o no computador. O limite é de 5 MB
5. Confira o **Código do ativo**: o painel o preenche com o nome do arquivo
6. (Opcional) Marque **Substituir o que já existe**
7. Clique em **Importar**

#### Formato do CSV

O arquivo segue o formato de exportação do **Investing.com** (histórico de preços, em CSV). As colunas **obrigatórias**, com estes nomes:

```csv
"Data","Último","Abertura","Máxima","Mínima","Vol."
"20.02.2026","25,00","24,88","25,48","24,86","30,94K"
"19.02.2026","25,00","24,78","25,30","24,62","23,22K"
"18.02.2026","24,74","24,79","25,00","24,30","26,93K"
```

**Especificações:**
- **Data** - Data no formato `dd.mm.aaaa` (ex: `20.02.2026`)
- **Último** - Preço de fechamento
- **Abertura** - Preço de abertura
- **Máxima** - Preço máximo
- **Mínima** - Preço mínimo
- **Vol.** - Volume negociado; aceita os sufixos `K` (mil) e `M` (milhão), como `30,94K`

**Regras:**
- ✅ Primeira linha deve ser o cabeçalho (nome das colunas)
- ✅ Valores numéricos usam `,` (vírgula) como separador decimal
- ✅ O arquivo precisa ser um CSV de até 5 MB. Outro tipo de arquivo é recusado com um aviso
- ⚠️ Valores ausentes viram zero e o servidor registra um aviso no log

**Exemplo de arquivo CSV válido:**

[📄 Baixe o arquivo de exemplo](/csv/exemplo-importacao-ohlcv.csv)


## Dicas Rápidas

- Use **Substituir o que já existe** quando quiser trocar os preços de um ticker que já está na base. Desmarcado, só entram os pregões que ainda não estão lá.
- A importação só pede confirmação quando vai substituir dados que já existem.
- Antes de escolher o período no lobby, confira na **Central de dados** até quando cada série tem dado real.
