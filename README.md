<div align="center">

<img src="docs/static/img/logo.svg" alt="Logo do Simulador Financeiro" width="96" height="96">

# Simulador Financeiro

**Invista no mercado brasileiro com preços reais, numa sala com seus amigos.**

[![Licença: GPL v3](https://img.shields.io/badge/licença-GPLv3-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Download](https://img.shields.io/github/v/release/LiloMarino/SimuladorFinanceiro?include_prereleases&label=download)](https://github.com/LiloMarino/SimuladorFinanceiro/releases)

[Download](#download) · [Documentação](https://lilomarino.github.io/SimuladorFinanceiro/) · [Novidades de cada versão](CHANGELOG.md)

![O jogo rodando: o tempo da simulação avança e a carteira acompanha](https://github.com/LiloMarino/SimuladorFinanceiro/raw/demo/gifs/time.gif)

</div>

O Simulador Financeiro é um jogo de investimentos inspirado em jogos de estratégia como Capitalism Lab e Victoria 3. Você recebe um capital, escolhe onde aplicar e acompanha o resultado enquanto o tempo da simulação passa, dia a dia, sobre os preços históricos da bolsa brasileira. Pode jogar sozinho ou numa sala com amigos. A partida pode ser clássica (jogar até a data final), uma corrida até uma meta de patrimônio ou uma partida de viver de renda, com salário e despesas.

Acesso antecipado: o jogo já roda, mas ainda muda a cada versão. Em português, voltado ao mercado brasileiro.

## O que ele faz

### Renda variável

Compre e venda ações, FIIs e ETFs com cotações históricas reais. O gráfico de cada ativo avança com o tempo da simulação, e o imposto de renda sobre as vendas é calculado como no Brasil.

![Tela de renda variável com a lista de ativos e o gráfico de preços](https://github.com/LiloMarino/SimuladorFinanceiro/raw/demo/gifs/stocks.gif)

### Renda fixa

Aplique em CDB, LCI, LCA e Tesouro Direto. Os títulos rendem sobre CDI, SELIC e IPCA, que também acompanham o tempo da simulação.

![Tela de renda fixa com a lista de títulos e a aplicação em um deles](https://github.com/LiloMarino/SimuladorFinanceiro/raw/demo/gifs/fixed-income.gif)

### Estatísticas

Acompanhe a evolução do patrimônio e como cada decisão pesou no resultado: retorno, volatilidade e comparação com os índices do mercado.

![Tela de estatísticas com a evolução do patrimônio](https://github.com/LiloMarino/SimuladorFinanceiro/raw/demo/gifs/statistics.gif)

### Multiplayer

Um jogador abre a sala e os amigos entram pelo endereço dele. Todos começam com o mesmo capital e jogam sobre o mesmo tempo simulado. Quem vence depende da regra escolhida no lobby, como o maior patrimônio ou a melhor nota de retorno e risco.

![Lobby da sala, com os jogadores e o convite](https://github.com/LiloMarino/SimuladorFinanceiro/raw/demo/gifs/lobby.gif)

### E também

- **Carteira**: patrimônio, alocação por classe e imposto de renda num só lugar.
- **Meta**: nas partidas de corrida à meta e de viver de renda, o seu progresso até a meta e a distância para os outros jogadores.
- **Conquistas**: objetivos que a partida vai liberando enquanto você joga.
- **Correlação**: o quanto os ativos andam juntos, para diversificar de verdade.
- **Futuro gerado**: depois do último pregão real, o simulador gera um futuro plausível para a partida seguir.
- **Importação de ativos**: traga o histórico de outros ativos para jogar com eles.
- **Estratégias automáticas**: em breve.

## Download

Baixe o arquivo do seu sistema na página de [Releases](https://github.com/LiloMarino/SimuladorFinanceiro/releases) e abra. O navegador abre sozinho em `http://localhost:8000`. Não precisa instalar Python nem Node.js.

| Sistema | Arquivo | O que mais precisa |
|---|---|---|
| Windows | `SimuladorFinanceiro-windows.exe` | Nada, o banco de dados já vem dentro. Se o Windows avisar que falta uma DLL do Visual C++, instale o `vc_redist.x64.exe` da mesma página. |
| Linux | `SimuladorFinanceiro-linux` | PostgreSQL instalado e um arquivo `.env` configurado. |
| macOS | `SimuladorFinanceiro-macos` | PostgreSQL instalado e um arquivo `.env` configurado. |

O passo a passo de cada sistema está na [página de instalação](https://lilomarino.github.io/SimuladorFinanceiro/como-usar/instalacao).

## Documentação

O [site da documentação](https://lilomarino.github.io/SimuladorFinanceiro/) tem um tour pelo jogo, um guia de cada tela e a documentação para quem desenvolve.

## Desenvolvimento

Precisa de [uv](https://docs.astral.sh/uv/), Node.js, pnpm e um PostgreSQL.

```bash
git clone https://github.com/LiloMarino/SimuladorFinanceiro.git
cd SimuladorFinanceiro
pnpm install     # ferramentas da raiz
pnpm run setup   # dependências do backend e do frontend
pnpm dev         # backend e frontend juntos
```

O frontend abre em `http://localhost:5173`. Configure o banco no `.env` (modelo em `example.env`) antes do primeiro `pnpm dev`. `pnpm setup`, sem o `run`, é um comando do próprio pnpm e não roda o script do projeto.

O guia completo está em [Desenvolvimento](https://lilomarino.github.io/SimuladorFinanceiro/desenvolvimento/setup), e as regras para contribuir em [Contribuindo](https://lilomarino.github.io/SimuladorFinanceiro/desenvolvimento/contribuindo). Bugs vão em [Issues](../../issues) e ideias em [Discussions](../../discussions).

## Licença

[GNU General Public License v3.0](LICENSE). Você pode usar, modificar e distribuir, mantendo a mesma licença e os créditos.

---

<div align="center">

Desenvolvido por [Murilo Marino](https://github.com/LiloMarino)

</div>
