import { InfoHint } from "@/shared/components/info-hint";
import { Badge } from "@/shared/components/ui/badge";
import { cn } from "@/shared/lib/utils";
import type { GroupReaction, MeasurePreview } from "@/types";
import { GROUP_INFO, VALUE_INFO } from "../lib/voters";
import { type SpendingKind } from "@/shared/lib/spending-kinds";
import { reasonOf, splitReactions } from "../lib/spending";

const MINUS = "−";

/** Pontos de um grupo com sinal e até uma casa: 2 → "+2", -0.5 → "−0,5". */
function signedReaction(points: string) {
  const value = Math.round(Number(points) * 10) / 10;
  const text = Math.abs(value).toLocaleString("pt-BR", { maximumFractionDigits: 1 });
  return `${value > 0 ? "+" : MINUS}${text}`;
}

type ReactionColumnProps = {
  title: string;
  tone: "like" | "dislike";
  reactions: GroupReaction[];
  kind: SpendingKind;
  raising: boolean;
};

function ReactionColumn({ title, tone, reactions, kind, raising }: ReactionColumnProps) {
  return (
    <div>
      <span className={cn("text-xs font-semibold", tone === "like" ? "text-success" : "text-destructive")}>
        {title}
      </span>
      {reactions.length === 0 && <p className="border-t py-2 text-xs text-muted-foreground">Nenhum grupo.</p>}
      {reactions.map((reaction) => (
        <div
          key={reaction.group}
          className="grid grid-cols-[minmax(0,1fr)_auto] gap-x-2.5 gap-y-0.5 border-t py-2 first-of-type:mt-1"
        >
          <span className="text-[13px] font-medium">{GROUP_INFO[reaction.group].label}</span>
          <span
            className={cn("font-mono text-[13px] font-semibold", tone === "like" ? "text-success" : "text-destructive")}
          >
            {signedReaction(reaction.points)}
          </span>
          <span className="col-span-2 text-xs text-muted-foreground">
            {reasonOf(kind, reaction.group, Number(reaction.points), raising)}
          </span>
        </div>
      ))}
    </div>
  );
}

type MeasureReactionsProps = {
  kind: SpendingKind;
  reactions: GroupReaction[];
  moves: MeasurePreview["profile_moves"];
  /** A medida sobe o gasto (o valor novo é maior que o de hoje) */
  raising: boolean;
};

/** Quem gosta e quem não gosta da medida de gasto, grupo a grupo, e as bandeiras do partido que ela move. */
export function MeasureReactions({ kind, reactions, moves, raising }: MeasureReactionsProps) {
  const { likes, dislikes } = splitReactions(reactions);

  return (
    <div className="grid gap-2.5 rounded-lg border p-3.5">
      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-1.5">
        <span className="inline-flex items-center gap-1 text-sm font-medium">
          Quem gosta e quem não gosta
          <InfoHint label="Como ler os pontos">
            <div className="space-y-1 text-left">
              <p>
                Cada número é o quanto o apoio do grupo ao seu partido muda quando a medida vale, já descontada a
                rejeição. Os pontos são da escala de 0 a 100 da satisfação do grupo.
              </p>
              <p>
                Ex.: +2 em Investidores quer dizer que, de cada 100 investidores, uns 2 a mais passam a apoiar o
                partido.
              </p>
              <p>Grupo que não aparece não muda. Bandeira com seta para cima ganha força no perfil do partido.</p>
            </div>
          </InfoHint>
        </span>
        {moves.length > 0 && (
          <span className="flex flex-wrap items-center gap-1.5">
            <span className="text-xs text-muted-foreground">bandeiras do partido</span>
            {moves.map((move) => (
              <Badge key={move.value} variant={Number(move.points) > 0 ? "success" : "destructive"} size="sm">
                {VALUE_INFO[move.value].label} {Number(move.points) > 0 ? "▲" : "▼"}
              </Badge>
            ))}
          </span>
        )}
      </div>

      <div className="grid gap-5 sm:grid-cols-2">
        <ReactionColumn title="Gostam" tone="like" reactions={likes} kind={kind} raising={raising} />
        <ReactionColumn title="Não gostam" tone="dislike" reactions={dislikes} kind={kind} raising={raising} />
      </div>

      <p className="text-xs leading-normal text-muted-foreground">
        Apoio ao seu partido em cada grupo, já descontada a rejeição. O gosto vem do que o grupo recebe e do que a
        inflação e o consumo fazem com ele.
      </p>
    </div>
  );
}
