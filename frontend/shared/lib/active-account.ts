import type { FundAccount } from "@/types";

/** O cabeçalho que diz ao servidor por qual conta a ordem sai; a conta pessoal não o envia. */
const ACCOUNT_HEADER = "X-Account";

// Por partida: a conta escolhida vive na memória e é lembrada no navegador
const selection = new Map<number, number | null>();
const listeners = new Set<() => void>();

const storageKey = (simulationId: number) => `active-account:${simulationId}`;

function loadFundId(simulationId: number): number | null {
  try {
    const saved = localStorage.getItem(storageKey(simulationId));
    const fundId = saved === null ? Number.NaN : Number(saved);
    return Number.isInteger(fundId) ? fundId : null;
  } catch {
    return null;
  }
}

/** A gestora escolhida na partida; `null` é a conta pessoal. */
export function getSelectedFundId(simulationId: number): number | null {
  if (!selection.has(simulationId)) selection.set(simulationId, loadFundId(simulationId));
  return selection.get(simulationId) ?? null;
}

export function selectFund(simulationId: number, fundId: number | null) {
  selection.set(simulationId, fundId);
  try {
    if (fundId === null) localStorage.removeItem(storageKey(simulationId));
    else localStorage.setItem(storageKey(simulationId), String(fundId));
  } catch {
    // Sem armazenamento (aba privada, dados bloqueados): a escolha só vale até recarregar
  }
  listeners.forEach((listener) => listener());
}

export function subscribeActiveAccount(listener: () => void) {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/**
 * A conta em uso: a escolhida, se ainda está na lista; senão a pessoal.
 * Sem lista (expansão desligada ou ainda carregando) a escolha não vale.
 */
export function resolveActiveAccount(accounts: FundAccount[] | undefined, selectedFundId: number | null) {
  const personal = accounts?.find((account) => account.fund_id === null);
  const selected = accounts?.find((account) => account.fund_id !== null && account.fund_id === selectedFundId);
  return selected ?? personal;
}

/**
 * Cabeçalhos da conta para a requisição. Com a lista já carregada, só uma gestora que ela traz
 * é enviada; antes da lista, a escolha lembrada segue valendo.
 */
export function accountHeaders(selectedFundId: number | null, accounts: FundAccount[] | undefined) {
  if (selectedFundId === null) return {};
  const known = accounts === undefined || accounts.some((account) => account.fund_id === selectedFundId);
  return known ? { [ACCOUNT_HEADER]: String(selectedFundId) } : {};
}
