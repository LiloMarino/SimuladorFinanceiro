import { ChevronDown } from "lucide-react";
import { AssetOriginFlag } from "@/shared/components/asset-origin-flag";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { ASSET_ORIGIN_LABELS, ASSET_ORIGINS } from "@/shared/lib/asset-origin";
import type { AssetClass, AssetOrigin } from "@/types";
import { useChangeAssetClass } from "../hooks/mutations/useChangeAssetClass";
import { useChangeAssetOrigin } from "../hooks/mutations/useChangeAssetOrigin";

// A classe no singular, como o selo do ativo a chama; classe nova sem rótulo não compila
const ASSET_CLASS_LABELS: Record<AssetClass, string> = {
  STOCK: "Ação",
  FII: "FII",
  ETF: "ETF",
  BDR: "BDR",
  CRYPTO: "Cripto",
};

/** A classe do ativo: o selo abre o menu e a troca vale na hora. */
export function AssetClassBadge({ ticker, value }: { ticker: string; value: AssetClass }) {
  const change = useChangeAssetClass();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        variant="badge"
        render={
          <button
            type="button"
            disabled={change.isPending}
            aria-label={`Classe de ${ticker}: ${ASSET_CLASS_LABELS[value]}. Trocar`}
          />
        }
      >
        {ASSET_CLASS_LABELS[value]}
        <ChevronDown />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="min-w-32">
        {Object.entries(ASSET_CLASS_LABELS).map(([option, label]) => (
          <DropdownMenuItem
            key={option}
            variant={option === value ? "selected" : "default"}
            onClick={() => option !== value && change.mutate({ ticker, value: option as AssetClass })}
          >
            {label}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/** A origem do ativo: o selo abre o menu e a troca vale na hora. */
export function AssetOriginBadge({ ticker, value }: { ticker: string; value: AssetOrigin }) {
  const change = useChangeAssetOrigin();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        variant="badge"
        render={
          <button
            type="button"
            disabled={change.isPending}
            aria-label={`Origem de ${ticker}: ${ASSET_ORIGIN_LABELS[value]}. Trocar`}
          />
        }
      >
        <AssetOriginFlag origin={value} size={14} />
        {ASSET_ORIGIN_LABELS[value]}
        <ChevronDown />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="min-w-40">
        {ASSET_ORIGINS.map((option) => (
          <DropdownMenuItem
            key={option}
            variant={option === value ? "selected" : "default"}
            onClick={() => option !== value && change.mutate({ ticker, value: option })}
          >
            <AssetOriginFlag origin={option} size={14} />
            {ASSET_ORIGIN_LABELS[option]}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
