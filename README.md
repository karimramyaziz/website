# Notes & Work — personal site

A tiny static site generator: notes are just PDFs you drop into a
folder, projects/CV are Markdown, and it builds a clean, tab-navigated
website. No CMS, no database, no build service to configure — just
Python and files.

## How it's organized

```
content/
  about.md              ← Home tab intro / about blurb
  cv.md                 ← your CV, as plain text/markdown
  notes/
    math/*.pdf            ← drop math note PDFs here
    physics/*.pdf         ← drop physics note PDFs here
  projects/
    math/*.md              ← math project write-ups
    physics/*.md            ← physics project write-ups

templates/               ← page layouts (Jinja2) — edit rarely
static/css/style.css     ← all styling lives here
build.py                 ← the generator — run this after any edit
docs/                    ← GENERATED — this is what gets published, don't hand-edit
```

The site has four tabs: **Home** (about + recent notes), **CV**,
**Mathematics**, and **Physics**. Each subject tab shows that
subject's Notes and Projects together, in that order.

## Language toggle (English / French)

The whole site builds twice — English at the root, French under `/fr/`
— with an EN/FR switcher in the top-right of the header that links
each page to its counterpart in the other language.

What's bilingual vs. not:
- **Site chrome** (tab names, section headings, buttons, empty-state
  messages): fully translated. Edit the `STRINGS` dict near the top of
  `build.py` to change wording in either language.
- **About / CV**: real separate content per language —
  `content/about.en.md` / `content/about.fr.md`, and
  `content/cv.en.md` / `content/cv.fr.md`. Edit each independently.
- **Notes (PDFs) and Project write-ups**: *not* auto-translated —
  they show up identically in both languages. Only the page chrome
  around them (header, tabs, footer) switches. If you want a project
  write-up in both languages, you'd need to write both versions
  yourself; ask me if you want help wiring that up.

To add a third language later, duplicate a language block in
`STRINGS`, add `about.<code>.md` / `cv.<code>.md`, and add `"<code>"`
to the `LANGS` list — the rest of the build handles it automatically.

## Adding a new note

Notes are just PDFs. No markdown, no frontmatter required.

1. Drop a `.pdf` file into `content/notes/math/` or
   `content/notes/physics/`.
2. **Optional but recommended:** name it with a leading date so it
   sorts and displays correctly, e.g.:

   ```
   content/notes/physics/2026-08-01_Quantum-Tunneling.pdf
   ```

   The date (`2026-08-01`) and title (`Quantum Tunneling`, from the
   dashes) are parsed straight from the filename. No date prefix?
   That's fine too — it'll just show without a date, sorted after the
   dated ones.

3. Run the build:

   ```
   python3 build.py
   ```

4. Your note now appears automatically on the Mathematics or Physics
   tab (under "Notes") and in the homepage's "recent notes" list.
   Clicking it opens the actual PDF in a new tab — no viewer page to
   generate or maintain.

## Adding a new project

Projects are still Markdown, since write-ups are prose you'll want to
edit in place.

1. Add a `.md` file to `content/projects/math/` or
   `content/projects/physics/`, with a frontmatter block:

   ```markdown
   ---
   title: Simulating Coupled Oscillators
   date: 2026-09-01
   summary: One-line description shown in listings.
   tags: [python, mechanics]
   ---

   Write-up here, in Markdown. Math works too: `$\omega^2 = k/m$`.
   ```

2. Run `python3 build.py` — it appears under "Projects" on the
   matching subject tab.

## Editing About / CV

Just edit `content/about.md` or `content/cv.md` directly and rebuild.
Fill in the `[bracketed placeholders]` with your real info.

## Local preview

From the `site/` folder:

```
python3 -m http.server --directory docs 8000
```

Then open `http://localhost:8000` in a browser.

## One-time setup

You'll need Python 3 and three packages:

```
pip install markdown pyyaml jinja2 python-frontmatter
```

## Publishing for free with GitHub Pages

The easiest way to do this whole thing is with **GitHub Desktop**
(free app, no command line): [desktop.github.com](https://desktop.github.com)

1. Install GitHub Desktop and sign in with your GitHub account.
2. On github.com, create a new empty repository (e.g. `personal-site`) —
   don't add a README, license, or .gitignore.
3. In GitHub Desktop: **File → Clone Repository**, pick the one you
   just made, and choose where to save it on your computer.
4. This creates an empty folder on your computer matching the repo.
   Copy everything from this project (`content`, `templates`, `static`,
   `docs`, `build.py`, `README.md`) into that folder.
5. Back in GitHub Desktop, you'll see all the new files listed on the
   left. Type a summary like "initial site" in the box at the
   bottom left, click **Commit to main**, then click **Push origin**
   at the top.
6. On github.com: **Settings → Pages → Build and deployment → Source:
   Deploy from a branch → Branch: `main`, folder: `/docs`** → Save.
7. Your site goes live at `https://YOUR_USERNAME.github.io/YOUR_REPO/`
   within a minute or two.

From then on, adding a new note is:

1. Drop the PDF into `content/notes/math/` or `content/notes/physics/`
   (in the folder on your computer).
2. Run `python3 build.py` (see setup below).
3. Open GitHub Desktop — it'll show the changed files — type a commit
   message, **Commit to main**, **Push origin**.

That's it — GitHub Pages redeploys automatically on every push, no
dashboard clicking required.

### Command-line alternative

If you're comfortable with a terminal, the same result:

```
git init
git add .
git commit -m "initial site"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Then for each new note: `python3 build.py`, `git add .`,
`git commit -m "..."`, `git push`.

## Customizing

- **Site name/tagline:** edit the `SITE` dict at the top of `build.py`.
- **Colors/fonts:** edit the `:root` variables at the top of
  `static/css/style.css`.
- **Layout:** edit files in `templates/` (Jinja2 syntax — `{{ var }}`
  for values, `{% for %}` for loops).
