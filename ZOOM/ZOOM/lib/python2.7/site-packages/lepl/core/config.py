
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
The main configuration object and various standard configurations.
'''

# pylint bug?
# pylint: disable-msg=W0404

from collections import namedtuple

from lepl.core.parser import make_raw_parser, make_single, make_multiple
from lepl.stream.factory import DEFAULT_STREAM_FACTORY


Configuration = namedtuple('Configuration', 
                           'rewriters monitors stream_factory stream_kargs')
'''Carrier for configuration.'''

    
class ConfigurationError(Exception):
    '''
    Error raised for problems with configuration.
    '''
    pass


class ConfigBuilder(object):
    '''
    Accumulate configuration through chained methods.
    '''
    
    def __init__(self, matcher):
        # we need to delay startup, to avoid loops
        self.__started = False
        # this is set whenever any config is changed.  it is cleared when
        # the configuration is read.  so if is is false then the configuration
        # is the same as previously read
        self.__changed = True
        self.__rewriters = set()
        self.__monitors = []
        self.__stream_factory = DEFAULT_STREAM_FACTORY
        self.__alphabet = None
        self.__stream_kargs = {}
        # this is set from the matcher.  it gives a memory loop, but not a 
        # very serious one, and allows single line configuration which is 
        # useful for timing.
        self.matcher = matcher
        
    def __start(self):
        '''
        Set default values on demand to avoid dependency loop.
        '''
        if not self.__started:
            self.__started = True
            self.default()
            
        
    # raw access to basic components
        
    def add_rewriter(self, rewriter):
        '''
        Add a rewriter that will be applied to the matcher graph when the
        parser is generated.
        '''
        self.__start()
        self.clear_cache()
        # we need to remove before adding to ensure last added is the one
        # used (exclusive rewriters are equal)
        if rewriter in self.__rewriters:
            self.__rewriters.remove(rewriter)
        self.__rewriters.add(rewriter)
        return self
    
    def remove_rewriter(self, rewriter):
        '''
        Remove a rewriter from the current configuration.
        '''
        self.__start()
        self.clear_cache()
        self.__rewriters = set(r for r in self.__rewriters 
                               if r is not rewriter)
        return self

    def remove_all_rewriters(self, type_=None):
        '''
        Remove all rewriters of a given type from the current configuration.
        '''
        self.__start()
        self.clear_cache()
        if type_:
            self.__rewriters = set(r for r in self.__rewriters 
                                   if not isinstance(r, type_))
        else:
            self.__rewriters = set()
        return self

    def add_monitor(self, monitor):
        '''
        Add a monitor to the current configuration.  Monitors are called
        from within the trampolining process and can be used to track 
        evaluation, control resource use, etc.
        '''
        self.__start()
        self.clear_cache()
        self.__monitors.append(monitor)
        return self
    
    def remove_all_monitors(self):
        '''
        Remove all monitors from the current configuration.
        '''
        self.__start()
        self.clear_cache()
        self.__monitors = []
        return self
    
    def stream_factory(self, stream_factory=DEFAULT_STREAM_FACTORY):
        '''
        Specify the stream factory.  This is used to generate the input stream
        for the parser.
        '''
        self.__start()
        self.clear_cache()
        self.__stream_factory = stream_factory
        return self
    
    def add_stream_kargs(self, ** kargs):
        '''
        Add a value for passing to the stream factory.
        '''
        for name in kargs:
            self.__stream_kargs[name] = kargs[name]
        return self
    
    def remove_all_stream_kargs(self):
        '''
        Remove all values passed to the stream factory.
        '''
        self.__stream_kargs = {}

    @property
    def configuration(self):
        '''
        The current configuration (rewriters, monitors, stream_factory).
        '''
        self.__start()
        self.__changed = False
        rewriters = list(self.__rewriters)
        rewriters.sort()
        return Configuration(rewriters, list(self.__monitors),
                             self.__stream_factory, dict(self.__stream_kargs))
    
    def __get_alphabet(self):
        '''
        Get the alphabet used.
        
        Typically this is Unicode, which is the default.  It is needed for
        the generation of regular expressions. 
        '''
        from lepl.regexp.unicode import UnicodeAlphabet
        if not self.__alphabet:
            self.__alphabet = UnicodeAlphabet.instance()
        return self.__alphabet
    
    def alphabet(self, alphabet):
        '''
        Set the alphabet used.  It is needed for the generation of regular 
        expressions, for example (but the default, for Unicode, is usually
        sufficient).
        '''
        if alphabet:
            if self.__alphabet:
                if self.__alphabet != alphabet:
                    raise ConfigurationError(
                        'Alphabet has changed during configuration '
                        '(perhaps the default was already used?)')
            else:
                self.__alphabet = alphabet
                self.__start()
                self.clear_cache()
                
    @property
    def changed(self):
        '''
        Has the config been changed by the user since it was last returned
        via `configuration`?  if not, any previously generated parser can be
        reused.
        '''
        return self.__changed
    
    def clear_cache(self):
        '''
        Force calculation of a new parser.
        '''
        self.__changed = True
    
    # rewriters
    
    def set_arguments(self, type_, **kargs):
        '''
        Set the given keyword arguments on all matchers of the given `type_`
        (ie class) in the grammar.
        '''
        from lepl.core.rewriters import SetArguments
        return self.add_rewriter(SetArguments(type_, **kargs))
    
    def no_set_arguments(self):
        '''
        Remove all rewriters that set arguments.
        '''
        from lepl.core.rewriters import SetArguments
        return self.remove_all_rewriters(SetArguments)
        
    def set_alphabet_arg(self, alphabet=None):
        '''
        Set `alphabet` on various matchers.  This is useful when using an 
        unusual alphabet (most often when using line-aware parsing), as
        it saves having to specify it on each matcher when creating the
        grammar.
        '''
        from lepl.regexp.matchers import BaseRegexp
        from lepl.lexer.matchers import BaseToken
        if alphabet:
            self.alphabet(alphabet)
        else:
            alphabet = self.__get_alphabet()
        if not alphabet:
            raise ValueError('An alphabet must be provided or already set')
        self.set_arguments(BaseRegexp, alphabet=alphabet)
        self.set_arguments(BaseToken, alphabet=alphabet)
        return self

    def full_first_match(self, eos=True):
        '''
        Raise an error if the first match fails.  If `eos` is True then this
        requires that the entire input is matched, otherwise it only requires
        that the matcher succeed.  The exception includes information about
        the deepest read to the stream (which is a good indication of where
        any error occurs).
        
        This is part of the default configuration.  It can be removed with
        `no_full_first_match()`.
        '''
        from lepl.core.rewriters import FullFirstMatch
        return self.add_rewriter(FullFirstMatch(eos))
        
    def no_full_first_match(self):
        '''
        Disable the automatic generation of an error if the first match fails.
        '''
        from lepl.core.rewriters import FullFirstMatch
        return self.remove_all_rewriters(FullFirstMatch)
    
    def flatten(self):
        '''
        Combined nested `And()` and `Or()` matchers.  This does not change
        the parser semantics, but improves efficiency.
        
        This is part of the default configuration.  It can be removed with
        `no_flatten`.
        '''
        from lepl.core.rewriters import Flatten
        return self.add_rewriter(Flatten())
    
    def no_flatten(self):
        '''
        Disable the combination of nested `And()` and `Or()` matchers.
        '''
        from lepl.core.rewriters import Flatten
        return self.remove_all_rewriters(Flatten)
        
    def compile_to_dfa(self, force=False, alphabet=None):
        '''
        Compile simple matchers to DFA regular expressions.  This improves
        efficiency but may change the parser semantics slightly (DFA regular
        expressions do not provide backtracking / alternative matches).
        '''
        from lepl.regexp.matchers import DfaRegexp
        from lepl.regexp.rewriters import CompileRegexp
        self.alphabet(alphabet)
        return self.add_rewriter(
                    CompileRegexp(self.__get_alphabet(), force, DfaRegexp))
    
    def compile_to_nfa(self, force=False, alphabet=None):
        '''
        Compile simple matchers to NFA regular expressions.  This improves
        efficiency and should not change the parser semantics.
        
        This is part of the default configuration.  It can be removed with
        `no_compile_regexp`.
        '''
        from lepl.regexp.matchers import NfaRegexp
        from lepl.regexp.rewriters import CompileRegexp
        self.alphabet(alphabet)
        return self.add_rewriter(
                    CompileRegexp(self.__get_alphabet(), force, NfaRegexp))

    def compile_to_re(self, force=False, alphabet=None):
        '''
        Compile simple matchers to re (C library) regular expressions.  
        This improves efficiency but may change the parser semantics slightly 
        (DFA regular expressions do not provide backtracking / alternative 
        matches).
        '''
        from lepl.matchers.core import Regexp
        from lepl.regexp.rewriters import CompileRegexp
        def regexp_wrapper(regexp, _alphabet):
            '''
            Adapt the Regexp matcher to the form needed (forcing Unicode).
            '''
            return Regexp(str(regexp))
        self.alphabet(alphabet)
        return self.add_rewriter(
                    CompileRegexp(self.__get_alphabet(), force, regexp_wrapper))

    def no_compile_to_regexp(self):
        '''
        Disable compilation of simple matchers to regular expressions.
        '''
        from lepl.regexp.rewriters import CompileRegexp
        return self.remove_all_rewriters(CompileRegexp)
    
    def optimize_or(self, conservative=False):
        '''
        Rearrange arguments to `Or()` so that left-recursive matchers are
        tested last.  This improves efficiency, but may alter the parser
        semantics (the ordering of multiple results with ambiguous grammars 
        may change).
        
        `conservative` refers to the algorithm used to detect loops; False
        may classify some left--recursive loops as right--recursive.
        '''
        from lepl.core.rewriters import OptimizeOr
        return self.add_rewriter(OptimizeOr(conservative))
    
    def no_optimize_or(self):
        '''
        Disable the re-ordering of some `Or()` arguments.
        '''
        from lepl.core.rewriters import OptimizeOr
        return self.remove_all_rewriters(OptimizeOr)
        
    def lexer(self, alphabet=None, discard=None, lexer=None):
        '''
        Detect the use of `Token()` and modify the parser to use the lexer.
        If tokens are not used, this has no effect on parsing.
        
        This is part of the default configuration.  It can be disabled with
        `no_lexer`.
        '''
        from lepl.lexer.rewriters import AddLexer
        self.alphabet(alphabet)
        return self.add_rewriter(
            AddLexer(alphabet=self.__get_alphabet(), 
                     discard=discard, lexer=lexer))
        
    def no_lexer(self):
        '''
        Disable support for the lexer.
        '''
        from lepl.lexer.rewriters import AddLexer
        self.remove_all_rewriters(AddLexer)
    
    def direct_eval(self, spec=None):
        '''
        Combine simple matchers so that they are evaluated without 
        trampolining.  This improves efficiency (particularly because it
        reduces the number of matchers that can be memoized).
        
        This is part of the default configuration.  It can be removed with
        `no_direct_eval`.
        '''
        from lepl.core.rewriters import DirectEvaluation
        return self.add_rewriter(DirectEvaluation(spec))
    
    def no_direct_eval(self):
        '''
        Disable direct evaluation.
        '''
        from lepl.core.rewriters import DirectEvaluation
        return self.remove_all_rewriters(DirectEvaluation)
    
    def compose_transforms(self):
        '''
        Combine transforms (functions applied to results) with matchers.
        This may improve efficiency.
        
        This is part of the default configuration.  It can be removed with
        `no_compose_transforms`.
        '''
        from lepl.core.rewriters import ComposeTransforms
        return self.add_rewriter(ComposeTransforms())
    
    def no_compose_transforms(self):
        '''
        Disable the composition of transforms.
        '''
        from lepl.core.rewriters import ComposeTransforms
        return self.remove_all_rewriters(ComposeTransforms)
        
    def auto_memoize(self, conservative=None, full=True, d=0):
        '''
        This configuration attempts to detect which memoizer is most effective
        for each matcher.  As such it is a general "fix" for left-recursive 
        grammars and is suggested in the warning shown when the right-only 
        memoizer detects left recursion.
        
        Lepl does not guarantee that all left-recursive grammars are handled 
        correctly.  The corrections applied may be incomplete and can be
        inefficient.  It is always better to re-write a grammar to avoid
        left-recursion.  One way to improve efficiency, at the cost of less
        accurate matching, is to specify a non-zero ``d`` parameter - this 
        is the maximum iteration depth that will be used (by default, when
        ``d`` is zero, it is the length of the remaining input, which can
        be very large).
        
        '''
        from lepl.core.rewriters import AutoMemoize
        from lepl.matchers.memo import LMemo, RMemo
        self.no_memoize()
        return self.add_rewriter(
            AutoMemoize(conservative=conservative, left=LMemo,
                        right=RMemo if full else None, d=d))
    
    def left_memoize(self, d=0):
        '''
        Add memoization that may detect and stabilise left-recursion.  This
        makes the parser more robust (so it can handle more grammars) but
        also more complex (and probably slower).
        
        ``config.auto_memoize()`` will also add memoization, but will select
        left/right memoization depending on the path through the parser.
        
        Lepl does not guarantee that all left-recursive grammars are handled 
        correctly.  The corrections applied may be incomplete and can be
        inefficient.  It is always better to re-write a grammar to avoid
        left-recursion.  One way to improve efficiency, at the cost of less
        accurate matching, is to specify a non-zero ``d`` parameter - this 
        is the maximum iteration depth that will be used (by default, when
        ``d`` is zero, it is the length of the remaining input, which can
        be very large).
        '''
        from lepl.core.rewriters import LeftMemoize
        self.no_memoize()
        return self.add_rewriter(LeftMemoize(d))
    
    def right_memoize(self):
        '''
        Add memoization that can make some complex parsers (with a lot of
        backtracking) more efficient.  This also detects left-recursive
        grammars and displays a suitable warning.
        
        This is included in the default configuration.  For simple grammars 
        it may make things slower; it can be disabled by 
        ``config.no_memoize()``. 
        '''      
        from lepl.core.rewriters import RightMemoize
        self.no_memoize()
        return self.add_rewriter(RightMemoize())
    
    def no_memoize(self):
        '''
        Remove memoization.  To use the default configuration without
        memoization (which may be faster in some cases), specify 
        `config.no_memoize()`.
        '''
        from lepl.core.rewriters import AutoMemoize, LeftMemoize, RightMemoize
        self.remove_all_rewriters(LeftMemoize)
        self.remove_all_rewriters(RightMemoize)
        return self.remove_all_rewriters(AutoMemoize)
        
    def lines(self, discard=None, tabsize=8, 
              block_policy=None, block_start=None):
        '''
        Configure "offside parsing".  This enables lexing and adds extra
        tokens to mark the start and end of lines.  If block_policy is 
        specified then the line start token will also include spaces
        which can be used by the ``Block()`` and ``BLine()`` matchers
        to do offside (whitespace-aware) parsing.
        
        `discard` is the regular expression to use to identify spaces
        between tokens (by default, spaces and tabs).
        
        The remaining parameters are used only if at least one of 
        `block_policy` and `block_start` is given.
        
        `block_policy` decides how indentation if calculated.
        See `explicit` etc in lepl.lexer.blocks.matchers.
        
        `block_start` is the initial indentation (by default, zero).  If set 
        to lepl.lexer.lines.matchers.NO_BLOCKS indentation will not 
        be checked (useful for tests).

        `tabsize` is used only if `block_policy` is given.  It is the number 
        of spaces used to replace a leading tab (no replacement if None).
        '''
        from lepl.lexer.lines.lexer import make_offside_lexer
        from lepl.lexer.lines.matchers import Block, DEFAULT_POLICY, LineStart
        from lepl.lexer.lines.monitor import block_monitor
        blocks = block_policy is not None or block_start is not None
        if blocks:
            if block_start is None:
                block_start = 0
            if block_policy is None:
                block_policy = DEFAULT_POLICY
            self.add_monitor(block_monitor(block_start))
            self.set_arguments(Block, policy=block_policy)
        else:
            self.set_arguments(LineStart, indent=False)
        self.lexer(self.__get_alphabet(), discard, 
                   make_offside_lexer(tabsize, blocks))
        return self
    
        
    # monitors
    
    def trace_stack(self, enabled=False):
        '''
        Add a monitor to trace results using `TraceStack()`.
        
        This is not used by default as it has a cost at runtime.
        '''
        from lepl.core.trace import TraceStack
        return self.add_monitor(TraceStack(enabled))
    
    def trace_variables(self):
        '''
        Add a monitor to correctly insert the transforms needed when using 
        the `TraceVariables()` context:
        
          with TraceVariables():
            ...
        
        This is used by default as it has no runtime cost (once the parser
        is created).
        '''
        from lepl.core.rewriters import TraceVariables
        return self.add_rewriter(TraceVariables())
    
    def low_memory(self, queue_len=100):
        '''
        Reduce memory use (at the expense of backtracking).
        
        This will:
        - Add a monitor to manage resources.  See `GeneratorManager()`.
        - Disable direct evaluation (more trampolining gives more scope
          for removing generators)
        - Disable the full first match error (which requires a copy of the
          input for the error message)
        - Disable memoisation (which would keep input in memory)
        
        This reduces memory usage, but makes the parser less reliable.
        Usually a value like 100 (the default) for the queue length will make 
        memory use insignificant and still give a useful first parse.
        
        Note that, although the parser will use less memory, it may run
        more slowly (as extra work needs to be done to "clean out" the 
        stored values).
        '''
        from lepl.core.manager import GeneratorManager
        self.add_monitor(GeneratorManager(queue_len))
        self.no_direct_eval()
        self.no_memoize()
        self.no_full_first_match()
        self.cache_level(-9)
        return self
    
    def cache_level(self, level=1):
        '''
        Control when the stream can be cached internally (this is used for
        debugging and error messages) - streams are cached for debugging when 
        the value is greater than zero.  The value is incremented each time
        a new stream is constructed (eg when constructing tokens).
        
        A value of 1 implies that a stream would be always cached.  A value of 
        0 might be used when iterating over a file with the lexer - the 
        iteration is not cached, but individual tokens will be.
        '''
        self.add_stream_kargs(cache_level=level)
    
    def record_deepest(self, n_before=6, n_results_after=2, n_done_after=2):
        '''
        Add a monitor to record deepest match.  See `RecordDeepest()`.
        '''
        from lepl.core.trace import RecordDeepest
        return self.add_monitor(
                RecordDeepest(n_before, n_results_after, n_done_after))
    
    # packages
   
    def clear(self):
        '''
        Delete any earlier configuration and disable the default (so no
        rewriters or monitors are used).
        '''
        self.__started = True
        self.clear_cache()
        self.__rewriters = set()
        self.__monitors = []
        self.__stream_factory = DEFAULT_STREAM_FACTORY
        self.__alphabet = None
        return self

    def default(self):
        '''
        Provide the default configuration (deleting what may have been
        configured previously).  This is equivalent to the initial 
        configuration.  It provides a moderately efficient, stable parser.
        '''
        self.clear()
        self.flatten()
        self.trace_variables()
        self.compose_transforms()
        self.lexer()
        self.right_memoize()
        self.direct_eval()
        self.compile_to_nfa()
        self.full_first_match()
        return self


class ParserMixin(object):
    '''
    Methods to configure and generate a parser or matcher.
    '''
    
    def __init__(self, *args, **kargs):
        super(ParserMixin, self).__init__(*args, **kargs)
        self.config = ConfigBuilder(self)
        self.__raw_parser_cache = None
        self.__from = None # needed to check cache is valid
        
    def _raw_parser(self, from_=None):
        '''
        Provide the parser.  This underlies the "fancy" methods below.
        '''
        if self.config.changed or self.__raw_parser_cache is None \
                or self.__from != from_:
            config = self.config.configuration
            self.__from = from_
            if from_:
                stream_factory = \
                    getattr(config.stream_factory, 'from_' + from_)
            else:
                stream_factory = config.stream_factory # __call__
            self.__raw_parser_cache = \
                make_raw_parser(self, stream_factory, config)
        return self.__raw_parser_cache
    
    
    def get_match_file(self):
        '''
        Get a function that will parse the contents of a file, returning a 
        sequence of (results, stream) pairs.  The data will be read as 
        required (using an iterator), so the file must remain open during 
        parsing.  To avoid this, read all data into a string and parse that.
        '''
        return self._raw_parser('file')
        
    def get_match_iterable(self):
        '''
        Get a function that will parse the contents of an iterable
        (eg. a generator), returning a sequence of (results, stream) pairs.
        The data will be read as required.
        '''
        return self._raw_parser('iterable')
        
    def get_match_list(self):
        '''
        Get a function that will parse the contents of a list returning a 
        sequence of (results, stream) pairs.
        '''
        return self._raw_parser('list')
        
    def get_match_string(self,):
        '''
        Get a function that will parse the contents of a string returning a 
        sequence of (results, stream) pairs.
        '''
        return self._raw_parser('string')
    
    def get_match_sequence(self):
        '''
        Get a function that will parse the contents of a generic sequence
        (with [] and len()) returning a sequence of (results, stream) pairs.
        '''
        return self._raw_parser('sequence')
    
    def get_match(self):
        '''
        Get a function that will parse input, returning a sequence of 
        (results, stream) pairs.  
        The type of stream is inferred from the input to the parser.
        '''
        return self._raw_parser()
    
    
    def match_file(self, file_, **kargs):
        '''
        Parse the contents of a file, returning a sequence of 
        (results, stream) pairs.  The data will be read as required 
        (using an iterator), so the file must remain open during parsing.  
        To avoid this, read all data into a string and parse that.
        '''
        return self.get_match_file()(file_, **kargs)
        
    def match_iterable(self, iterable, **kargs):
        '''
        Parse the contents of an iterable (eg. a generator), returning 
        a sequence of (results, stream) pairs.  The data will be read as 
        required.
        '''
        return self.get_match_iterable()(iterable, **kargs)
        
    def match_list(self, list_, **kargs):
        '''
        Parse the contents of a list returning a sequence of (results, stream) 
        pairs.
        '''
        return self.get_match_list()(list_, **kargs)
        
    def match_string(self, string, **kargs):
        '''
        Parse the contents of a string, returning a sequence of 
        (results, stream) pairs.
        '''
        return self.get_match_string()(string, **kargs)
    
    def match_sequence(self, sequence, **kargs):
        '''
        Parse the contents of a generic sequence (with [] and len()) 
        returning a sequence of (results, stream) pairs.
        '''
        return self.get_match_sequence()(sequence, **kargs)
    
    def match(self, input_, **kargs):
        '''
        Parse input, returning a sequence of (results, stream) pairs.  
        The type of stream is inferred from the input.
        '''
        return self.get_match()(input_, **kargs)
    
    
    def get_parse_file(self):
        '''
        Get a function that will parse the contents of a file, returning a 
        single match.  The data will be read as required (using an iterator), 
        so the file must remain open during parsing.  To avoid this, read 
        all data into a string and parse that.
        '''
        return make_single(self.get_match_file())
        
    def get_parse_iterable(self):
        '''
        Get a function that will parse the contents of an iterable
        (eg. a generator), returning a single match.  The data will be read 
        as required.
        '''
        return make_single(self.get_match_iterable())
        
    def get_parse_list(self):
        '''
        Get a function that will parse the contents of a list returning a 
        single match.
        '''
        return make_single(self.get_match_list())
        
    def get_parse_string(self):
        '''
        Get a function that will parse the contents of a string returning a 
        single match.
        '''
        return make_single(self.get_match_string())
    
    def get_parse_sequence(self):
        '''
        Get a function that will parse the contents of a generic sequence
        (with [] and len()) returning a single match.
        '''
        return make_single(self.get_match_sequence())
    
    def get_parse(self):
        '''
        Get a function that will parse input, returning a single match.
        The type of stream is inferred from the input to the parser.
        '''
        return make_single(self.get_match())
    
    
    def parse_file(self, file_, **kargs):
        '''
        Parse the contents of a file, returning a single match.  The data 
        will be read as required (using an iterator), so the file must 
        remain open during parsing.  To avoid this, read all data into a
        string and parse that.
        '''
        return self.get_parse_file()(file_, **kargs)
        
    def parse_iterable(self, iterable, **kargs):
        '''
        Parse the contents of an iterable (eg. a generator), returning 
        a single match.  The data will be read as required.
        '''
        return self.get_parse_iterable()(iterable, **kargs)
        
    def parse_list(self, list_, **kargs):
        '''
        Parse the contents of a list returning a single match.
        '''
        return self.get_parse_list()(list_, **kargs)
    
    def parse_string(self, string, **kargs):
        '''
        Parse the contents of a string, returning a single match.
        '''
        return self.get_parse_string()(string, **kargs)
    
    def parse_sequence(self, sequence, **kargs):
        '''
        Pparse the contents of a generic sequence (with [] and len()) 
        returning a single match.
        '''
        return self.get_parse_sequence()(sequence, **kargs)
    
    def parse(self, input_, **kargs):
        '''
        Parse the input, returning a single match.  The type of stream is 
        inferred from the input.
        '''
        return self.get_parse()(input_, **kargs)
    
    
    def get_parse_file_all(self):
        '''
        Get a function that will parse the contents of a file, returning a 
        sequence of matches.  The data will be read as required (using an 
        iterator), so the file must remain open during parsing.  To avoid 
        this, read all data into a string and parse that.
        '''
        return make_multiple(self.get_match_file())
        
    def get_parse_iterable_all(self):
        '''
        Get a function that will parse the contents of an iterable
        (eg. a generator), returning a sequence of matches.  The data will 
        be read as required.
        '''
        return make_multiple(self.get_match_iterable())
        
    def get_parse_list_all(self):
        '''
        Get a function that will parse the contents of a list returning a 
        sequence of matches.
        '''
        return make_multiple(self.get_match_list())
        
    def get_parse_string_all(self):
        '''
        Get a function that will parse a string, returning a sequence of 
        matches.
        '''
        return make_multiple(self.get_match_string())

    def get_parse_sequence_all(self):
        '''
        Get a function that will parse the contents of a generic sequence
        (with [] and len()) returning a sequence of matches.
        '''
        return make_multiple(self.get_match_sequence())

    def get_parse_all(self):
        '''
        Get a function that will parse input, returning a sequence of 
        matches.  The type of stream is inferred from the input to the 
        parser.
        '''
        return make_multiple(self.get_match())

    
    def parse_file_all(self, file_, **kargs):
        '''
        Parse the contents of a file, returning a sequence of matches.  
        The data will be read as required (using an iterator), so the file 
        must remain open during parsing.  To avoid this, read all data 
        into a string and parse that.
        '''
        return self.get_parse_file_all()(file_, **kargs)
        
    def parse_iterable_all(self, iterable, **kargs):
        '''
        Parse the contents of an iterable (eg. a generator), returning 
        a sequence of matches.  The data will be read as required.
        '''
        return self.get_parse_iterable_all()(iterable, **kargs)
        
    def parse_list_all(self, list_, **kargs):
        '''
        Parse the contents of a list returning a sequence of matches.
        '''
        return self.get_parse_list_all()(list_, **kargs)
        
    def parse_string_all(self, string, **kargs):
        '''
        Parse the contents of a string, returning a sequence of matches.
        '''
        return self.get_parse_string_all()(string, **kargs)

    def parse_sequence_all(self, sequence, **kargs):
        '''
        Parse the contents of a generic sequence (with [] and len()) 
        returning a sequence of matches.
        '''
        return self.get_parse_sequence_all()(sequence, **kargs)

    def parse_all(self, input_, **kargs):
        '''
        Parse input, returning a sequence of 
        matches.  The type of stream is inferred from the input to the 
        parser.
        '''
        return self.get_parse_all()(input_, **kargs)
