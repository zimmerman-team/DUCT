
# The contents of this file are subject to the Mozilla Public License
# (MPL) Version 1.1 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License
# at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See
# the License for the specific language governing rights and
# limitations under the License.
#
# The Original Code is LEPL (http://www.acooke.org/lepl)
# The Initial Developer of the Original Code is Andrew Cooke.
# Portions created by the Initial Developer are Copyright (C) 2009-2010
# Andrew Cooke (andrew@acooke.org). All Rights Reserved.
#
# Alternatively, the contents of this file may be used under the terms
# of the LGPL license (the GNU Lesser General Public License,
# http://www.gnu.org/licenses/lgpl.html), in which case the provisions
# of the LGPL License are applicable instead of those above.
#
# If you wish to allow use of your version of this file only under the
# terms of the LGPL License and not to allow others to use your version
# of this file under the MPL, indicate your decision by deleting the
# provisions above and replace them with the notice and other provisions
# required by the LGPL License.  If you do not delete the provisions
# above, a recipient may use your version of this file under either the
# MPL or the LGPL License.

#@PydevCodeAnalysisIgnore
# pylint: disable-msg=C0301, E0611, W0401
# confused by __init__?

'''
Lepl is a parser library written in Python.
  
This is the API documentation; the module index is at the bottom of this page.  
There is also a `manual <../index.html>`_ which gives a higher level
overview.

The home page for this package is the 
`Lepl website <http://www.acooke.org/lepl>`_.


Example
-------

A simple example of how to use Lepl::

    from lepl import *
    
    # For a simpler result these could be replaced with 'list', giving
    # an AST as a set of nested lists 
    # (ie replace '> Term' etc with '> list' below).
    
    class Term(List): pass
    class Factor(List): pass
    class Expression(List): pass
       
    def build():
        
        # Here we define the grammar
        
        # A delayed value is defined later (see penultimate line in block) 
        expr   = Delayed()
        number = Digit()[1:,...]                        >> int

        # Allow spaces between items
        with DroppedSpace():
            term    = number | '(' & expr & ')'         > Term
            muldiv  = Any('*/')
            factor  = term & (muldiv & term)[:]         > Factor
            addsub  = Any('+-')
            expr   += factor & (addsub & factor)[:]     > Expression
            line    = Trace(expr) & Eos()
    
        return line.get_parse()
    
    if __name__ == '__main__':
        parser = build()
        # parser returns a list of tokens, but line 
        # returns a single value, so take the first entry
        print(parser('1 + 2 * (3 + 4 - 5)')[0])

Running this gives the result::

    Expression
     +- Factor
     |   `- Term
     |       `- 1
     +- '+'
     `- Factor
         +- Term
         |   `- 2
         +- '*'
         `- Term
             +- '('
             +- Expression
             |   +- Factor
             |   |   `- Term
             |   |       `- 3
             |   +- '+'
             |   +- Factor
             |   |   `- Term
             |   |       `- 4
             |   +- '-'
             |   `- Factor
             |       `- Term
             |           `- 5
             `- ')'
'''

from lepl.contrib.matchers import SmartSeparator2
from lepl.core.config import Configuration, ConfigBuilder
from lepl.core.manager import GeneratorManager
from lepl.core.trace import RecordDeepest, TraceStack
from lepl.matchers.combine import And, Or, First, Difference, Limit
from lepl.matchers.core import Empty, Any, Delayed, Literal, Empty, \
    Lookahead, Regexp
from lepl.matchers.complex import PostMatch, Columns, Iterate
from lepl.matchers.monitor import Trace
from lepl.matchers.derived import Apply, args, KApply, Join, \
    AnyBut, Optional, Star, ZeroOrMore, Map, Add, Drop, Repeat, Plus, \
    OneOrMore, Substitute, Name, Eof, Eos, Identity, Newline, Space, \
    Whitespace, Digit, Letter, Upper, Lower, Printable, Punctuation, \
    UnsignedInteger, SignedInteger, Integer, UnsignedFloat, SignedFloat, \
    UnsignedEFloat, SignedEFloat, Float, UnsignedReal, SignedReal, \
    UnsignedEReal, SignedEReal, Real, Word, DropEmpty, Literals, \
    String, SingleLineString, SkipString, SkipTo
from lepl.matchers.error import Error, make_error, raise_error
from lepl.matchers.memo import RMemo, LMemo, MemoException
from lepl.matchers.operators import Override, Separator, SmartSeparator1, \
    GREEDY, NON_GREEDY, DEPTH_FIRST, BREADTH_FIRST, DroppedSpace, REDUCE
from lepl.matchers.support import function_matcher, function_matcher_factory, \
    sequence_matcher, sequence_matcher_factory, \
    trampoline_matcher, trampoline_matcher_factory
from lepl.matchers.transform import PostCondition, Transform, Assert
from lepl.matchers.variables import TraceVariables
from lepl.lexer.matchers import Token
from lepl.lexer.support import LexerError, RuntimeLexerError
from lepl.lexer.lines.matchers import Block, Line, LineStart, LineEnd, \
    constant_indent, explicit, to_right, ContinuedLineFactory, Extend, \
    NO_BLOCKS, DEFAULT_POLICY
from lepl.regexp.core import RegexpError
from lepl.regexp.matchers import NfaRegexp, DfaRegexp
from lepl.regexp.unicode import UnicodeAlphabet
from lepl.stream.core import s_debug, s_deepest, s_delta, s_empty, s_eq, \
    s_factory, s_fmt, s_global_kargs, s_id, s_join, s_kargs, s_key, \
    s_len, s_line, s_max, s_next, s_stream
from lepl.stream.maxdepth import FullFirstMatchException
from lepl.stream.factory import DEFAULT_STREAM_FACTORY
from lepl.support.list import List, sexpr_fold, sexpr_throw, sexpr_flatten, \
    sexpr_to_tree
from lepl.support.node import Node, make_dict, join_with, node_throw
from lepl.support.timer import print_timing

__all__ = [
           
        # lepl.core.config
        'Configuration',
        'ConfigBuilder',
        
        # lepl.contrib.matchers
        'SmartSeparator2',
        
        # lepl.matchers.error
        'make_error',
        'raise_error',
        'Error',
        
        # lepl.matchers.core
        'Empty',
        'Repeat',
        'Join',
        'Any',
        'Literal',
        'Empty',
        'Lookahead',
        'Regexp', 
        
        # lepl.matchers.combine
        'And',
        'Or',
        'First',
        'Difference',
        'Limit',
        
        # lepl.matchers.derived
        'Apply',
        'args',
        'KApply',
        'Delayed', 
        'Trace', 
        'AnyBut', 
        'Optional', 
        'Star', 
        'ZeroOrMore', 
        'Plus', 
        'OneOrMore', 
        'Map', 
        'Add', 
        'Drop',
        'Substitute', 
        'Name', 
        'Eof', 
        'Eos', 
        'Identity', 
        'Newline', 
        'Space', 
        'Whitespace', 
        'Digit', 
        'Letter', 
        'Upper', 
        'Lower', 
        'Printable', 
        'Punctuation',
         
        'UnsignedInteger', 
        'SignedInteger', 
        'Integer',
         
        # float matchers exclude integers
        'UnsignedFloat', 
        'SignedFloat', 
        'UnsignedEFloat',
        'SignedEFloat', 
        'Float',
         
        # real matchers match both floats and integers
        'UnsignedReal', 
        'SignedReal', 
        'UnsignedEReal',
        'SignedEReal', 
        'Real',
        
        'Word',
        'DropEmpty',
        'Literals',
        'String',
        'SingleLineString',
        'SkipString',
        'SkipTo',
        'GREEDY',
        'NON_GREEDY',
        'DEPTH_FIRST',
        'BREADTH_FIRST',
        'REDUCE',
        
        # lepl.matchers.complex
        'PostMatch',
        'Columns',
        'Iterate',

        # lepl.matchers.support
        'function_matcher', 
        'function_matcher_factory',
        'sequence_matcher', 
        'sequence_matcher_factory',
        'trampoline_matcher', 
        'trampoline_matcher_factory',
        
        # lepl.matchers.transform
        'PostCondition',
        'Transform',
        'Assert',
        
        # lepl.matchers.variables
        'TraceVariables',
        
        # lepl.stream.stream
        'DEFAULT_STREAM_FACTORY',
        
        # lepl.matchers.operators
        'Override',
        'Separator',
        'SmartSeparator1',
        'DroppedSpace',
        
        # lepl.support.node
        'Node',
        'make_dict',
        'join_with',
        'node_throw',
        
        # lepl.support.list
        'List',
        'sexpr_fold',
        'sexpr_throw',
        'sexpr_flatten',
        'sexpr_to_tree',
        
        # lepl.lexer.matchers
        'Token',
        'LexerError',
        'RuntimeLexerError',
        
        # lepl.core.manager
        'GeneratorManager',
        
        # lepl.core.trace
        'RecordDeepest',
        'TraceStack',
        
        # lepl.core.memo,
        'RMemo',
        'LMemo',
        'MemoException',
        
        # lepl.regexp.core
        'RegexpError',
        
        # lepl.regexp.matchers
        'NfaRegexp',
        'DfaRegexp',
        
        # lepl.regexp.unicode
        'UnicodeAlphabet',
        
        # lepl.stream.core
        's_debug', 
        's_deepest', 
        's_delta', 
        's_empty', 
        's_eq',
        's_factory', 
        's_fmt', 
        's_global_kargs',
        's_id', 
        's_join', 
        's_kargs', 
        's_key',
        's_len', 
        's_line', 
        's_max', 
        's_next', 
        's_stream',

        # lepl.stream.maxdepth
        'FullFirstMatchException',
        
        # lepl.lexer.lines.matchers
        'LineStart',
        'LineEnd',
        'Line',
        'ContinuedLineFactory',
        'Extend',
        'Block',
        'NO_BLOCKS',
        'DEFAULT_POLICY',
        'explicit',
        'constant_indent',
        'to_right',
        
        # lepl.support.timer
        'print_timing'
       ]

__version__ = '5.1.3'

if __version__.find('b') > -1:
    from logging import getLogger, basicConfig, WARN
    #basicConfig(level=WARN)
    getLogger('lepl').warn('You are using a BETA version of LEPL.')
