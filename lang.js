const translations = {
  ru: {
    app_title: "SportTrack",
    lang_ru: "Русский",
    lang_en: "Английский",
    lang_kz: "Казахский",

    reg_title: "Регистрация",
    reg_email_label: "Почта",
    reg_username_label: "Имя",
    reg_lastname_label: "Фамилия",
    reg_password_label: "Пароль",
    reg_sport_label: "Введите ваш вид спорта",
    reg_sport_placeholder: "Например: Футбол, Бокс, Бег...",
    reg_role_label: "Выберите роль",
    reg_role_athlete: "Спортсмен",
    reg_role_coach: "Тренер",
    reg_button: "Зарегистрироваться",

    confirm_title: "Подтверждение почты",
    confirm_desc: "Мы отправили код подтверждения на вашу почту. Введите его ниже.",
    confirm_code_label: "Код из письма",
    confirm_button: "Подтвердить",
    confirm_fill_error: "Введите код из письма",

    back_to_reg: "← Назад к регистрации",

    athlete_page_title: "Профиль спортсмена",
    athlete_label_fullname: "Имя и фамилия:",
    athlete_label_status: "Статус:",
    athlete_label_status_value: "спортсмен",
    athlete_label_sport: "Вид спорта:",
    athlete_label_email: "Email:",

    coach_page_title: "Профиль тренера",
    coach_label_fullname: "Имя и фамилия:",
    coach_label_status: "Статус:",
    coach_label_status_value: "тренер",
    coach_label_sport: "Вид спорта:",
    coach_label_email: "Email:",
  },

  en: {
    app_title: "SportTrack",
    lang_ru: "Russian",
    lang_en: "English",
    lang_kz: "Kazakh",

    reg_title: "Sign up",
    reg_email_label: "Email",
    reg_username_label: "First name",
    reg_lastname_label: "Last name",
    reg_password_label: "Password",
    reg_sport_label: "Enter your sport",
    reg_sport_placeholder: "For example: Football, Boxing, Running...",
    reg_role_label: "Choose role",
    reg_role_athlete: "Athlete",
    reg_role_coach: "Coach",
    reg_button: "Sign up",

    confirm_title: "Email confirmation",
    confirm_desc: "We sent a confirmation code to your email. Enter it below.",
    confirm_code_label: "Code from email",
    confirm_button: "Confirm",
    confirm_fill_error: "Please enter the code",

    back_to_reg: "← Back to registration",

    athlete_page_title: "Athlete profile",
    athlete_label_fullname: "Full name:",
    athlete_label_status: "Status:",
    athlete_label_status_value: "athlete",
    athlete_label_sport: "Sport:",
    athlete_label_email: "Email:",

    coach_page_title: "Coach profile",
    coach_label_fullname: "Full name:",
    coach_label_status: "Status:",
    coach_label_status_value: "coach",
    coach_label_sport: "Sport:",
    coach_label_email: "Email:",
  },

  kz: {
    app_title: "SportTrack",
    lang_ru: "Орысша",
    lang_en: "Ағылшынша",
    lang_kz: "Қазақша",

    reg_title: "Тіркелу",
    reg_email_label: "Пошта",
    reg_username_label: "Аты",
    reg_lastname_label: "Тегі",
    reg_password_label: "Құпия сөз",
    reg_sport_label: "Спорт түрін енгізіңіз",
    reg_sport_placeholder: "Мысалы: Футбол, Бокс, Жүгіру...",
    reg_role_label: "Рөлді таңдаңыз",
    reg_role_athlete: "Спортшы",
    reg_role_coach: "Жаттықтырушы",
    reg_button: "Тіркелу",

    confirm_title: "Поштаны растау",
    confirm_desc: "Электрондық поштаңызға растау коды жіберілді. Сол кодты төменге енгізіңіз.",
    confirm_code_label: "Код",
    confirm_button: "Растау",
    confirm_fill_error: "Кодты енгізіңіз",

    back_to_reg: "← Тіркелуге оралу",

    athlete_page_title: "Спортшы профилі",
    athlete_label_fullname: "Аты-жөні:",
    athlete_label_status: "Мәртебесі:",
    athlete_label_status_value: "спортшы",
    athlete_label_sport: "Спорт түрі:",
    athlete_label_email: "Email:",

    coach_page_title: "Жаттықтырушы профилі",
    coach_label_fullname: "Аты-жөні:",
    coach_label_status: "Мәртебесі:",
    coach_label_status_value: "жаттықтырушы",
    coach_label_sport: "Спорт түрі:",
    coach_label_email: "Email:",
  },
};

function applyTranslations(lang) {
  const dict = translations[lang] || translations["ru"];

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key]) {
      el.placeholder = dict[key];
    }
  });
}

function setLanguage(lang) {
  localStorage.setItem("lang", lang);
  applyTranslations(lang);
}

document.addEventListener("DOMContentLoaded", () => {
  const select = document.getElementById("langSelect");
  const savedLang = localStorage.getItem("lang") || "ru";

  if (select) {
    select.value = savedLang;
    select.addEventListener("change", () => {
      setLanguage(select.value);
    });
  }

  applyTranslations(savedLang);
});
