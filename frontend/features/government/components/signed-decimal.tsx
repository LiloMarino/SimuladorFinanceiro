import { cn } from "@/shared/lib/utils";
import { signedDecimal } from "../lib/promises";

type SignedDecimalProps = {
  value: string | number;
  /** O que subir significa: apoio bom, rejeição ruim */
  rising: "good" | "bad";
  className?: string;
};

/** Número com sinal na cor do que ele faz ao partido; zero vira traço. */
export function SignedDecimal({ value, rising, className }: SignedDecimalProps) {
  const number = Number(value);
  const good = rising === "good" ? number > 0 : number < 0;
  return (
    <span
      className={cn(
        "font-mono",
        number !== 0 && (good ? "text-success" : "text-destructive"),
        number === 0 && "text-faint-foreground",
        className,
      )}
    >
      {number === 0 ? "—" : signedDecimal(number)}
    </span>
  );
}
