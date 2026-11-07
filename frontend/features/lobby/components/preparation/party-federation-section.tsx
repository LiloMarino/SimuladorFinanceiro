import { useState } from "react";
import { Clock, Handshake } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { PlayerOption } from "@/shared/components/player-option";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { defaultFederationName } from "@/shared/lib/federation-name";
import type { MyPreparation, Preparations, RoomPlayer } from "@/types";
import { useProposePreparationFederation } from "../../hooks/mutations/useProposePreparationFederation";
import { federationCandidates, federationPartners } from "../../lib/preparation";
import { PreparationSection } from "./preparation-section";

type PartyFederationSectionProps = {
  preparations: Preparations;
  mine: MyPreparation;
  me: Preparations["players"][number];
  /** Humanos na sala, para a cor de cada candidato */
  humans: RoomPlayer[];
};

/** A federação do fundador no lobby: propor a outro fundador, esperar a resposta ou desfazer a combinada. A trava da sala vem do fieldset que a contém. */
export function PartyFederationSection({ preparations, mine, me, humans }: PartyFederationSectionProps) {
  const [partnerChoice, setPartnerChoice] = useState<string | null>(null);
  const [candidateChoice, setCandidateChoice] = useState<string | null>(null);
  const [nameChoice, setNameChoice] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const propose = useProposePreparationFederation();

  const partners = federationPartners(preparations, me.nickname);
  const partner = partners.find((player) => player.nickname === partnerChoice) ?? partners[0];
  const candidates = partner ? federationCandidates(preparations, me.nickname, partner.nickname) : [];
  const candidate = candidates.find((entry) => entry.nickname === candidateChoice)?.nickname ?? me.nickname;
  const name =
    nameChoice ?? (me.party && partner?.party ? defaultFederationName(me.party.abbr, partner.party.abbr) : "");
  const colorOf = (nickname: string) => humans.find((player) => player.nickname === nickname)?.color;

  const send = (body: { partner?: string; name?: string; candidate?: string }) => {
    setError(null);
    propose.mutate(body, { onError: (err) => setError(err.message) });
  };

  return (
    <PreparationSection title="Federação" hint="com outro fundador da sala">
      {me.federation ? (
        // Federação combinada
        <div className="grid gap-2">
          <Badge variant="federation" className="justify-self-start">
            <Handshake /> {me.federation.name}
          </Badge>
          <span className="text-xs text-muted-foreground">
            Com {me.federation.partner}, candidato {me.federation.candidate}. Os dois partidos entram numa lista só no
            Congresso e disputam a primeira eleição juntos.
          </span>
          <Button
            type="button"
            size="sm"
            variant="outline-destructive"
            className="justify-self-start"
            disabled={propose.isPending}
            onClick={() => send({})}
          >
            Desfazer a federação
          </Button>
        </div>
      ) : mine.federation_invited ? (
        // Proposta enviada
        <div className="grid gap-2">
          <Badge variant="warning" className="justify-self-start">
            <Clock /> Proposta enviada · {mine.federation_invited} ainda não respondeu
          </Badge>
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="justify-self-start"
            disabled={propose.isPending}
            onClick={() => send({})}
          >
            Retirar a proposta
          </Button>
        </div>
      ) : mine.federation_invite ? (
        // Proposta recebida
        <span className="text-xs text-muted-foreground">
          {mine.federation_invite.owner} propôs federação ao seu partido. Aceite ou recuse no topo desta aba.
        </span>
      ) : partner ? (
        // Nova proposta
        <div className="grid gap-3">
          <span className="text-xs text-muted-foreground">
            Dois partidos viram uma lista só no Congresso e somam os votos na barreira. A chapa leva o candidato e as
            promessas do partido dele.
          </span>
          <Field>
            <FieldLabel>Com qual partido</FieldLabel>
            <Select
              value={partner.nickname}
              items={Object.fromEntries(
                partners.map((player) => [
                  player.nickname,
                  <span key={player.nickname} className="flex items-center gap-2">
                    {player.party && <PartyMark abbr={player.party.abbr} color={player.party.color} size="sm" />}
                    {player.party?.name} · {player.nickname}
                  </span>,
                ]),
              )}
              onValueChange={(value) => {
                if (!value) return;
                setPartnerChoice(value);
                setCandidateChoice(null);
                setNameChoice(null);
              }}
            >
              <SelectTrigger className="w-full" aria-label="Partido parceiro">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {partners.map((player) => (
                  <SelectItem key={player.nickname} value={player.nickname}>
                    <span className="flex items-center gap-2">
                      {player.party && <PartyMark abbr={player.party.abbr} color={player.party.color} size="sm" />}
                      {player.party?.name} · {player.nickname}
                    </span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field>
              <FieldLabel>Candidato da chapa</FieldLabel>
              <Select
                value={candidate}
                items={Object.fromEntries(
                  candidates.map((entry) => [
                    entry.nickname,
                    <PlayerOption key={entry.nickname} nickname={entry.nickname} color={colorOf(entry.nickname)} />,
                  ]),
                )}
                onValueChange={(value) => value && setCandidateChoice(value)}
              >
                <SelectTrigger className="w-full" aria-label="Candidato da chapa">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {candidates.map((entry) => (
                    <SelectItem key={entry.nickname} value={entry.nickname}>
                      <PlayerOption nickname={entry.nickname} color={colorOf(entry.nickname)} />
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </Field>
            <Field>
              <FieldLabel>Nome</FieldLabel>
              <Input
                value={name}
                maxLength={60}
                aria-label="Nome da federação"
                onChange={(event) => setNameChoice(event.target.value)}
              />
            </Field>
          </div>
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="justify-self-start"
            disabled={propose.isPending}
            onClick={() => send({ partner: partner.nickname, name: name.trim(), candidate })}
          >
            <Handshake />
            Propor federação
          </Button>
        </div>
      ) : (
        <span className="text-xs text-muted-foreground">
          Quando outro jogador preparar um partido, você pode propor federação a ele.
        </span>
      )}
      {error && <span className="text-xs text-destructive">{error}</span>}
    </PreparationSection>
  );
}
