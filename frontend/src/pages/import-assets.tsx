import React, { useState, useRef } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileCsv, faChartLine, faCloudUploadAlt, faSearch } from "@fortawesome/free-solid-svg-icons";

export default function ImportAssetsPage() {
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [csvTicker, setCsvTicker] = useState("");
  const [csvOverwrite, setCsvOverwrite] = useState(false);
  const [yTicker, setYTicker] = useState("");
  const [yOverwrite, setYOverwrite] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [currentAction, setCurrentAction] = useState<"csv" | "yfinance" | null>(null);

  const csvFormRef = useRef<HTMLFormElement>(null);
  const yFormRef = useRef<HTMLFormElement>(null);

  // Drag & Drop
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setCsvFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  // Abrir modal
  const openModal = (action: "csv" | "yfinance") => {
    setCurrentAction(action);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setCurrentAction(null);
  };

  // Confirmar ação
  const handleConfirm = () => {
    let form: HTMLFormElement | null = null;

    if (currentAction === "csv") form = csvFormRef.current;
    else if (currentAction === "yfinance") form = yFormRef.current;

    if (form && currentAction) {
      // Adiciona input hidden com action (como no JS antigo)
      const actionInput = document.createElement("input");
      actionInput.type = "hidden";
      actionInput.name = "action";
      actionInput.value = currentAction;
      form.appendChild(actionInput);

      form.submit();
    }

    closeModal();
  };

  return (
    <section id="import-assets" className="section-content p-4">
      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full p-6 text-center">
            <h2 className="text-xl font-semibold mb-4">Confirmar Importação</h2>
            <p className="text-gray-700 mb-6">Deseja realmente importar os dados selecionados?</p>
            <div className="flex justify-center gap-4">
              <button
                onClick={handleConfirm}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
              >
                Sim
              </button>
              <button
                onClick={closeModal}
                className="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded"
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow p-6 space-y-8">
        <h2 className="text-xl font-semibold mb-6">Importar Ativos</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* CSV Form */}
          <form ref={csvFormRef} method="POST" action="/import-assets" encType="multipart/form-data">
            <div className="border rounded-lg p-6">
              <div className="flex items-center mb-4">
                <FontAwesomeIcon icon={faFileCsv} className="text-blue-500 text-2xl mr-3" />
                <h3 className="text-lg font-medium">Importar via CSV</h3>
              </div>
              <p className="text-gray-600 mb-4">Faça upload de um arquivo CSV com os dados históricos do ativo.</p>

              <div className="mb-4">
                <label htmlFor="asset-name" className="block text-sm font-medium text-gray-700 mb-1">
                  Nome do Ativo
                </label>
                <input
                  type="text"
                  id="asset-name"
                  name="ticker"
                  className="w-full p-2 border rounded-md"
                  placeholder="Digite o nome do ativo"
                  value={csvTicker}
                  onChange={(e) => setCsvTicker(e.target.value)}
                />
              </div>

              <div
                id="drop-area"
                className="border-2 border-dashed border-gray-300 rounded-md p-6 text-center mb-4 transition-colors cursor-pointer"
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onClick={() => document.getElementById("csv-upload")?.click()}
              >
                <input
                  type="file"
                  id="csv-upload"
                  name="csv_file"
                  className="hidden"
                  accept=".csv"
                  onChange={(e) => e.target.files && setCsvFile(e.target.files[0])}
                  required
                />
                <FontAwesomeIcon icon={faCloudUploadAlt} className="text-3xl text-gray-400 mb-2" />
                <p className="text-sm text-gray-500">Arraste e solte ou clique para selecionar</p>
                <p className="mt-2 text-sm text-gray-700">{csvFile?.name}</p>
              </div>

              <div className="mb-4">
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={csvOverwrite}
                    onChange={(e) => setCsvOverwrite(e.target.checked)}
                  />
                  <span className="text-sm text-gray-700">Sobrescrever dados existentes</span>
                </label>
              </div>

              <button
                type="button"
                onClick={() => openModal("csv")}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"
              >
                Importar CSV
              </button>
            </div>
          </form>

          {/* yFinance Form */}
          <form ref={yFormRef} method="POST" action="/import-assets">
            <div className="border rounded-lg p-6">
              <div className="flex items-center mb-4">
                <FontAwesomeIcon icon={faChartLine} className="text-yellow-500 text-2xl mr-3" />
                <h3 className="text-lg font-medium">Buscar via yFinance</h3>
              </div>
              <p className="text-gray-600 mb-4">Busque ativos usando a API do yFinance.</p>

              <div className="mb-4 relative">
                <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 mb-1">
                  Código do Ativo
                </label>
                <input
                  type="text"
                  id="ticker"
                  name="ticker"
                  placeholder="Ex: PETR4, VALE3, BTC-USD"
                  className="w-full p-2 border rounded-md"
                  value={yTicker}
                  onChange={(e) => setYTicker(e.target.value)}
                  required
                />
                <button className="absolute right-2 top-2 text-gray-500">
                  <FontAwesomeIcon icon={faSearch} />
                </button>
              </div>

              <div className="mb-4">
                <label className="inline-flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={yOverwrite}
                    onChange={(e) => setYOverwrite(e.target.checked)}
                  />
                  <span className="text-sm text-gray-700">Sobrescrever dados existentes</span>
                </label>
              </div>

              <button
                type="button"
                onClick={() => openModal("yfinance")}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"
              >
                Buscar e Importar
              </button>
            </div>
          </form>
        </div>
      </div>
    </section>
  );
}
