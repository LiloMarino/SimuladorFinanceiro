import { useState } from "react";
import { Info, TriangleAlert } from "lucide-react";
import { StrategyList } from "@/shared/components/strategy-list";
import { StrategyParamsForm } from "@/shared/components/strategy-params-form";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  defaultValues,
  draftErrors,
  fromDraft,
  profileValues,
  sameValues,
  toDraft,
  type ParamDraft,
} from "@/shared/lib/strategy-params";
import type { BotTicker, SavedStrategyParams, StrategyInfo } from "@/types";
import { useSaveStrategyParams } from "../../hooks/mutations/useSaveStrategyParams";
import { useAutosave } from "../../hooks/useAutosave";
import { adjustedStrategies } from "../../lib/preparation";
import { PreparationFooter } from "./preparation-footer";

type StrategiesTabProps = {
  strategies: StrategyInfo[];
  saved: SavedStrategyParams;
  tickers: BotTicker[];
  /** O saldo inicial da sala, para o exemplo em reais dos parâmetros */
  startingCash: string;
  onClose: () => void;
};

/** Aba Estratégias: os parâmetros de cada estratégia que o automático usa em toda partida. */
export function StrategiesTab({ strategies, saved, tickers, startingCash, onClose }: StrategiesTabProps) {
  const profile = (strategy: StrategyInfo) => profileValues(strategy, saved[strategy.key], tickers);
  const [selected, setSelected] = useState(strategies.find((s) => s.params.length > 0)?.key ?? strategies[0]?.key);
  const [drafts, setDrafts] = useState<Record<string, ParamDraft>>(() =>
    Object.fromEntries(strategies.map((strategy) => [strategy.key, toDraft(profile(strategy).values)])),
  );
  const save = useSaveStrategyParams();
  const adjusted = adjustedStrategies(strategies, saved, tickers);

  // O que o jogador mexeu e ainda não gravou: só essas vão para o perfil
  const edits = strategies.flatMap((item) => {
    const values = fromDraft(item.params, drafts[item.key] ?? {});
    const valid = values !== null && Object.keys(draftErrors(item.params, drafts[item.key] ?? {})).length === 0;
    return valid && sameValues(values, profile(item).values) ? [] : [{ strategy: item, values: valid ? values : null }];
  });
  const autosave = useAutosave({
    dirty: edits.length > 0,
    incomplete: edits.some((edit) => edit.values === null) ? "Corrija os campos destacados para salvar." : null,
    signature: JSON.stringify(drafts),
    save: async () => {
      for (const edit of edits) {
        if (edit.values) await save.mutateAsync({ key: edit.strategy.key, params: edit.values });
      }
    },
  });

  const strategy = strategies.find((s) => s.key === selected);
  if (!strategy) return null;

  const draft = drafts[strategy.key] ?? toDraft(defaultValues(strategy));
  const setDraft = (next: ParamDraft) => setDrafts({ ...drafts, [strategy.key]: next });
  const { missing } = profile(strategy);

  return (
    <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 grid-cols-[320px_minmax(0,1fr)]">
        {/* Estratégias por grupo */}
        <div className="min-h-0 overflow-y-auto border-r bg-subtle px-3 pt-3 pb-5">
          <StrategyList
            strategies={strategies}
            selectedKey={strategy.key}
            adjustedKeys={adjusted}
            surface="panel"
            onSelect={setSelected}
          />
        </div>

        {/* Parâmetros da estratégia escolhida */}
        <div className="min-h-0 overflow-y-auto px-6 py-5">
          <div className="grid min-w-0 content-start gap-4">
            <div className="grid gap-0.5">
              <b className="text-base font-semibold">{strategy.name}</b>
              <span className="text-[13px] text-muted-foreground">{strategy.description}</span>
            </div>
            {missing.length > 0 && (
              <Alert variant="warning">
                <TriangleAlert />
                <AlertDescription>
                  {missing.join(", ")} não {missing.length === 1 ? "existe" : "existem"} nas ações cadastradas: o
                  formulário voltou ao padrão nesse campo.
                </AlertDescription>
              </Alert>
            )}
            {strategy.params.length === 0 ? (
              <span className="text-[13px] text-muted-foreground">
                Esta estratégia não tem parâmetros para ajustar.
              </span>
            ) : (
              <StrategyParamsForm
                key={strategy.key}
                strategy={strategy}
                draft={draft}
                saved={{}}
                compareToDefault
                errors={draftErrors(strategy.params, draft)}
                tickerOptions={tickers}
                cash={startingCash}
                cashLabel="o saldo inicial desta sala"
                headerAction={
                  <Button
                    type="button"
                    variant="link-muted"
                    size="sm"
                    onClick={() => setDraft(toDraft(defaultValues(strategy)))}
                  >
                    Voltar ao padrão
                  </Button>
                }
                onChange={setDraft}
              />
            )}
            <Alert variant="info">
              <Info />
              <AlertTitle>Vale em toda partida</AlertTitle>
              <AlertDescription>
                Ligar o automático abre o formulário com estes valores. Mudar lá, dentro da partida, também grava aqui.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </div>

      <PreparationFooter
        note="Fica no seu perfil e vale para toda partida, com ou sem expansão."
        saving={autosave.saving}
        error={autosave.error}
        incomplete={autosave.incomplete}
        onRetry={autosave.retry}
        onClose={onClose}
      />
    </div>
  );
}
