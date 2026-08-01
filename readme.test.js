const fs = require('fs');
const path = require('path');

const read = (f) => {
  const p = path.join(__dirname, f);
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : '';
};

// Every tile is full width. GitHub styles img[align=left] with
// padding-right:20px under box-sizing:content-box, so a 50% tile measures
// 50%+20px and two of them wrap instead of pairing. Measured on the live
// page; a partial width silently breaks the layout.
const TILES = [
  { name: 'masthead', width: '100%', href: 'https://natejswenson.com' },
  { name: 'row-001', width: '100%', href: 'https://github.com/natejswenson/local-fitness' },
  { name: 'row-002', width: '100%', href: 'https://github.com/natejswenson/traefik-local-cli' },
  { name: 'row-003', width: '100%', href: 'https://github.com/natejswenson/claude-skills' },
  { name: 'row-004', width: '100%', href: 'https://github.com/natejswenson/local-budget' },
  { name: 'colophon-a', width: '100%', href: 'https://natejswenson.com' },
  { name: 'colophon-b', width: '100%', href: 'https://linkedin.com/in/natejswenson' },
];

describe('README.md — tiled, fully clickable PRESS page', () => {
  const readme = read('README.md');

  test('should be built entirely from linked tiles', () => {
    const anchors = readme.match(/<a href="[^"]+"><img[^>]*><\/a>/g) || [];
    expect(anchors.length).toBe(TILES.length);
  });

  // float:left is what makes the tiles butt together without the
  // line-height gaps that stacked inline images produce. Lose the float and
  // the page grows white hairlines at every seam.
  test('should float every tile so they tile without gaps', () => {
    const floats = readme.match(/align="left"/g) || [];
    expect(floats.length).toBe(TILES.length);
  });

  // A blank line between tiles would split them into separate <p> blocks and
  // break the float chain. They must stay in one paragraph.
  test('should keep every tile in a single paragraph', () => {
    expect(readme.trim()).not.toMatch(/\n\s*\n/);
  });

  test.each(TILES)('should link the $name tile to $href', ({ name, width, href }) => {
    const tile = new RegExp(
      `<a href="${href.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}">` +
      `<img align="left" width="${width}" src="[^"]*${name}\\.svg"`,
    );
    expect(readme).toMatch(tile);
  });

  test('should serve every tile from the GitHub raw URL, not GitLab', () => {
    const srcs = readme.match(/src="([^"]+)"/g) || [];
    expect(srcs.length).toBe(TILES.length);
    srcs.forEach((s) => {
      expect(s).toContain('raw.githubusercontent.com/natejswenson/natejswenson/main/assets/press/');
    });
    expect(readme).not.toMatch(/gitlab\.com/i);
  });

  test('should size every tile to full width', () => {
    const widths = [...readme.matchAll(/width="(\d+)%"/g)].map((m) => Number(m[1]));
    expect(widths.length).toBe(TILES.length);
    expect(widths.every((w) => w === 100)).toBe(true);
  });

  test('should not fall back to the retired PNG artifacts', () => {
    expect(readme).not.toMatch(/output\.gif|banner\.png|profile\.svg|card-\d{3}\.(png|svg)/);
  });

  // Tile text lives in SVG loaded through <img>, so alt text is the only
  // accessible and searchable surface.
  describe('alt text coverage', () => {
    const alts = [...readme.matchAll(/alt="([^"]*)"/g)].map((m) => m[1]);

    test('should give every tile alt text', () => {
      expect(alts.length).toBe(TILES.length);
      alts.forEach((a) => expect(a.length).toBeGreaterThan(0));
    });

    test.each(['local-fitness', 'traefik-local-cli', 'claude-skills', 'local-budget'])(
      'should name the %s project',
      (repo) => expect(alts.join(' ')).toContain(repo),
    );

    test.each(['MCP', 'Claude Code', 'Flask', 'Docker', 'SQLite'])(
      'should name the %s technology',
      (tech) => expect(alts.join(' ')).toContain(tech),
    );

    test('should describe each card in prose, not just a label', () => {
      const cardAlts = alts.filter((a) => /^No\. \d{3}/.test(a));
      expect(cardAlts.length).toBe(4);
      cardAlts.forEach((a) => {
        expect(a.length).toBeGreaterThan(80);
        expect(a).toMatch(/Built with .+\./);
      });
    });

    test('should name Nate, his role, and both contacts', () => {
      const all = alts.join(' ');
      expect(all).toMatch(/Nate Swenson/);
      expect(all).toMatch(/Senior DevOps Engineer/);
      expect(all).toMatch(/natejswenson\.com/);
      expect(all).toMatch(/linkedin\.com\/in\/natejswenson/);
    });
  });
});

describe('PRESS tiles — brand compliance', () => {
  const svgs = TILES.map((t) => ({ ...t, svg: read(`assets/press/${t.name}.svg`) }));

  test.each(svgs)('$name should be a self-contained SVG', ({ svg }) => {
    expect(svg).toMatch(/^<svg[^>]*xmlns="http:\/\/www\.w3\.org\/2000\/svg"/);
    expect(svg).toMatch(/<\/svg>$/);
  });

  // An SVG in an <img> is an isolated context that cannot fetch anything.
  // Any external reference renders as a fallback face or not at all.
  test.each(svgs)('$name should reference no external resources', ({ svg }) => {
    expect(svg.match(/(?:href|src|url)\(?["']?https?:\/\//g) || []).toEqual([]);
  });

  test.each(svgs)('$name should embed its faces as woff2 data URIs', ({ svg }) => {
    const faces = svg.match(/@font-face\{font-family:'([^']+)'/g) || [];
    expect(faces.length).toBeGreaterThan(0);
    expect((svg.match(/data:font\/woff2;base64,/g) || []).length).toBe(faces.length);
  });

  test.each(svgs)('$name should style with real CSS', ({ svg }) => {
    expect(svg).toMatch(/<style>/);
  });

  test.each(svgs)('$name should carry an aria-label', ({ svg }) => {
    const m = svg.match(/aria-label="([^"]+)"/);
    expect(m).not.toBeNull();
    expect(m[1].length).toBeGreaterThan(20);
  });

  test.each(svgs)('$name should sit on the canonical paper token', ({ svg }) => {
    expect(svg).toContain('#F5F0E6');
  });

  test.each(svgs)('$name should use no retired-palette color', ({ svg }) => {
    expect(svg).not.toMatch(/df0024|f3c300|00ab9f|2e6db4/i);
  });

  // The accent law: orange is a signature, not a scheme. A card spends it
  // once, on its ledger numeral. Counted as drawn elements rather than hex
  // occurrences, so a stylesheet rule is not mistaken for an ink mark.
  test.each(svgs.filter((s) => s.name.startsWith('row')))(
    '$name should spend the accent on exactly one element',
    ({ svg }) => {
      const marks = svg.match(/<(?:text|tspan)[^>]*class="[^"]*(?:accent|cardno)[^"]*"/g) || [];
      expect(marks.length).toBe(1);
    },
  );

  test('the masthead should hold the accent to the stamp, numeral, and pivot', () => {
    const svg = svgs.find((s) => s.name === 'masthead').svg;
    const marks = svg.match(/<(?:text|tspan)[^>]*class="[^"]*(?:accent|stamp)[^"]*"/g) || [];
    expect(marks.length).toBe(3);
  });

  test('the whole page should stay small enough to load fast', () => {
    const kb = svgs.reduce((n, s) => n + Buffer.byteLength(s.svg, 'utf8'), 0) / 1024;
    expect(kb).toBeLessThan(200);
  });

  test('should carry no emoji anywhere, since PRESS is typographic', () => {
    const all = svgs.map((s) => s.svg).join('');
    // U+FE0F is a variation selector: it COMBINES with the preceding character,
    // so inside a character class it silently means "the selector on its own"
    // rather than "an emoji-presentation glyph". Alternation says the same
    // thing without misleading anyone (and satisfies no-misleading-character-class).
    const emoji = /[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]|\u{FE0F}/gu;
    expect(all.match(emoji)).toBeNull();
  });

  test('should no longer feature the retired llm-token-calculator entry', () => {
    expect(svgs.map((s) => s.svg).join('')).not.toMatch(/llm-token-calculator/);
  });
});
