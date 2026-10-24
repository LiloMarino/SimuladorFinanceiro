import type { BacktestFailure, BacktestPoint, BacktestStatus } from "@/types";

type ProgressEvent = {
  progress: NonNullable<BacktestStatus["progress"]>;
  points: BacktestPoint[];
  failures: BacktestFailure[];
};

export const EMPTY_STATUS: BacktestStatus = { progress: null, participants: [], points: [], failures: [] };

/** Soma ao andamento guardado o que o aviso trouxe de novo; ponto de um dia já guardado não entra duas vezes. */
export function applyProgress(current: BacktestStatus, event: ProgressEvent): BacktestStatus {
  const lastDay = current.points.at(-1)?.day ?? "";
  return {
    ...current,
    progress: event.progress,
    points: [...current.points, ...event.points.filter((point) => point.day > lastDay)],
    failures: [...current.failures, ...event.failures],
  };
}
