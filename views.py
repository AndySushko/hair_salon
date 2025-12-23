# views.py
from __future__ import annotations
from typing import List, Dict, Any
from hair_salon_lab1_task9 import Client


def page_layout(title: str, body: str, scripts: List[str]) -> str:
    scripts_tags = "\n".join([f'<script src="{s}"></script>' for s in scripts])
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 12px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background: #f4f4f4; }}
    .rowlink {{ cursor: pointer; color: #0b57d0; text-decoration: underline; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; max-width: 900px; }}
    input {{ width: 100%; padding: 8px; box-sizing: border-box; }}
    button {{ padding: 8px 12px; cursor: pointer; }}
    .topbar {{ display:flex; gap: 12px; align-items:center; }}
    .hint {{ color:#555; margin-top:8px; }}
  </style>
</head>
<body>
{body}
{scripts_tags}
</body>
</html>"""


def index_page(clients: List[Client]) -> str:
    rows = []
    for c in clients:
        rows.append(
            f"<tr data-id='{c.get_id()}'>"
            f"<td>{c.get_id()}</td>"
            f"<td class='rowlink'>{c.get_last_name()}</td>"
            f"<td>{c.get_first_name()}</td>"
            f"<td>{c.get_father_name()}</td>"
            f"<td>{c.get_haircut_counter()}</td>"
            f"<td>{c.get_discount()}</td>"
            f"<td><button class='delbtn'>Удалить</button></td>"
            f"</tr>"
        )

    body = f"""
<h1>Clients CRUD (MVC без фреймворка)</h1>

<div class="topbar">
  <button id="openCreate">Добавить клиента</button>
</div>

<table id="clientsTable">
  <thead>
    <tr>
      <th>ID</th><th>Фамилия</th><th>Имя</th><th>Отчество</th><th>Стрижек</th><th>Скидка</th><th></th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""
    return page_layout("Clients", body, scripts=["/static/main.js"])


def details_page(client_id: int) -> str:
    body = f"""
<h1>Client details</h1>
<p>Client ID: <b>{client_id}</b></p>

<div id="card">Загрузка...</div>

<h2>Редактировать</h2>
<form id="updateForm" class="grid">
  <div><label>Фамилия</label><input name="last_name" required></div>
  <div><label>Имя</label><input name="first_name" required></div>
  <div><label>Отчество</label><input name="father_name" required></div>
  <div><label>Стрижек</label><input name="haircut_counter" type="number" min="0" required></div>
  <div><label>Скидка %</label><input name="discount" type="number" min="0" max="100" required></div>
  <div style="display:flex;align-items:end;"><button type="submit">Сохранить</button></div>
</form>

<script>window.__DETAILS__ = {{ client_id: {client_id} }};</script>
"""
    return page_layout(f"Client {client_id}", body, scripts=["/static/details.js"])


# --------- NEW WINDOW: CREATE CLIENT ---------

def new_client_page(errors: Dict[str, str], values: Dict[str, Any]) -> str:
    def err(k: str) -> str:
        if errors.get(k):
            return f"<div style='color:#b00020;font-size:12px'>{errors[k]}</div>"
        return ""

    def val(k: str) -> str:
        return str(values.get(k, "") or "")

    all_err = ""
    if errors.get("__all__"):
        all_err = f"<p style='color:#b00020'><b>{errors['__all__']}</b></p>"

    body = f"""
<h1>Создать клиента</h1>
{all_err}

<form id="createForm" class="grid">
  <div><label>Фамилия</label><input name="last_name" value="{val('last_name')}" required>{err('last_name')}</div>
  <div><label>Имя</label><input name="first_name" value="{val('first_name')}" required>{err('first_name')}</div>
  <div><label>Отчество</label><input name="father_name" value="{val('father_name')}" required>{err('father_name')}</div>
  <div><label>Стрижек</label><input name="haircut_counter" type="number" min="0" value="{val('haircut_counter')}" required>{err('haircut_counter')}</div>
  <div><label>Скидка %</label><input name="discount" type="number" min="0" max="100" value="{val('discount')}" required>{err('discount')}</div>
  <div style="display:flex;align-items:end;">
    <button type="submit">Создать</button>
  </div>
</form>

<p><a href="#" id="closeWin">Закрыть</a></p>
"""
    return page_layout("New Client", body, scripts=["/static/new_client.js"])


def new_client_success_page(new_id: int) -> str:
    body = f"""
<h1>Готово</h1>
<p>Клиент создан. ID: <b>{new_id}</b></p>
<p>Окно закроется автоматически.</p>

<script>
  // уведомляем главное окно (обновить таблицу)
  try {{
    const bc = new BroadcastChannel("clients_channel");
    bc.postMessage({{ type: "created", id: {new_id} }});
    bc.close();
  }} catch (e) {{}}

  // запасной способ (если окно открыто через window.open)
  try {{
    if (window.opener) {{
      window.opener.postMessage({{ type: "created", id: {new_id} }}, "*");
    }}
  }} catch (e) {{}}

  window.close();
</script>
"""
    return page_layout("Created", body, scripts=[])
