
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
Tests for the lepl.apps.rfc3696 module.
'''

from logging import basicConfig, DEBUG

from lepl import *
from lepl._test.base import BaseTest
from lepl.apps.rfc3696 import _PreferredFullyQualifiedDnsName, _EmailLocalPart,\
    _Email, _HttpUrl, MailToUrl, HttpUrl, Email, _IpV4Address, _Ipv6Address


class DnsNameTest(BaseTest):
    
    def test_dns_name_matcher(self):
        
        name = _PreferredFullyQualifiedDnsName() & Eos()
        
        self.assert_fail('', name)
        self.assert_fail('a', name)
        self.assert_fail('12.34', name)
        self.assert_fail('a.b.', name)
        self.assert_fail(' a.b', name)
        self.assert_fail('a.b ', name)
        self.assert_fail('a._.', name)
        self.assert_fail('a.-b.c', name)
        self.assert_fail('a.b-.c', name)
        self.assert_fail('a.b.c.123', name)
        
        self.assert_literal('a.b.123.c', name)
        self.assert_literal('a.b-c.d', name)
        self.assert_literal('a.b--c.d', name)
        self.assert_literal('acooke.org', name)
        self.assert_literal('EXAMPLE.COM', name)
        self.assert_literal('example.a23', name)
        self.assert_literal('example.12c', name)
        
        
class IpV4AddressTest(BaseTest):
    
    def test_ipv4_address(self):
        
        address = _IpV4Address() & Eos()
        
        self.assert_literal('1.2.3.4', address)
        self.assert_literal('255.255.255.255', address)
        self.assert_literal('0.0.0.0', address)
        
        self.assert_fail('1.2.3', address)
        self.assert_fail('1.2.3.', address)
        self.assert_fail('1.256.3.4', address)
        self.assert_fail('1.a.3.4', address)
        self.assert_fail('1.-1.3.4', address)
        
        
class IpV6AddressTest(BaseTest):
    
    def test_ipv6_address(self):
        
        address = _Ipv6Address() & Eos()
        
        self.assert_literal('FEDC:BA98:7654:3210:FEDC:BA98:7654:3210', address)
        self.assert_literal('1080:0:0:0:8:800:200C:417A', address)
        self.assert_literal('FF01:0:0:0:0:0:0:101', address)
        self.assert_literal('0:0:0:0:0:0:0:1', address)
        self.assert_literal('0:0:0:0:0:0:0:0', address)
        self.assert_literal('1080::8:800:200C:417A', address)
        self.assert_literal('FF01::101', address)
        self.assert_literal('::1', address)
        self.assert_literal('::', address)
        self.assert_literal('0:0:0:0:0:0:13.1.68.3', address)
        self.assert_literal('0:0:0:0:0:FFFF:129.144.52.38', address)
        self.assert_literal('::13.1.68.3', address)
        self.assert_literal('::FFFF:129.144.52.38', address)
        
        self.assert_fail('1:2:3:4:5:6:7', address)
        self.assert_fail('1:2:3:4:5:6:7:8:9', address)
        self.assert_fail('::1:2:3:4:5:6:7:8', address)
        self.assert_fail(':1::2:3:4:5:6:7:8', address)
        self.assert_fail(':1:2:3:4:5:6:7:8::', address)
        self.assert_fail('1:2:3:4:5:1.2.3.4', address)
        self.assert_fail('1:2:3:4:5.6.7:1.2.3.4', address)
        self.assert_fail('::1:2:3:4:5:6:1.2.3.4', address)
        self.assert_fail('1::2:3:4:5:6:1.2.3.4', address)
        self.assert_fail('1:2:3:4:5:6::1.2.3.4', address)


class _EmailLocalPartTest(BaseTest):
    
    def test_email_local_part_matcher(self):
        
        local = _EmailLocalPart() & Eos()
        
        self.assert_fail('', local)
        self.assert_fail('""', local)
        self.assert_fail('"unmatched', local)
        self.assert_fail('unmatched"', local)
        self.assert_fail(' ', local)
        self.assert_fail('a b', local)
        
        self.assert_literal(r'andrew', local)
        self.assert_literal(r'Abc\@def', local)
        self.assert_literal(r'Fred\ Bloggs', local)
        self.assert_literal(r'Joe.\\Blow', local)
        self.assert_literal(r'"Abc@def"', local)
        self.assert_literal(r'"Fred Bloggs"', local)
        self.assert_literal(r'user+mailbox', local)
        self.assert_literal(r'customer/department=shipping', local)
        self.assert_literal(r'$A12345', local)
        self.assert_literal(r'!def!xyz%abc', local)
        self.assert_literal(r'_somename', local)


class _EmailTest(BaseTest):
    
    def test_email_matcher(self):
        
        email = _Email() & Eos()
        
        self.assert_literal(r'andrew@acooke.org', email)
        self.assert_literal(r'Abc\@def@example.com', email)
        self.assert_literal(r'Fred\ Bloggs@example.com', email)
        self.assert_literal(r'Joe.\\Blow@example.com', email)
        self.assert_literal(r'"Abc@def"@example.com', email)
        self.assert_literal(r'"Fred Bloggs"@example.com', email)
        self.assert_literal(r'user+mailbox@example.com', email)
        self.assert_literal(r'customer/department=shipping@example.com', email)
        self.assert_literal(r'$A12345@example.com', email)
        self.assert_literal(r'!def!xyz%abc@example.com', email)
        self.assert_literal(r'_somename@example.com', email)
                
    def test_email(self):
        
        email = Email()
        
        assert email(r'andrew@acooke.org',)
        assert email(r'Abc\@def@example.com',)
        assert email(r'Fred\ Bloggs@example.com',)
        assert email(r'Joe.\\Blow@example.com',)
        assert email(r'"Abc@def"@example.com',)
        assert email(r'"Fred Bloggs"@example.com',)
        assert email(r'user+mailbox@example.com',)
        assert email(r'customer/department=shipping@example.com',)
        assert email(r'$A12345@example.com',)
        assert email(r'!def!xyz%abc@example.com',)
        assert email(r'_somename@example.com',)
        
        addresses = ['', 'a', '12.34', 'a.b.', ' a.b', 'a.b ', 'a._.', 
                     'a.-b.c', 'a.b-.c', 'a.b.c.123']
        names = ['', '""', '"unmatched', 'unmatched"', ' ', 'a b']
        for name in names:
            for address in addresses:
                bad = name + '@' + address
                assert not email(bad), bad
                

class HttpUrlTest(BaseTest):
    
    def test_http_matcher(self):
        #basicConfig(level=DEBUG)
        
        http = _HttpUrl() & Eos()
        http.config.compile_to_re()
        #print(http.get_parse().matcher.tree())
        
        self.assert_literal(r'http://www.acooke.org', http)
        self.assert_literal(r'http://www.acooke.org/', http)
        self.assert_literal(r'http://www.acooke.org:80', http)
        self.assert_literal(r'http://www.acooke.org:80/', http)
        self.assert_literal(r'http://www.acooke.org/andrew', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew', http)
        self.assert_literal(r'http://www.acooke.org/andrew/', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/', http)
        self.assert_literal(r'http://www.acooke.org/?foo', http)
        self.assert_literal(r'http://www.acooke.org:80/?foo', http)
        self.assert_literal(r'http://www.acooke.org/#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew?foo', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew?foo', http)
        self.assert_literal(r'http://www.acooke.org/andrew/?foo', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/?foo', http)
        self.assert_literal(r'http://www.acooke.org/andrew#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew/#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew?foo#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew?foo#bar', http)
        self.assert_literal(r'http://www.acooke.org/andrew/?foo#bar', http)
        self.assert_literal(r'http://www.acooke.org:80/andrew/?foo#bar', http)
        
        self.assert_fail(r'http://www.acooke.org:80/andrew/?foo#bar ', http)
        self.assert_fail(r'http://www.acooke.org:80/andrew/?foo#bar baz', http)
        
    def test_http(self):
        
        httpUrl = HttpUrl()
        
        assert httpUrl(r'http://www.acooke.org')
        assert httpUrl(r'http://www.acooke.org/')
        assert httpUrl(r'http://www.acooke.org:80')
        assert httpUrl(r'http://www.acooke.org:80/')
        assert httpUrl(r'http://www.acooke.org/andrew')
        assert httpUrl(r'http://www.acooke.org:80/andrew')
        assert httpUrl(r'http://www.acooke.org/andrew/')
        assert httpUrl(r'http://www.acooke.org:80/andrew/')
        assert httpUrl(r'http://www.acooke.org/?foo')
        assert httpUrl(r'http://www.acooke.org:80/?foo')
        assert httpUrl(r'http://www.acooke.org/#bar')
        assert httpUrl(r'http://www.acooke.org:80/#bar')
        assert httpUrl(r'http://www.acooke.org/andrew?foo')
        assert httpUrl(r'http://www.acooke.org:80/andrew?foo')
        assert httpUrl(r'http://www.acooke.org/andrew/?foo')
        assert httpUrl(r'http://www.acooke.org:80/andrew/?foo')
        assert httpUrl(r'http://www.acooke.org/andrew#bar')
        assert httpUrl(r'http://www.acooke.org:80/andrew#bar')
        assert httpUrl(r'http://www.acooke.org/andrew/#bar')
        assert httpUrl(r'http://www.acooke.org:80/andrew/#bar')
        assert httpUrl(r'http://www.acooke.org/andrew?foo#bar')
        assert httpUrl(r'http://www.acooke.org:80/andrew?foo#bar')
        assert httpUrl(r'http://www.acooke.org/andrew/?foo#bar')
        assert httpUrl(r'http://www.acooke.org:80/andrew/?foo#bar')
        assert httpUrl(r'http://1.2.3.4:80/andrew/?foo#bar')
        assert httpUrl(r'http://[1:2:3:4:5:6:7:8]:80/andrew/?foo#bar')
        
        # http://base.google.com/support/bin/answer.py?hl=en&answer=25230
        assert not httpUrl(r'http://www.example.com/space here.html')
        assert not httpUrl(r'http://www.example.com\main.html')
        assert not httpUrl(r'/main.html')
        assert not httpUrl(r'www.example.com/main.html')
        assert not httpUrl(r'http:www.example.com/main.html')


class MailToUrlTest(BaseTest):
    
    def test_mail_to_url(self):
        
        mailToUrl = MailToUrl()
        
        assert mailToUrl('mailto:joe@example.com')
        assert mailToUrl('mailto:user%2Bmailbox@example.com')
        assert mailToUrl('mailto:customer%2Fdepartment=shipping@example.com')
        assert mailToUrl('mailto:$A12345@example.com')
        assert mailToUrl('mailto:!def!xyz%25abc@example.com')
        assert mailToUrl('mailto:_somename@example.com')
