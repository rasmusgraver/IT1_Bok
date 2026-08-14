// Denne filen bruker addEventListener til å styre mobilmenyen —
// samme konsept elevene lærer om i JS-delen av faget.

document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const sidebar = document.getElementById("sidebar");

  if (!toggle || !sidebar) return;

  const closeMenu = () => {
    sidebar.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
  };

  const openMenu = () => {
    sidebar.classList.add("is-open");
    toggle.setAttribute("aria-expanded", "true");
  };

  toggle.addEventListener("click", () => {
    const isOpen = sidebar.classList.contains("is-open");
    isOpen ? closeMenu() : openMenu();
  });

  // Lukk menyen når en lenke i sidemenyen klikkes (mobil)
  sidebar.querySelectorAll(".nav-link, .nav-home").forEach((link) => {
    link.addEventListener("click", closeMenu);
  });

  // Lukk menyen med Escape
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") closeMenu();
  });
});
