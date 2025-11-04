import { useLocation } from "react-router-dom";

export default function useActivePage(): string {
  const location = useLocation();
  // Retira a barra inicial e pega a primeira parte da URL
  return location.pathname.replace("/", "") || "portfolio";
}
