import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const organizationName = "LiloMarino";
const projectName = "SimuladorFinanceiro";

const config: Config = {
  title: "Simulador Financeiro",
  tagline: "Documentação oficial do projeto",
  favicon: "img/favicon.ico",
  url: "https://lilomarino.github.io",

  future: {
    v4: true,
  },

  baseUrl: `/${projectName}/`,
  organizationName,
  trailingSlash: false,
  projectName,
  deploymentBranch: "gh-pages",
  onBrokenLinks: "throw",

  i18n: {
    defaultLocale: "pt-BR",
    locales: ["pt-BR"],
  },

  markdown: {
    mermaid: true,
  },

  themes: ["@docusaurus/theme-mermaid", "docusaurus-theme-openapi-docs"],

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          editUrl: `https://github.com/${organizationName}/${projectName}/tree/main/docs/`,
          routeBasePath: "/",
          docItemComponent: "@theme/ApiItem",
        },
        pages: false,
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    [
      "docusaurus-plugin-openapi-docs",
      {
        id: "api",
        docsPluginId: "classic",
        config: {
          api: {
            specPath: "openapi.json",
            outputDir: "docs/api",
            sidebarOptions: {
              groupPathsBy: "tag",
              categoryLinkSource: "tag",
            },
          },
        },
      },
    ],
  ],

  themeConfig: {
    image: "img/docusaurus-social-card.jpg",

    colorMode: {
      respectPrefersColorScheme: true,
    },

    navbar: {
      title: "Simulador Financeiro",
      logo: {
        alt: "Simulador Financeiro Logo",
        src: "img/logo.svg",
      },
      items: [
        {
          type: "docSidebar",
          sidebarId: "tutorialSidebar",
          position: "left",
          label: "Documentação",
        },
        {
          type: "docSidebar",
          sidebarId: "apisidebar",
          position: "left",
          label: "API",
        },
        {
          href: `https://github.com/${organizationName}/${projectName}`,
          label: "GitHub",
          position: "right",
        },
      ],
    },

    footer: {
      style: "dark",
      links: [
        {
          title: "Documentação",
          items: [
            { label: "Introdução", to: "/" },
            { label: "Como Usar", to: "/como-usar/instalacao" },
            { label: "Desenvolvimento", to: "/desenvolvimento/intro-dev" },
          ],
        },
        {
          title: "Projeto",
          items: [
            {
              label: "GitHub",
              href: `https://github.com/${organizationName}/${projectName}`,
            },
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} Simulador Financeiro`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
