import { useState } from "react";
import { Flag } from "lucide-react";
import { PartyMark } from "@/shared/components/party-mark";
import { ValueChips } from "@/shared/components/value-chip";
import { Button } from "@/shared/components/ui/button";
import { displayMonthSlashYear } from "@/shared/lib/utils/display";
import { useSetPreparation } from "../../hooks/mutations/useSetPreparation";
import { affiliationDeadline } from "../../lib/government-rules";
import { PreparationFooter } from "./preparation-footer";
import { PreparationSection } from "./preparation-section";
import type { PartyModeProps } from "./party-tab";

/** Sem partido: quando ainda dá para entrar num partido e concorrer, o partido salvo e os partidos da sala. */
export function PartyNoneTab({
  preparations,
  saved,
  nickname,
  rules,
  savedSimulation,
  lead,
  locked,
  onMode,
  onClose,
}: PartyModeProps) {
  const [error, setError] = useState<string | null>(null);
  const prepare = useSetPreparation();
  const parties = preparations.players.filter((p) => p.kind === "FOUND" && p.party && p.nickname !== nickname);
  const firstElection = rules.first_election ?? "";
  const deadline = affiliationDeadline(rules.start_date, firstElection);

  const timeline = [
    {
      when: displayMonthSlashYear(rules.start_date),
      title: "Desde o 1º dia",
      text: "Fundar o seu partido ou entrar no de outro jogador, na tela Eleição.",
    },
    ...(deadline
      ? [
          {
            when: `até ${displayMonthSlashYear(deadline)}`,
            title: "Filiar-se para concorrer",
            text: `Quem está num partido até 6 meses antes do 1º turno (${displayMonthSlashYear(firstElection)}) pode ser candidato ou vice nessa eleição.`,
          },
        ]
      : []),
    {
      when: "depois",
      title: "Filiado, sem concorrer",
      text: "Ainda dá para entrar num partido, mas a candidatura fica para a eleição seguinte.",
    },
  ];

  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        setError(null);
        prepare.mutate({ kind: "NONE" }, { onError: (err) => setError(err.message) });
      }}
      className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]"
    >
      <div className="grid min-h-0 content-start gap-4.5 overflow-y-auto px-6 py-5">
        {lead}
        <fieldset
          disabled={locked}
          className="grid min-w-0 grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)] items-start gap-6 disabled:opacity-55"
        >
          {/* Linha do tempo da filiação */}
          <div className="grid min-w-0 gap-3">
            <div className="grid gap-0.5">
              <b className="text-sm font-semibold">Você começa a partida sem partido</b>
              <span className="text-[13px] text-muted-foreground">
                Nada sai do seu caixa, e o partido continua possível dentro da partida. O que muda é a eleição em que
                você pode concorrer.
              </span>
            </div>
            <ol className="grid">
              {timeline.map((step) => (
                <li key={step.title} className="grid grid-cols-[6.5rem_1fr] gap-3 border-t border-muted py-2.5">
                  <span className="font-mono text-xs text-muted-foreground">{step.when}</span>
                  <div className="grid gap-0.5">
                    <b className="text-[13px] font-semibold">{step.title}</b>
                    <span className="text-xs text-muted-foreground">{step.text}</span>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          <div className="grid min-w-0 gap-4.5">
            {/* Partido salvo no perfil */}
            <PreparationSection title="Seu partido" hint="salvo no perfil">
              {saved ? (
                <div className="grid gap-2.5 rounded-lg border p-3">
                  <div className="flex items-center gap-2.5">
                    <PartyMark abbr={saved.abbr} color={saved.color} size="lg" />
                    <b className="truncate text-sm font-semibold" title={saved.name}>
                      {saved.name}
                    </b>
                  </div>
                  <ValueChips values={saved.flags} />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="justify-self-start"
                    onClick={() => onMode("FOUND")}
                  >
                    <Flag /> Fundar nesta sala
                  </Button>
                  <span className="text-xs text-muted-foreground">
                    Fundar troca a escolha para “Fundar o meu partido” com você de candidato e sem vice.
                  </span>
                </div>
              ) : (
                <div className="grid gap-2 rounded-lg border border-dashed p-3">
                  <b className="text-[13px] font-semibold">Você ainda não montou o seu partido</b>
                  <span className="text-xs text-muted-foreground">
                    Nome, sigla, cor e bandeiras ficam no perfil e voltam prontos nas próximas salas.
                  </span>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="justify-self-start"
                    onClick={() => onMode("FOUND")}
                  >
                    Montar em Fundar o meu partido
                  </Button>
                </div>
              )}
            </PreparationSection>

            {/* Partidos da sala */}
            {parties.length > 0 && (
              <PreparationSection title="Nesta sala">
                <div className="flex flex-wrap items-center gap-2">
                  {parties.map(
                    (p) =>
                      p.party && <PartyMark key={p.nickname} abbr={p.party.abbr} color={p.party.color} size="md" />,
                  )}
                  <span className="text-xs text-muted-foreground">
                    {parties.length} {parties.length === 1 ? "partido preparado" : "partidos preparados"} por jogadores
                  </span>
                  <Button type="button" variant="link" size="sm" onClick={() => onMode("JOIN")}>
                    Ver em Entrar
                  </Button>
                </div>
              </PreparationSection>
            )}

            <span className="text-xs text-muted-foreground">
              Na próxima sala você começa sem partido de novo: a última escolha volta marcada.
            </span>
          </div>
        </fieldset>
      </div>

      <PreparationFooter
        note={
          savedSimulation
            ? "Travado com partida salva selecionada."
            : "Fica no seu perfil: a escolha de começar sem partido."
        }
        error={error}
        saving={prepare.isPending}
        canSave={!locked}
        onClose={onClose}
      />
    </form>
  );
}
