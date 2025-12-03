const API_BASE = "http://localhost:8000";

function getCurrentUser() {
  const raw = localStorage.getItem("coursehub_user");
  return raw ? JSON.parse(raw) : null;
}

function setCurrentUser(user) {
  localStorage.setItem("coursehub_user", JSON.stringify(user));
}

function clearCurrentUser() {
  localStorage.removeItem("coursehub_user");
}

function requireRole(role) {
  const user = getCurrentUser();
  if (!user || user.role !== role) {
    window.location.href = "index.html";
  }
  return user;
}

function attachLogoutHandler() {
  const btn = document.getElementById("logout-btn");
  if (!btn) return;
  btn.addEventListener("click", () => {
    clearCurrentUser();
    window.location.href = "index.html";
  });
}
