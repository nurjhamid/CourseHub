document.addEventListener("DOMContentLoaded", () => {
  setupStudentDashboard();
});

function setupStudentDashboard() {
  const info = document.getElementById("student-info");
  if (!info) return;

  const user = requireRole("student");
  info.textContent = `Logged in as ${user.username} (Student)`;

  attachLogoutHandler();
  loadAvailableCoursesForStudent(user);
  loadMyEnrollments(user);
  loadMyGrades(user);
}
