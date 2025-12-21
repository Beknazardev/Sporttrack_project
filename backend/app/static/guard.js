(function () {
  window.requireRole = function requireRole(allowedRoles) {
    const raw = localStorage.getItem("user");
    if (!raw) {
      location.href = "/static/login.html";
      return null;
    }
    try {
      const u = JSON.parse(raw);
      const role = (u.role || "").toLowerCase();
      if (!allowedRoles.includes(role)) {
        location.href = "/static/login.html";
        return null;
      }
      return u;
    } catch (e) {
      location.href = "/static/login.html";
      return null;
    }
  };

  window.fillProfile = function fillProfile(u, map) {
    // map: {nameSel, roleSel, avatarSel(optional)}
    const full = u.last_name ? `${u.username} ${u.last_name}` : (u.username || "User");
    if (map.nameSel) document.querySelector(map.nameSel).textContent = full;
    if (map.roleSel) document.querySelector(map.roleSel).textContent = map.roleText || (u.role || "");
    if (map.avatarSel) {
      const first = (u.username || full || "").trim()[0];
      if (first) document.querySelector(map.avatarSel).textContent = first.toUpperCase();
    }
  };

  window.logout = function logout() {
    localStorage.removeItem("user");
    location.href = "/static/login.html";
  };
})();
