const fs = require('fs');
const path = require('path');

const read = (f) => {
  const p = path.join(__dirname, f);
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
};

describe('README.md — a single PRESS document', () => {
  const readme = read('README.md');

  test('should embed profile.svg and nothing else', () => {
    expect(readme).toMatch(/!\[[^\]]*\]\([^)]*profile\.svg\)/);
    const images = readme.match(/!\[[^\]]*\]\([^)]+\)/g) || [];
    expect(images.length).toBe(1);
  });

  test('should serve the SVG from the GitHub raw URL, not GitLab', () => {
    expect(readme).toMatch(
      /raw\.githubusercontent\.com\/natejswenson\/natejswenson\/main\/profile\.svg/,
    );
    expect(readme).not.toMatch(/gitlab\.com/i);
  });

  test('should not fall back to the retired PNG artifacts', () => {
    expect(readme).not.toMatch(/output\.gif|banner\.png|card-\d{3}\.png/);
  });

  // The page is one image, so alt text is the entire accessible and
  // searchable surface. It has to carry every repo, stack, and contact.
  describe('alt text carries the whole page', () => {
    const alt = (readme.match(/!\[([^\]]*)\]/) || [, ''])[1];

    test('should be substantial prose, not a label', () => {
      expect(alt.length).toBeGreaterThan(400);
    });

    test.each(['local-fitness', 'traefik-local-cli', 'claude-skills', 'local-budget'])(
      'should name the %s project',
      (repo) => expect(alt).toContain(repo),
    );

    test.each(['MCP', 'Claude Code', 'Flask', 'Docker', 'SQLite'])(
      'should name the %s technology',
      (tech) => expect(alt).toContain(tech),
    );

    test('should name Nate and his role', () => {
      expect(alt).toMatch(/Nate Swenson/);
      expect(alt).toMatch(/Senior DevOps Engineer/);
    });

    test('should include both contact links', () => {
      expect(alt).toMatch(/natejswenson\.com/);
      expect(alt).toMatch(/linkedin\.com\/in\/natejswenson/);
    });
  });
});

describe('profile.svg — PRESS brand compliance', () => {
  const svg = read('profile.svg');

  test('should exist and be a self-contained SVG', () => {
    expect(svg).toMatch(/^<svg[^>]*xmlns="http:\/\/www\.w3\.org\/2000\/svg"/);
    expect(svg).toMatch(/<\/svg>$/);
  });

  // GitHub loads the SVG through <img>, which is an isolated context that
  // cannot fetch anything. Every asset must be inlined or it renders in a
  // fallback face.
  test('should reference no external resources', () => {
    const external = svg.match(/(?:href|src|url)\(?["']?https?:\/\//g) || [];
    expect(external).toEqual([]);
  });

  test('should embed all four brand faces as woff2 data URIs', () => {
    const faces = svg.match(/@font-face\{font-family:'([^']+)'/g) || [];
    expect(faces.length).toBe(4);
    expect((svg.match(/data:font\/woff2;base64,/g) || []).length).toBe(4);
  });

  test('should style with real CSS, not per-element attributes', () => {
    expect(svg).toMatch(/<style>/);
    expect(svg).toMatch(/letter-spacing:/);
  });

  describe('tokens', () => {
    const TOKENS = {
      paper: '#F5F0E6',
      ink: '#181510',
      dim: '#6E675C',
      accent: '#E8501F',
    };

    test.each(Object.entries(TOKENS))('should use the canonical %s token', (_n, hex) => {
      expect(svg).toContain(hex);
    });

    test('should not reference any retired-palette color', () => {
      expect(svg).not.toMatch(/df0024|f3c300|00ab9f|2e6db4/i);
    });

    // The accent law: orange is a signature, not a scheme. One headline
    // pivot plus the stamp plus one ledger numeral per card.
    test('should spend the accent sparingly', () => {
      const uses = (svg.match(/E8501F/gi) || []).length;
      expect(uses).toBeGreaterThan(0);
      expect(uses).toBeLessThanOrEqual(6);
    });
  });

  describe('content', () => {
    test.each(['local-fitness', 'traefik-local-cli', 'claude-skills', 'local-budget'])(
      'should set the %s entry',
      (repo) => expect(svg).toContain(`>${repo}<`),
    );

    test('should no longer feature the retired llm-token-calculator entry', () => {
      expect(svg).not.toMatch(/llm-token-calculator/);
    });

    test('should number the entries as ledger rows', () => {
      const nos = svg.match(/>No\. \d{3}</g) || [];
      // Four cards plus the masthead eyebrow.
      expect(nos.length).toBe(5);
    });

    test('should carry no emoji, since PRESS is typographic', () => {
      const emoji = svg.match(
        /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu,
      );
      expect(emoji).toBeNull();
    });
  });

  test('should stay small enough to load fast', () => {
    const kb = Buffer.byteLength(svg, 'utf8') / 1024;
    expect(kb).toBeLessThan(120);
  });
});
