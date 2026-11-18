import { Link } from "react-router-dom";
import { FundSection } from "@/shared/components/fund-section";
import { Button } from "@/shared/components/ui/button";
import { managerShareOf } from "@/shared/lib/fund-view";
import { displayPercent } from "@/shared/lib/utils/display";
import type { FundDetails } from "@/types";

/** Quem gere a cota e o caminho para a página da gestora. */
export function FundAboutCard({ fund }: { fund: FundDetails }) {
  return (
    <FundSection
      title="Sobre a gestora"
      action={
        <Button size="xs" variant="outline" nativeButton={false} render={<Link to={`/funds/${fund.id}`} />}>
          Ver a gestora
        </Button>
      }
    >
      <p className="text-[13px] text-muted-foreground">
        {fund.name} é gerida por <b className="font-semibold text-foreground">{fund.manager_nickname ?? "—"}</b>, que
        controla {displayPercent(managerShareOf(fund), 1)} das cotas.
      </p>
    </FundSection>
  );
}
