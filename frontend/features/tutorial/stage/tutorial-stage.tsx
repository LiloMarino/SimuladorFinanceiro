import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthContext, type AuthContextValue } from "@/shared/context/auth/AuthContext";
import { RealtimeContext } from "@/shared/context/realtime";
import { SimulationContext } from "@/shared/context/simulation";
import { BaseSubscriberRealtime } from "@/shared/lib/realtime/BaseSubscriberRealtime";
import { queryClient as appQueryClient } from "@/shared/lib/queryClient";
import { queryKeys } from "@/shared/lib/queryKeys";
import type { MyStrategy } from "@/types";
import { installStageFetch } from "./stage-fetch";
import { StageContext } from "./stage-context";

/** Subscriber do palco: não escuta nada, porque os dados do exemplo não mudam sozinhos. */
class SilentSubscriber extends BaseSubscriberRealtime {
  connect() {}
  send() {}
  protected async updateBackendSubscription() {}
}

const subscriber = new SilentSubscriber();
const realtime = { subscriber, connected: false };

const auth: AuthContextValue = {
  session: null,
  user: { id: 0, client_id: "00000000-0000-0000-0000-000000000000", nickname: "Lilo", is_bot: false },
  logout: async () => {},
  deleteAccount: async () => {},
  loading: false,
  entryError: null,
};

const simulation = { simulation: null, simulationActive: true, loading: false, failed: false, retry: () => {} };

const manualStrategy: MyStrategy = { active: null, error: null, resumed: false, open_orders: 0, panel: null };

/** Cache próprio do palco: tudo que a cena lê já vem semeado, e nada é buscado de novo. */
function createStageClient() {
  const client = new QueryClient({
    defaultOptions: { queries: { staleTime: Infinity, retry: false, refetchOnWindowFocus: false } },
  });
  client.setQueryData(queryKeys.myStrategy(), manualStrategy);
  return client;
}

interface TutorialStageProps {
  /** Tamanho de projeto da cena, em px; a cena é escalada para caber na ilustração. */
  width: number;
  height: number;
  children: ReactNode;
}

/**
 * Palco da ilustração: os componentes reais do app, com dados fixos, escalados e sem interação.
 * O roteador é o do app (o portal da janela preserva o contexto): links e linhas clicáveis só não são acionados.
 */
export function TutorialStage({ width, height, children }: TutorialStageProps) {
  const frame = useRef<HTMLDivElement>(null);
  const root = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [client] = useState(createStageClient);

  // A cena acompanha o tamanho da ilustração
  useEffect(() => {
    const element = frame.current;
    if (!element) return;
    const observer = new ResizeObserver(([entry]) => {
      const { width: w, height: h } = entry.contentRect;
      setScale(Math.min(w / width, h / height, 1));
    });
    observer.observe(element);
    return () => observer.disconnect();
  }, [width, height]);

  // A prévia da ordem é a única chamada que chega à rede: o interceptador vale enquanto o palco existe.
  // Ele entra antes dos efeitos dos filhos, que já pedem a prévia ao montar.
  useLayoutEffect(() => {
    const restore = installStageFetch();
    return () => {
      restore();
      // Prévias e ordens do ativo de exemplo não ficam na boleta real que está atrás da janela
      void appQueryClient.invalidateQueries({
        predicate: ({ queryKey }) => queryKey[0] === "variable-income" && ["order-preview", "orders"].includes(String(queryKey[2])),
      });
    };
  }, []);

  // A faixa de baixo fica livre para a barra de reprodução
  return (
    <div ref={frame} className="absolute inset-0 bottom-14 overflow-hidden">
      <div
        ref={root}
        inert
        aria-hidden
        className="absolute top-1/2 left-1/2 select-none"
        style={{ width, height, transform: `translate(-50%, -50%) scale(${scale})` }}
      >
        <QueryClientProvider client={client}>
          <AuthContext.Provider value={auth}>
            <RealtimeContext.Provider value={realtime}>
              <SimulationContext.Provider value={simulation}>
                <StageContext.Provider value={{ root, scale }}>{children}</StageContext.Provider>
              </SimulationContext.Provider>
            </RealtimeContext.Provider>
          </AuthContext.Provider>
        </QueryClientProvider>
      </div>
    </div>
  );
}
