import { Button } from "@/shared/components/ui/button";
import { VALUE_SHARES } from "../lib/treasury";

type ShareShortcutsProps = {
  onPick: (share: number) => void;
  disabled?: boolean;
};

/** Atalhos de valor ao lado do campo: 25%, 50% e o total. */
export function ShareShortcuts({ onPick, disabled }: ShareShortcutsProps) {
  return (
    <>
      {VALUE_SHARES.map(({ label, share }) => (
        <Button key={label} type="button" variant="outline" size="xl" disabled={disabled} onClick={() => onPick(share)}>
          {label}
        </Button>
      ))}
    </>
  );
}
