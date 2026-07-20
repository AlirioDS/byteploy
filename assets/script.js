(() => {
  "use strict";

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Año actual en el footer
  const year = $("#year");
  if (year) year.textContent = new Date().getFullYear();

  // Header: sombra al hacer scroll
  const header = $(".site-header");
  if (header) {
    const onScroll = () => header.classList.toggle("scrolled", window.scrollY > 8);
    addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

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
      const TYPE = 85, ERASE = 45, HOLD = 1800, GAP = 320;
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

  // Aparición suave al hacer scroll con stagger (progressive enhancement:
  // sin JS los elementos quedan visibles; la clase .reveal se agrega aquí)
  const targets = $$("[data-reveal]");
  if (targets.length) {
    if (reduced || !("IntersectionObserver" in window)) {
      targets.forEach((t) => t.classList.add("in"));
    } else {
      targets.forEach((t, i) => {
        t.classList.add("reveal");
        t.style.transitionDelay = (i % 4) * 70 + "ms";
      });
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

  // Formulario de contacto: envío AJAX al endpoint propio (/api/contact,
  // Cloudflare Pages Function que valida Turnstile y envía con Resend).
  // Sin JS, el <form> hace POST nativo al mismo endpoint (fallback funcional).
  const form = $("#contact-form");
  if (form) {
    const statusEl = $(".form-status", form);
    const btn = $(".form-submit", form);
    const setStatus = (msg, kind) => {
      statusEl.textContent = msg || "";
      statusEl.classList.toggle("is-err", kind === "err");
    };

    // Turnstile: el script de Cloudflare se carga recién cuando el usuario
    // interactúa con el formulario (no pesa en la carga inicial de la página).
    const tsBox = $(".cf-turnstile", form);
    const tsKey = tsBox ? tsBox.dataset.sitekey || "" : "";
    const tsReady = tsKey && !/PON-AQUI|SITE-KEY/i.test(tsKey);
    if (tsReady) {
      form.addEventListener(
        "focusin",
        () => {
          tsBox.style.minHeight = "65px"; // reserva el alto del widget
          const s = document.createElement("script");
          s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js";
          s.async = true;
          document.head.appendChild(s);
        },
        { once: true }
      );
    }

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      setStatus("", null);
      if (form.botcheck && form.botcheck.checked) return; // honeypot
      if (!form.checkValidity()) { form.reportValidity(); return; }
      if (!tsReady) {
        setStatus(form.dataset.config, "err"); // sitekey aún sin configurar
        return;
      }
      const data = Object.fromEntries(new FormData(form).entries());
      if (!data["cf-turnstile-response"]) {
        setStatus(form.dataset.captcha, "err"); // widget sin resolver todavía
        return;
      }
      const label = btn.textContent;
      btn.disabled = true;
      btn.textContent = form.dataset.sending || "…";
      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify(data),
        });
        const out = await res.json().catch(() => ({}));
        if (res.ok && out.success) {
          setStatus(form.dataset.ok, "ok");
          form.reset();
        } else {
          setStatus(out.message || form.dataset.err, "err");
        }
        if (window.turnstile) window.turnstile.reset(); // token es de un solo uso
      } catch (_) {
        setStatus(form.dataset.err, "err");
      } finally {
        btn.disabled = false;
        btn.textContent = label;
      }
    });
  }
})();
