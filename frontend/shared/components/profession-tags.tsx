import { tagTable } from "@/shared/lib/profession-tag-tables";
import { TAG_NAMES, type TagKey } from "@/shared/lib/professions";
import type { Profession } from "@/types";
import { Badge } from "./ui/badge";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "./ui/hover-card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

type ProfessionTagsProps = {
  profession: Profession;
  tags: TagKey[];
  /** O salário que o host definiu, base das tabelas */
  salary: number;
};

/** As etiquetas "Afetado por" de uma profissão: cada uma abre, no mouse e no foco, a tabela de como mexe na renda. */
export function ProfessionTags({ profession, tags, salary }: ProfessionTagsProps) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {tags.map((tag) => {
        const table = tagTable(tag, profession, salary);
        return (
          <HoverCard key={tag}>
            <HoverCardTrigger
              delay={150}
              render={
                // oxlint-disable-next-line jsx-a11y/control-has-associated-label
                <Badge variant="outline" className="cursor-help" render={<button type="button" />} />
              }
            >
              {TAG_NAMES[tag]}
            </HoverCardTrigger>
            <HoverCardContent compact>
              <div className="grid gap-0.5">
                <b className="text-sm font-semibold">{table.title}</b>
                <span className="text-xs text-muted-foreground">{table.subtitle}</span>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{table.header[0]}</TableHead>
                    <TableHead>{table.header[1]}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {table.rows.map(([left, right]) => (
                    <TableRow key={left}>
                      <TableCell>{left}</TableCell>
                      <TableCell>{right}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <span className="text-xs text-muted-foreground">{table.footnote}</span>
            </HoverCardContent>
          </HoverCard>
        );
      })}
    </div>
  );
}
