#!/usr/bin/env python3
"""Intègre un menu hebdomadaire (JSON) dans site-breizhou/index.html.

Usage : python3 outils/integrer-menu.py menus/2026-09-28.json [--date AAAA-MM-JJ]

Le JSON a la forme du bloc #menu-data de la page : titre, debut, fin, note, textures,
jours[] (nom, date, veggie, intro/petit/moyen/grand/geant/gouter, mentions facultatives).

Le script réécrit quatre zones de la page, rien d'autre :
  1. le bloc <script id="menu-data">           (la donnée, lue par le script de la page)
  2. le bloc <!--MENU-->…<!--/MENU-->            (menu du jour rendu, pour l'affichage sans JS)
  3. la table <div class="menu-wrap">…</div>     (menu de la semaine)
  4. le titre #sem-titre et sa note
Le rendu statique dépend de la date du jour (ou --date) : semaine à venir, en cours, ou
dépassée (« menu bientôt en ligne »). Le script de la page refait le même calcul chez le
visiteur, la version statique n'est qu'un point de départ.
Aucune publication : le script ne touche ni à Git ni au réseau.
"""
import json, re, sys, datetime, pathlib

ICI = pathlib.Path(__file__).resolve().parent.parent
PAGE = ICI / "index.html"
VEG = ' <span class="veggie">Veggie</span>'
VIDE = ('<div class="jour-vide"><p class="jd">Le menu de la semaine arrive bientôt.</p>'
        '<p class="jt">Il est affiché ici dès sa publication par la cuisine.</p></div>')

def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def liste(j, k):
    html = "<br>".join(esc(x) for x in j.get(k, []))
    m = (j.get("mentions") or {}).get(k)
    if m:
        html += '<span class="mention">' + esc(m) + "</span>"
    return html

def jour_html(sem, j, avenir):
    rows = "".join(
        "<div><dt>%s<small>%s</small></dt><dd>%s</dd></div>" % (esc(lab), esc(sub), liste(j, k))
        for k, lab, sub in sem["textures"])
    sous = "<b>Menu de la semaine prochaine</b>" if avenir else "<b>Cuisiné à Bréteil</b>"
    return ('<div class="jour-date"><p class="jd">%s%s</p><p class="jt">%s<br>%s</p></div>'
            '<dl class="jour-list">%s</dl>'
            % (esc(j["date"]), VEG if j.get("veggie") else "", sous, esc(sem["titre"]), rows))

def table_html(sem, i_today):
    th = "".join('<th scope="col">%s%s</th>' % (esc(j["nom"]), VEG if j.get("veggie") else "")
                 for j in sem["jours"])
    body = ""
    for k, lab, sub in sem["textures"]:
        body += '<tr><th scope="row">%s<small>%s</small></th>' % (esc(lab), esc(sub))
        for n, j in enumerate(sem["jours"]):
            cls = ' class="today"' if n == i_today else ""
            body += "<td%s>%s</td>" % (cls, liste(j, k))
        body += "</tr>"
    return ('<table class="menu"><thead><tr><th scope="col"><span class="sr">Texture</span></th>%s</tr>'
            '</thead><tbody>%s</tbody></table>' % (th, body))

def remplacer(s, motif, nouveau, nom):
    s2, n = re.subn(motif, lambda m: nouveau, s, count=1, flags=re.S)
    if n != 1:
        sys.exit("zone introuvable dans index.html : " + nom)
    return s2

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sem = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    today = datetime.date.today()
    if "--date" in sys.argv:
        today = datetime.date.fromisoformat(sys.argv[sys.argv.index("--date") + 1])
    iso = today.isoformat()
    for cle in ("titre", "debut", "fin", "textures", "jours"):
        if cle not in sem:
            sys.exit("clé manquante dans le JSON : " + cle)
    if len(sem["jours"]) != 5:
        sys.exit("il faut 5 jours, trouvé %d" % len(sem["jours"]))
    for j in sem["jours"]:
        for k, _, _ in sem["textures"]:
            if not j.get(k):
                sys.exit("%s : texture « %s » vide" % (j["nom"], k))

    depasse = iso > sem["fin"]
    avenir = iso < sem["debut"]
    wd = today.weekday()  # 0 lundi … 6 dimanche
    i = 0 if avenir else (wd if wd <= 4 else 4)

    s = PAGE.read_text(encoding="utf-8")
    donnee = json.dumps(sem, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    s = remplacer(s, r'<script type="application/json" id="menu-data">.*?</script>',
                  '<script type="application/json" id="menu-data">' + donnee + '</script>', "menu-data")
    jour = VIDE if depasse else jour_html(sem, sem["jours"][i], avenir)
    s = remplacer(s, r'<!--MENU-->.*?<!--/MENU-->', "<!--MENU-->" + jour + "<!--/MENU-->", "menu du jour")
    cache = " hidden" if depasse else ""
    s = remplacer(s, r'<div class="sem-head"[^>]*>', '<div class="sem-head"%s>' % cache, "sem-head")
    s = remplacer(s, r'<h3 id="sem-titre">.*?</h3>', '<h3 id="sem-titre">%s</h3>' % esc(sem["titre"]), "titre")
    s = remplacer(s, r'<p id="sem-note">.*?</p>',
                  '<p id="sem-note">Toutes les textures, du lundi au vendredi. %s</p>' % esc(sem.get("note", "")), "note")
    s = remplacer(s, r'<div class="menu-wrap"[^>]*>.*?</table></div>',
                  '<div class="menu-wrap"%s>%s</div>' % (cache, table_html(sem, None if (avenir or depasse) else i)), "tableau")
    PAGE.write_text(s, encoding="utf-8")
    etat = "dépassée" if depasse else ("à venir" if avenir else "en cours")
    print("index.html mis à jour : %s — semaine %s au %s — jour affiché : %s"
          % (sem["titre"], etat, iso, "aucun" if depasse else sem["jours"][i]["nom"]))

if __name__ == "__main__":
    main()
