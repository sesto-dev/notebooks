from .config import NobitexConfig

class NobitexEndpoints:
    BASE_URL = NobitexConfig.BASE_URL

    @staticmethod
    def login() -> str:
        return f"{NobitexEndpoints.BASE_URL}/auth/login"

    @staticmethod
    def order_book(symbol: str) -> str:
        return f"{NobitexEndpoints.BASE_URL}/v2/orderbook/{symbol}"

    @staticmethod
    def trades(symbol: str) -> str:
        return f"{NobitexEndpoints.BASE_URL}/v2/trades/{symbol}"

    @staticmethod
    def stats() -> str:
        return f"{NobitexEndpoints.BASE_URL}/market/stats"

    @staticmethod
    def post_order() -> str:
        return f"{NobitexEndpoints.BASE_URL}/market/orders/add"

    @staticmethod
    def order_status() -> str:
        return f"{NobitexEndpoints.BASE_URL}/market/orders/status"

    @staticmethod
    def my_orders() -> str:
        return f"{NobitexEndpoints.BASE_URL}/market/orders/list"

    @staticmethod
    def cancel_order(client_order_id: str) -> str:
        return f"{NobitexEndpoints.BASE_URL}/market/orders/update-status/{client_order_id}"
    
    @staticmethod
    def close_position(position_id: str) -> str:
        return f"{NobitexEndpoints.BASE_URL}/positions/{position_id}/close"

    @staticmethod
    def margin_markets_list() -> str:
        return f"{NobitexEndpoints.BASE_URL}/margin/markets/list"
    
    @staticmethod
    def positions_list() -> str:
        return f"{NobitexEndpoints.BASE_URL}/positions/list"
    
