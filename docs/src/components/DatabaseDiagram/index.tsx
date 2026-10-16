import BrowserOnly from "@docusaurus/BrowserOnly";
import { useColorMode } from "@docusaurus/theme-common";
import { useEffect, useRef } from "react";
import schema from "../../generated/schema.json";

type EditorElement = HTMLElement & {
  setSchemaSQL: (
    value: string,
    options?: { placement?: "auto" | "grid" },
  ) => Promise<void> | void;
  setPresetTheme: (options: { appearance: "light" | "dark" }) => void;
  setInitialValue: (value: string) => void;
  value: string;
};

// Ajusta zoom e origem para o diagrama inteiro caber na área visível
function fitToView(editor: EditorElement, width: number, height: number) {
  const doc = JSON.parse(editor.value);
  const tables = Object.values<{
    ui: { x: number; y: number };
    columnIds: string[];
  }>(doc.collections.tableEntities);
  const TABLE_WIDTH = 420;
  const minX = Math.min(...tables.map((t) => t.ui.x));
  const minY = Math.min(...tables.map((t) => t.ui.y));
  const maxX = Math.max(...tables.map((t) => t.ui.x)) + TABLE_WIDTH;
  const maxY = Math.max(...tables.map((t) => t.ui.y + 40 + t.columnIds.length * 24));
  const zoom = Math.min(1, width / (maxX - minX + 100), height / (maxY - minY + 100));
  doc.settings.zoomLevel = zoom;
  doc.settings.originX = (-minX + 50) * zoom;
  doc.settings.originY = (-minY + 50) * zoom;
  editor.setInitialValue(JSON.stringify(doc));
}

function Editor() {
  const host = useRef<HTMLDivElement>(null);
  const editorRef = useRef<EditorElement | null>(null);
  const { colorMode } = useColorMode();
  const colorModeRef = useRef(colorMode);
  colorModeRef.current = colorMode;

  useEffect(() => {
    let cancelled = false;
    void import("@dineug/erd-editor").then(async () => {
      if (cancelled || !host.current) return;
      const editor = document.createElement("erd-editor") as EditorElement;
      Object.assign(editor.style, { display: "block", width: "100%", height: "100%" });
      host.current.appendChild(editor);
      editorRef.current = editor;
      editor.setPresetTheme({ appearance: colorModeRef.current });
      // O editor nasce editável e nada é salvo: o diagrama volta ao schema dos models a cada visita
      await editor.setSchemaSQL(schema.ddl, { placement: "auto" });
      const { width, height } = editor.getBoundingClientRect();
      fitToView(editor, width, height);
    });
    return () => {
      cancelled = true;
      editorRef.current?.remove();
      editorRef.current = null;
    };
  }, []);

  useEffect(() => {
    editorRef.current?.setPresetTheme({ appearance: colorMode });
  }, [colorMode]);

  return <div ref={host} style={{ width: "100%", height: "85vh" }} />;
}

export default function DatabaseDiagram() {
  return <BrowserOnly>{() => <Editor />}</BrowserOnly>;
}
