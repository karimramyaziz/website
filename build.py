#!/usr/bin/env python3
"""
Static site generator for a math/physics notes site — now bilingual (EN/FR).

Usage:
    python3 build.py

Site structure: 4 tabs — Home, CV, Mathematics, Physics — built TWICE,
once at the site root (English, the default) and once under /fr/
(French). A language toggle in the header links each page to its
counterpart in the other language.

WHAT'S TRANSLATED vs NOT:
  - Site chrome (tab names, headings, buttons, empty states): fully
    bilingual, edit the STRINGS dict below.
  - About / CV: separate source files per language — edit both
    content/about.en.md & content/about.fr.md (same for cv).
  - Notes (PDFs) and Project write-ups: NOT auto-translated. They show
    up identically regardless of language, since translating your
    actual coursework isn't something to fake. Only the page chrome
    around them switches language.

NOTES ARE JUST PDFs. To add a new note:
  1. Drop a .pdf file into content/notes/math/ or content/notes/physics/
  2. (Optional) Name it like "2026-08-01_Quantum-Tunneling.pdf" — the
     leading date and the dashes-to-spaces title are read automatically.
  3. Run: python3 build.py

PROJECTS are Markdown. Add a .md file to content/projects/math/ or
content/projects/physics/ with a frontmatter block (title, date,
summary, tags).
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
    "name": "Notes & Work",
    "description": "Course notes, research, and projects in mathematics and physics.",
}

SUBJECTS = [
    {"slug": "math", "prefix": "M"},
    {"slug": "physics", "prefix": "P"},
]

STRINGS = {
    "en": {
        "lang_label": "EN",
        "other_lang_label": "FR",
        "site_tagline": "math + physics — Boston University",
        "home": "Home", "cv": "CV", "math_tab": "Mathematics", "physics_tab": "Physics",
        "subject_label": {"math": "Mathematics", "physics": "Physics"},
        "subject_desc": {
            "math": "Course notes and projects from my math coursework and independent study.",
            "physics": "Course notes and projects from my physics coursework and independent study.",
        },
        "notes_heading": "Notes",
        "projects_heading": "Projects",
        "recent_notes": "Recent notes",
        "boston_line": "Boston University · Mathematics & Physics",
        "cv_eyebrow": "Curriculum Vitae",
        "no_notes": "No notes posted yet — drop a PDF into content/notes/{slug}/ and rebuild.",
        "no_projects": "No projects posted yet — add a .md file to content/projects/{slug}/ and rebuild.",
        "no_notes_home": "No notes posted yet — drop a PDF into content/notes/ and rebuild.",
        "footer_built": "built with a hand-rolled markdown/PDF site generator",
        "footer_school": "Boston University",
        "project_word": "project",
    },
    "fr": {
        "lang_label": "FR",
        "other_lang_label": "EN",
        "site_tagline": "maths + physique — Université de Boston",
        "home": "Accueil", "cv": "CV", "math_tab": "Mathématiques", "physics_tab": "Physique",
        "subject_label": {"math": "Mathématiques", "physics": "Physique"},
        "subject_desc": {
            "math": "Notes de cours et projets issus de mes études de mathématiques.",
            "physics": "Notes de cours et projets issus de mes études de physique.",
        },
        "notes_heading": "Notes",
        "projects_heading": "Projets",
        "recent_notes": "Notes récentes",
        "boston_line": "Université de Boston · Mathématiques et physique",
        "cv_eyebrow": "Curriculum Vitae",
        "no_notes": "Aucune note pour l'instant — ajoutez un PDF dans content/notes/{slug}/ et relancez la génération.",
        "no_projects": "Aucun projet pour l'instant — ajoutez un fichier .md dans content/projects/{slug}/ et relancez la génération.",
        "no_notes_home": "Aucune note pour l'instant — ajoutez un PDF dans content/notes/ et relancez la génération.",
        "footer_built": "généré avec un petit générateur de site Markdown/PDF",
        "footer_school": "Université de Boston",
        "project_word": "projet",
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


def read_pdf_notes(folder):
    notes = []
    if not os.path.isdir(folder):
        return notes
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
        notes.append({
            "fname": fname, "slug": title_slug, "title": title_from_slug(title_slug),
            "date_obj": date_obj,
            "date": date_obj.strftime("%b %-d, %Y") if date_obj else "",
        })
    notes.sort(key=lambda n: (n["date_obj"] is None, n["date_obj"] or datetime.min, n["title"]), reverse=True)
    return notes


def read_md_posts(folder):
    posts = []
    if not os.path.isdir(folder):
        return posts
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(folder, fname)
        post = frontmatter.load(path)
        slug = os.path.splitext(fname)[0]
        date_raw = post.get("date", "")
        try:
            date_obj = datetime.strptime(str(date_raw), "%Y-%m-%d")
        except ValueError:
            date_obj = datetime.min
        posts.append({
            "slug": slug, "title": post.get("title", slug), "date_obj": date_obj,
            "date": date_obj.strftime("%b %-d, %Y") if date_obj != datetime.min else "",
            "summary": post.get("summary", ""), "tags": post.get("tags", []) or [],
            "body_html": render_md(post.content),
        })
    posts.sort(key=lambda p: p["date_obj"], reverse=True)
    return posts


def write(path, html):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def href(out_path, target_abs_path):
    """Relative URL from an output file to another absolute path under docs/."""
    return os.path.relpath(target_abs_path, start=os.path.dirname(out_path))


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(STATIC, os.path.join(OUT, "static"))

    year = datetime.now().year

    # ---- notes: PDFs, language-independent, copied once ----
    notes_by_subject = {}
    for subj in SUBJECTS:
        slug, prefix = subj["slug"], subj["prefix"]
        notes = read_pdf_notes(os.path.join(CONTENT, "notes", slug))
        for i, n in enumerate(notes, start=1):
            n["num"] = f"§{prefix}{len(notes) - i + 1}"
            n["abs_path"] = os.path.join(OUT, "notes", slug, n["fname"])
            src = os.path.join(CONTENT, "notes", slug, n["fname"])
            os.makedirs(os.path.dirname(n["abs_path"]), exist_ok=True)
            shutil.copy2(src, n["abs_path"])
        notes_by_subject[slug] = notes

    # ---- projects: Markdown, language-independent content, per-language chrome ----
    projects_by_subject = {}
    for subj in SUBJECTS:
        slug, prefix = subj["slug"], subj["prefix"]
        projects = read_md_posts(os.path.join(CONTENT, "projects", slug))
        for i, p in enumerate(projects, start=1):
            p["num"] = f"§{prefix}R{len(projects) - i + 1}"
            p["rel_page"] = f"projects/{slug}/{p['slug']}.html"
        projects_by_subject[slug] = projects

    def base_ctx(out_path, lang, active, rel_page, page_title="", page_description=""):
        S = STRINGS[lang]
        out_root = OUT_ROOT[lang]
        other_lang = "fr" if lang == "en" else "en"
        other_root = OUT_ROOT[other_lang]
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

        # ---- subject tab pages (Mathematics / Physics) ----
        for subj in SUBJECTS:
            slug = subj["slug"]
            rel_page = f"{slug}.html"
            out_path = os.path.join(out_root, rel_page)
            label = S["subject_label"][slug]

            notes = [{
                "num": n["num"], "title": n["title"], "date": n["date"],
                "href": href(out_path, n["abs_path"]),
            } for n in notes_by_subject[slug]]

            project_items = []
            for p in projects_by_subject[slug]:
                p_out_path = os.path.join(out_root, p["rel_page"])
                project_items.append({
                    "num": p["num"], "title": p["title"], "sub": p["summary"], "date": p["date"],
                    "href": href(out_path, p_out_path),
                })

            ctx = base_ctx(out_path, lang, slug, rel_page, page_title=label, page_description=S["subject_desc"][slug])
            ctx.update({
                "eyebrow": f"§{'3' if slug == 'math' else '4'} — {label}",
                "subject_name": label,
                "subject_slug": slug,
                "subject_description": S["subject_desc"][slug],
                "notes": notes,
                "projects": project_items,
                "no_notes_msg": S["no_notes"].format(slug=slug),
                "no_projects_msg": S["no_projects"].format(slug=slug),
            })
            write(out_path, env.get_template("subject.html").render(**ctx))

            # ---- individual project detail pages ----
            for p in projects_by_subject[slug]:
                p_out_path = os.path.join(out_root, p["rel_page"])
                ctx = base_ctx(p_out_path, lang, slug, p["rel_page"], page_title=p["title"], page_description=p["summary"])
                ctx.update({
                    "eyebrow": f"{p['num']} — {label} {S['project_word']}",
                    "title": p["title"], "summary": p["summary"], "body_html": p["body_html"],
                })
                write(p_out_path, env.get_template("page.html").render(**ctx))

        # ---- CV ----
        cv_path = os.path.join(CONTENT, f"cv.{lang}.md")
        cv_post = frontmatter.load(cv_path) if os.path.exists(cv_path) else frontmatter.loads("")
        cv_out = os.path.join(out_root, "cv.html")
        ctx = base_ctx(cv_out, lang, "cv", "cv.html", page_title="CV")
        ctx.update({
            "eyebrow": f"§2 — {S['cv_eyebrow']}",
            "title": cv_post.get("title", "CV"),
            "summary": cv_post.get("summary", ""),
            "body_html": render_md(cv_post.content),
        })
        write(cv_out, env.get_template("page.html").render(**ctx))

        # ---- Home ----
        about_path = os.path.join(CONTENT, f"about.{lang}.md")
        about_post = frontmatter.load(about_path) if os.path.exists(about_path) else frontmatter.loads("")
        index_out = os.path.join(out_root, "index.html")

        all_notes_flat = []
        for subj in SUBJECTS:
            for n in notes_by_subject[subj["slug"]]:
                all_notes_flat.append((subj["slug"], n))
        all_notes_flat.sort(key=lambda t: (t[1]["date_obj"] is None, t[1]["date_obj"] or datetime.min), reverse=True)

        recent = [{
            "num": n["num"], "title": n["title"], "date": n["date"],
            "subject_label": S["subject_label"][slug],
            "href": href(index_out, n["abs_path"]),
        } for slug, n in all_notes_flat[:6]]

        ctx = base_ctx(index_out, lang, "home", "index.html", page_title=S["home"])
        ctx.update({
            "about_title": about_post.get("title", "About"),
            "about_html": render_md(about_post.content),
            "recent_notes": recent,
        })
        write(index_out, env.get_template("index.html").render(**ctx))

    total_notes = sum(len(v) for v in notes_by_subject.values())
    total_projects = sum(len(v) for v in projects_by_subject.values())
    print(f"Built site (EN + FR): {total_notes} PDF notes, {total_projects} projects → {OUT}/")


if __name__ == "__main__":
    build()
