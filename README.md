# Pablo Piantanida — research website

GitHub-ready source for Pablo Piantanida's academic research website.

## Positioning

The site presents one coherent programme:

1. mathematical foundations of reliable and adaptive AI;
2. adaptive evaluation under limited evidence;
3. resource-aware agentic and collaborative intelligence.

The five public pages are Home, Research, People, Publications, and Projects.

## Local preview

```bash
npm install
npm run build
npm run dev
```

The generated site is written to `dist/`. To validate local links, assets,
anchors, and heading structure:

```bash
python scripts/check.py
```

## Updating content

- Edit page prose in `content/`.
- Update people and projects in `data/people.json` and
  `data/projects.json`.
- Update the BibTeX files and `data/publication-selection.tex`; the build
  regenerates the searchable publication list.
- Use `data/publication-overrides.json` for a verified venue or status that
  should replace a provisional label.

## GitHub Pages

The workflow in `.github/workflows/pages.yml` builds and deploys from
`main`. In the repository settings, set **Pages → Source** to
**GitHub Actions** before merging the review branch.

## Custom domain cutover

Keep the existing site live while reviewing the GitHub Pages URL. Only after
approval:

1. add the verified hostname in **Settings → Pages → Custom domain**;
2. apply GitHub's DNS records at the domain provider;
3. wait for DNS and HTTPS validation;
4. enable **Enforce HTTPS**;
5. retain a rollback record of the previous DNS values until validation is
   complete.

Do not commit credentials or provider tokens.
