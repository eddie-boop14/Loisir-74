#!/usr/bin/env python3
"""inject_sister_home.py — the "L'autre département" card on the 12 homepages.

WHY A CARD AND NOT A LINE
  loisirs73.fr presents the 74 with a full card before its footer: a kicker
  ("L'AUTRE DÉPARTEMENT"), the sibling's name and département, one editorial
  sentence stating the shared standard, and an "Ouvrir loisirs74.fr" button.
  The first version of this script rendered a one-line footer mention — which
  the owner had explicitly ruled out ("not a one-line footer job") and rightly
  sent back. This is the mirror of the 73's treatment, on the 74.

  The fiche pages keep their one-line footer mention (build_lieu_page's
  sister_link_html — that IS the right weight on 5,208 interior pages);
  the homepage gets the full card.

WHAT IT RENDERS, per homepage, localized (12 languages)

      [icon]  L'AUTRE DÉPARTEMENT
              Loisirs 73 · Savoie
              Même éditeur, même règle : chaque fait vérifié auprès d'une
              source officielle… Passez la frontière départementale.
                                              [ Ouvrir loisirs73.fr → ]

  The body sentence is the 73's own editorial text mirrored back; the six
  facts-language versions came through the DeepL flow (2026-08-16, FR
  source), same as the station-route strings. The icon is the 73's real
  app icon, SELF-HOSTED at /img/loisirs73-icon.png — never hotlinked.

  Colors are locked hex, no CSS vars: cream card (#fdfaf3) with dark text,
  deep-canard button (#14333a) with light text. The homepage's lower zone
  renders dark and its cards render cream in every mode the owner's phone
  has produced — this card behaves exactly like the site's own cards, and
  a var-driven color in this zone has been invisible twice already.

CONFIG-DRIVEN, BOTH WAYS
  siteconfig.SISTER present → card inserted or repaired (fenced, idempotent).
  siteconfig.SISTER absent  → card removed. One flip arms every surface,
  one removal disarms every surface.

Usage:
    python3 scripts/inject_sister_home.py            # report, writes nothing
    python3 scripts/inject_sister_home.py --apply

2026 · Bleu canard édition · Edmaster & Claudius 🦆
"""
import argparse
import html as html_lib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import siteconfig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MARK_A, MARK_B = "<!--sister-home:start-->", "<!--sister-home:end-->"
FENCE_RE = re.compile(re.escape(MARK_A) + r".*?" + re.escape(MARK_B) + r"\n?", re.S)
ICON = "/img/loisirs73-icon.png"

RTL = {"ar", "he"}

# kicker / body / cta. fr = the 73's editorial text mirrored verbatim;
# en/de/it/es/nl authored against it; pl/pt/cs/ar/he/ja via DeepL (FR source,
# free API, 2026-08-16) — same reviewed-flow as the station-route strings.
COPY = {
    "fr": ("L'autre département",
           "Même éditeur, même règle : chaque fait vérifié auprès d'une source "
           "officielle, et les contradictions affichées plutôt qu'arbitrées. "
           "Passez la frontière départementale.",
           "Ouvrir loisirs73.fr"),
    "en": ("The other département",
           "Same publisher, same rule: every fact checked against an official "
           "source, and contradictions shown rather than settled. Cross the "
           "departmental border.",
           "Open loisirs73.fr"),
    "de": ("Das andere Departement",
           "Gleicher Herausgeber, gleiche Regel: jeder Fakt an einer "
           "offiziellen Quelle geprüft, Widersprüche werden angezeigt statt "
           "entschieden. Überqueren Sie die Departementsgrenze.",
           "loisirs73.fr öffnen"),
    "it": ("L'altro dipartimento",
           "Stesso editore, stessa regola: ogni fatto verificato su una fonte "
           "ufficiale, e le contraddizioni mostrate anziché arbitrate. "
           "Attraversate il confine dipartimentale.",
           "Apri loisirs73.fr"),
    "es": ("El otro departamento",
           "Mismo editor, misma regla: cada dato verificado con una fuente "
           "oficial, y las contradicciones se muestran en lugar de "
           "arbitrarse. Cruza la frontera departamental.",
           "Abrir loisirs73.fr"),
    "nl": ("Het andere departement",
           "Zelfde uitgever, zelfde regel: elk feit gecontroleerd bij een "
           "officiële bron, en tegenstrijdigheden worden getoond in plaats "
           "van beslecht. Steek de departementsgrens over.",
           "Open loisirs73.fr"),
    "pl": ("Inny departament",
           "Ten sam wydawca, te same zasady: każda informacja zweryfikowana "
           "w oficjalnym źródle, a sprzeczności przedstawiane wprost, a nie "
           "rozstrzygane. Przekrocz granicę departamentu.",
           "Otwórz stronę loisirs73.fr"),
    "pt": ("O outro departamento",
           "A mesma editora, a mesma regra: cada facto é verificado junto de "
           "uma fonte oficial e as contradições são apresentadas em vez de "
           "serem resolvidas. Atravesse a fronteira departamental.",
           "Aceda a loisirs73.fr"),
    "cs": ("Jiný departement",
           "Stejný vydavatel, stejná zásada: každá informace je ověřena u "
           "oficiálního zdroje a rozpory jsou uvedeny, nikoli zamlčovány. "
           "Překročte hranici departementu.",
           "Otevřít loisirs73.fr"),
    "ar": ("المقاطعة الأخرى",
           "نفس الناشر، نفس القاعدة: يتم التحقق من كل حقيقة من مصدر رسمي، "
           "ويتم عرض التناقضات بدلاً من التغاضي عنها. اعبروا حدود المقاطعة.",
           "افتحوا موقع loisirs73.fr"),
    "he": ("המחוז האחר",
           'אותו מו"ל, אותו כלל: כל עובדה נבדקת מול מקור רשמי, והסתירות '
           "מוצגות כפי שהן, במקום שיישבו. חצו את גבול המחוז.",
           "היכנסו לאתר loisirs73.fr"),
    "ja": ("もう一つの県",
           "同じ出版社、同じルール：すべての事実は公式情報源で確認され、"
           "矛盾点は恣意的に調整するのではなく、そのまま掲載されています。"
           "県の境界を越えてみましょう。",
           "loisirs73.frを開く"),
}


# "what you'll find" count frame — {count} swapped in at render. fr authored;
# en/de/it/es/nl authored against it; pl/pt/cs/ar/he/ja via DeepL (FR source,
# 2026-08-16). pl/cs plural forms agree with counts ending 2-4 (73 does);
# revisit if the sibling's count moves into another plural class.
FRAME = {
    "fr": "{count} lieux vérifiés en Savoie",
    "en": "{count} verified places in Savoie",
    "de": "{count} geprüfte Orte in Savoie",
    "it": "{count} luoghi verificati in Savoia",
    "es": "{count} lugares verificados en Saboya",
    "nl": "{count} geverifieerde plekken in Savoie",
    "pl": "{count} sprawdzone miejsca w Sabaudii",
    "pt": "{count} locais inspecionados na Saboia",
    "cs": "{count} prověřených míst v Savojsku",
    "ar": "{count} موقعاً تم فحصها في سافوا",
    "he": "{count} אתרים שנבדקו בסבואה",
    "ja": "サヴォワ県で調査済みの{count}カ所",
}


def esc(s):
    return html_lib.escape(str(s), quote=True)


def homepages():
    yield "fr", ROOT / "index.html"
    for sub in sorted(ROOT.iterdir()):
        if sub.is_dir() and len(sub.name) == 2 and (sub / "index.html").exists():
            yield sub.name, sub / "index.html"


def card_for(lang, sis):
    kicker, body, cta = COPY.get(lang) or COPY["fr"]
    arrow = "←" if lang in RTL else "→"
    dir_attr = ' dir="rtl"' if lang in RTL else ""
    title = f'{sis["name"]} · {sis.get("dept", "")}'.rstrip(" ·")
    # the "top picks" line: what the reader will find, before how it is served.
    what_html = ""
    count, highlights = sis.get("count"), sis.get("highlights") or []
    if count and highlights:
        frame = (FRAME.get(lang) or FRAME["fr"]).replace("{count}", str(count))
        colon = " : " if lang == "fr" else ("：" if lang == "ja" else ": ")
        names = " · ".join(esc(h) for h in highlights)
        what_html = (f'<p style="margin:0 0 7px;color:#1c1814;font-weight:600;line-height:1.5">'
                     f'{esc(frame)}{colon}{names}…</p>')
    icon_html = ""
    if (ROOT / ICON.lstrip("/")).is_file():
        icon_html = (f'<img src="{ICON}" alt="" width="56" height="56" loading="lazy" '
                     'decoding="async" style="border-radius:14px;flex-shrink:0">')
    return (
        f'{MARK_A}<section class="sister-dept"{dir_attr} aria-labelledby="sister-dept-h" '
        'style="position:relative;z-index:2;max-width:1080px;margin:30px auto;padding:0 18px">'
        '<div style="background:#fdfaf3;border:1px solid #d9cdb3;border-radius:18px;'
        'padding:clamp(18px,4vw,26px);display:flex;flex-wrap:wrap;gap:18px;align-items:center;'
        'box-shadow:0 10px 30px rgba(28,24,20,.12)">'
        f'{icon_html}'
        '<div style="flex:1 1 320px;min-width:0">'
        f'<p style="margin:0 0 4px;font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;'
        f'color:#7a6b58;font-weight:700">{esc(kicker)}</p>'
        f'<h2 id="sister-dept-h" style="margin:0 0 8px;font-size:clamp(1.15rem,3vw,1.45rem);'
        f'color:#1c1814">{esc(title)}</h2>'
        f'{what_html}'
        f'<p style="margin:0;color:#3d342a;line-height:1.55">{esc(body)}</p>'
        '</div>'
        f'<a href="{esc(sis["url"])}" rel="nofollow noopener" style="display:inline-flex;align-items:center;'
        'gap:.5rem;background:#14333a;color:#f4ede0;font-weight:600;text-decoration:none;'
        f'padding:.78rem 1.25rem;border-radius:999px;flex-shrink:0">{esc(cta)} {arrow}</a>'
        f'</div></section>{MARK_B}'
    )


def main():
    ap = argparse.ArgumentParser(description="Sister-département card on the homepages.")
    ap.add_argument("--apply", action="store_true", help="write changes (default: report only)")
    args = ap.parse_args()

    sis = getattr(siteconfig, "SISTER", None)
    armed = bool(sis and sis.get("url") and sis.get("name"))

    changed = removed = ok = no_anchor = 0
    for lang, page in homepages():
        html = page.read_text(encoding="utf-8")
        has = FENCE_RE.search(html)

        if not armed:
            if has:
                removed += 1
                if args.apply:
                    page.write_text(FENCE_RE.sub("", html), encoding="utf-8")
            continue

        want = card_for(lang, sis)
        # sweep any previous fence wherever it sits (v1 lived inside
        # foot-bottom), then insert fresh directly before the footer — the
        # 73's card occupies exactly that slot.
        stripped = FENCE_RE.sub("", html)
        idx = stripped.rfind('<footer class="site"')
        if idx == -1:
            no_anchor += 1
            continue
        new = stripped[:idx] + want + "\n" + stripped[idx:]
        if new == html:
            ok += 1
            continue
        changed += 1
        if args.apply:
            page.write_text(new, encoding="utf-8")

    verb = "" if args.apply else "would "
    state = "armed" if armed else "DISARMED (no sister block in site.config.json)"
    print(f"inject_sister_home [{state}]: {verb}write {changed} card(s) · already correct {ok} "
          f"· {verb}remove {removed}")
    if no_anchor:
        print(f"  ⚑ no <footer class=\"site\"> anchor on {no_anchor} homepage(s) — not injected")
    if not args.apply and (changed or removed):
        print("  report only — re-run with --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
