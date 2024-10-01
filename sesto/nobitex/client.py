import requests
from typing import Dict, Any, Optional
from .config import NobitexConfig
from .models import NobitexSymbol, OrderSide, OrderType
from .exceptions import NobitexAPIException, NobitexRequestException

class NobitexClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {self.api_key}"})

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{NobitexConfig.BASE_URL}{endpoint}"
        print(f"Requesting URL: {url}")  # Add this line
        response = self.session.request(method, url, **kwargs)
        
        try:
            data = response.json()
        except ValueError:
            raise NobitexRequestException("Invalid JSON response from API")
        
        if not response.ok:
            raise NobitexAPIException(data.get('message', 'Unknown error occurred'))
        
        return data

    def get_order_book(self, symbol: NobitexSymbol) -> Dict[str, Any]:
        return self._request("GET", f"{NobitexConfig.ENDPOINTS['order_book']}/{symbol.value}")

    def get_trades(self, symbol: NobitexSymbol) -> Dict[str, Any]:
        return self._request("GET", f"{NobitexConfig.ENDPOINTS['trades']}/{symbol.value}")

    def get_stats(self, src_currency: str, dst_currency: str) -> Dict[str, Any]:
        params = {"srcCurrency": src_currency, "dstCurrency": dst_currency}
        return self._request("GET", NobitexConfig.ENDPOINTS['stats'], params=params)

    def place_order(self, symbol: NobitexSymbol, side: OrderSide, order_type: OrderType,
                    price: float, amount: float) -> Dict[str, Any]:
        data = {
            "type": side.value,
            "execution": order_type.value,
            "srcCurrency": symbol.value.split('-')[0].lower(),
            "dstCurrency": symbol.value.split('-')[1].lower(),
            "amount": str(amount),
            "price": str(price)
        }
        return self._request("POST", NobitexConfig.ENDPOINTS['post_order'], json=data)

    def get_order_status(self, client_order_id: str) -> Dict[str, Any]:
        params = {"clientOrderId": client_order_id}
        return self._request("GET", NobitexConfig.ENDPOINTS['order_status'], params=params)

    def get_my_orders(self, symbol: Optional[NobitexSymbol] = None) -> Dict[str, Any]:
        params = {}
        if symbol:
            params["symbol"] = symbol.value
        return self._request("GET", NobitexConfig.ENDPOINTS['my_orders'], params=params)

    def cancel_order(self, client_order_id: str) -> Dict[str, Any]:
        return self._request("DELETE", f"{NobitexConfig.ENDPOINTS['cancel_order']}/{client_order_id}")