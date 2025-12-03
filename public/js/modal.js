function openModal(id) {
  document.getElementById(id).classList.remove("hidden");
}

function closeAllModals() {
  document.querySelectorAll(".modal").forEach(m => m.classList.add("hidden"));
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-close]").forEach(btn => {
    btn.onclick = closeAllModals;
  });
});
