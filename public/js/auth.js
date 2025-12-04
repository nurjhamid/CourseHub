

document.addEventListener("DOMContentLoaded", () => {
  setupIndexPage();
});

function setupIndexPage() {
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const messageEl = document.getElementById("login-message");
      messageEl.textContent = "Signing in...";
      messageEl.classList.remove("error");

      const username = document.getElementById("login-username").value.trim();
      const password = document.getElementById("login-password").value;

      try {
        const res = await fetch(`${API_BASE}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });

        const data = await res.json();
        if (!res.ok) {
          messageEl.textContent = data.detail || "Login failed";
          messageEl.classList.add("error");
          return;
        }

        setCurrentUser(data);
        messageEl.textContent = "Login successful — redirecting...";

        setTimeout(() => {
          if (data.role === "admin") {
            window.location.href = "admin_dashboard.html";
          } else {
            window.location.href = "student_dashboard.html";
          }
        }, 700);

      } catch {
        messageEl.textContent = "Network error";
        messageEl.classList.add("error");
      }
    });
  }

  const demoBtn = document.getElementById("demo-login");
  if (demoBtn) {
    demoBtn.addEventListener("click", async () => {
      let res = await tryLogin("admin1", "admin123");
      if (res.success) { setCurrentUser(res.data); return window.location.href = "admin_dashboard.html"; }
      res = await tryLogin("student1", "stud123");
      if (res.success) { setCurrentUser(res.data); return window.location.href = "student_dashboard.html"; }
      alert("Demo login failed — backend might not be running.");
    });
  }

  async function tryLogin(username, password) {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });
      const data = await res.json();
      return { success: res.ok, data };
    } catch {
      return { success: false };
    }
  }

  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const msg = document.getElementById("register-message");
      msg.textContent = "Registering...";
      msg.classList.remove("error");

      const payload = {
        name: document.getElementById("reg-name").value.trim(),
        username: document.getElementById("reg-username").value.trim(),
        email: document.getElementById("reg-email").value.trim(),
        phone: document.getElementById("reg-phone").value.trim(),
        address: document.getElementById("reg-address").value.trim(),
        password: document.getElementById("reg-password").value,
        role: document.getElementById("reg-role").value,
      };

      try {
        const res = await fetch(`${API_BASE}/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        const data = await res.json();
        if (!res.ok) {
          msg.textContent = data.detail || "Registration failed";
          msg.classList.add("error");
          return;
        }

        setCurrentUser({ user_id: data.user_id, username: data.username, role: data.role });

        msg.textContent = "Registration successful — redirecting...";
        setTimeout(() => {
          if (data.role === "admin") window.location.href = "admin_dashboard.html";
          else window.location.href = "student_dashboard.html";
        }, 700);

      } catch {
        msg.textContent = "Network error";
        msg.classList.add("error");
      }
    });
  }
}
