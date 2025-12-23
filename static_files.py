# static_files.py
MAIN_JS = r"""
(function () {
  const table = document.getElementById("clientsTable");

  // открыть окно создания
  const openBtn = document.getElementById("openCreate");
  if (openBtn) openBtn.addEventListener("click", () => window.open("/clients/new", "_blank"));

  // обновить главную при created/updated
  try {
    const bc = new BroadcastChannel("clients_channel");
    bc.onmessage = (ev) => {
      if (!ev.data) return;
      if (ev.data.type === "created" || ev.data.type === "updated") location.reload();
    };
  } catch (e) {}

  window.addEventListener("message", (ev) => {
    if (!ev.data) return;
    if (ev.data.type === "created" || ev.data.type === "updated") location.reload();
  });

  if (!table) return;

  table.addEventListener("click", async (e) => {
    const tr = e.target.closest("tr");
    if (!tr) return;
    const id = tr.getAttribute("data-id");

    if (e.target.classList.contains("delbtn")) {
      await fetch(`/api/clients/${id}`, { method: "DELETE" });
      location.reload();
      return;
    }

    if (e.target.classList.contains("editbtn")) {
      window.open(`/clients/${id}/edit`, "_blank");
      return;
    }
  });
})();
"""

CLIENT_FORM_JS = r"""
(function () {
  const cfg = window.__FORM__;
  if (!cfg) return;

  const form = document.getElementById("clientForm");
  const closeBtn = document.getElementById("closeWin");

  if (closeBtn) closeBtn.addEventListener("click", (e) => { e.preventDefault(); window.close(); });

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());

    const res = await fetch(cfg.post_url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    // сервер возвращает HTML: форма с ошибками или success page
    const html = await res.text();
    document.open();
    document.write(html);
    document.close();
  });
})();
"""
