import { useAuth } from "@/shared/hooks/useAuth";
import type { User } from "@/types";
import { useEffect, useState } from "react";

export default function SettingsPage() {
  const { getUser } = useAuth();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const user = await getUser();
      setUser(user);
    };
    fetchUser();
  }, [getUser]);

  return (
    <section id="settings" className="section-content p-4">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Configurações</h2>
        <p className="text-gray-600">Ajuste as configurações do simulador conforme suas preferências.</p>
        <p>
          <strong>Nome:</strong> {user?.nickname}
        </p>
        {/* Aqui você pode adicionar os componentes de configuração */}
      </div>
    </section>
  );
}
