(() => {
  const STORAGE_KEY = "lang";

  const I18N = {
    ru: {
      app_title: "SportTrack",
      lang_ru: "Русский",
      lang_en: "English",
      lang_kz: "Қазақша",
      back: "← Назад",
      save: "Сохранить",
      cancel: "Отмена",
      loading: "Загрузка...",
      no_data: "Пока данных нет",

      athlete_dashboard_workouts_title: "Мои тренировки",
      athlete_dashboard_progress_title: "Прогресс",
      athlete_dashboard_tasks_title: "Задания",
      athlete_dashboard_notifications_title: "Уведомления",
      athlete_dashboard_welcome: "Добро пожаловать",

      progress_title: "Прогресс",
      progress_workouts_done: "Тренировок выполнено",
      progress_tasks_done: "Заданий выполнено",
      progress_hours: "Часов тренировок",
      progress_chart_placeholder: "📈 График прогресса (можно добавить позже)",

      tasks_title: "Задания",
      tasks_active: "Активные задания",
      tasks_submit: "Сдать",
      tasks_submitted_view: "Отправлено (посмотреть)",
      tasks_send_to_coach: "Отправить тренеру",
      tasks_add_text_or_photo: "Добавь текст или фото",

      coach_send_task_title: "Выдать задание",
      coach_my_tasks: "Мои отправленные задания",
      coach_athlete: "Спортсмен",
      coach_task_name: "Название задания",
      coach_desc: "Описание",
      coach_deadline: "Дедлайн",
      coach_photo_optional: "Фото (необязательно)",
      coach_send: "Отправить",

      notifications_title: "Уведомления",
      notifications_empty: "Пока уведомлений нет",

      profile_edit_title: "Редактирование профиля",
      profile_edit_avatar: "Аватар",
      profile_edit_avatar_desc: "Нажмите, чтобы загрузить новое фото",
      profile_edit_firstname: "Имя",
      profile_edit_lastname: "Фамилия",
      profile_edit_email: "Email",
      profile_edit_sport: "Вид спорта",
      profile_edit_save: "Сохранить изменения",
      profile_edit_cancel: "Отмена",
      profile_edit_reset_password: "Сбросить пароль",
      profile_edit_reset_desc: "Получить ссылку для сброса пароля на email",
    },

    en: {
      app_title: "SportTrack",
      lang_ru: "Русский",
      lang_en: "English",
      lang_kz: "Қазақша",
      back: "← Back",
      save: "Save",
      cancel: "Cancel",
      loading: "Loading...",
      no_data: "No data yet",

      athlete_dashboard_workouts_title: "My workouts",
      athlete_dashboard_progress_title: "Progress",
      athlete_dashboard_tasks_title: "Tasks",
      athlete_dashboard_notifications_title: "Notifications",
      athlete_dashboard_welcome: "Welcome",

      progress_title: "Progress",
      progress_workouts_done: "Workouts completed",
      progress_tasks_done: "Tasks completed",
      progress_hours: "Training hours",
      progress_chart_placeholder: "📈 Progress chart (add later)",

      tasks_title: "Tasks",
      tasks_active: "Active tasks",
      tasks_submit: "Submit",
      tasks_submitted_view: "Submitted (view)",
      tasks_send_to_coach: "Send to coach",
      tasks_add_text_or_photo: "Add text or photo",

      coach_send_task_title: "Create a task",
      coach_my_tasks: "My sent tasks",
      coach_athlete: "Athlete",
      coach_task_name: "Task title",
      coach_desc: "Description",
      coach_deadline: "Deadline",
      coach_photo_optional: "Photo (optional)",
      coach_send: "Send",

      notifications_title: "Notifications",
      notifications_empty: "No notifications yet",

      profile_edit_title: "Edit profile",
      profile_edit_avatar: "Avatar",
      profile_edit_avatar_desc: "Click to upload a new photo",
      profile_edit_firstname: "First name",
      profile_edit_lastname: "Last name",
      profile_edit_email: "Email",
      profile_edit_sport: "Sport",
      profile_edit_save: "Save changes",
      profile_edit_cancel: "Cancel",
      profile_edit_reset_password: "Reset password",
      profile_edit_reset_desc: "Send password reset link to email",
    },

    kz: {
      app_title: "SportTrack",
      lang_ru: "Русский",
      lang_en: "English",
      lang_kz: "Қазақша",
      back: "← Артқа",
      save: "Сақтау",
      cancel: "Болдырмау",
      loading: "Жүктелуде...",
      no_data: "Әзірге дерек жоқ",

      athlete_dashboard_workouts_title: "Менің жаттығуларым",
      athlete_dashboard_progress_title: "Прогресс",
      athlete_dashboard_tasks_title: "Тапсырмалар",
      athlete_dashboard_notifications_title: "Хабарландырулар",
      athlete_dashboard_welcome: "Қош келдіңіз",

      progress_title: "Прогресс",
      progress_workouts_done: "Орындалған жаттығулар",
      progress_tasks_done: "Орындалған тапсырмалар",
      progress_hours: "Жаттығу сағаттары",
      progress_chart_placeholder: "📈 Прогресс графигі (кейін қосуға болады)",

      tasks_title: "Тапсырмалар",
      tasks_active: "Белсенді тапсырмалар",
      tasks_submit: "Тапсыру",
      tasks_submitted_view: "Жіберілді (қарау)",
      tasks_send_to_coach: "Жаттықтырушыға жіберу",
      tasks_add_text_or_photo: "Мәтін немесе фото қос",

      coach_send_task_title: "Тапсырма беру",
      coach_my_tasks: "Жіберілген тапсырмаларым",
      coach_athlete: "Спортшы",
      coach_task_name: "Тапсырма атауы",
      coach_desc: "Сипаттама",
      coach_deadline: "Мерзім",
      coach_photo_optional: "Фото (міндетті емес)",
      coach_send: "Жіберу",

      notifications_title: "Хабарландырулар",
      notifications_empty: "Әзірге хабарландыру жоқ",

      profile_edit_title: "Профильді өңдеу",
      profile_edit_avatar: "Аватар",
      profile_edit_avatar_desc: "Жаңа фото жүктеу үшін басыңыз",
      profile_edit_firstname: "Аты",
      profile_edit_lastname: "Тегі",
      profile_edit_email: "Email",
      profile_edit_sport: "Спорт түрі",
      profile_edit_save: "Өзгерістерді сақтау",
      profile_edit_cancel: "Болдырмау",
      profile_edit_reset_password: "Құпиясөзді қалпына келтіру",
      profile_edit_reset_desc: "Email-ға қалпына келтіру сілтемесін жіберу",
    }
  };

  function getLang() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && I18N[saved]) return saved;
    return "ru";
  }

  function t(lang, key) {
    return (I18N[lang] && I18N[lang][key]) || (I18N.ru[key]) || key;
  }

  function applyI18n(lang) {
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      el.textContent = t(lang, key);
    });

    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const key = el.getAttribute("data-i18n-placeholder");
      el.setAttribute("placeholder", t(lang, key));
    });

    const titleEl = document.querySelector("title[data-i18n]");
    if (titleEl) titleEl.textContent = t(lang, titleEl.getAttribute("data-i18n"));
  }

  function bindLangSelect() {
    const sel = document.getElementById("langSelect");
    if (!sel) return;

    const current = getLang();
    sel.value = current;

    sel.addEventListener("change", () => {
      const lang = sel.value;
      localStorage.setItem(STORAGE_KEY, lang);
      applyI18n(lang);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    const lang = getLang();
    bindLangSelect();
    applyI18n(lang);
  });

  window.setLang = (lang) => {
    if (!I18N[lang]) return;
    localStorage.setItem(STORAGE_KEY, lang);
    applyI18n(lang);
    const sel = document.getElementById("langSelect");
    if (sel) sel.value = lang;
  };
})();
