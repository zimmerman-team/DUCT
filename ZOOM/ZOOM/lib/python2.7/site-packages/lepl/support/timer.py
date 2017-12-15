
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
Support for measuring the speed of different parsers and configurations.
'''

from time import time
from sys import stdout
from gc import collect

from lepl.support.lib import fmt


DEFAULT = 'default'


def print_timing(input, matchers, count=10, count_compile=None, best_of=3, 
                 parse_all=False, out=None, reference=None):
    '''
    Generate timing information for the given input and parsers.
    
    `input` can be a sequence or a function that generates sequences (this is
    useful if you need to subvert caching).  Note that a function is evaluated
    once before the timing starts.
    
    `matchers` is a dict that maps names to matchers.  The names are used in 
    the output.  Alternatively, a single matcher can be given (which will be 
    called "default").  A typical use might look like:
      matcher = ....
      time("...", {'default': matcher.clone().config.default().matcher,
                   'clear': matcher.clone().config.clear().matcher})
                   
    `count` is the number of parses to make when measuring a single time.  This
    is to make sure that the time taken is long enough to measure accurately
    (times less that 10ms or so will be imprecise).  The final time reported
    is adjusted to be for a single parse, no matter what the value of `count`.
    By default 10 matches are made.
    
    `count_compile` allows a different `count` value for timing when the
    compiler parser is not re-used.  By default this is the same as `count`.
    
    `best_of` repeats the test this many times and takes the shortest result.
    This corrects for any slow-down caused by other programs running. 
    
    `parse_all`, if True, evaluates all parses through backtracking (otherwise
    a single parse is made)
    
    `out` is the destination for the printing (stdout by default).
                   
    `reference` names the matcher against which others are compared.  By 
    default any matcher called "default" will be used; otherwise the first
    matcher when sorted alphabetically is used.
    '''
    try:
        input()
        source = input
    except TypeError:
        source = lambda: input
    if not isinstance(matchers, dict):
        matchers = {DEFAULT: matchers}
    if out is None:
        out = stdout
    if count_compile is None:
        count_compile = count
        
    # python 2 has no support for print(..., file=...)
    def prnt(msg='', end='\n'):
        out.write(msg + end)
        
    prnt('\n\nTiming Results (ms)')
    prnt('-------------------')
    prnt(fmt('\nCompiling:  best of {1:d} averages over {0:d} repetition(s)',
              count_compile, best_of))
    prnt(fmt('Parse only: best of {1:d} averages over {0:d} repetition(s)',
              count, best_of))
    prnt('\n             Matcher           Compiling | Parse only')
    prnt('-----------------------------------------+------------------')
    
    references = [None, None]
    names = sorted(matchers.keys())
    if not reference:
        if DEFAULT in names:
            reference = DEFAULT
        else:
            reference = names[0]
    assert reference in names, 'Reference must be in names'
    names = [reference] + [name for name in names if name != reference]
    
    for name in names:
        prnt(fmt('{0:>20s}  ', name), end='')
        matcher = matchers[name]
        for (compile, n, end, r) in ((True, count_compile, ' |', 0), 
                                     (False, count, '\n', 1)):
            times = []
            for i in range(best_of):
                collect()
                t = time()
                for j in range(n):
                    if compile:
                        matcher.config.clear_cache()
                    if parse_all:
                        list(matcher.parse_all(source()))
                    else:
                        matcher.parse(source())
                times.append(time() - t)
                
            times.sort()
            best = 1000 * times[0] / float(n)
            prnt(fmt('{0:7.2f}', best), end='')

            ref = references[r]
            if ref is None:
                references[r] = best
                prnt('           ', end=end)
            elif ref:
                ratio = best / ref
                prnt(fmt('  (x {0:5.1f})', ratio), end=end)
            else:
                prnt('  (x -----)', end=end)
                
    prnt()
    
