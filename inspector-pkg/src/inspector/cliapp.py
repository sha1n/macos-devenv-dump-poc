import argparse

from inspector.api.context import Context, Mode
from inspector.api.executor import Executor
from inspector.api.registry import Registry


class CliAppRunner:
    def __init__(self, name, register_components, run):
        self.name = name
        self._register_components = register_components
        self._do_run = run

    def run(self):
        ctx = parse_context(self.name, Registry())

        self._register_components(ctx.registry)

        ctx.logger.info("Starting {}.".format(self.name))
        self._print_header(ctx)

        if ctx.plan:
            _run_safe_execution_plan(ctx)
        else:
            run_safe(ctx, self._do_run)

        ctx.logger.info("{} finished.".format(self.name.capitalize()))

    def _print_header(self, ctx):
        logger = ctx.logger

        if ctx.plan:
            logger.info("Running in plan mode. No changes will be applied to the system.")
        elif ctx.dryrun:
            logger.info("Running in dry-run mode. No changes will be applied to the system.")

        logger.debug("Execution context = {}".format(ctx))
        logger.debug("Running in {} mode".format(str(ctx.mode)))


def parse_context(name, registry: Registry):
    parser = argparse.ArgumentParser(description='Takes an environment dump for support purposes.')
    parser.add_argument("--mode", "-m",
                        choices=["interactive", "background"],
                        dest="mode",
                        default="interactive",
                        help="one of [ interactive | background ]")
    parser.add_argument("--dry-run",
                        default=False,
                        dest="dryrun",
                        action="store_true",
                        help="runs in dry run mode")
    parser.add_argument("--plan", "-p",
                        default=False,
                        dest="plan",
                        action="store_true",
                        help="prints out an execution plan")
    parser.add_argument("--debug", "-d",
                        default=False,
                        dest="debug",
                        action="store_true",
                        help="logs debug information")
    parser.add_argument("--log-file",
                        dest="log_file",
                        help="log file path")

    args = parser.parse_args()

    return Context(
        name=name,
        registry=registry,
        mode=Mode.from_str(args.mode),
        debug=args.debug,
        log_file=args.log_file,
        plan=args.plan,
        dryrun=args.dryrun
    )


def run_safe(ctx: Context, fn):
    try:
        fn(ctx)
    except Exception as err:
        ctx.logger.error(err)
        ctx.logger.failure("Unexpected error - exiting :(")
        exit(1)


def _run_safe_execution_plan(ctx: Context):
    run_safe(ctx, Executor().plan)
