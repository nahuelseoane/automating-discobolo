
#!/usr/bin/env python3
import argparse
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import math
import os
import re

# ---------- Helpers ----------

KEYWORD_MAP = [
    (r"tenis.*mes", "Tenis Mes"),
    (r"cuota.*activa", "Cuota Activa"),
    (r"luz", "Luz"),
    (r"invita|invitado", "Invitado"),
    (r"torneo", "Torneo"),
]

def simplify_concept(text: str) -> str:
    t = str(text).lower()
    for patt, label in KEYWORD_MAP:
        if re.search(patt, t):
            return label
    # Fallback: take first two words capitalized
    words = re.sub(r"[^a-zA-ZÁÉÍÓÚÜÑáéíóúüñ0-9 ]+", " ", str(text)).strip().split()
    return " ".join(words[:2]).title() if words else "Concepto"

def parse_date(x):
    # Supports dd/mm/yyyy or yyyy-mm-dd
    x = str(x).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(x, fmt)
        except ValueError:
            pass
    # Try dd/mm/yy
    for fmt in ("%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(x, fmt)
        except ValueError:
            pass
    raise ValueError(f"Fecha inválida: {x} (use dd/mm/yyyy)")

def format_ars(amount: float) -> str:
    # Argentine style: thousands dot, comma decimals
    s = f"{amount:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

# ---------- Rendering ----------

def load_font(size, bold=False):
    # Try to use DejaVu fonts (available by default)
    try:
        if bold:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def render_summary(df: pd.DataFrame, title: str, out_path: str, width=1080):
    # Prepare canvas
    margin = 64
    row_h = 86
    section_gap = 18
    line_color = (210, 214, 220)
    text_color = (20, 24, 33)
    faint = (120, 126, 140)
    bg = (255, 255, 255)

    title_font = load_font(64, bold=True)
    month_font = load_font(40, bold=True)
    header_font = load_font(36, bold=True)
    cell_font = load_font(40, bold=False)
    total_font = load_font(48, bold=True)

    # Compute height
    unique_months = list(df["month_label"].unique())
    rows = len(df)
    height = margin*2 + 90 + len(unique_months)* (row_h + section_gap) + rows*row_h + 140

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    x_date = margin
    x_concept = int(width*0.32)
    x_amount = int(width*0.75)
    right_margin = width - margin

    y = margin

    # Title
    draw.text(((width - draw.textlength(title, font=title_font))/2, y), title, fill=text_color, font=title_font)
    y += 90

    # Table Header
    draw.line((margin, y, right_margin, y), fill=line_color, width=3); y += 10
    draw.text((x_date, y), "Fecha", fill=faint, font=header_font)
    draw.text((x_concept, y), "Concepto", fill=faint, font=header_font)
    draw.text((x_amount, y), "Monto", fill=faint, font=header_font)
    y += row_h

    # Content grouped by month
    total = 0.0
    for month in unique_months:
        # Month separator
        draw.line((margin, y-20, right_margin, y-20), fill=line_color, width=2)
        draw.text((margin, y), month.upper(), fill=text_color, font=month_font)
        y += row_h - 8

        sub = df[df["month_label"] == month]
        for _, r in sub.iterrows():
            date_str = r["Fecha"].strftime("%d/%m/%Y")
            concept = r["Concepto_simplificado"]
            amount = float(r["Monto"])
            total += amount

            draw.text((x_date, y), date_str, fill=text_color, font=cell_font)
            draw.text((x_concept, y), concept, fill=text_color, font=cell_font)

            amt_text = format_ars(amount)
            tw = draw.textlength(amt_text, font=cell_font)
            draw.text((x_amount + (right_margin - x_amount - tw), y), amt_text, fill=text_color, font=cell_font)

            y += row_h

    # Total line
    y += 6
    draw.line((margin, y, right_margin, y), fill=line_color, width=3)
    y += 24
    draw.text((x_date, y), "Total", fill=text_color, font=total_font)
    total_text = format_ars(total)
    tw = draw.textlength(total_text, font=total_font)
    draw.text((x_amount + (right_margin - x_amount - tw), y), total_text, fill=text_color, font=total_font)

    img.save(out_path, quality=95)
    return out_path

def read_input(path: str) -> pd.DataFrame:
    # Expect columns: Fecha, Concepto, Monto
    if path.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    # Normalize columns
    cols = {c.lower().strip(): c for c in df.columns}
    # Try mapping
    fecha_col = next((c for c in df.columns if c.lower().startswith("fecha")), None)
    concepto_col = next((c for c in df.columns if "concepto" in c.lower() or "comprob" in c.lower() or "descripcion" in c.lower()), None)
    monto_col = next((c for c in df.columns if "monto" in c.lower() or "importe" in c.lower()), None)
    if not (fecha_col and concepto_col and monto_col):
        raise ValueError("El archivo debe tener columnas 'Fecha', 'Concepto' y 'Monto' (o similares).")
    # Build clean dataframe
    out = pd.DataFrame({
        "Fecha": df[fecha_col].apply(parse_date),
        "Concepto": df[concepto_col].astype(str),
        "Monto": pd.to_numeric(df[monto_col], errors="coerce").fillna(0.0),
    })
    # Simplify concept and month label
    out["Concepto_simplificado"] = out["Concepto"].apply(simplify_concept)
    out["month_label"] = out["Fecha"].dt.strftime("%B %Y").str.title()
    return out.sort_values(["Fecha", "Concepto_simplificado"]).reset_index(drop=True)

def main():
    ap = argparse.ArgumentParser(description="Generar imagen de resumen simple para WhatsApp.")
    ap.add_argument("input", help="CSV o Excel con columnas: Fecha, Concepto, Monto")
    ap.add_argument("-o", "--output", default="resumen.png", help="Ruta de salida (PNG)")
    ap.add_argument("-t", "--title", default="Resumen Paz Lopez", help="Título superior")
    args = ap.parse_args()

    df = read_input(args.input)
    render_summary(df, args.title, args.output)
    print(f"✅ Imagen generada en: {args.output}")

if __name__ == "__main__":
    main()
