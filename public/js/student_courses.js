async function loadAvailableCoursesForStudent(user) {
  const tbody = document.querySelector("#available-courses-table tbody");
  const msg = document.getElementById("student-message");

  tbody.innerHTML = "";
  msg.textContent = "";

  const res = await fetch(`${API_BASE}/courses/`);
  const courses = await res.json();

  courses.forEach((c) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${c.course_id}</td>
      <td>${c.course_name}</td>
      <td>${c.credits}</td>
      <td>${c.max_students}</td>
      <td><button class="btn btn-primary small" data-course="${c.course_id}">Enroll</button></td>
    `;
    tbody.appendChild(tr);
  });

  tbody.addEventListener("click", async (e) => {
    if (e.target.dataset.course) {
      const courseId = Number(e.target.dataset.course);
      msg.textContent = "Enrolling...";

      const res = await fetch(`${API_BASE}/courses/enroll`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.user_id, course_id: courseId }),
      });

      const data = await res.json();
      if (!res.ok) {
        msg.textContent = data.detail || "Enrollment failed";
        msg.classList.add("error");
      } else {
        msg.textContent = "Enrolled successfully";
        msg.classList.remove("error");
        loadMyEnrollments(user);
        loadMyGrades(user);
      }
    }
  });
}

async function loadMyEnrollments(user) {
  const tbody = document.querySelector("#my-enrollments-table tbody");
  const msg = document.getElementById("student-message");

  tbody.innerHTML = "";
  msg.textContent = "";

  const res = await fetch(`${API_BASE}/courses/my-enrollments?user_id=${user.user_id}`);
  const enrollments = await res.json();

  enrollments.forEach((en) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${en.enrollment_id}</td>
      <td>${en.course_name}</td>
      <td>${en.credits}</td>
      <td>${new Date(en.date_enrolled).toLocaleString()}</td>
      <td>${en.grade || "Not graded"}</td>
      <td><button class="btn btn-ghost small" data-enroll="${en.enrollment_id}">Unenroll</button></td>
    `;
    tbody.appendChild(tr);
  });

  tbody.addEventListener("click", async (e) => {
    if (e.target.dataset.enroll) {
      const id = Number(e.target.dataset.enroll);
      msg.textContent = "Unenrolling...";

      const res = await fetch(`${API_BASE}/courses/enroll/${id}?user_id=${user.user_id}`, {
        method: "DELETE",
      });

      const data = await res.json();
      if (!res.ok) {
        msg.textContent = data.detail || "Unenrollment failed";
        msg.classList.add("error");
      } else {
        msg.textContent = data.message;
        msg.classList.remove("error");
        loadMyEnrollments(user);
        loadMyGrades(user);
      }
    }
  });
}
