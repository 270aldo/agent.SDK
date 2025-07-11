"""
Herramientas relacionadas con la información y gestión de los programas NGX.
"""
# from agents import function_tool
# TODO: Implementar function_tool alternativo o instalar agents sin conflictos
def function_tool(func):
    """Decorador temporal para herramientas de función."""
    return func
from src.conversation.flows.basic_flow import ConversationFlow # Para acceder a program_config
from src.conversation.prompts import PRICE_OBJECTION_TEMPLATE # Importar plantilla
from typing import Optional

@function_tool
async def get_program_details(program_name: str) -> str:
    """
    Provides detailed information about a specified NGX program.
    Use this tool to answer questions about program specifics like price, duration, key benefits, etc.

    Args:
        program_name: The name of the program (PRIME or LONGEVITY).

    Returns:
        A string containing key details of the program.
    """
    program_type_upper = program_name.upper()
    if program_type_upper not in ["PRIME", "LONGEVITY"]:
        return "Error: Programa no válido. Por favor, especifica PRIME o LONGEVITY."

    # Usamos ConversationFlow para obtener la configuración del programa de forma centralizada.
    # En un escenario real, esto podría venir de una base de datos o un archivo de configuración más robusto.
    flow_simulator = ConversationFlow(program_type=program_type_upper)
    config = flow_simulator.program_config

    details = f"Detalles del programa NGX {program_type_upper}:\n"
    details += f"- Precio Completo: ${config['price_full']} USD\n"
    details += f"- Precio Mensual: ${config['price_monthly']} USD durante {config['months']} meses\n"
    # Ajustar la duración para que sea más clara y correcta
    duration_days = "90 días" if program_type_upper == "PRIME" else "120 días"
    details += f"- Duración: {config['months']} meses ({duration_days})\n"
    details += "- Beneficios Clave:\n"
    for benefit in config['key_benefits']:
        details += f"  - {benefit}\n"
    details += f"- Audiencia Objetivo: {config['target_audience']}\n"
    details += "- Garantía de satisfacción de 30 días\n" # Añadido para completar la info
    
    # Podríamos añadir más detalles si es necesario, como la garantía.
    # Por ejemplo: "- Garantía de satisfacción de 30 días\n"

    return details 

@function_tool
async def handle_price_objection(program_name: str, customer_concerns: Optional[str] = None) -> str:
    """
    Addresses customer concerns specifically about the price or cost of an NGX program.
    Use this tool when a customer explicitly mentions keywords like 'precio', 'costo', 'caro', 
    'inversión', 'presupuesto', or asks 'cuánto cuesta' after already knowing general details.
    It provides a structured response addressing the value and payment options.

    Args:
        program_name: The name of the program (PRIME or LONGEVITY) the customer is asking about.
        customer_concerns: Optional. Specific concerns or context provided by the customer regarding price.
                           This can help tailor the response, though the primary response is template-based.

    Returns:
        A string containing a response to the price objection.
    """
    program_type_upper = program_name.upper()
    if program_type_upper not in ["PRIME", "LONGEVITY"]:
        return "Error: Programa no válido para manejar objeción de precio. Por favor, especifica PRIME o LONGEVITY."

    flow_simulator = ConversationFlow(program_type=program_type_upper)
    config = flow_simulator.program_config

    # Podríamos usar customer_concerns para una lógica más avanzada en el futuro,
    # por ahora, la plantilla es bastante genérica.

    response = PRICE_OBJECTION_TEMPLATE.format(
        programa=program_type_upper,
        beneficio_principal=config["key_benefits"][0], # Tomamos el primer beneficio como principal
        beneficio_1=config["key_benefits"][1] if len(config["key_benefits"]) > 1 else "mejor salud general",
        beneficio_2=config["key_benefits"][2] if len(config["key_benefits"]) > 2 else "mayor bienestar",
        beneficio_3=config["key_benefits"][3] if len(config["key_benefits"]) > 3 else "calidad de vida mejorada",
        precio_completo=config["price_full"],
        precio_mensual=config["price_monthly"],
        meses=config["months"]
    )
    return response 