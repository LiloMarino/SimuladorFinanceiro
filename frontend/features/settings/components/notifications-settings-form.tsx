import { Checkbox } from "@/shared/components/ui/checkbox";
import { useNotificationSettings } from "@/shared/hooks/useNotificationSettings";
import type { NotificationPreferences } from "@/types";

type NotificationLabels = {
  [Section in keyof NotificationPreferences]: {
    label: string;
    items: {
      [Item in keyof NotificationPreferences[Section]]: string;
    };
  };
};

const notificationLabels: NotificationLabels = {
  orders: {
    label: "Ordens",
    items: {
      executed: "Ordem executada",
      partial: "Execução parcial",
    },
  },
} as const;

export function NotificationSettingsForm() {
  const { preferences, updatePreferences } = useNotificationSettings();

  return (
    <div className="space-y-6">
      {(Object.keys(preferences) as Array<keyof typeof preferences>).map((sectionKey) => {
        const section = preferences[sectionKey];
        const sectionLabel = notificationLabels[sectionKey];

        return (
          <section key={sectionKey} className="space-y-3">
            {/* Sub-seção */}
            <h3 className="text-base font-semibold text-gray-800">{sectionLabel.label}</h3>

            <div className="space-y-3 pl-1">
              {(Object.keys(section) as Array<keyof typeof section>).map((itemKey) => (
                <label key={itemKey} className="flex items-center gap-3">
                  <Checkbox
                    checked={section[itemKey]}
                    onCheckedChange={(checked) =>
                      updatePreferences({
                        ...preferences,
                        [sectionKey]: {
                          ...section,
                          [itemKey]: Boolean(checked),
                        },
                      })
                    }
                  />
                  <span className="text-sm text-gray-700">{sectionLabel.items[itemKey]}</span>
                </label>
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}
