import { ArrowLeft } from "lucide-react";
import { Link, Outlet, matchPath, useLocation } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";

export function PlainLayout() {
  const { pathname } = useLocation();
  // O fim de partida já tem o botão de voltar no topo escuro
  const hasOwnBackButton = matchPath("/match-result/:simulationId", pathname) !== null;

  return (
    <div className="min-h-screen">
      <div className="mx-auto flex w-full max-w-[1320px] flex-col gap-5 px-7 pt-6 pb-10">
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
