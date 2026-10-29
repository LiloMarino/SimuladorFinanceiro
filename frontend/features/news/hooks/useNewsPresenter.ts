import { useContext } from "react";
import { NewsPresenterContext } from "../context/NewsPresenterContext";

export function useNewsPresenter() {
  const ctx = useContext(NewsPresenterContext);
  if (!ctx) {
    throw new Error("useNewsPresenter must be used within NewsPresenterProvider");
  }
  return ctx;
}
