import type { CSSProperties } from "react";
import { Ban } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { useTutorial } from "@/features/tutorial/hooks/useTutorial";
import { DEFAULT_TUTORIAL_STYLE, type TutorialStyle } from "@/features/tutorial/lib/tutorial-storage";
import { cn } from "@/shared/lib/utils";

interface StyleOption {
  value: TutorialStyle;
  label: string;
  description: string;
}

const OPTIONS: StyleOption[] = [
  {
    value: "edge-tab",
    label: "Aba na borda",
    description: "Aba azul presa na borda direita; recolhe até virar uma alça. O aviso sai da aba.",
  },
  {
    value: "menu-item",
    label: "Item no menu",
    description: "“Como jogar” em Ferramentas, no menu lateral. Nada flutua sobre a tela.",
  },
  {
    value: "topbar-button",
    label: "Botão na topbar",
    description: "Chapéu ao lado da data. Fica perto do relógio, mas divide a topbar com as informações da partida.",
  },
  {
    value: "off",
    label: "Desligado",
    description: "Sem aviso e sem acesso na partida. O botão “Como jogar” do lobby continua.",
  },
];

/** Como o Como jogar aparece durante a partida; vale só para este navegador. */
export function TutorialStyleCard() {
  const { state, setStyle } = useTutorial();

  return (
    <Card className="lg:col-span-2">
      <CardHeader>
        <CardTitle>Tutorial</CardTitle>
        <CardDescription>Como o “Como jogar” aparece durante a partida. Vale só para você.</CardDescription>
        <CardAction>
          <Badge variant="info">Novo</Badge>
        </CardAction>
      </CardHeader>
      <CardContent>
        <RadioGroup
          value={state.style}
          onValueChange={(value) => setStyle(value as TutorialStyle)}
          aria-label="Como o Como jogar aparece"
          spacious
          className="grid-cols-2 lg:grid-cols-4"
        >
          {OPTIONS.map((option) => (
            <label
              key={option.value}
              className={cn(
                "grid cursor-pointer content-start gap-2.5 rounded-xl border p-3",
                state.style === option.value && "border-primary bg-info-soft/60 ring-1 ring-primary",
              )}
            >
              <StyleSketch style={option.value} />
              <div className="flex items-center gap-2">
                <RadioGroupItem value={option.value} />
                <b className="font-semibold">{option.label}</b>
                {option.value === DEFAULT_TUTORIAL_STYLE && (
                  <Badge variant="info" className="ml-auto">
                    Padrão
                  </Badge>
                )}
              </div>
              <span className="text-xs text-muted-foreground">{option.description}</span>
            </label>
          ))}
        </RadioGroup>
      </CardContent>
    </Card>
  );
}

const box = "absolute rounded-[5px] bg-card ring-1 ring-border";

/** Miniatura do app com o acesso desenhado no lugar onde ele aparece. */
function StyleSketch({ style }: { style: TutorialStyle }) {
  return (
    <div aria-hidden className="relative h-33 overflow-hidden rounded-lg bg-background ring-1 ring-border">
      {/* Menu lateral */}
      <span className="absolute inset-y-0 left-0 w-9 bg-sidebar" />
      {[16, 29, 42, 55, 68].map((top) => (
        <span key={top} className="absolute left-2 h-1 w-5 rounded-sm bg-sidebar-accent" style={{ top }} />
      ))}

      {/* Topbar */}
      <span className="absolute inset-x-0 top-0 left-9 h-5 border-b bg-card" />
      <span className="absolute top-1.75 left-11 h-1.5 w-7.5 rounded-sm bg-input" />
      <span className="absolute top-1.75 right-7.5 h-1.5 w-8.5 rounded-sm bg-input" />

      {/* Telas */}
      <span className={box} style={{ left: 44, top: 30, width: 92, height: 40 }} />
      <span className={box} style={{ left: 142, top: 30, right: 12, height: 40 }} />
      <span className={box} style={{ left: 44, top: 78, right: 12, height: 44 }} />

      {style === "edge-tab" && (
        <>
          <span className="absolute right-0 w-3 rounded-l-md bg-primary" style={{ top: 56, height: 40 }} />
          <Popup style={{ right: 18, top: 54 }} />
        </>
      )}
      {style === "menu-item" && (
        <>
          <span className="absolute left-1.5 h-2 w-6.5 rounded-sm bg-primary" style={{ top: 86 }} />
          <Popup style={{ left: 40, top: 74 }} />
        </>
      )}
      {style === "topbar-button" && (
        <>
          <span className="absolute top-0.75 right-2 size-3.5 rounded-full bg-primary" />
          <Popup style={{ right: 10, top: 24 }} />
        </>
      )}
      {style === "off" && <Ban className="absolute top-1/2 left-1/2 -mt-3.5 -ml-3.5 size-7 text-faint-foreground" />}
    </div>
  );
}

/** O aviso do tópico, em miniatura. */
function Popup({ style }: { style: CSSProperties }) {
  return (
    <span className="absolute h-7.5 w-19.5 rounded-[5px] bg-card shadow-md ring-1 ring-input" style={style}>
      <span className="absolute top-1.75 left-1.5 h-1 w-12 rounded-sm bg-muted-foreground/60" />
      <span className="absolute top-4.25 left-1.5 h-1.5 w-6.5 rounded-sm bg-primary" />
    </span>
  );
}
