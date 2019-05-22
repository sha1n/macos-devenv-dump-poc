from abc import abstractmethod
from inspector.commons.context import Context


class Collector:
    def __init__(self, ctx: Context):
        self.ctx = ctx
        self.logger = ctx.logger

    @abstractmethod
    def collect(self) -> object: pass
