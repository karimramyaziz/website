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
        "home": "Home", "cv": "CV", "math_tab": "Mathematics", "physics_tab": "Physics",
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
        "footer_built": "built with a hand-rolled site generator",
        "footer_school": "Boston University",
    },
    "fr": {
        "lang_label": "FR", "other_lang_label": "EN",
        "site_tagline": "Université de Boston",
        "home": "Accueil", "cv": "CV", "math_tab": "Mathématiques", "physics_tab": "Physique",
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
