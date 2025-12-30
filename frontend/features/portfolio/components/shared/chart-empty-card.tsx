import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";

interface ChartEmptyCardProps {
  title: string;
  height?: number | string;
  icon?: React.ReactNode;
  message?: string;
}

export function ChartEmptyCard({
  title,
  height = 380,
  icon = "📊",
  message = "Nenhum dado disponível",
}: ChartEmptyCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>

      <CardContent
        className="flex flex-col items-center justify-center text-center text-muted-foreground"
        style={{ height }}
      >
        <div className="space-y-2">
          <div className="text-4xl opacity-50">{icon}</div>
          <p>{message}</p>
        </div>
      </CardContent>
    </Card>
  );
}
