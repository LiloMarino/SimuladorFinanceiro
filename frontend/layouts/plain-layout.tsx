import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import { useNavigate } from "react-router-dom";
import { Outlet } from "react-router-dom";
import { Button } from "@/shared/components/ui/button";

export function PlainLayout() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col">
      <header className="px-4 py-3 border-b bg-white flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <FontAwesomeIcon icon={faArrowLeft} className="mr-2" />
          Voltar
        </Button>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
