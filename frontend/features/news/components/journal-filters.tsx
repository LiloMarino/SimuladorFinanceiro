import { Search } from "lucide-react";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import type { NewsSection, NotificationCatalog } from "@/types";
import type { JournalFilter } from "../lib/filter";

const ALL = "ALL";

type JournalFiltersProps = {
  filter: JournalFilter;
  onChange: (filter: JournalFilter) => void;
  catalog: NotificationCatalog | undefined;
};

/** Busca, seções e "só minha carteira" do jornal. */
export function JournalFilters({ filter, onChange, catalog }: JournalFiltersProps) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <InputGroup size="lg" className="w-85">
        <InputGroupAddon>
          <Search />
        </InputGroupAddon>
        <InputGroupInput
          value={filter.query}
          onChange={(e) => onChange({ ...filter, query: e.target.value })}
          placeholder="Buscar manchete, empresa ou ticker"
          aria-label="Buscar no jornal"
        />
      </InputGroup>
      {catalog && (
        <Tabs
          value={filter.section ?? ALL}
          onValueChange={(value) => onChange({ ...filter, section: value === ALL ? null : (value as NewsSection) })}
        >
          <TabsList variant="line">
            <TabsTrigger value={ALL}>Tudo</TabsTrigger>
            {catalog.sections.map((section) => (
              <TabsTrigger key={section.section} value={section.section}>
                {section.label}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      )}
      <div className="ml-auto flex items-center gap-2">
        <Switch
          id="journal-only-mine"
          checked={filter.onlyMine}
          onCheckedChange={(onlyMine) => onChange({ ...filter, onlyMine })}
        />
        <Label htmlFor="journal-only-mine">Só minha carteira</Label>
      </div>
    </div>
  );
}
