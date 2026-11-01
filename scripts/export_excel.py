"""scripts/export_excel.py — 수집 데이터를 엑셀 파일로 출력"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

# CWE-1236(수식 주입) 방지: 크롤러는 신뢰할 수 없는 웹 데이터를 엑셀에 넣는다.
# 아래 문자로 시작하는 문자열 셀은 스프레드시트(Excel·LibreOffice·Sheets)나 CSV 재변환 시
# 수식으로 실행될 수 있다(데이터 유출·DDE 명령). 그런 값 앞에 ' 를 붙여 텍스트로 강제한다(OWASP 권고).
_FORMULA_TRIGGERS = ("=", "+", "-", "@", "\t", "\r", "\n")


def _neutralize_formula(value):
    """문자열 셀이 수식으로 해석되지 않게 중화한다. 문자열이 아니면(숫자·None 등) 그대로 둔다."""
    if isinstance(value, str) and value and value[0] in _FORMULA_TRIGGERS:
        return "'" + value
    return value


def export_to_excel(
    data: list[dict],
    filepath: str,
    sheet_name: str = "수집 데이터",
    sanitize_formulas: bool = True,
) -> str | None:
    """데이터 리스트를 엑셀 파일로 저장.

    Args:
        data: 딕셔너리 리스트. 각 딕셔너리의 키가 헤더가 됨.
        filepath: 저장할 .xlsx 파일 경로.
        sheet_name: 시트 이름 (기본값: "수집 데이터").
        sanitize_formulas: 수집 값이 수식으로 실행되지 않게 중화할지(기본 True).
            신뢰할 수 있는 데이터만 넣고 원본을 그대로 보존해야 하면 False.

    Returns:
        저장된 파일 경로. 데이터가 없으면 None.
    """
    clean = _neutralize_formula if sanitize_formulas else (lambda v: v)
    if not data:
        return None

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name
    headers = list(data[0].keys())

    # Header row (bold)
    bold_font = Font(bold=True)
    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=clean(header))
        cell.font = bold_font

    # Data rows
    for row_idx, item in enumerate(data, 2):
        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=row_idx, column=col_idx, value=clean(item.get(header)))

    # Auto column width
    for col_idx, header in enumerate(headers, 1):
        max_len = len(str(header))
        for row in range(2, len(data) + 2):
            val = ws.cell(row=row, column=col_idx).value
            if val is not None:
                max_len = max(max_len, len(str(val)))
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 50)

    # Auto filter
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{len(data) + 1}"

    wb.save(filepath)
    return filepath
