from abc import ABC,abstractmethod

class BaseAgent(ABC):
    def __init__(self, reporter=None):
        self._reporter = reporter

    def report(self, content, info_type="info"):
        if self._reporter:
            self._reporter(content, info_type)
    @abstractmethod
    def invoke(self,input:str):
        pass
    @abstractmethod
    def stream(self,input:str):
        pass