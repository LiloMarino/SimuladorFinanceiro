import { UserPlus } from "lucide-react";
import { BotDialog } from "@/shared/components/bot-dialog";
import { TeamGrid } from "@/shared/components/team-grid";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { useBotStrategies } from "@/shared/hooks/queries/useBotStrategies";
import { useRoomPlayers } from "@/shared/hooks/queries/useRoomPlayers";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";
import { addValues, editValues } from "@/shared/lib/bot-form";
import type { PlayerGrouping, Profession, RoomPlayer, TeamNaming } from "@/types";
import { useAddBot } from "../hooks/mutations/useAddBot";
import { useAddBots } from "../hooks/mutations/useAddBots";
import { useUpdateBot } from "../hooks/mutations/useUpdateBot";
import { batchRequests, NAME_TAKEN_STATUS } from "../lib/bot-form";

const NAME_TAKEN_MESSAGE = "Já tem um jogador com esse nome na sala. Sorteie outro ou mude.";

type LobbyBotDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** O bot a configurar; sem ele, o diálogo adiciona um */
  bot?: RoomPlayer | undefined;
  grouping: PlayerGrouping;
  naming: TeamNaming;
  /** Sala de profissões: as que o bot pode ter; nulo nas outras salas */
  professions: Profession[] | null;
  /** As vagas livres da sala: o teto da quantidade ao adicionar */
  freeSlots: number;
};

/** Adicionar ou configurar um bot da sala: o diálogo de bot com a equipe e a chamada ao servidor. */
export function LobbyBotDialog({
  open,
  onOpenChange,
  bot,
  grouping,
  naming,
  professions,
  freeSlots,
}: LobbyBotDialogProps) {
  const { data: players } = useRoomPlayers();
  const { data: settings } = useSimulationSettings();
  const { data: strategies } = useBotStrategies();
  const add = useAddBot();
  const addMany = useAddBots();
  const update = useUpdateBot(bot?.nickname ?? "");

  // Cor, nome e equipe dos outros jogadores: o bot em edição não conta contra si mesmo
  const others = (players ?? []).filter((p) => p.nickname !== bot?.nickname);

  return (
    <BotDialog
      open={open}
      onOpenChange={onOpenChange}
      title={bot ? "Configurar bot" : "Adicionar bot"}
      description="Joga sozinho, com carteira própria e as mesmas regras de dinheiro de todos."
      loading={!players || !settings}
      others={others}
      startingCash={settings?.simulation.starting_cash ?? "0"}
      cashLabel="o saldo inicial"
      initial={(strategies) =>
        bot?.bot
          ? editValues(strategies, {
              nickname: bot.nickname,
              color: bot.color,
              team: bot.team,
              strategyKey: bot.bot.strategy_key,
              params: bot.bot.params,
            })
          : addValues(strategies, players ?? [])
      }
      profession={professions ? { available: professions, initial: bot?.profession ?? null } : undefined}
      saved={bot?.bot ? { strategyKey: bot.bot.strategy_key, params: bot.bot.params } : undefined}
      nameTakenMessage={NAME_TAKEN_MESSAGE}
      nameHelp="Da lista da estratégia; é o nome no ranking."
      submitLabel={bot ? "Salvar" : "Adicionar bot"}
      submitIcon={bot ? null : <UserPlus className="size-3.5" />}
      saving={add.isPending || addMany.isPending || update.isPending}
      maxQuantity={bot ? undefined : freeSlots}
      extraFields={(form) =>
        grouping === "TEAMS" && (
          <Field>
            <FieldLabel>Equipe</FieldLabel>
            <TeamGrid
              players={others}
              naming={naming}
              selected={form.watch("team")}
              onSelect={(next) => form.setValue("team", next)}
            />
            <FieldDescription>
              No modo em equipes, o host escolhe a equipe do bot. “Distribuir quem falta” também distribui os bots.
            </FieldDescription>
          </Field>
        )
      }
      onSubmit={(values, { close, refuseName }) => {
        // Vários bots: o servidor cria o lote inteiro, com nomes já sorteados fora dos da sala
        if (!bot && values.quantity > 1) {
          const requests = batchRequests(
            strategies ?? [],
            others.map((p) => p.nickname),
            values,
          );
          addMany.mutate(requests, { onSuccess: close });
          return;
        }
        const request = {
          nickname: values.nickname,
          strategy_key: values.strategyKey,
          params: values.params,
          color: values.color,
          team: grouping === "TEAMS" ? values.team : null,
          profession: values.profession,
        };
        const options = {
          onSuccess: close,
          onError: (err: { status: number }) => {
            if (err.status === NAME_TAKEN_STATUS) refuseName();
          },
        };
        if (bot) update.mutate(request, options);
        else add.mutate(request, options);
      }}
    />
  );
}
