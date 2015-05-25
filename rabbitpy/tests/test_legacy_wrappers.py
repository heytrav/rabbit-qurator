import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from ..utilities.jobqueue import preprocess, postprocess


class TestLegacyWrapper(TestCase):

    """Test ability of wrappers to convert legacy jobqueue structure."""

    def test_preprocess_iwmn_request(self):
        """Test wrapping queue calls with wrappers. """

        @preprocess
        def stripped_out_data(raw_data):
            self.assertNotIn('data', raw_data)
            self.assertEqual(raw_data, {"one": "stuff"})

        arg = {
            'data': {
                'options': {
                    "one": "stuff"
                }
            }
        }
        func_data = stripped_out_data(arg)

    def test_raise_key_error(self):
        """Calling something with preprocess and non-legacy data should throw
        an error.
        """
        @preprocess
        def fail_legacy_call(raw_data):
            pass

        arg = {"one": "stuff"}
        with self.assertRaises(KeyError):
            fail_legacy_call(arg)

    def test_isolate_subset_jobqueue(self):
        """Test that wrapper plucks data out of part of jobqueue structure.
        """
        @preprocess(subset='subset')
        def specific_part(raw_data):
            self.assertNotIn('data', raw_data)
            self.assertNotIn('excluded', raw_data)
            self.assertEqual(raw_data, {"one": "stuff"})

        @preprocess(subset='irrelevant')
        def will_fail(raw_data):
            pass

        arg = {
            'data': {
                'options': {
                    "subset": {"one": "stuff"},
                    "excluded": "irrelevant"
                }
            }
        }
        func_data = specific_part(arg)

        with self.assertRaises(KeyError):
            will_fail(arg)

    def test_postprocess_data(self):
        """Test postprocess wrapper puts stuff back into jobqueue structure. """
        @postprocess
        def generic_func(raw_data):
            return {"account_id": "testuser"}

        arg = {
            'data': {
                'options': {
                    "account_id": None
                }
            }
        }
        func_data = generic_func(arg)
        print("Generic func returned {!r}".format(func_data))
        self.assertIn('data', func_data)
        self.assertIn('options', func_data['data'])
        self.assertEqual(
            func_data['data']['options'], {
                "account_id": "testuser"})

    def test_isolate_subset_return_jobqueue(self):
        """Test that postprocess wrapper puts data in specific place. """

        @postprocess(subset='domains')
        def generic_func_subset(raw_data):
            return [{"test-me.com": {"registered": 14394893}}]

        arg = {
            'data': {
                'options': {
                    "account_id": None
                }
            }
        }
        func_data = generic_func_subset(arg)
        print("Generic func returned {!r}".format(func_data))
        self.assertIn('data', func_data)
        self.assertIn('options', func_data['data'])
        options = func_data['data']['options']
        self.assertIn('account_id', options)
        self.assertIn('domains', options)

    def test_pre_postprocess(self):
        """Test preprocess and postprocess decorators together.  """
        @postprocess
        @preprocess
        def generic_function_pre_post(raw_data):
            self.assertNotIn('data', raw_data)
            self.assertIn('user_id', raw_data)
            return_data = {
                "account_id": "testuser",
                "domains": [{"testme.com": {"registered": 1439940393}}]
            }
            raw_data.update(return_data)
            return return_data

        arg = {
            'data': {
                'options': {
                    "user_id": 'testuser',
                    "account_id": None
                }
            }
        }
        func_data = generic_function_pre_post(arg)
        print("Generic func returned {!r}".format(func_data))
        self.assertIn('data', func_data)
        self.assertIn('options', func_data['data'])
        options = func_data['data']['options']
        self.assertIn('account_id', options)
        self.assertEqual(options['account_id'], "testuser")
        self.assertIn('user_id', options)
        self.assertIn('domains', options)

    def test_wrapper_error(self):
        """Test error handling.
        """
        @postprocess
        @preprocess
        def generic_throw_error(arg):
            raise Exception("Just to see what happens")

        arg = {
            "data": {
                "options": {
                    "stuff": "doesn't matter"
                }
            }
        }
        result = generic_throw_error(arg)
        self.assertIn('error', result)
        options = result['data']['options']
        self.assertEqual(options, arg['data']['options'])
