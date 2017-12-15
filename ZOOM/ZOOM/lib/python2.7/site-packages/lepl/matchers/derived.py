
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
Matchers that are defined in terms of other matchers (ie the majority).
'''

from string import whitespace, digits, ascii_letters, \
    ascii_uppercase, ascii_lowercase, printable, punctuation
from operator import __add__

from lepl.matchers.combine import And, DepthFirst, BreadthFirst, \
    OrderByResultCount, Or, Limit
from lepl.matchers.core import Lookahead, Any, Eof, Literal, Regexp
from lepl.matchers.operators import BREADTH_FIRST, DEPTH_FIRST, GREEDY, \
    NON_GREEDY
from lepl.matchers.support import coerce_
from lepl.matchers.transform import TransformationWrapper, Transform, \
    ApplyArgs, ApplyRaw
from lepl.regexp.matchers import NfaRegexp, DfaRegexp
from lepl.support.lib import assert_type, lmap, fmt, basestring, reduce
from lepl.support.warn import warn_on_use

 
# pylint: disable-msg=C0103
# (consistent interface)
# pylint: disable-msg=W0142
# (*args)
# pylint: disable-msg=W0105
# (string comments)
# pylint: disable-msg=W0141
# (map)

def Repeat(matcher, start=0, stop=None, limit=None, algorithm=DEPTH_FIRST, 
            separator=None, add_=False, reduce=None):
    '''
    This is called by the [] operator.  It repeats the given matcher between
    `start` and `stop` number of times (inclusive).
    
    If `limit` is given it is an upper limit on the number of different
    results returned on backtracking.
    
    `algorithm` selects the repeat algorithm to use.
    
    If `separator` is given then each repetition is separated by that matcher.
    
    If `add_` is true then the results are joined with `Add` (once all
    results are obtained).
    
    If `reduce` is given it should be a pair (zero, join) where
    `join(results, next)` is used to accumulate results and `zero` is the
    initial value of `results`.  This is implemented via `Reduce`.

    `reduce` and `add_` cannot be given together.
    '''
    first = coerce_(matcher)
    if separator is None:
        rest = first
    else:
        rest = And(coerce_(separator, Regexp), first)
    if start is None:
        start = 0
    # allow duck typing (mutable values - IntVar etc)
#    assert_type('The start index for Repeat or [...]', start, int)
#    assert_type('The stop index for Repeat or [...]', stop, int, none_ok=True)
#    assert_type('The limit value (step index) for Repeat or [...]', limit, int, none_ok=True)
#    assert_type('The algorithm (step index) for Repeat or [...]', algorithm, str)
#    if start < 0:
#        raise ValueError('Repeat or [...] cannot have a negative start.')
#    if stop is not None and stop < start:
#        raise ValueError('Repeat or [...] must have a stop '
#                         'value greater than or equal to the start.')
#    if 'dbgn'.find(algorithm) == -1:
#        raise ValueError('Repeat or [...] must have a step (algorithm) '
#                         'of d, b, g or n.')
    if add_ and reduce:
        raise ValueError('Repeat cannot apply both add_ and reduce')
    elif add_:
        process = Add
    elif reduce:
        process = lambda r: Reduce(r, reduce[0], reduce[1])
    else:
        process = Identity
    matcher = {DEPTH_FIRST:
                process(DepthFirst(first=first, start=start, stop=stop, rest=rest)),
               BREADTH_FIRST: 
                process(BreadthFirst(first=first, start=start, stop=stop, rest=rest)),
               GREEDY:
                process(OrderByResultCount(
                        BreadthFirst(first=first, start=start, stop=stop, rest=rest))),
               NON_GREEDY:
                process(OrderByResultCount(
                        BreadthFirst(first=first, start=start, stop=stop, rest=rest),
                        False))
            }[algorithm]
    if limit is not None:
        matcher = Limit(matcher, count=limit)
    return matcher

            
def Apply(matcher, function, raw=False, args=False):
    '''
    Apply an arbitrary function to the results of the matcher 
    (**>**, **>=**).
    
    Apply can be used via the standard operators by placing ``>`` 
    (or ``>=`` to set ``raw=True``, or ``*`` to set ``args=True``) 
    to the right of a matcher.

    If the function is a `TransformationWrapper` it is used directly.  
    Otherwise a `TransformationWrapper` is constructed via the `raw` and 
    `args` parameters, as described below.

    **Note:** The creation of named pairs (when a string argument is
    used) behaves more like a mapping than a single function invocation.
    If several values are present, several pairs will be created.

    **Note:** There is an asymmetry in the default values of *raw*
    and *args*.  If the identity function is used with the default settings
    then a list of results is passed as a single argument (``args=False``).
    That is then returned (by the identity) as a list, which is wrapped
    in an additional list (``raw=False``), giving an extra level of
    grouping.  This is necessary because Python's ``list()`` is an
    identity for lists, but we want it to add an extra level of grouping
    so that nested S-expressions are easy to generate.
    
    See also `Map`.

    :Parameters:

      matcher
        The matcher whose results will be modified.

      function
        The modification to apply.
        
        If a `Transformation`, this is used directly.
        
        If a string is given, named pairs will be created (and raw and args
        ignored).
        
        Otherwise the function should expect a list of results (unless 
        ``args=True`` in which case the list is supplied as ``*args``)
        and can return any value (unless ``raw=True`` in which case it should
        return a list).

      raw
        If True the results are used directly.  Otherwise they are wrapped in
        a list.  The default is False --- a list is added.  This is set to
        true if the target function is an `ApplyRaw` instance.

      args
        If True, the results are passed to the function as separate
        arguments (Python's '*args' behaviour).  The default is False ---
        the results are passed inside a list).  This is set to true if the
        target function is an `ApplyArgs` instance.
    '''
    raw = raw or (type(function) is type and issubclass(function, ApplyRaw))
    args = args or (type(function) is type 
                      and issubclass(function, ApplyArgs))
    if isinstance(function, TransformationWrapper):
        apply = function
    else:
        if isinstance(function, basestring):
            function = lambda results, f=function: \
                            lmap(lambda x: (f, x), results)
            raw = True
            args = False
        if args:
            if raw:
                function = lambda results, f=function: f(*results)
            else:
                function = lambda results, f=function: [f(*results)]
        else:
            if not raw:
                function = lambda results, f=function: [f(results)]
        def apply(stream_in, matcher):
            (results, stream_out) = matcher()
            return (function(results), stream_out)
    return Transform(matcher, apply)


def args(function):
    '''
    A decorator that has the same effect as ApplyArgs for functions/methods.
    '''
    def wrapper(args_):
        '''
        Apply args as *args.
        '''
        return function(*args_)
    return wrapper


def KApply(matcher, function, raw=False):
    '''
    Apply an arbitrary function to named arguments (**\****).
    The function should typically expect and return a list.
    It can be used indirectly by placing ``**=`` to the right of the matcher.

    The function will be applied with the following keyword arguments:

      stream_out
        The stream returned from the matcher.

      results
        A list of the results returned.

    :Parameters:

      matcher
        The matcher whose results will be modified.

      function
        The modification to apply.

      raw
        If false (the default), the final return value from the function
        will be placed in a list and returned in a pair together with the
        new stream returned from the matcher (ie the function returns a
        single new result).

        If true, the final return value from the function is used directly
        and so should match the ``([results], stream)`` type expected by
        other matchers.
        '''
    def fun(stream_in, matcher):
        '''
        Apply args as **kargs.
        '''
        (results, stream_out) = matcher()
        kargs = {'results': results,
                 'stream_in': stream_in,
                 'stream_out': stream_out}
        if raw:
            return function(**kargs)
        else:
            return ([function(**kargs)], stream_out)
    return Transform(matcher, fun)

        
def AnyBut(exclude=None):
    '''
    Match any character except those specified (or, if a matcher is used as
    the exclude, if the matcher fails).
    
    The argument should be a list of tokens (or a string of suitable 
    characters) to exclude, or a matcher.  If omitted all tokens are accepted.
    '''
    return And(~Lookahead(coerce_(exclude, Any)), Any())
            

def Optional(matcher):
    '''
    Match zero or one instances of a matcher (**[0:1]**).
    '''
    return Repeat(coerce_(matcher), stop=1)
    #return Or(coerce_(matcher), Empty())


def Star(matcher):
    '''
    Match zero or more instances of a matcher (**[0:]**)
    '''
    return Repeat(coerce_(matcher))


ZeroOrMore = Star
'''
Match zero or more instances of a matcher (**[0:]**)
'''


def Plus(matcher):
    '''
    Match one or more instances of a matcher (**[1:]**)
    ''' 
    return Repeat(coerce_(matcher), start=1)


OneOrMore = Plus
'''
Match one or more instances of a matcher (**[1:]**)
''' 


def Map(matcher, function):
    '''
    Apply an arbitrary function to each of the tokens in the result of the 
    matcher (**>>**).  If the function is a name, named pairs are created 
    instead.  It can be used indirectly by placing ``>>`` to the right of the 
    matcher.
    
    See also `Apply`.
    '''
    # list() necessary so we can use '+' on result
    if isinstance(function, basestring):
        return Apply(matcher, lambda l: list(map(lambda x: (function, x), l)), 
                     raw=True)
    else:
        return Apply(matcher, lambda l: list(map(function, l)), raw=True)


def Reduce(matcher, zero, join=__add__):
    '''
    Combine the results from the matcher using `reduce(join, results, zero)`.
    Unlike `Add` this will return a value (`zero`) when there are no matches.
    '''
    def reduce_(_stream, matcher):
        (results, stream_out) = matcher()
        return ([reduce(join, results, zero)], stream_out)
    return Apply(matcher, TransformationWrapper(reduce_))


def add(_stream, matcher):
    '''
    The transformation used in `Add` - we carefully use "+" in as generic
    a manner as possible.
    '''
    (results, stream_out) = matcher()
    if results:
        result = results[0]
        for extra in results[1:]:
            try:
                result = result + extra
            except TypeError:
                raise TypeError(
                    fmt('An attempt was made to add two results '
                           'that do not have consistent types: {0!r} + {1!r}',
                           result, extra))
        result = [result]
    else:
        result = []
    return (result, stream_out)


def Add(matcher):
    '''
    Join tokens in the result using the "+" operator (**+**).
    This joins strings and merges lists.
    Unlike `Reduce` this will have no effect of there are no matches.
    '''
    return Apply(matcher, TransformationWrapper(add))


def Join(*matchers):
    '''
    Combine many matchers together with Add(And(...)).
    It can be used indirectly by placing ``+`` between matchers.
    '''
    return Add(And(*matchers))


def Drop(matcher):
    '''
    Do the match, but return nothing (**~**).  The ~ prefix is equivalent.
    '''
    return Apply(matcher, lambda l: [], raw=True)


def Substitute(matcher, value):
    '''
    Replace each return value with that given.
    '''
    return Map(matcher, lambda x: value)


def Name(matcher, name):
    '''
    Name the result of matching (**> name**)
    
    This replaces each value in the match with a tuple whose first value is 
    the given name and whose second value is the matched token.  The Node 
    class recognises this form and associates such values with named attributes.
    '''
    return Map(matcher, name)


Eos = Eof
'''Match the end of a stream.  Returns nothing.'''


def Identity(matcher):
    '''Functions identically to the matcher given as an argument.'''
    return coerce_(matcher)


def Newline():
    '''Match newline (Unix) or carriage return newline (Windows)'''
    return Or(Literal('\n'), Literal('\r\n'))


def Space(space=' \t'):
    '''Match a single space (by default space or tab).'''
    return Any(space)


def Whitespace(space=whitespace):
    '''
    Match a single space (by default from string.whitespace,
    which includes newlines).
    '''
    return Any(space)


def Digit():
    '''Match any single digit.'''
    return Any(digits)


def Letter():
    '''Match any ASCII letter (A-Z, a-z).'''
    return Any(ascii_letters)


def Upper():
    '''Match any ASCII uppercase letter (A-Z).'''
    return Any(ascii_uppercase)

    
def Lower():
    '''Match any ASCII lowercase letter (A-Z).'''
    return Any(ascii_lowercase)


def Printable():
    '''Match any printable character (string.printable).'''
    return Any(printable)


def Punctuation():
    '''Match any punctuation character (string.punctuation).'''
    return Any(punctuation)


def UnsignedInteger():
    '''Match a  simple sequence of digits.'''
    return Repeat(Digit(), start=1, add_=True)


def SignedInteger():
    '''Match a sequence of digits with an optional initial sign.'''
    return Add(And(Optional(Any('+-')), UnsignedInteger()))

    
Integer = SignedInteger
'''
The default integer is a signed one.
'''


def UnsignedReal(decimal='.'):
    '''
    Match a sequence of digits that may include a decimal point.  This
    will match both integer and float values.
    '''
    return Or(Join(Optional(UnsignedInteger()), 
                   Any(decimal), UnsignedInteger()),
              Join(UnsignedInteger(), Optional(Any(decimal))))

    
def SignedReal(decimal='.'):
    '''
    Match a signed sequence of digits that may include a decimal point.  
    This will match both integer and float values.
    '''
    return Join(Optional(Any('+-')), UnsignedReal(decimal))
    
    
def UnsignedEReal(decimal='.', exponent='eE'):
    '''
    Match an `UnsignedReal` followed by an optional exponent 
    (e+02 etc).  This will match both integer and float values.
    '''
    return Join(UnsignedReal(decimal), 
                Optional(And(Any(exponent), SignedInteger())))

    
def SignedEReal(decimal='.', exponent='eE'):
    '''
    Match a `SignedReal` followed by an optional exponent 
    (e+02 etc).  This will match both integer and float values.
    '''
    if decimal == '.' and exponent == 'eE':
        # hack to faster direct implementation for now
        return NfaRegexp(r'[\+\-]?(?:[0-9]*\.[0-9]+|[0-9]+\.|[0-9]+)(?:[eE][\+\-]?[0-9]+)?')
    else:
        return Join(SignedReal(decimal), 
                    Optional(Join(Any(exponent), SignedInteger())))

    
Real = SignedEReal
'''
The default float is signed with exponents.
'''

_FLOAT_WARN = '''WARNING: The definition of the Float matchers changed in Lepl 4.4.0
(you may want to use Real instead).'''

@warn_on_use(_FLOAT_WARN)
def UnsignedFloat(decimal='.'):
    '''
    Match a sequence of digits that must include a decimal point.  This
    will match real values that are not integers.
    '''
    return Or(Join(Optional(UnsignedInteger()), 
                   Any(decimal), UnsignedInteger()),
              Join(UnsignedInteger(), Any(decimal)))
              
    
@warn_on_use(_FLOAT_WARN)
def SignedFloat(decimal='.'):
    '''
    Match a signed sequence of digits that must include a decimal point.  This
    will match real values that are not integers.
    '''
    return Join(Optional(Any('+-')), UnsignedFloat(decimal))
    
    
@warn_on_use(_FLOAT_WARN)
def UnsignedEFloat(decimal='.', exponent='eE'):
    '''
    As `UnsignedEReal`, but must contain a decimal or exponent.  This
    will match real values that are not integers.
    '''
    return Or(Join(UnsignedReal(decimal), Any(exponent), SignedInteger()),
              UnsignedFloat(decimal))

    
@warn_on_use(_FLOAT_WARN)
def SignedEFloat(decimal='.', exponent='eE'):
    '''
    As `SignedEReal`, but must contain a decimal or exponent.  This
    will match real values that are not integers.
    '''
    if decimal == '.' and exponent == 'eE':
        # hack to faster direct implementation for now
        return NfaRegexp(r'[\+\-]?(?:[0-9]*\.[0-9]+(?:[eE][\+\-]?[0-9]+)?|[0-9]+\.(?:[eE][\+\-]?[0-9]+)?|[0-9]+[eE][\+\-]?[0-9]+)')
    else:
        return Or(Join(SignedReal(decimal), Any(exponent), SignedInteger()),
                  SignedFloat(decimal))

    
Float = SignedEFloat
'''
The default float matcher accepts signed values with optional exponents.
This will not match integers - see `Real` for that.
'''


def Word(chars=NfaRegexp('[^%s]' % whitespace), body=None):
    '''
    Match a sequence of non-space characters, joining them together. 
     
    chars and body, if given as strings, define possible characters to use
    for the first and rest of the characters in the word, respectively.
    If body is not given, then chars is used for the entire word.
    They can also specify matchers, which typically should match only a
    single character.
    
    So ``Word(Upper(), Lower())`` would match names that being with an upper
    case letter, for example, while ``Word(AnyBut(Space()))`` (the default)
    matches any sequence of non-space characters. 
    '''
    chars = coerce_(chars, Any)
    body = chars if body is None else coerce_(body, Any)
    return Add(And(chars, Star(body)))
 
 
def DropEmpty(matcher):
    '''
    Drop results if they are empty (ie if they are ``False`` in Python).
    
    This will drop empty strings and lists.  It will also drop
    `Node` instances if they are empty (since the length is then
    zero).
    '''
    def drop(results):
        '''
        Only drop "False" values.
        '''
        return [result for result in results if result]
    return Apply(matcher, drop, raw=True)


def Literals(*matchers):
    '''
    A series of literals, joined with `Or`.
    '''
    # I considered implementing this by extending Literal() itself, but
    # that would have meant putting "Or-like" functionality in Literal,
    # and I felt it better to keep the base matchers reasonably orthogonal.
    return Or(*lmap(Literal, matchers))


def String(quote='"', escape='\\', empty='', join=__add__):
    '''
    Match a string with quotes that can be escaped.  This will match across
    newlines (see `SingleLineString` for an alternative).

    More generally, a string is a grouping of results.  Setting `empty` and
    `join` correctly will allow this matcher to work with a variety of types.
    '''
    q = Literal(quote)
    content = AnyBut(q)
    if escape:
        content = Or(And(Drop(escape), q), content)
    content = Repeat(content, reduce=(empty, join))
    return And(Drop(q), content, Drop(q))


def SingleLineString(quote='"', escape='\\', exclude='\n', empty='', join=__add__):
    '''
    Like `String`,  but will not match across multiple lines.
    '''
    q = Literal(quote)
    content = AnyBut(Or(q, Any(exclude)))
    if escape:
        content = Or(content, And(Drop(escape), q))
    content = Repeat(content, reduce=(empty, join))
    return And(Drop(q), content, Drop(q))


def SkipString(quote='"', escape='\\', ignore='\n', empty='', join=__add__):
    '''
    Like `String`, matching across multiple lines, but will silently 
    drop newlines.
    '''
    q = Literal(quote)
    content = AnyBut(Or(q, Any(ignore)))
    if escape:
        content = Or(content, And(Drop(escape), q))
    content = Or(content, Drop(Any(ignore)))
    content = Repeat(content, reduce=(empty, join))
    return And(Drop(q), content, Drop(q))


def SkipTo(matcher, include=True):
    '''
    Consume everything up to (and including, if include is True, as it is by
    default) the matcher.  Returns all the skipped data, joined.
    '''
    if include:
        return Add(And(Star(AnyBut(matcher)), matcher))
    else:
        return And(Add(Star(AnyBut(matcher))), Lookahead(matcher))


