from inspector.api.executor import Executor
from inspector.cli import run_safe, context
from inspector.components.bazel import BazelInfoCollector, BazelInfoValidator
from inspector.components.disk import DiskInfoCollector, DiskInfoValidator
from inspector.components.hardware import HardwareInfoValidator, HardwareInfoCollector
from inspector.components.python import PythonInfoCollector, PythonInfoValidator
from inspector.components.semver import SemVer
from installer.components.bazel import BazelInstallReactor
from installer.components.python import PythonInstallReactor

HARDWARE_COMP_ID = "hardware config"
DISK_COMP_ID = "disk space"
BAZEL_COMP_ID = "bazel"
PYTHON_COMP_ID = "python"


def install():
    ctx = _installer_context()

    def execute():
        ctx.logger.info("Starting the installer...")
        executor = Executor()
        executor.execute(ctx)
        ctx.logger.info("Installer finished.")

    run_safe(ctx, execute)


def _installer_context():
    ctx = context("installer")
    registry = ctx.registry

    registry.register_collector(HARDWARE_COMP_ID, HardwareInfoCollector(ctx))
    registry.register_validator(HARDWARE_COMP_ID, HardwareInfoValidator(ctx=ctx))

    registry.register_collector(DISK_COMP_ID, DiskInfoCollector(ctx))
    registry.register_validator(DISK_COMP_ID, DiskInfoValidator(ctx=ctx))

    registry.register_collector(BAZEL_COMP_ID, BazelInfoCollector(ctx))
    registry.register_validator(BAZEL_COMP_ID, BazelInfoValidator(ctx=ctx))
    registry.register_reactor(BAZEL_COMP_ID, BazelInstallReactor(ctx))

    registry.register_collector(PYTHON_COMP_ID, PythonInfoCollector(ctx))
    registry.register_validator(PYTHON_COMP_ID, PythonInfoValidator(expected_ver=SemVer("2", "7", "0"), ctx=ctx))
    registry.register_reactor(PYTHON_COMP_ID, PythonInstallReactor(ctx))

    return ctx
