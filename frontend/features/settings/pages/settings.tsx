import { useAuth } from "@/shared/hooks/useAuth";
import { Input } from "@/shared/components/ui/input";
import { Button } from "@/shared/components/ui/button";
import { NotificationSettingsForm } from "../components/notifications-settings-form";
import { SettingsSection } from "../components/settings-section";
import { useMutationApi } from "@/shared/hooks/useMutationApi";
import { toast } from "sonner";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSimulation } from "@/shared/hooks/useSimulation";
import { useQueryApi } from "@/shared/hooks/useQueryApi";
import type { SimulationSettings } from "@/types";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const { simulationActive } = useSimulation();
  const navigate = useNavigate();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showStopConfirm, setShowStopConfirm] = useState(false);

  // Verificar se o usuário é host
  const { data: settings } = useQueryApi<SimulationSettings>("/api/simulation/settings", {
    initialFetch: true,
  });

  const isHost = settings?.is_host ?? false;

  // Mutação para deletar conta
  const { mutate: deleteAccount, loading: deletingAccount } = useMutationApi("/api/user", {
    method: "DELETE",
    onSuccess: () => {
      toast.success("Conta excluída com sucesso!");
      handleLogout();
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  // Mutação para encerrar simulação
  const { mutate: stopSimulation, loading: stoppingSimulation } = useMutationApi("/api/simulation/stop", {
    method: "POST",
    onSuccess: () => {
      toast.success("Simulação encerrada com sucesso!");
      setShowStopConfirm(false);
    },
    onError: (err) => {
      toast.error(err.message);
    },
  });

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  const handleDeleteAccount = () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }
    deleteAccount({});
  };

  const handleStopSimulation = () => {
    if (!showStopConfirm) {
      setShowStopConfirm(true);
      return;
    }
    stopSimulation({});
  };

  return (
    <section className="section-content p-4">
      <div className="bg-white rounded-lg shadow p-6 space-y-8">
        {/* Header principal */}
        <header className="space-y-1">
          <h1 className="text-2xl font-semibold">Configurações</h1>
          <p className="text-gray-600">Ajuste as configurações do simulador conforme suas preferências.</p>
        </header>

        <SettingsSection title="Dados do usuário">
          <div className="max-w-sm space-y-2">
            <label className="text-sm font-medium text-gray-700">Nome</label>
            <Input value={user?.nickname ?? ""} disabled readOnly className="bg-gray-50 text-gray-900 opacity-100" />
          </div>
        </SettingsSection>

        <SettingsSection title="Notificações" bordered>
          <NotificationSettingsForm />
        </SettingsSection>

        <SettingsSection title="Conta" bordered>
          <div className="max-w-sm space-y-4">
            <div>
              <Button onClick={handleLogout} variant="outline" className="w-full">
                Sair da Conta
              </Button>
              <p className="text-xs text-gray-500 mt-2">Você será desconectado do simulador.</p>
            </div>

            <div>
              <Button
                onClick={handleDeleteAccount}
                variant={showDeleteConfirm ? "destructive" : "outline"}
                className="w-full"
                disabled={deletingAccount}
              >
                {showDeleteConfirm ? "Confirmar Exclusão" : "Excluir Conta"}
              </Button>
              {showDeleteConfirm && (
                <div className="mt-2 space-y-2">
                  <p className="text-xs text-red-600 font-semibold">
                    ⚠️ Esta ação é irreversível! Todos os seus dados serão perdidos.
                  </p>
                  <Button onClick={() => setShowDeleteConfirm(false)} variant="ghost" size="sm" className="w-full">
                    Cancelar
                  </Button>
                </div>
              )}
              {!showDeleteConfirm && (
                <p className="text-xs text-gray-500 mt-2">Esta ação é permanente e não pode ser desfeita.</p>
              )}
            </div>
          </div>
        </SettingsSection>

        {simulationActive && isHost && (
          <SettingsSection title="Controle da Simulação" bordered>
            <div className="max-w-sm space-y-4">
              <div>
                <Button
                  onClick={handleStopSimulation}
                  variant={showStopConfirm ? "destructive" : "outline"}
                  className="w-full"
                  disabled={stoppingSimulation}
                >
                  {showStopConfirm ? "Confirmar Encerramento" : "Encerrar Simulação"}
                </Button>
                {showStopConfirm && (
                  <div className="mt-2 space-y-2">
                    <p className="text-xs text-orange-600 font-semibold">
                      ⚠️ Todos os jogadores serão redirecionados para o lobby.
                    </p>
                    <Button onClick={() => setShowStopConfirm(false)} variant="ghost" size="sm" className="w-full">
                      Cancelar
                    </Button>
                  </div>
                )}
                {!showStopConfirm && (
                  <p className="text-xs text-gray-500 mt-2">
                    Encerra a simulação atual e retorna todos os jogadores ao lobby.
                  </p>
                )}
              </div>
            </div>
          </SettingsSection>
        )}
      </div>
    </section>
  );
}
