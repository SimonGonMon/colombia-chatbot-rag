"""
Tests para la funcionalidad de extracción de datos de la clase DataExtractor.

Estos tests verifican que la extracción de contenido web funciona como se espera,
utilizando mocks para simular las respuestas HTTP y evitar dependencias de red reales.
"""

import pytest
import requests
from unittest.mock import patch
from src.rag.data_extractor import DataExtractor


@patch("src.rag.data_extractor.requests.get")
def test_fetch_content_success(mock_get):
    """Verifica que DataExtractor.fetch_content extrae correctamente el contenido de una página web simulada."""
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    mock_response.text = '<html><body><div class="mw-parser-output"><h2>Test Title</h2><p>Some test content.</p></div></body></html>'

    extractor = DataExtractor()
    result = extractor.fetch_content()

    expected_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    mock_get.assert_called_once_with(
        extractor.WIKI_URL, timeout=15, headers=expected_headers
    )
    assert "Test Title" in result
    assert "Some test content." in result


@patch("src.rag.data_extractor.requests.get")
def test_fetch_content_failure(mock_get):
    """Verifica que DataExtractor.fetch_content maneja los fallos de la solicitud HTTP, retornando None."""
    mock_response = mock_get.return_value
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError

    extractor = DataExtractor()
    result = extractor.fetch_content()
    assert result is None

    expected_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    mock_get.assert_called_once_with(
        extractor.WIKI_URL, timeout=15, headers=expected_headers
    )
