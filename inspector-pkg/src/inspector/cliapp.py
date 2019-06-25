import argparse
import json

from inspector.api.context import Context, Mode
from inspector.api.executor import ExecPlanExecutor
from inspector.api.registry import Registry


class CliAppRunner:
    def __init__(self, name, description, register_components, run):
        self.name = name
        self.description = description
        self._register_components = register_components
        self._do_run = run

    def run(self):
        ctx = parse_context(name=self.name, registry=Registry(), description=self.description)

        self._register_components(ctx.registry)

        ctx.logger.info("Starting {}.".format(self.name))
        _print_header(ctx)

        if ctx.flags.plan:
            _run_safe_execution_plan(ctx)
        else:
            run_safe(ctx, self._do_run)

        ctx.logger.info("{} finished.".format(self.name.capitalize()))


def _print_header(ctx):
    logger = ctx.logger

    if ctx.flags.plan:
        logger.info("Running in plan mode. No changes will be applied to the system.")
    elif ctx.flags.dryrun:
        logger.info("Running in dry-run mode. No changes will be applied to the system.")

    logger.debug("Execution context = {}".format(ctx))
    logger.debug("Configuration = {}".format(json.dumps(ctx.config, indent=2)))
    logger.debug("Running in {} mode".format(str(ctx.mode)))


def parse_context(name, registry: Registry, description=""):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--mode", "-m",
                        choices=["interactive", "background"],
                        dest="mode",
                        default="interactive",
                        help="one of [ interactive | background ]. "
                             "Note that some actions cannot be executed in non-interactive mode")
    parser.add_argument("--dry-run",
                        default=False,
                        dest="dryrun",
                        action="store_true",
                        help="runs in dry run mode. In that mode actions that modify your environment will not be "
                             "executed")
    parser.add_argument("--plan", "-p",
                        default=False,
                        dest="plan",
                        action="store_true",
                        help="prints out an execution plan (takes into account your platform and program flags)")
    parser.add_argument("--debug", "-d",
                        default=False,
                        dest="debug",
                        action="store_true",
                        help="logs debug information to the console")
    parser.add_argument("--experimental", "-e",
                        default=False,
                        dest="experimental",
                        action="store_true",
                        help="turns on experimental features")
    parser.add_argument("--log-file",
                        dest="log_file",
                        help="absolute path to optional log file")
    parser.add_argument("--config",
                        dest="config_file",
                        help="optional JSON config file path")

    args = parser.parse_args()

    return Context(
        name=name,
        config_file=args.config_file,
        registry=registry,
        mode=Mode.from_str(args.mode),
        debug=args.debug,
        log_file=args.log_file,
        plan=args.plan,
        dryrun=args.dryrun,
        experimental=args.experimental,
    )


def run_safe(ctx: Context, fn):
    try:
        fn(ctx)
    except Exception as err:
        ctx.logger.error(err)
        ctx.logger.failure("Unexpected error - exiting :(")
        exit(1)


def _run_safe_execution_plan(ctx: Context):
    run_safe(ctx, ExecPlanExecutor().execute)
