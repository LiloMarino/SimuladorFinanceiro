import { PlayerAvatar } from "@/shared/components/player-avatar";

type PlayerOptionProps = {
  nickname: string;
  color: string;
};

/** Jogador numa lista de escolha: o avatar dele e o apelido. */
export function PlayerOption({ nickname, color }: PlayerOptionProps) {
  return (
    <span className="flex items-center gap-2">
      <PlayerAvatar nickname={nickname} color={color} size="sm" />
      {nickname}
    </span>
  );
}
