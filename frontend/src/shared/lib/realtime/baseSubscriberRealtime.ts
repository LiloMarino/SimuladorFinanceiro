/** Representa uma chave válida de evento (ex: "price_update", "user_joined") */
type EventKey<T> = keyof T;

/** Representa uma função callback associada a um evento específico */
type EventCallback<T, K extends keyof T> = (data: T[K]) => void;

/**
 * Base para qualquer cliente de eventos em tempo real (SSE ou WebSocket).
 *
 * Gerencia callbacks locais e mantém o backend informado sobre quais eventos
 * o cliente deseja receber.
 *
 * TEvents representa o conjunto de eventos disponíveis.
 * Exemplo:
 * type MyEvents = {
 *   price_update: { symbol: string; value: number };
 *   user_joined: { name: string };
 * };
 */
export abstract class BaseSubscriberRealtime<TEvents extends Record<string, unknown> = Record<string, unknown>> {
  /**
   * Estrutura de dados que mapeia cada tipo de evento para um conjunto de callbacks.
   *
   * Exemplo:
   * ```
   * {
   *   "price_update" => Set([cb1, cb2]),
   *   "user_joined"  => Set([cb3])
   * }
   * ```
   *
   * A escolha por `Set` evita duplicação de callbacks e facilita a remoção.
   */
  protected listeners = new Map<EventKey<TEvents>, Set<EventCallback<TEvents, EventKey<TEvents>>>>();
  protected clientId: string = crypto.randomUUID();

  /**
   * Responsável por abrir a conexão com o servidor (ex: via WebSocket ou SSE)
   * e acionar `notify(event, data)` sempre que uma nova mensagem for recebida.
   *
   * @param url - Endereço da fonte de eventos (opcional)
   */
  public abstract connect(url?: string): void;

  /**
   * Registra um novo callback para um determinado tipo de evento.
   *
   * @param event - Nome do evento a ser escutado
   * @param cb - Função a ser chamada sempre que o evento ocorrer
   * @returns Uma função que, ao ser chamada, remove a inscrição (unsubscribe)
   */
  public subscribe<K extends EventKey<TEvents>>(event: K, cb: EventCallback<TEvents, K>): () => void {
    // Caso o evento ainda não tenha callbacks registrados, inicializa um novo Set
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }

    // Adiciona o callback ao conjunto de ouvintes do evento
    this.listeners.get(event)?.add(cb as EventCallback<TEvents, EventKey<TEvents>>);

    // Atualiza backend sobre os eventos atuais
    this.updateBackendSubscription();

    // Retorna função para desinscrição
    return () => this.unsubscribe(event, cb);
  }

  /**
   * Cancela a inscrição de um callback específico para um determinado evento.
   *
   * @param event - Nome do evento
   * @param cb - Callback previamente registrado em `subscribe()`
   */
  public unsubscribe<K extends EventKey<TEvents>>(event: K, cb: EventCallback<TEvents, K>): void {
    // Remove o callback correspondente do conjunto de ouvintes do evento
    this.listeners.get(event)?.delete(cb as EventCallback<TEvents, EventKey<TEvents>>);

    // Atualiza backend sobre os eventos atuais
    this.updateBackendSubscription();
  }

  /**
   * Notifica todos os inscritos de que um evento ocorreu.
   *
   * @param event - Nome do evento ocorrido
   * @param data - Dados enviados junto ao evento
   */
  protected notify<K extends EventKey<TEvents>>(event: K, data: TEvents[K]): void {
    // Executa cada callback associado ao evento, passando os dados recebidos
    this.listeners.get(event)?.forEach((cb) => (cb as EventCallback<TEvents, K>)(data));
  }

  /**
   * Informa o backend sobre os eventos que este cliente está inscrito
   */
  protected abstract updateBackendSubscription(): Promise<void>;
}
