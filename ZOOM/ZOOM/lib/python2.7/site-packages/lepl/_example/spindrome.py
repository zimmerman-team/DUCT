
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
A palindrome is a word that reads the same backwards as forwards.

Some letters look like letters when they are upside down, which suggests that
there should be something like a palindromes that work when a word is rotated
by 180 degress about its middle.  I will call these spindromes.

This seemed like an obvious use for Lepl, which will give multiple matches - 
all we need to do is
  1 - Identify which letters work
  2 - Write a parser that matches words consisting of such letters
  3 - Run that parser against a list of words
'''

from lepl import *


# What letters can we match?  I don't know how to generate this except by
# checking each letter by eye, which gives the following (I'll use either case
# in the hope of getting more matches):

pairs = [('b', 'q'), ('d', 'p'), ('h', 'y'), ('i', 'i'), ('l', 'l'), ('m', 'w'), 
         ('n', 'u'), ('o', 'o'), ('s', 's'), ('x', 'x'), ('z', 'z'),
         ('H', 'H'), ('I', 'I'), ('M', 'W')]

# Some of those are self-images so can occur in the middle of words with an
# odd number of letters

def single(pair):
    return pair[0] == pair[1]

singles = [pair[0] for pair in pairs if single(pair)] 

# We want to do caseless matching but return the correct case (so we can
# see when capitals are used).  So we need a matcher that does that.  Lepl
# doesn't have anything built-in, but we can write our own (following Lepl's
# convention of using capitals to indicate matcher factories).

@function_matcher_factory()
def Caseless(letter):
    '''
    Given a letter, this returns a matcher that will match the first character
    of a stream if the letter appears (ignoring case), returning the letter
    as the match.
    '''
    def matcher(support, stream):
        (char, next_stream) = s_next(stream)
        if char.lower() == letter.lower():
            return ([letter], next_stream)
    return matcher

# And then we can use that to match and of the central letters:

central = Or(*map(Caseless, singles))

# The final matcher is going to be recursive (matching repeated pairs "inside"
# itself).  That's going to be recursive; we handle that by introducing 
# the name so that we can reference it later.

outer = Delayed()

# To define a matcher for any pair we'll first write a function that can
# generate one for a single pair (note how this calls the pre-defined outer)

def Bracket(pair, inner):
    a, b = [Caseless(letter) for letter in pair]
    if single(pair):
        return a + inner + b
    else:
        return a + inner + b | b + inner + a 
    
def Outer(pair):
    return Bracket(pair, outer | Empty())

# Finally, we can "tie the knot" (we put the central matcher here so that
# we can match single letters)

outer += Or(*[Outer(pair) for pair in pairs]) | central

# Some simple tests:

assert outer.parse('o') == ['o']
assert outer.parse('O') == ['o']
assert outer.parse('pod') == ['pod']
assert outer.parse('pboQd') == ['pboqd']

# But that takes WAY too long.  Instead, we need to restrict backtracking by
# adjusting the matcher to the word length.  We'll make a matcher for a given
# length then cache/build matchers as necessary.

def CountedOuter(n):
    if n == 0:
        return Empty()
    elif n == 1:
        return central
    else:
        inner = CountedOuter(n-2)
        return Or(*[Bracket(pair, inner) for pair in pairs])

# And cache by length

cache = {}
def parse(word):
    n = len(word)
    if n not in cache:
        cache[n] = CountedOuter(n)
        # I tried compiling to a regular expression here (re lib), but it
        # doesn't work too well (hangs dues to exponential complexity on 
        # longer words)
    return cache[len(word)].parse_string(word)

assert parse('o') == ['o']
assert parse('O') == ['o']
assert parse('pod') == ['pod']
assert parse('pboQd') == ['pboqd']

# Now let's run that against the contents of the dictionary:
if __name__ == '__main__':
    with open('/usr/share/dict/words', encoding='latin_1') as words:
        for word in words:
            word = word.strip()
            try:
                print(parse(word)[0]) # will be a list containing a single word
            except:
                pass

'''
The results are less exciting than I had hoped:

dip
dollop
dop
dp
H
HoH
hoy
HunH
hy
i
issi
l
lil
ll
mow
msw
mw
niu
nu
o
oHo
oo
oxo
pd
pHd
pid
pod
pood
qb
s
sis
solos
sos
spods
ss
sss
suns
swims
un
usn
wm
x
z
ziz
zzz
'''
