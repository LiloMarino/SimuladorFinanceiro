import { useState } from "react";
import { Briefcase, Lock } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Empty, EmptyDescription, EmptyHeader, EmptyMedia, EmptyTitle } from "@/shared/components/ui/empty";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import type {
  BotTicker,
  FundIdentity,
  FundPreparationRequest,
  Preparations,
  RoomPlayer,
  SimulationSettings,
} from "@/types";
import { fundChoice } from "../../lib/fund-preparation";
import { FundFoundTab } from "./fund-found-tab";
import { FundNoneTab } from "./fund-none-tab";
import { PreparationFooter } from "./preparation-footer";

type FundChoice = FundPreparationRequest["kind"];

export type FundTabProps = {
  preparations: Preparations;
  /** A gestora salva no perfil; nula enquanto o jogador não salvou uma */
  saved: FundIdentity | null;
  /** Humanos na sala: a cor de quem preparou cada gestora */
  humans: RoomPlayer[];
  /** As ações da partida: as letras delas não servem de sigla */
  assets: BotTicker[];
  nickname: string;
  rules: SimulationSettings["simulation"];
  /** O nome da partida salva selecionada; nulo quando a sala prepara uma partida nova */
  savedSimulation: string | null;
  onClose: () => void;
};

/** Aba Gestora: fundar a própria gestora no 1º dia ou ficar sem, com as travas da sala. */
export function FundTab(props: FundTabProps) {
  const { preparations, nickname, rules, savedSimulation, onClose } = props;
  // A escolha aberta na aba começa na que o servidor já guarda
  const [mode, setMode] = useState<FundChoice>(fundChoice(preparations, nickname));

  if (!rules.funds_enabled) {
    return (
      <div className="grid min-h-0 grid-rows-[minmax(0,1fr)_auto]">
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <Briefcase />
            </EmptyMedia>
            <EmptyTitle>Gestora só com a expansão Gestoras</EmptyTitle>
            <EmptyDescription>
              A expansão está desligada nesta sala. A sua gestora salva continua no perfil e volta quando o host ligar a
              expansão. A profissão, o partido e as estratégias seguem valendo.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
        <PreparationFooter note="O host liga a expansão em Editar regras." onClose={onClose} />
      </div>
    );
  }

  const locked = preparations.fund_locked_reason !== null;
  const lead = (
    <>
      {/* Travas da sala */}
      {savedSimulation ? (
        <Alert variant="muted">
          <Lock />
          <AlertTitle>Continuar · {savedSimulation}</AlertTitle>
          <AlertDescription>
            A partida salva já passou do 1º dia: a gestora dela, se houver, continua como estava. O que você mudar aqui
            vale na próxima partida nova.
          </AlertDescription>
        </Alert>
      ) : (
        locked && (
          <Alert variant="muted">
            <Lock />
            <AlertDescription>{preparations.fund_locked_reason}</AlertDescription>
          </Alert>
        )
      )}

      {/* Escolha */}
      <ToggleGroup
        variant="segmented"
        aria-label="Como você começa a partida"
        value={[mode]}
        onValueChange={(values) => values[0] && setMode(values[0] as FundChoice)}
        disabled={locked}
        className="w-full"
      >
        <ToggleGroupItem value="FOUND" className="flex-1">
          Fundar a minha gestora
        </ToggleGroupItem>
        <ToggleGroupItem value="NONE" className="flex-1">
          Sem gestora
        </ToggleGroupItem>
      </ToggleGroup>
    </>
  );

  const tab = { ...props, lead, locked, onMode: setMode };
  return mode === "FOUND" ? <FundFoundTab {...tab} /> : <FundNoneTab {...tab} />;
}

/** O que cada escolha recebe da aba: os dados resolvidos, o topo comum e a troca de escolha. */
export type FundModeProps = FundTabProps & {
  /** Travas e a escolha, no topo do corpo */
  lead: React.ReactNode;
  locked: boolean;
  onMode: (mode: FundChoice) => void;
};
