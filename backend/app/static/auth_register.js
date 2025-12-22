const $ = (id) => document.getElementById(id);

const emailSection = $("emailSection");
const confirmSection = $("confirmSection");
const dataSection = $("dataSection");

const emailInput = $("email");
const confirmEmailText = $("confirmEmailText");
const dataEmailText = $("dataEmailText");

const emailError = $("emailError");
const confirmError = $("confirmError");
const registerError = $("registerError");

const sendCodeBtn = $("sendCodeBtn");
const resendBtn = $("resendBtn");
const confirmBtn = $("confirmBtn");
const registerBtn = $("registerBtn");

const backToEmail = $("backToEmail");
const backToConfirm = $("backToConfirm");

let confirmedCode = "";

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }

function setStep(step) {
  hide(emailSection); hide(confirmSection); hide(dataSection);
  if (step === 1) show(emailSection);
  if (step === 2) show(confirmSection);
  if (step === 3) show(dataSection);
}

function setErr(el, text="") { el.textContent = text || ""; }

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  let data = {};
  try { data = await res.json(); } catch {}

  if (!res.ok) throw new Error(data.detail || data.message || ("HTTP " + res.status));
  return data;
}

function roleRedirect(role) {
  const r = (role || "").toLowerCase();
  if (r === "admin") location.href = "/static/admin_page.html";
  else if (r === "coach") location.href = "/static/coach_page.html";
  else location.href = "/static/athlete_page.html";
}

sendCodeBtn.addEventListener("click", async () => {
  setErr(emailError); setErr(confirmError); setErr(registerError);

  const email = (emailInput.value || "").trim();
  if (!email) return setErr(emailError, "Введи email");

  sendCodeBtn.disabled = true;
  try {
    await postJSON("/api/email/send-code", { email });

    confirmEmailText.textContent = email;
    dataEmailText.textContent = email;
    confirmedCode = "";

    setStep(2);
  } catch (e) {
    setErr(emailError, e.message);
  } finally {
    sendCodeBtn.disabled = false;
  }
});

resendBtn.addEventListener("click", async () => {
  setErr(confirmError);

  const email = (emailInput.value || "").trim();
  if (!email) return setErr(confirmError, "Нет email");

  resendBtn.disabled = true;
  try {
    await postJSON("/api/email/send-code", { email });
    setErr(confirmError, "Код отправлен ещё раз ✅");
  } catch (e) {
    setErr(confirmError, e.message);
  } finally {
    resendBtn.disabled = false;
  }
});

confirmBtn.addEventListener("click", async () => {
  setErr(confirmError); setErr(registerError);

  const email = (emailInput.value || "").trim();
  const code = ($("confirmCode").value || "").trim();
  if (!code) return setErr(confirmError, "Введи код");

  confirmBtn.disabled = true;
  try {
    await postJSON("/api/email/check-code", { email, code });
    confirmedCode = code;
    dataEmailText.textContent = email;
    setStep(3);
  } catch (e) {
    confirmedCode = "";
    setErr(confirmError, e.message);
  } finally {
    confirmBtn.disabled = false;
  }
});

registerBtn.addEventListener("click", async () => {
  setErr(registerError);

  const email = (emailInput.value || "").trim();
  const username = ($("username").value || "").trim();
  const last_name = ($("lastname").value || "").trim();
  const password = $("password").value || "";
  const sport = ($("sportInput").value || "").trim();
  const role = $("role").value;

  if (!confirmedCode) return setErr(registerError, "Сначала подтверди код");
  if (!username) return setErr(registerError, "Введи имя");
  if (!password || password.length < 4) return setErr(registerError, "Пароль минимум 4 символа");

  registerBtn.disabled = true;
  try {
    const data = await postJSON("/api/register", {
      email,
      code: confirmedCode,
      username,
      last_name: last_name || null,
      password,
      role,
      sport: sport || null
    });

    localStorage.setItem("user", JSON.stringify(data));
    roleRedirect(data.role);
  } catch (e) {
    setErr(registerError, e.message);
  } finally {
    registerBtn.disabled = false;
  }
});

backToEmail.addEventListener("click", (e) => {
  e.preventDefault();
  confirmedCode = "";
  setErr(confirmError);
  setStep(1);
});

backToConfirm.addEventListener("click", (e) => {
  e.preventDefault();
  setErr(registerError);
  setStep(2);
});

setStep(1);
