import { ArrowLeft } from "lucide-react";
import { Link, Outlet, matchPath, useLocation } from "react-router-dom";
import { PlainTopbar } from "@/layouts/partial/plain-topbar";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";

export function PlainLayout() {
  const { pathname } = useLocation();
  // Conquistas abre com a barra do topo (volta, sala e jogador); o fim de partida já tem o botão de voltar no topo escuro
  const hasTopbar = matchPath("/achievements", pathname) !== null;
  const hasOwnBackButton =
    hasTopbar ||
    matchPath("/match-result/:simulationId", pathname) !== null ||
    matchPath("/backtest/running", pathname) !== null;

  return (
    <div className="min-h-screen">
      {hasTopbar && <PlainTopbar />}
      <div
        className={cn(
          "mx-auto flex w-full flex-col gap-5 px-7 pt-6 pb-10",
          hasTopbar ? "max-w-[1120px]" : "max-w-[1320px]",
        )}
      >
        {!hasOwnBackButton && (
          <Button variant="link" size="sm" nativeButton={false} render={<Link to="/lobby" />} className="self-start">
            <ArrowLeft />
            Voltar ao lobby
          </Button>
        )}
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
