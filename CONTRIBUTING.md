# Guia de Desenvolvimento

## 📁 Estrutura do Projeto  

**Estrutura Documentada:**

```plaintext
/SimuladorFinanceiro
├── .gitignore                   # Arquivos e pastas a serem ignorados pelo Git
├── CONTRIBUTING.md              # Guia para contribuir com o projeto
├── LICENSE                      # Licença de uso do projeto
├── README.md                    # Documentação principal
├── backend/                     # Lógica do backend em Flask
│   ├── data_loader.py
│   ├── database.py              # Configuração do banco de dados
│   ├── logger_utils.py          # Utilitários para logging
│   ├── models/                  # Modelos ORM
│   │   └── models.py            # Definição dos modelos de dados
│   ├── routes.py                # Rotas de navegação (páginas)
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/               # HTML com Jinja2
│       └── index.html
├── data/                        # Arquivos de dados de entrada
│   └── simulador_financeiro.mwb # Modelo visual do banco (MySQL Workbench)
├── example.env                  # Exemplo de variáveis de ambiente
├── main.py                      # Ponto de entrada da aplicação Flask
├── requirements.txt             # Lista de dependências do projeto
└── scripts/                     # Scripts auxiliares
    ├── fix_model.py
    ├── tree.py                  # Geração da árvore do projeto
    └── tree_descriptions.yaml
```

A árvore da estrutura do projeto é mantido automaticamente com o script

```bash
python .\scripts\tree.py
```

As descrições exibidas ao lado dos arquivos e pastas na árvore são carregadas automaticamente do arquivo

```
scripts/tree_descriptions.yaml
```

Para adicionar ou alterar descrições, basta editar esse arquivo YAML, seguindo o padrão:

```yaml
backend/: Lógica do backend em Flask
backend/database.py: Configuração do banco de dados
data/: Arquivos de dados de entrada
```

Após salvar, execute novamente:

```bash
python .\scripts\tree.py
```

para gerar a estrutura atualizada com os comentários alinhados.

## 🔁 Ciclo de Desenvolvimento com Banco de Dados

1. ✏️ **Editar modelo no MySQL Workbench** (`.mwb`)
2. 📥 **Sincronizar o banco de dados MySQL**
3. 🧬 **Gerar ORM com sqlacodegen**  

```bash
   sqlacodegen mysql+pymysql://usuario:senha@localhost/simulador_financeiro > backend/models/models.py
```
4. 🛠️ **Compatibilizar com múltiplos bancos (MySQL/SQLite)**

O projeto detecta automaticamente qual banco usar (MySQL ou SQLite) com base nas variáveis de ambiente, e cria as tabelas automaticamente com:
```python
Base.metadata.create_all(bind=engine)
```