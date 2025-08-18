
#!/usr/bin/env python3
import argparse
import pandas as pd
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import re, os

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
    import re as _re
    words = _re.sub(r"[^a-zA-ZÁÉÍÓÚÜÑáéíóúüñ0-9 ]+", " ", str(text)).strip().split()
    return " ".join(words[:2]).title() if words else "Concepto"

def parse_date(x):
    x = str(x).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(x, fmt)
        except ValueError:
            pass
    raise ValueError(f"Fecha inválida: {x} (use dd/mm/yyyy)")

def format_ars(amount: float) -> str:
    s = f"{amount:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return s

def load_font(size, bold=False):
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def render_summary(df: pd.DataFrame, title: str, out_path: str, width=1080,
                   primary="#3B37A5", accent="#F2D20C", success="#0E8B3D",
                   logo_path: str=None):
    primary = hex_to_rgb(primary)
    accent = hex_to_rgb(accent)
    success = hex_to_rgb(success)
    text_color = (20, 24, 33)
    faint = (110, 116, 130)
    line_soft = (224, 229, 238)
    bg = (255, 255, 255)

    margin = 64
    row_h = 86
    title_font = load_font(60, bold=True)
    month_font = load_font(38, bold=True)
    header_font = load_font(34, bold=True)
    cell_font = load_font(40, bold=False)
    total_font = load_font(46, bold=True)

    unique_months = list(df["month_label"].unique())
    rows = len(df)
    top_block = 150
    height = margin*2 + top_block + len(unique_months)*(row_h) + rows*row_h + 140

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    y = margin
    title_x = margin
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            max_h = 110
            ratio = max_h / logo.height
            new_w = int(logo.width * ratio)
            logo = logo.resize((new_w, max_h), Image.LANCZOS)
            pad = 8
            framed = Image.new("RGBA", (new_w + pad*2, max_h + pad*2), (0,0,0,0))
            framed.paste(logo, (pad, pad), logo)
            img.paste(framed, (margin, y), framed)
            title_x = margin + framed.width + 24
        except Exception:
            pass

    draw.text((title_x, y+10), title, fill=primary, font=title_font)

    y += 120
    draw.line((margin, y, width-margin, y), fill=accent, width=4); y += 16

    x_date = margin
    x_concept = int(width*0.33)
    x_amount = int(width*0.74)
    right_margin = width - margin

    draw.text((x_date, y), "Fecha", fill=faint, font=header_font)
    draw.text((x_concept, y), "Concepto", fill=faint, font=header_font)
    draw.text((x_amount, y), "Monto", fill=faint, font=header_font)
    y += row_h - 10

    total = 0.0
    for i, month in enumerate(unique_months):
        bar_y = y - 18
        draw.line((margin, bar_y, right_margin, bar_y), fill=line_soft, width=2)
        month_color = success if i == 0 else primary
        draw.text((margin, y), month.upper(), fill=month_color, font=month_font)
        y += row_h - 12

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

    y += 4
    draw.line((margin, y, right_margin, y), fill=accent, width=4); y += 16
    draw.text((x_date, y), "Total", fill=primary, font=total_font)
    total_text = format_ars(total)
    tw = draw.textlength(total_text, font=total_font)
    draw.text((x_amount + (right_margin - x_amount - tw), y), total_text, fill=primary, font=total_font)

    img.save(out_path, quality=95)
    return out_path

def read_input(path: str) -> pd.DataFrame:
    if path.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)
    fecha_col = next((c for c in df.columns if c.lower().startswith("fecha")), None)
    concepto_col = next((c for c in df.columns if "concepto" in c.lower() or "comprob" in c.lower() or "descripcion" in c.lower()), None)
    monto_col = next((c for c in df.columns if "monto" in c.lower() or "importe" in c.lower()), None)
    if not (fecha_col and concepto_col and monto_col):
        raise ValueError("Columnas requeridas: Fecha, Concepto, Monto (o similares).")
    out = pd.DataFrame({
        "Fecha": df[fecha_col].apply(parse_date),
        "Concepto": df[concepto_col].astype(str),
        "Monto": pd.to_numeric(df[monto_col], errors="coerce").fillna(0.0),
    })
    out["Concepto_simplificado"] = out["Concepto"].apply(simplify_concept)
    out["month_label"] = out["Fecha"].dt.strftime("%B %Y").str.title()
    return out.sort_values(["Fecha", "Concepto_simplificado"]).reset_index(drop=True)

def main():
    ap = argparse.ArgumentParser(description="Generar imagen de resumen simple para WhatsApp.")
    ap.add_argument("input", help="CSV o Excel con columnas: Fecha, Concepto, Monto")
    ap.add_argument("-o", "--output", default="resumen.png", help="Ruta de salida (PNG)")
    ap.add_argument("-t", "--title", default="Resumen Paz Lopez", help="Título superior")
    ap.add_argument("--primary", default="#3B37A5", help="Color primario (hex)")
    ap.add_argument("--accent", default="#F2D20C", help="Color acento (hex)")
    ap.add_argument("--success", default="#0E8B3D", help="Color verde (hex)")
    ap.add_argument("--logo", default=None, help="Ruta a logo (PNG/JPG)")
    args = ap.parse_args()

    df = read_input(args.input)
    render_summary(df, args.title, args.output,
                   primary=args.primary, accent=args.accent, success=args.success,
                   logo_path=args.logo)
    print(f"✅ Imagen generada en: {args.output}")

if __name__ == "__main__":
    main()
