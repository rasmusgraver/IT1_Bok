// IT1 — mobilmeny, tilgjengelighet og kodekasse-verktøy.
// Samme konsept elevene lærer om i JS-delen av faget.

(function () {
  "use strict";

  /* ============================================================
     Mobilmeny – med fokuslås, backdrop-lukking og skjult sidefelt
     for skjermlesere/tastatur når menyen er lukket (R-08).
     ============================================================ */

  const toggle = document.querySelector(".menu-toggle");
  const sidebar = document.getElementById("sidebar");

  if (toggle && sidebar) {
    const mobileQuery =
      typeof window.matchMedia === "function"
        ? window.matchMedia("(max-width: 880px)")
        : null;
    const isMobile = () =>
      mobileQuery ? mobileQuery.matches : window.innerWidth <= 880;

    let lastFocus = null;

    const closeMenu = () => {
      sidebar.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      sidebar.setAttribute("aria-hidden", "true");
      sidebar.inert = true;
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };

    const openMenu = () => {
      sidebar.classList.add("is-open");
      toggle.setAttribute("aria-expanded", "true");
      sidebar.removeAttribute("aria-hidden");
      sidebar.inert = false;
      lastFocus = document.activeElement;
      const first = sidebar.querySelector("a");
      if (first) first.focus();
    };

    toggle.addEventListener("click", () => {
      sidebar.classList.contains("is-open") ? closeMenu() : openMenu();
    });

    // Lukk med Escape (fokuset går tilbake til hamburgeren)
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && sidebar.classList.contains("is-open")) {
        closeMenu();
      }
    });

    // Lukk når det klikkes utenfor menyen (backdrop)
    document.addEventListener("click", (event) => {
      if (!sidebar.classList.contains("is-open")) return;
      if (event.target.closest) {
        if (event.target.closest(".sidebar, .menu-toggle")) return;
      }
      closeMenu();
    });

    // Fokuslås mens menyen er åpen
    document.addEventListener("keydown", (event) => {
      if (!sidebar.classList.contains("is-open") || event.key !== "Tab") return;
      const links = Array.from(sidebar.querySelectorAll("a, button"));
      if (!links.length) return;
      const first = links[0];
      const last = links[links.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    // Desktop: sidefeltet skal aldri være inert
    const syncDesktop = () => {
      sidebar.classList.remove("is-open");
      sidebar.removeAttribute("aria-hidden");
      sidebar.inert = false;
    };
    if (mobileQuery) mobileQuery.addEventListener("change", syncDesktop);
    window.addEventListener("resize", syncDesktop);

    // Utgangstilstand: lukket sidefelt er skjult for skjermleser/tastatur
    if (isMobile()) {
      sidebar.setAttribute("aria-hidden", "true");
      sidebar.inert = true;
    }
  }

  /* ============================================================
     Kodekasser – kopi-knapp + lett syntax-belysning (R-06).
     ============================================================ */

  const escapeHtml = (text) =>
    text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

  const highlightCode = (code) => {
    if (!code || code.dataset.hl === "1") return;
    code.dataset.hl = "1";

    const escaped = escapeHtml(code.textContent);

    // Farger <tagg attributt="verdi">-mønstre med bokas sporfarger.
    // Kommentarer og doctype (starter med «!») legges ikke inn.
    const tagPattern =
      /(&lt;)(\/?[a-zA-Z][a-zA-Z0-9-]*)((?:\s+[a-zA-Z-]+(?:=(?:"[^"]*"|'[^']*'|[^\s>&]*))?)*)(\s?\/?)(&gt;)/g;

    const colored = escaped.replace(tagPattern, (m, lt, tag, attrs, slash, gt) => {
      let attrPart = "";
      if (attrs && attrs.trim()) {
        attrPart = attrs.replace(
          /([a-zA-Z-]+)(=)("[^"]*"|'[^']*'|[^\s>&]*)/g,
          (m2, name, eq, val) =>
            `<span class="hl-attr">${name}</span>${eq}<span class="hl-str">${val}</span>`,
        );
      }
      return `${lt}<span class="hl-tag">${tag}</span>${attrPart}${slash}${gt}`;
    });

    // Når det fantes tagger å farge, bytt inn; ellers la koden stå urørt.
    if (colored !== escaped) code.innerHTML = colored;
  };

  const copyCode = async (source, button) => {
    let ok = false;
    try {
      await navigator.clipboard.writeText(source);
      ok = true;
    } catch (err) {
      try {
        const area = document.createElement("textarea");
        area.value = source;
        area.style.position = "fixed";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.select();
        ok = document.execCommand("copy");
        area.remove();
      } catch (err2) {
        ok = false;
      }
    }
    button.textContent = ok ? "kopiert ✓" : "kopier mislyktes";
    const original = "⧉ kopi";
    window.setTimeout(() => {
      button.textContent = original;
    }, 1600);
  };

  document.querySelectorAll("pre").forEach((pre) => {
    if (pre.parentElement && pre.parentElement.classList.contains("code-box")) {
      return;
    }

    const code = pre.querySelector("code") || pre;

    // Wrapper-div slik at kopi-knappen ikke scroller med koden
    const box = document.createElement("div");
    box.className = "code-box";

    const button = document.createElement("button");
    button.type = "button";
    button.className = "code-copy";
    button.textContent = "⧉ kopi";

    box.appendChild(button);
    pre.replaceWith(box);
    box.appendChild(pre);

    highlightCode(code);

    const copyButton = button;
    button.addEventListener("click", () => copyCode(code.textContent, copyButton));
  });
})();