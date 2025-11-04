import { useContext, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { PageLabelContext } from "@/context/page-label";

export default function usePageLabel(customLabel?: string) {
  const context = useContext(PageLabelContext);
  if (!context) throw new Error("usePageLabel deve ser usado dentro de PageLabelProvider");

  const { label, setLabel, routeLabels } = context;
  const location = useLocation();

  useEffect(() => {
    if (customLabel) {
      setLabel(customLabel);
    } else if (routeLabels) {
      const path = location.pathname;
      const mappedLabel = routeLabels[path];
      if (mappedLabel) {
        setLabel(mappedLabel);
      }
    }
  }, [customLabel, routeLabels, setLabel, location.pathname]);

  return { label };
}
