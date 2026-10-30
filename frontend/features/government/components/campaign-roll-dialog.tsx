import { useState, type ReactNode } from "react";
import { Newspaper, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { displayMoney } from "@/shared/lib/utils/display";
import type { CampaignAction, CampaignActionRequest, CampaignRoll, CampaignTarget } from "@/types";
import { useCampaignAction } from "../hooks/mutations/useCampaignAction";
import {
  BAND_INFO,
  bandOf,
  bandRange,
  groupWord,
  headline,
  rallyExtremes,
  repairUsed,
  resultTitle,
  signed,
} from "../lib/campaign";
import { ActionIcon } from "./campaign-action-icon";
import { BandsTable, D20 } from "./campaign-dice";

// O dado gira por este tempo antes de parar no número que o servidor já sorteou
const DICE_MS = 1000;

const wait = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms));

type Phase = "before" | "rolling" | "result" | "error";

type CampaignRollDialogProps = {
  action: CampaignAction;
  target: CampaignTarget;
  request: CampaignActionRequest;
  /** "Evento com aposentados" */
  title: string;
  /** "2ª vez em ago · rende 50%" */
  subtitle: string;
  partyAbbr: string;
  rivalAbbr: string | null;
  onClose: () => void;
  /** Fecha o diálogo e leva a pessoa de volta à escolha da próxima ação */
  onAnother: () => void;
};

/** O dado de uma ação: a tabela de faixas antes de pagar, o giro e o número tirado com o efeito no grupo. */
export function CampaignRollDialog({
  action,
  target: liveTarget,
  request,
  title,
  subtitle,
  partyAbbr,
  rivalAbbr,
  onClose,
  onAnother,
}: CampaignRollDialogProps) {
  // O cartão renova depois da ação; a tabela do diálogo segue a de antes de rolar
  const [target] = useState(liveTarget);
  const [phase, setPhase] = useState<Phase>("before");
  const [roll, setRoll] = useState<CampaignRoll | null>(null);
  const [failure, setFailure] = useState("");
  const act = useCampaignAction();

  const throwDice = async () => {
    setPhase("rolling");
    try {
      const [response] = await Promise.all([act.mutateAsync(request), wait(DICE_MS)]);
      setRoll(response);
      setPhase("result");
    } catch (error) {
      setFailure(error instanceof Error ? error.message : "A conexão caiu antes de o servidor rolar o dado.");
      setPhase("error");
    }
  };

  const rolling = phase === "rolling";

  return (
    <Dialog open onOpenChange={(open) => !open && !rolling && onClose()}>
      <DialogContent className="sm:max-w-110">
        {phase === "before" && (
          <>
            <DialogHeader variant="divided">
              <div className="flex items-center gap-3">
                <ActionIcon kind={action.action} />
                <div className="grid gap-0.5">
                  <DialogTitle>{title}</DialogTitle>
                  <DialogDescription>{subtitle}</DialogDescription>
                </div>
              </div>
            </DialogHeader>
            <DialogBody>
              <div className="grid gap-3">
                <BandsTable bands={target.bands} />
                <span className="text-xs leading-snug text-muted-foreground">{beforeNote(action, target)}</span>
              </div>
            </DialogBody>
            <DialogFooter variant="divided" className="sm:justify-end">
              <Button variant="outline" size="sm" onClick={onClose}>
                Cancelar
              </Button>
              <Button size="sm" onClick={() => void throwDice()}>
                Rolar · {displayMoney(action.price)}
              </Button>
            </DialogFooter>
          </>
        )}

        {rolling && (
          <>
            <DialogHeader variant="divided">
              <div className="grid gap-1">
                <Badge variant="secondary" size="sm">
                  Rolando…
                </Badge>
                <DialogTitle>{title}</DialogTitle>
                <DialogDescription className="sr-only">O dado está rolando.</DialogDescription>
              </div>
            </DialogHeader>
            <DialogBody>
              <div className="grid gap-3">
                <div className="flex items-center gap-3">
                  <BandsTable bands={target.bands} className="flex-1" />
                  <div className="flex w-20 shrink-0 justify-center">
                    <D20 value="?" band={null} size={68} className="motion-safe:animate-spin" />
                  </div>
                </div>
                <span className="text-[12.5px] text-muted-foreground">
                  O dado gira por 1 segundo e para no número. O valor já foi pago; o resultado sai da semente da
                  partida.
                </span>
              </div>
            </DialogBody>
            <DialogFooter variant="divided" className="sm:justify-end">
              <Button size="sm" disabled>
                Fechar
              </Button>
            </DialogFooter>
          </>
        )}

        {phase === "result" && roll && (
          <RollResult
            roll={roll}
            target={target}
            partyAbbr={partyAbbr}
            rivalAbbr={rivalAbbr}
            onClose={onClose}
            onAnother={onAnother}
          />
        )}

        {phase === "error" && (
          <>
            <DialogHeader variant="divided">
              <DialogTitle>{title}</DialogTitle>
              <DialogDescription className="sr-only">A ação não foi feita.</DialogDescription>
            </DialogHeader>
            <DialogBody>
              <Alert variant="destructive">
                <TriangleAlert />
                <AlertTitle>A ação não foi feita</AlertTitle>
                <AlertDescription>{failure} Nada foi cobrado da sua carteira.</AlertDescription>
              </Alert>
            </DialogBody>
            <DialogFooter variant="divided" className="sm:justify-end">
              <Button variant="outline" size="sm" onClick={onClose}>
                Cancelar
              </Button>
              <Button size="sm" onClick={() => void throwDice()}>
                Tentar de novo
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

/** O que a ação faz além do apoio, escrito para quem ainda vai pagar. */
function beforeNote(action: CampaignAction, target: CampaignTarget) {
  switch (action.action) {
    case "EVENT":
      return `Fora o desastre, repara 1 de rejeição (${repairUsed(target)} de ${target.repair_limit} usados na campanha). Desastre e viral saem no jornal.`;
    case "RALLY":
      return "Os extremos valem o dobro: o desastre perde 4 vezes o ganho normal e o viral rende 6. Desastre e viral saem no jornal.";
    case "ATTACK":
      return "No 1 o tiro sai pela culatra: o grupo passa a rejeitar quem atacou, e o apoio de quem atacou e o do rival não mudam. Todo ataque sai no jornal.";
    case "TV":
      return "Dois dados, vale o maior: o desastre só sai quando os dois caem no 1. Desastre e viral saem no jornal.";
  }
}

type RollResultProps = {
  roll: CampaignRoll;
  target: CampaignTarget;
  partyAbbr: string;
  rivalAbbr: string | null;
  onClose: () => void;
  onAnother: () => void;
};

function RollResult({ roll, target, partyAbbr, rivalAbbr, onClose, onAnother }: RollResultProps) {
  const { entry } = roll;
  const band = entry.band ?? "NORMAL";
  const hit = bandOf(target.bands, entry.roll ?? 0);
  const style = BAND_INFO[band];
  const group = entry.group ? groupWord(entry.group) : null;
  const dice = entry.rolls;
  const repaired = Number(entry.rejection) < 0 ? -Number(entry.rejection) : 0;
  // O dado que vale (o maior, na TV) vem por último e maior; o descartado fica apagado
  const chosen = dice.indexOf(entry.roll ?? -1);
  const extremes =
    entry.kind === "RALLY"
      ? rallyExtremes(band, entry.support, target.bands.find((item) => item.band === "NORMAL")?.support ?? 0)
      : null;
  const diceOrder = dice.map((_, index) => index).sort((a, b) => Number(a === chosen) - Number(b === chosen));

  return (
    <>
      <DialogHeader variant="divided">
        <div className="grid gap-1.5">
          <Badge variant={style.badge} size="sm">
            {style.label} · {hit ? bandRange(hit) : entry.roll}
          </Badge>
          <DialogTitle>{resultTitle(roll)}</DialogTitle>
          <DialogDescription className="sr-only">O resultado do dado.</DialogDescription>
        </div>
      </DialogHeader>
      <DialogBody>
        <div className="grid gap-3.5">
          <div className="flex items-center gap-3">
            <BandsTable bands={target.bands} roll={entry.roll ?? undefined} className="flex-1" />
            <div className="flex w-20 shrink-0 flex-col items-center gap-1.5">
              {diceOrder.map((index) => (
                <D20
                  key={index}
                  value={dice[index] ?? 0}
                  band={bandOf(target.bands, dice[index] ?? 0)?.band ?? band}
                  size={index === chosen ? 68 : 44}
                  dim={index !== chosen}
                />
              ))}
            </div>
          </div>

          <dl className="grid text-[13px]">
            {extremes && <ResultRow label={extremes.label} value={extremes.value} />}
            {dice.length > 1 && (
              <ResultRow label="Dois dados, vale o maior" value={`${dice.join(" e ")} → ${entry.roll}`} />
            )}
            {entry.kind === "TV" && (
              <ResultRow
                label={`Apoio do ${partyAbbr} em todos os grupos`}
                value={`${signed(entry.support)} em cada`}
              />
            )}
            {entry.kind === "ATTACK" ? (
              <>
                <ResultRow
                  label={`Apoio do ${rivalAbbr} entre ${group}`}
                  value={Number(entry.support) === 0 ? "não muda" : signed(entry.support)}
                />
                <ResultRow label={`Apoio do ${partyAbbr}`} value="não muda" />
                {Number(entry.rejection) !== 0 && (
                  <ResultRow
                    label={`Rejeição ao ${partyAbbr} entre ${group}`}
                    value={`${Math.round(Number(roll.rejection_before))} → ${Math.round(Number(roll.rejection_after))}`}
                  />
                )}
              </>
            ) : (
              entry.kind !== "TV" && (
                <>
                  <ResultRow
                    label={`Apoio do ${partyAbbr} entre ${group}`}
                    value={`${Math.round(Number(roll.support_before))} → ${Math.round(Number(roll.support_after))}`}
                  />
                  <ResultRow
                    label={
                      entry.kind === "EVENT"
                        ? `Rejeição (${repairUsed(target) + repaired} de ${target.repair_limit} reparados na campanha)`
                        : "Rejeição"
                    }
                    value={
                      Number(roll.rejection_before) === Number(roll.rejection_after)
                        ? "não muda"
                        : `${Math.round(Number(roll.rejection_before))} → ${Math.round(Number(roll.rejection_after))}`
                    }
                  />
                </>
              )
            )}
            <ResultRow label="Pago da sua carteira" value={displayMoney(entry.price ?? 0)} />
          </dl>

          {entry.newsworthy && (
            <Alert variant={band === "DISASTER" ? "destructive" : "info"}>
              <Newspaper />
              <AlertTitle>{entry.kind === "ATTACK" ? "Todo ataque sai no jornal" : "Sai no jornal"}</AlertTitle>
              <AlertDescription>“{headline(entry)}”</AlertDescription>
            </Alert>
          )}
        </div>
      </DialogBody>
      <DialogFooter variant="divided" className="sm:justify-end">
        <Button variant="outline" size="sm" onClick={onAnother}>
          Fazer outra ação
        </Button>
        <Button size="sm" onClick={onClose}>
          Fechar
        </Button>
      </DialogFooter>
    </>
  );
}

function ResultRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex justify-between gap-3 border-b py-1.5 last:border-b-0">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-mono font-semibold">{value}</dd>
    </div>
  );
}
