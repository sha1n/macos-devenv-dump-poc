import unittest

from shminspector.api.semver import SemVer
from shminspector.api.validator import Status
from shminspector.components.bazel import BazelInfo, BazelInfoValidator
from tests.testutil import test_context


class BazelInfoValidatorTest(unittest.TestCase):

    def test_validate_no_bazelisk(self):
        validator = BazelInfoValidator()
        bazel_info = bazel_info_with()

        result = validator.validate(bazel_info, ctx=test_context())
        self.assertEqual(Status.UPGRADE_REQUIRED, result.status)

    def test_validate_bazelisk(self):
        validator = BazelInfoValidator()
        bazel_info = bazel_info_with(bazelisk=True)

        result = validator.validate(bazel_info, ctx=test_context())
        self.assertEqual(Status.OK, result.status)

    def test_missing_bazel_info(self):
        validator = BazelInfoValidator()

        result = validator.validate(None, ctx=test_context())
        self.assertEqual(result.status, Status.NOT_FOUND)


def bazel_info_with(major="1", minor="24", patch="0", bazelisk=False):
    return BazelInfo(path="/", version=SemVer(major, minor, patch), bazelisk=bazelisk)


if __name__ == '__main__':
    unittest.main()
