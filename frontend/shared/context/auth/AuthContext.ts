import { createContext } from "react";
import type { Session, User } from "@/types/user";

export interface AuthContextValue {
  getSession: () => Session | null;
  getUser: () => User | null;
  refresh: () => Promise<Session>;
  logout: () => Promise<void>;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
