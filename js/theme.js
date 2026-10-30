/* Run before the page renders to respect the saved theme without a flash. */
(() => {
  let theme = null;
  try {
    theme = localStorage.getItem("portfolio-theme");
  } catch {
    /* Storage can be disabled. */
  }
  if (theme !== "light" && theme !== "dark") {
    theme = window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }
  document.documentElement.dataset.theme = theme;
})();
