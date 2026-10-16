import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { playerInitials } from "@/shared/lib/player-initials";

type PlayerAvatarProps = {
  nickname: string;
  /** Chave da paleta que o servidor devolve; ausente, o avatar fica neutro (comparação de simulações). */
  color?: string;
  size?: React.ComponentProps<typeof Avatar>["size"];
};

/** Avatar do jogador: a cor exclusiva dele e a sigla de duas letras do apelido. */
export function PlayerAvatar({ nickname, color, size }: PlayerAvatarProps) {
  const { background, foreground } = playerColorStyle(color);

  return (
    <Avatar size={size}>
      <AvatarFallback color={background} foreground={foreground}>
        {playerInitials(nickname)}
      </AvatarFallback>
    </Avatar>
  );
}
