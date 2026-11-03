import { useState } from "react";
import { CircleAlert, Flag, Lock, Mail, SlidersHorizontal } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/shared/components/ui/empty";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import type {
  MyPreparation,
  PartyIdentity,
  PreparationRequest,
  Preparations,
  RoomPlayer,
  SimulationSettings,
} from "@/types";
import { useAnswerPreparationVice } from "../../hooks/mutations/useAnswerPreparationVice";
import { PartyFoundTab } from "./party-found-tab";
import { PartyJoinTab } from "./party-join-tab";
import { PartyNoneTab } from "./party-none-tab";
import { PreparationFooter } from "./preparation-footer";

export type Choice = PreparationRequest["kind"];

export type PartyTabProps = {
  preparations: Preparations;
  mine: MyPreparation;
  /** O Meu partido salvo no perfil; nulo enquanto o jogador não salvou um */
  saved: PartyIdentity | null;
  /** A contribuição mensal salva no perfil */
  contribution: string;
  /** Humanos na sala, para o vice */
  humans: RoomPlayer[];
  nickname: string;
  rules: SimulationSettings["simulation"];
  /** O nome da partida salva selecionada; nulo quando a sala prepara uma partida nova */
  savedSimulation: string | null;
  onStrategies: () => void;
  onClose: () => void;
};

/** Aba Partido: fundar, entrar ou ficar sem partido, com o convite de vice e as travas da sala. */
export function PartyTab(props: PartyTabProps) {
  const { preparations, mine, nickname, rules, savedSimulation, onStrategies, onClose } = props;
  const me = preparations.players.find((player) => player.nickname === nickname);
  // O modo aberto na aba; começa no que o servidor já guarda
  const [mode, setMode] = useState<Choice>(me?.kind ?? "NONE");
  const [refusal, setRefusal] = useState<string | null>(null);
  const answerVice = useAnswerPreparationVice();

  if (!rules.government_enabled) {
    return (
      <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <Flag />
            </EmptyMedia>
            <EmptyTitle>Partido só com Governo & Política</EmptyTitle>
            <EmptyDescription>
              A expansão está desligada nesta sala. Seu partido salvo continua no perfil e volta quando o host ligar a
              expansão. As estratégias seguem valendo.
            </EmptyDescription>
          </EmptyHeader>
          <EmptyContent>
            <Button variant="outline" onClick={onStrategies}>
              <SlidersHorizontal /> Ir para Estratégias
            </Button>
          </EmptyContent>
        </Empty>
        <PreparationFooter note="O host liga a expansão em Editar regras." onClose={onClose} />
      </div>
    );
  }

  const locked = preparations.locked_reason !== null;
  const lead = (
    <>
      {/* Convite de vice */}
      {mine.invite && !locked && (
        <Alert variant="info">
          <Mail />
          <AlertTitle>
            {mine.invite.owner} te convidou para vice na chapa do {mine.invite.abbr}
          </AlertTitle>
          <AlertDescription>
            Com {mine.invite.candidate} de candidato. Aceitar não te filia ao {mine.invite.abbr}: o vice pode ser de
            outro partido ou de nenhum.
          </AlertDescription>
          <AlertAction>
            <div className="flex items-center gap-2">
              <Button
                type="button"
                size="sm"
                disabled={answerVice.isPending}
                onClick={() => answerVice.mutate({ accept: true }, { onError: (err) => setRefusal(err.message) })}
              >
                Aceitar
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={answerVice.isPending}
                onClick={() => answerVice.mutate({ accept: false }, { onError: (err) => setRefusal(err.message) })}
              >
                Recusar
              </Button>
            </div>
          </AlertAction>
        </Alert>
      )}
      {refusal && (
        <Alert variant="destructive">
          <CircleAlert />
          <AlertDescription>{refusal}</AlertDescription>
        </Alert>
      )}

      {/* Travas da sala */}
      {savedSimulation ? (
        <Alert variant="muted">
          <Lock />
          <AlertTitle>Continuar · {savedSimulation}</AlertTitle>
          <AlertDescription>
            Os partidos já nasceram nesta partida salva. O que você mudar aqui vale na próxima partida nova; veja os
            partidos dela na página Eleição.
          </AlertDescription>
        </Alert>
      ) : (
        locked && (
          <Alert variant="muted">
            <Lock />
            <AlertDescription>{preparations.locked_reason}</AlertDescription>
          </Alert>
        )
      )}

      {/* Escolha */}
      <ToggleGroup
        variant="segmented"
        aria-label="Como você começa a partida"
        value={[mode]}
        onValueChange={(values) => values[0] && setMode(values[0] as Choice)}
        disabled={locked}
        className="w-full"
      >
        <ToggleGroupItem value="FOUND" className="flex-1">
          Fundar o meu partido
        </ToggleGroupItem>
        <ToggleGroupItem value="JOIN" className="flex-1">
          Entrar num partido
        </ToggleGroupItem>
        <ToggleGroupItem value="NONE" className="flex-1">
          Sem partido
        </ToggleGroupItem>
      </ToggleGroup>
    </>
  );

  const tab = { ...props, me, lead, locked, onMode: setMode };
  if (mode === "FOUND") return <PartyFoundTab {...tab} />;
  if (mode === "JOIN") return <PartyJoinTab {...tab} />;
  return <PartyNoneTab {...tab} />;
}

/** O que cada modo recebe da aba: os dados resolvidos, o topo comum e a troca de modo. */
export type PartyModeProps = PartyTabProps & {
  me: Preparations["players"][number] | undefined;
  /** Convite, travas e a escolha do modo, no topo do corpo */
  lead: React.ReactNode;
  locked: boolean;
  onMode: (mode: Choice) => void;
};
