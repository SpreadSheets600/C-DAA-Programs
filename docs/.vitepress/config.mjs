import { defineConfig } from "vitepress";

export default defineConfig({
  base: "/C-DAA-Programs/",

  title: "C · DAA Programs",
  description:
    "Design and Analysis of Algorithms — Lab programs, algorithms, and code walkthroughs.",

  head: [
    ["link", { rel: "icon", href: "/C-DAA-Programs/favicon.svg" }],
    ["meta", { name: "theme-color", content: "#7c3aed" }],
  ],

  lastUpdated: true,
  cleanUrls: true,

  markdown: {
    theme: {
      light: "one-dark-pro",
      dark: "one-dark-pro",
    },
    lineNumbers: true,
  },

  themeConfig: {
    logo: { src: "/favicon.svg", alt: "DAA" },

    nav: [
      { text: "Home", link: "/" },
      { text: "Sessions", link: "/sessions/10-04-2026" },
      {
        text: "GitHub",
        link: "https://github.com/SpreadSheets600/C-DAA-Programs",
      },
    ],

    sidebar: [
      {
        text: "📁 Sessions",
        items: [
          {
            text: "April 10, 2026",
            link: "/sessions/10-04-2026",
            items: [
              {
                text: "Binary Search — Iterative",
                link: "/sessions/10-04-2026#exercise-1-binary-search-with-iteration",
              },
              {
                text: "Binary Search — Recursive",
                link: "/sessions/10-04-2026#exercise-2-binary-search-with-recursion",
              },
              {
                text: "Binary Search — Unsorted Array",
                link: "/sessions/10-04-2026#exercise-3-binary-search-with-unsorted-array",
              },
            ],
          },
        ],
      },
    ],

    socialLinks: [
      {
        icon: "github",
        link: "https://github.com/SpreadSheets600/C-DAA-Programs",
      },
    ],

    search: {
      provider: "local",
    },

    footer: {
      message: "Design & Analysis of Algorithms — Lab Programs",
      copyright: "Built with VitePress · SpreadSheets600",
    },

    editLink: {
      pattern:
        "https://github.com/SpreadSheets600/C-DAA-Programs/edit/main/docs/:path",
      text: "Edit this page on GitHub",
    },

    outline: {
      level: [2, 3],
      label: "On this page",
    },

    docFooter: {
      prev: "← Previous Session",
      next: "Next Session →",
    },
  },
});
