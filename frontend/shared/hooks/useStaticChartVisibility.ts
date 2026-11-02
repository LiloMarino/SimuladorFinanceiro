import { useState } from "react";

export function useStaticChartVisibility<T extends readonly { key: string; defaultVisible?: boolean }[]>(series: T) {
  type Key = T[number]["key"];

  // Guarda só o que a pessoa alternou: a série que chega depois (como o Ibovespa do backtest) nasce com o padrão dela
  const [overrides, setOverrides] = useState<Partial<Record<string, boolean>>>({});

  const visible = Object.fromEntries(
    series.map((s) => [s.key, overrides[s.key] ?? s.defaultVisible ?? true]),
  ) as Record<Key, boolean>;

  const toggle = (key: Key) => {
    setOverrides((prev) => ({ ...prev, [key]: !visible[key] }));
  };

  return { visible, toggle };
}
