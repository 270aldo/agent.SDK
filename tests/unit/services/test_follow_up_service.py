"""
Pruebas unitarias para el servicio de seguimiento.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta

from src.services.follow_up_service import FollowUpService

class TestFollowUpService:
    """Pruebas para la clase FollowUpService."""
    
    @pytest.fixture
    def mock_resilient_client(self):
        """Fixture que proporciona un cliente resiliente simulado."""
        with patch("src.services.follow_up_service.supabase_client") as mock_client:
            # Configurar el comportamiento del mock para table().insert().execute()
            execute_mock_insert = AsyncMock()
            execute_mock_insert.return_value.data = [
                {
                    "id": "test-follow-up-id",
                    "user_id": "test-user-id",
                    "conversation_id": "test-conversation-id",
                    "follow_up_type": "high_intent",
                    "status": "scheduled"
                }
            ]
            
            mock_client.table = MagicMock()
            mock_client.table.return_value.insert = MagicMock()
            mock_client.table.return_value.insert.return_value.execute = execute_mock_insert
            
            # Configurar el comportamiento del mock para table().select().eq().lt().execute()
            execute_mock_select = AsyncMock()
            execute_mock_select.return_value.data = [
                {
                    "id": "test-follow-up-id",
                    "user_id": "test-user-id",
                    "conversation_id": "test-conversation-id",
                    "follow_up_type": "high_intent",
                    "status": "scheduled",
                    "scheduled_date": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "created_at": datetime.now().isoformat()
                }
            ]
            
            mock_client.table.return_value.select = MagicMock()
            mock_client.table.return_value.select.return_value.eq = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.lt = MagicMock()
            mock_client.table.return_value.select.return_value.eq.return_value.lt.return_value.execute = execute_mock_select
            
            # Configurar el comportamiento del mock para table().update().eq().execute()
            execute_mock_update = AsyncMock()
            execute_mock_update.return_value.data = [
                {
                    "id": "test-follow-up-id",
                    "status": "completed"
                }
            ]
            
            mock_client.table.return_value.update = MagicMock()
            mock_client.table.return_value.update.return_value.eq = MagicMock()
            mock_client.table.return_value.update.return_value.eq.return_value.execute = execute_mock_update
            
            yield mock_client
    
    @pytest.fixture
    def mock_follow_up_service(self):
        """Fixture que proporciona una instancia simulada de FollowUpService."""
        # Crear un mock del servicio
        mock_service = MagicMock(spec=FollowUpService)
        
        # Configurar métodos
        mock_service.schedule_follow_up = AsyncMock(return_value={"id": "test-follow-up-id"})
        mock_service.get_pending_follow_ups = AsyncMock(return_value=[
            {
                "id": "test-follow-up-id",
                "conversation_id": "test-conversation-id",
                "customer_id": "test-customer-id",
                "scheduled_time": datetime.now().isoformat(),
                "status": "pending",
                "message": "Mensaje de seguimiento",
                "created_at": datetime.now().isoformat()
            }
        ])
        mock_service.mark_follow_up_completed = AsyncMock(return_value=True)
        mock_service.cancel_follow_up = AsyncMock(return_value=True)
        
        return mock_service
    
    @pytest.mark.asyncio
    async def test_schedule_follow_up(self, mock_resilient_client):
        """Prueba que schedule_follow_up crea correctamente un seguimiento."""
        # Crear servicio
        service = FollowUpService()
        
        # Datos de prueba
        user_id = "test-user-id"
        conversation_id = "test-conversation-id"
        follow_up_type = "high_intent"
        days_delay = 2
        
        # Programar seguimiento
        result = await service.schedule_follow_up(
            user_id=user_id,
            conversation_id=conversation_id,
            follow_up_type=follow_up_type,
            days_delay=days_delay
        )
        
        # Verificar resultado
        assert "id" in result
        assert result["id"] == "test-follow-up-id"
        assert result["user_id"] == "test-user-id"
        assert result["conversation_id"] == "test-conversation-id"
        assert result["follow_up_type"] == "high_intent"
        assert result["status"] == "scheduled"
        
        # Verificar que se llamó al método table().insert().execute()
        mock_resilient_client.table.assert_called_with("follow_up_requests")
        mock_resilient_client.table.return_value.insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_pending_follow_ups(self, mock_resilient_client):
        """Prueba que get_pending_follow_ups obtiene correctamente los seguimientos pendientes."""
        # Crear servicio
        service = FollowUpService()
        
        # Obtener seguimientos pendientes
        result = await service.get_pending_follow_ups()
        
        # Verificar resultado
        assert len(result) == 1
        assert result[0]["id"] == "test-follow-up-id"
        assert result[0]["status"] == "scheduled"
        
        # Verificar que se llamó al método table().select().eq().lt().execute()
        mock_resilient_client.table.assert_called_with("follow_up_requests")
        mock_resilient_client.table.return_value.select.assert_called_with("*")
        mock_resilient_client.table.return_value.select.return_value.eq.assert_called_with("status", "scheduled")
    
    # Este método no existe en la implementación actual, por lo que se omite la prueba
    # @pytest.mark.asyncio
    # async def test_get_pending_follow_ups_for_customer(self, mock_resilient_client):
    #     """Prueba que get_pending_follow_ups_for_customer obtiene los seguimientos para un cliente específico."""
    #     pass
    
    @pytest.mark.asyncio
    async def test_update_follow_up_status(self, mock_resilient_client):
        """Prueba que update_follow_up_status actualiza correctamente el estado de un seguimiento."""
        # Crear servicio
        service = FollowUpService()
        
        # Actualizar estado del seguimiento
        result = await service.update_follow_up_status(
            follow_up_id="test-follow-up-id",
            status="completed",
            notes="Seguimiento completado con éxito"
        )
        
        # Verificar resultado
        assert result["id"] == "test-follow-up-id"
        assert result["status"] == "completed"
        
        # Verificar que se llamó al método table().update().eq().execute()
        mock_resilient_client.table.assert_called_with("follow_up_requests")
        mock_resilient_client.table.return_value.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_follow_up_status_cancelled(self, mock_resilient_client):
        """Prueba que update_follow_up_status cancela correctamente un seguimiento."""
        # Configurar el mock para devolver un estado cancelado
        execute_mock_update = AsyncMock()
        execute_mock_update.return_value.data = [
            {
                "id": "test-follow-up-id",
                "status": "cancelled"
            }
        ]
        mock_resilient_client.table.return_value.update.return_value.eq.return_value.execute = execute_mock_update
        
        # Crear servicio
        service = FollowUpService()
        
        # Actualizar estado del seguimiento (cancelar)
        result = await service.update_follow_up_status(
            follow_up_id="test-follow-up-id",
            status="cancelled",
            notes="Seguimiento cancelado por el usuario"
        )
        
        # Verificar resultado
        assert result["id"] == "test-follow-up-id"
        assert result["status"] == "cancelled"
        
        # Verificar que se llamó al método table().update().eq().execute()
        mock_resilient_client.table.assert_called_with("follow_up_requests")
        mock_resilient_client.table.return_value.update.assert_called_once()
