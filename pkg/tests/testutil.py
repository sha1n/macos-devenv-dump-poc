import os
from inspector.commons.context import Context, Mode


def test_context() -> Context:
    mode = Mode.from_str(os.environ.get('INSPECTOR_TEST_MODE', str(Mode.SILENT)))

    return Context(name="test", mode=mode)