import { ArrowLeft } from "lucide-react";
import { Link, Outlet } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";

export function PlainLayout() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto flex w-full max-w-[1320px] flex-col gap-5 px-7 pt-6 pb-10">
        <Button variant="link" size="sm" nativeButton={false} render={<Link to="/lobby" />} className="self-start">
          <ArrowLeft />
          Voltar ao lobby
        </Button>
        <main>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
