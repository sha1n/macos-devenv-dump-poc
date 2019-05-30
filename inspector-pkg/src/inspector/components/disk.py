from collections import namedtuple
from shutil import disk_usage

from inspector.api import context
from inspector.api.collector import Collector
from inspector.api.context import Context
from inspector.api.validator import Validator, ValidationResult, Status

DiskInfo = namedtuple(typename="DiskInfo", field_names=["filesystem", "total", "used", "free"])


class DiskInfoCollector(Collector):
    def __init__(self, ctx: context.Context):
        super().__init__(ctx)

    def collect(self):
        self.logger.info("Collecting disk information...")

        total, used, free = disk_usage("/")

        return DiskInfo(
            filesystem="/",
            total=_b_to_gb(total),
            used=_b_to_gb(used),
            free=_b_to_gb(free),
        )


class DiskInfoValidator(Validator):
    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def validate(self, input_data: DiskInfo) -> ValidationResult:
        if input_data is None:
            return ValidationResult(input_data, Status.ERROR)

        free_ratio = input_data.free / input_data.total
        if free_ratio < 0.1:
            free_percent = int(free_ratio * 100)
            self.ctx.logger.warn("Low disk space on filesystem '{}' ({}% free)".format(
                input_data.filesystem,
                free_percent)
            )
            return ValidationResult(input_data, Status.WARNING)

        return ValidationResult(input_data, Status.OK)


def _b_to_gb(value):
    return int(value / (1024 ** 3))