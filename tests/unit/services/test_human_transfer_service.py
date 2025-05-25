"""
Pruebas unitarias para el servicio de transferencia humana.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from src.services.human_transfer_service import HumanTransferService

class TestHumanTransferService:
    """Pruebas para la clase HumanTransferService."""
    
    @pytest.fixture
    def mock_resilient_client(self):
        """Fixture que proporciona un cliente resiliente simulado."""
        with patch("src.services.human_transfer_service.supabase_client") as mock_client:
            # Configurar el comportamiento del mock para table().insert().execute()
            execute_mock_insert = AsyncMock()
            execute_mock_insert.return_value.data = [
                {
                    "id": "test-transfer-id",
                    "conversation_id": "test-conversation-id",
                    "user_id": "test-user-id",
                    "reason": "El cliente solicita hablar con un humano",
                    "status": "requested",
                    "requested_at": datetime.now().isoformat(),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            ]
            
            mock_client.table = MagicMock()
            mock_client.table.return_value.insert = MagicMock()
            mock_client.table.return_value.insert.return_value.execute = execute_mock_insert
            
            # Configurar el comportamiento del mock para table().select().eq().execute()
            execute_mock_select = AsyncMock()
            execute_mock_select.return_value.data = [
                {
                    "id": "test-transfer-id",
                    "conversation_id": "test-conversation-id",
                    "user_id": "test-user-id",
                    "agent_id": None,
                    "status": "pending",
                    "reason": "El cliente solicita hablar con un humano",
                    "created_at": datetime.now().isoformat()
                }
            ]
            
            mock_client.table.return_value.select = MagicMock()
            mock_client.table.return_value.select.return_value.eq = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.execute = execute_mock_select
            
            # Configurar el comportamiento del mock para table().update().eq().execute()
            execute_mock_update = AsyncMock()
            execute_mock_update.return_value.data = [
                {
                    "id": "test-transfer-id",
                    "status": "assigned",
                    "agent_id": "test-agent-id"
                }
            ]
            
            mock_client.table.return_value.update = MagicMock()
            mock_client.table.return_value.update.return_value.eq = MagicMock()
            mock_client.table.return_value.update.return_value.eq.return_value.execute = execute_mock_update
            
            yield mock_client
    
    @pytest.fixture
    def mock_human_transfer_service(self):
        """Fixture que proporciona una instancia simulada de HumanTransferService."""
        # Crear un mock del servicio
        mock_service = MagicMock(spec=HumanTransferService)
        
        # Configurar métodos
        mock_service.request_human_transfer = AsyncMock(return_value={
            "id": "test-transfer-id",
            "conversation_id": "test-conversation-id",
            "user_id": "test-user-id",
            "reason": "El cliente solicita hablar con un humano",
            "status": "requested",
            "requested_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        
        mock_service.get_transfer_status = AsyncMock(return_value={
            "id": "test-transfer-id",
            "conversation_id": "test-conversation-id",
            "user_id": "test-user-id",
            "agent_id": None,
            "status": "pending",
            "reason": "El cliente solicita hablar con un humano",
            "created_at": datetime.now().isoformat()
        })
        
        mock_service.update_transfer_status = AsyncMock(return_value={
            "id": "test-transfer-id",
            "status": "assigned",
            "agent_id": "test-agent-id",
            "updated_at": datetime.now().isoformat()
        })
        
        mock_service.detect_transfer_request = MagicMock(return_value=True)
        mock_service.generate_transfer_message = MagicMock(return_value="Entiendo que prefieres hablar con un agente humano. Estoy transfiriendo tu conversación a uno de nuestros representantes.")
        
        return mock_service
    
    @pytest.mark.asyncio
    async def test_request_human_transfer(self, mock_resilient_client):
        """Prueba que request_human_transfer crea correctamente una solicitud de transferencia."""
        # Crear servicio
        service = HumanTransferService()
        
        # Datos de prueba
        conversation_id = "test-conversation-id"
        user_id = "test-user-id"
        reason = "El cliente solicita hablar con un humano"
        
        # Solicitar transferencia
        result = await service.request_human_transfer(
            conversation_id=conversation_id,
            user_id=user_id,
            reason=reason
        )
        
        # Verificar resultado
        assert "id" in result
        assert result["id"] == "test-transfer-id"
        assert result["conversation_id"] == "test-conversation-id"
        assert result["user_id"] == "test-user-id"
        assert result["status"] == "requested"
        assert result["reason"] == "El cliente solicita hablar con un humano"
        
        # Verificar que se llamó al método table().insert().execute()
        mock_resilient_client.table.assert_called_with("human_transfer_requests")
        mock_resilient_client.table.return_value.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_transfer_status(self, mock_resilient_client):
        """Prueba que get_transfer_status obtiene correctamente el estado de una transferencia."""
        # Crear servicio
        service = HumanTransferService()
        
        # Obtener estado de transferencia
        result = await service.get_transfer_status(transfer_id="test-transfer-id")
        
        # Verificar resultado
        assert result["id"] == "test-transfer-id"
        assert result["status"] == "pending"
        
        # Verificar que se llamó al método table().select().eq().execute()
        mock_resilient_client.table.assert_called_with("human_transfer_requests")
        mock_resilient_client.table.return_value.select.assert_called_with("*")
        mock_resilient_client.table.return_value.select.return_value.eq.assert_called_with("id", "test-transfer-id")
    
    @pytest.mark.asyncio
    async def test_update_transfer_status(self, mock_resilient_client):
        """Prueba que update_transfer_status actualiza correctamente el estado de una transferencia."""
        # Crear servicio
        service = HumanTransferService()
        
        # Actualizar estado de transferencia (asignar agente)
        result = await service.update_transfer_status(
            transfer_id="test-transfer-id",
            status="accepted",
            agent_id="test-agent-id"
        )
        
        # Verificar resultado
        assert result["id"] == "test-transfer-id"
        assert result["status"] == "assigned"
        assert result["agent_id"] == "test-agent-id"
        
        # Verificar que se llamó al método table().update().eq().execute()
        mock_resilient_client.table.assert_called_with("human_transfer_requests")
        mock_resilient_client.table.return_value.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_transfer_status_completed(self, mock_resilient_client):
        """Prueba que update_transfer_status marca correctamente una transferencia como completada."""
        # Configurar el mock para devolver un estado completado
        execute_mock_update = AsyncMock()
        execute_mock_update.return_value.data = [
            {
                "id": "test-transfer-id",
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            }
        ]
        mock_resilient_client.table.return_value.update.return_value.eq.return_value.execute = execute_mock_update
        
        # Crear servicio
        service = HumanTransferService()
        
        # Actualizar estado de transferencia (completar)
        result = await service.update_transfer_status(
            transfer_id="test-transfer-id",
            status="completed"
        )
        
        # Verificar resultado
        assert result["id"] == "test-transfer-id"
        assert result["status"] == "completed"
        
        # Verificar que se llamó al método table().update().eq().execute()
        mock_resilient_client.table.assert_called_with("human_transfer_requests")
        mock_resilient_client.table.return_value.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_transfer_status_rejected(self, mock_resilient_client):
        """Prueba que update_transfer_status rechaza correctamente una transferencia."""
        # Configurar el mock para devolver un estado rechazado
        execute_mock_update = AsyncMock()
        execute_mock_update.return_value.data = [
            {
                "id": "test-transfer-id",
                "status": "rejected",
                "rejected_at": datetime.now().isoformat()
            }
        ]
        mock_resilient_client.table.return_value.update.return_value.eq.return_value.execute = execute_mock_update
        
        # Crear servicio
        service = HumanTransferService()
        
        # Actualizar estado de transferencia (rechazar)
        result = await service.update_transfer_status(
            transfer_id="test-transfer-id",
            status="rejected"
        )
        
        # Verificar resultado
        assert result["id"] == "test-transfer-id"
        assert result["status"] == "rejected"
        
        # Verificar que se llamó al método table().update().eq().execute()
        mock_resilient_client.table.assert_called_with("human_transfer_requests")
        mock_resilient_client.table.return_value.update.assert_called_once()
