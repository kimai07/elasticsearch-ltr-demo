import unittest
# from unittest.mock import patch

from app.demo.check_search_results import create_es_query, create_es_ltr_query


class TestCheckSearchResults(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    # @patch('os.path.exists', return_value=True)
    def test_create_es_query(self):
        q = create_es_query("abc")
        want = {
            'query': {
                'multi_match': {
                    'query': 'abc',
                    'fields': ['title', 'overview']
                }
            }
        }
        self.assertDictEqual(want, q)

    def test_create_es_ltr_query(self):
        q = create_es_ltr_query("abc")
        want = {
            'query': {
                'multi_match': {
                    'query': 'abc',
                    'fields': ['title', 'overview']
                }
            },
            'rescore': {
                'query': {
                    'rescore_query': {
                        'sltr': {
                            'model': 'test_6',
                            'params': {'keywords': 'abc'}
                        }
                    }
                }
            }
        }
        self.assertDictEqual(want, q)


#  self.assertEqual(self.cache.get("missing-value"), None)
# self.assertTrue("test:value" in self.cache._cache)
#  self.assertDictEqual(
#     {"test1": 1, "test2": 2},
#     self.cache.get_all())
