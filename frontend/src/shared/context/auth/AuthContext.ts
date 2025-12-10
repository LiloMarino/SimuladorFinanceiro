import { createContext } from "react";
import type { User } from "@/types/user";

export interface AuthContextValue {
  user: User | null;
  clientId: string | null;
  loading: boolean;
  refresh: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
