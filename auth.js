const AUTH_URL = "http://127.0.0.1:8000/api/auth/login";

document.addEventListener("DOMContentLoaded", () => {
    const loginBtn = document.querySelector(".btn");
    const status = document.getElementById("loginStatus");
    const emailField = document.getElementById("email");
    const passField = document.getElementById("password");

    if (!loginBtn) return; 

    loginBtn.addEventListener("click", async () => {
        const email = emailField.value.trim();
        const password = passField.value.trim();

        status.textContent = "";
        status.className = "status"; 

        
        if (!email || !password) {
            status.textContent = "Введите email и пароль";
            status.classList.add("error");
            return;
        }

        try {
            const res = await fetch(AUTH_URL, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ email, password })
            });

            const data = await res.json().catch(() => ({}));

            
            if (!res.ok) {
                status.textContent = data.detail || "Неверные данные";
                status.classList.add("error");
                return;
            }

           
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("user", JSON.stringify(data.user));

            status.textContent = "Успешный вход";
            status.classList.add("success");

            const role = data.user.role;

            if (role === "coach") {
                window.location.href = "coach_main.html";
            } else if (role === "athlete") {
                window.location.href = "athlete_main.html";
            } else if (role === "admin") {
                window.location.href = "landing.html";
            } else {
                window.location.href = "landing.html";
            }

        } catch (err) {
            status.textContent = "Ошибка подключения";
            status.classList.add("error");
            console.error(err);
        }
    });
});