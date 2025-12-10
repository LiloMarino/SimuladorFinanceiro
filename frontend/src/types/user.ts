export type Player = {
  name: string;
  status: string;
  color: string;
  isYou?: boolean;
};

export type User = {
  id: number;
  client_id: string;
  nickname: string | null;
};

export type Session = {
  authenticated: boolean;
  user: User | null;
};
