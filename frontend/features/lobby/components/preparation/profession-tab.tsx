import { Info, Lock, TriangleAlert } from "lucide-react";
import { useState } from "react";
import { CommissionedPartyPicker, type PartyOption } from "@/shared/components/commissioned-party-picker";
import { ProfessionCards } from "@/shared/components/profession-cards";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { PROFESSIONS, type RoomRules } from "@/shared/lib/professions";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { Profession } from "@/types";
import { useChooseProfession } from "../../hooks/mutations/useChooseProfession";
import { PreparationFooter } from "./preparation-footer";

type ProfessionTabProps = {
  /** A profissão do jogador na sala; nula enquanto ele não escolheu */
  current: Profession | null | undefined;
  /** A sigla do partido do Comissionado; nula nas outras profissões */
  currentParty: string | null;
  /** Os partidos que o Comissionado pode escolher */
  parties: PartyOption[];
  /** O nome da partida salva que guarda a profissão do jogador; nulo fora dela */
  lockedBy: string | null;
  /** O nome da partida salva em que o jogador entra como novo; nulo fora desse caso */
  joiningNew: string | null;
  /** As regras da sala: o salário que o host definiu e o que cada profissão sente */
  room: RoomRules;
  onClose: () => void;
};

/** Aba Profissão: cada clique grava na hora; o servidor recusa fora da hora e a escolha volta à anterior. */
export function ProfessionTab({
  current,
  currentParty,
  parties,
  lockedBy,
  joiningNew,
  room,
  onClose,
}: ProfessionTabProps) {
  const { mutate, isPending, variables, error } = useChooseProfession();
  const locked = lockedBy !== null;
  // Durante o salvamento o cartão clicado já aparece marcado; sem a resposta do servidor ele volta ao anterior
  const shown = isPending ? variables.profession : current;
  // O Comissionado só vai ao servidor com partido: o clique no cartão abre a escolha do partido
  const [choosingParty, setChoosingParty] = useState(false);
  const commissioned = shown === "COMMISSIONED" || choosingParty;
  const partyValid = currentParty !== null && parties.some((party) => party.abbr === currentParty);

  function selectProfession(profession: Profession) {
    if (profession !== "COMMISSIONED") {
      setChoosingParty(false);
      mutate({ profession });
    } else if (partyValid) {
      mutate({ profession, party: currentParty });
    } else {
      setChoosingParty(true);
    }
  }

  return (
    <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
      <div className="grid min-h-0 content-start gap-4.5 overflow-y-auto px-6 py-5">
        <div className="grid gap-0.5">
          <b className="text-base font-semibold">
            {locked ? `Sua profissão em ${lockedBy}` : "Sua profissão nesta sala"}
          </b>
          <span className="text-[13px] text-muted-foreground">
            Muda só o que entra por mês e o que o governo faz com a renda: a despesa e a meta são as mesmas para todos.
            Valores com o salário de{" "}
            <b className="font-mono font-semibold text-foreground">{displayMoneyWhole(Number(room.monthly_salary))}</b>{" "}
            que o host definiu.
          </span>
        </div>

        {/* Partida salva */}
        {locked && (
          <Alert variant="muted">
            <Lock />
            <AlertDescription>
              A profissão fica com a partida salva, como a cor. A do seu perfil volta a valer na próxima sala.
            </AlertDescription>
          </Alert>
        )}
        {joiningNew && (
          <Alert variant="info">
            <Info />
            <AlertDescription>
              Você entra em {joiningNew} como jogador novo. Confira a profissão antes de entrar: a do seu perfil é a que
              vale se você não trocar.
            </AlertDescription>
          </Alert>
        )}

        <ProfessionCards
          room={room}
          selected={choosingParty ? "COMMISSIONED" : shown}
          disabled={locked}
          onSelect={selectProfession}
        />

        {/* Partido do Comissionado */}
        {commissioned && (
          <CommissionedPartyPicker
            options={parties}
            value={partyValid ? currentParty : null}
            disabled={locked}
            onChange={(party) => {
              setChoosingParty(false);
              mutate({ profession: "COMMISSIONED", party });
            }}
          />
        )}

        {/* Recusa do servidor */}
        {error && (
          <Alert variant="warning">
            <TriangleAlert />
            <AlertTitle>Não deu para trocar a profissão</AlertTitle>
            <AlertDescription>
              {error.message}
              {current ? ` Sua profissão segue ${PROFESSIONS[current].name}.` : ""}
            </AlertDescription>
          </Alert>
        )}
      </div>

      <PreparationFooter
        note="A profissão fica no seu perfil e vale nas próximas salas. Numa partida salva, vale a profissão guardada nela."
        saving={error ? undefined : isPending}
        onClose={onClose}
      />
    </div>
  );
}
