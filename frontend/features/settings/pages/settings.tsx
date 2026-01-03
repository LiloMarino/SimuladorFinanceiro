import { useAuth } from "@/shared/hooks/useAuth";
import { Input } from "@/shared/components/ui/input";
import { NotificationSettingsForm } from "../components/notifications-settings-form";
import { SettingsSection } from "../components/settings-section";

export default function SettingsPage() {
  const { getUser } = useAuth();
  const user = getUser();

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
      </div>
    </section>
  );
}
