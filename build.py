#!/usr/bin/env python3
"""
Static site generator for a math/physics notes site — bilingual (EN/FR),
with notes, projects, and the CV all as plain PDFs.

Usage:
    python3 build.py

WHAT'S TRANSLATED vs NOT:
  - Site chrome (tab names, headings, buttons, empty states): fully
    bilingual — edit the STRINGS dict below.
  - About: separate source files per language — edit both
    content/about.en.md and content/about.fr.md.
  - Notes, Projects, and the CV are all PDFs and are NOT translated —
    they show up identically regardless of language. Only the page
    chrome around them switches.

NOTES & PROJECTS ARE JUST PDFs. To add one:
  1. Drop a .pdf into content/notes/math/, content/notes/physics/,
     content/projects/math/, or content/projects/physics/.
  2. (Optional) Name it like "2026-08-01_Quantum-Tunneling.pdf" — the
     leading date and the dashes-to-spaces title are read automatically.
  3. Run: python3 build.py

CV: replace content/cv.pdf with your own file and rebuild.

PHOTOS WITH CAPTIONS: put an image in content/images/, then reference
it from content/about.en.md (or any markdown file) with:

    <figure class="photo">
      <img src="images/yourphoto.jpg" alt="Description">
      <figcaption>Your caption here.</figcaption>
    </figure>

Add class="photo float-right" instead of class="photo" to float it
beside a paragraph on wide screens.

MUSIC TAB:
  - Favorite recordings: edit content/music/recordings.yaml (title,
    performer, cover image path, link to Spotify/YouTube/etc.). Cover
    images go in content/music/covers/.
  - Concerts attended: edit content/music/concerts.csv (columns:
    date, program, venue). Easiest to bulk-edit in a spreadsheet —
    just keep the same column headers and export back to CSV. Dates
    should be YYYY-MM-DD so they sort and group by year correctly.
"""

import os
import re
import shutil
from datetime import datetime

import frontmatter
import markdown as md
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")
TEMPLATES = os.path.join(ROOT, "templates")
STATIC = os.path.join(ROOT, "static")
OUT = os.path.join(ROOT, "docs")

LANGS = ["en", "fr"]
OUT_ROOT = {"en": OUT, "fr": os.path.join(OUT, "fr")}

SITE = {
    "name": "Karim Aziz",
    "description": "Course notes, research, and projects in mathematics and physics.",
}

SUBJECTS = [
    {"slug": "math", "prefix": "M"},
    {"slug": "physics", "prefix": "P"},
]

STRINGS = {
    "en": {
        "lang_label": "EN", "other_lang_label": "FR",
        "site_tagline": "Boston University",
        "home": "Home", "cv": "CV", "math_tab": "Mathematics", "physics_tab": "Physics", "music_tab": "Music",
        "subject_label": {"math": "Mathematics", "physics": "Physics"},
        "subject_desc": {
            "math": "Course notes and projects from my math coursework and independent study.",
            "physics": "Course notes and projects from my physics coursework and independent study.",
        },
        "notes_heading": "Notes",
        "projects_heading": "Projects",
        "cv_eyebrow": "Curriculum Vitae",
        "cv_title": "CV",
        "cv_open": "Download as PDF",
        "no_notes": "No notes posted yet — drop a PDF into content/notes/{slug}/ and rebuild.",
        "no_projects": "No projects posted yet — drop a PDF into content/projects/{slug}/ and rebuild.",
        "music_eyebrow": "§5 — Music",
        "music_title": "Music",
        "music_desc": "A few favorite recordings, and a running list of concerts I've been to. Compositions and recordings of my own playing are coming eventually.",
        "recordings_heading": "Favorite Recordings",
        "concerts_heading": "Concerts Attended",
        "no_recordings": "No recordings added yet — edit content/music/recordings.yaml and rebuild.",
        "no_concerts": "No concerts added yet — edit content/music/concerts.csv and rebuild.",
        "footer_built": "built with a hand-rolled site generator",
        "footer_school": "Boston University",
    },
    "fr": {
        "lang_label": "FR", "other_lang_label": "EN",
        "site_tagline": "Université de Boston",
        "home": "Accueil", "cv": "CV", "math_tab": "Mathématiques", "physics_tab": "Physique", "music_tab": "Musique",
        "subject_label": {"math": "Mathématiques", "physics": "Physique"},
        "subject_desc": {
            "math": "Notes de cours et projets issus de mes études de mathématiques.",
            "physics": "Notes de cours et projets issus de mes études de physique.",
        },
        "notes_heading": "Notes",
        "projects_heading": "Projets",
        "cv_eyebrow": "Curriculum Vitae",
        "cv_title": "CV",
        "cv_open": "Télécharger en PDF",
        "no_notes": "Aucune note pour l'instant — ajoutez un PDF dans content/notes/{slug}/ et relancez la génération.",
        "no_projects": "Aucun projet pour l'instant — ajoutez un PDF dans content/projects/{slug}/ et relancez la génération.",
        "music_eyebrow": "§5 — Musique",
        "music_title": "Musique",
        "music_desc": "Quelques enregistrements favoris, et une liste des concerts auxquels j'ai assisté. Mes propres compositions et enregistrements arriveront plus tard.",
        "recordings_heading": "Enregistrements favoris",
        "concerts_heading": "Concerts",
        "no_recordings": "Aucun enregistrement pour l'instant — modifiez content/music/recordings.yaml et relancez la génération.",
        "no_concerts": "Aucun concert pour l'instant — modifiez content/music/concerts.csv et relancez la génération.",
        "footer_built": "généré avec un petit générateur de site",
        "footer_school": "Université de Boston",
    },
}

MD_EXTENSIONS = ["extra", "sane_lists", "toc", "codehilite", "smarty"]
env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=False)
DATE_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})[_\-\s]*(.*)$")


def render_md(text):
    return md.markdown(text, extensions=MD_EXTENSIONS)


def title_from_slug(slug):
    words = re.split(r"[_\-]+", slug)
    return " ".join(w if w.isupper() else w.capitalize() for w in words if w)


def read_pdfs(folder):
    """Scan a folder of PDFs, parsing an optional leading YYYY-MM-DD date
    from the filename. Used for both notes and projects."""
    items = []
    if not os.path.isdir(folder):
        return items
    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith(".pdf"):
            continue
        stem = os.path.splitext(fname)[0]
        m = DATE_PREFIX_RE.match(stem)
        if m:
            date_str, rest = m.groups()
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                date_obj = None
            title_slug = rest or stem
        else:
            date_obj = None
            title_slug = stem
        items.append({
            "fname": fname, "slug": title_slug, "title": title_from_slug(title_slug),
            "date_obj": date_obj,
            "date": date_obj.strftime("%b %-d, %Y") if date_obj else "",
        })
    items.sort(key=lambda n: (n["date_obj"] is None, n["date_obj"] or datetime.min, n["title"]), reverse=True)
    return items


def read_recordings(yaml_path, out_covers_dir, content_music_dir):
    """Load favorite recordings from YAML, copy cover images to output."""
    import yaml
    if not os.path.exists(yaml_path):
        return []
    with open(yaml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or []
    items = []
    for entry in data:
        cover_rel = entry.get("cover", "")
        cover_abs = None
        if cover_rel:
            src = os.path.join(content_music_dir, cover_rel)
            if os.path.exists(src):
                dst = os.path.join(out_covers_dir, os.path.basename(cover_rel))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                cover_abs = dst
        items.append({
            "title": entry.get("title", ""),
            "performer": entry.get("performer", ""),
            "link": entry.get("link", ""),
            "cover_abs": cover_abs,
        })
    return items


def read_concerts(csv_path):
    """Load concert list from CSV, sorted most-recent first."""
    import csv as csv_module
    if not os.path.exists(csv_path):
        return []
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv_module.DictReader(f)
        for row in reader:
            date_raw = (row.get("date") or "").strip()
            try:
                date_obj = datetime.strptime(date_raw, "%Y-%m-%d")
            except ValueError:
                date_obj = None
            rows.append({
                "date_obj": date_obj,
                "date": date_obj.strftime("%b %Y") if date_obj else date_raw,
                "year": date_obj.strftime("%Y") if date_obj else "",
                "program": (row.get("program") or "").strip(),
                "venue": (row.get("venue") or "").strip(),
            })
    rows.sort(key=lambda r: (r["date_obj"] is None, r["date_obj"] or datetime.min), reverse=True)
    return rows


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def href(out_path, target_abs_path):
    return os.path.relpath(target_abs_path, start=os.path.dirname(out_path))


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(STATIC, os.path.join(OUT, "static"))
    if os.path.isdir(os.path.join(CONTENT, "images")):
        # Copied into both language roots so a plain "images/x.jpg" path
        # in about.en.md / about.fr.md resolves correctly from either.
        shutil.copytree(os.path.join(CONTENT, "images"), os.path.join(OUT, "images"))
        os.makedirs(OUT_ROOT["fr"], exist_ok=True)
        shutil.copytree(os.path.join(CONTENT, "images"), os.path.join(OUT_ROOT["fr"], "images"))

    year = datetime.now().year

    # ---- notes & projects: PDFs, language-independent, copied once ----
    notes_by_subject = {}
    projects_by_subject = {}
    for subj in SUBJECTS:
        slug, prefix = subj["slug"], subj["prefix"]

        notes = read_pdfs(os.path.join(CONTENT, "notes", slug))
        for i, n in enumerate(notes, start=1):
            n["num"] = f"§{prefix}{len(notes) - i + 1}"
            n["abs_path"] = os.path.join(OUT, "notes", slug, n["fname"])
            src = os.path.join(CONTENT, "notes", slug, n["fname"])
            os.makedirs(os.path.dirname(n["abs_path"]), exist_ok=True)
            shutil.copy2(src, n["abs_path"])
        notes_by_subject[slug] = notes

        projects = read_pdfs(os.path.join(CONTENT, "projects", slug))
        for i, p in enumerate(projects, start=1):
            p["num"] = f"§{prefix}R{len(projects) - i + 1}"
            p["abs_path"] = os.path.join(OUT, "projects", slug, p["fname"])
            src = os.path.join(CONTENT, "projects", slug, p["fname"])
            os.makedirs(os.path.dirname(p["abs_path"]), exist_ok=True)
            shutil.copy2(src, p["abs_path"])
        projects_by_subject[slug] = projects

    # ---- CV PDF: single file, kept only as a download ----
    cv_pdf_src = os.path.join(CONTENT, "cv.pdf")
    cv_pdf_abs_path = os.path.join(OUT, "cv.pdf")
    if os.path.exists(cv_pdf_src):
        shutil.copy2(cv_pdf_src, cv_pdf_abs_path)

    # ---- Music: favorite recordings (YAML + cover images) and concerts (CSV) ----
    music_content_dir = os.path.join(CONTENT, "music")
    recordings = read_recordings(
        os.path.join(music_content_dir, "recordings.yaml"),
        os.path.join(OUT, "music", "covers"),
        music_content_dir,
    )
    concerts = read_concerts(os.path.join(music_content_dir, "concerts.csv"))
    concert_years = []
    seen_years = set()
    for c in concerts:
        y = c["year"] or "Undated"
        if y not in seen_years:
            seen_years.add(y)
            concert_years.append(y)
    concerts_by_year = {y: [c for c in concerts if (c["year"] or "Undated") == y] for y in concert_years}

    def base_ctx(out_path, lang, active, rel_page, page_title="", page_description=""):
        S = STRINGS[lang]
        out_root = OUT_ROOT[lang]
        other_root = OUT_ROOT["fr" if lang == "en" else "en"]
        return {
            "site": SITE, "year": year, "S": S, "lang": lang, "active": active,
            "page_title": page_title, "page_description": page_description or SITE["description"],
            "css_href": href(out_path, os.path.join(OUT, "static", "css", "style.css")),
            "home_href": href(out_path, os.path.join(out_root, "index.html")),
            "cv_href": href(out_path, os.path.join(out_root, "cv.html")),
            "math_href": href(out_path, os.path.join(out_root, "math.html")),
            "physics_href": href(out_path, os.path.join(out_root, "physics.html")),
            "music_href": href(out_path, os.path.join(out_root, "music.html")),
            "toggle_href": href(out_path, os.path.join(other_root, rel_page)),
        }

    for lang in LANGS:
        S = STRINGS[lang]
        out_root = OUT_ROOT[lang]

        # ---- subject tab pages ----
        for subj in SUBJECTS:
            slug = subj["slug"]
            rel_page = f"{slug}.html"
            out_path = os.path.join(out_root, rel_page)
            label = S["subject_label"][slug]

            notes = [{
                "num": n["num"], "title": n["title"], "date": n["date"],
                "href": href(out_path, n["abs_path"]),
            } for n in notes_by_subject[slug]]

            projects = [{
                "num": p["num"], "title": p["title"], "date": p["date"],
                "href": href(out_path, p["abs_path"]),
            } for p in projects_by_subject[slug]]

            ctx = base_ctx(out_path, lang, slug, rel_page, page_title=label, page_description=S["subject_desc"][slug])
            ctx.update({
                "eyebrow": f"§{'3' if slug == 'math' else '4'} — {label}",
                "subject_name": label,
                "subject_description": S["subject_desc"][slug],
                "notes": notes,
                "projects": projects,
                "no_notes_msg": S["no_notes"].format(slug=slug),
                "no_projects_msg": S["no_projects"].format(slug=slug),
            })
            write(out_path, env.get_template("subject.html").render(**ctx))

        # ---- CV ----
        cv_out = os.path.join(out_root, "cv.html")
        cv_md_path = os.path.join(CONTENT, f"cv.{lang}.md")
        cv_body_html = ""
        if os.path.exists(cv_md_path):
            with open(cv_md_path, encoding="utf-8") as f:
                cv_body_html = render_md(f.read())
        ctx = base_ctx(cv_out, lang, "cv", "cv.html", page_title=S["cv_title"])
        ctx.update({
            "eyebrow": f"§2 — {S['cv_eyebrow']}",
            "cv_body_html": cv_body_html,
            "cv_pdf_href": href(cv_out, cv_pdf_abs_path) if os.path.exists(cv_pdf_abs_path) else None,
        })
        write(cv_out, env.get_template("cv.html").render(**ctx))

        # ---- Music ----
        music_out = os.path.join(out_root, "music.html")
        recordings_ctx = [{
            "title": r["title"], "performer": r["performer"], "link": r["link"],
            "cover_href": href(music_out, r["cover_abs"]) if r["cover_abs"] else None,
        } for r in recordings]
        concert_groups = [{
            "year": y,
            "rows": [{"date": c["date"], "program": c["program"], "venue": c["venue"]} for c in concerts_by_year[y]],
        } for y in concert_years]
        ctx = base_ctx(music_out, lang, "music", "music.html", page_title=S["music_title"], page_description=S["music_desc"])
        ctx.update({
            "eyebrow": S["music_eyebrow"],
            "music_description": S["music_desc"],
            "recordings": recordings_ctx,
            "concert_groups": concert_groups,
            "concert_count": len(concerts),
        })
        write(music_out, env.get_template("music.html").render(**ctx))

        # ---- Home ----
        about_path = os.path.join(CONTENT, f"about.{lang}.md")
        about_post = frontmatter.load(about_path) if os.path.exists(about_path) else frontmatter.loads("")
        index_out = os.path.join(out_root, "index.html")

        ctx = base_ctx(index_out, lang, "home", "index.html", page_title=S["home"])
        ctx.update({
            "about_title": about_post.get("title", "About"),
            "about_html": render_md(about_post.content),
        })
        write(index_out, env.get_template("index.html").render(**ctx))

    total_notes = sum(len(v) for v in notes_by_subject.values())
    total_projects = sum(len(v) for v in projects_by_subject.values())
    print(f"Built site (EN + FR): {total_notes} notes, {total_projects} projects, CV → {OUT}/")


if __name__ == "__main__":
    build()
