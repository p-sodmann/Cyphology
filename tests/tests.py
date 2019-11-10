import unittest
from cyphology.cyphology import Cyphology

class TestCypolLoading(unittest.TestCase):

    def test_simple(self):
        # well formated Cyphol file, should not raise any exceptions
       
        sample = Cyphology("tests/sample_data/import.cyphol")
        self.assertTrue(len(sample) == 2)

        sample = Cyphology("tests/sample_data/sample.cyphol")

        sample = Cyphology("tests/sample_data/own.cyphol")
        sample.write_to_neo4j()

    def test_exeptions(self):
        with self.assertRaises(Exception) as context:
            Cyphology("tests/sample_data/faulty_object.cyphol")
        self.assertTrue("Error 01" in str(context.exception))

        with self.assertRaises(Exception) as context:
            Cyphology("tests/sample_data/double_object.cyphol")
        self.assertTrue("Error 03" in str(context.exception))
        
        with self.assertRaises(Exception) as context:
            Cyphology("tests/sample_data/attribute_target_unknown.cyphol")
        self.assertTrue("Error 04" in str(context.exception))

if __name__ == '__main__':
    unittest.main()