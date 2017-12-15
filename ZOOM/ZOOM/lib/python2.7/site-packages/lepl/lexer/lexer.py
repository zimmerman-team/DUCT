
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

from lepl.support.lib import fmt
from lepl.support.context import NamespaceMixin
from lepl.matchers.support import BaseMatcher
from lepl.lexer.operators import TOKENS, TokenNamespace
from lepl.core.parser import tagged
from lepl.stream.core import s_empty, s_debug, s_stream, s_fmt, s_factory, \
    s_max, s_new_max, s_id, s_global_kargs, s_delta, s_len, \
    s_cache_level
from lepl.lexer.support import RuntimeLexerError
from lepl.regexp.core import Compiler

# pylint can't detect _kargs etc
# pylint: disable-msg=E1101

class Lexer(NamespaceMixin, BaseMatcher):
    '''
    This takes a set of regular expressions and provides a matcher that
    converts a stream into a stream of tokens, passing the new stream to 
    the embedded matcher.
    
    It is added to the matcher graph by the lexer_rewriter; it is not
    specified explicitly by the user.
    '''
    
    def __init__(self, matcher, tokens, alphabet, discard, 
                  t_regexp=None, s_regexp=None):
        '''
        matcher is the head of the original matcher graph, which will be called
        with a tokenised stream. 
        
        tokens is the set of `Token` instances that define the lexer.
        
        alphabet is the alphabet for which the regexps are defined.
        
        discard is the regular expression for spaces (which are silently
        dropped if not token can be matcher).
        
        t_regexp and s_regexp are internally compiled state, use in cloning,
        and should not be provided by non-cloning callers.
        '''
        super(Lexer, self).__init__(TOKENS, TokenNamespace)
        if t_regexp is None:
            unique = {}
            for token in tokens:
                token.compile(alphabet)
                self._debug(fmt('Token: {0}', token))
                # this just reduces the work for the regexp compiler
                unique[token.id_] = token
            t_regexp = Compiler.multiple(alphabet, 
                            [(t.id_, t.regexp) 
                             for t in unique.values() if t.regexp is not None]).dfa()
        if s_regexp is None and discard is not None:
            s_regexp = Compiler.single(alphabet, discard).dfa()
        self._arg(matcher=matcher)
        self._arg(tokens=tokens)
        self._arg(alphabet=alphabet)
        self._arg(discard=discard)
        self._karg(t_regexp=t_regexp)
        self._karg(s_regexp=s_regexp)
        
    def token_for_id(self, id_):
        '''
        A utility that checks the known tokens for a given ID.  The ID is used
        internally, but is (by default) an unfriendly integer value.  Note that 
        a lexed stream associates a chunk of input with a list of IDs - more 
        than one regexp may be a maximal match (and this is a feature, not a 
        bug).
        '''
        for token in self.tokens:
            if token.id_ == id_:
                return token
            
    def _tokens(self, stream, max):
        '''
        Generate tokens, on demand.
        '''
        try:
            id_ = s_id(stream)
            while not s_empty(stream):
                # avoid conflicts between tokens
                id_ += 1
                try:
                    (terminals, match, next_stream) = \
                                        self.t_regexp.match(stream)
                    self._debug(fmt('Token: {0!r} {1!r} {2!s}',
                                    terminals, match, s_debug(stream)))
                    yield (terminals, s_stream(stream, match, max=max, id_=id_))
                except TypeError:
                    (terminals, _size, next_stream) = \
                                        self.s_regexp.size_match(stream)
                    self._debug(fmt('Space: {0!r} {1!s}',
                                    terminals, s_debug(stream)))
                stream = next_stream
        except TypeError:
            raise RuntimeLexerError(
                s_fmt(stream, 
                      'No token for {rest} at {location} of {text}.'))
        
    @tagged
    def _match(self, in_stream):
        '''
        Implement matching - pass token stream to tokens.
        '''
        (max, clean_stream) = s_new_max(in_stream)
        try:
            length = s_len(in_stream)
        except TypeError:
            length = None
        factory = s_factory(in_stream)
        token_stream = factory.to_token(
                            self._tokens(clean_stream, max), 
                            id=s_id(in_stream), factory=factory, 
                            max=s_max(in_stream), 
                            global_kargs=s_global_kargs(in_stream),
                            delta=s_delta(in_stream), len=length,
                            cache_level=s_cache_level(in_stream)+1) 
        in_stream = None
        generator = self.matcher._match(token_stream)
        while True:
            yield (yield generator)
