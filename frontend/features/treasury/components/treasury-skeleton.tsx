import { Card, CardContent } from "@/shared/components/ui/card";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableRow } from "@/shared/components/ui/table";

const ROWS = 6;
const COLUMNS = 5;

/** O formato da tela carregando: cabeçalho, a tabela dos títulos e o gráfico ao lado do termômetro. */
export function TreasurySkeleton() {
  return (
    <div className="grid gap-5" aria-busy="true" aria-label="Carregando o Tesouro">
      {/* Header */}
      <Card>
        <CardContent>
          <div className="flex items-center gap-4">
            <Skeleton className="size-14" />
            <div className="grid flex-1 gap-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-3.5 w-2/3" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Títulos à venda */}
      <Card className="overflow-hidden">
        <CardContent>
          <div className="grid gap-2">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-3.5 w-1/2" />
          </div>
        </CardContent>
        <Table>
          <TableBody>
            {Array.from({ length: ROWS }, (_, row) => (
              <TableRow key={row}>
                {Array.from({ length: COLUMNS }, (_, column) => (
                  <TableCell key={column}>
                    {column === 0 ? (
                      <div className="grid gap-1.5">
                        <Skeleton className="h-3.5 w-3/5" />
                        <Skeleton className="h-2.5 w-1/3" />
                      </div>
                    ) : (
                      <Skeleton className="h-5 w-16" />
                    )}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Gráfico e termômetro */}
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_420px]">
        <Card>
          <CardContent>
            <Skeleton className="h-[340px] w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Skeleton className="h-[340px] w-full" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
