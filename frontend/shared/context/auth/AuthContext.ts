import { createContext } from "react";
import type ApiError from "@/shared/lib/models/ApiError";
import type { Session, User } from "@/types";

export interface AuthContextValue {
  session: Session | null;
  user: User | null;
  logout: () => Promise<void>;
  deleteAccount: () => Promise<void>;
  loading: boolean;
  /** Por que a sala recusou a entrada (cheia, partida em andamento); ausente quando entrou ou ainda não tentou */
  entryError: ApiError | null;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
