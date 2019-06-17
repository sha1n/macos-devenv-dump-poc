from inspector.api.executor import Executor
from inspector.api.registry import Registry
from inspector.cli import run_safe, context
from inspector.components.bazel import BazelInfoCollector, BazelInfoValidator
from inspector.components.disk import DiskInfoCollector, DiskInfoValidator
from inspector.components.hardware import HardwareInfoValidator, HardwareInfoCollector
from inspector.components.network import UrlConnectivityInfoCollector, UrlConnectivityInfoValidator
from inspector.components.python import PythonInfoCollector, PythonInfoValidator
from inspector.components.semver import SemVer
from inspector.components.xcode import XcodeInfoCollector, XcodeInfoValidator

HARDWARE_COMP_ID = "hardware config"
DISK_COMP_ID = "disk space"
NET_COMP_ID = "network connectivity"
BAZEL_COMP_ID = "bazel"
PYTHON_COMP_ID = "python"
PYTHON3_COMP_ID = "python3"
XCODE_COMP_ID = "xcode"


def inspect():
    ctx = _inspector_context()
    executor = Executor()

    def execute():
        ctx.logger.info("Starting the inspector...")

        executor.execute(ctx)

        ctx.logger.info("Inspector finished.")

    run_safe(ctx, execute)


def _inspector_context():
    return context("inspector", create_component_registry())


def create_component_registry() -> Registry:
    registry = Registry()

    registry.register_collector(NET_COMP_ID, UrlConnectivityInfoCollector())
    registry.register_validator(NET_COMP_ID, UrlConnectivityInfoValidator())

    registry.register_collector(HARDWARE_COMP_ID, HardwareInfoCollector())
    registry.register_validator(HARDWARE_COMP_ID, HardwareInfoValidator())

    registry.register_collector(DISK_COMP_ID, DiskInfoCollector())
    registry.register_validator(DISK_COMP_ID, DiskInfoValidator())

    registry.register_collector(BAZEL_COMP_ID, BazelInfoCollector())
    registry.register_validator(BAZEL_COMP_ID, BazelInfoValidator())

    registry.register_collector(PYTHON_COMP_ID, PythonInfoCollector())
    registry.register_validator(PYTHON_COMP_ID, PythonInfoValidator(expected_ver=SemVer("2", "7", "0")))

    registry.register_collector(PYTHON3_COMP_ID, PythonInfoCollector(binary_name="python3"))
    registry.register_validator(PYTHON3_COMP_ID, PythonInfoValidator(expected_ver=SemVer("3", "0", "0")))

    registry.register_collector(XCODE_COMP_ID, XcodeInfoCollector())
    registry.register_validator(XCODE_COMP_ID, XcodeInfoValidator())

    return registry
