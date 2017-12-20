
from __future__ import print_function

from lepl import List
from lepl.support.lib import fmt
from lepl.support.list import sexpr_fold


class Foo(List): pass

class Bar(List): pass

def per_list(type_, items):
    if issubclass(type_, List):
        return fmt('<{0}>{1}</{0}>', type_.__name__, '\n'.join(items))
    else:
        raise Exception

def per_item(item):
    return repr(item)

sexpr_to_xml = sexpr_fold(per_list=per_list, per_item=per_item)

ast = Foo([Bar([1,2,3]),Bar(['a','b','c'])])
print(sexpr_to_xml(ast))
