/** Descrição curta, em português, de cada status HTTP que a API devolve. */
const HTTP_STATUS_TEXT: Record<number, string> = {
  400: "requisição inválida",
  401: "não autorizado",
  403: "acesso negado",
  404: "não encontrado",
  405: "método não permitido",
  408: "tempo esgotado",
  409: "conflito",
  413: "arquivo grande demais",
  415: "tipo de arquivo não aceito",
  422: "dados inválidos",
  423: "sala fechada para você",
  429: "muitas requisições",
  500: "o servidor falhou",
  502: "o servidor não respondeu",
  503: "servidor indisponível",
  504: "o servidor demorou demais",
};

/** Status 0 é a requisição que não chegou a ter resposta: servidor desligado ou fora da rede. */
export const NETWORK_ERROR_STATUS = 0;

/** Falha do servidor ou da rede: o pedido em si pode estar certo e valer de novo. */
export const isConnectionFailure = (status: number) => status === NETWORK_ERROR_STATUS || status >= 500;

/** O que dizer ao jogador quando a API não manda mensagem própria. */
export function defaultErrorMessage(status: number): string {
  if (isConnectionFailure(status)) return "O servidor não respondeu";
  if (status === 400 || status === 422) return "Os dados enviados não são válidos";
  if (status === 401) return "Sua sessão expirou";
  if (status === 403) return "Você não tem permissão para isso";
  if (status === 404) return "Não encontrado";
  if (status === 409) return "Conflito com o estado atual";
  return "Algo deu errado";
}

export default class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.status = status;
    this.body = body;
  }

  /** Linha técnica que acompanha a mensagem, ex.: "Erro 500 · o servidor falhou". */
  get statusLine(): string {
    if (this.status === NETWORK_ERROR_STATUS) return "Sem conexão com o servidor do host";
    return `Erro ${this.status} · ${HTTP_STATUS_TEXT[this.status] ?? "erro desconhecido"}`;
  }
}
