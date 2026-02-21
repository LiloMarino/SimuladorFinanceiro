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
          id: "api/import-assets-json-api-import-assets-yfinance-post",
          label: "Importar dados de yfinance",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "api/import-assets-csv-api-import-assets-csv-post",
          label: "Importar dados de CSV",
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
          id: "api/stream-api-stream-get",
          label: "Stream de eventos SSE",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "api/update-subscription-api-update-subscription-post",
          label: "Atualizar inscrição de eventos",
          className: "api-method post",
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
          id: "api/get-statistics-api-statistics-get",
          label: "Obter estatísticas de desempenho",
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
          label: "Continuar simulação",
          className: "api-method post",
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
  ],
};

export default sidebar.apisidebar;
