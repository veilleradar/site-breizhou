#!/usr/bin/env python3
"""Compare le menu du site (JSON) avec les menus quotidiens de l'agent étiquettes.

Usage : python3 outils/comparer-etiquettes.py menus/2026-09-28.json

Lecture seule des fichiers `Etiquettes Breizhou/comparaisons/<date>/menu-<jour>.txt`
(un bloc par texture : INTRO, PETIT, MOYEN, GRAND, GEANT, GOUTER, puis « Changements »
qu'on ignore). Le rapport va sur la sortie standard et dans menus/<date>-comparaison.txt.

Deux plats sont considérés identiques après normalisation : minuscules, sans accents,
« & » = « et », « / » = « ou », apostrophes et ponctuation retirées, mots vides retirés
(de, du, des, d, le, la, les, l, a, au, aux, en, et). Une différence n'est pas forcément
une faute : le chef écrit parfois « Pom'Bananes » et l'affiche « Purée pom'bananes ». Le
rapport les montre côte à côte, c'est un humain qui tranche.
"""
import json, re, sys, pathlib, unicodedata, datetime

ICI = pathlib.Path(__file__).resolve().parent.parent          # site-breizhou/
RACINE = ICI.parent                                           # claude code/
DOSSIER = RACINE / "Etiquettes Breizhou" / "comparaisons"
TEXTURES = ["intro", "petit", "moyen", "grand", "geant", "gouter"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
VIDES = {"de", "du", "des", "d", "le", "la", "les", "l", "a", "au", "aux", "en", "et", "ou", "the"}

def norm(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    t = t.replace("&", " et ").replace("/", " ou ").replace("'", " ").replace("’", " ")
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    mots = [m for m in t.split() if m not in VIDES]
    return " ".join(mots)

def lire_txt(chemin):
    """Renvoie {texture: [plats]} depuis un menu-<jour>.txt de l'agent étiquettes."""
    blocs, courant = {}, None
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        l = ligne.strip()
        if not l:
            continue
        if re.match(r"^changements?\b", l, re.I):
            break
        cle = norm(l).replace(" ", "")
        if cle in TEXTURES and l.upper() == l:
            courant = cle
            blocs[courant] = []
            continue
        if courant:
            blocs[courant].append(l)
    return blocs

def comparer(site, etq):
    """Renvoie (communs, seulement_site, seulement_etiquettes) sur une texture."""
    ns = {norm(p): p for p in site}
    ne = {norm(p): p for p in etq}
    communs = [ns[k] for k in ns if k in ne]
    seul_s = [ns[k] for k in ns if k not in ne]
    seul_e = [ne[k] for k in ne if k not in ns]
    return communs, seul_s, seul_e

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    fichier = pathlib.Path(sys.argv[1]).resolve()
    sem = json.loads(fichier.read_text(encoding="utf-8"))
    debut = datetime.date.fromisoformat(sem["debut"])
    lignes = ["Comparaison site ↔ agent étiquettes — " + sem["titre"],
              "Site : " + str(fichier.relative_to(RACINE)) + " · Étiquettes : " + str(DOSSIER.relative_to(RACINE)) + "/<date>/menu-<jour>.txt", ""]
    ecarts_total, jours_compares = 0, 0
    for n, jour in enumerate(sem["jours"]):
        date = debut + datetime.timedelta(days=n)
        nom = JOURS[n]
        chemin = DOSSIER / date.isoformat() / ("menu-%s.txt" % nom)
        if not chemin.exists():
            lignes.append("%s %s : pas de menu étiquettes (%s absent)" % (jour["nom"], date.strftime("%d/%m"), chemin.relative_to(RACINE)))
            continue
        jours_compares += 1
        etq = lire_txt(chemin)
        lignes.append("%s %s : comparé avec %s" % (jour["nom"], date.strftime("%d/%m"), chemin.relative_to(RACINE)))
        for t in TEXTURES:
            if t not in etq:
                lignes.append("  %-7s ⚠ texture absente du fichier étiquettes" % t.upper())
                ecarts_total += 1
                continue
            communs, seul_s, seul_e = comparer(jour.get(t, []), etq[t])
            if not seul_s and not seul_e:
                lignes.append("  %-7s ✓ identique (%d plats)" % (t.upper(), len(communs)))
            else:
                ecarts_total += len(seul_s) + len(seul_e)
                lignes.append("  %-7s ✗ écart" % t.upper())
                for p in seul_s:
                    lignes.append("          site seulement       : " + p)
                for p in seul_e:
                    lignes.append("          étiquettes seulement : " + p)
        lignes.append("")
    lignes.append("Bilan : %d jour(s) comparé(s), %d écart(s) à relire par un humain." % (jours_compares, ecarts_total))
    texte = "\n".join(lignes)
    print(texte)
    sortie = fichier.with_name(fichier.stem + "-comparaison.txt")
    sortie.write_text(texte + "\n", encoding="utf-8")
    print("\nRapport écrit : " + str(sortie.relative_to(RACINE)))

if __name__ == "__main__":
    main()
