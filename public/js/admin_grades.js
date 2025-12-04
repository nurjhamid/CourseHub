async function loadAdminEnrollments() {
  const tbody = document.querySelector("#admin-enrollments-table tbody");
  tbody.innerHTML = "";

  const res = await fetch(`${API_BASE}/courses/all-enrollments`);
  const data = await res.json();

  data.forEach((e) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${e.enrollment_id}</td>
      <td>${e.student_name}</td>
      <td>${e.course_name}</td>
      <td>${e.credits}</td>
      <td>${e.grade || "—"}</td>
      <td>${new Date(e.date_enrolled).toLocaleString()}</td>
      <td><button class="btn btn-primary small" data-grade="${e.enrollment_id}">Assign</button></td>
    `;
    tbody.appendChild(tr);
  });

  tbody.onclick = (ev) => {
    if (ev.target.dataset.grade) {
      openGradeModal(ev.target.dataset.grade);
    }
  };
}

function openGradeModal(id) {
  document.getElementById("assign-grade-save").dataset.enrollment = id;
  openModal("modal-grade");
}

async function saveGrade() {
  const id = this.dataset.enrollment;
  const grade = document.getElementById("grade-input").value;
  await fetch(`${API_BASE}/courses/grade/${id}`, {
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ grade }),
  });
  closeAllModals();
  loadAdminEnrollments();
}
