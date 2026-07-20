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

    const projects = [
      'local-fitness-dude',
      'traefik-local-cli',
      'claude-skills',
      'llm-token-calculator',
    ];

    test.each(projects)('should link to the %s repository', (repo) => {
      const url = `https://github.com/natejswenson/${repo}`;
      expect(readmeContent).toContain(`[${repo}](${url})`);
    });

    test('should feature exactly the four curated repositories', () => {
      const headingMatches = readmeContent.match(/###\s+.*\[[^\]]+\]\(https:\/\/github\.com\/natejswenson\//g) || [];
      expect(headingMatches.length).toBe(projects.length);
    });

    test('should describe the tech stack for each project', () => {
      expect(readmeContent).toMatch(/`MCP`/);
      expect(readmeContent).toMatch(/`Claude Code`/);
      expect(readmeContent).toMatch(/`Flask`/);
      expect(readmeContent).toMatch(/`Docker`/);
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
      const entries = readmeContent.match(/###\s+No\.\s+\d{3}\s+·/g) || [];
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
