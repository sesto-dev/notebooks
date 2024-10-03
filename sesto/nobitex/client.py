import requests
from typing import Dict, Any, Optional
from .config import NobitexConfig
from .endpoints import NobitexEndpoints
from .models import NobitexSymbol, OrderSide, OrderType
from .exceptions import NobitexAPIException, NobitexRequestException
from IPython import display

class NobitexClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Token {self.api_key}"})

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = endpoint
        print(f"Requesting URL: {url}")
        response = self.session.request(method, url, **kwargs)
        
        try:
            data = response.json()
        except ValueError:
            raise NobitexRequestException("Invalid JSON response from API")
        
        if not response.ok:
            raise NobitexAPIException(data.get('message', 'Unknown error occurred'))
        
        return data

    def get_order_book(self, symbol: NobitexSymbol) -> Dict[str, Any]:
        return self._request("GET", NobitexEndpoints.order_book(symbol.value))

    def get_trades(self, symbol: NobitexSymbol) -> Dict[str, Any]:
        return self._request("GET", NobitexEndpoints.trades(symbol.value))

    def get_stats(self) -> Dict[str, Any]:
        return self._request("GET", NobitexEndpoints.stats())

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
        return self._request("POST", NobitexEndpoints.post_order(), json=data)

    def get_order_status(self, client_order_id: str) -> Dict[str, Any]:
        params = {"clientOrderId": client_order_id}
        return self._request("GET", NobitexEndpoints.order_status(), params=params)

    def get_my_orders(self, symbol: Optional[NobitexSymbol] = None) -> Dict[str, Any]:
        params = {}
        if symbol:
            params["symbol"] = symbol.value
        return self._request("GET", NobitexEndpoints.my_orders(), params=params)

    def cancel_order(self, client_order_id: str) -> Dict[str, Any]:
        return self._request("POST", NobitexEndpoints.cancel_order(client_order_id))
    
    def cancel_all_orders(self, hours: Optional[float] = None, execution: Optional[str] = None,
                          trade_type: Optional[str] = None, src_currency: Optional[str] = None,
                          dst_currency: Optional[str] = None) -> Dict[str, Any]:
        data = {}
        if hours is not None:
            data['hours'] = hours
        if execution:
            data['execution'] = execution
        if trade_type:
            data['tradeType'] = trade_type
        if src_currency:
            data['srcCurrency'] = src_currency
        if dst_currency:
            data['dstCurrency'] = dst_currency
        
        return self._request("POST", NobitexEndpoints.cancel_all_orders(), json=data)
    
    def get_available_markets(self) -> Dict[str, Any]:
        return self._request("GET", NobitexEndpoints.margin_markets_list())

    def close_position(self, position_id: str) -> Dict[str, Any]:
        return self._request("POST", NobitexEndpoints.close_position(position_id))
    
    def modify_sl_tp(self, position_id: str, mode: str, amount: float, price: float,
                    stop_price: float, stop_limit_price: float) -> Dict[str, Any]:
        data = {
            "positionId": position_id,
            "mode": mode,
            "amount": str(amount),
            "price": str(price),
            "stopPrice": str(stop_price),
            "stopLimitPrice": str(stop_limit_price)
        }
        return self._request("POST", NobitexEndpoints.close_position(position_id), json=data)

    def get_positions(self) -> Dict[str, Any]:
        return self._request("GET", NobitexEndpoints.positions_list())