
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

'''
Some intermediate classes that support parsers for objects that can be
converted to strings using str().
'''

from lepl.matchers.support import coerce_
from lepl.regexp.core import Alphabet, Character, Sequence, Choice, Repeat, \
    Option, _Choice, _Character
from lepl.support.lib import fmt, str, LogMixin


ILLEGAL = '{}[]*()-?.+\\^$|'
'''
Characters that must be escaped.
'''


class StrParser(LogMixin):
    '''
    Construct a parser for string based expressions.
    
    We need a clear policy on backslashes.  To be as backwards compatible as
    possible I am going with:
    
      0. "Escaping" means prefixing with \.

      1. These characters are special: {, }, [, ], -, \, (, ), *, ?, ., +, 
         ^, $, |.

      2. Special characters (ie literal, or unescaped special characters) may 
         not have a meaning currently, or may only have a meaning in certain 
         contexts.

      3. To use a special character literally, it must be escaped.

      4. If a special character is used without an escape, in a context
         where it doesn't have a meaning, then it is an error.

      5. If a non-special character is escaped, that is also an error.
    
    This is not the same as the Python convention, but I believe it makes
    automatic escaping of given text easier.
    '''
    
    def __init__(self, alphabet):
        super(StrParser, self).__init__()
        self.alphabet = alphabet
        
    def dup(self, x):
        '''
        Create an interval from a single character.
        '''
        return (self.alphabet.from_char(x), self.alphabet.from_char(x))
    
    def tup(self, x):
        '''
        Create an interval from a tuple.
        '''
        return (self.alphabet.from_char(x[0]), self.alphabet.from_char(x[1]))
    
    def dot(self, _):
        '''
        Create a "complete" interval.
        '''
        return (self.alphabet.min, self.alphabet.max)
    
    def invert(self, x):
        '''
        Invert an interval.
        '''
        # Character needed here to ensure intervals passed to invert are ordered 
        return self.alphabet.invert(Character(x, self.alphabet))
    
    def sequence(self, x):
        '''
        Create a sequence.
        '''
        return Sequence(self.alphabet, *x)
    
    def star(self, x):
        '''
        Repeat a sub-expression.
        '''
        return Repeat(self.alphabet, *x)
    
    def plus(self, x):
        '''
        Repeat a sub-expression.
        '''
        return self.sequence([self.sequence(x), self.star(x)])
    
    def option(self, x):
        '''
        Make a sub-expression optional.
        '''
        return Option(self.alphabet, *x)
    
    def choice(self, x):
        '''
        Construct a choice from a list of sub-expressions.
        '''
        return Choice(self.alphabet, *x)
    
    def char(self, x):
        '''
        Construct a character from an interval (pair).
        '''
        return Character(x, self.alphabet)
    
    def extend(self, x):
        '''
        Delegate a character extension to the alphabet.
        '''
        return self.alphabet.extension(x)
    
    def build(self):
        '''
        Construct the parser.
        '''
        
        # Avoid dependency loops
        from lepl.matchers.derived import Drop, Eos, AnyBut, Upper
        from lepl.matchers.core import Any, Lookahead, Literal, Delayed
        from lepl.matchers.error import make_error
        from lepl.matchers.variables import TraceVariables
        from lepl.support.node import node_throw
    
        with TraceVariables(False):
    
            # these two definitions enforce the conditions above, providing only
            # special characters appear as literals in the grammar
            escaped  = Drop(self.alphabet.escape) & self.alphabet.escaped
            raw      = ~Lookahead(self.alphabet.escape) & \
                            AnyBut(self.alphabet.illegal)
            close    = Drop(')')
            extend   = (Drop('(*') & Upper()[1:,...] & close)        >> self.extend
            
            single   = escaped | raw | extend
            
            any_     = Literal('.')                                  >> self.dot
            letter   = single                                        >> self.dup
            pair     = single & Drop('-') & single                   > self.tup
             
            interval = pair | letter
            brackets = Drop('[') & interval[1:] & Drop(']')
            inverted = Drop('[^') & interval[1:] & Drop(']')         >= self.invert      
            char     = inverted | brackets | letter | any_ | extend  > self.char
        
            item     = Delayed()
            
            open     = Drop('(?:')
            range    = Drop(self.alphabet.escape) & self.alphabet.range
            seq      = (char | item | range)[0:]                     > self.sequence
            group    = open & seq & close
            alts     = open & seq[2:, Drop('|')] & close             > self.choice
            star     = (alts | group | char) & Drop('*')             > self.star
            plus     = (alts | group | char) & Drop('+')             > self.plus
            opt      = (alts | group | char) & Drop('?')             > self.option
            bad_grp  = (Drop('(') & ~Lookahead('?:') & seq & close) \
                            ** make_error(
                                "Lepl's own regular expressions do not currently "
                                "support matched groups.\n"
                                "Use '(?:...)' to group expressions without "
                                "matching.") 
            
            item    += alts | group | star | plus | opt | bad_grp
            
            expr     = ((char | item)[:] & Drop(Eos())) >> node_throw
    
        # Empty config here avoids loops if the default config includes
        # references to alphabets
        expr.config.clear()
        return expr.parse_string


def make_str_parser(alphabet):
    '''
    Create a parser.
    '''
    return StrParser(alphabet).build()


class StrAlphabet(Alphabet):
    '''
    Support for alphabets.
    '''
    
    # pylint: disable-msg=E1002
    # (pylint bug?  this chains back to a new style abc)
    def __init__(self, min_, max_, escape='\\', escaped=ILLEGAL,
                 illegal=ILLEGAL, range=None,
                 parser_factory=make_str_parser):
        from lepl.matchers.core import Any, Never
        super(StrAlphabet, self).__init__(min_, max_)
        self.__escape = escape
        self.__escaped = coerce_(escaped, Any)
        self.__illegal = illegal
        self.__range = range if range else Never()
        self._parser = parser_factory(self)
    
    @property
    def escape(self):
        return self.__escape
    
    @property
    def escaped(self):
        return self.__escaped
    
    @property
    def illegal(self):
        return self.__illegal
    
    @property
    def range(self):
        return self.__range
    
    def _escape_char(self, char):
        '''
        Escape a character if necessary.
        '''
        if self.escape is not None and str(char) in self.illegal:
            return self.escape + str(char)
        else:
            return str(char)
        
    def _no_parens(self, children):
        '''
        Returns True of no parens are needed around this when fmtting.
        '''
        return len(children) == 1 and \
            (isinstance(children[0], _Character) or
             len(children[0]) == 1 and isinstance(children[0][0], _Choice))
    
    def fmt_intervals(self, intervals):
        '''
        Hide unicode chars because of some strange error that occurs with
        Python2.6 on the command line.
        
        This is in StrAlphabet, but for ASCII makes no difference.  Having it
        here helps LineAwareAlphabet work (the whole idea of subclassing
        alphabets etc is not so great).
        '''
        def pretty(c):
            x = self._escape_char(c)
            if len(x) > 1 or 32 <= ord(x) <= 127:
                return str(x)
            elif ord(c) < 0x100:
                return fmt('\\x{0:02x}', ord(c)) 
            elif ord(c) < 0x10000:
                return fmt('\\u{0:04x}', ord(c)) 
            else:
                return fmt('\\U{0:08x}', ord(c)) 
        ranges = []
        if len(intervals) == 1:
            if intervals[0][0] == intervals[0][1]:
                return self._escape_char(intervals[0][0])
            elif intervals[0][0] == self.min and intervals[0][1] == self.max:
                return '.'
        # pylint: disable-msg=C0103
        # (sorry. but i use this (a, b) convention throughout the regexp lib) 
        for (a, b) in intervals:
            if a == b:
                ranges.append(pretty(a))
            else:
                ranges.append(fmt('{0!s}-{1!s}', pretty(a), pretty(b)))
        return fmt('[{0}]', self.join(ranges))
    
    def fmt_sequence(self, children):
        '''
        Generate a string representation of a sequence.
        
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return self.join(str(c) for c in children)
    
    def fmt_repeat(self, children):
        '''
        Generate a string representation of a repetition.
        
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        string = self.fmt_sequence(children)
        if self._no_parens(children):
            return string + '*'
        else:
            return fmt('(?:{0})*', string)

    def fmt_choice(self, children):
        '''
        Generate a string representation of a choice.
        
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return fmt('(?:{0})', '|'.join(str(child) for child in children))

    def fmt_option(self, children):
        '''
        Generate a string representation of an option.
        
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        string = self.fmt_sequence(children)
        if self._no_parens(children):
            return string + '?'
        else:
            return fmt('(?:{0})?', string)
        
    def fmt_label(self, label, child):
        '''
        Generate a string representation of labelled options.
        
        This must fully describe the data in the children (it is used to
        hash the data).
        '''
        return fmt('(?P<{0}>{1})', label, child)
        
    def join(self, chars):
        '''
        Join characters together.
        '''
        return ''.join(chars)
    
    def from_char(self, char):
        '''
        This must convert a single character.
        '''
        return char
    
    def parse(self, regexp):
        '''
        Generate a Sequence from the given text.
        '''
        return self._parser(regexp)

