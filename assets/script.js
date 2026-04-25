/* ==========================================================
   Interview Prep Mastery — Site Scripts
   ========================================================== */

(function () {
  "use strict";

  // ---------- Theme toggle ----------
  const THEME_KEY = "ipm-theme";
  const root = document.documentElement;

  function getSavedTheme() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (_e) {
      return null;
    }
  }

  function saveTheme(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (_e) {
      /* ignore */
    }
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    const btn = document.querySelector(".theme-toggle");
    if (btn) {
      btn.textContent = theme === "dark" ? "☀ Light" : "☾ Dark";
      btn.setAttribute("aria-label", theme === "dark" ? "Switch to light mode" : "Switch to dark mode");
    }
  }

  function initTheme() {
    const saved = getSavedTheme();
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = saved || (prefersDark ? "dark" : "light");
    applyTheme(initial);

    const btn = document.querySelector(".theme-toggle");
    if (btn) {
      btn.addEventListener("click", function () {
        const current = root.getAttribute("data-theme") || "light";
        const next = current === "dark" ? "light" : "dark";
        applyTheme(next);
        saveTheme(next);
      });
    }
  }

  // ---------- Mobile sidebar ----------
  function initSidebar() {
    const toggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");
    if (!toggle || !sidebar) return;

    // Create backdrop
    const backdrop = document.createElement("div");
    backdrop.className = "sidebar-backdrop";
    document.body.appendChild(backdrop);

    function open() {
      sidebar.classList.add("open");
      backdrop.classList.add("open");
      document.body.style.overflow = "hidden";
    }
    function close() {
      sidebar.classList.remove("open");
      backdrop.classList.remove("open");
      document.body.style.overflow = "";
    }

    toggle.addEventListener("click", function () {
      if (sidebar.classList.contains("open")) close();
      else open();
    });
    backdrop.addEventListener("click", close);

    // Close on link click (mobile)
    sidebar.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () {
        if (window.innerWidth <= 1024) close();
      });
    });

    // Close on ESC
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && sidebar.classList.contains("open")) close();
    });
  }

  // ---------- Active link highlight ----------
  function initActiveLink() {
    const path = window.location.pathname;
    const file = path.split("/").pop();
    if (!file) return;
    document.querySelectorAll(".sidebar a").forEach(function (a) {
      const href = a.getAttribute("href") || "";
      if (href.endsWith(file) && file !== "index.html") {
        a.classList.add("active");
        // Scroll active link into view
        try {
          a.scrollIntoView({ block: "center", behavior: "instant" });
        } catch (_e) {
          a.scrollIntoView(false);
        }
      }
    });
  }

  // ---------- Smooth anchor scroll with header offset ----------
  function initSmoothAnchor() {
    document.addEventListener("click", function (e) {
      const link = e.target.closest('a[href^="#"]');
      if (!link) return;
      const id = link.getAttribute("href").slice(1);
      if (!id) return;
      const target = document.getElementById(id);
      if (!target) return;
      e.preventDefault();
      const header = document.querySelector(".site-header");
      const offset = (header ? header.offsetHeight : 0) + 10;
      const top = target.getBoundingClientRect().top + window.pageYOffset - offset;
      window.scrollTo({ top: top, behavior: "smooth" });
      history.replaceState(null, "", "#" + id);
    });
  }

  // ---------- Boot ----------
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initTheme();
      initSidebar();
      initActiveLink();
      initSmoothAnchor();
    });
  } else {
    initTheme();
    initSidebar();
    initActiveLink();
    initSmoothAnchor();
  }
})();
