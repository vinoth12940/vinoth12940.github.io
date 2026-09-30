const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#site-nav');
menuButton.addEventListener('click', () => {
  const expanded = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!expanded));
  navigation.classList.toggle('open', !expanded);
});
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  menuButton.setAttribute('aria-expanded', 'false');
  navigation.classList.remove('open');
}));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && navigation.classList.contains('open')) {
    menuButton.setAttribute('aria-expanded', 'false');
    navigation.classList.remove('open');
    menuButton.focus();
  }
});
const credentials = Array.from(document.querySelectorAll('.credential'));
document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => {
  const category = button.dataset.filter;
  document.querySelectorAll('.filter').forEach(filter => {
    const selected = filter === button;
    filter.classList.toggle('active', selected);
    filter.setAttribute('aria-pressed', String(selected));
  });
  let count = 0;
  credentials.forEach(credential => {
    credential.hidden = category !== 'All' && credential.dataset.category !== category;
    if (!credential.hidden) count++;
  });
  document.querySelector('#credential-status').textContent = `${count} credentials shown for ${category}.`;
}));
