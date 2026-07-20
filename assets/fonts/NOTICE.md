# Vendored brand fonts

These are the three PRESS typographic voices, used only by
`generate_banner.py` to render `banner.png`. They are build-time assets;
nothing here is served to a browser.

| File | Voice | Upstream |
|---|---|---|
| `Inter-Black.ttf` | Display, structure (headline, stamp) | [Inter](https://github.com/rsms/inter) |
| `Inter-Bold.ttf` | Display, labels (eyebrow, colophon) | [Inter](https://github.com/rsms/inter) |
| `IBMPlexSerif-Italic.ttf` | Serif, meaning (standfirst, tagline) | [IBM Plex](https://github.com/IBM/plex) |
| `IBMPlexMono-Regular.ttf` | Mono, data (the url) | [IBM Plex](https://github.com/IBM/plex) |

Copied from `natejswenson.io/src/assets/og/`, which uses the same faces for
its OG cards, so the banner and the site's social cards render identically.

## License

Both families are licensed under the **SIL Open Font License 1.1**.

- Inter — Copyright (c) 2016 The Inter Project Authors
- IBM Plex — Copyright (c) 2017 IBM Corp.

Full license text: <https://openfontlicense.org/open-font-license-official-text/>

Note: these are subset builds and do not carry every Unicode codepoint. In
particular neither Inter file includes U+00B7 (`·`) or U+2022 (`•`) — both
render as tofu. `generate_banner.py` draws the eyebrow separator as a small
ink square for this reason.
