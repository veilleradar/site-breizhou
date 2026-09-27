/* Page Menus : choisit le jour à afficher à partir du bloc #menu-data écrit par l'outil
   d'intégration. Trois cas : semaine à venir (on montre le lundi), semaine en cours (le
   jour, colonne surlignée), semaine dépassée (message neutre, tableau masqué). Jamais un
   ancien menu présenté comme actuel. Sans script, la version écrite par l'outil reste lisible. */
(function () {
  var box = document.getElementById('jour');
  var data = document.getElementById('menu-data');
  if (!box || !data) return;
  var sem;
  try { sem = JSON.parse(data.textContent); } catch (e) { return; }
  var head = document.querySelector('.sem-head'), wrap = document.querySelector('.menu-wrap');
  var esc = function (t) { return String(t || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var vide = function () {
    box.innerHTML = '<div class="jour-vide"><p class="jd">Le menu de la semaine arrive bientôt.</p><p class="jt">Il est affiché ici dès sa publication par la cuisine.</p></div>';
    if (head) head.hidden = true;
    if (wrap) wrap.hidden = true;
  };
  if (!sem || !sem.jours || sem.jours.length !== 5 || !sem.fin || !sem.textures) { vide(); return; }
  var now = new Date();
  var iso = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
  if (iso > sem.fin) { vide(); return; }
  if (head) head.hidden = false;
  if (wrap) wrap.hidden = false;
  var avenir = sem.debut && iso < sem.debut;
  var d = now.getDay();
  var i = avenir ? 0 : ((d >= 1 && d <= 5) ? d - 1 : 4);
  var j = sem.jours[i];
  var liste = function (k) {
    var h = (j[k] || []).map(esc).join('<br>');
    if (j.mentions && j.mentions[k]) h += '<span class="mention">' + esc(j.mentions[k]) + '</span>';
    return h;
  };
  var rows = sem.textures.map(function (t) {
    return '<div><dt>' + esc(t[1]) + '<small>' + esc(t[2]) + '</small></dt><dd>' + liste(t[0]) + '</dd></div>';
  }).join('');
  var sous = avenir ? '<b>Menu de la semaine prochaine</b>' : '<b>Cuisiné à Bréteil</b>';
  box.innerHTML = '<div class="jour-date"><p class="jd">' + esc(j.date) + (j.veggie ? ' <span class="veggie">Veggie</span>' : '') +
    '</p><p class="jt">' + sous + '<br>' + esc(sem.titre) + '</p></div><dl class="jour-list">' + rows + '</dl>';
  document.querySelectorAll('table.menu tbody tr').forEach(function (tr) {
    for (var c = 1; c < tr.children.length; c++) tr.children[c].classList.toggle('today', !avenir && c === i + 1);
  });
})();
