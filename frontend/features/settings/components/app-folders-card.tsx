import { useState } from "react";
import { Check, Copy, FolderOpen, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import type { AppFolderTarget } from "@/types";
import { useOpenAppFolder } from "../hooks/mutations/useOpenAppFolder";
import { useAppFolders } from "../hooks/queries/useAppFolders";

const FOLDERS: { target: AppFolderTarget; label: string; description: string }[] = [
  { target: "config", label: "Abrir pasta de configurações", description: "Onde ficam o config.toml e o .env." },
  { target: "logs", label: "Abrir pasta de logs", description: "O registro do que o servidor fez." },
];

/** As pastas do app no computador do host, com o caminho sempre à vista e um botão para abri-las. */
export function AppFoldersCard() {
  const { data: folders } = useAppFolders();
  const open = useOpenAppFolder();
  const [copied, setCopied] = useState<AppFolderTarget | null>(null);
  const [copyFailed, setCopyFailed] = useState(false);

  // O navegador só libera a área de transferência em https (ou localhost)
  const copy = async (target: AppFolderTarget, path: string) => {
    try {
      await navigator.clipboard.writeText(path);
      setCopyFailed(false);
      setCopied(target);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      setCopyFailed(true);
    }
  };

  if (!folders) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Pastas do app</CardTitle>
        <CardDescription>Os arquivos que você edita à mão, no computador que roda o servidor.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4">
          {FOLDERS.map(({ target, label, description }) => (
            <div key={target} className="grid grid-cols-1 gap-1.5">
              <div className="flex items-center justify-between gap-3">
                <span className="text-xs text-muted-foreground">{description}</span>
                <Button variant="outline" size="sm" onClick={() => open.mutate(target)} disabled={open.isPending}>
                  <FolderOpen />
                  {label}
                </Button>
              </div>
              <div className="flex items-center justify-between gap-3 rounded-lg bg-subtle px-3 py-2">
                <code className="min-w-0 truncate font-mono text-xs" title={folders[target]}>
                  {folders[target]}
                </code>
                <Button variant="ghost" size="xs" onClick={() => void copy(target, folders[target])}>
                  {copied === target ? <Check /> : <Copy />}
                  {copied === target ? "Copiado" : "Copiar"}
                </Button>
              </div>
            </div>
          ))}
          {copyFailed && (
            <Alert variant="warning">
              <TriangleAlert />
              <AlertDescription>Não deu para copiar: selecione o caminho e copie à mão.</AlertDescription>
            </Alert>
          )}
          <Alert variant="muted">
            <AlertDescription>
              As pastas <code className="font-mono">db</code> e <code className="font-mono">postgres</code> são do banco
              de dados e não devem ser editadas.
            </AlertDescription>
          </Alert>
        </div>
      </CardContent>
    </Card>
  );
}
