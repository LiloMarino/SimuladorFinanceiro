import { PlayerAvatar } from "@/shared/components/player-avatar";

type PlayerOptionProps = {
  nickname: string;
  color?: string | undefined;
  /** Complemento ao lado do apelido, como "(você)" */
  suffix?: string | undefined;
};

/** Jogador numa lista de escolha: o avatar dele e o apelido. */
export function PlayerOption({ nickname, color, suffix }: PlayerOptionProps) {
  return (
    <span className="flex items-center gap-2">
      <PlayerAvatar nickname={nickname} color={color} size="sm" />
      {suffix ? `${nickname} ${suffix}` : nickname}
    </span>
  );
}
