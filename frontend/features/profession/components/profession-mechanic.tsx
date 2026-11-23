import type { ProfessionMechanic as Mechanic } from "@/types";
import { BankerBlock } from "./banker-block";
import { BrokerBlock } from "./broker-block";
import { CltBlock } from "./clt-block";
import { EntrepreneurBlock } from "./entrepreneur-block";
import { ExporterBlock } from "./exporter-block";
import { FreelancerBlock } from "./freelancer-block";
import { AppointeeBlock, HeirBlock, OffersBankerBlock } from "./other-blocks";
import { PublicServantBlock } from "./public-servant-block";
import { RetireeBlock } from "./retiree-block";
import { WelfareBlock } from "./welfare-block";

/** O bloco da mecânica que a profissão tem; sem mecânica, nada a mostrar. */
export function ProfessionMechanic({ mechanic }: { mechanic: Mechanic }) {
  switch (mechanic.kind) {
    case "clt":
      return <CltBlock mechanic={mechanic} />;
    case "entrepreneur":
      return <EntrepreneurBlock mechanic={mechanic} />;
    case "retiree":
      return <RetireeBlock mechanic={mechanic} />;
    case "exporter":
      return <ExporterBlock mechanic={mechanic} />;
    case "freelancer":
      return <FreelancerBlock mechanic={mechanic} />;
    case "public_servant":
      return <PublicServantBlock mechanic={mechanic} />;
    case "welfare":
      return <WelfareBlock mechanic={mechanic} />;
    case "banker":
      return <BankerBlock mechanic={mechanic} />;
    case "broker":
      return <BrokerBlock mechanic={mechanic} />;
    case "heir":
      return <HeirBlock mechanic={mechanic} />;
    case "appointee":
      return <AppointeeBlock mechanic={mechanic} />;
    case "offers_banker":
      return <OffersBankerBlock mechanic={mechanic} />;
    case "none":
      return null;
  }
}
