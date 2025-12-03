async function loadAdminCourses() {
  const tbody = document.querySelector("#admin-courses-table tbody");
  tbody.innerHTML = "";

  const res = await fetch(`${API_BASE}/courses/`);
  const courses = await res.json();

  courses.forEach((c) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.course_id}</td>
      <td>${c.course_name}</td>
      <td>${c.credits}</td>
      <td>${c.max_students}</td>
      <td>
        <button class="btn btn-ghost small" data-edit="${c.course_id}">Edit</button>
        <button class="btn btn-ghost small" data-del="${c.course_id}">Delete</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  tbody.onclick = (e) => {
    if (e.target.dataset.edit) loadCourseToEdit(e.target.dataset.edit);
    if (e.target.dataset.del) deleteCourse(e.target.dataset.del);
  };
}

async function loadCourseToEdit(id) {
  openModal("modal-edit-course");
  const res = await fetch(`${API_BASE}/courses/${id}`);
  const c = await res.json();

  document.getElementById("edit-course-name").value = c.course_name;
  document.getElementById("edit-course-credits").value = c.credits;
  document.getElementById("edit-course-max").value = c.max_students;
  document.getElementById("edit-course-save").dataset.id = id;
}

async function saveNewCourse() {
  const user = getCurrentUser();
  const payload = {
    admin_id: user.user_id,
    course_name: document.getElementById("add-course-name").value,
    credits: Number(document.getElementById("add-course-credits").value),
    max_students: Number(document.getElementById("add-course-max").value),
  };
  await fetch(`${API_BASE}/courses`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  closeAllModals();
  loadAdminCourses();
}

async function saveCourseEdit() {
  const id = this.dataset.id;
  const user = getCurrentUser();
  const payload = {
    admin_id: user.user_id,
    course_name: document.getElementById("edit-course-name").value,
    credits: Number(document.getElementById("edit-course-credits").value),
    max_students: Number(document.getElementById("edit-course-max").value),
  };
  await fetch(`${API_BASE}/courses/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  closeAllModals();
  loadAdminCourses();
}

async function deleteCourse(id) {
  if (!confirm("Delete this course?")) return;
  const user = getCurrentUser();
  await fetch(`${API_BASE}/courses/${id}?admin_id=${user.user_id}`, { method: "DELETE" });
  loadAdminCourses();
}
