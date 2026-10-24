import unittest
from tools import list_topics, search_knowledge, get_topic_details, get_knowledge_stats

class AgentToolsTests(unittest.TestCase):
    def test_topics_are_available(self):
        result = list_topics()
        self.assertTrue(result["found"])
        self.assertIn("Python", result["topics"])

    def test_python_search_finds_entry(self):
        result = search_knowledge("What is Python?")
        self.assertTrue(result["found"])
        self.assertTrue(any(item["topic"] == "Python" for item in result["entries"]))

    def test_css_parser_retrieval(self):
        result = get_topic_details("What does a CSS parser do?")
        self.assertTrue(result["found"])
        self.assertTrue(any(item["topic"] == "CSS Parser" for item in result["entries"]))

    def test_stats(self):
        stats = get_knowledge_stats()
        self.assertGreaterEqual(stats["entries"], 1)
        self.assertGreaterEqual(stats["topics"], 1)

if __name__ == "__main__":
    unittest.main()
