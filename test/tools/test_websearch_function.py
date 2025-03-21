import unittest

from src.agent.tools.all.web_search_function import (
    web_search_tavily,
    get_content_of_websites,
    web_search_perplexity,
    web_search_exa,
    get_content_of_exa_document,
    find_similar_links
)


class TestWebSearchFunction(unittest.TestCase):

    TEST_EXA_DOC_ID = "https://fig.io/manual/exa"

    def test_web_search_tavily(self):
        result = web_search_tavily.invoke(
            input={"query": "tavily", }
        )
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("url", result[0])

    def test_get_content_of_websites(self):
        results = get_content_of_websites.invoke(
            input={"links": ["https://www.google.com/"]}
        )
        self.assertIn("google", results[0]['raw_content'].lower())

    def test_web_search_exa(self):
        result = web_search_exa.invoke(
            input={"query": "exa", }
        )
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("score", result[0])

    def test_get_content_of_exa_document(self):
        results = get_content_of_exa_document.invoke(
            input={"content_ids": [self.TEST_EXA_DOC_ID]}
        )
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], dict)
        self.assertEqual(results[0]['id'], self.TEST_EXA_DOC_ID)

    def test_find_similar_links(self):
        result = find_similar_links.invoke(
            input={"link": "https://google.com", "num_results": 4}
        )
        self.assertEqual(len(result), 4)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], dict)
        self.assertIn("id", result[0])

    # TODO:test case for search perplexity


if __name__ == "__main__":
    unittest.main()
