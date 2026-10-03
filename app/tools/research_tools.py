from langchain_core.tools import tool


@tool
def search_customer(customer_id: str) -> str:
    """
    Search customer information using customer ID.
    """

    # Later this can call PostgreSQL/API/etc.
    return f"Customer {customer_id} found. Status: ACTIVE"


@tool
def get_customer_transactions(customer_id: str) -> str:
    """
    Retrieve recent customer transactions.
    """

    return f"Transactions for customer {customer_id}: 5 recent transactions"