/* Progressive enhancements: the portfolio content works without JavaScript. */
(() => {
  "use strict";
  const root = document.documentElement;
  root.classList.add("js");
  const menuButton = document.querySelector(".menu-toggle");
  const navigation = document.querySelector("#nav-links");
  menuButton.hidden = false;

  function closeMenu(returnFocus = false) {
    const wasOpen = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
    if (wasOpen && returnFocus) menuButton.focus();
  }
  menuButton.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(open));
    navigation.classList.toggle("is-open", open);
  });
  navigation
    .querySelectorAll("a")
    .forEach((link) => link.addEventListener("click", () => closeMenu()));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu(true);
  });
  document.addEventListener("click", (event) => {
    if (!event.target.closest(".navigation")) closeMenu();
  });
  const desktopQuery = window.matchMedia("(min-width: 681px)");
  desktopQuery.addEventListener("change", (event) => {
    if (event.matches) closeMenu();
  });

  // Persist an explicit choice; follow the system preference until one is made.
  const themeButton = document.querySelector(".theme-toggle");
  const themeColor = document.querySelector('meta[name="theme-color"]');
  let themeChoice = null;
  try {
    themeChoice = localStorage.getItem("portfolio-theme");
  } catch {
    /* Optional storage. */
  }
  function applyTheme(theme) {
    root.dataset.theme = theme;
    themeButton.setAttribute(
      "aria-label",
      `Switch to ${theme === "dark" ? "light" : "dark"} theme`,
    );
    themeColor.setAttribute(
      "content",
      theme === "dark" ? "#101a24" : "#ffffff",
    );
  }
  applyTheme(root.dataset.theme || "light");
  themeButton.hidden = false;
  themeButton.addEventListener("click", () => {
    themeChoice = root.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(themeChoice);
    try {
      localStorage.setItem("portfolio-theme", themeChoice);
    } catch {
      /* Theme still works in memory. */
    }
  });
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", (event) => {
      if (themeChoice !== "light" && themeChoice !== "dark")
        applyTheme(event.matches ? "dark" : "light");
    });

  // Mark the section nearest the top of the viewport without moving focus.
  if ("IntersectionObserver" in window) {
    const links = [...navigation.querySelectorAll('a[href^="#"]')];
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          links.forEach((link) => {
            if (link.hash === `#${entry.target.id}`)
              link.setAttribute("aria-current", "location");
            else link.removeAttribute("aria-current");
          });
        });
      },
      { rootMargin: "-15% 0px -60% 0px" },
    );
    document
      .querySelectorAll("main section[id]")
      .forEach((section) => observer.observe(section));
  }

  const controls = document.querySelector(".skills-controls");
  const filters = [...document.querySelectorAll("[data-filter]")];
  const skills = [...document.querySelectorAll(".skill-item")];
  const search = document.querySelector("#skill-search");
  const filterStatus = document.querySelector(".filter-status");
  const emptyState = document.querySelector(".empty-state");
  let category = "all";
  controls.hidden = false;
  function filterSkills() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    skills.forEach((skill) => {
      const matchesCategory =
        category === "all" ||
        skill.dataset.category.split(" ").includes(category);
      const matchesSearch = skill.textContent
        .toLocaleLowerCase()
        .includes(query);
      skill.hidden = !(matchesCategory && matchesSearch);
      if (!skill.hidden) visible++;
    });
    emptyState.hidden = visible !== 0;
    filterStatus.textContent = `${visible} skill ${visible === 1 ? "group" : "groups"} shown.`;
  }
  filters.forEach((button) =>
    button.addEventListener("click", () => {
      category = button.dataset.filter;
      filters.forEach((filter) => {
        const active = filter === button;
        filter.classList.toggle("is-active", active);
        filter.setAttribute("aria-pressed", String(active));
      });
      filterSkills();
    }),
  );
  search.addEventListener("input", filterSkills);

  const copyButton = document.querySelector(".copy-email");
  const copyStatus = document.querySelector("#copy-status");
  if (navigator.clipboard && window.isSecureContext) {
    copyButton.hidden = false;
    copyButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText("philipmuimi05@gmail.com");
        copyStatus.textContent = "Email address copied.";
      } catch {
        copyStatus.textContent =
          "Copy unavailable. Use the email link above, or select and copy the address.";
      }
    });
  }

  // Compose only. The visitor reviews and sends the message in their email app.
  const formPanel = document.querySelector(".contact-form-panel");
  const form = document.querySelector("#contact-form");
  const formStatus = document.querySelector("#form-status");
  formPanel.hidden = false;
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const values = new FormData(form);
    const name = String(values.get("name")).trim();
    const email = String(values.get("email")).trim();
    const subject = String(values.get("subject")).trim();
    const message = String(values.get("message")).trim();
    if (![name, email, subject, message].every(Boolean)) {
      formStatus.textContent = "Please fill in every field before continuing.";
      return;
    }
    const body = `${message}\n\nFrom: ${name}\nEmail: ${email}`;
    const composeLink = `mailto:philipmuimi05@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    const link = document.createElement("a");
    link.href = composeLink;
    link.click();
    formStatus.textContent =
      "Continue in your email app to review and send. If it does not open, email philipmuimi05@gmail.com directly. Your draft remains here.";
  });
  document.querySelector("#year").textContent = String(
    new Date().getFullYear(),
  );
})();
