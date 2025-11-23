import pytest
from src.services.dte_service import process_new_dte # Assuming this function will exist
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
@patch('src.services.auth_service.AuthManager.get_mh_token')
@patch('src.core.signing.sign_json_payload')
@patch('src.core.client.transmit_dte')
@patch('src.repositories.dte_repository.create_dte')
@patch('src.repositories.dte_repository.update_dte_after_transmission')
async def test_dte_issuance_integration_success(
    mock_update_dte,
    mock_create_dte,
    mock_transmit,
    mock_sign,
    mock_get_token
):
    """
    Integration test for the DTE issuance service.
    Mocks external dependencies (auth, signing, transmission, db) to test the orchestration logic.
    """
    # Arrange: Mock return values from external services
    mock_get_token.return_value = "fake_jwt_token"
    mock_sign.return_value = "fake.signed.jws"
    mock_transmit.return_value = {"estado": "RECIBIDO", "selloRecepcion": "fake_sello_123"}
    mock_save_dte.return_value = MagicMock()

    test_payload = {
        "tipo_dte": "01",
        "datos_dte": {"key": "value"}
    }

    # Act: Call the main service function
    result = await process_new_dte(db=MagicMock(), dte_data=test_payload)

    # Assert: Verify that the orchestration flow is correct
    mock_get_token.assert_called_once()
    mock_sign.assert_called_once()
    mock_transmit.assert_called_once_with("fake.signed.jws", "fake_jwt_token")
    mock_create_dte.assert_called_once()
    mock_update_dte.assert_called_once()
    assert result["estado"] == "RECIBIDO"
    assert result["sello_recepcion"] == "fake_sello_123"
