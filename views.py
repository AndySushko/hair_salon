# views.py
from __future__ import annotations
from typing import List
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
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background: #f4f4f4; }}
    .rowlink {{ cursor: pointer; color: #0b57d0; text-decoration: underline; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    input {{ width: 100%; padding: 8px; }}
    button {{ padding: 8px 12px; }}
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

<h2>Создать клиента</h2>
<form id="createForm" class="grid">
  <div><label>Фамилия</label><input name="last_name" required></div>
  <div><label>Имя</label><input name="first_name" required></div>
  <div><label>Отчество</label><input name="father_name" required></div>
  <div><label>Стрижек</label><input name="haircut_counter" type="number" min="0" required></div>
  <div><label>Скидка %</label><input name="discount" type="number" min="0" max="100" required></div>
  <div style="display:flex;align-items:end;"><button type="submit">Создать</button></div>
</form>

<h2>Список</h2>
<p>Клик по фамилии открывает полную карточку в новой вкладке (details).</p>
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

<script>window.__BOOT__ = {{}};</script>
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
