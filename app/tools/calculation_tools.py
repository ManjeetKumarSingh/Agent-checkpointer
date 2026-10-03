from langchain_core.tools import tool


@tool
def calculate_risk(amount: float, income: float) -> float:
    """
    Calculate a simple risk ratio.
    """

    if income <= 0:
        return 1.0

    return round(amount / income, 4)