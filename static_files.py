# static_files.py
MAIN_JS = r"""
(function () {
  const table = document.getElementById("clientsTable");

  // открыть окно создания
  const openBtn = document.getElementById("openCreate");
  if (openBtn) {
    openBtn.addEventListener("click", () => {
      window.open("/clients/new", "_blank");
    });
  }

  // обновить главную при успешном создании/обновлении в другой вкладке
  try {
    const bc = new BroadcastChannel("clients_channel");
    bc.onmessage = (ev) => {
      if (!ev.data) return;
      if (ev.data.type === "created" || ev.data.type === "updated") {
        location.reload();
      }
    };
  } catch (e) {}

  // запасной вариант
  window.addEventListener("message", (ev) => {
    if (!ev.data) return;
    if (ev.data.type === "created" || ev.data.type === "updated") {
      location.reload();
    }
  });

  // delete / edit
  if (table) {
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

      // (опционально) клик по фамилии тоже можно считать "edit"
      if (e.target.classList.contains("rowlink")) {
        window.open(`/clients/${id}/edit`, "_blank");
      }
    });
  }
})();
"""

NEW_CLIENT_JS = r"""
(function () {
  const form = document.getElementById("createForm");
  const closeBtn = document.getElementById("closeWin");

  if (closeBtn) closeBtn.addEventListener("click", (e) => { e.preventDefault(); window.close(); });

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());

    const res = await fetch("/clients/new", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const html = await res.text();
    document.open();
    document.write(html);
    document.close();
  });
})();
"""

EDIT_CLIENT_JS = r"""
(function () {
  const id = window.__EDIT__?.client_id;
  if (!id) return;

  const form = document.getElementById("editForm");
  const closeBtn = document.getElementById("closeWin");

  if (closeBtn) closeBtn.addEventListener("click", (e) => { e.preventDefault(); window.close(); });

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());

    // POST на HTML-эндпоинт /clients/<id>/edit
    const res = await fetch(`/clients/${id}/edit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const html = await res.text();
    document.open();
    document.write(html);
    document.close();
  });
})();
"""
