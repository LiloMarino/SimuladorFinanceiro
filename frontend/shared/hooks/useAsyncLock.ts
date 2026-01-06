import { useRef } from "react";
import { Mutex } from "async-mutex";

/**
 * Hook de Lock assíncrono
 */
export function useAsyncLock() {
  // Mutex é estável, então podemos manter a mesma instância
  const mutexRef = useRef<Mutex>(new Mutex());

  /**
   * Executa o callback dentro do lock.
   * Se já estiver rodando outro callback, espera ele terminar antes de executar.
   * @param fn Callback assíncrono
   */
  const runExclusive = async <T>(fn: () => Promise<T>): Promise<T> => {
    return mutexRef.current.runExclusive(fn);
  };

  /**
   * Retorna true se algum callback estiver rodando no momento.
   */
  const isLocked = () => mutexRef.current.isLocked();

  return { runExclusive, isLocked };
}
