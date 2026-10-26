import { Bot } from "lucide-react";
import { Avatar, AvatarFallback } from "@/shared/components/ui/avatar";
import { playerColorStyle } from "@/shared/lib/player-colors";
import { playerInitials } from "@/shared/lib/player-initials";

type PlayerAvatarProps = {
  nickname: string;
  /** Chave da paleta que o servidor devolve; ausente, o avatar fica neutro (comparação de simulações). */
  color?: string | undefined;
  /** Jogador sem pessoa por trás: o robô no lugar da sigla */
  bot?: boolean | undefined;
  size?: React.ComponentProps<typeof Avatar>["size"] | undefined;
};

/** Avatar do jogador: a cor exclusiva dele e a sigla de duas letras do apelido (ou o robô, no bot). */
export function PlayerAvatar({ nickname, color, bot = false, size }: PlayerAvatarProps) {
  const { background, foreground } = playerColorStyle(color);

  return (
    <Avatar {...(size ? { size } : {})}>
      <AvatarFallback color={background} foreground={foreground}>
        {bot ? <Bot className="size-1/2" strokeWidth={2.2} /> : playerInitials(nickname)}
      </AvatarFallback>
    </Avatar>
  );
}
