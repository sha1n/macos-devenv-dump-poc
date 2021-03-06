import urllib.request as request
from collections import namedtuple
from time import time
from typing import List

from shminspector.api.collector import Collector
from shminspector.api.context import Context
from shminspector.api.validator import Validator, ValidationResult, Status
from shminspector.util.diag import timeit_if

NetConnectivityInfo = namedtuple(typename="NetConnectivityInfo", field_names=["address", "ok", "time", "message"])
Spec = namedtuple(typename="Spec", field_names=["address", "failure_message"])


class UrlConnectivityInfoCollector(Collector):

    def collect(self, ctx: Context) -> List[NetConnectivityInfo]:
        specs = self._collect_specs(ctx)
        ctx.logger.progress("Checking network connectivity...")
        return list((self._check_connectivity(spec, ctx) for spec in specs))

    @timeit_if(more_than_sec=3)
    def _check_connectivity(self, spec, ctx):
        start_time = time()

        def elapsed():
            return time() - start_time

        try:
            address = spec.address
            ctx.logger.progress("Checking connectivity to {}".format(spec.address))

            request.urlopen(address, timeout=10)
            return NetConnectivityInfo(address=address, ok=True, time=elapsed(), message=None)

        except request.HTTPError as error:
            if error.code < 400 or error.code > 499:
                return NetConnectivityInfo(address=spec.address, ok=False, time=elapsed(), message=spec.failure_message)
            else:
                return NetConnectivityInfo(address=spec.address, ok=True, time=elapsed(), message=None)

        except request.URLError:
            return NetConnectivityInfo(address=spec.address, ok=False, time=elapsed(), message=spec.failure_message)

    def _collect_specs(self, ctx):
        specs = []
        if ctx.config.get("network", None) is not None and \
                ctx.config.get("network").get("check_specs", None) is not None:
            for raw_spec in ctx.config["network"]["check_specs"]:
                specs.append(Spec(raw_spec["address"], raw_spec["failure_message"]))

        return specs


class UrlConnectivityInfoValidator(Validator):
    def validate(self, input_data, ctx: Context) -> ValidationResult:
        if input_data is None:
            ctx.logger.error("Network connectivity check returned no data!")
            return ValidationResult(input_data, Status.ERROR)

        for check in input_data:
            if check.ok:
                if check.time > 2:
                    ctx.logger.warn(
                        "Network connectivity check to {} took {} seconds".format(check.address, check.time)
                    )
            else:
                ctx.logger.warn(
                    "Network connectivity check to {} failed! Error: {}".format(check.address, check.message)
                )

        return ValidationResult(input_data, Status.OK)
