import { Swatch } from "../indicator-selector";

type PopRowProps = { token: string; name: string; value: string };

export function PopRow({ token, name, value }: PopRowProps) {
  return (
    <div className="flex justify-between gap-2">
      <span className="flex items-center gap-1.5">
        <Swatch token={token} shape="line" />
        {name}
      </span>
      <span className="font-mono tabular-nums">{value}</span>
    </div>
  );
}
