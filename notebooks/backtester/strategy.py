# strategy.py
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def should_enter_trade(self, symbol_data, index):
        """ Define entry conditions for a trade """
        pass
    
    @abstractmethod
    def should_exit_trade(self, open_position, symbol_data, index):
        """ Define exit conditions for a trade """
        pass
