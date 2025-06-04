import re

MODELS_PATH = "backend/models/models.py"

with open(MODELS_PATH, "r", encoding="utf-8") as f:
    code = f.read()

# Substitui automaticamente as referências ao Decimal geradas pelo sqlacodegen
code = re.sub(r"Double\(asdecimal=True\)", "Double()", code)
code = re.sub(r"Mapped\[decimal\.Decimal\]", "Mapped[float]", code)
code = re.sub(r"import decimal\n", "", code)

with open(MODELS_PATH, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ Modelos corrigidos para usar float (Double sem asdecimal=True).")
