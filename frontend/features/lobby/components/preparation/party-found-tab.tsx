import { useState } from "react";
import { Controller, useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { CircleAlert, Clock, TriangleAlert, UserCheck, UserX } from "lucide-react";
import { ContributionField } from "@/shared/components/contribution-field";
import { FlagCards } from "@/shared/components/flag-cards";
import { OptionSelect, type SelectOption } from "@/shared/components/option-select";
import { PartyIdentityFields } from "@/shared/components/party-identity-fields";
import { PartyMark } from "@/shared/components/party-mark";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { ProfileRadar } from "@/shared/components/profile-radar";
import { ValueChip } from "@/shared/components/value-chip";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldLabel } from "@/shared/components/ui/field";
import { contributionAmount, contributionText, STARTING_CONTRIBUTION_CAP } from "@/shared/lib/contribution";
import { defaultPartyColor } from "@/shared/lib/party-colors";
import { flagRadarScores } from "@/shared/lib/party-flags";
import { partyIdentitySchema } from "@/shared/lib/party-identity";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { PartyIdentity, VoterValue } from "@/types";
import { useSaveMyParty } from "../../hooks/mutations/useSaveMyParty";
import { useSavePartyContribution } from "../../hooks/mutations/useSavePartyContribution";
import { useSetPreparation } from "../../hooks/mutations/useSetPreparation";
import { useAutosave } from "../../hooks/useAutosave";
import { cashShare, closeRivalTag, rivalsOf, sharedFlags, type Rival } from "../../lib/preparation";
import { PartyFederationSection } from "./party-federation-section";
import { PreparationFooter } from "./preparation-footer";
import { PreparationSection } from "./preparation-section";
import type { PartyModeProps } from "./party-tab";

/** Fundar o meu partido: identidade e bandeiras à esquerda; chapa, contribuição e com quem divide eleitor à direita. */
export function PartyFoundTab({
  preparations,
  mine,
  me,
  saved,
  contribution,
  humans,
  nickname,
  rules,
  savedSimulation,
  lead,
  locked,
  onClose,
}: PartyModeProps) {
  const rivals = rivalsOf(preparations, nickname);
  const taken = rivals.flatMap((rival) => (rival.color ? [{ color: rival.color, abbr: rival.abbr }] : []));
  // O partido em branco nasce uma vez: a cor marcada fica a mesma quando um rival troca a dele
  const [blank] = useState<PartyIdentity>(() => {
    const ownColor = humans.find((player) => player.nickname === nickname)?.color;
    return {
      name: "",
      abbr: "",
      color: defaultPartyColor(
        ownColor,
        taken.map((party) => party.color),
      ),
      flags: [],
    };
  });
  const form = useForm<PartyIdentity>({
    resolver: zodResolver(partyIdentitySchema),
    values: saved ?? blank,
    mode: "onChange",
    resetOptions: { keepDirtyValues: true },
  });
  const draft = useWatch({ control: form.control });
  const flags = useWatch({ control: form.control, name: "flags" });
  const color = useWatch({ control: form.control, name: "color" });
  const founding = me?.kind === "FOUND" ? me : undefined;
  const [candidate, setCandidate] = useState(founding?.candidate ?? nickname);
  const [vice, setVice] = useState<string | null>(founding?.vice ?? mine.invited ?? mine.vice_declined);
  const [amount, setAmount] = useState(contributionText(contribution));
  const [inviteError, setInviteError] = useState<string | null>(null);
  const saveParty = useSaveMyParty();
  const saveContribution = useSavePartyContribution();
  const prepare = useSetPreparation();
  const inviteVice = useSetPreparation();

  // Grava a identidade e a contribuição no perfil e só depois a escolha da sala, que parte do perfil
  const identity = partyIdentitySchema.safeParse(draft);
  const savedIdentity = saved ?? blank;
  const identityChanged =
    !identity.success ||
    identity.data.name !== savedIdentity.name ||
    identity.data.abbr !== savedIdentity.abbr ||
    identity.data.color !== savedIdentity.color ||
    [...identity.data.flags].sort().join() !== [...savedIdentity.flags].sort().join();
  const autosave = useAutosave({
    dirty:
      !locked &&
      (me?.kind !== "FOUND" ||
        identityChanged ||
        Number(contributionAmount(amount)) !== Number(contribution) ||
        candidate !== founding?.candidate),
    incomplete: identity.success ? null : (identity.error.issues[0]?.message ?? "Falta completar o partido."),
    signature: JSON.stringify({ draft, amount, candidate }),
    save: async () => {
      if (!identity.success) return;
      await saveParty.mutateAsync(identity.data);
      await saveContribution.mutateAsync(contributionAmount(amount));
      await prepare.mutateAsync({ kind: "FOUND", candidate });
    },
  });

  const members = preparations.players
    .filter((p) => p.kind === "JOIN" && p.founder === nickname)
    .map((p) => p.nickname);
  const candidates = [nickname, ...members].map((name) => ({
    nickname: name,
    color: humans.find((player) => player.nickname === name)?.color,
  }));
  const viceOptions = humans.filter((player) => player.nickname !== candidate);
  // O vice escolhido some do seletor quando vira o candidato
  const viceValue = vice === candidate ? null : vice;
  // O convite vigente: aceito ou aguardando; o recusado pode ser refeito
  const currentVice = founding?.vice_accepted ? founding.vice : mine.invited;
  const sendInvite = (body: { kind: "INVITE_VICE"; vice: string } | { kind: "WITHDRAW_VICE" }) => {
    setInviteError(null);
    inviteVice.mutate(body, { onError: (err) => setInviteError(err.message) });
  };

  return (
    <form onSubmit={(event) => event.preventDefault()} className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 content-start gap-4.5 overflow-y-auto px-6 py-5">
        {lead}
        <fieldset
          disabled={locked}
          className="grid min-w-0 grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] items-start gap-6 disabled:opacity-55"
        >
          {/* Identidade e bandeiras */}
          <div className="grid min-w-0 gap-4.5">
            <PreparationSection title="Identidade" hint="salva no perfil">
              <PartyIdentityFields control={form.control} taken={taken} idPrefix="prep-party" />
            </PreparationSection>
            <Controller
              control={form.control}
              name="flags"
              render={({ field, fieldState }) => (
                <FlagCards
                  value={field.value}
                  onChange={field.onChange}
                  tag={closeRivalTag(field.value, rivals)}
                  columns={2}
                  error={fieldState.error?.message}
                />
              )}
            />
            <PreparationSection title="Como o eleitorado recebe" hint="perfil de partida">
              <div className="flex justify-center">
                <ProfileRadar
                  width={308}
                  height={188}
                  labelSize={12}
                  highlighted={flags}
                  label="Perfil de partida do partido"
                  series={[
                    {
                      key: "profile",
                      scores: flagRadarScores(flags, preparations.radar_neutral, preparations.radar_flag),
                      color,
                    },
                  ]}
                />
              </div>
            </PreparationSection>
          </div>

          {/* Chapa, contribuição e rivais */}
          <div className="grid min-w-0 gap-4.5">
            <PreparationSection title="Chapa" hint="só nesta sala">
              <div className="grid grid-cols-2 gap-3">
                <Field>
                  <FieldLabel>Candidato</FieldLabel>
                  <OptionSelect
                    value={candidate}
                    options={candidates.map((item): SelectOption => ({
                      value: item.nickname,
                      label: item.nickname === nickname ? `${item.nickname} (você)` : item.nickname,
                      leading: <PlayerAvatar nickname={item.nickname} color={item.color} size="sm" />,
                    }))}
                    onChange={setCandidate}
                    className="w-full"
                    aria-label="Candidato"
                  />
                </Field>
                <Field>
                  <FieldLabel>Vice</FieldLabel>
                  <OptionSelect
                    value={viceValue}
                    options={viceOptions.map((player): SelectOption => ({
                      value: player.nickname,
                      label: player.nickname,
                      leading: <PlayerAvatar nickname={player.nickname} color={player.color} size="sm" />,
                    }))}
                    onChange={setVice}
                    placeholder="Escolha o vice"
                    className="w-full"
                    aria-label="Vice"
                  />
                </Field>
              </div>
              {/* Convite do vice */}
              <div className="flex flex-wrap items-center gap-2">
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={!founding || viceValue === null || viceValue === currentVice || inviteVice.isPending}
                  onClick={() => viceValue && sendInvite({ kind: "INVITE_VICE", vice: viceValue })}
                >
                  Convidar
                </Button>
                {founding?.vice_accepted && founding.vice && (
                  <Badge variant="success">
                    <UserCheck /> {founding.vice} aceitou ser vice
                  </Badge>
                )}
                {mine.invited && (
                  <Badge variant="warning">
                    <Clock /> Convite enviado · {mine.invited} ainda não respondeu
                  </Badge>
                )}
                {mine.vice_declined && (
                  <Badge variant="secondary">
                    <UserX /> {mine.vice_declined} recusou o convite
                  </Badge>
                )}
                {(currentVice || mine.vice_declined) && (
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={inviteVice.isPending}
                    onClick={() => sendInvite({ kind: "WITHDRAW_VICE" })}
                  >
                    Retirar convite
                  </Button>
                )}
              </div>
              {inviteError && (
                <Alert variant="destructive">
                  <CircleAlert />
                  <AlertDescription>{inviteError}</AlertDescription>
                </Alert>
              )}
              <span className="text-xs text-muted-foreground">
                {founding
                  ? "Escolher o vice não o convida: use Convidar. Um novo convite ocupa o lugar do anterior."
                  : "Com o partido salvo, você pode convidar o vice."}
              </span>
            </PreparationSection>

            <PreparationSection title="Contribuição mensal" hint="vale fundando ou entrando">
              <ContributionField
                id="prep-found-contribution"
                value={amount}
                onChange={setAmount}
                cap={STARTING_CONTRIBUTION_CAP}
                note={`${cashShare(contributionAmount(amount), rules.starting_cash)} do saldo inicial desta sala (${displayMoneyWhole(rules.starting_cash)}). Cobrada no 1º dia útil de cada mês da campanha. Mês sem caixa vira pendência.`}
              />
            </PreparationSection>

            {founding && (
              <PartyFederationSection preparations={preparations} mine={mine} me={founding} humans={humans} />
            )}

            <SharedVoters flags={flags} rivals={rivals} />
          </div>
        </fieldset>

        {/* Conflitos que travam o Iniciar */}
        {preparations.conflicts.length > 0 && (
          <Alert variant="destructive">
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

      <PreparationFooter
        note={
          savedSimulation
            ? "Travado com partida salva selecionada."
            : "Fica no seu perfil: identidade, bandeiras e contribuição. Só nesta sala: a chapa."
        }
        saving={autosave.saving}
        error={autosave.error}
        incomplete={autosave.incomplete}
        onRetry={autosave.retry}
        onClose={onClose}
      />
    </form>
  );
}

/** "Com quem você divide eleitor": cada partido da sala com as bandeiras que repete as suas. */
function SharedVoters({ flags, rivals }: { flags: VoterValue[]; rivals: Rival[] }) {
  const rows = rivals
    .map((rival) => ({ rival, shared: sharedFlags(flags, rival) }))
    .sort((a, b) => b.shared.length - a.shared.length);
  const closest = rows[0];
  return (
    <div className="grid gap-1.5 rounded-[10px] border px-3.5 py-3">
      <div className="grid gap-0.5">
        <b className="text-[13.5px] font-semibold">Com quem você divide eleitor</b>
        <span className="text-xs text-muted-foreground">
          Bandeira em comum disputa o mesmo grupo de eleitores.
          {closest &&
            closest.shared.length >= 2 &&
            ` Com ${closest.shared.length} de 3 iguais, você e o ${closest.rival.abbr} largam brigando pelo mesmo voto.`}
        </span>
      </div>
      {rows.map(({ rival, shared }) => (
        <div
          key={rival.abbr}
          className="grid grid-cols-[2.75rem_minmax(0,1fr)_auto] items-center gap-2.5 border-t border-muted py-2"
        >
          <PartyMark abbr={rival.abbr} color={rival.color} size="sm" />
          <div className="grid min-w-0 gap-1">
            <span className="truncate text-[12.5px]" title={rival.name}>
              {rival.name} · {rival.founder ?? "computador"}
            </span>
            {shared.length > 0 && (
              <span className="flex flex-wrap gap-1">
                {shared.map((flag) => (
                  <ValueChip key={flag} value={flag} />
                ))}
              </span>
            )}
          </div>
          <Badge variant={shared.length === 0 ? "success" : shared.length === 1 ? "secondary" : "warning"} size="sm">
            {shared.length === 0 ? "nenhuma" : shared.length === 1 ? "1 bandeira" : `${shared.length} bandeiras`}
          </Badge>
        </div>
      ))}
    </div>
  );
}
