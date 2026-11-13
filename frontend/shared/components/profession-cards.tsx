import type { KeyboardEvent } from "react";
import { Check, X } from "lucide-react";
import {
  PROFESSION_ORDER,
  PROFESSIONS,
  professionIncome,
  visibleProfession,
  type RoomRules,
} from "@/shared/lib/professions";
import { cn } from "@/shared/lib/utils";
import { displayDecimal, displayMoneyWhole } from "@/shared/lib/utils/display";
import type { Profession } from "@/types";
import { FieldCaption } from "./ui/field";
import { ProfessionTags } from "./profession-tags";

type ProfessionCardsProps = {
  /** As regras da sala: o que cada profissão sente depende delas */
  room: RoomRules;
  /** Profissão do próprio jogador, marcada */
  selected: Profession | null | undefined;
  disabled?: boolean;
  onSelect: (profession: Profession) => void;
};

/** As 6 profissões em cartões: a renda do mês, o que cada uma ganha e perde e o que mexe na renda dela. */
export function ProfessionCards({ room, selected, disabled, onSelect }: ProfessionCardsProps) {
  const salary = Number(room.monthly_salary);
  // Só um cartão entra na ordem do Tab: o marcado, ou o primeiro enquanto não há escolha
  const tabStop = selected ?? PROFESSION_ORDER[0];

  // Setas movem a escolha entre os cartões, como num grupo de opções
  function moveWithArrows(event: KeyboardEvent<HTMLDivElement>) {
    const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
    if (!step) return;
    const options = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>("[role=radio]"));
    const next = options[options.indexOf(document.activeElement as HTMLButtonElement) + step];
    if (!next) return;
    event.preventDefault();
    next.focus();
    next.click();
  }

  return (
    <div className="@container">
      <div
        role="radiogroup"
        aria-label="Profissão"
        tabIndex={-1}
        onKeyDown={moveWithArrows}
        className="grid gap-3 outline-none @xl:grid-cols-2"
      >
        {PROFESSION_ORDER.map((profession) => {
          const { name, icon: Icon, incomeMultiple, benefitMultiple } = PROFESSIONS[profession];
          const { gains, losses, tags } = visibleProfession(profession, room);
          const isMine = profession === selected;
          return (
            <div
              key={profession}
              className={cn(
                "flex min-w-0 flex-col gap-3 rounded-xl border bg-card p-4 transition-colors hover:border-input",
                isMine && "bg-subtle ring-2 ring-foreground",
                disabled && "opacity-55",
              )}
            >
              <button
                type="button"
                role="radio"
                aria-checked={isMine}
                tabIndex={profession === tabStop ? 0 : -1}
                disabled={disabled}
                onClick={() => onSelect(profession)}
                className="grid cursor-pointer content-start gap-3 rounded-lg text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default"
              >
                {/* Cabeçalho */}
                <span className="flex items-start gap-2.5">
                  <span
                    className={cn(
                      "grid size-8 shrink-0 place-content-center rounded-lg bg-muted text-secondary-foreground",
                      isMine && "bg-foreground text-background",
                    )}
                  >
                    <Icon className="size-4" />
                  </span>
                  <span className="grid min-w-0">
                    <span className="truncate text-sm leading-5 font-semibold">{name}</span>
                    <span className="flex flex-wrap items-baseline gap-1">
                      <span className="font-mono text-base font-semibold">
                        {displayMoneyWhole(professionIncome(profession, salary))}
                      </span>
                      <span className="text-xs text-muted-foreground">por mês</span>
                    </span>
                    <span className="font-mono text-xs text-muted-foreground">
                      {displayDecimal(incomeMultiple + (benefitMultiple ?? 0))}× o salário
                    </span>
                    {benefitMultiple !== undefined && (
                      <span className="font-mono text-xs text-muted-foreground">
                        {displayDecimal(incomeMultiple)}× do bico + {displayDecimal(benefitMultiple)}× do auxílio
                      </span>
                    )}
                  </span>
                </span>

                {/* Ganha e Perde */}
                <span className="grid grid-cols-2 gap-4">
                  <PointList title="Ganha" tone="gain" points={gains.map((point) => point.text)} />
                  <PointList title="Perde" tone="loss" points={losses.map((point) => point.text)} />
                </span>
              </button>

              {/* Afetado por */}
              <div className="mt-auto flex flex-wrap items-center gap-2.5 border-t border-muted pt-3">
                <FieldCaption>Afetado por</FieldCaption>
                {tags.length > 0 ? (
                  <ProfessionTags profession={profession} tags={tags} salary={salary} />
                ) : (
                  <span className="text-xs text-muted-foreground">
                    {room.inflation_adjusted
                      ? "Nada que mude na partida: a renda só sobe com a inflação."
                      : "Nada que mude na partida."}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

type PointListProps = { title: string; tone: "gain" | "loss"; points: string[] };

function PointList({ title, tone, points }: PointListProps) {
  const Mark = tone === "gain" ? Check : X;
  return (
    <span className="grid content-start gap-1.5">
      <FieldCaption tone={tone === "gain" ? "success" : "destructive"}>{title}</FieldCaption>
      <span className="grid gap-1.5">
        {points.map((point) => (
          <span key={point} className="flex items-start gap-1.5 text-[13px]">
            <Mark className={cn("mt-0.5 size-3.5 shrink-0", tone === "gain" ? "text-success" : "text-destructive")} />
            <span>{point}</span>
          </span>
        ))}
      </span>
    </span>
  );
}
