---
sidebar_position: 3
---

# 🤝 Contribuindo com o Projeto

Saiba como contribuir com código, reportar bugs ou sugerir melhorias.

## Antes de Começar

1. Faça um **fork** do repositório
2. Clone seu fork: `git clone https://github.com/seu-usuario/SimuladorFinanceiro.git`
3. Configure um remote upstream: `git remote add upstream https://github.com/LiloMarino/SimuladorFinanceiro.git`

## Tipos de Contribuição

### 🐛 Reportar Bugs

1. Abra uma [Issue](https://github.com/LiloMarino/SimuladorFinanceiro/issues)
2. Descreva o problema detalhadamente
3. Inclua:
   - Sistema operacional
   - Versão da aplicação
   - Passos para reproduzir
   - Resultado esperado vs atual

### 💡 Sugerir Melhorias

1. Abra uma [Discussion](https://github.com/LiloMarino/SimuladorFinanceiro/discussions)
2. Descreva sua ideia
3. Aguarde feedback da comunidade
4. Se aprovado, abra uma Issue para rastrear

### 🔧 Enviar Código

1. **Crie uma branch** para sua feature
   ```bash
   git checkout -b feature/minha-feature
   ```

2. **Faça suas mudanças**
   - Escreva código limpo e bem comentado
   - Siga as convenções do projeto

3. **Teste suas mudanças**
   ```bash
   # Backend
   python -m pytest
   
   # Frontend
   pnpm test
   ```

4. **Commit e Push**
   ```bash
   git add .
   git commit -m "feat: descrição clara da mudança"
   git push origin feature/minha-feature
   ```

5. **Abra uma Pull Request**
   - Compare contra a branch `main`
   - Descreva suas mudanças
   - Referencie issues relacionadas

## Diretrizes de Código

### Python
- Siga [PEP 8](https://pep8.org/)
- Use type hints
- Escreva docstrings claras

### TypeScript
- Use ESLint + Prettier
- Escreva tipos explícitos
- Evite `any`

## Processo de Review

1. Um mantenedor revisará seu código
2. Pode haverrequests para mudanças
3. Uma vez aprovado, será feito merge na `main`

## Licença

Ao contribuir, você concorda que seu código será licenciado sob [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0).

## Dúvidas?

Abra uma **Discussion** ou entre em contato! 🙌
