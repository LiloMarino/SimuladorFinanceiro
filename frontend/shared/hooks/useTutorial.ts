import { useContext } from "react";
import { TutorialContext } from "../context/tutorial";

export function useTutorial() {
  const ctx = useContext(TutorialContext);
  if (!ctx) throw new Error("useTutorial must be used within TutorialProvider");
  return ctx;
}
