interface FixedIncomeProduct {
  name: string;
  rate: string;
  description: string;
  maturity: string;
  liquidity: string;
  ir: string;
}

interface FixedIncomeProps {
  products: FixedIncomeProduct[];
}

export default function FixedIncomePage({
  products = [
    {
      name: "LCI",
      rate: "94% CDI",
      description: "Letra de Crédito Imobiliário",
      maturity: "1 ano",
      liquidity: "D+0",
      ir: "Isento",
    },
    {
      name: "LCA",
      rate: "92% CDI",
      description: "Letra de Crédito do Agronegócio",
      maturity: "2 anos",
      liquidity: "D+30",
      ir: "Isento",
    },
    {
      name: "CDB",
      rate: "110% CDI",
      description: "Certificado de Depósito Bancário",
      maturity: "3 anos",
      liquidity: "D+1",
      ir: "15%",
    },
    {
      name: "Tesouro IPCA+",
      rate: "IPCA + 5,80%",
      description: "Tesouro Direto",
      maturity: "2035",
      liquidity: "D+1",
      ir: "15% (reduz)",
    },
    {
      name: "CDB Prefixado",
      rate: "11,5% a.a.",
      description: "Certificado de Depósito Bancário",
      maturity: "2 anos",
      liquidity: "D+0",
      ir: "15%",
    },
    {
      name: "Tesouro Selic",
      rate: "Selic + 0,10%",
      description: "Tesouro Direto",
      maturity: "2029",
      liquidity: "D+1",
      ir: "15% (reduz)",
    },
  ],
}: FixedIncomeProps) {
  return (
    <section id="fixed-income" className="section-content p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <div
            key={product.name}
            className="bg-white rounded-lg shadow-md overflow-hidden card-hover transition-all duration-200"
          >
            <div className="p-4 border-b">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-lg">{product.name}</h3>
                <span className="text-green-500 text-sm font-medium">
                  Taxa: {product.rate}
                </span>
              </div>
              <p className="text-gray-500 text-sm">{product.description}</p>
            </div>
            <div className="p-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500">Vencimento:</span>
                <span className="font-medium">{product.maturity}</span>
              </div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500">Liquidez:</span>
                <span className="font-medium">{product.liquidity}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">IR:</span>
                <span className="font-medium">{product.ir}</span>
              </div>
            </div>
            <div className="bg-gray-50 px-4 py-2 flex justify-end">
              <button className="text-blue-600 text-sm font-medium hover:text-blue-800">
                Adicionar
              </button>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
