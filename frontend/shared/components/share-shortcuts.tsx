import { Button } from "@/shared/components/ui/button";

const SHARES = [0.25, 0.5, 1] as const;

type ShareShortcutsProps = {
  /** Recebe a fração do total: 0,25, 0,5 ou 1 */
  onPick: (share: number) => void;
  /** Rótulo do botão que pega o total: "Tudo" ou "Máx" */
  maxLabel?: string;
  disabled?: boolean;
};

/** Atalhos de valor ao lado do campo: 25%, 50% e o total. */
export function ShareShortcuts({ onPick, maxLabel = "Tudo", disabled }: ShareShortcutsProps) {
  return (
    <>
      {SHARES.map((share) => (
        <Button key={share} type="button" variant="outline" size="xl" disabled={disabled} onClick={() => onPick(share)}>
          {share === 1 ? maxLabel : `${share * 100}%`}
        </Button>
      ))}
    </>
  );
}
