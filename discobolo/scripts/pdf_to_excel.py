import re
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd
import typer
from openpyxl import Workbook, load_workbook
from openpyxl.chart import PieChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows

app = typer.Typer(help="Genera resumen")


# ------ Helpers -------
def _to_float(x) -> float:
    """Parse numbers whether they come like 52.000,00 or 52000.00 or '52,000.00'"""
    if pd.isna(x):
        return 0.0
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip()
    if not s:
        return 0.0
    # Standarize decimal separator to dot, remove thousands separators
    # Try the common cases:
    # 1) 52.000,00 (ES format) -> 52000.00
    if re.match(r"^\d{1,3}(\. \d{3})+,\d{2}$", s):
        s = s.replace(".", "").replace(",", ".")
    # 2) 52,000.00 (EN format with comma thousands)
    elif re.match(r"^\d{1,3}(,\d{3})+\.\d{2}$", s):
        s = s.replace(",", "")
    # 3) 52000,00 -> 52000.00
    elif re.match(r"^\d+,\d{2}$", s):
        s = s.replace(",", ".")
    # 4) 52000.00 -> keep
    # 5) 52000 -> convert safely
    elif re.match(r"^\d+$", s):
        pass
    try:
        return float(s)
    except ValueError:
        return 0.0
