import { useEffect, useState } from "react";
import { useDebouncedCallback } from "use-debounce";

const AUTOSAVE_DELAY_MS = 600;

type AutosaveOptions = {
  /** O rascunho difere do que o servidor guarda */
  dirty: boolean;
  /** O que falta preencher para o rascunho poder ser gravado; nulo quando está completo */
  incomplete: string | null;
  /** O rascunho serializado: cada mudança dele reinicia a contagem do salvamento */
  signature: string;
  /** Grava o rascunho atual; roda no render mais recente, então lê o estado já atualizado */
  save: () => Promise<unknown>;
};

/** Salva o rascunho sozinho, um instante depois da última mudança, e conta o que está em curso, a recusa e a nova tentativa. */
export function useAutosave({ dirty, incomplete, signature, save }: AutosaveOptions) {
  const [pending, setPending] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    setError(null);
    setPending((count) => count + 1);
    try {
      await save();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setPending((count) => count - 1);
    }
  };

  const debounced = useDebouncedCallback(run, AUTOSAVE_DELAY_MS);
  const ready = dirty && incomplete === null;

  useEffect(() => {
    if (ready) void debounced();
  }, [ready, signature, debounced]);

  // Trocar de aba ou fechar o diálogo grava o que ainda esperava a contagem
  useEffect(() => () => void debounced.flush(), [debounced]);

  return {
    saving: pending > 0 || (ready && error === null),
    error,
    incomplete: dirty ? incomplete : null,
    retry: () => void run(),
    flush: () => void debounced.flush(),
  };
}
