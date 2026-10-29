import { useAuth } from "@/shared/hooks/useAuth";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";
import { AppFoldersCard } from "../components/app-folders-card";
import { DangerZoneCard } from "../components/danger-zone-card";
import { JournalSettingsCard } from "../components/journal-settings-card";
import { MatchCard } from "../components/match-card";
import { NewsPositionCard } from "../components/news-position-card";
import { NotificationsCard } from "../components/notifications-card";
import { ProfileCard } from "../components/profile-card";
import { TutorialStyleCard } from "../components/tutorial-style-card";

export default function SettingsPage() {
  const { user } = useAuth();
  const { data: settings } = useSimulationSettings();
  if (!user) return null;

  return (
    <div className="grid items-start gap-5 grid-cols-2">
      <div className="grid gap-5">
        <JournalSettingsCard />
        {settings?.is_host && <MatchCard />}
        {settings?.is_host && <AppFoldersCard />}
      </div>
      <div className="grid gap-5">
        <ProfileCard nickname={user.nickname} />
        <NewsPositionCard />
        <NotificationsCard />
        <DangerZoneCard nickname={user.nickname} />
      </div>
      <TutorialStyleCard />
    </div>
  );
}
