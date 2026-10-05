/* Text-mode contact screen: when the browser runs JavaScript, the anti-spam
   pledge becomes a selectable link that decodes the email and phone.
   Without JS the screen points to the interactive terminal instead. */
(function () {
  var body = document.getElementById('cli-contact-body');
  var slot = document.getElementById('cli-pledge');
  if (!body || !slot) return;
  var PLEDGE = 'i will not spam';

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function xorDecode(codes, key) {
    return codes.map(function (c, i) { return String.fromCharCode(c ^ key.charCodeAt(i % key.length)); }).join('');
  }

  slot.innerHTML = 'To reveal it, take the pledge: [ <a href="#" id="cli-pledge-link">I will not spam</a> ]';
  document.getElementById('cli-pledge-link').addEventListener('click', function (e) {
    e.preventDefault();
    var email = xorDecode(JSON.parse(body.getAttribute('data-email')), PLEDGE);
    var phone = xorDecode(JSON.parse(body.getAttribute('data-phone')), PLEDGE);
    body.innerHTML = '<p>EMAIL: <a href="mailto:' + esc(email) + '">' + esc(email) + '</a></p>' +
      '<p>PHONE: ' + esc(phone) + '</p>';
    slot.textContent = 'access granted.';
  });
})();
