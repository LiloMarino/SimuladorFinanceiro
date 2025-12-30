import { Card } from "@/shared/components/ui/card";

export function PortfolioPieEmpty({ title }: { title: string }) {
  return (
    <Card className="p-6 flex flex-col">
      <h3 className="font-semibold">{title}</h3>
      <div className="flex-1 flex items-center justify-center text-muted-foreground">Sem dados</div>
    </Card>
  );
}
