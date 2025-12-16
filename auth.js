const BASE = "http://127.0.0.1:8000";
const LOGIN_URL = `${BASE}/api/login`;

document.addEventListener("DOMContentLoaded", () => {
    console.log("auth.js загружен");

    const emailField = document.getElementById("email");
    const passField = document.getElementById("password");
    const loginBtn = document.querySelector(".btn");
    const status = document.getElementById("loginStatus");

    if (!emailField || !passField || !loginBtn || !status) {
        console.error("Не найдены элементы логина");
        return;
    }

    loginBtn.addEventListener("click", async (e) => {
        e.preventDefault();

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
            const res = await fetch(LOGIN_URL, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                status.textContent = data.detail || "Ошибка входа";
                status.classList.add("error");
                console.log("Login error:", data);
                return;
            }

            status.textContent = "Успешный вход";
            status.classList.add("success");

            try {
                localStorage.setItem("user", JSON.stringify(data));
            } catch (e) {
                console.warn("Не удалось сохранить пользователя", e);
            }

            const role = data.role;

            if (role === "coach") {
                window.location.href = "coach_main.html";
            } else if (role === "athlete") {
                window.location.href = "athlete_main.html";
            } else if (role === "admin") {
                window.location.href = "admin.html";
            } else {
                window.location.href = "landing.html";
            }
        } catch (err) {
            console.error("Ошибка подключения:", err);
            status.textContent = "Ошибка подключения к серверу";
            status.classList.add("error");
        }
    });
});
