from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import MagicMock, patch, ANY
import pytest
from src.core.db import get_db
from src.models import db_models
import uuid
from datetime import datetime

# Fixture to override the get_db dependency
@pytest.fixture(name="db_session")
def db_session_fixture():
    session = MagicMock()
    yield session

# Fixture to override the get_db dependency in the app
@pytest.fixture(name="client")
def client_fixture(db_session: MagicMock):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# Mock the dte_service.process_new_dte function
@pytest.fixture(autouse=True)
def mock_dte_service_process_new_dte():
    with patch('src.services.dte_service.process_new_dte') as mock_process:
        mock_process.return_value = {
            "codigo_generacion": uuid.uuid4(),
            "estado": "PROCESANDO",
            "sello_recepcion": None
        }
        yield mock_process

# Mock the dte_repository.get_dte_by_codigo_generacion function
@pytest.fixture(autouse=True)
def mock_dte_repository_get_dte():
    with patch('src.repositories.dte_repository.get_dte_by_codigo_generacion') as mock_get_dte:
        # Default behavior: DTE not found
        mock_get_dte.return_value = None
        yield mock_get_dte

# Mock the dte_service.process_invalidation function
@pytest.fixture(autouse=True)
def mock_dte_service_process_invalidation():
    with patch('src.services.dte_service.process_invalidation') as mock_invalidation:
        mock_invalidation.return_value = None # Invalidation process is async
        yield mock_invalidation


def test_post_dte_success(client: TestClient, mock_dte_service_process_new_dte):
    """
    Tests the successful initiation of a DTE issuance process.
    This is a contract test for the `POST /dte` endpoint.
    """
    # A simplified DTE payload for testing purposes
    test_payload = {
        "tipo_dte": "01",
        "datos_dte": {
            "receptor_nit": "1234-567890-123-4",
            "items": [{"nombre": "Test Item", "cantidad": 1, "precio": 10.0}]
        }
    }

    response = client.post("/dte", json=test_payload)

    assert response.status_code == 202
    data = response.json()
    assert "codigo_generacion" in data
    assert data["estado"] == "PROCESANDO"
    mock_dte_service_process_new_dte.assert_called_once()

def test_get_dte_status_not_found(client: TestClient, mock_dte_repository_get_dte):
    """
    Tests the case where a DTE is not found.
    """
    non_existent_uuid = uuid.uuid4()
    response = client.get(f"/dte/{non_existent_uuid}")
    assert response.status_code == 404
    mock_dte_repository_get_dte.assert_called_once_with(ANY, codigo_generacion=non_existent_uuid)

def test_get_dte_status_found(client: TestClient, mock_dte_repository_get_dte):
    """
    Tests retrieving the status of an existing DTE.
    """
    existing_uuid = uuid.uuid4()
    mock_dte_repository_get_dte.return_value = db_models.DTE(
        id=uuid.uuid4(),
        codigo_generacion=existing_uuid,
        numero_control="DTE-01-001-001-000000000000001",
        tipo_dte="01",
        estado="RECIBIDO",
        documento_json={}, # Simplified
        fecha_emision=datetime.now(),
        monto_total=100.00
    )
    response = client.get(f"/dte/{existing_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["codigo_generacion"] == str(existing_uuid)
    assert data["estado"] == "RECIBIDO"
    mock_dte_repository_get_dte.assert_called_once_with(ANY, codigo_generacion=existing_uuid)

def test_invalidate_dte_success(client: TestClient, mock_dte_service_process_invalidation):
    """
    Tests the successful initiation of a DTE invalidation process.
    """
    test_uuid = uuid.uuid4()
    
    response = client.post(
        f"/dte/{test_uuid}/invalidate",
        json={"motivo": "Error en la descripción del producto"}
    )
    
    assert response.status_code == 202
    mock_dte_service_process_invalidation.assert_called_once_with(ANY, test_uuid, "Error en la descripción del producto")
