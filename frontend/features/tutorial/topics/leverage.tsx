import { motion, useReducedMotion } from "motion/react";
import { cn } from "@/shared/lib/utils";
import { displayMoneyWhole } from "@/shared/lib/utils/display";
import type { IllustrationProps } from "../lib/topics";

// Exemplo: R$ 10.000 do jogador e R$ 10.000 emprestados, tudo investido numa ação que cai 10%
const OWN = 10_000;
const BORROWED = 10_000;
const DROP = 0.1;

const invested = OWN + BORROWED;
const loss = invested * DROP;
const lossOfOwn = loss / OWN;

const percent = new Intl.NumberFormat("pt-BR", { style: "percent", maximumFractionDigits: 0 });

/** Bar cresce da esquerda até a fração do investido que ela representa. */
function Bar({ label, value, tone }: { label: string; value: number; tone: "primary" | "muted" }) {
  const reduced = useReducedMotion();
  return (
    <div className="grid grid-cols-[120px_1fr_110px] items-center gap-2.5 text-[13px]">
      <span className="text-muted-foreground">{label}</span>
      <motion.span
        className={cn("h-[22px] rounded-[5px]", tone === "primary" ? "bg-primary" : "bg-muted-foreground/30")}
        initial={{ width: reduced ? `${(value / invested) * 100}%` : 0 }}
        animate={{ width: `${(value / invested) * 100}%` }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      />
      <span className="text-right font-mono">{displayMoneyWhole(value)}</span>
    </div>
  );
}

/** Alavancagem 2×: R$ 1 seu e R$ 1 do banco; uma queda de 10% na ação tira 20% do seu dinheiro. */
export default function LeverageIllustration({ still = false }: IllustrationProps) {
  void still;
  return (
    <div className="absolute inset-0 grid content-center gap-3 p-5.5">
      <Bar label="Seu dinheiro" value={OWN} tone="primary" />
      <Bar label="Emprestado" value={BORROWED} tone="muted" />
      <Bar label="Investido" value={invested} tone="primary" />
      <div className="grid gap-1.5 border-t border-dashed border-input pt-3 text-[13px]">
        <div className="flex justify-between">
          <span>Ação cai {percent.format(DROP)}</span>
          <span className="font-mono text-destructive">−{displayMoneyWhole(loss)}</span>
        </div>
        <div className="flex justify-between">
          <b>Do seu dinheiro</b>
          <b className="font-mono text-destructive">−{percent.format(lossOfOwn)}</b>
        </div>
      </div>
    </div>
  );
}
