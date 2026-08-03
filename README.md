# Notes & Work — personal site

A tiny static site generator: notes, projects, and your CV are all
just PDFs you drop into folders, and it builds a clean, tab-navigated,
bilingual website around them. No CMS, no database, no build service
to configure — just Python and files.

## How it's organized

```
content/
  about.en.md / about.fr.md   ← Home tab intro, one per language
  cv.en.md / cv.fr.md         ← CV page content, one per language
  cv.pdf                      ← downloadable CV PDF
  images/                     ← photos referenced from about.*.md
  notes/
    math/*.pdf                  ← drop math note PDFs here
    physics/*.pdf                ← drop physics note PDFs here
  projects/
    math/*.pdf                  ← drop math project PDFs here
    physics/*.pdf                ← drop physics project PDFs here
  music/
    recordings.yaml              ← favorite recordings (title, performer, cover, link)
    concerts.csv                 ← concerts attended (date, program, venue)
    covers/*.jpg                 ← album cover images referenced from recordings.yaml

templates/               ← page layouts (Jinja2) — edit rarely
static/css/style.css     ← all styling lives here (black, formal theme)
build.py                 ← the generator — run this after any edit
docs/                    ← GENERATED — this is what gets published, don't hand-edit
```

The site has five tabs: **Home** (about), **CV**, **Mathematics**,
**Physics**, and **Music**. Each subject tab shows that subject's
Notes and Projects together, in that order — everything opens as a
PDF in a new tab.

## Language toggle (English / French)

The whole site builds twice — English at the root, French under `/fr/`
— with an EN/FR switcher in the top-right of the header that links
each page to its counterpart in the other language.

What's bilingual vs. not:
- **Site chrome** (tab names, section headings, buttons, empty-state
  messages): fully translated. Edit the `STRINGS` dict near the top of
  `build.py` to change wording in either language.
- **About**: real separate content per language —
  `content/about.en.md` / `content/about.fr.md`. Edit each
  independently.
- **Notes, Projects, and the CV**: all PDFs, and *not*
  auto-translated — they show up identically in both languages. Only
  the page chrome around them (header, tabs, footer) switches.

To add a third language later, duplicate a language block in
`STRINGS`, add `about.<code>.md`, and add `"<code>"` to the `LANGS`
list — the rest of the build handles it automatically.

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

Projects work exactly like notes — just PDFs, same filename pattern.

1. Drop a `.pdf` into `content/projects/math/` or
   `content/projects/physics/`, optionally named with a leading date:

   ```
   content/projects/physics/2026-09-01_Coupled-Oscillator-Simulation.pdf
   ```

2. Run `python3 build.py` — it appears under "Projects" on the
   matching subject tab, opening as a PDF in a new tab.

## Editing About

Edit `content/about.en.md` and `content/about.fr.md` directly and
rebuild. Fill in the `[bracketed placeholders]` with your real info —
these are plain Markdown files.

## Replacing the CV

Just overwrite `content/cv.pdf` with your own PDF (export/print your
résumé, or compile your own LaTeX to PDF) and run `python3 build.py`.
The CV tab shows the full content plus a "Download as PDF" link.
Edit `content/cv.en.md` / `content/cv.fr.md` to change the on-page
text itself (separate from the downloadable PDF).

## Adding music content

**Favorite recordings** — edit `content/music/recordings.yaml`:

```yaml
- title: "Goldberg Variations, BWV 988"
  performer: "Glenn Gould (1981 recording)"
  cover: covers/goldberg.jpg
  link: "https://open.spotify.com/..."
```

Drop the cover image into `content/music/covers/`, matching the path
you used above, then run `python3 build.py`.

**Concerts attended** — edit `content/music/concerts.csv`. This is a
plain spreadsheet file: open it in Excel, Numbers, or Google Sheets,
keep the same three column headers (`date`, `program`, `venue`), and
add a row per concert — this is the easiest way to bulk-add all 100+
at once rather than editing by hand. Use `YYYY-MM-DD` for dates so
they sort correctly and group by year. Save/export back to CSV format
when done, then run `python3 build.py`.

Recordings and concerts aren't translated between languages (same
policy as Notes/Projects/CV) — they show up identically on both the
English and French Music tab.

## Adding photos with captions

Put an image file in `content/images/`, then reference it from any
Markdown content (currently just `about.en.md` / `about.fr.md`) with:

```html
<figure class="photo">
  <img src="images/yourphoto.jpg" alt="Description">
  <figcaption>Your caption here.</figcaption>
</figure>
```

Use `class="photo float-right"` instead to float it beside a
paragraph on wide screens (it stacks full-width automatically on
mobile). A placeholder photo and caption are already wired up in
`about.en.md` / `about.fr.md` — just swap `content/images/profile.jpg`
for your own photo of the same filename, or update the `src` path.

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
