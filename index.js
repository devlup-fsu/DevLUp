let projects = [];
let current = 0;

fetch('featured_projects.json')
  .then(r => r.json())
  .then(data => { projects = data; renderProject(); });

function renderProject() {
  const p = projects[current];
  document.getElementById('proj-tag').textContent = p.tag;
  document.getElementById('proj-title').textContent = p.title;
  document.getElementById('proj-desc').textContent = p.desc;
  document.getElementById('proj-author').textContent = 'by ' + p.authors.join(', ');
  document.getElementById('proj-year').textContent = p.year;
  document.getElementById('proj-counter').textContent = (current+1) + ' of ' + projects.length;

  document.getElementById('card-preview').style.setProperty('background-image', p.bg);

  const art = document.getElementById('preview-art');
  art.src = p.art_link;
  const dots = document.getElementById('dots');

  dots.innerHTML = '';
  projects.forEach(function(_, i) {
    const d = document.createElement('div');
    d.className = 'dot' + (i === current ? ' active' : '');
    d.onclick = function() { current = i; renderProject(); };
    dots.appendChild(d);
  });
}

function changeProject(dir) {
  current = (current + dir + projects.length) % projects.length;
  renderProject();
}

function viewProject() {
  const link = projects[current].link;
  if (link) window.open(link, '_blank', 'noopener,noreferrer');
}

document.querySelector('.navbar-toggle').addEventListener('click', function() {
  document.querySelector('.navbar').classList.toggle('open');
});
