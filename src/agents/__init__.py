# Paquete de Agentes NGX

# Clases simuladas para desarrollo
class NGXBaseAgent:
    def __init__(self, program_type="PRIME"):
        self.program_type = program_type
        
    async def run(self, messages):
        # Esta es una implementación simulada
        return None

__all__ = [
    "NGXBaseAgent"
]
