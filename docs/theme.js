// Light/dark toggle shared by the demo page and the explainer.
// Load in <head> (not deferred) so the saved theme applies before first paint.
// Pages define dark tokens on :root and light tokens on :root[data-theme="light"];
// any element with [data-theme-toggle] becomes the toggle button.
(function () {
  const KEY = "vibe-theme", root = document.documentElement;
  let saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage blocked: default to dark */ }
  // ?theme=light|dark in the URL wins (handy for sharing a link in a given theme)
  const fromUrl = new URLSearchParams(location.search).get("theme");
  if (fromUrl === "light" || fromUrl === "dark") saved = fromUrl;
  root.dataset.theme = saved === "light" ? "light" : "dark";

  window.vibeTheme = {
    get: () => root.dataset.theme,
    set(v) {
      root.dataset.theme = v;
      try { localStorage.setItem(KEY, v); } catch (e) { /* not persisted; still switches */ }
      // Canvas charts read colours when drawn, so ask every chart to redraw.
      window.dispatchEvent(new Event("resize"));
      window.dispatchEvent(new Event("themechange"));
    },
    toggle() { this.set(this.get() === "dark" ? "light" : "dark"); },
  };

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-theme-toggle]").forEach(btn => {
      const label = () => {
        const dark = vibeTheme.get() === "dark";
        btn.textContent = dark ? "☀️ Light" : "🌙 Dark";
        btn.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
      };
      label();
      btn.addEventListener("click", () => { vibeTheme.toggle(); label(); });
    });
  });
})();
