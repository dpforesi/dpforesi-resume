/* Text-mode prompt: turns the static "guest@dpforesi:~$" line on each text-mode
   screen into a typed command prompt when the browser runs JavaScript.
   Without JS the screens still work through their lettered links. */
(function () {
  if (document.documentElement.getAttribute('data-mode') === 'gui') return;
  var cli = document.getElementById('cli');
  var slot = document.getElementById('cli-prompt');
  if (!cli || !slot) return;

  var root = cli.getAttribute('data-root') || '';
  var PAGES = {
    menu: 'index.html?cli', resume: 'cli/resume.html', history: 'cli/history.html',
    skills: 'cli/skills.html', experience: 'cli/experience.html', education: 'cli/education.html',
    about: 'cli/about.html', books: 'cli/books.html', projects: 'cli/projects.html',
    contact: 'cli/contact.html', gui: 'index.html?gui'
  };
  var ALIASES = {
    m: 'menu', home: 'menu', main: 'menu', r: 'resume', hist: 'history', s: 'skills',
    exp: 'experience', work: 'experience', edu: 'education', book: 'books', scifi: 'books',
    'sci-fi': 'books', project: 'projects', github: 'projects', gh: 'projects', con: 'contact',
    exit: 'gui', terminal: 'gui', interactive: 'gui'
  };
  var HELP = [
    ['menu', 'return to main menu'], ['resume', 'full resume'], ['history', 'work history (compact)'],
    ['skills', 'skills & expertise'], ['experience', 'detailed work experience'],
    ['education', 'education background'], ['about', 'about David Foresi'], ['books', 'sci-fi works'],
    ['projects', 'github projects'], ['contact', 'contact information'],
    ['gui', 'switch to the interactive terminal'], ['clear', 'clear command output'], ['help', 'this help text']
  ];
  var PLEDGE = 'i will not spam';

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  slot.innerHTML =
    '<div id="cli-out"></div>' +
    '<form id="cli-form" autocomplete="off"><label>guest@dpforesi:~$ ' +
    '<input type="text" id="cli-input" spellcheck="false" aria-label="Command" /></label></form>' +
    '<p class="cli-hint">enter a letter, a command name, or "help"</p>';
  var out = document.getElementById('cli-out');
  var input = document.getElementById('cli-input');

  function print(html) { out.insertAdjacentHTML('beforeend', '<p>' + html + '</p>'); }
  function go(href) { location.href = href; }

  function exec(raw) {
    var cmd = raw.toLowerCase().trim();
    if (!cmd) return;
    print('guest@dpforesi:~$ ' + esc(raw));

    /* lettered options on this screen win, like the GUI's per-view selectors */
    if (cmd.length === 1) {
      var opt = cli.querySelector('a[data-key="' + cmd.toUpperCase() + '"]');
      if (opt) { go(opt.href); return; }
    }
    var contact = document.getElementById('cli-contact-body');
    if (contact && cmd === PLEDGE) { decodeContact(contact); return; }
    if (cmd === 'clear' || cmd === 'cls') { out.innerHTML = ''; return; }
    if (cmd === 'help' || cmd === 'h' || cmd === '?') {
      print(HELP.map(function (h) { return esc((h[0] + '            ').slice(0, 13) + h[1]); }).join('<br>'));
      return;
    }
    var page = PAGES[ALIASES[cmd] || cmd];
    if (page) { go(root + page); return; }
    print('<i>unknown command: "' + esc(raw) + '" — type "help" for available commands</i>');
  }

  function xorDecode(codes, key) {
    return codes.map(function (c, i) { return String.fromCharCode(c ^ key.charCodeAt(i % key.length)); }).join('');
  }

  function decodeContact(el) {
    var email = xorDecode(JSON.parse(el.getAttribute('data-email')), PLEDGE);
    var phone = xorDecode(JSON.parse(el.getAttribute('data-phone')), PLEDGE);
    el.innerHTML = '<p>access granted — decoding...</p>' +
      '<p>EMAIL: <a href="mailto:' + esc(email) + '">' + esc(email) + '</a></p>' +
      '<p>PHONE: ' + esc(phone) + '</p>';
  }

  document.getElementById('cli-form').addEventListener('submit', function (e) {
    e.preventDefault();
    var val = input.value;
    input.value = '';
    exec(val);
    input.scrollIntoView({ block: 'nearest' });
  });
  /* click anywhere (except links or a text selection) to focus the prompt */
  document.addEventListener('click', function (e) {
    if (e.target.closest('a') || String(window.getSelection())) return;
    input.focus();
  });
  input.focus();
})();
