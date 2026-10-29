import { Gavel, Trophy } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
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
import { displayDayMonth, displayShortDate, displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { ElectionPanel, ElectionRound } from "@/types";
import { GROUP_INFO, pollPoints } from "../lib/voters";
import { PartyMark, PersonMark } from "./party-mark";
import { PromiseBadges } from "./promise-badges";

type RoundResultDialogProps = {
  result: ElectionRound | null;
  /** Dados atuais da eleição: dizem se quem vê pode doar */
  panel: ElectionPanel | undefined;
  onClose: () => void;
  onOpenPage: () => void;
};

/** O resultado de um turno, para todos: quem ficou onde, quem avança ou governa e o que vem a seguir. */
export function RoundResultDialog({ result, panel, onClose, onOpenPage }: RoundResultDialogProps) {
  const winner = result?.parties.find((party) => party.party_id === result.winner);
  const finalists = result?.parties.filter((party) => result.finalists.includes(party.party_id)) ?? [];
  const ranked = result
    ? [...result.parties].sort((a, b) => Number(b.share) - Number(a.share) || a.party_id - b.party_id)
    : [];
  const donations = result?.donations.filter((entry) => Number(entry.amount) > 0) ?? [];
  const canDonate = panel?.can_donate ?? false;

  return (
    <Dialog open={result !== null} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="flex max-h-[calc(100dvh-2rem)] flex-col sm:max-w-130">
        {result && (
          <>
            <DialogHeader variant="divided">
              <DialogTitle>Resultado do {result.round}º turno</DialogTitle>
              <DialogDescription>
                Eleição de {result.election_year} · {displayShortDate(result.date)} · a partida está pausada; retome
                pelo controle de velocidade no topo.
              </DialogDescription>
            </DialogHeader>

            <DialogBody>
              <div className="grid gap-3.5">
                <div className="grid gap-2">
                  {ranked.map((party) => (
                    <div
                      key={party.party_id}
                      className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-3 text-[13px]"
                    >
                      <span className="flex min-w-0 items-center gap-2">
                        <PartyMark abbr={party.abbr} color={party.color} size="sm" />
                        {party.candidate && <PersonMark person={party.candidate} />}
                        <span className="truncate">{party.candidate?.name ?? party.name}</span>
                      </span>
                      <span className="font-mono font-semibold">{displayPercent(party.share, 1)}</span>
                      <span className="relative col-span-2 h-2 rounded-full bg-muted">
                        <span
                          className="absolute inset-y-0 left-0 rounded-full"
                          style={{
                            width: `${Number(party.share) * 100}%`,
                            backgroundColor: party.color ?? "var(--muted-foreground)",
                          }}
                        />
                      </span>
                    </div>
                  ))}
                </div>

                {result.round === 2 && (
                  <div className="grid gap-1.5 text-xs text-muted-foreground">
                    <span className="text-sm font-medium text-foreground">
                      Por grupo de eleitores · não votaram {Number(result.not_voted).toFixed(1).replace(".", ",")}% do
                      eleitorado
                    </span>
                    {result.groups.map((group) => {
                      const points = pollPoints(group.entries);
                      return (
                        <span key={group.group} className="flex flex-wrap justify-between gap-x-3">
                          <span>{GROUP_INFO[group.group].label}</span>
                          <span className="font-mono">
                            {finalists
                              .map((party) => `${party.abbr} ${Math.round(points.get(party.party_id) ?? 0)}`)
                              .join(" · ")}
                            {` · indecisos ${Math.round(Number(group.undecided))}`}
                          </span>
                        </span>
                      );
                    })}
                  </div>
                )}

                {winner ? (
                  <Alert variant="success">
                    <Trophy />
                    <AlertTitle>
                      {winner.candidate ? `${winner.candidate.name} (${winner.abbr})` : `O candidato do ${winner.abbr}`}{" "}
                      venceu
                      {result.round === 1 ? " já no 1º turno" : ""}
                    </AlertTitle>
                    <AlertDescription>
                      {winner.vice ? `Vice: ${winner.vice.name}. ` : "Chapa sem vice. "}
                      A posse é em {displayShortDate(panel?.dates.inauguration ?? result.date)}, e o mandato dura 4
                      anos.
                      {winner.promises.length > 0 && (
                        <span className="mt-2 grid gap-1">
                          <b className="text-foreground">O que o governo eleito prometeu</b>
                          <PromiseBadges promises={winner.promises} computer={winner.is_computer} />
                          <span>Cobradas no fim do mandato, pelo que estiver em vigor.</span>
                        </span>
                      )}
                    </AlertDescription>
                  </Alert>
                ) : (
                  <Alert variant="info">
                    <Gavel />
                    <AlertTitle>Vai ao 2º turno: {finalists.map((party) => party.abbr).join(" e ")}</AlertTitle>
                    <AlertDescription>
                      Ninguém passou de 50% dos votos válidos. Os eleitores dos partidos que ficaram de fora se dividem
                      entre os finalistas e os indecisos, e a disputa continua até a votação.
                      {panel && ` O 2º turno é em ${displayShortDate(panel.dates.runoff)}.`}
                    </AlertDescription>
                  </Alert>
                )}

                {canDonate && panel && (
                  <Alert variant="warning">
                    <AlertTitle>
                      Os filiados do seu partido podem doar a um finalista até{" "}
                      {displayDayMonth(panel.dates.donation_deadline)}
                    </AlertTitle>
                    <AlertDescription>
                      A doação é pública, sai do patrimônio de quem doa e vira verba do finalista.
                    </AlertDescription>
                  </Alert>
                )}

                {donations.length > 0 && (
                  <div className="grid gap-1 text-xs text-muted-foreground">
                    <span className="text-sm font-medium text-foreground">Doações entre os turnos</span>
                    {donations.map((entry) => {
                      const party = result.parties.find((p) => p.party_id === entry.party_id);
                      return (
                        <span key={entry.party_id}>
                          {party?.abbr}: {displayMoney(entry.amount)} doados
                        </span>
                      );
                    })}
                  </div>
                )}
              </div>
            </DialogBody>

            <DialogFooter variant="divided" className="sm:justify-end">
              <Button variant="outline" onClick={onClose}>
                Fechar
              </Button>
              <Button onClick={onOpenPage}>Ver a página da eleição</Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
