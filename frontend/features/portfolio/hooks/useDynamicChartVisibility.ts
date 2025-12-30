import { useState } from "react";

export function useDynamicChartVisibility<T extends { name: string }>(data: T[]) {
  const [hidden, setHidden] = useState<Set<string>>(new Set());

  const visibleData = data.filter((item) => !hidden.has(item.name));

  const toggle = (name: string) => {
    setHidden((prev) => {
      const next = new Set(prev);

      if (next.has(name)) {
        next.delete(name);
      } else if (next.size < data.length - 1) {
        next.add(name);
      }

      return next;
    });
  };

  return {
    hidden,
    visibleData,
    toggle,
  };
}
