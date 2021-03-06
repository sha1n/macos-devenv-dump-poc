import unittest

from shminspector.api.semver import SemVer
from shminspector.api.validator import ValidationResult, Status
from shminspector.components.python import PythonInfo
from shminstaller.components.python import Python3InstallReactor
from tests.testutil import test_context


class Python3InstallReactorTest(unittest.TestCase):

    def test_reaction_to_status_ok(self):
        reactor = Python3InstallReactor()

        commands = reactor.react(validation_result_with(status=Status.OK), ctx=test_context())
        self.assertEqual(0, len(commands))

    def test_reaction_to_not_found(self):
        reactor = Python3InstallReactor()

        commands = reactor.react(validation_result_with(status=Status.NOT_FOUND), ctx=test_context())

        self.assertEqual(4, len(commands))

        download_command = commands[0]
        self.assertIn("curl -s", str(download_command))

        install_command = commands[1]
        self.assertIn("sudo installer", str(install_command))

        install_certs_command = commands[2]
        self.assertIn("/Install Certificates.command", str(install_certs_command))

        update_shell_profile_command = commands[3]
        self.assertIn("/Update Shell Profile.command", str(update_shell_profile_command))

    def test_reaction_to_upgrade_required(self):
        reactor = Python3InstallReactor()

        commands = reactor.react(validation_result_with(status=Status.UPGRADE_REQUIRED), ctx=test_context())
        self.assertEqual(0, len(commands))

    def test_reaction_to_downgrade_required(self):
        reactor = Python3InstallReactor()

        commands = reactor.react(validation_result_with(status=Status.DOWNGRADE_REQUIRED), ctx=test_context())
        self.assertEqual(0, len(commands))


def validation_result_with(status: Status):
    return ValidationResult(python_info_with(), status)


def python_info_with(major="0", minor="0", patch="0"):
    return PythonInfo("/", SemVer(major, minor, patch))


if __name__ == '__main__':
    unittest.main()
