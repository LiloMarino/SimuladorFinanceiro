import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebar: SidebarsConfig = {
  apisidebar: [
    {
      type: "doc",
      id: "api/simulador-financeiro",
    },
    {
      type: "category",
      label: "Operations",
      items: [
        {
          type: "doc",
          id: "api/get-variable-income-api-variable-income-get",
          label: "Listar ativos de renda variável",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-variable-income-details-api-variable-income-asset-get",
          label: "Obter detalhes de um ativo",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/submit-order-api-variable-income-asset-orders-post",
          label: "Submeter ordem de compra/venda",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/cancel-order-api-variable-income-asset-orders-delete",
          label: "Cancelar ordem",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/list-order-book-api-variable-income-asset-orders-get",
          label: "Listar ordens do livro",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/preview-order-api-variable-income-asset-order-preview-post",
          label: "Prévia de uma ordem",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/list-trades-api-variable-income-asset-trades-get",
          label: "Execuções da sala no ativo",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-fixed-income-api-fixed-income-get",
          label: "Listar ativos de renda fixa",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-fixed-income-details-api-fixed-income-asset-uuid-get",
          label: "Obter detalhes de renda fixa",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-fixed-income-projection-api-fixed-income-asset-uuid-projection-get",
          label: "Projetar investimento em renda fixa",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/buy-fixed-income-api-fixed-income-asset-uuid-buy-post",
          label: "Comprar ativo de renda fixa",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Portfolio",
      items: [
        {
          type: "doc",
          id: "api/get-portfolio-api-portfolio-get",
          label: "Obter portfólio",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-patrimonial-history-api-portfolio-history-get",
          label: "Obter histórico patrimonial",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-cash-api-portfolio-cash-get",
          label: "Obter saldo em caixa",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-portfolio-ticker-api-portfolio-ticker-get",
          label: "Obter posição de um ativo",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Settings",
      items: [
        {
          type: "doc",
          id: "api/get-settings-api-settings-get",
          label: "Obter configurações do usuário",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/update-settings-api-settings-put",
          label: "Atualizar configurações do usuário",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "Import Assets",
      items: [
        {
          type: "doc",
          id: "api/get-coverage-api-import-assets-coverage-get",
          label: "Cobertura das séries",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/refresh-all-indicators-api-import-assets-indicators-post",
          label: "Atualizar todos os indicadores",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/refresh-one-indicator-api-import-assets-indicators-series-post",
          label: "Atualizar um indicador",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/update-asset-class-api-import-assets-stocks-ticker-asset-class-put",
          label: "Alterar a classe de um ativo",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "api/update-segment-api-import-assets-stocks-ticker-segment-put",
          label: "Classificar um ativo por setor e segmento",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "api/delete-segment-api-import-assets-stocks-ticker-segment-delete",
          label: "Remover a classificação de um ativo",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/get-sectors-api-import-assets-sectors-get",
          label: "Setores e segmentos",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/import-assets-json-api-import-assets-yfinance-post",
          label: "Importar dados de yfinance",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/import-assets-batch-api-import-assets-yfinance-batch-post",
          label: "Importar dados de múltiplos ativos via yfinance",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/import-assets-csv-api-import-assets-csv-post",
          label: "Importar dados de CSV",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-segment-suggestion-api-import-assets-stocks-ticker-suggestion-get",
          label: "Sugestão de setor do yfinance",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/refresh-stock-profile-api-import-assets-stocks-ticker-profile-refresh-post",
          label: "Atualizar o perfil do ativo",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-ticker-suggestions-api-import-assets-tickers-get",
          label: "Sugestão de código de ativo",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-generated-future-api-import-assets-future-get",
          label: "Futuro gerado",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/record-future-api-import-assets-future-post",
          label: "Gravar o futuro",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/preview-future-api-import-assets-future-preview-post",
          label: "Prévia do futuro",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/cancel-future-recording-api-import-assets-future-cancel-post",
          label: "Cancelar a gravação do futuro",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Realtime",
      items: [
        {
          type: "doc",
          id: "api/get-realtime-events-schema-api-internal-realtime-events-schema-get",
          label: "[DEV] Catálogo de payloads de eventos realtime",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Simulation Control",
      items: [
        {
          type: "doc",
          id: "api/set-speed-api-set-speed-post",
          label: "Definir velocidade da simulação",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-simulation-state-api-get-simulation-state-get",
          label: "Obter estado da simulação",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Authentication",
      items: [
        {
          type: "doc",
          id: "api/session-init-api-session-init-post",
          label: "Inicializa a sessão",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/session-me-api-session-me-get",
          label: "Obter dados da sessão",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/session-logout-api-session-logout-post",
          label: "Logout do cliente",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/user-register-api-user-register-post",
          label: "Registrar novo usuário",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/user-claim-api-user-claim-post",
          label: "Recuperar usuário existente",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/user-delete-api-user-delete",
          label: "Deletar usuário",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Statistics",
      items: [
        {
          type: "doc",
          id: "api/get-overview-api-statistics-overview-get",
          label: "Estatísticas: geral",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-highlights-api-statistics-highlights-get",
          label: "Estatísticas: destaques",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-returns-api-statistics-returns-get",
          label: "Estatísticas: rentabilidade",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-risk-api-statistics-risk-get",
          label: "Estatísticas: risco",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-composition-api-statistics-composition-get",
          label: "Estatísticas: composição",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-operations-api-statistics-operations-get",
          label: "Estatísticas: operações",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-economic-indicators-api-economic-indicators-get",
          label: "Obter indicadores econômicos",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Correlation",
      items: [
        {
          type: "doc",
          id: "api/get-correlation-assets-api-correlation-assets-get",
          label: "Ativos da correlação",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-correlation-api-correlation-get",
          label: "Matriz de correlação",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Simulation",
      items: [
        {
          type: "doc",
          id: "api/simulation-status-api-simulation-status-get",
          label: "Obter status da simulação",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/create-simulation-api-simulation-create-post",
          label: "Criar nova simulação",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/continue-simulation-api-simulation-continue-post",
          label: "Continuar a simulação selecionada",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/select-simulation-api-simulation-selection-put",
          label: "Selecionar simulação salva",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "api/clear-selection-api-simulation-selection-delete",
          label: "Remover a seleção da simulação salva",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/delete-simulation-api-simulation-simulation-id-delete",
          label: "Excluir simulação salva",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "api/list-simulations-api-simulation-list-get",
          label: "Listar simulações salvas",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/price-impact-preview-api-simulation-price-impact-preview-get",
          label: "Prévia do impacto de preço",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/stop-simulation-api-simulation-stop-post",
          label: "Parar simulação",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-active-players-api-simulation-players-get",
          label: "Listar jogadores ativos",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/set-player-color-api-simulation-players-me-color-put",
          label: "Escolher a cor do jogador",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "api/set-player-team-api-simulation-players-me-team-put",
          label: "Escolher a equipe do jogador",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "api/distribute-teams-api-simulation-teams-distribute-post",
          label: "Distribuir quem falta nas equipes",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-match-players-api-simulation-match-players-get",
          label: "Listar jogadores da partida em andamento",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-goal-progress-api-simulation-goal-progress-get",
          label: "Progresso da corrida à meta",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-life-status-api-simulation-life-get",
          label: "Vida financeira do jogador",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/get-life-history-api-simulation-life-history-get",
          label: "Histórico do viver de renda",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/join-match-api-simulation-join-post",
          label: "Entrar na partida em andamento",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-simulation-settings-api-simulation-settings-get",
          label: "Obter configurações da simulação",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/update-simulation-settings-api-simulation-settings-put",
          label: "Atualizar configurações da simulação",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "Tunnel",
      items: [
        {
          type: "doc",
          id: "api/start-tunnel-api-tunnel-start-post",
          label: "Iniciar túnel",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/stop-tunnel-api-tunnel-stop-post",
          label: "Parar túnel",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/get-tunnel-status-api-tunnel-status-get",
          label: "Obter status do túnel",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Version",
      items: [
        {
          type: "doc",
          id: "api/get-app-version-api-version-get",
          label: "Obter a versão do app",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Debug",
      items: [
        {
          type: "doc",
          id: "api/get-metrics-api-debug-metrics-get",
          label: "Medições de desempenho",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/reset-metrics-api-debug-metrics-reset-post",
          label: "Zerar as medições",
          className: "api-method post",
        },
      ],
    },
  ],
};

export default sidebar.apisidebar;
