from unittest.mock import MagicMock, patch

from src.data_processing.excel_converter import convert_xls_to_xlsx

def test_convert_xls_to_xlsx_success(tmp_path):
    # Arrange
    xls_path = tmp_path / "test.xls"
    xlsx_path = tmp_path / "test.xlsx"
    
    # Crear un archivo XLS simulado (vacío para la prueba)
    xls_path.touch()

    with patch('src.data_processing.excel_converter.win32.Dispatch') as mock_dispatch, \
         patch('src.data_processing.excel_converter.pythoncom.CoInitialize') as mock_coinitialize, \
         patch('src.data_processing.excel_converter.pythoncom.CoUninitialize') as mock_couninitialize:

        mock_excel = MagicMock()
        mock_workbook = MagicMock()

        mock_dispatch.return_value = mock_excel
        mock_excel.Workbooks.Open.return_value = mock_workbook

        # Act
        result = convert_xls_to_xlsx(str(xls_path), str(xlsx_path))

        # Assert
        assert result is True
        mock_coinitialize.assert_called_once()
        mock_dispatch.assert_called_once_with("Excel.Application")
        mock_excel.Visible = False
        mock_excel.DisplayAlerts = False
        mock_excel.Workbooks.Open.assert_called_once_with(str(xls_path))
        mock_workbook.SaveAs.assert_called_once_with(str(xlsx_path), FileFormat=51)
        mock_workbook.Close.assert_called_once_with(SaveChanges=False)
        mock_excel.Quit.assert_called_once()
        mock_couninitialize.assert_called_once()

def test_convert_xls_to_xlsx_failure(tmp_path):
    # Arrange
    xls_path = tmp_path / "test.xls"
    xlsx_path = tmp_path / "test.xlsx"
    xls_path.touch()

    with patch('src.data_processing.excel_converter.win32.Dispatch') as mock_dispatch, \
         patch('src.data_processing.excel_converter.pythoncom.CoInitialize') as mock_coinitialize, \
         patch('src.data_processing.excel_converter.pythoncom.CoUninitialize') as mock_couninitialize:

        mock_excel = MagicMock()
        mock_dispatch.return_value = mock_excel
        mock_excel.Workbooks.Open.side_effect = Exception("Simulated Excel Error")

        # Act
        result = convert_xls_to_xlsx(str(xls_path), str(xlsx_path))

        # Assert
        assert result is False
        mock_coinitialize.assert_called_once()
        mock_dispatch.assert_called_once_with("Excel.Application")
        mock_excel.Workbooks.Open.assert_called_once_with(str(xls_path))
        mock_excel.Quit.assert_called_once()
        mock_couninitialize.assert_called_once()