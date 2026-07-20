// Endpoint del formulario de contacto (Cloudflare Pages Function).
// Verifica Cloudflare Turnstile en el servidor (mismo patrón que altairum)
// y envía el correo con la API de Resend.
//
// Variables de entorno (Pages > Settings > Variables and Secrets):
//   TURNSTILE_SECRET_KEY  secreto del widget Turnstile (obligatoria)
//   RESEND_API_KEY        API key de Resend (obligatoria)
//   CONTACT_TO            destinatario, por defecto info@byteploy.com
//   CONTACT_FROM          remitente verificado en Resend, p. ej. "Web Byteploy <web@byteploy.com>"

const VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });

async function readBody(request) {
  const type = request.headers.get("Content-Type") || "";
  if (type.includes("application/json")) return request.json();
  const form = await request.formData();
  return Object.fromEntries(form.entries());
}

export async function onRequestPost({ request, env }) {
  let data;
  try {
    data = await readBody(request);
  } catch {
    return json({ success: false, message: "Solicitud inválida." }, 400);
  }

  // Honeypot: responder "ok" sin enviar nada.
  if (data.botcheck) return json({ success: true });

  const name = String(data.name || "").trim().slice(0, 200);
  const email = String(data.email || "").trim().slice(0, 200);
  const message = String(data.message || "").trim().slice(0, 5000);
  if (!name || !message || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json({ success: false, message: "Revisa los campos del formulario." }, 422);
  }

  if (!env.TURNSTILE_SECRET_KEY || !env.RESEND_API_KEY) {
    return json({ success: false, message: "Formulario en configuración." }, 503);
  }

  const verify = await fetch(VERIFY_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      secret: env.TURNSTILE_SECRET_KEY,
      response: data["cf-turnstile-response"] || "",
      remoteip: request.headers.get("CF-Connecting-IP") || undefined,
    }),
  });
  const verdict = await verify.json().catch(() => ({ success: false }));
  if (!verdict.success) {
    return json({ success: false, message: "No pudimos validar el captcha. Recarga e inténtalo de nuevo." }, 403);
  }

  const sent = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      from: env.CONTACT_FROM || "Web Byteploy <web@byteploy.com>",
      to: [env.CONTACT_TO || "info@byteploy.com"],
      reply_to: email,
      subject: `Nuevo contacto: ${name}`,
      text: `Nombre/empresa: ${name}\nEmail: ${email}\n\n${message}\n\n· Enviado desde el formulario de byteploy.com`,
    }),
  });
  if (!sent.ok) {
    return json({ success: false, message: "No pudimos enviar el mensaje. Escríbenos a info@byteploy.com." }, 502);
  }
  return json({ success: true });
}
