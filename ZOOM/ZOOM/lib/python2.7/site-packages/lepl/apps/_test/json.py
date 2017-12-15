
from lepl.apps.json import Simple
from lepl._test.base import BaseTest


class JsonTest(BaseTest):
    
    def test_dict(self):
        self.assert_direct('{"a": 123, "b": "somewhere"}', Simple(),
                           [[{'a': 123.0, 'b': 'somewhere'}]])
        
    def test_escape(self):
        self.assert_direct('"a\\u0020b"', Simple(),
                           [['a b']])
        self.assert_direct('"a\\nb"', Simple(),
                           [['a\nb']])

    def test_array(self):
        self.assert_direct('[1,2,[3,4],[[5], 6]]', Simple(),
                           [[[1.0,2.0,[3.0,4.0],[[5.0],6.0]]]])
    
    def test_object(self):
        self.assert_direct('{"a": 1}', Simple(),
                           [[{"a": 1.0}]])
        self.assert_direct('{"a": 1, "b": [2,3]}', Simple(),
                           [[{"a": 1.0, "b": [2.0, 3.0]}]])

    def test_spaces(self):
        self.assert_direct('{"a": 1, "b":"c","d"  : [ 2, 3.]}', Simple(),
                           [[{'a': 1.0, 'b': 'c', 'd': [2.0, 3.0]}]])
