import pytest
from src.services import dte_service
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
@patch('src.services.auth_service.AuthManager.get_mh_token')
@patch('src.core.signing.sign_json_payload')
@patch('src.core.client.transmit_dte', side_effect=Exception("MH Service Unavailable"))
@patch('src.repositories.dte_repository.update_dte_status') # Mock the repository function
async def test_contingency_flow_is_triggered(
    mock_update_dte_status,
    mock_transmit,
    mock_sign,
    mock_get_token
):
    """
    Tests that the contingency flow is triggered when the transmission to MH fails repeatedly.
    """
    # Arrange
    mock_get_token.return_value = "fake_jwt_token"
        mock_sign.return_value = "fake.signed.jws"
>       mock_update_dte_status.return_value = MagicMock()

    test_payload = {
        "tipo_dte": "01",
        "datos_dte": {"key": "value"}
    }

    # Act & Assert
    # We expect an exception to be raised after all retries fail, 
    # which then should be caught by the endpoint to trigger contingency logic.
    with pytest.raises(Exception, match="Failed to transmit DTE to MH"):
        await dte_service.process_new_dte(db=MagicMock(), dte_data=test_payload)

    # Assert that the function to save the DTE as a contingency was called
    mock_update_dte_status.assert_called_once_with(db=ANY, db_dte=ANY, new_status="CONTINGENCIA")
