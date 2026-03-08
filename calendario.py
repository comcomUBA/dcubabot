"""Calendario académico de Exactas UBA - lógica copiada de calendarioacademico."""

from __future__ import annotations

import hashlib
import html
import os
import re
import time
from dataclasses import dataclass, field
from datetime import date
from html import escape as html_escape
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from telegram.constants import ParseMode

if TYPE_CHECKING:
    from telegram import Update

    from context_types import DCUBACallbackContext

URL = "https://exactas.uba.ar/calendario-academico/"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
CACHE_TTL = 3600
CONTENT_PATTERNS = (
    r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</article>',
    r"<article[^>]*>(.*?)</article>",
    r"<main[^>]*>(.*?)</main>",
)
TAGS_TO_REMOVE = ("script", "style", "nav", "header", "footer")
NAV_KEYWORDS = frozenset(
    {
        "inicio",
        "institucional",
        "enseñanza",
        "investigación",
        "extensión",
        "futuros estudiantes",
        "estudiantes grado",
        "contacto",
        "seguinos",
        "buscar",
    }
)
PATRON_ACTIVIDAD_FECHAS = re.compile(
    r"(.+?):\s*((?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+[\d/]+\s*(?:al\s+(?:lunes|martes|miércoles|jueves|viernes|sábado|domingo)\s+[\d/]+)?)",
    re.IGNORECASE,
)
PATRON_FECHA = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")
MESES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


@dataclass
class SeccionCalendario:
    nombre: str
    categoria: str
    items: list[tuple[str, str]] = field(default_factory=list)


def _cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path("~/.cache").expanduser())
    return Path(base) / "calendario_academico"


def _cache_path(url: str) -> Path:
    key = hashlib.sha256(url.encode()).hexdigest()[:16]
    return _cache_dir() / f"calendario_{key}.html"


def _fetch_html(*, use_cache: bool = True) -> str:
    if use_cache:
        path = _cache_path(URL)
        if path.exists() and time.time() - path.stat().st_mtime < CACHE_TTL:
            return path.read_text(encoding="utf-8", errors="replace")
    r = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=15)
    r.raise_for_status()
    html_content = r.text
    if use_cache:
        try:
            _cache_dir().mkdir(parents=True, exist_ok=True)
            _cache_path(URL).write_text(html_content, encoding="utf-8")
        except OSError:
            pass
    return html_content


def _extract_content(html_content: str) -> str:
    for pattern in CONTENT_PATTERNS:
        m = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1)
    m = re.search(r"<body[^>]*>(.*?)</body>", html_content, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else html_content


def _remove_tags(content: str) -> str:
    for tag in TAGS_TO_REMOVE:
        content = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", content, flags=re.DOTALL | re.IGNORECASE)
    return content


def _clean_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw)
    text = html.unescape(text.strip())
    return re.sub(r"\s+", " ", text)


def _is_nav(text: str) -> bool:
    if len(text) >= 50:
        return False
    return any(kw in text.lower() for kw in NAV_KEYWORDS)


def _extract_raw(html_content: str) -> str:
    content = _remove_tags(_extract_content(html_content))
    lines, seen = [], set()
    for level in range(1, 7):
        prefix = "\n" + ("=" * 2 if level <= 2 else "=") + " "
        for m in re.finditer(
            rf"<h{level}[^>]*>(.*?)</h{level}>", content, re.DOTALL | re.IGNORECASE
        ):
            t = _clean_text(m.group(1))
            if t and t not in seen and not _is_nav(t):
                seen.add(t)
                lines.append((m.start(), prefix, t))
    for m in re.finditer(r"<p[^>]*>(.*?)</p>", content, re.DOTALL | re.IGNORECASE):
        t = _clean_text(m.group(1))
        if len(t) > 2 and t not in seen and not _is_nav(t):
            seen.add(t)
            lines.append((m.start(), "", t))
    for m in re.finditer(r"<li[^>]*>(.*?)</li>", content, re.DOTALL | re.IGNORECASE):
        t = _clean_text(m.group(1))
        if t and t not in seen:
            seen.add(t)
            lines.append((m.start(), "  - ", t))
    lines.sort(key=lambda x: x[0])
    return "\n".join(p + t for _, p, t in lines).strip()


def _categorizar(titulo: str) -> str:
    t = titulo.lower()
    if any(k in t for k in ("exámenes", "turno")):
        return "examenes"
    if any(k in t for k in ("inscripción", "preinscripción")):
        return "inscripciones"
    if any(k in t for k in ("cuatrimestre", "bimestre", "curso de verano", "curso de invierno")):
        return "clases"
    if "feriados" in t:
        return "feriados"
    if "recesos" in t:
        return "recesos"
    return "otras"


def _parsear_linea(linea: str) -> list[tuple[str, str]]:
    out = []
    for m in PATRON_ACTIVIDAD_FECHAS.finditer(linea):
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out or ([(linea.strip(), "")] if linea.strip() else [])


def _parsear_secciones(raw: str) -> list[SeccionCalendario]:
    secciones, actual = [], None
    for ln in (ln.strip() for ln in raw.split("\n") if ln.strip()):
        if ln.startswith("=="):
            titulo = ln.lstrip("=").strip()
            if titulo and len(titulo) > 2:
                actual = SeccionCalendario(titulo, _categorizar(titulo))
                secciones.append(actual)
        elif ln.startswith("="):
            titulo = ln.lstrip("=").strip()
            if titulo:
                actual = SeccionCalendario(titulo, _categorizar(titulo))
                secciones.append(actual)
        elif actual:
            texto = ln.lstrip("- ").lstrip("• ").strip()
            for a, f in _parsear_linea(texto):
                actual.items.append((a, f))
    return secciones


def _filtrar_solo_examenes(secciones: list[SeccionCalendario]) -> list[SeccionCalendario]:
    return [s for s in secciones if s.categoria == "examenes"]


def _extraer_insc_exam(items: list[tuple[str, str]]) -> tuple[str, str]:
    insc, exam = "", ""
    for a, f in items:
        al = a.lower()
        if "inscripción" in al or "inscripcion" in al:
            insc = f
        elif "exámenes" in al or "examenes" in al:
            exam = f
    return insc, exam


def _es_titulo_turno(nombre: str) -> bool:
    return bool(re.match(r"^EXÁMENES\s*[-]\s*TURNO\s+DE\s+", nombre, re.IGNORECASE))


def _agrupar_examenes(
    secciones: list[SeccionCalendario],
) -> list[tuple[str | None, list[tuple[str, str, str]]]]:
    grupos: list[tuple[str | None, list[tuple[str, str, str]]]] = []
    filas: list[tuple[str, str, str]] = []
    titulo: str | None = None
    for sec in secciones:
        if sec.categoria != "examenes":
            if filas:
                grupos.append((titulo, filas))
                filas, titulo = [], None
            continue
        if not sec.items:
            if filas:
                grupos.append((titulo, filas))
                filas = []
            titulo = sec.nombre
            continue
        if _es_titulo_turno(sec.nombre) and filas:
            grupos.append((titulo, filas))
            filas, titulo = [], sec.nombre
        insc, exam = _extraer_insc_exam(sec.items)
        if insc or exam:
            turno = (sec.nombre[:30] + "…") if len(sec.nombre) > 32 else sec.nombre
            filas.append((turno, insc or "—", exam or "—"))
            if titulo is None and "turno" in sec.nombre.lower():
                titulo = sec.nombre
    if filas:
        grupos.append((titulo, filas))
    return grupos


def _extraer_mes_año(fechas: str) -> tuple[int, int] | None:
    m = PATRON_FECHA.search(fechas)
    if not m:
        return None
    _dd, mm, yyyy = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return (yyyy, mm) if 1 <= mm <= 12 else None


def _agrupar_por_mes(secciones: list[SeccionCalendario]) -> list[tuple[str, list[tuple[str, str]]]]:  # noqa: C901
    grupos_exam = _agrupar_examenes(secciones)
    items_por_mes: dict[tuple[int, int], list[tuple[str, str]]] = {}

    def agregar(act: str, fechas: str, clave: tuple[int, int] | None = None) -> None:
        if not fechas or fechas == "—":
            return
        k = clave or _extraer_mes_año(fechas) or (9999, 99)
        items_por_mes.setdefault(k, []).append((act, fechas))

    for _, filas in grupos_exam:
        for turno, insc, exam in filas:
            if insc and insc != "—":
                agregar(f"{turno} - Inscripción", insc, _extraer_mes_año(insc))
            if exam and exam != "—":
                agregar(turno, exam, _extraer_mes_año(exam))
    for sec in secciones:
        if sec.categoria in ("inscripciones", "clases"):
            for act, fechas in sec.items:
                if fechas:
                    agregar(act, fechas, _extraer_mes_año(fechas))

    resultado = []
    for año, mes in sorted(items_por_mes.keys(), key=lambda k: (k[0], k[1])):
        nombre = "Otros" if (año, mes) == (9999, 99) else f"{MESES[mes - 1].upper()} {año}"
        resultado.append((nombre, items_por_mes[(año, mes)]))
    return resultado


def _extraer_turno_desde_nombre(nombre: str) -> str | None:
    """Extrae el turno desde cualquier sección: '1er Llamado del Turno de Febrero-Marzo' o 'EXÁMENES - TURNO DE ABRIL'."""
    # Formato "EXÁMENES - TURNO DE X" o "TURNO DE X"
    m = re.search(r"TURNO\s+DE\s+([A-Za-záéíóúñ]+(?:-[A-Za-záéíóúñ]+)?)", nombre, re.IGNORECASE)
    if m:
        return m.group(1).strip().title()
    # Formato "Turno Febrero-Marzo" (sin "de")
    m = re.search(r"Turno\s+([A-Za-záéíóúñ]+(?:-[A-Za-záéíóúñ]+)?)", nombre, re.IGNORECASE)
    if m:
        return m.group(1).strip().title()
    return None


def _agrupar_solo_examenes_por_turno(
    secciones: list[SeccionCalendario],
) -> list[tuple[str, int, list[str]]]:
    """Agrupa por turno extrayendo el nombre de cada sección. Abril, Mayo, Septiembre, Octubre son turnos aparte."""
    turnos: dict[tuple[str, int], list[str]] = {}

    for sec in secciones:
        if sec.categoria != "examenes":
            continue
        nombre_turno = _extraer_turno_desde_nombre(sec.nombre)
        if not nombre_turno:
            continue
        _insc, exam = _extraer_insc_exam(sec.items)
        if exam and exam != "—":
            ma = _extraer_mes_año(exam)
            if not ma:
                continue
            año, _mes = ma
            clave = (nombre_turno, año)
            turnos.setdefault(clave, []).append(exam)

    # Ordenar por fecha del primer examen
    resultado = []
    for (nombre_turno, año), exams in turnos.items():
        if not exams:
            continue
        ma = _extraer_mes_año(exams[0])
        if not ma:
            continue
        _, mes = ma
        orden = (año, mes)
        resultado.append((orden, nombre_turno, año, exams))

    resultado.sort(key=lambda x: x[0])
    return [(nombre, año, items) for _orden, nombre, año, items in resultado]


def _extraer_fechas_cortas(fechas_str: str) -> str:
    """Extrae fechas en formato dd/mm desde un texto como 'lunes 15/12/2025' o rangos."""
    fechas = []
    for m in PATRON_FECHA.finditer(fechas_str):
        dd, mm = int(m.group(1)), int(m.group(2))
        if 1 <= mm <= 12 and 1 <= dd <= 31:
            fechas.append(f"{dd}/{mm}")
    if not fechas:
        return ""
    if len(fechas) == 1:
        return fechas[0]
    return f"{fechas[0]} - {fechas[-1]}"


def _primera_fecha_completa(fechas_str: str) -> date | None:
    """Devuelve (año, mes, día) de la primera fecha en el string, o None."""
    m = PATRON_FECHA.search(fechas_str)
    if not m:
        return None
    dd, mm, yyyy = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if 1 <= mm <= 12 and 1 <= dd <= 31:
        return date(yyyy, mm, dd)
    return None


def _buscar_fecha_mas_cercana(
    date_lines: list[tuple[date, str]], hoy: date
) -> tuple[date, str] | None:
    """Devuelve (date, line) de la fecha de final más cercana en el futuro, o None."""
    candidato = None
    for d, line in date_lines:
        if d >= hoy and (candidato is None or d < candidato[0]):
            candidato = (d, line)
    return candidato


def _construir_html_con_destacado(
    out: list[tuple[str, str]],
    candidato: tuple[date, str] | None,
) -> str:
    """Construye el HTML escapando y poniendo en negrita la línea más cercana."""
    partes = []
    for typ, content in out:
        safe = html_escape(content)
        if typ == "fecha" and candidato and content == candidato[1]:
            partes.append(f"<b>{safe}</b>")
        else:
            partes.append(safe)
    return "\n".join(partes) + "\n" if partes else ""


def _formatear_solo_examenes(secciones: list[SeccionCalendario]) -> str:
    """Formato por turno (ej. Febrero-Marzo), no por mes. Llamado solo si hay más de uno. La más cercana en negrita."""
    grupos = _agrupar_solo_examenes_por_turno(secciones)
    ordinals = ("1er", "2do", "3er", "4to", "5to")
    hoy = date.today()
    out = []
    date_lines = []
    año_actual = None

    for nombre_turno, año, items in grupos:
        año_str = str(año)
        if año_str != año_actual:
            año_actual = año_str
            out.append(("txt", f"Año— {año_str}"))
        out.append(("txt", nombre_turno))

        añadir_llamado = len(items) > 1
        for i, fechas_str in enumerate(items):
            fecha_corta = _extraer_fechas_cortas(fechas_str)
            if not fecha_corta:
                continue
            sufijo = f" ({ordinals[i]} llamado)" if añadir_llamado and i < len(ordinals) else ""
            line = f"  {fecha_corta}{sufijo}"
            out.append(("fecha", line))
            if d := _primera_fecha_completa(fechas_str):
                date_lines.append((d, line))

    candidato = _buscar_fecha_mas_cercana(date_lines, hoy)
    return _construir_html_con_destacado(out, candidato)


def _formatear_fechas_finales(secciones: list[SeccionCalendario]) -> str:
    out = ["\n  Calendario Académico · FCEN · UBA\n"]
    for nombre_mes, items in _agrupar_por_mes(secciones):
        out.append(f"  {nombre_mes}")
        out.append("  " + "─" * min(len(nombre_mes), 72))
        col_act = min(48, max((len(a) for a, _ in items if a), default=1))
        col_fechas = 38
        out.append(f"  │ {'Actividad':<{col_act}} │ {'Fechas':<{col_fechas}} │")
        out.append(f"  ├{'─' * (col_act + 2)}┼{'─' * (col_fechas + 2)}┤")
        for act, fechas in items:
            act_corta = (act[:45] + "…") if len(act) > 48 else act
            out.append(f"  │ {act_corta:<{col_act}} │ {fechas:<{col_fechas}} │")
        out.append(f"  └{'─' * (col_act + 2)}┴{'─' * (col_fechas + 2)}┘\n")
    return "\n".join(out).rstrip() + "\n"


def _split_for_telegram(text: str, max_len: int = 4000) -> list[str]:
    chunks = []
    while len(text) > max_len:
        idx = text.rfind("\n", 0, max_len)
        if idx <= 0:
            idx = max_len
        chunks.append(text[:idx].strip())
        text = text[idx:].lstrip()
    if text.strip():
        chunks.append(text.strip())
    return chunks


async def fechafinales(update: Update, context: DCUBACallbackContext) -> None:
    """Muestra las fechas de exámenes del calendario académico de Exactas."""
    if update.message is None:
        return
    msg = await update.message.reply_text("Bancá, busco las fechas...", do_quote=False)
    context.sent_messages.append(msg)

    try:
        html = _fetch_html(use_cache=True)
        raw = _extract_raw(html)
        secciones = _parsear_secciones(raw)
        filtradas = _filtrar_solo_examenes(secciones)
        texto = _formatear_solo_examenes(filtradas)
    except Exception as e:
        await context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=msg.message_id,
            text=f"No pude obtener las fechas: {e}",
        )
        return

    if not texto.strip():
        await context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=msg.message_id,
            text="No encontré fechas de finales.",
        )
        return

    chunks = _split_for_telegram(texto)
    for i, chunk in enumerate(chunks):
        if i == 0:
            await context.bot.edit_message_text(
                chat_id=msg.chat_id,
                message_id=msg.message_id,
                text=chunk,
                parse_mode=ParseMode.HTML,
            )
        else:
            m = await context.bot.send_message(
                chat_id=msg.chat_id,
                text=chunk,
                parse_mode=ParseMode.HTML,
            )
            context.sent_messages.append(m)
