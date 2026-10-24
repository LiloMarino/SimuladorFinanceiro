import { Plus } from "lucide-react";
import { BotDialog, type BotSubmit } from "@/shared/components/bot-dialog";
import { addValues, type BotFormValues } from "@/shared/lib/bot-form";
import { moneyToBody } from "@/shared/lib/utils/money-field";

const NAME_TAKEN_MESSAGE = "Outra estratégia já tem esse nome. Sorteie outro ou mude.";

type BacktestBotDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  /** A estratégia a configurar; sem ela, o diálogo adiciona uma */
  participant?: BotFormValues;
  /** As outras estratégias do backtest: ocupam nome e cor */
  others: BotFormValues[];
  startDate: string;
  startingCash: string;
  onSubmit: (values: BotFormValues) => void;
};

/** Adicionar ou configurar uma estratégia do backtest: o diálogo de bot, sem equipe nem chamada ao servidor. */
export function BacktestBotDialog({
  open,
  onOpenChange,
  participant,
  others,
  startDate,
  startingCash,
  onSubmit,
}: BacktestBotDialogProps) {
  return (
    <BotDialog
      open={open}
      onOpenChange={onOpenChange}
      title={participant ? "Configurar estratégia" : "Adicionar estratégia"}
      description="Vira um jogador sem pessoa, com carteira própria e as mesmas regras de dinheiro das outras."
      startDate={startDate}
      others={others}
      startingCash={moneyToBody(startingCash)}
      cashLabel="o saldo inicial"
      initial={(strategies) => participant ?? addValues(strategies, others)}
      nameTakenMessage={NAME_TAKEN_MESSAGE}
      nameHelp="Da lista da estratégia; é o nome no gráfico e no ranking."
      compareToDefault
      submitLabel={participant ? "Salvar" : "Adicionar estratégia"}
      submitIcon={participant ? null : <Plus className="size-3.5" />}
      saving={false}
      onSubmit={(bot: BotSubmit, { close }) => {
        onSubmit({
          nickname: bot.nickname,
          strategyKey: bot.strategyKey,
          color: bot.color,
          team: null,
          drafts: bot.drafts,
        });
        close();
      }}
    />
  );
}
