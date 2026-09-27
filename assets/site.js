/* breizhou.fr — script commun : onglets sur téléphone, anciens liens, encart du menu sur
   l'accueil. Aucun lien ne fait défiler la page. Le site reste lisible sans script. */
(function () {
  /* Anciens liens de la page unique (breizhou.fr/#menus, #contact…) : on renvoie vers la
     page qui a pris la place de la section. */
  var anciens = { '#cuisine': '/la-cuisine/', '#textures': '/textures/', '#menus': '/menus/',
    '#securite': '/tracabilite/', '#publics': '/ecoles-seniors/', '#engagements': '/la-cuisine/',
    '#contact': '/contact/' };
  if ((location.pathname === '/' || /\/index\.html$/.test(location.pathname)) && anciens[location.hash]) {
    location.replace(anciens[location.hash]);
    return;
  }

  /* Onglets sur téléphone : l'onglet de la page courante est ramené dans la rangée visible.
     On ne fait défiler que la rangée d'onglets, jamais la page. */
  var ul = document.querySelector('.menu-nav ul'), actif = document.querySelector('.menu-nav a[aria-current="page"]');
  if (ul && actif && ul.scrollWidth > ul.clientWidth) {
    var li = actif.parentNode;
    ul.scrollLeft = Math.max(0, li.offsetLeft - (ul.clientWidth - li.offsetWidth) / 2);
  }

  /* Lien d'évitement (clavier, lecteur d'écran) : il place le curseur sur le contenu sans
     faire défiler la page ni ajouter de # à l'adresse. */
  var evite = document.querySelector('.lien-evitement'), contenu = document.getElementById('contenu');
  if (evite && contenu) {
    evite.addEventListener('click', function (e) { e.preventDefault(); contenu.focus({ preventScroll: true }); });
  }

  /* Encart « menu du jour » de l'accueil : lit menus/semaine.json, écrit par l'outil
     d'intégration. Même règle que la page Menus : jamais un menu dépassé présenté comme
     actuel. Sans script ou sans données valides, l'encart garde son texte d'attente et son
     lien vers la page Menus. */
  var encart = document.getElementById('encart-menu');
  if (!encart || !window.fetch) return;
  var esc = function (t) { return String(t || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  fetch('/menus/semaine.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (sem) {
    if (!sem || !sem.jours || sem.jours.length !== 5 || !sem.debut || !sem.fin) return;
    var now = new Date();
    var iso = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
    var jour = encart.querySelector('.em-jour'), sous = encart.querySelector('.em-sous'), plats = encart.querySelector('.em-plats ul'), titre = encart.querySelector('.em-plats h3');
    var titreSection = document.getElementById('t-menu');
    if (iso > sem.fin) {
      jour.textContent = 'Le menu de la semaine arrive bientôt.';
      sous.textContent = 'Il est affiché dès sa publication par la cuisine.';
      return;
    }
    var avenir = iso < sem.debut, d = now.getDay();
    var i = avenir ? 0 : ((d >= 1 && d <= 5) ? d - 1 : 4);
    var j = sem.jours[i];
    /* « aujourd'hui » seulement si c'est vrai : un jour de semaine, dans la semaine en cours */
    if (titreSection) {
      var court = String(j.date || '').replace(/\s+\d{4}$/, '');
      titreSection.textContent = (!avenir && d >= 1 && d <= 5) ? 'Au menu aujourd\u2019hui' : 'Au menu ' + court.charAt(0).toLowerCase() + court.slice(1);
    }
    jour.innerHTML = esc(j.date) + (j.veggie ? ' <span class="veggie">Veggie</span>' : '');
    sous.textContent = (avenir ? 'Semaine prochaine · ' : '') + sem.titre;
    titre.textContent = 'Au menu, en texture grand (dès 12 mois)';
    plats.innerHTML = (j.grand || []).map(function (p) { return '<li>' + esc(p) + '</li>'; }).join('');
    plats.hidden = false;
  }).catch(function () {});
})();
