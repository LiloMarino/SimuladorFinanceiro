import { Button } from "@/shared/components/ui/button";
import { Card, CardContent } from "@/shared/components/ui/card";
import { PlayerAvatar } from "@/shared/components/player-avatar";
import { displayDayMonth, displayMoney } from "@/shared/lib/utils/display";
import type { CampaignPanel, ElectionParty } from "@/types";
import { signed } from "../lib/campaign";

type CampaignBaseCardProps = {
  campaign: CampaignPanel;
  party: ElectionParty;
  nickname: string;
  onChangeContribution: () => void;
};

/** A verba de base: a contribuição de cada filiado, cobrada todo dia 1º, e o apoio da última cobrança. */
export function CampaignBaseCard({ campaign, party, nickname, onChangeContribution }: CampaignBaseCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="grid gap-3">
          <div className="flex items-start justify-between gap-3">
            <div className="grid gap-1">
              <h2 className="text-[15px] font-semibold">Verba de base</h2>
              <span className="text-[13px] text-muted-foreground">
                A contribuição dos filiados, cobrada todo dia 1º
              </span>
            </div>
            <Button variant="link" size="sm" onClick={onChangeContribution}>
              Mudar a minha ›
            </Button>
          </div>

          <div className="grid gap-2.5">
            {party.members.map((member) => (
              <div key={member.nickname} className="flex items-center justify-between gap-3 text-[13px]">
                <span className="flex min-w-0 items-center gap-2">
                  <PlayerAvatar nickname={member.nickname} color={member.color} size="sm" />
                  <span className="truncate">
                    {member.nickname}
                    {member.nickname === nickname && " (você)"}
                  </span>
                </span>
                <span className="font-mono">{displayMoney(member.contribution)}/mês</span>
              </div>
            ))}
          </div>

          <div className="flex items-baseline justify-between gap-3 border-t pt-2.5">
            {campaign.last_charge_date && campaign.last_charge_amount && campaign.last_charge_points ? (
              <>
                <span className="text-xs font-medium text-muted-foreground">
                  Em {displayDayMonth(campaign.last_charge_date)}, {displayMoney(campaign.last_charge_amount)} viraram
                </span>
                <span className="font-mono text-[13px] font-semibold text-success">
                  {signed(campaign.last_charge_points, 1)} em cada grupo
                </span>
              </>
            ) : (
              <span className="text-xs text-muted-foreground">A primeira cobrança sai no próximo dia 1º.</span>
            )}
          </div>

          <p className="rounded-lg bg-subtle px-2.5 py-2 text-xs leading-relaxed text-muted-foreground">
            A verba rende pela raiz: o dobro rende 1,4 vez, e não 2. Para gastar mais com bom retorno, as ações avulsas
            espalham o dinheiro entre os grupos.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
