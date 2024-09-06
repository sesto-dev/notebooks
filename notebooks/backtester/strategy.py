# strategy.py
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def should_enter_trade(self, symbol_data, index, additional_data=None):
        """
        Define entry conditions for a trade.
        
        :param symbol_data: DataFrame with the symbol's historical data.
        :param index: Current index in the DataFrame.
        :param additional_data: Dictionary containing additional data such as higher timeframe indicators.
        :return: 'long' or 'short' for entry signals, None for no signal.
        """
        pass
    
    @abstractmethod
    def should_exit_trade(self, open_position, symbol_data, index, additional_data=None):
        """
        Define exit conditions for a trade.
        
        :param open_position: Dictionary representing the current open position.
        :param symbol_data: DataFrame with the symbol's historical data.
        :param index: Current index in the DataFrame.
        :param additional_data: Dictionary containing additional data such as higher timeframe indicators.
        :return: True to exit the trade, False to hold the position.
        """
        pass
