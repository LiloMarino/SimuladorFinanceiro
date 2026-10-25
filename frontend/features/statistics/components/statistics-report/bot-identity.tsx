import { Lock, ScrollText } from "lucide-react";
import { KeyValueRow } from "@/shared/components/key-value-row";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "@/shared/components/ui/hover-card";
import { useStatisticsReport } from "@/shared/hooks/queries/useStatisticsReport";
import type { BotReport, PlayerRef } from "@/types";
import { displayBotParam } from "../../lib/bot-param";

type BotIdentityProps = {
  player: PlayerRef;
  /** O nome como a tabela o escreve (entre partidas, com a letra da partida) */
  label: string;
  simulationIds: number[];
  /** Abre o registro das ordens do bot; sem ele, o cartão só informa */
  onOpenLog?: (bot: PlayerRef) => void;
};

/** O bot na tabela: avatar de robô, o nome (que abre o cartão dele), o selo "Bot" e a estratégia embaixo. */
export function BotIdentity({ player, label, simulationIds, onOpenLog }: BotIdentityProps) {
  const { data: bots } = useStatisticsReport("bots", simulationIds);
  const report = bots?.find(
    (bot) => bot.simulation_id === player.simulation_id && bot.player_nickname === player.player_nickname,
  );

  return (
    <span className="flex items-center gap-2.5">
      <PlayerAvatar
        nickname={player.player_nickname}
        color={simulationIds.length > 1 ? undefined : player.color}
        bot
        size="sm"
      />
      <span className="grid min-w-0">
        <span className="flex items-center gap-1.5">
          <HoverCard>
            <HoverCardTrigger term delay={150} render={<button type="button" />}>
              {label}
            </HoverCardTrigger>
            <HoverCardContent>
              <BotCard player={player} report={report} onOpenLog={onOpenLog} />
            </HoverCardContent>
          </HoverCard>
          <Badge variant="secondary" size="tag">
            Bot
          </Badge>
        </span>
        {report && <span className="truncate text-xs text-muted-foreground">{report.strategy_name}</span>}
      </span>
    </span>
  );
}

type BotCardProps = {
  player: PlayerRef;
  report: BotReport | undefined;
  onOpenLog?: (bot: PlayerRef) => void;
};

/** O cartão do bot: quem o pôs na sala, a estratégia com os parâmetros e o log das ordens, que só abre no fim. */
function BotCard({ player, report, onOpenLog }: BotCardProps) {
  return (
    <>
      <div className="flex items-center gap-3">
        <PlayerAvatar nickname={player.player_nickname} color={player.color} bot size="xl" />
        <div className="grid gap-0.5">
          <span className="flex items-center gap-1.5">
            <b className="text-[15px] font-semibold">{player.player_nickname}</b>
            <Badge variant="secondary" size="tag">
              Bot
            </Badge>
          </span>
          {report && <span className="text-xs text-muted-foreground">Adicionado por {report.added_by}</span>}
        </div>
      </div>

      {report && (
        <div>
          <KeyValueRow label="Estratégia" value={report.strategy_name} valueClassName="font-sans font-medium" />
          {report.params.map((param) => (
            <KeyValueRow key={param.label} label={param.label} value={displayBotParam(param)} />
          ))}
        </div>
      )}

      {report &&
        (report.log_open ? (
          onOpenLog && (
            <Button type="button" variant="outline" size="sm" className="w-full" onClick={() => onOpenLog(player)}>
              Ver o log das ordens
              <ScrollText />
            </Button>
          )
        ) : (
          <div className="flex items-center gap-2.5 rounded-lg border bg-subtle px-3 py-2.5 text-[13px]">
            <Lock className="size-[15px] shrink-0 text-faint-foreground" />
            <span>
              <b className="font-semibold">Log das ordens</b>{" "}
              <span className="text-muted-foreground">· abre para todos no fim da partida</span>
            </span>
          </div>
        ))}
    </>
  );
}
