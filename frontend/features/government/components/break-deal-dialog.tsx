import type { ReactNode } from "react";
import { Newspaper, TrendingUp, Users, Wallet, type LucideIcon } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { cn } from "@/shared/lib/utils";
import { displayDayMonth } from "@/shared/lib/utils/display";
import type { BaseDeal, CongressBase } from "@/types";
import { useBreakDeal } from "../hooks/mutations/useBreakDeal";
import { useLeaveBase } from "../hooks/mutations/useLeaveBase";
import { daysLeftLabel, groupsLabel, monthlyLabel, yearShare } from "../lib/base";

type BreakDealDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  base: CongressBase;
  deal: BaseDeal;
  /** Quem rompe: o presidente corta a emenda; o líder aliado sai da base */
  side: "government" | "ally";
};

type Line = { icon: LucideIcon; bad: boolean; text: ReactNode };

/** Romper é sempre à vista: o diálogo mostra a base que sobra e a rejeição antes do clique. */
export function BreakDealDialog({ open, onOpenChange, base, deal, side }: BreakDealDialogProps) {
  const breakDeal = useBreakDeal();
  const leave = useLeaveBase();
  const pending = breakDeal.isPending || leave.isPending;
  const government = side === "government";
  const governingAbbr = base.governing_abbr ?? "governo";
  const losesMajority = deal.base_after < base.majority && base.seats >= base.majority;
  const done = { onSuccess: () => onOpenChange(false) };

  const newspaper: Line = { icon: Newspaper, bad: false, text: "O rompimento sai no jornal, para a sala inteira." };
  const lines: Line[] = government
    ? [
        {
          icon: Users,
          bad: losesMajority,
          text: (
            <>
              A base cai de <b className="font-mono">{base.seats}</b> para{" "}
              <b className={cn("font-mono", losesMajority && "text-destructive")}>{deal.base_after}</b> cadeiras
              {losesMajority && <b className="text-destructive">: perde a maioria</b>}.
            </>
          ),
        },
        {
          icon: Wallet,
          bad: false,
          text: `A emenda de ${monthlyLabel(deal.monthly)} por mês para hoje; o gasto cai ${yearShare(deal.ratio)} do PIB por ano.`,
        },
        {
          icon: TrendingUp,
          bad: true,
          text: (
            <>
              {groupsLabel(deal.ally_groups)}, que recebiam a emenda, somam <b className="text-destructive">+8</b> de
              rejeição ao {governingAbbr}. Ela só cai com reparação.
            </>
          ),
        },
        newspaper,
      ]
    : [
        {
          icon: Wallet,
          bad: false,
          text: `A emenda de ${monthlyLabel(deal.monthly)} por mês às suas bases para hoje.`,
        },
        {
          icon: TrendingUp,
          bad: true,
          text: (
            <>
              {groupsLabel(deal.government_groups)}, os grupos do governo, somam <b className="text-destructive">+8</b>{" "}
              de rejeição ao {deal.abbr}.
            </>
          ),
        },
        { icon: Users, bad: false, text: `O ${deal.abbr} volta a orientar como quiser.` },
        newspaper,
      ];

  const left = deal.days_left !== null ? daysLeftLabel(deal.days_left) : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-110">
        <DialogHeader variant="divided">
          <DialogTitle>{government ? `Romper o acordo com o ${deal.abbr}?` : "Sair da base do governo?"}</DialogTitle>
          <DialogDescription>
            {government
              ? `${left ? `${left.charAt(0).toUpperCase()}${left.slice(1)} de prazo. ` : ""}O que acontece ao romper:`
              : `O ${deal.abbr} está na base${deal.end ? ` até ${displayDayMonth(deal.end)}` : ""}. O que acontece ao sair:`}
          </DialogDescription>
        </DialogHeader>

        <DialogBody>
          <ul className="grid text-[13px]">
            {lines.map((line, index) => (
              <li key={index} className="flex items-start gap-2.5 py-2">
                <line.icon className={cn("mt-0.5 size-4 shrink-0", line.bad && "text-destructive")} />
                <span>{line.text}</span>
              </li>
            ))}
          </ul>
        </DialogBody>

        <DialogFooter variant="divided" className="sm:justify-end">
          <Button variant="outline" disabled={pending} onClick={() => onOpenChange(false)}>
            {government ? "Manter o acordo" : "Ficar na base"}
          </Button>
          <Button
            variant="destructive"
            disabled={pending}
            onClick={() => (government ? breakDeal.mutate(deal.id, done) : leave.mutate(undefined, done))}
          >
            {government ? "Romper acordo" : "Sair da base"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
