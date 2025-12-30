export type Snapshot = {
  user_id: number;
  snapshot_date: string; // ISO
  total_equity: number;
  total_fixed: number;
  total_cash: number;
  total_networth: number;
  created_at: string; // ISO
};
