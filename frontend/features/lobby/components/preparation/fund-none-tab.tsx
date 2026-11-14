import { useSetFundPreparation } from "../../hooks/mutations/useSetFundPreparation";
import { useAutosave } from "../../hooks/useAutosave";
import { Button } from "@/shared/components/ui/button";
import { FundMark } from "@/shared/components/fund-mark";
import { Badge } from "@/shared/components/ui/badge";
import { rivalFunds } from "../../lib/fund-preparation";
import { FundConflictsAlert, FundRoomSection } from "./fund-room-section";
import { PreparationFooter } from "./preparation-footer";
import { PreparationSection } from "./preparation-section";
import type { FundModeProps } from "./fund-tab";

const TIMELINE = [
  {
    when: "Aqui, na sala",
    title: "Preparar e fundar no 1º dia",
    text: "Escolha “Fundar a minha gestora”: nome e sigla ficam no perfil, e ela nasce vazia no 1º dia.",
  },
  {
    when: "Na partida",
    title: "Fundar depois",
    text: "Pelo item Gestoras do menu, em qualquer dia, levando caixa, ações e títulos.",
  },
];

/** Sem gestora: o que continua possível dentro da partida, a gestora salva no perfil e as gestoras da sala. */
export function FundNoneTab({
  preparations,
  saved,
  humans,
  nickname,
  savedSimulation,
  lead,
  locked,
  onMode,
  onClose,
}: FundModeProps) {
  const prepare = useSetFundPreparation();
  const mine = preparations.funds.some((fund) => fund.nickname === nickname);
  // Sem preparação gravada o servidor já trata o jogador como sem gestora
  const autosave = useAutosave({
    dirty: !locked && mine,
    incomplete: null,
    signature: "NONE",
    save: () => prepare.mutateAsync({ kind: "NONE" }),
  });
  const rivals = rivalFunds(preparations, nickname);

  return (
    <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 content-start gap-4.5 overflow-y-auto px-6 py-5">
        {lead}
        <fieldset
          disabled={locked}
          className="grid min-w-0 grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] items-start gap-6 disabled:opacity-55"
        >
          {/* Linha do tempo */}
          <div className="grid min-w-0 gap-3">
            <div className="grid gap-0.5">
              <b className="text-sm font-semibold">Você começa a partida sem gestora</b>
              <span className="text-[13px] text-muted-foreground">
                Nada muda no seu caixa. A gestora continua possível dentro da partida.
              </span>
            </div>
            <ol className="grid">
              {TIMELINE.map((step) => (
                <li key={step.title} className="grid grid-cols-[6.5rem_1fr] gap-3 border-t border-muted py-2.5">
                  <span className="font-mono text-xs text-muted-foreground">{step.when}</span>
                  <div className="grid gap-0.5">
                    <b className="text-[13px] font-semibold">{step.title}</b>
                    <span className="text-xs text-muted-foreground">{step.text}</span>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          <div className="grid min-w-0 gap-4.5">
            {/* Gestora salva no perfil */}
            <PreparationSection title="Sua gestora" hint="salva no perfil">
              {saved ? (
                <div className="grid gap-2.5 rounded-[10px] border p-3">
                  <div className="flex items-center gap-2.5">
                    <FundMark name={saved.name} />
                    <b className="min-w-0 truncate text-sm font-semibold" title={saved.name}>
                      {saved.name}
                    </b>
                    <Badge variant="fund" numeric size="sm">
                      {saved.ticker}
                    </Badge>
                  </div>
                  <Button
                    type="button"
                    variant="fund"
                    size="sm"
                    className="justify-self-start"
                    onClick={() => onMode("FOUND")}
                  >
                    Fundar nesta sala
                  </Button>
                  <span className="text-xs text-muted-foreground">
                    Fundar troca a escolha para “Fundar a minha gestora” com este nome e esta sigla.
                  </span>
                </div>
              ) : (
                <div className="grid gap-2 rounded-[10px] border border-dashed border-input p-3">
                  <b className="text-[13px] font-semibold">Você ainda não montou a sua gestora</b>
                  <span className="text-xs text-muted-foreground">
                    Nome e sigla ficam no perfil e voltam prontos nas próximas salas.
                  </span>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="justify-self-start"
                    onClick={() => onMode("FOUND")}
                  >
                    Montar em Fundar a minha gestora
                  </Button>
                </div>
              )}
            </PreparationSection>

            <FundRoomSection rivals={rivals} humans={humans} draft={{ name: "", ticker: "" }} />
          </div>
        </fieldset>

        <FundConflictsAlert conflicts={preparations.fund_conflicts} />
      </div>

      <PreparationFooter
        note={
          savedSimulation
            ? "Travado com partida salva selecionada."
            : "Fica no seu perfil: a escolha de começar sem gestora."
        }
        saving={autosave.saving}
        error={autosave.error}
        incomplete={autosave.incomplete}
        onRetry={autosave.retry}
        onClose={onClose}
      />
    </div>
  );
}
