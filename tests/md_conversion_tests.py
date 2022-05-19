import unittest

from k8sDocTools import charm_tables

class Test_indent(unittest.TestCase):
    def test_list_int(self):
        """
        Test that markdownify code fences simple indent
        """
        input ="""
        paragraph text
          indent
        paragraph text
        """
        output ="""
        paragraph text

        ```
        indent
        ```

        paragraph text
        """

        result = k8sDocTools.charm_tables.markdownify(input)
        self.assertEqual(result, output)

if __name__ == '__main__':
    unittest.main()
