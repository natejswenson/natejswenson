const fs = require('fs');
const path = require('path');

describe('README.md — repo-focused profile', () => {
  let readmeContent = '';

  beforeAll(() => {
    const readmePath = path.join(__dirname, 'README.md');
    if (fs.existsSync(readmePath)) {
      readmeContent = fs.readFileSync(readmePath, 'utf8');
    }
  });

  describe('Header: PRESS masthead banner', () => {
    test('should embed the PRESS banner image', () => {
      expect(readmeContent).toMatch(/!\[[^\]]*\]\([^)]*banner\.png\)/);
    });

    test('should serve the banner from the GitHub raw URL, not GitLab', () => {
      expect(readmeContent).toMatch(
        /raw\.githubusercontent\.com\/natejswenson\/natejswenson\/main\/banner\.png/,
      );
      expect(readmeContent).not.toMatch(/gitlab\.com/i);
    });

    test('should include descriptive alt text naming Nate Swenson', () => {
      expect(readmeContent).toMatch(/!\[[^\]]*nate swenson[^\]]*\]/i);
    });
  });

  describe('Selected work section', () => {
    test('should have a Selected work heading', () => {
      expect(readmeContent).toMatch(/##\s+.*Selected work/i);
    });

    // Cards are rendered as PRESS images because GitHub strips CSS from
    // markdown, so each entry is a linked card rather than a heading.
    const projects = [
      { repo: 'local-fitness', card: 'card-001.png' },
      { repo: 'traefik-local-cli', card: 'card-002.png' },
      { repo: 'claude-skills', card: 'card-003.png' },
      { repo: 'local-budget', card: 'card-004.png' },
    ];

    test.each(projects)('should link the $card card to the $repo repository', ({ repo, card }) => {
      const link = new RegExp(
        `<a href="https://github\\.com/natejswenson/${repo}">\\s*<img[^>]*${card.replace('.', '\\.')}`,
      );
      expect(readmeContent).toMatch(link);
    });

    test('should no longer feature the retired llm-token-calculator entry', () => {
      expect(readmeContent).not.toMatch(/llm-token-calculator/);
    });

    test('should feature exactly the four curated repositories', () => {
      const cards = readmeContent.match(/assets\/cards\/card-\d{3}\.png/g) || [];
      // Each card appears once, in a src attribute.
      expect(cards.length).toBe(projects.length);
    });

    test('should serve every card from the GitHub raw URL', () => {
      const srcs = readmeContent.match(/src="([^"]*card-\d{3}\.png)"/g) || [];
      expect(srcs.length).toBe(projects.length);
      srcs.forEach((src) => {
        expect(src).toContain('raw.githubusercontent.com/natejswenson/natejswenson/main/');
      });
    });

    // The card text lives in a PNG, so alt text is the only thing a screen
    // reader or GitHub search can see. It has to carry the real content.
    test('should carry descriptive alt text naming each repo and its stack', () => {
      const alts = [...readmeContent.matchAll(/alt="([^"]+)"/g)].map((m) => m[1]);
      const cardAlts = alts.filter((a) => /^No\. \d{3}/.test(a));
      expect(cardAlts.length).toBe(projects.length);
      cardAlts.forEach((alt) => {
        expect(alt.length).toBeGreaterThan(80);
        expect(alt).toMatch(/Built with .+\./);
      });
      projects.forEach(({ repo }) => {
        expect(cardAlts.some((a) => a.includes(repo))).toBe(true);
      });
    });

    test('should describe the tech stack for each project', () => {
      expect(readmeContent).toMatch(/MCP/);
      expect(readmeContent).toMatch(/Claude Code/);
      expect(readmeContent).toMatch(/Flask/);
      expect(readmeContent).toMatch(/Docker/);
    });
  });

  describe('Connect footer', () => {
    test('should include the LinkedIn profile link', () => {
      expect(readmeContent).toMatch(/linkedin\.com\/in\/natejswenson/);
    });

    test('should include the personal website link', () => {
      expect(readmeContent).toMatch(/natejswenson\.com/);
    });

    test('should include a collaboration call-to-action', () => {
      expect(readmeContent).toMatch(/collaborat|build something|connect/i);
    });
  });

  describe('Leanness: no third-party stat widgets', () => {
    test('should not depend on github-readme-stats', () => {
      expect(readmeContent).not.toMatch(/github-readme-stats\.vercel\.app/i);
    });

    test('should not embed streak-stats widgets', () => {
      expect(readmeContent).not.toMatch(/streak-stats/i);
    });
  });

  describe('PRESS brand compliance', () => {
    test('should carry no emoji, since PRESS is typographic', () => {
      // Pictographic + dingbat ranges. Excludes the U+00B7 separator and the
      // typographic punctuation the brand does use.
      const emoji = readmeContent.match(
        /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\u{2190}-\u{21FF}]/gu,
      );
      expect(emoji).toBeNull();
    });

    test('should not use shields.io badges, which PRESS bans as pills', () => {
      expect(readmeContent).not.toMatch(/img\.shields\.io/i);
    });

    test('should not reference any retired-palette color', () => {
      // The pre-PRESS palette: red, yellow, teal, blue.
      expect(readmeContent).not.toMatch(/df0024|f3c300|00ab9f|2e6db4/i);
    });

    test('should number Selected work entries as ledger rows', () => {
      const entries = readmeContent.match(/alt="No\. \d{3} /g) || [];
      expect(entries.length).toBe(4);
    });
  });

  describe('Markdown health', () => {
    test('should be non-empty', () => {
      expect(readmeContent.length).toBeGreaterThan(500);
    });

    test('should use valid markdown links', () => {
      expect(readmeContent).toMatch(/\[.+\]\(.+\)/);
    });
  });
});
