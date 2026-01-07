import { createContext } from "react";
import type { Session, User } from "@/types/user";

export interface AuthContextValue {
  session: Session | null;
  user: User | null;
  refresh: () => Promise<Session | null>;
  logout: () => Promise<void>;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
