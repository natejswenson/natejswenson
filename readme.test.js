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

  describe('Header: typing animation', () => {
    test('should embed the typing animation GIF', () => {
      expect(readmeContent).toMatch(/!\[[^\]]*\]\([^)]*output\.gif\)/);
    });

    test('should serve the GIF from the GitHub raw URL, not GitLab', () => {
      expect(readmeContent).toMatch(
        /raw\.githubusercontent\.com\/natejswenson\/natejswenson\/main\/output\.gif/,
      );
      expect(readmeContent).not.toMatch(/gitlab\.com/i);
    });

    test('should include descriptive alt text naming Nate Swenson', () => {
      expect(readmeContent).toMatch(/!\[[^\]]*nate swenson[^\]]*\]/i);
    });
  });

  describe('Featured Projects section', () => {
    test('should have a Featured Projects heading', () => {
      expect(readmeContent).toMatch(/##\s+.*Featured Projects/i);
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

  describe('Markdown health', () => {
    test('should be non-empty', () => {
      expect(readmeContent.length).toBeGreaterThan(500);
    });

    test('should use valid markdown links', () => {
      expect(readmeContent).toMatch(/\[.+\]\(.+\)/);
    });
  });
});
