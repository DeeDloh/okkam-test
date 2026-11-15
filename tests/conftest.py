"""Общий HTTP-клиент и таблица времени запросов."""

from datetime import datetime
from pathlib import Path
from statistics import mean, median
from zoneinfo import ZoneInfo

import httpx
import pytest


@pytest.fixture(scope="session")
def api_client():
    with httpx.Client(timeout=30) as client:
        yield client


@pytest.fixture(scope="session")
def timings(request):
    rows = []
    yield rows

    if not rows:
        return

    timestamp = datetime.now(ZoneInfo("Europe/Moscow")).isoformat(timespec="seconds")
    lines = [
        "# Время ответов API",
        "",
        f"Замер: {timestamp}. Адрес: {rows[0][2]}.",
        "",
        "Последовательные запросы с переиспользованием HTTP-соединения, без прогрева.",
        "Время включает HTTP-запрос и получение ответа; "
        "чтение CSV и проверки исключены.",
        "Это время ответа API с точки зрения клиента, а не только время SQL.",
        "В таблице только сценарии, где все ответы прошли проверки.",
        "",
        "| Сценарий | Запросов | Мин., мс | Среднее, мс | Медиана, мс | Макс., мс |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, samples, _ in rows:
        lines.append(
            f"| {name} | {len(samples)} | {min(samples):.3f} | "
            f"{mean(samples):.3f} | {median(samples):.3f} | {max(samples):.3f} |"
        )

    report = Path(__file__).with_name("timings.md")
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")

    terminal = request.config.pluginmanager.get_plugin("terminalreporter")
    if terminal:
        terminal.write_sep("=", "Время ответов API")
        for line in lines[9:]:
            terminal.write_line(line)
        terminal.write_line(f"Отчёт: {report}")
