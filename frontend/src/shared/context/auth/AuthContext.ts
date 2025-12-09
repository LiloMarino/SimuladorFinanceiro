import { createContext } from "react";

export interface User {
  id: number;
  nickname: string;
}

export interface AuthContextValue {
  user: User | null;
  clientId: string | null;
  loading: boolean;
  registerNickname: (nickname: string) => Promise<void>;
  claimNickname: (nickname: string) => Promise<void>;
  refresh: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
