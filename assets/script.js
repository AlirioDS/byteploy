(() => {
  "use strict";

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Año actual en el footer
  const year = $("#year");
  if (year) year.textContent = new Date().getFullYear();

  // Menú móvil
  const toggle = $(".nav-toggle");
  const menu = $("#nav-menu");
  if (toggle && menu) {
    const close = () => {
      document.body.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
    };
    toggle.addEventListener("click", () => {
      const open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    menu.addEventListener("click", (e) => {
      if (e.target.closest("a")) close();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") close();
    });
  }

  // Efecto máquina de escribir en el titular
  const word = $("#typeword");
  if (word && !reduced) {
    let words = [];
    try {
      words = JSON.parse(word.dataset.words || "[]");
    } catch (_) {
      words = [];
    }
    if (words.length > 1) {
      const TYPE = 75, ERASE = 42, HOLD = 1900, GAP = 350;
      let i = 1;
      const type = (w, n, done) => {
        word.textContent = w.slice(0, n);
        if (n < w.length) setTimeout(() => type(w, n + 1, done), TYPE);
        else done();
      };
      const erase = (done) => {
        const cur = word.textContent;
        if (cur.length) {
          word.textContent = cur.slice(0, -1);
          setTimeout(() => erase(done), ERASE);
        } else done();
      };
      const loop = () => {
        const w = words[i % words.length];
        i += 1;
        type(w, 0, () => setTimeout(() => erase(() => setTimeout(loop, GAP)), HOLD));
      };
      setTimeout(() => erase(loop), HOLD);
    }
  }

  // Aparición suave al hacer scroll (progressive enhancement:
  // sin JS los elementos quedan visibles, la clase .reveal se agrega aquí)
  const targets = $$("[data-reveal]");
  if (targets.length) {
    if (reduced || !("IntersectionObserver" in window)) {
      targets.forEach((t) => t.classList.add("in"));
    } else {
      targets.forEach((t) => t.classList.add("reveal"));
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("in");
              io.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
      );
      targets.forEach((t) => io.observe(t));
    }
  }
})();
