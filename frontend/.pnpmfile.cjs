// O pacote typescript 7 não exporta a API de compilador; o openapi-typescript gera os tipos
// com ela e recebe a do 6 como dependência própria. O pnpm resolve peer dependency pelo
// typescript da raiz, ignorando overrides e packageExtensions, por isso o manifesto muda aqui.
module.exports = {
  hooks: {
    readPackage(pkg) {
      if (pkg.name === 'openapi-typescript') {
        delete pkg.peerDependencies.typescript
        pkg.dependencies = { ...pkg.dependencies, typescript: 'npm:@typescript/typescript6@^6' }
      }
      return pkg
    },
  },
}
