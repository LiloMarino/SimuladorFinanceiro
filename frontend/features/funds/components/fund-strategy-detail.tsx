import { Power } from "lucide-react";
import { ActiveMark } from "@/shared/components/active-mark";
import { DisabledHint } from "@/shared/components/disabled-hint";
import { InfoHint } from "@/shared/components/info-hint";
import { StrategyDataBlock } from "@/shared/components/strategy-data-block";
import { StrategyParamsForm } from "@/shared/components/strategy-params-form";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { GROUP_LABEL } from "@/shared/lib/strategy-groups";
import {
  defaultValues,
  draftErrors,
  fromDraft,
  sameValues,
  toDraft,
  type ParamDraft,
  type ParamValues,
} from "@/shared/lib/strategy-params";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { BotTicker, MyStrategy, StrategyInfo } from "@/types";
import { useFundStrategyView } from "../hooks/queries/useFundStrategyView";

type FundStrategyDetailProps = {
  fundId: number;
  strategy: StrategyInfo;
  /** A configuração ligada desta estratégia; nulo se a carteira não a segue */
  active: MyStrategy["active"];
  /** Outra estratégia está ligada: ligar esta é trocar */
  otherActive: boolean;
  draft: ParamDraft;
  /** Caixa da gestora hoje, em reais */
  cash: string;
  currentDate: string | undefined;
  tickerOptions: BotTicker[];
  heldTickers: string[];
  saving: boolean;
  onDraftChange: (draft: ParamDraft) => void;
  onSave: (values: ParamValues) => void;
  onTurnOn: (values: ParamValues) => void;
};

/** A estratégia escolhida para a carteira da gestora: regra, parâmetros em rascunho e o que ela faria hoje. */
export function FundStrategyDetail({
  fundId,
  strategy,
  active,
  otherActive,
  draft,
  cash,
  currentDate,
  tickerOptions,
  heldTickers,
  saving,
  onDraftChange,
  onSave,
  onTurnOn,
}: FundStrategyDetailProps) {
  const defaults = defaultValues(strategy);
  const saved = active ? active.params : defaults;
  const values = fromDraft(strategy.params, draft);
  const changed = values === null || !sameValues(values, saved);

  const dataKind = strategy.view === "ranking" || strategy.view === "allocation" ? strategy.view : null;
  const dataView = useFundStrategyView(fundId, strategy.key, dataKind && values ? values : null, currentDate);
  const dataReady = !!dataView.data && !dataView.isPlaceholderData;

  // Erro do servidor (por campo) e o que a digitação ainda não permite
  const errors: Record<string, string> = dataReady ? { ...dataView.data.errors } : {};
  Object.assign(errors, draftErrors(strategy.params, draft));
  const valid = values !== null && Object.keys(errors).length === 0 && (!dataKind || dataReady);

  const blockedReason = saving
    ? null
    : values === null || Object.keys(errors).length > 0
      ? "Corrija os parâmetros marcados."
      : active && !changed
        ? "Mude algum parâmetro para salvar."
        : null;

  return (
    <div className="grid min-w-0 content-start">
      {/* Cabeçalho */}
      <div className="grid gap-1 px-5.5 py-4">
        <span className="flex items-center gap-2">
          <Badge variant={strategy.group === "tactic" ? "info" : "secondary"} size="tag">
            {GROUP_LABEL[strategy.group]}
          </Badge>
          {active ? (
            <ActiveMark since={displayDayMonth(active.since)} />
          ) : (
            <span className="text-xs text-muted-foreground">Desligada</span>
          )}
        </span>
        <h3 className="text-lg font-semibold">{strategy.name}</h3>
        <p className="flex items-start gap-1.5 text-[13px] text-muted-foreground">
          <span>{strategy.description}</span>
          {strategy.term_hint && <InfoHint label="O que isso quer dizer">{strategy.term_hint}</InfoHint>}
        </p>
      </div>

      {/* Parâmetros */}
      <div className="border-t px-5.5 py-3.5">
        {strategy.params.length > 0 ? (
          <StrategyParamsForm
            strategy={strategy}
            draft={draft}
            saved={saved}
            errors={errors}
            tickerOptions={tickerOptions}
            heldTickers={heldTickers}
            cash={cash}
            cashLabel="o caixa da gestora hoje"
            onChange={onDraftChange}
          />
        ) : (
          <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs text-muted-foreground">
            Esta estratégia não tem parâmetros: é ligar ou deixar desligada.
          </p>
        )}
      </div>

      {/* O que ela faria hoje */}
      {dataKind && (
        <div className="grid gap-2.5 border-t px-5.5 py-3.5">
          <span className="text-xs font-semibold text-muted-foreground">O que ela faria hoje</span>
          <StrategyDataBlock kind={dataKind} query={dataView} />
        </div>
      )}

      {/* Ações */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-t px-5.5 py-3.5">
        <span className="text-xs text-muted-foreground">
          {active && strategy.params.length > 0 ? "Vale a partir do próximo dia da partida." : ""}
        </span>
        <div className="flex gap-2">
          {strategy.params.length > 0 && (
            <Button
              variant="outline"
              disabled={values !== null && sameValues(values, defaults)}
              onClick={() => onDraftChange(toDraft(defaults))}
            >
              Restaurar padrão
            </Button>
          )}
          {active ? (
            strategy.params.length > 0 && (
              <DisabledHint reason={blockedReason}>
                <Button disabled={!valid || !changed || saving} onClick={() => values && onSave(values)}>
                  Salvar parâmetros
                </Button>
              </DisabledHint>
            )
          ) : (
            <DisabledHint reason={blockedReason}>
              <Button disabled={!valid || saving} onClick={() => values && onTurnOn(values)}>
                <Power />
                {otherActive ? "Trocar para esta estratégia" : "Ligar esta estratégia"}
              </Button>
            </DisabledHint>
          )}
        </div>
      </div>
    </div>
  );
}
