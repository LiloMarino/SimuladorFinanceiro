import type { LucideIcon } from "lucide-react";

/** Item de navegação (menu lateral, abas etc.) */

export interface NavItem {
  key: string;
  label: string;
  endpoint: string;
  icon: LucideIcon;
  group: "Mercado" | "Você" | "Expansões" | "Ferramentas";
  badge?: string;
  /** `warning`: selo âmbar (ferramentas de debug) */
  badgeTone?: "warning";
  /** Só aparece com o modo debug ligado e para o host */
  debugOnly?: boolean;
  /** Só aparece nas partidas com meta (fora da Clássica); o selo mostra o seu percentual */
  goalOnly?: boolean;
  /** O selo mostra o placar de conquistas ("9/24"), com um ponto dourado quando há alguma nova */
  achievementTally?: boolean;
  /** Ponto vermelho no item enquanto há parcela em atraso ou sem caixa para cobrir */
  creditAlert?: boolean;
  /** O selo mostra o modo do jogador (Ligada/Desligada), com um ponto vermelho quando a estratégia deu erro e o erro não foi visto */
  strategyStatus?: boolean;
  /** Abre a janela Como jogar em vez de navegar; só aparece quando o jogador escolheu o acesso pelo menu */
  tutorial?: boolean;
  /** Só aparece nas partidas com a expansão ligada */
  expansion?: "government";
}

export type RedirectState = {
  from?: {
    pathname: string;
  };
};
