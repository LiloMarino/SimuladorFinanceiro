const HTTP_STATUS_TEXT: Record<number, string> = {
  400: "Bad Request",
  401: "Unauthorized",
  403: "Forbidden",
  404: "Not Found",
  405: "Method Not Allowed",
  408: "Request Timeout",
  409: "Conflict",
  413: "Payload Too Large",
  415: "Unsupported Media Type",
  422: "Unprocessable Entity",
  429: "Too Many Requests",
  500: "Internal Server Error",
  502: "Bad Gateway",
  503: "Service Unavailable",
  504: "Gateway Timeout",
};

/** Status 0 é a requisição que não chegou a ter resposta: servidor desligado ou fora da rede. */
export const NETWORK_ERROR_STATUS = 0;

/** O que dizer ao jogador quando a API não manda mensagem própria. */
export function defaultErrorMessage(status: number): string {
  if (status === NETWORK_ERROR_STATUS || status >= 500) return "O servidor não respondeu";
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

  /** Linha técnica que acompanha a mensagem, ex.: "Erro 500 · Internal Server Error". */
  get statusLine(): string {
    if (this.status === NETWORK_ERROR_STATUS) return "Sem resposta do servidor";
    return `Erro ${this.status} · ${HTTP_STATUS_TEXT[this.status] ?? "Unknown Error"}`;
  }
}
