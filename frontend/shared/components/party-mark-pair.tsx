import { PartyMark } from "@/shared/components/party-mark";
import type { ElectionParty } from "@/types";

type PartyMarkPairProps = {
  parties: Pick<ElectionParty, "abbr" | "color">[];
  size?: "sm" | "md" | "lg";
};

/** As siglas de uma federação lado a lado, a segunda encostada na primeira com um filete da cor do fundo. */
export function PartyMarkPair({ parties, size = "md" }: PartyMarkPairProps) {
  return (
    <span className="inline-flex items-center">
      {parties.map((party, index) => (
        <span
          key={party.abbr}
          className={index === 0 ? "inline-flex" : "-ml-1 inline-flex rounded-[5px] shadow-[0_0_0_2px_var(--card)]"}
        >
          <PartyMark abbr={party.abbr} color={party.color} size={size} />
        </span>
      ))}
    </span>
  );
}
