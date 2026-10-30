import { useState } from "react";
import { Flag, Lock, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useAuth } from "@/shared/hooks/useAuth";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import type { PartyIdentity, PlayerPreparation, PreparationRequest, Preparations, RoomPlayer } from "@/types";
import { useAnswerPreparationVice } from "../hooks/mutations/useAnswerPreparationVice";
import { useSetPreparation } from "../hooks/mutations/useSetPreparation";
import { useMyParty } from "../hooks/queries/useMyParty";
import { usePreparations } from "../hooks/queries/usePreparations";
import { PreparationFoundForm } from "./preparation-found-form";

type Choice = PreparationRequest["kind"];

/** "Minha preparação": o que o jogador faz quando a campanha abre (fundar, filiar-se ou nada). */
export function MyPreparationCard() {
  const { data: saved, isPending: partyPending } = useMyParty();
  const { data: preparations } = usePreparations();
  const { data: room } = useRoomPlayers();
  const { user } = useAuth();

  if (partyPending || !preparations || !room || !user) return <Skeleton className="h-40 w-full" />;
  return (
    <PreparationPanel
      saved={saved ?? null}
      preparations={preparations}
      nickname={user.nickname}
      humans={room.filter((p) => !p.bot)}
    />
  );
}

type PreparationPanelProps = {
  saved: PartyIdentity | null;
  preparations: Preparations;
  nickname: string;
  humans: RoomPlayer[];
};

function PreparationPanel({ saved, preparations, nickname, humans }: PreparationPanelProps) {
  const mine = preparations.players.find((p) => p.nickname === nickname);
  const [refusal, setRefusal] = useState<string | null>(null);
  // O modo aberto no card; começa no que o servidor já guarda
  const [mode, setMode] = useState<Choice>(mine?.kind ?? "NONE");
  const prepare = useSetPreparation();
  const answerVice = useAnswerPreparationVice();

  const founders = preparations.players.filter((p) => p.kind === "FOUND" && p.nickname !== nickname);
  const members = preparations.players.filter((p) => p.kind === "JOIN" && p.founder === nickname);
  const invite = preparations.players.find((p) => p.vice === nickname && !p.vice_accepted);
  const viceOf = preparations.players.find((p) => p.vice === nickname && p.vice_accepted);
  const takenColors = founders.flatMap((p) => (p.party ? [p.party.color] : []));
  const locked = preparations.locked_reason;

  const onSuccess = () => setRefusal(null);
  const onError = (err: Error) => setRefusal(err.message);
  const pick = (kind: Choice) => {
    setMode(kind);
    setRefusal(null);
    if (kind === "NONE") prepare.mutate({ kind }, { onSuccess, onError });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="inline-flex items-center gap-2">
            <Flag className="size-4" /> Minha preparação
          </span>
        </CardTitle>
        <CardDescription>
          Vale na abertura da campanha, com contribuição zero. Quem não estiver na sala quando a partida começar fica de
          fora.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3.5">
          {locked ? (
            <Alert variant="muted">
              <Lock />
              <AlertDescription>{locked}</AlertDescription>
            </Alert>
          ) : (
            <>
              <ToggleGroup
                variant="segmented"
                aria-label="O que fazer na abertura da campanha"
                value={[mode]}
                onValueChange={(values) => values[0] && pick(values[0] as Choice)}
                className="w-full"
              >
                <ToggleGroupItem value="FOUND" className="flex-1">
                  Fundar o meu partido
                </ToggleGroupItem>
                <ToggleGroupItem value="JOIN" className="flex-1" disabled={founders.length === 0 && mode !== "JOIN"}>
                  Entrar no partido de outro
                </ToggleGroupItem>
                <ToggleGroupItem value="NONE" className="flex-1">
                  Nada por enquanto
                </ToggleGroupItem>
              </ToggleGroup>

              {mode === "JOIN" && (
                <JoinList
                  founders={founders}
                  joined={mine?.founder ?? null}
                  disabled={prepare.isPending}
                  onJoin={(founder) => prepare.mutate({ kind: "JOIN", founder }, { onSuccess, onError })}
                />
              )}

              {mode === "FOUND" && (
                <PreparationFoundForm
                  saved={saved}
                  nickname={nickname}
                  humans={humans}
                  mine={mine}
                  members={members.map((p) => p.nickname)}
                  takenColors={takenColors}
                  onError={setRefusal}
                />
              )}
            </>
          )}

          {/* Convite de vice */}
          {invite && !locked && (
            <ViceInvite
              owner={invite}
              disabled={answerVice.isPending}
              onAnswer={(accept) => answerVice.mutate({ accept }, { onSuccess, onError })}
            />
          )}
          {viceOf && (
            <span className="text-[13px] text-muted-foreground">
              Você é o vice de {viceOf.candidate} no {viceOf.party?.abbr}.
            </span>
          )}

          {refusal && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertDescription>{refusal}</AlertDescription>
            </Alert>
          )}

          {/* Conflitos que bloqueiam o Iniciar */}
          {preparations.conflicts.length > 0 && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertTitle>Há partidos em conflito: o host não consegue iniciar</AlertTitle>
              <AlertDescription>
                <ul className="list-disc pl-4">
                  {preparations.conflicts.map((conflict) => (
                    <li key={conflict}>{conflict}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

type JoinListProps = {
  founders: PlayerPreparation[];
  joined: string | null;
  disabled: boolean;
  onJoin: (founder: string) => void;
};

function JoinList({ founders, joined, disabled, onJoin }: JoinListProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {founders.map((founder) => (
        <Button
          key={founder.nickname}
          variant={joined === founder.nickname ? "default" : "outline"}
          size="sm"
          disabled={disabled}
          onClick={() => onJoin(founder.nickname)}
        >
          {founder.party?.abbr} · de {founder.nickname}
        </Button>
      ))}
    </div>
  );
}

type ViceInviteProps = { owner: PlayerPreparation; disabled: boolean; onAnswer: (accept: boolean) => void };

function ViceInvite({ owner, disabled, onAnswer }: ViceInviteProps) {
  return (
    <Alert variant="info">
      <Flag />
      <AlertTitle>{owner.nickname} te convidou para vice</AlertTitle>
      <AlertDescription>
        <p>
          Na chapa do {owner.party?.abbr}, com {owner.candidate} de candidato.
        </p>
        <div className="mt-2 flex gap-2">
          <Button size="sm" disabled={disabled} onClick={() => onAnswer(true)}>
            Aceitar
          </Button>
          <Button size="sm" variant="outline" disabled={disabled} onClick={() => onAnswer(false)}>
            Recusar
          </Button>
        </div>
      </AlertDescription>
    </Alert>
  );
}
