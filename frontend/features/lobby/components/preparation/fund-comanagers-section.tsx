import { useState } from "react";
import { CircleAlert, Clock, Plus, UserCheck, UserX } from "lucide-react";
import { OptionSelect, type SelectOption } from "@/shared/components/option-select";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { InputGroup, InputGroupAddon, InputGroupInput, InputGroupText } from "@/shared/components/ui/input-group";
import { MAX_COMANAGERS, maxSharePoints } from "@/shared/lib/fund-comanager-shares";
import type { RoomPlayer } from "@/types";
import { useSetFundComanager } from "../../hooks/mutations/useSetFundComanager";
import {
  openComanagers,
  pointsToShare,
  reservedPoints,
  sharePercent,
  type FundComanagerRow,
} from "../../lib/fund-comanagers";
import { PreparationSection } from "./preparation-section";

const DEFAULT_POINTS = 10;

type FundComanagersSectionProps = {
  comanagers: FundComanagerRow[];
  /** Humanos na sala: de onde saem os co-gestores */
  humans: RoomPlayer[];
  nickname: string;
};

/** Os co-gestores da gestora que o jogador funda: convites, aceites e o convite novo, com a parte das taxas. */
export function FundComanagersSection({ comanagers, humans, nickname }: FundComanagersSectionProps) {
  const set = useSetFundComanager();
  const [guest, setGuest] = useState<string | null>(null);
  const [points, setPoints] = useState(DEFAULT_POINTS);
  const [error, setError] = useState<string | null>(null);

  const open = openComanagers(comanagers);
  const max = maxSharePoints(reservedPoints(comanagers));
  const value = Math.min(points, max);
  const candidates = humans.filter(
    (player) => player.nickname !== nickname && !open.some((c) => c.nickname === player.nickname),
  );
  const full = open.length >= MAX_COMANAGERS;
  const noRoom = max < 1;
  const colorOf = (name: string) => humans.find((player) => player.nickname === name)?.color;

  const send = (body: Parameters<typeof set.mutate>[0], onSuccess?: () => void) => {
    setError(null);
    set.mutate(body, { ...(onSuccess && { onSuccess }), onError: (err) => setError(err.message) });
  };

  return (
    <PreparationSection title="Co-gestores" hint={`até ${MAX_COMANAGERS}`}>
      <span className="text-xs text-muted-foreground">
        Co-gestor opera a carteira da gestora. Emitir cotas, pegar empréstimo e fundir ficam com você.
      </span>

      {/* Convidados */}
      <div className="grid">
        {comanagers.map((comanager) => (
          <div key={comanager.nickname} className="flex items-center gap-2.5 border-t border-muted py-2.5">
            <PlayerAvatar nickname={comanager.nickname} color={colorOf(comanager.nickname)} size="sm" />
            <b className="font-bold">{comanager.nickname}</b>
            {comanager.status === "INVITED" && (
              <Badge variant="warning" size="tag">
                <Clock /> convite enviado
              </Badge>
            )}
            {comanager.status === "ACCEPTED" && (
              <Badge variant="success" size="tag">
                <UserCheck /> aceitou
              </Badge>
            )}
            {comanager.status === "DECLINED" && (
              <Badge variant="secondary" size="tag">
                <UserX /> recusou
              </Badge>
            )}
            <span className="font-mono text-xs text-muted-foreground">{sharePercent(comanager.share)} das taxas</span>
            <div className="ml-auto">
              {comanager.status === "DECLINED" ? (
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={set.isPending || full}
                  onClick={() => send({ nickname: comanager.nickname, share: comanager.share })}
                >
                  Convidar de novo
                </Button>
              ) : (
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={set.isPending}
                  onClick={() => send({ nickname: comanager.nickname })}
                >
                  {comanager.status === "ACCEPTED" ? "Remover" : "Cancelar"}
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Convite novo */}
      {full ? (
        <Badge variant="note" size="note">
          <CircleAlert /> A gestora já tem {MAX_COMANAGERS} co-gestores. Remova um para convidar outro.
        </Badge>
      ) : noRoom ? (
        <Badge variant="note" size="note">
          <CircleAlert /> As partes já somam 99%: o gestor principal fica com ao menos 1%. Cancele um convite para
          convidar outro.
        </Badge>
      ) : candidates.length > 0 ? (
        <div className="flex items-center gap-2 border-t border-muted pt-2.5">
          <OptionSelect
            value={guest}
            options={candidates.map((player): SelectOption => ({
              value: player.nickname,
              label: player.nickname,
              leading: <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />,
            }))}
            onChange={setGuest}
            placeholder="Convidar jogador…"
            className="min-w-0 flex-1"
            aria-label="Jogador a convidar"
          />
          <InputGroup className="w-24 shrink-0">
            <InputGroupInput
              numeric
              type="number"
              min={1}
              max={max}
              step={1}
              value={value}
              aria-label="Parte das taxas do co-gestor"
              onChange={(event) => setPoints(Math.min(max, Math.max(1, Math.trunc(Number(event.target.value)) || 1)))}
            />
            <InputGroupAddon align="inline-end">
              <InputGroupText>%</InputGroupText>
            </InputGroupAddon>
          </InputGroup>
          <Button
            type="button"
            variant="fund"
            size="sm"
            disabled={guest === null || set.isPending}
            onClick={() => guest && send({ nickname: guest, share: pointsToShare(value) }, () => setGuest(null))}
          >
            <Plus /> Convidar
          </Button>
        </div>
      ) : (
        comanagers.length === 0 && (
          <Empty>
            <EmptyHeader>
              <EmptyMedia variant="icon">
                <UserX />
              </EmptyMedia>
              <EmptyTitle>Ninguém para convidar ainda</EmptyTitle>
              <EmptyDescription>Os co-gestores saem dos jogadores da sala. Bots não entram na gestão.</EmptyDescription>
            </EmptyHeader>
          </Empty>
        )
      )}
      {error && (
        <Alert variant="destructive">
          <CircleAlert />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
    </PreparationSection>
  );
}
