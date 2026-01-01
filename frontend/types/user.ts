export type User = {
  id: number;
  client_id: string;
  nickname: string;
};

export type Session = {
  authenticated: boolean;
  user: User | null;
};
