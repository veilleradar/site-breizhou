/* breizhou.fr — script commun : bouton « Menu » sur téléphone, anciens liens, encart du
   menu sur l'accueil. Le site reste lisible sans script. */
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

  /* Bouton « Menu » */
  var btn = document.querySelector('.menu-btn'), nav = document.getElementById('menu');
  if (btn && nav) {
    var fermer = function () { nav.classList.remove('ouvert'); btn.setAttribute('aria-expanded', 'false'); };
    btn.addEventListener('click', function () {
      var ouvert = nav.classList.toggle('ouvert');
      btn.setAttribute('aria-expanded', ouvert ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') fermer(); });
    window.matchMedia('(min-width: 1061px)').addEventListener('change', fermer);
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
    if (iso > sem.fin) {
      jour.textContent = 'Le menu de la semaine arrive bientôt.';
      sous.textContent = 'Il est affiché dès sa publication par la cuisine.';
      return;
    }
    var avenir = iso < sem.debut, d = now.getDay();
    var i = avenir ? 0 : ((d >= 1 && d <= 5) ? d - 1 : 4);
    var j = sem.jours[i];
    jour.innerHTML = esc(j.date) + (j.veggie ? ' <span class="veggie">Veggie</span>' : '');
    sous.textContent = (avenir ? 'Semaine prochaine · ' : '') + sem.titre;
    titre.textContent = 'Au menu, en texture grand (dès 12 mois)';
    plats.innerHTML = (j.grand || []).map(function (p) { return '<li>' + esc(p) + '</li>'; }).join('');
    plats.hidden = false;
  }).catch(function () {});
})();
