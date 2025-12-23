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

  // обновить главную при успешном создании в другой вкладке
  try {
    const bc = new BroadcastChannel("clients_channel");
    bc.onmessage = (ev) => {
      if (ev.data && ev.data.type === "created") {
        location.reload();
      }
    };
  } catch (e) {}

  // запасной вариант
  window.addEventListener("message", (ev) => {
    if (ev.data && ev.data.type === "created") {
      location.reload();
    }
  });

  // delete / open details
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

      if (e.target.classList.contains("rowlink")) {
        window.open(`/clients/${id}`, "_blank");
      }
    });
  }
})();
"""

DETAILS_JS = r"""
(function () {
  const id = window.__DETAILS__?.client_id;
  if (!id) return;

  const card = document.getElementById("card");
  const form = document.getElementById("updateForm");

  function renderClient(c) {
    card.innerHTML = `
      <div style="border:1px solid #ddd; padding:12px;">
        <div><b>${c.last_name} ${c.first_name} ${c.father_name}</b></div>
        <div>ID: ${c.id}</div>
        <div>Стрижек: ${c.haircut_counter}</div>
        <div>Скидка: ${c.discount}%</div>
      </div>
    `;
    form.last_name.value = c.last_name;
    form.first_name.value = c.first_name;
    form.father_name.value = c.father_name;
    form.haircut_counter.value = c.haircut_counter;
    form.discount.value = c.discount;
  }

  function renderDeleted() {
    card.innerHTML = "<b>Клиент удалён или не найден.</b>";
  }

  // Observer через SSE:
  const es = new EventSource(`/api/clients/${id}/subscribe`);
  es.addEventListener("client", (ev) => renderClient(JSON.parse(ev.data)));
  es.addEventListener("deleted", () => renderDeleted());

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const res = await fetch(`/api/clients/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) alert("Ошибка обновления (возможно клиент не уникален)");
  });
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

    // сервер возвращает HTML (форма с ошибками или success page)
    const html = await res.text();
    document.open();
    document.write(html);
    document.close();
  });
})();
"""
