import { CircleDollarSign, TrendingUp, Trophy, type LucideIcon } from "lucide-react";
import { BrandMark } from "@/shared/components/brand-mark";

const FEATURES: { icon: LucideIcon; text: string }[] = [
  { icon: TrendingUp, text: "Preços históricos da bolsa, pregão a pregão" },
  { icon: CircleDollarSign, text: "Renda fixa atrelada a CDI, SELIC e IPCA" },
  { icon: Trophy, text: "Ranking com nota de risco e retorno" },
];

/** Painel da esquerda do login: o que é o FinSim. */
export function LoginShowcase() {
  return (
    <aside className="hidden w-[560px] shrink-0 flex-col justify-between bg-sidebar p-12 text-sidebar-foreground lg:flex">
      {/* Marca */}
      <div className="flex items-center gap-3">
        <BrandMark />
        <span className="text-xl font-bold text-sidebar-accent-foreground">FinSim</span>
      </div>

      {/* Proposta */}
      <div className="grid gap-7">
        <h2 className="text-[34px] leading-tight font-bold text-sidebar-accent-foreground">
          Invista com dados reais da bolsa, numa sala com seus amigos.
        </h2>
        <ul className="grid gap-3.5 text-[15px]">
          {FEATURES.map(({ icon: Icon, text }) => (
            <li key={text} className="flex items-center gap-3">
              <span className="flex size-8 items-center justify-center rounded-lg bg-sidebar-border text-sidebar-primary">
                <Icon className="size-4" />
              </span>
              {text}
            </li>
          ))}
        </ul>
      </div>

      {/* Rodapé */}
      <div>
        <svg viewBox="0 0 460 120" className="h-[120px] w-full" aria-hidden="true">
          <defs>
            <linearGradient id="login-spark" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="var(--primary)" stopOpacity=".5" />
              <stop offset="1" stopColor="var(--primary)" stopOpacity="0" />
            </linearGradient>
          </defs>
          <path
            d="M0 96 L30 90 L60 98 L90 80 L120 84 L150 70 L180 76 L210 58 L240 64 L270 46 L300 52 L330 36 L360 42 L390 26 L420 30 L460 14 L460 120 L0 120Z"
            fill="url(#login-spark)"
          />
          <path
            d="M0 96 L30 90 L60 98 L90 80 L120 84 L150 70 L180 76 L210 58 L240 64 L270 46 L300 52 L330 36 L360 42 L390 26 L420 30 L460 14"
            fill="none"
            stroke="var(--sidebar-primary)"
            strokeWidth="2"
          />
        </svg>
        <p className="mt-2 font-mono text-xs text-sidebar-muted">
          Simulação local · o servidor roda no computador do host
        </p>
      </div>
    </aside>
  );
}
