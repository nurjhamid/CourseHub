document.addEventListener("DOMContentLoaded", () => {
  setupAdminDashboard();
});

function setupAdminDashboard() {
  const info = document.getElementById("admin-info");
  if (!info) return;

  const user = requireRole("admin");
  info.textContent = `Logged in as ${user.username} (Admin)`;

  attachLogoutHandler();
  loadAdminCourses();
  loadAdminEnrollments();

  document.getElementById("btn-open-add-course").onclick = () =>
    openModal("modal-add-course");

  document.getElementById("add-course-save").onclick = saveNewCourse;
  document.getElementById("edit-course-save").onclick = saveCourseEdit;
  document.getElementById("assign-grade-save").onclick = saveGrade;
}
