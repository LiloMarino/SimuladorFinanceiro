import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { cn } from "@/shared/lib/utils";
import type { CampaignBand, DiceBand } from "@/types";
import { BAND_INFO, bandEffect, bandRange, chancePercent } from "../lib/campaign";

type D20Props = {
  value: number | "?";
  /** Sem faixa, o dado ainda não foi rolado */
  band: DiceBand | null;
  /** Largura e altura em pixels */
  size: number;
  /** O dado descartado da TV, que vale o maior dos dois */
  dim?: boolean;
  className?: string;
};

/** O dado de 20 lados: um hexágono na cor da faixa, com o número rolado dentro. */
export function D20({ value, band, size, dim = false, className }: D20Props) {
  const style = band ? BAND_INFO[band] : null;
  return (
    <span
      className={cn(
        "relative inline-flex shrink-0 items-center justify-center",
        style?.text ?? "text-faint-foreground",
        dim && "opacity-40",
        className,
      )}
      style={{ width: size, height: size }}
    >
      <svg aria-hidden viewBox="0 0 100 100" className="absolute inset-0 size-full">
        <polygon
          points="50,4 90,27 90,73 50,96 10,73 10,27"
          strokeWidth={4}
          strokeLinejoin="round"
          className={cn(style?.fill ?? "fill-muted", style?.stroke ?? "stroke-faint-foreground")}
        />
        <polygon
          points="50,24 77,68 23,68"
          strokeWidth={2}
          strokeLinejoin="round"
          className="fill-none stroke-current opacity-30"
        />
      </svg>
      <b className="relative mt-[10%] font-mono font-semibold tabular-nums" style={{ fontSize: size * 0.35 }}>
        {value}
      </b>
    </span>
  );
}

type BandsTableProps = {
  bands: CampaignBand[];
  /** O número rolado: a faixa dele ganha destaque */
  roll?: number | undefined;
  className?: string;
};

/** As cinco faixas do d20 com o efeito e a chance de cada uma. */
export function BandsTable({ bands, roll, className }: BandsTableProps) {
  return (
    <table className={cn("w-full border-collapse text-[12.5px]", className)}>
      <tbody>
        {bands.map((band) => {
          const style = BAND_INFO[band.band];
          const hit = roll !== undefined && roll >= band.first_roll && roll <= band.last_roll;
          return (
            <tr
              key={band.band}
              className={cn("border-t first:border-t-0", style.text, hit && cn(style.soft, "font-semibold"))}
            >
              <td className={cn("px-2 py-1.5 font-mono whitespace-nowrap", !hit && "text-muted-foreground")}>
                {bandRange(band)}
              </td>
              <td className="px-2 py-1.5 font-semibold whitespace-nowrap">
                <Tooltip>
                  <TooltipTrigger render={<span className="cursor-help" />} aria-label={style.label}>
                    <span aria-hidden className="mr-1.5 inline-block size-2.5 rounded-[3px] bg-current" />
                    {style.label}
                  </TooltipTrigger>
                  <TooltipContent side="top" className="max-w-70">
                    {style.label} · sai no {bandRange(band)} · chance de {chancePercent(band.chance)}. Rende{" "}
                    {bandEffect(band)}.
                  </TooltipContent>
                </Tooltip>
              </td>
              <td className="px-2 py-1.5 text-right font-mono whitespace-nowrap tabular-nums">{bandEffect(band)}</td>
              <td className="px-2 py-1.5 text-right font-mono whitespace-nowrap text-muted-foreground tabular-nums">
                {chancePercent(band.chance)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
