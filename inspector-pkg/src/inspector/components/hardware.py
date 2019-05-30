import multiprocessing
from collections import namedtuple

from inspector.api import context
from inspector.api.collector import Collector
from inspector.api.context import Context
from inspector.api.validator import Validator, ValidationResult, Status
from inspector.util import cmd

HardwareInfo = namedtuple(typename="HardwareInfo", field_names=["cpu_count", "total_ram"])


class HardwareInfoCollector(Collector):
    def __init__(self, ctx: context.Context):
        super().__init__(ctx)

    def collect(self):
        self.logger.info("Collecting hardware information...")
        cpu_count = multiprocessing.cpu_count()
        total_ram = _total_ram()
        return HardwareInfo(cpu_count, total_ram)


class HardwareInfoValidator(Validator):
    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def validate(self, input_data: HardwareInfo) -> ValidationResult:
        if input_data is None:
            return ValidationResult(input_data, Status.ERROR)

        if input_data.cpu_count < 8:  # fixme shai: to config
            self.ctx.logger.warn("If you are using Bazel regularly, {} CPUs is suboptimal".format(input_data.cpu_count))

        if input_data.total_ram < 16:  # fixme shai: to config
            self.ctx.logger.warn("If you are using Bazel regularly, {}G RAM is suboptimal".format(input_data.total_ram))

        return ValidationResult(input_data, Status.OK)


def _total_ram():
    raw_total_ram = cmd.execute(["sysctl", "hw.memsize"]).split(":")[1].strip()
    return int(int(raw_total_ram) / (1024 * 1000 * 1024))