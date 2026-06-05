import type { components } from "@/types/openapi";

export type NotificationPreferences = {
  orders: components["schemas"]["OrderNotificationSettings"];
};
