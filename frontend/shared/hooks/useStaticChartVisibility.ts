import { useState } from "react";

export function useStaticChartVisibility<T extends readonly { key: string; defaultVisible?: boolean }[]>(series: T) {
  type Key = T[number]["key"];

  const [visible, setVisible] = useState<Record<Key, boolean>>(
    () => Object.fromEntries(series.map((s) => [s.key, s.defaultVisible ?? true])) as Record<Key, boolean>
  );

  const toggle = (key: Key) => {
    setVisible((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return { visible, toggle };
}
