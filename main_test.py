import importlib
import unittest
from unittest.mock import patch, MagicMock
import main
import os
import argparse


class TestYourScript(unittest.TestCase):
    @patch("requests.post")
    def test_create_github_repo_failure(self, mock_post):
        # Setup the mock
        mock_post.return_value.status_code = 400
        # Call the function
        ssh_url = main.create_github_repo("test")
        # Assert that the function worked correctly
        self.assertIsNone(ssh_url)


@patch("requests.put")
def test_update_spy_list_failure(self, mock_put):
    # Setup the mock
    mock_put.return_value.status_code = 400

    # Call the function with appropriate parameters
    repo_name = "test_repo"
    ssh_url = "test_url"
    main.update_spy_list(repo_name, ssh_url)

    # Assert that the function worked correctly
    mock_put.assert_called()  # We expect the put request to have been called

    @patch("os.getenv")
    def test_env_variables_with_mock(self, mock_getenv):
        # Setup the mock to return specific values for certain inputs
        mock_getenv.side_effect = (
            lambda x: "test_token" if x == "GITHUB_TOKEN" else "test_username"
        )

        # Reload main to get the updated environment variables
        importlib.reload(main)

        # Verify that getenv was called with the correct arguments
        mock_getenv.assert_any_call("GITHUB_TOKEN")
        mock_getenv.assert_any_call("GITHUB_USERNAME")

        # Assert that the returned values are as expected
        self.assertEqual(main.GITHUB_TOKEN, "test_token")
        self.assertEqual(main.USERNAME, "test_username")

    @patch("os.path.isdir", return_value=False)
    def test_main_invalid_directory(self, mock_isdir):
        with self.assertRaises(SystemExit) as cm:
            main.main()
        self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
