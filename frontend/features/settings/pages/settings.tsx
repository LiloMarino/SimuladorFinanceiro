import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/shared/hooks/useAuth";
import { simulationSettingsOptions } from "@/shared/lib/queries/simulationSettingsOptions";
import { DangerZoneCard } from "../components/danger-zone-card";
import { MatchCard } from "../components/match-card";
import { NotificationsCard } from "../components/notifications-card";
import { ProfileCard } from "../components/profile-card";

export default function SettingsPage() {
  const { user } = useAuth();
  const { data: settings } = useQuery(simulationSettingsOptions());
  if (!user) return null;

  return (
    <div className="grid items-start gap-5 lg:grid-cols-2">
      <div className="grid gap-5">
        <ProfileCard nickname={user.nickname} />
        {settings?.is_host && <MatchCard />}
      </div>
      <div className="grid gap-5">
        <NotificationsCard />
        <DangerZoneCard nickname={user.nickname} />
      </div>
    </div>
  );
}
