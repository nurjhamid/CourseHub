async function loadMyGrades(user) {
  const tbody = document.querySelector("#my-grades-table tbody");
  tbody.innerHTML = "";

  const res = await fetch(`${API_BASE}/courses/grades?user_id=${user.user_id}`);
  const grades = await res.json();

  grades.forEach((g) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${g.course_name}</td>
      <td>${g.credits}</td>
      <td>${g.grade || "Not graded"}</td>
    `;
    tbody.appendChild(tr);
  });
}
