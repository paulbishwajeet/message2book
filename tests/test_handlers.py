import unittest
from unittest.mock import patch
from bot.responses import get_response

class TestGetResponse(unittest.TestCase):

    @patch('bot.responses.config')
    def test_greeting_response(self, mock_config):
        mock_config.keywords = {'greeting': ['hello'], 'urgent': []}
        mock_config.response_templates = {'greeting': 'Hello [USER_NAME]!'}
        response = get_response('hello there', 'testuser')
        self.assertEqual(response, 'Hello testuser!')

    @patch('bot.responses.config')
    def test_urgent_response(self, mock_config):
        mock_config.keywords = {'greeting': [], 'urgent': ['urgent']}
        mock_config.response_templates = {'urgent': 'Urgent message for [USER_NAME]!'}
        response = get_response('this is an urgent message', 'testuser')
        self.assertEqual(response, 'Urgent message for testuser!')

    @patch('bot.responses.config')
    @patch('bot.responses.is_business_hours')
    def test_business_hours_response(self, mock_is_business_hours, mock_config):
        mock_is_business_hours.return_value = False
        mock_config.keywords = {'greeting': [], 'urgent': []}
        mock_config.response_templates = {'business_hours': 'We are closed, [USER_NAME].'}
        response = get_response('are you open?', 'testuser')
        self.assertEqual(response, 'We are closed, testuser.')

    @patch('bot.responses.config')
    @patch('bot.responses.is_business_hours')
    def test_default_response(self, mock_is_business_hours, mock_config):
        mock_is_business_hours.return_value = True
        mock_config.keywords = {'greeting': [], 'urgent': []}
        mock_config.response_templates = {'default': 'Default response for [USER_NAME].'}
        response = get_response('some random message', 'testuser')
        self.assertEqual(response, 'Default response for testuser.')

if __name__ == '__main__':
    unittest.main()
