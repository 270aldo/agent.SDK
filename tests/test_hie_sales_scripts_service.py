"""
Tests for HIE Sales Scripts Service.
"""

import pytest
from src.services.hie_sales_scripts_service import (
    HIESalesScriptsService,
    HIEArchetype,
    HIEMetrics
)


class TestHIESalesScriptsService:
    """Test suite for HIE Sales Scripts Service."""
    
    def setup_method(self):
        """Setup test environment."""
        self.hie_service = HIESalesScriptsService()
    
    def test_service_initialization(self):
        """Test that service initializes correctly."""
        assert self.hie_service is not None
        assert self.hie_service.scripts_database is not None
        assert self.hie_service.neurological_triggers is not None
        assert self.hie_service.biological_constants is not None
    
    def test_hie_metrics_calculation_optimizador(self):
        """Test HIE metrics calculation for optimizador archetype."""
        user_profile = {
            'edad': 35,
            'profession': 'ceo startup',
            'energy_level': 7,
            'sleep_quality': 6,
            'stress_level': 8,
            'goals': 'increase productivity and performance'
        }
        
        metrics = self.hie_service.calculate_hie_metrics(user_profile)
        
        assert isinstance(metrics, HIEMetrics)
        assert 30 <= metrics.indice_eficiencia <= 95
        assert metrics.potencial_maximo > metrics.indice_eficiencia
        assert metrics.gap_biologico > 0
        assert 0 <= metrics.urgencia_score <= 1
        assert metrics.roi_biologico > 0
    
    def test_hie_metrics_calculation_arquitecto_vida(self):
        """Test HIE metrics calculation for arquitecto vida archetype."""
        user_profile = {
            'edad': 52,
            'profession': 'doctor',
            'energy_level': 5,
            'sleep_quality': 7,
            'stress_level': 6,
            'goals': 'maintain health and longevity'
        }
        
        metrics = self.hie_service.calculate_hie_metrics(user_profile)
        
        assert isinstance(metrics, HIEMetrics)
        assert 30 <= metrics.indice_eficiencia <= 95
        assert metrics.potencial_maximo > metrics.indice_eficiencia
        assert metrics.gap_biologico > 0
    
    def test_archetype_determination_optimizador(self):
        """Test archetype determination for optimizador profile."""
        user_profile = {
            'edad': 28,
            'profession': 'entrepreneur tech startup',
            'goals': 'maximize productivity and achieve competitive advantage'
        }
        
        archetype = self.hie_service.determine_hie_archetype(user_profile)
        assert archetype == HIEArchetype.OPTIMIZADOR
    
    def test_archetype_determination_arquitecto_vida(self):
        """Test archetype determination for arquitecto vida profile."""
        user_profile = {
            'edad': 58,
            'profession': 'teacher',
            'goals': 'maintain health and quality of life for family'
        }
        
        archetype = self.hie_service.determine_hie_archetype(user_profile)
        assert archetype == HIEArchetype.ARQUITECTO_VIDA
    
    def test_archetype_determination_hibrido(self):
        """Test archetype determination for hibrido profile."""
        user_profile = {
            'edad': 48,
            'profession': 'manager',
            'goals': 'balance performance with long-term wellness'
        }
        
        archetype = self.hie_service.determine_hie_archetype(user_profile)
        assert archetype == HIEArchetype.HIBRIDO
    
    def test_opening_script_generation(self):
        """Test opening script generation."""
        user_profile = {
            'edad': 35,
            'nombre': 'Carlos',
            'profession': 'consultant',
            'goals': 'improve efficiency'
        }
        
        script = self.hie_service.generate_hie_opening_script(user_profile)
        
        assert isinstance(script, str)
        assert len(script) > 50  # Should be a substantial message
        assert 'Carlos' in script or 'HIE' in script
    
    def test_diagnostic_sequence_generation(self):
        """Test diagnostic sequence generation."""
        user_profile = {
            'edad': 42,
            'profession': 'executive',
            'goals': 'optimize performance'
        }
        
        questions = self.hie_service.generate_hie_diagnostic_sequence(user_profile)
        
        assert isinstance(questions, list)
        assert len(questions) >= 5  # Should have at least 5 questions
        assert all(isinstance(q, str) for q in questions)
        assert all(len(q) > 20 for q in questions)  # Substantial questions
    
    def test_revelation_script_generation(self):
        """Test HIE revelation script generation."""
        hie_metrics = HIEMetrics(
            indice_eficiencia=68.5,
            potencial_maximo=87.2,
            gap_biologico=18.7,
            urgencia_score=0.75,
            roi_biologico=4.3
        )
        
        user_profile = {'edad': 38, 'profession': 'manager'}
        
        script = self.hie_service.generate_hie_revelation_script(hie_metrics, user_profile)
        
        assert isinstance(script, str)
        assert len(script) > 100  # Should be detailed
        assert '68.5' in script  # Should include actual metrics
        assert '87.2' in script
        assert '18.7' in script
    
    def test_urgency_script_generation(self):
        """Test urgency script generation."""
        hie_metrics = HIEMetrics(
            indice_eficiencia=65.0,
            potencial_maximo=85.0,
            gap_biologico=20.0,
            urgencia_score=0.8,
            roi_biologico=5.0
        )
        
        user_profile = {
            'edad': 45,
            'hourly_rate': 100
        }
        
        script = self.hie_service.generate_urgency_script(hie_metrics, user_profile)
        
        assert isinstance(script, str)
        assert len(script) > 50
        # Should mention time factors or opportunity costs
        assert any(keyword in script.lower() for keyword in 
                  ['tiempo', 'mes', 'año', 'costo', 'oportunidad', 'eficiencia'])
    
    def test_authority_script_generation(self):
        """Test authority script generation."""
        script = self.hie_service.generate_authority_script(HIEArchetype.OPTIMIZADOR)
        
        assert isinstance(script, str)
        assert len(script) > 50
        # Should include scientific or social proof elements
        assert any(keyword in script.lower() for keyword in 
                  ['investigación', 'estudio', 'stanford', 'harvard', 'científico', 'clientes'])
    
    def test_complete_hie_sequence_generation(self):
        """Test complete HIE sequence generation."""
        user_profile = {
            'edad': 35,
            'nombre': 'Ana',
            'profession': 'ceo fintech',
            'energy_level': 6,
            'sleep_quality': 7,
            'stress_level': 8,
            'goals': 'maximize performance and efficiency',
            'hourly_rate': 150
        }
        
        sequence = self.hie_service.generate_complete_hie_sequence(user_profile)
        
        # Verify all required components are present
        required_keys = [
            'apertura', 'diagnostico_preguntas', 'revelacion_indice',
            'urgencia_biologica', 'autoridad_cientifica', 'metricas_hie',
            'arquetipo_detectado'
        ]
        
        for key in required_keys:
            assert key in sequence
        
        # Verify metrics structure
        metrics = sequence['metricas_hie']
        assert 'indice_actual' in metrics
        assert 'potencial_maximo' in metrics
        assert 'gap_biologico' in metrics
        assert 'urgencia_score' in metrics
        assert 'roi_biologico' in metrics
        
        # Verify archetype
        assert sequence['arquetipo_detectado'] in ['optimizador', 'arquitecto_vida', 'hibrido']
        
        # Verify content quality
        assert len(sequence['apertura']) > 30
        assert len(sequence['diagnostico_preguntas']) >= 5
        assert len(sequence['revelacion_indice']) > 50
        assert len(sequence['urgencia_biologica']) > 50
        assert len(sequence['autoridad_cientifica']) > 50
    
    def test_fallback_sequence_generation(self):
        """Test fallback sequence generation."""
        fallback = self.hie_service._generate_fallback_sequence()
        
        assert isinstance(fallback, dict)
        assert 'apertura' in fallback
        assert 'error' in fallback
        assert 'metricas_hie' in fallback
        assert fallback['error'] == 'fallback_mode'
    
    def test_edge_cases_age_boundaries(self):
        """Test edge cases for age boundaries."""
        # Very young user
        young_profile = {
            'edad': 22,
            'profession': 'student',
            'goals': 'improve focus'
        }
        
        archetype_young = self.hie_service.determine_hie_archetype(young_profile)
        metrics_young = self.hie_service.calculate_hie_metrics(young_profile)
        
        assert archetype_young in [HIEArchetype.OPTIMIZADOR, HIEArchetype.ARQUITECTO_VIDA]
        assert metrics_young.indice_eficiencia > 0
        
        # Very old user
        old_profile = {
            'edad': 70,
            'profession': 'retired',
            'goals': 'maintain vitality'
        }
        
        archetype_old = self.hie_service.determine_hie_archetype(old_profile)
        metrics_old = self.hie_service.calculate_hie_metrics(old_profile)
        
        assert archetype_old in [HIEArchetype.OPTIMIZADOR, HIEArchetype.ARQUITECTO_VIDA]
        assert metrics_old.indice_eficiencia > 0
    
    def test_neurological_triggers_loaded(self):
        """Test that neurological triggers are properly loaded."""
        triggers = self.hie_service.neurological_triggers
        
        expected_categories = [
            'escasez_biologica', 'autoridad_cientifica', 
            'urgencia_temporal', 'valor_personal'
        ]
        
        for category in expected_categories:
            assert category in triggers
            assert len(triggers[category]) > 0
    
    def test_biological_constants_loaded(self):
        """Test that biological constants are properly loaded."""
        constants = self.hie_service.biological_constants
        
        expected_constants = [
            'declive_anual_hie', 'edad_critica_optimizacion',
            'edad_limite_efectividad', 'factor_urgencia_base',
            'multiplicador_costo_oportunidad', 'threshold_candidato_ideal'
        ]
        
        for constant in expected_constants:
            assert constant in constants
            assert isinstance(constants[constant], (int, float))
            assert constants[constant] > 0


class TestHIEIntegration:
    """Integration tests for HIE service with different scenarios."""
    
    def setup_method(self):
        """Setup test environment."""
        self.hie_service = HIESalesScriptsService()
    
    def test_ceo_profile_integration(self):
        """Test complete flow for CEO profile."""
        ceo_profile = {
            'edad': 42,
            'nombre': 'Roberto',
            'profession': 'ceo tech company',
            'energy_level': 5,
            'sleep_quality': 4,
            'stress_level': 9,
            'goals': 'maximize productivity and competitive advantage',
            'hourly_rate': 300
        }
        
        sequence = self.hie_service.generate_complete_hie_sequence(ceo_profile)
        
        # Should be optimizador archetype
        assert sequence['arquetipo_detectado'] == 'optimizador'
        
        # Should have high urgency due to stress and low sleep
        metrics = sequence['metricas_hie']
        assert metrics['urgencia_score'] > 0.5
        assert metrics['gap_biologico'] > 10
    
    def test_doctor_profile_integration(self):
        """Test complete flow for doctor profile (longevity focused)."""
        doctor_profile = {
            'edad': 55,
            'nombre': 'Dra. Martinez',
            'profession': 'medical doctor family practice',
            'energy_level': 6,
            'sleep_quality': 7,
            'stress_level': 6,
            'goals': 'maintain health and vitality for long-term practice',
            'hourly_rate': 200
        }
        
        sequence = self.hie_service.generate_complete_hie_sequence(doctor_profile)
        
        # Should be arquitecto_vida archetype due to age and goals
        assert sequence['arquetipo_detectado'] == 'arquitecto_vida'
        
        # Should mention longevity-related concepts
        revelation = sequence['revelacion_indice'].lower()
        assert any(term in revelation for term in ['vitalidad', 'eficiencia', 'potencial'])
    
    def test_hybrid_profile_integration(self):
        """Test complete flow for hybrid profile (45-55 age range)."""
        hybrid_profile = {
            'edad': 48,
            'nombre': 'Carmen',
            'profession': 'executive director nonprofit',
            'energy_level': 7,
            'sleep_quality': 6,
            'stress_level': 7,
            'goals': 'balance high performance with sustainable wellness',
            'hourly_rate': 120
        }
        
        sequence = self.hie_service.generate_complete_hie_sequence(hybrid_profile)
        
        # Should be hibrido archetype due to age
        assert sequence['arquetipo_detectado'] == 'hibrido'
        
        # Should have balanced messaging
        opening = sequence['apertura'].lower()
        assert 'hie' in opening or 'eficiencia' in opening