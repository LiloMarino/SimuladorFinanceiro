export class RealtimeConnectionManager {
  private connected = false;
  private connectListeners = new Set<() => void>();
  private disconnectListeners = new Set<() => void>();

  /**
   * Verifica se a conexão está ativa.
   */
  public isConnected(): boolean {
    return this.connected;
  }

  /**
   * Registra um callback para quando a conexão for estabelecida.
   */
  public onConnect(cb: () => void): () => void {
    this.connectListeners.add(cb);
    return () => this.connectListeners.delete(cb);
  }

  /**
   * Registra um callback para quando a conexão for encerrada.
   */
  public onDisconnect(cb: () => void): () => void {
    this.disconnectListeners.add(cb);
    return () => this.disconnectListeners.delete(cb);
  }

  /**
   * Atualiza o estado da conexão e notifica listeners se houve mudança.
   */
  public setConnected(value: boolean): void {
    if (this.connected === value) return;

    this.connected = value;

    const listeners = value ? this.connectListeners : this.disconnectListeners;

    listeners.forEach((cb) => cb());
  }
}
