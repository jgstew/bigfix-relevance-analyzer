"""Inspector tables, generated from the dumps. Do not edit by hand.

Regenerate with ``python tools/generate_inspector_data.py``;
``tests/test_inspector_data.py`` fails if this file and the dumps in
``tests/examples/relevance_inspectors/`` disagree.

Each table is one row per line, ``<source mask in hex>\t<dump line>``.
The mask indexes :data:`SOURCES`, recording which dumps defined the row --
a row present in every client platform and no session surface is client-only
vocabulary, and one present in both dialects is shared.
"""

from __future__ import annotations

SOURCES: tuple[str, ...] = (
    "client:debian",
    "client:macos",
    "client:rhel",
    "client:ubuntu",
    "client:windows",
    "session:console",
    "session:rest_api",
    "session:web_reports",
)

# 526 rows
BINARY_OPERATORS: str = """\
40	<bes action set> * <bes action set>: bes action set
40	<bes action set> + <bes action set>: bes action set
40	<bes action set> - <bes action set>: bes action set
40	<bes action set> = <bes action set>: boolean
40	<bes action set> contains <bes action set>: boolean
40	<bes action set> contains <bes action>: boolean
40	<bes action status> = <bes action status>: boolean
40	<bes action> = <bes action>: boolean
40	<bes computer group set> * <bes computer group set>: bes computer group set
40	<bes computer group set> + <bes computer group set>: bes computer group set
40	<bes computer group set> - <bes computer group set>: bes computer group set
40	<bes computer group set> = <bes computer group set>: boolean
40	<bes computer group set> contains <bes computer group set>: boolean
40	<bes computer group set> contains <bes computer group>: boolean
40	<bes computer group> = <bes computer group>: boolean
40	<bes computer set> * <bes computer set>: bes computer set
40	<bes computer set> + <bes computer set>: bes computer set
40	<bes computer set> - <bes computer set>: bes computer set
40	<bes computer set> = <bes computer set>: boolean
40	<bes computer set> contains <bes computer set>: boolean
40	<bes computer set> contains <bes computer>: boolean
40	<bes computer> = <bes computer>: boolean
40	<bes domain set> * <bes domain set>: bes domain set
40	<bes domain set> + <bes domain set>: bes domain set
40	<bes domain set> - <bes domain set>: bes domain set
40	<bes domain set> = <bes domain set>: boolean
40	<bes domain set> contains <bes domain set>: boolean
40	<bes domain set> contains <bes domain>: boolean
40	<bes domain> = <bes domain>: boolean
40	<bes filter set> * <bes filter set>: bes filter set
40	<bes filter set> + <bes filter set>: bes filter set
40	<bes filter set> - <bes filter set>: bes filter set
40	<bes filter set> = <bes filter set>: boolean
40	<bes filter set> contains <bes filter set>: boolean
40	<bes filter set> contains <bes filter>: boolean
40	<bes filter> = <bes filter>: boolean
40	<bes fixlet set> * <bes fixlet set>: bes fixlet set
40	<bes fixlet set> + <bes fixlet set>: bes fixlet set
40	<bes fixlet set> - <bes fixlet set>: bes fixlet set
40	<bes fixlet set> = <bes fixlet set>: boolean
40	<bes fixlet set> contains <bes fixlet set>: boolean
40	<bes fixlet set> contains <bes fixlet>: boolean
40	<bes fixlet> = <bes fixlet>: boolean
40	<bes idp directory set> * <bes idp directory set>: bes idp directory set
40	<bes idp directory set> + <bes idp directory set>: bes idp directory set
40	<bes idp directory set> - <bes idp directory set>: bes idp directory set
40	<bes idp directory set> = <bes idp directory set>: boolean
40	<bes idp directory set> contains <bes idp directory set>: boolean
40	<bes idp directory set> contains <bes idp directory>: boolean
40	<bes idp directory> = <bes idp directory>: boolean
40	<bes ldap directory set> * <bes ldap directory set>: bes ldap directory set
40	<bes ldap directory set> + <bes ldap directory set>: bes ldap directory set
40	<bes ldap directory set> - <bes ldap directory set>: bes ldap directory set
40	<bes ldap directory set> = <bes ldap directory set>: boolean
40	<bes ldap directory set> contains <bes ldap directory set>: boolean
40	<bes ldap directory set> contains <bes ldap directory>: boolean
40	<bes ldap directory> = <bes ldap directory>: boolean
40	<bes peer download> < <bes peer download>: boolean
40	<bes peer download> = <bes peer download>: boolean
40	<bes property set> * <bes property set>: bes property set
40	<bes property set> + <bes property set>: bes property set
40	<bes property set> - <bes property set>: bes property set
40	<bes property set> = <bes property set>: boolean
40	<bes property set> contains <bes property set>: boolean
40	<bes property set> contains <bes property>: boolean
40	<bes property> = <bes property>: boolean
40	<bes role set> * <bes role set>: bes role set
40	<bes role set> + <bes role set>: bes role set
40	<bes role set> - <bes role set>: bes role set
40	<bes role set> = <bes role set>: boolean
40	<bes role set> contains <bes role set>: boolean
40	<bes role set> contains <bes role>: boolean
40	<bes role> = <bes role>: boolean
40	<bes site file set> * <bes site file set>: bes site file set
40	<bes site file set> + <bes site file set>: bes site file set
40	<bes site file set> - <bes site file set>: bes site file set
40	<bes site file set> = <bes site file set>: boolean
40	<bes site file set> contains <bes site file set>: boolean
40	<bes site file set> contains <bes site file>: boolean
40	<bes site file> = <bes site file>: boolean
40	<bes site set> * <bes site set>: bes site set
40	<bes site set> + <bes site set>: bes site set
40	<bes site set> - <bes site set>: bes site set
40	<bes site set> = <bes site set>: boolean
40	<bes site set> contains <bes site set>: boolean
40	<bes site set> contains <bes site>: boolean
40	<bes site> = <bes site>: boolean
40	<bes unmanagedasset set> * <bes unmanagedasset set>: bes unmanagedasset set
40	<bes unmanagedasset set> + <bes unmanagedasset set>: bes unmanagedasset set
40	<bes unmanagedasset set> - <bes unmanagedasset set>: bes unmanagedasset set
40	<bes unmanagedasset set> = <bes unmanagedasset set>: boolean
40	<bes unmanagedasset set> contains <bes unmanagedasset set>: boolean
40	<bes unmanagedasset set> contains <bes unmanagedasset>: boolean
40	<bes unmanagedasset> = <bes unmanagedasset>: boolean
40	<bes user set> * <bes user set>: bes user set
40	<bes user set> + <bes user set>: bes user set
40	<bes user set> - <bes user set>: bes user set
40	<bes user set> = <bes user set>: boolean
40	<bes user set> contains <bes user set>: boolean
40	<bes user set> contains <bes user>: boolean
40	<bes user> = <bes user>: boolean
40	<bes webui app set> * <bes webui app set>: bes webui app set
40	<bes webui app set> + <bes webui app set>: bes webui app set
40	<bes webui app set> - <bes webui app set>: bes webui app set
40	<bes webui app set> = <bes webui app set>: boolean
40	<bes webui app set> contains <bes webui app set>: boolean
40	<bes webui app set> contains <bes webui app>: boolean
40	<bes webui app> = <bes webui app>: boolean
40	<bes wizard set> * <bes wizard set>: bes wizard set
40	<bes wizard set> + <bes wizard set>: bes wizard set
40	<bes wizard set> - <bes wizard set>: bes wizard set
40	<bes wizard set> = <bes wizard set>: boolean
40	<bes wizard set> contains <bes wizard set>: boolean
40	<bes wizard set> contains <bes wizard>: boolean
40	<bes wizard> = <bes wizard>: boolean
52	<binary_string> & <binary_string>: binary_string
52	<binary_string> < <binary_string>: boolean
52	<binary_string> <= <binary_string>: boolean
52	<binary_string> = <binary_string>: boolean
52	<binary_string> contains <binary_string>: boolean
52	<binary_string> ends with <binary_string>: boolean
52	<binary_string> starts with <binary_string>: boolean
52	<bit set> * <bit set>: bit set
52	<bit set> + <bit set>: bit set
52	<bit set> - <bit set>: bit set
52	<bit set> = <bit set>: boolean
52	<bit set> contains <bit set>: boolean
52	<boolean> * <time range>: timed( time range, boolean )
52	<boolean> = <boolean>: boolean
12	<cidr subnet> = <cidr subnet>: boolean
12	<cidr subnet> = <string>: boolean
12	<cidr subnet> contains <cidr subnet>: boolean
12	<cidr subnet> contains <ipv4 address>: boolean
12	<cidr subnet> contains <ipv4or6 address>: boolean
12	<cidr subnet> contains <ipv6 address>: boolean
10	<connection status> = <connection status>: boolean
2	<country> = <country>: boolean
52	<date> & <time of day with time zone>: time
52	<date> + <number of months>: date
52	<date> + <time interval>: date
52	<date> - <date>: time interval
52	<date> - <number of months>: date
52	<date> - <time interval>: date
52	<date> < <date>: boolean
52	<date> <= <date>: boolean
52	<date> = <date>: boolean
52	<day of month> & <month and year>: date
52	<day of month> & <month>: day of year
52	<day of month> + <time interval>: day of month
52	<day of month> - <day of month>: time interval
52	<day of month> - <time interval>: day of month
52	<day of month> < <day of month>: boolean
52	<day of month> <= <day of month>: boolean
52	<day of month> = <day of month>: boolean
52	<day of week> + <time interval>: day of week
52	<day of week> - <day of week>: time interval
52	<day of week> - <time interval>: day of week
52	<day of week> = <day of week>: boolean
52	<day of year> & <month and year>: date
52	<day of year> & <year>: date
52	<day of year> + <number of months>: day of year
52	<day of year> + <time interval>: day of year
52	<day of year> - <day of year>: time interval
52	<day of year> - <number of months>: day of year
52	<day of year> - <time interval>: day of year
52	<day of year> < <day of year>: boolean
52	<day of year> <= <day of year>: boolean
52	<day of year> = <day of year>: boolean
10	<event log event type> = <event log event type>: boolean
12	<file content> contains <string>: boolean
2	<file signature> = <file signature>: boolean
2	<file type> = <file type>: boolean
12	<firewall action> = <firewall action>: boolean
10	<firewall local policy modify state> = <firewall local policy modify state>: boolean
10	<firewall profile type> = <firewall profile type>: boolean
10	<firewall scope> = <firewall scope>: boolean
10	<firewall service type> = <firewall service type>: boolean
52	<floating point> * <floating point>: floating point
52	<floating point> * <integer>: floating point
42	<floating point> * <rate>: rate
52	<floating point> + <floating point>: floating point
52	<floating point> + <integer>: floating point
52	<floating point> - <floating point>: floating point
52	<floating point> - <integer>: floating point
52	<floating point> / <floating point>: floating point
52	<floating point> / <integer>: floating point
42	<floating point> / <time interval>: rate
52	<floating point> < <floating point>: boolean
52	<floating point> < <integer>: boolean
52	<floating point> <= <floating point>: boolean
52	<floating point> <= <integer>: boolean
52	<floating point> = <floating point>: boolean
52	<floating point> = <integer>: boolean
52	<format> + <date>: format
52	<format> + <day of week>: format
52	<format> + <format>: format
52	<format> + <integer>: format
52	<format> + <string>: format
52	<format> + <time interval>: format
52	<format> + <time of day>: format
52	<format> + <time>: format
50	<hertz> % <hertz>: hertz
2	<hertz> %25 <hertz>: hertz
52	<hertz> * <integer>: hertz
52	<hertz> + <hertz>: hertz
52	<hertz> - <hertz>: hertz
52	<hertz> / <hertz>: integer
52	<hertz> / <integer>: hertz
52	<hertz> < <hertz>: boolean
52	<hertz> <= <hertz>: boolean
52	<hertz> = <hertz>: boolean
52	<html> & <html>: html
52	<html> & <string>: html
52	<integer set> * <integer set>: integer set
52	<integer set> + <integer set>: integer set
52	<integer set> - <integer set>: integer set
52	<integer set> = <integer set>: boolean
52	<integer set> contains <integer set>: boolean
52	<integer set> contains <integer>: boolean
50	<integer> % <integer>: integer
50	<integer> % <large integer>: large integer
50	<integer> % <uinteger>: uinteger
2	<integer> %25 <integer>: integer
2	<integer> %25 <large integer>: large integer
2	<integer> %25 <uinteger>: uinteger
52	<integer> * <floating point>: floating point
52	<integer> * <hertz>: hertz
52	<integer> * <integer>: integer
52	<integer> * <large integer>: large integer
52	<integer> * <number of months>: number of months
52	<integer> * <time interval>: time interval
52	<integer> * <time range>: timed( time range, integer )
52	<integer> * <uinteger>: uinteger
52	<integer> + <floating point>: floating point
52	<integer> + <integer>: integer
52	<integer> + <large integer>: large integer
52	<integer> + <uinteger>: uinteger
52	<integer> - <floating point>: floating point
52	<integer> - <integer>: integer
52	<integer> - <large integer>: large integer
52	<integer> - <uinteger>: uinteger
52	<integer> / <floating point>: floating point
52	<integer> / <integer>: integer
52	<integer> / <large integer>: large integer
52	<integer> / <uinteger>: uinteger
52	<integer> < <floating point>: boolean
52	<integer> < <integer>: boolean
52	<integer> < <large integer>: boolean
10	<integer> < <registry key value type>: boolean
10	<integer> < <registry key value>: boolean
52	<integer> < <uinteger>: boolean
52	<integer> <= <floating point>: boolean
52	<integer> <= <integer>: boolean
52	<integer> <= <large integer>: boolean
10	<integer> <= <registry key value type>: boolean
10	<integer> <= <registry key value>: boolean
52	<integer> <= <uinteger>: boolean
52	<integer> = <floating point>: boolean
52	<integer> = <integer>: boolean
52	<integer> = <large integer>: boolean
10	<integer> = <registry key value type>: boolean
10	<integer> = <registry key value>: boolean
52	<integer> = <uinteger>: boolean
10	<internet protocol> = <internet protocol>: boolean
52	<ip version> = <ip version>: boolean
52	<ipv4 address> < <ipv4 address>: boolean
52	<ipv4 address> < <string>: boolean
52	<ipv4 address> <= <ipv4 address>: boolean
52	<ipv4 address> <= <string>: boolean
52	<ipv4 address> = <ipv4 address>: boolean
52	<ipv4 address> = <string>: boolean
52	<ipv4or6 address> < <ipv4or6 address>: boolean
52	<ipv4or6 address> < <string>: boolean
52	<ipv4or6 address> <= <ipv4or6 address>: boolean
52	<ipv4or6 address> <= <string>: boolean
52	<ipv4or6 address> = <ipv4or6 address>: boolean
52	<ipv4or6 address> = <string>: boolean
52	<ipv6 address> < <ipv6 address>: boolean
52	<ipv6 address> <= <ipv6 address>: boolean
52	<ipv6 address> = <ipv6 address>: boolean
52	<json key> = <json key>: boolean
52	<json value> = <json value>: boolean
50	<large integer> % <integer>: large integer
50	<large integer> % <large integer>: large integer
2	<large integer> %25 <integer>: large integer
2	<large integer> %25 <large integer>: large integer
52	<large integer> * <integer>: large integer
52	<large integer> * <large integer>: large integer
52	<large integer> + <integer>: large integer
52	<large integer> + <large integer>: large integer
52	<large integer> - <integer>: large integer
52	<large integer> - <large integer>: large integer
52	<large integer> / <integer>: large integer
52	<large integer> / <large integer>: large integer
52	<large integer> < <integer>: boolean
52	<large integer> < <large integer>: boolean
52	<large integer> <= <integer>: boolean
52	<large integer> <= <large integer>: boolean
52	<large integer> = <integer>: boolean
52	<large integer> = <large integer>: boolean
10	<media type> = <media type>: boolean
10	<metabase identifier> = <metabase identifier>: boolean
10	<metabase type> = <metabase type>: boolean
10	<metabase user type> = <metabase user type>: boolean
52	<month and year> & <day of month>: date
52	<month and year> & <day of year>: date
52	<month and year> + <number of months>: month and year
52	<month and year> - <month and year>: number of months
52	<month and year> - <number of months>: month and year
52	<month and year> < <month and year>: boolean
52	<month and year> <= <month and year>: boolean
52	<month and year> = <month and year>: boolean
52	<month> & <day of month>: day of year
52	<month> & <year>: month and year
52	<month> + <number of months>: month
52	<month> - <month>: number of months
52	<month> - <number of months>: month
52	<month> < <month>: boolean
52	<month> <= <month>: boolean
52	<month> = <month>: boolean
50	<number of months> % <number of months>: number of months
2	<number of months> %25 <number of months>: number of months
52	<number of months> * <integer>: number of months
52	<number of months> + <date>: date
52	<number of months> + <day of year>: day of year
52	<number of months> + <month and year>: month and year
52	<number of months> + <month>: month
52	<number of months> + <number of months>: number of months
52	<number of months> + <year>: year
52	<number of months> - <number of months>: number of months
52	<number of months> / <integer>: number of months
52	<number of months> / <number of months>: integer
52	<number of months> < <number of months>: boolean
52	<number of months> <= <number of months>: boolean
52	<number of months> = <number of months>: boolean
10	<operating system product type> = <operating system product type>: boolean
10	<plugin store key> = <plugin store key>: boolean
10	<plugin store> = <plugin store>: boolean
12	<power state> = <power state>: boolean
10	<priority class> = <priority class>: boolean
42	<rate> * <floating point>: rate
42	<rate> * <time interval>: floating point
42	<rate> + <rate>: rate
42	<rate> - <rate>: rate
42	<rate> / <floating point>: rate
42	<rate> < <rate>: boolean
42	<rate> <= <rate>: boolean
42	<rate> = <rate>: boolean
10	<registry key value type> < <integer>: boolean
10	<registry key value type> < <registry key value type>: boolean
10	<registry key value type> < <string>: boolean
10	<registry key value type> <= <integer>: boolean
10	<registry key value type> <= <registry key value type>: boolean
10	<registry key value type> <= <string>: boolean
10	<registry key value type> = <integer>: boolean
10	<registry key value type> = <registry key value type>: boolean
10	<registry key value type> = <string>: boolean
10	<registry key value> < <integer>: boolean
10	<registry key value> < <registry key value>: boolean
10	<registry key value> < <string>: boolean
10	<registry key value> <= <integer>: boolean
10	<registry key value> <= <registry key value>: boolean
10	<registry key value> <= <string>: boolean
10	<registry key value> = <integer>: boolean
10	<registry key value> = <registry key value>: boolean
10	<registry key value> = <string>: boolean
52	<regular expression> = <string>: boolean
52	<rope> & <rope>: rope
52	<rope> & <string>: rope
52	<rope> contains <string>: boolean
12	<security identifier> = <security identifier>: boolean
52	<site version list> < <site version list>: boolean
52	<site version list> <= <site version list>: boolean
52	<site version list> = <site version list>: boolean
52	<site version list> contains <site version list>: boolean
2	<stage> = <stage>: boolean
52	<string set> * <string set>: string set
52	<string set> + <string set>: string set
52	<string set> - <string set>: string set
52	<string set> = <string set>: boolean
52	<string set> contains <string set>: boolean
52	<string set> contains <string>: boolean
52	<string> & <html>: html
52	<string> & <rope>: rope
52	<string> & <string>: string
52	<string> < <ipv4 address>: boolean
52	<string> < <ipv4or6 address>: boolean
10	<string> < <registry key value type>: boolean
10	<string> < <registry key value>: boolean
52	<string> < <string>: boolean
40	<string> < <strverscmp version>: boolean
12	<string> < <uuid>: boolean
52	<string> < <version>: boolean
52	<string> <= <ipv4 address>: boolean
52	<string> <= <ipv4or6 address>: boolean
10	<string> <= <registry key value type>: boolean
10	<string> <= <registry key value>: boolean
52	<string> <= <string>: boolean
40	<string> <= <strverscmp version>: boolean
12	<string> <= <uuid>: boolean
52	<string> <= <version>: boolean
12	<string> = <cidr subnet>: boolean
52	<string> = <ipv4 address>: boolean
52	<string> = <ipv4or6 address>: boolean
10	<string> = <registry key value type>: boolean
10	<string> = <registry key value>: boolean
52	<string> = <regular expression>: boolean
52	<string> = <string>: boolean
40	<string> = <strverscmp version>: boolean
12	<string> = <uuid>: boolean
52	<string> = <version>: boolean
52	<string> contains <regular expression>: boolean
52	<string> contains <string>: boolean
52	<string> ends with <regular expression>: boolean
52	<string> ends with <string>: boolean
52	<string> starts with <regular expression>: boolean
52	<string> starts with <string>: boolean
40	<strverscmp version> < <string>: boolean
40	<strverscmp version> < <strverscmp version>: boolean
40	<strverscmp version> <= <string>: boolean
40	<strverscmp version> <= <strverscmp version>: boolean
40	<strverscmp version> = <string>: boolean
40	<strverscmp version> = <strverscmp version>: boolean
10	<task action type> = <task action type>: boolean
10	<task trigger type> = <task trigger type>: boolean
50	<time interval> % <time interval>: time interval
2	<time interval> %25 <time interval>: time interval
52	<time interval> & <time>: time range
52	<time interval> * <integer>: time interval
42	<time interval> * <rate>: floating point
52	<time interval> + <date>: date
52	<time interval> + <day of month>: day of month
52	<time interval> + <day of week>: day of week
52	<time interval> + <day of year>: day of year
52	<time interval> + <time interval>: time interval
52	<time interval> + <time of day with time zone>: time of day with time zone
52	<time interval> + <time of day>: time of day
52	<time interval> + <time zone>: time zone
52	<time interval> + <time>: time
52	<time interval> - <time interval>: time interval
52	<time interval> / <integer>: time interval
52	<time interval> / <time interval>: integer
52	<time interval> < <time interval>: boolean
52	<time interval> <= <time interval>: boolean
52	<time interval> = <time interval>: boolean
52	<time of day with time zone> & <date>: time
52	<time of day with time zone> & <time zone>: time of day with time zone
52	<time of day with time zone> + <time interval>: time of day with time zone
52	<time of day with time zone> - <time interval>: time of day with time zone
52	<time of day with time zone> - <time of day with time zone>: time interval
52	<time of day with time zone> < <time of day with time zone>: boolean
52	<time of day with time zone> <= <time of day with time zone>: boolean
52	<time of day with time zone> = <time of day with time zone>: boolean
52	<time of day> & <time zone>: time of day with time zone
52	<time of day> + <time interval>: time of day
52	<time of day> - <time interval>: time of day
52	<time of day> - <time of day>: time interval
52	<time of day> < <time of day>: boolean
52	<time of day> <= <time of day>: boolean
52	<time of day> = <time of day>: boolean
52	<time range> & <time range>: time range
52	<time range> & <time>: time range
52	<time range> * <boolean>: timed( time range, boolean )
52	<time range> * <integer>: timed( time range, integer )
52	<time range> * <time range>: time range
52	<time range> + <time range>: time range
52	<time range> = <time range>: boolean
52	<time range> contains <time range>: boolean
52	<time range> contains <time>: boolean
52	<time zone> & <time of day with time zone>: time of day with time zone
52	<time zone> & <time of day>: time of day with time zone
52	<time zone> + <time interval>: time zone
52	<time zone> - <time interval>: time zone
52	<time zone> - <time zone>: time interval
52	<time zone> = <time zone>: boolean
52	<time> & <time interval>: time range
52	<time> & <time range>: time range
52	<time> & <time>: time range
52	<time> + <time interval>: time
52	<time> - <time interval>: time
52	<time> - <time>: time interval
52	<time> < <time>: boolean
52	<time> <= <time>: boolean
52	<time> = <time>: boolean
52	<type> = <type>: boolean
50	<uinteger> % <integer>: uinteger
50	<uinteger> % <uinteger>: uinteger
2	<uinteger> %25 <integer>: uinteger
2	<uinteger> %25 <uinteger>: uinteger
52	<uinteger> * <integer>: uinteger
52	<uinteger> * <uinteger>: uinteger
52	<uinteger> + <integer>: uinteger
52	<uinteger> + <uinteger>: uinteger
52	<uinteger> - <integer>: uinteger
52	<uinteger> - <uinteger>: uinteger
52	<uinteger> / <integer>: uinteger
52	<uinteger> / <uinteger>: uinteger
52	<uinteger> < <integer>: boolean
52	<uinteger> < <uinteger>: boolean
52	<uinteger> <= <integer>: boolean
52	<uinteger> <= <uinteger>: boolean
52	<uinteger> = <integer>: boolean
52	<uinteger> = <uinteger>: boolean
12	<uuid> < <string>: boolean
12	<uuid> < <uuid>: boolean
12	<uuid> <= <string>: boolean
12	<uuid> <= <uuid>: boolean
12	<uuid> = <string>: boolean
12	<uuid> = <uuid>: boolean
52	<version> < <string>: boolean
52	<version> < <version>: boolean
52	<version> <= <string>: boolean
52	<version> <= <version>: boolean
52	<version> = <string>: boolean
52	<version> = <version>: boolean
2	<volume> = <volume>: boolean
2	<yaml key> = <yaml key>: boolean
2	<yaml value> = <yaml value>: boolean
52	<year> & <day of year>: date
52	<year> & <month>: month and year
52	<year> + <number of months>: year
52	<year> - <number of months>: year
52	<year> - <year>: number of months
52	<year> < <year>: boolean
52	<year> <= <year>: boolean
52	<year> = <year>: boolean
"""

# 265 rows
CASTS: str = """\
12	<action lock state> as string: string
12	<action> as string: string
12	<agent interface capability> as string: string
2	<application> as string: string
40	<bes action set> as xml string: string
40	<bes action set> as xml: utf8 string
40	<bes action status> as string: string
40	<bes action> as xml string: string
40	<bes action> as xml: utf8 string
40	<bes computer group set> as xml string: string
40	<bes computer group set> as xml: utf8 string
40	<bes computer group> as xml string: string
40	<bes computer group> as xml: utf8 string
40	<bes fixlet field value> as date: date
40	<bes fixlet field value> as integer: integer
40	<bes fixlet field value> as string: string
40	<bes fixlet field value> as time: time
40	<bes fixlet set> as xml string: string
40	<bes fixlet set> as xml: utf8 string
40	<bes fixlet> as xml string: string
40	<bes fixlet> as xml: utf8 string
40	<bes property set> as xml string: string
40	<bes property set> as xml: utf8 string
40	<bes property> as xml string: string
40	<bes property> as xml: utf8 string
52	<binary operator> as string: string
52	<binary_string> as fxf string: string
52	<binary_string> as hexadecimal: string
52	<binary_string> as local string: string
52	<binary_string> as string: string
52	<binary_string> as utf16 string: string
52	<binary_string> as utf8 string: string
52	<binary_substring> as binary_substring: binary_substring
52	<binary_substring> as string: string
12	<bios> as string: string
52	<bit set> as integer: integer
52	<bit set> as string: string
52	<boolean> as boolean: boolean
52	<boolean> as string: string
52	<cast> as string: string
12	<cidr subnet> as string: string
2	<client process owner> as string: string
52	<date> as string: string
52	<day of month> as integer: integer
52	<day of month> as string: string
52	<day of month> as two digits: string
52	<day of week> as string: string
52	<day of week> as three letters: string
52	<day of year> as string: string
10	<discretionary access control list> as string: string
2	<dummy type> as string: string
12	<environment variable> as string: string
12	<file content> as lowercase: file content
12	<file content> as uppercase: file content
12	<file> as string: string
2	<filesystem object> as file: file
2	<filesystem object> as folder: folder
12	<filesystem object> as string: string
10	<firewall profile type> as string: string
52	<floating point> as floating point: floating point
52	<floating point> as integer: integer
52	<floating point> as scientific notation: string
52	<floating point> as standard notation: string
52	<floating point> as string: string
52	<format> as string: string
52	<hertz> as string: string
52	<html> as decoded string: string
52	<html> as html: html
52	<html> as string: string
52	<integer> as bit set: bit set
52	<integer> as bits: bit set
52	<integer> as day_of_month: day of month
52	<integer> as floating point: floating point
52	<integer> as hexadecimal: string
52	<integer> as integer: integer
52	<integer> as large integer: large integer
52	<integer> as month: month
52	<integer> as string: string
52	<integer> as uinteger: uinteger
52	<integer> as year: year
52	<ip version> as string: string
52	<ipv4 address> as ipv4or6 address: ipv4or6 address
52	<ipv4 address> as ipv6 address: ipv6 address
52	<ipv4 address> as string: string
52	<ipv4or6 address> as compressed string with ipv4 with zone index: string
52	<ipv4or6 address> as compressed string with ipv4: string
52	<ipv4or6 address> as compressed string with zone index: string
52	<ipv4or6 address> as compressed string: string
52	<ipv4or6 address> as string with ipv4 with zone index: string
52	<ipv4or6 address> as string with ipv4: string
52	<ipv4or6 address> as string with leading zeros with zone index: string
52	<ipv4or6 address> as string with leading zeros: string
52	<ipv4or6 address> as string with zone index: string
52	<ipv4or6 address> as string: string
52	<ipv6 address> as compressed string with ipv4 with zone index: string
52	<ipv6 address> as compressed string with ipv4: string
52	<ipv6 address> as compressed string with zone index: string
52	<ipv6 address> as compressed string: string
52	<ipv6 address> as ipv4or6 address: ipv4or6 address
52	<ipv6 address> as string with ipv4 with zone index: string
52	<ipv6 address> as string with ipv4: string
52	<ipv6 address> as string with leading zeros with zone index: string
52	<ipv6 address> as string with leading zeros: string
52	<ipv6 address> as string with zone index: string
52	<ipv6 address> as string: string
52	<json key> as string: string
52	<json value> as boolean: boolean
52	<json value> as float: floating point
52	<json value> as integer: integer
52	<json value> as string: string
10	<language> as string: string
52	<large integer> as hexadecimal: string
52	<large integer> as integer: integer
52	<large integer> as large integer: large integer
52	<large integer> as string: string
52	<large integer> as uinteger: uinteger
10	<local group member> as string: string
12	<manual group> as string: string
10	<metabase identifier> as integer: integer
10	<metabase identifier> as string: string
10	<metabase type> as integer: integer
10	<metabase type> as string: string
10	<metabase user type> as integer: integer
10	<metabase user type> as string: string
10	<metabase value> as integer: integer
10	<metabase value> as string: string
52	<month and year> as string: string
52	<month> as integer: integer
52	<month> as string: string
52	<month> as three letters: string
52	<month> as two digits: string
52	<number of months> as string: string
12	<operating system> as string: string
10	<plugin store key> as string: string
10	<plugin store> as string: string
12	<power level> as string: string
12	<power state> as string: string
10	<primary language> as string: string
52	<property> as string: string
42	<rate> as string: string
10	<registry key value type> as string: string
10	<registry key value> as application: application
10	<registry key value> as file: file
10	<registry key value> as folder: folder
10	<registry key value> as integer: integer
10	<registry key value> as large integer: large integer
10	<registry key value> as string: string
10	<registry key value> as system file: file
10	<registry key value> as system x32 file: file
10	<registry key value> as system x64 file: file
10	<registry key value> as time: time
10	<registry key value> as uinteger: uinteger
10	<registry key> as string: string
52	<rope> as string: string
10	<security descriptor> as string: string
12	<security identifier> as string: string
12	<server based group> as string: string
10	<service> as string: string
12	<setting> as string: string
10	<site profile variable> as string: string
52	<site version list> as string: string
12	<smbios value> as hexadecimal: string
12	<smbios value> as string: string
12	<sqlite column type> as string: string
12	<sqlite column> as string: string
12	<sqlite database> as string: string
12	<sqlite row> as string: string
12	<sqlite table> as string: string
2	<stage> as string: string
52	<string> as binary_string: binary_string
52	<string> as boolean: boolean
52	<string> as date: date
52	<string> as day_of_month: day of month
52	<string> as day_of_week: day of week
52	<string> as floating point: floating point
52	<string> as fxf binary_string: binary_string
52	<string> as hexadecimal: string
52	<string> as html: html
52	<string> as integer: integer
52	<string> as ipv4or6 address: ipv4or6 address
52	<string> as ipv6 address: ipv6 address
52	<string> as large integer: large integer
52	<string> as left trimmed string: string
52	<string> as local binary_string: binary_string
52	<string> as local time: time
52	<string> as local zoned time_of_day: time of day with time zone
52	<string> as lowercase: string
52	<string> as month: month
52	<string> as right trimmed string: string
52	<string> as site version list: site version list
52	<string> as string: string
40	<string> as strverscmp version: strverscmp version
52	<string> as time interval: time interval
52	<string> as time zone: time zone
52	<string> as time: time
52	<string> as time_of_day: time of day
52	<string> as trimmed string: string
52	<string> as uinteger: uinteger
52	<string> as universal time: time
52	<string> as universal zoned time_of_day: time of day with time zone
52	<string> as uppercase: string
52	<string> as utf16 binary_string: binary_string
52	<string> as utf8 binary_string: binary_string
52	<string> as version: version
50	<string> as windows display time: time
52	<string> as year: year
52	<string> as zoned time_of_day: time of day with time zone
52	<substring> as string: string
52	<substring> as substring: substring
10	<system access control list> as string: string
10	<task action> as com handler task action: com handler task action
10	<task action> as email task action: email task action
10	<task action> as exec task action: exec task action
10	<task action> as show message task action: show message task action
10	<task trigger> as boot task trigger: boot task trigger
10	<task trigger> as daily task trigger: daily task trigger
10	<task trigger> as event task trigger: event task trigger
10	<task trigger> as idle task trigger: idle task trigger
10	<task trigger> as logon task trigger: logon task trigger
10	<task trigger> as monthly task trigger: monthly task trigger
10	<task trigger> as monthlydow task trigger: monthlydow task trigger
10	<task trigger> as registration task trigger: registration task trigger
10	<task trigger> as session state change task trigger: session state change task trigger
10	<task trigger> as time task trigger: time task trigger
10	<task trigger> as weekly task trigger: weekly task trigger
12	<tcp state> as string: string
52	<time interval> as string: string
52	<time of day with time zone> as string: string
52	<time of day> as string: string
52	<time range> as string: string
52	<time zone> as string: string
52	<time> as local date: date
52	<time> as local string: string
52	<time> as string: string
52	<time> as universal date: date
52	<time> as universal string: string
52	<tuple item> as string: string
52	<type> as string: string
52	<uinteger> as hexadecimal: string
52	<uinteger> as integer: integer
52	<uinteger> as large integer: large integer
52	<uinteger> as string: string
52	<uinteger> as uinteger: uinteger
52	<unary operator> as string: string
52	<undefined> as string: string
2	<user attribute> as string: string
12	<uuid> as binary_string: binary_string
12	<uuid> as hexadecimal: string
12	<uuid> as string: string
52	<version> as string: string
52	<version> as version: version
10	<winrt enumeration> as string: string
10	<winrt package user information> as string: string
10	<winrt package> as string: string
10	<wmi object> as string: string
10	<wmi select> as string: string
10	<xml dom node> as text: string
10	<xml dom node> as xml: string
2	<yaml key> as string: string
2	<yaml value> as boolean: boolean
2	<yaml value> as float: floating point
2	<yaml value> as integer: integer
2	<yaml value> as string: string
52	<year> as integer: integer
52	<year> as string: string
"""

# 4517 rows
PROPERTIES: str = """\
bf	abbr <string> of <html>: html
bf	abbr <string> of <string>: html
bf	abbr of <html>: html
bf	abbr of <string>: html
10	above normal priority: priority class
bf	absolute value of <hertz>: hertz
bf	absolute value of <integer>: integer
bf	absolute value of <time interval>: time interval
10	access mode of <access control entry>: integer
10	access system security permission of <access control entry>: boolean
1d	accessed time of <filesystem object>: time
d	accessed time of <symlink>: time
10	account disabled flag of <user>: boolean
10	account expiration of <user>: time
10	account lockout duration of <security database>: time interval
10	account lockout observation window of <security database>: time interval
10	account lockout threshold of <security database>: integer
10	account logon category of <audit policy>: audit policy category
10	account management category of <audit policy>: audit policy category
10	account name of <security identifier>: string
10	accounts operator flag of <user>: boolean
10	accounts with privilege <string>: security account
10	accounts with privileges: security account
1f	accuracy of <dmi electrical_current_probe>: integer
1f	accuracy of <dmi temperature_probe>: integer
1f	accuracy of <dmi voltage_probe>: integer
10	ace flag of <access control entry>: integer
10	ace type of <access control entry>: integer
bf	acronym <string> of <html>: html
bf	acronym <string> of <string>: html
bf	acronym of <html>: html
bf	acronym of <string>: html
a0	action <integer> of <bes fixlet>: bes fixlet action
1f	action <integer>: action
a0	action <string> of <bes fixlet>: bes fixlet action
a0	action dependencies of <bes action>: bes action
1f	action duration of <evaluation cycle>: time interval
a0	action flag of <bes filter>: boolean
1f	action lock state: action lock state
a0	action of <bes action result>: bes action
a0	action of <bes baseline component>: bes fixlet action
12	action of <firewall rule>: firewall action
1f	action percent of <evaluation cycle>: floating point
a0	action results of <bes computer>: bes action result
a0	action script of <bes action>: string
a0	action script type of <bes action>: string
a0	action set of <bes domain>: bes action set
a0	action set of <bes filter>: bes action set
a0	action set of <bes site>: bes action set
a0	action site of <bes user>: bes site
1f	action: action
a0	actions of <bes domain>: bes action
a0	actions of <bes fixlet>: bes fixlet action
a0	actions of <bes site>: bes action
10	actions of <task definition>: task action
a0	activations of <bes fixlet>: bes activation
1f	active action: action
1f	active container count of <bes product>: integer
1f	active count of <action>: integer
10	active device files <string>: file
10	active device files: file
10	active devices: active device
a0	active directory of <bes ldap directory>: boolean
a0	active directory path of <bes computer>: distinguished name
12	active directory user of <user>: active directory local user
12	active directory: active directory server
a0	active flag of <bes activation>: boolean
1f	active line number of <action>: integer
1f	active of <action>: boolean
1f	active of <logged on user>: boolean
1f	active start time of <action>: time
12	active state: power state
10	activity history of <logged on user>: activity history
12	adapter <integer> of <network>: network adapter
2	adapter <string> of <network>: network adapter
1f	adapter of <network adapter interface>: network adapter
1f	adapters of <network>: network adapter
1f	additional_information <integer> of <dmi>: dmi additional_information
1f	additional_informations of <dmi>: dmi additional_information
bf	address <string> of <html>: html
bf	address <string> of <string>: html
10	address lists of <network adapter>: network address list
1f	address of <dmi management_device>: integer
bf	address of <html>: html
1f	address of <network adapter interface>: ipv4or6 address
1f	address of <network adapter>: ipv4 address
10	address of <network address list>: ipv4 address
1f	address of <network ip interface>: ipv4 address
bf	address of <string>: html
1f	address_type of <dmi management_device>: integer
10	admin privilege of <user>: boolean
a0	administered computer set of <bes user>: bes computer set
a0	administered computers of <bes user>: bes computer
1f	administrative rights of <client>: administrative rights
a0	administrator <( bes computer, bes user )>: boolean
a0	administrator <( bes user, bes computer )>: boolean
a0	administrator <bes computer> of <bes user>: boolean
a0	administrator <bes user> of <bes computer>: boolean
1f	administrator <string> of <client>: setting
a0	administrator set of <bes computer>: bes user set
a0	administrators of <bes computer>: bes user
1f	administrators of <client>: setting
12	agent interface <string> of <client>: agent interface
12	agent interfaces of <client>: agent interface
a0	agent type of <bes computer>: string
a0	agent version of <bes computer>: string
2	alias of <file>: boolean
f	alias of <network ip interface>: boolean
a0	all bes sites: bes site
a0	all computer counts: historical computer count
10	all firewall scope: firewall scope
a0	all fixlet counts: historical fixlet count
10	all running services: service
10	all services: service
2	allocation block count of <volume>: integer
10	allow demand start of <task settings>: boolean
12	allow firewall action: firewall action
10	allow hard terminate of <task settings>: boolean
10	allow inbound echo request of <firewall icmp settings>: boolean
10	allow inbound mask request of <firewall icmp settings>: boolean
10	allow inbound router request of <firewall icmp settings>: boolean
10	allow inbound timestamp request of <firewall icmp settings>: boolean
10	allow outbound destination unreachable of <firewall icmp settings>: boolean
10	allow outbound packet too big of <firewall icmp settings>: boolean
10	allow outbound parameter problem of <firewall icmp settings>: boolean
10	allow outbound source quench of <firewall icmp settings>: boolean
10	allow outbound time exceeded of <firewall icmp settings>: boolean
10	allow redirect of <firewall icmp settings>: boolean
bf	allow unmentioned site of <license>: boolean
1f	allowed of <site>: boolean
1f	allowed sites of <restricted site>: site
10	allowed workstations string of <user>: string
a0	analysis flag of <bes filter>: boolean
a0	analysis flag of <bes fixlet>: boolean
a0	analysis flag of <bes property>: boolean
a0	analysis of <bes activation>: bes fixlet
a0	analysis set of <bes filter>: bes fixlet set
1f	analysis: analysis
1f	ancestors of <filesystem object>: folder
d	ancestors of <symlink>: folder
bf	anchor <string> of <html>: html
bf	anchor <string> of <string>: html
bf	anchor of <html>: html
bf	anchor of <string>: html
d	android of <operating system>: boolean
10	anonymous logon group: security account
10	ansi code page: integer
10	any adapter <integer> of <network>: network adapter
1f	any adapters of <network>: network adapter
bf	any ip version: ip version
10	aol error of <file>: string
10	aol error time of <file>: time
1f	api duration of <evaluation cycle>: time interval
1f	api percent of <evaluation cycle>: floating point
1f	apparent registration server time: time
10	append permission of <access control entry>: boolean
2	apple extras folder of <domain>: folder
2	apple extras folder: folder
2	apple menu items folder of <domain>: folder
2	apple menu items folder: folder
a0	applicability relevance of <bes action>: string
a0	applicable computer count of <bes baseline component>: integer
a0	applicable computer count of <bes fixlet>: integer
a0	applicable computer set of <bes baseline component>: bes computer set
a0	applicable computer set of <bes fixlet>: bes computer set
a0	applicable computers of <bes fixlet>: bes computer
1d	application <binary_string> of <folder>: application
1f	application <binary_string>: application
1d	application <string> of <folder>: application
10	application <string> of <registry key>: application
10	application <string> of <registry>: application
1f	application <string>: application
10	application event log: event log
10	application folder <string> of <registry key>: folder
10	application folder <string> of <registry>: folder
10	application folder of <registry key>: folder
12	application name of <firewall rule>: string
10	application of <registry key>: application
10	application parameter string of <user>: string
2	application support folder of <domain>: folder
2	application support folder: folder
1f	application usage summaries: application usage summary
1f	application usage summary <string>: application usage summary
1f	application usages <string>: timed( time range, integer )
2	applications folder of <domain>: folder
2	applications folder: folder
2	applications of <folder>: application
10	applications of <registry>: application
2	applications: application
a0	apply count of <bes action result>: integer
a0	approver role of <bes user>: bes role
bf	april <integer> of <integer>: date
bf	april <integer>: day of year
bf	april of <integer>: month and year
bf	april: month
9	architecture of <debian versioned package>: string
9	architecture of <debianpkg version>: string
1f	architecture of <operating system>: string
4	architecture of <package>: string
10	architecture of <winrt package id>: winrt enumeration
1f	archive duration of <evaluation cycle>: time interval
10	archive of <filesystem object>: boolean
1f	archive percent of <evaluation cycle>: floating point
10	argument string of <exec task action>: string
10	argument string of <file shortcut>: string
2	array <integer> of <array>: array
2	array <string> of <dictionary>: array
2	array <string> of <preference>: array
2	array of <file>: array
2	array of <osxvalue>: array
a0	asset of <bes unmanagedasset field>: bes unmanagedasset
1f	asset_tag of <dmi base_board_information>: string
1f	asset_tag of <dmi memory_device>: string
1f	asset_tag of <dmi processor_information>: string
1f	asset_tag_number of <dmi system_enclosure_or_chassis>: string
1f	asset_tag_number of <dmi system_power_supply>: string
2	assistants folder of <domain>: folder
2	assistants folder: folder
1f	associativity of <dmi cache_information>: integer
10	at compatibility of <task settings>: boolean
10	attachments of <email task action>: string
bf	attr lists of <( string, string )>: html attribute list
bd	attribute <integer> of <xml dom node>: xml dom node
2	attribute <string> of <user>: user attribute
bd	attribute <string> of <xml dom node>: xml dom node
10	attribute permission of <network share>: boolean
1f	attributes of <dmi memory_device>: integer
2	attributes of <user>: user attribute
bd	attributes of <xml dom node>: xml dom node
2	audio folder of <domain>: folder
2	audio folder: folder
2	audio plane of <registryroot>: registrynode
10	audit failure event log event type: event log event type
10	audit failure of <access control entry>: boolean
10	audit failure of <audit policy information>: boolean
10	audit level of <local mssql database>: integer
10	audit policy: audit policy
10	audit success event log event type: event log event type
10	audit success of <access control entry>: boolean
10	audit success of <audit policy information>: boolean
bf	august <integer> of <integer>: date
bf	august <integer>: day of year
bf	august of <integer>: month and year
bf	august: month
10	authenticated users group: security account
1f	authenticating of <client>: boolean
1f	authenticating of <current relay>: boolean
a0	author of <bes comment>: bes user
10	author of <task registration info>: string
10	authorized applications of <firewall profile>: firewall authorized application
a0	automatic flag of <bes computer group>: boolean
d	available amount of <ram>: integer
1f	average duration of <evaluation cycle>: time interval
1f	average of <evaluation cycle>: integer
bf	b <string> of <html>: html
bf	b <string> of <string>: html
bf	b of <html>: html
bf	b of <string>: html
1f	b32_bit_memory_error_information <integer> of <dmi>: dmi b32_bit_memory_error_information
1f	b32_bit_memory_error_informations of <dmi>: dmi b32_bit_memory_error_information
1f	b64_bit_memory_error_information <integer> of <dmi>: dmi b64_bit_memory_error_information
1f	b64_bit_memory_error_informations of <dmi>: dmi b64_bit_memory_error_information
d	background of <grub color pair>: grub color
10	backoffice bit <operating system suite mask>: boolean
2	backup time of <filesystem object>: time
10	bad password count of <user>: integer
1f	bank_connections of <dmi memory_module_information>: integer
1f	bank_locator of <dmi memory_device>: string
1f	banned prefetch plugins of <client>: string
bf	base <string> of <html>: html
bf	base <string> of <string>: html
a0	base distinguished name of <bes ldap directory>: string
10	base name of <operating system>: string
bf	base of <html>: html
bf	base of <string>: html
9	base package of <debianpkg version>: debian base package
9	base packages <string> of <debianpackagecache>: debian base package
9	base packages of <debianpackagecache>: debian base package
10	base priority of <process>: priority class
bf	base64 decode <string>: string
1d	base64 der encoded certificate string of <string>: x509 certificate
bf	base64 encode <string>: string
1f	base_address of <dmi ipmi_device_information>: integer
1f	base_board_information <integer> of <dmi>: dmi base_board_information
1f	base_board_informations of <dmi>: dmi base_board_information
a0	baseline flag of <bes filter>: boolean
a0	baseline flag of <bes fixlet>: boolean
a0	baseline set of <bes filter>: bes fixlet set
10	batch group: security account
10	bcc of <email task action>: string
10	below normal priority: priority class
a0	bes action set: bes action set
a0	bes action status constrained: bes action status
a0	bes action status disk free limited: bes action status
a0	bes action status disk limited: bes action status
a0	bes action status download failed: bes action status
a0	bes action status download size limited: bes action status
a0	bes action status error: bes action status
a0	bes action status evaluating: bes action status
a0	bes action status expired: bes action status
a0	bes action status failed: bes action status
a0	bes action status fixed: bes action status
a0	bes action status hash mismatch: bes action status
a0	bes action status invalid signature: bes action status
a0	bes action status irrelevant: bes action status
a0	bes action status locked site: bes action status
a0	bes action status locked: bes action status
a0	bes action status offers disabled: bes action status
a0	bes action status pending downloads: bes action status
a0	bes action status pending login: bes action status
a0	bes action status pending message: bes action status
a0	bes action status pending offer: bes action status
a0	bes action status pending restart: bes action status
a0	bes action status plugin interrupted: bes action status
a0	bes action status postponed: bes action status
a0	bes action status running: bes action status
a0	bes action status script unavailable: bes action status
a0	bes action status timeout reached: bes action status
a0	bes action status unreported: bes action status
a0	bes action status user cancelled: bes action status
a0	bes action status waiting: bes action status
a0	bes actions: bes action
a0	bes analyses: bes fixlet
a0	bes analysis set: bes fixlet set
a0	bes baseline set: bes fixlet set
a0	bes baselines: bes fixlet
a0	bes brand: string
a0	bes computer <integer>: bes computer
a0	bes computer group set of <bes computer>: bes computer group set
a0	bes computer group set: bes computer group set
a0	bes computer groups of <bes computer>: bes computer group
a0	bes computer groups: bes computer group
a0	bes computer set: bes computer set
a0	bes computer with extensions set: bes computer set
a0	bes computers with extensions: bes computer
a0	bes computers: bes computer
a0	bes current wruser: string
a0	bes custom sites: bes site
a0	bes deployment options <string>: bes deployment option
a0	bes deployment options: bes deployment option
a0	bes domain <string>: bes domain
a0	bes domain set: bes domain set
a0	bes domains: bes domain
a0	bes filter <integer>: bes filter
a0	bes filter set: bes filter set
a0	bes filters: bes filter
a0	bes fixlet set: bes fixlet set
a0	bes fixlets: bes fixlet
a0	bes languages: string
a0	bes ldap directories: bes ldap directory
a0	bes ldap directory set: bes ldap directory set
bf	bes license: license
a0	bes properties: bes property
a0	bes property <string>: bes property
a0	bes property set: bes property set
a0	bes role set: bes role set
a0	bes roles: bes role
a0	bes sites: bes site
a0	bes task set: bes fixlet set
a0	bes tasks: bes fixlet
a0	bes unmanagedasset set: bes unmanagedasset set
a0	bes unmanagedassets: bes unmanagedasset
a0	bes user set: bes user set
a0	bes users: bes user
a0	bes wakeonlan statuses: bes wakeonlan status
a0	bes webui app set: bes webui app set
a0	bes webui apps: bes webui app
a0	bes webui: bes webui
a0	bes wizard set: bes wizard set
a0	bes wizards: bes wizard
a0	best activation of <bes fixlet>: bes activation
bf	big <string> of <html>: html
bf	big <string> of <string>: html
1f	big endian of <operating system>: boolean
bf	big of <html>: html
bf	big of <string>: html
a0	bin at <time> of <statistic range>: statistical bin
1d	binary location of <filesystem object>: binary_string
1f	binary name of <filesystem object>: binary_string
1f	binary named files of <folder>: file
1f	binary named folders of <folder>: folder
bf	binary operators <string>: binary operator
bf	binary operators returning <type>: binary operator
bf	binary operators: binary operator
1d	binary pathname of <filesystem object>: binary_string
bf	binary_string <string>: binary_string
bf	binary_substring <( integer, integer )> of <binary_string>: binary_substring
bf	binary_substrings <binary_string> of <binary_string>: binary_substring
a0	bins of <statistic range>: statistical bin
1f	bios: bios
1f	bios_characteristics of <dmi bios_information>: integer
1f	bios_information <integer> of <dmi>: dmi bios_information
1f	bios_informations of <dmi>: dmi bios_information
1f	bios_language_information <integer> of <dmi>: dmi bios_language_information
1f	bios_language_informations of <dmi>: dmi bios_language_information
1f	bios_release_date of <dmi bios_information>: string
1f	bios_rom_size of <dmi bios_information>: integer
1f	bios_starting_address_segment of <dmi bios_information>: integer
1f	bios_version of <dmi bios_information>: string
bf	bit <integer> of <bit set>: boolean
bf	bit <integer> of <integer>: boolean
1a	bit <integer> of <large integer>: boolean
1a	bit <integer> of <uinteger>: boolean
bf	bit <integer>: bit set
bf	bit set <string>: bit set
2	blackhole flag of <route>: boolean
10	blade bit <operating system suite mask>: boolean
1f	blob of <sqlite column type>: boolean
12	block firewall action: firewall action
d	block list of <grub file location>: grub block list
d	block size of <filesystem>: integer
bf	blockquote <string> of <html>: html
bf	blockquote <string> of <string>: html
bf	blockquote of <html>: html
bf	blockquote of <string>: html
1f	board_type of <dmi base_board_information>: integer
bf	body <string> of <html>: html
bf	body <string> of <string>: html
a0	body of <bes fixlet>: html
10	body of <email task action>: string
bf	body of <html>: html
bf	body of <string>: html
d	bogomips of <processor>: integer
2	boolean <integer> of <array>: boolean
2	boolean <string> of <dictionary>: boolean
2	boolean <string> of <preference>: boolean
bf	boolean <string>: boolean
2	boolean of <osxvalue>: boolean
10	boolean value <integer> of <wmi select>: boolean
10	boolean values of <wmi select>: boolean
d	boot argument <integer> of <grub kernel>: string
d	boot arguments of <grub kernel>: string
10	boot task trigger type: task trigger type
1f	boot time of <operating system>: time
d	bootable image <integer> of <grub config file>: grub bootable image
d	bootable image <string> of <grub config file>: grub bootable image
d	bootable images of <grub config file>: grub bootable image
1f	bootup_state of <dmi system_enclosure_or_chassis>: integer
bf	br <string>: html
bf	br: html
12	brand id of <processor>: integer
1f	brand of <client>: string
1f	brand string of <processor>: string
1f	broadcast address of <network adapter interface>: ipv4or6 address
2	broadcast address of <network adapter>: ipv4 address
1f	broadcast address of <network ip interface>: ipv4 address
2	broadcast flag of <route>: boolean
1f	broadcast support of <network adapter interface>: boolean
2	broadcast support of <network adapter>: boolean
1f	broadcast support of <network ip interface>: boolean
12	bssid of <wifi network>: string
d	buffered amount of <ram>: integer
2	bug revision of <version>: integer
1f	build number high of <operating system>: integer
1f	build number low of <operating system>: integer
1f	build number of <operating system>: integer
1f	build of <operating system>: string
bf	build revision of <version>: integer
1f	build target of <client>: string
10	built in of <firewall open port>: boolean
1f	built_in_pointing_device <integer> of <dmi>: dmi built_in_pointing_device
1f	built_in_pointing_devices of <dmi>: dmi built_in_pointing_device
10	builtin administrators group: security account
10	builtin backup operators group: security account
10	builtin guests group: security account
10	builtin network configuration operators group: security account
10	builtin power users group: security account
10	builtin remote desktop users group: security account
10	builtin replicator group: security account
10	builtin users group: security account
2	bundle <string>: bundle
2	bundle of <folder>: bundle
2	bundle version of <bundle>: version
2	bundle version of <filesystem object>: version
2	bundle version of <folder>: version
1f	bus_number of <dmi onboard_devices_extended_information>: integer
1f	bus_number of <dmi system_slots>: integer
bf	byte <integer> of <binary_string>: binary_substring
1f	byte <integer> of <file>: integer
bf	byte <integer>: binary_string
bf	bytes of <binary_string>: binary_substring
2	cache folder of <domain>: folder
2	cache folder: folder
1f	cache_configuration of <dmi cache_information>: integer
1f	cache_information <integer> of <dmi>: dmi cache_information
1f	cache_informations of <dmi>: dmi cache_information
1f	cache_speed of <dmi cache_information>: integer
d	cached amount of <ram>: integer
a0	can create actions flag of <bes user>: boolean
10	can interact with desktop of <service>: boolean
a0	can lock flag of <bes user>: boolean
a0	can send multiple refresh flag of <bes user>: boolean
a0	can submit queries flag of <bes role>: boolean
a0	can submit queries flag of <bes user>: boolean
12	capabilities of <agent interface>: agent interface capability
1f	capabilities of <dmi system_reset>: integer
12	capability <string> of <agent interface>: agent interface capability
4	capability <string> of <rpmdatabase>: capability
4	capability <string>: capability
bf	caption <string> of <html>: html
bf	caption <string> of <string>: html
bf	caption of <html>: html
bf	caption of <string>: html
2	carbon folder of <domain>: folder
2	carbon folder: folder
1a	case insensitive perl regexes <string>: regular expression
1a	case insensitive perl regular expressions <string>: regular expression
bf	case insensitive regexes <string>: regular expression
bf	case insensitive regular expressions <string>: regular expression
bf	casts <string>: cast
bf	casts from of <type>: cast
bf	casts returning <type>: cast
bf	casts: cast
10	categories of <audit policy>: audit policy category
a0	category of <bes fixlet>: string
a0	category of <bes property>: string
10	category of <event log record>: integer
10	cc of <email task action>: string
1f	certificate of <client>: x509 certificate
d	chainloader of <grub bootable image>: grub file location
10	change notification permission of <access control entry>: boolean
d	change time of <filesystem object>: time
d	change time of <symlink>: time
12	channel band of <wifi network>: string
12	channel number of <wifi network>: integer
1f	channel_type of <dmi memory_channel>: integer
bf	character <integer> of <string>: substring
bf	character <integer>: string
1f	character sets of <client>: string
bf	characters of <string>: substring
a0	charset of <bes fixlet>: string
a0	charset of <bes wizard>: string
1f	chassis_handle of <dmi base_board_information>: integer
10	checkpoint of <service>: integer
2	chewable items folder of <domain>: folder
2	chewable items folder: folder
bd	child node <integer> of <xml dom node>: xml dom node
bd	child nodes of <xml dom node>: xml dom node
1f	cidr address of <network adapter interface>: string
1f	cidr address of <network adapter>: string
10	cidr address of <network address list>: string
1f	cidr address of <network ip interface>: string
1f	cidr string of <network adapter interface>: string
1f	cidr string of <network adapter>: string
10	cidr string of <network address list>: string
1f	cidr string of <network ip interface>: string
1a	cidr subnet <string>: cidr subnet
1a	cidr subnet of <network adapter interface>: cidr subnet
1a	cidr subnet of <network adapter>: cidr subnet
10	cidr subnet of <network address list>: cidr subnet
1a	cidr subnet of <network ip interface>: cidr subnet
bf	cite <string> of <html>: html
bf	cite <string> of <string>: html
bf	cite of <html>: html
bf	cite of <string>: html
10	class id of <com handler task action>: string
10	class of <active device>: string
2	classic domain: domain
2	classic folder of <domain>: folder
2	classic folder: folder
2	classname of <registrynode>: string
1f	client cryptography: client_cryptography
bf	client device count of <bes product>: integer
a0	client evaluated flag of <bes computer group>: boolean
1f	client folder of <site>: folder
a0	client installed flag of <bes unmanagedasset>: boolean
bf	client license: license
12	client product of <agent interface>: string
1f	client query duration of <evaluation cycle>: time interval
1f	client query percent of <evaluation cycle>: floating point
a0	client settings of <bes computer>: bes client setting
1f	client: client
2	cloned of <route>: boolean
2	cloning flag of <route>: boolean
1f	close wait of <tcp state>: boolean
1f	closed of <tcp state>: boolean
1f	closing of <tcp state>: boolean
bf	cloud count of <bes product>: integer
1f	cloud provider: cloud provider
bf	code <string> of <html>: html
bf	code <string> of <string>: html
bf	code of <html>: html
bf	code of <string>: html
10	code page of <user>: integer
f	codename of <operating system>: string
10	codepage of <file version block>: string
bf	col <string> of <html>: html
bf	col <string> of <string>: html
bf	col of <html>: html
bf	col of <string>: html
bf	colgroup <string> of <html>: html
bf	colgroup <string> of <string>: html
bf	colgroup of <html>: html
bf	colgroup of <string>: html
d	color scheme of <grub config file>: grub color scheme
2	color sync folder of <domain>: folder
2	color sync folder: folder
2	colorsync profiles folder of <domain>: folder
2	colorsync profiles folder: folder
1f	column <integer> of <sqlite row>: sqlite column
1f	column <string> of <sqlite row>: sqlite column
1f	column type <integer> of <sqlite table>: sqlite column type
1f	column type <string> of <sqlite table>: sqlite column type
1f	column types of <sqlite table>: sqlite column type
10	com handler task action type: task action type
d	coma bug of <processor>: boolean
d	command line argument <integer> of <process>: string
d	command line arguments of <process>: string
10	comment of <local group>: string
10	comment of <network share>: string
12	comment of <user>: string
a0	comments of <bes action>: bes comment
a0	comments of <bes computer>: bes comment
a0	comments of <bes fixlet>: bes comment
bf	common name of <license>: string
10	communications bit <operating system suite mask>: boolean
10	communications operator flag of <user>: boolean
9	compare_op of <debianpkg dependency>: string
1f	competition size of <selected server>: integer
1f	competition weight of <selected server>: integer
1f	complete time of <action>: time
b0	component <integer> of <distinguished name>: distinguished name component
bf	component <integer> of <site version list>: integer
2	component folder of <domain>: folder
2	component folder: folder
a0	component groups of <bes fixlet>: bes baseline component group
12	component string of <security identifier>: string
1f	component_handle of <dmi management_device_component>: integer
a0	components of <bes baseline component group>: bes baseline component
b0	components of <distinguished name>: distinguished name component
a0	components xml of <bes fixlet>: string
2	components: component
10	compressed of <filesystem object>: boolean
bf	computer count of <bes product>: integer
a0	computer flag of <bes filter>: boolean
a0	computer group flag of <bes action>: boolean
a0	computer group set of <bes domain>: bes computer group set
a0	computer group set of <bes filter>: bes fixlet set
a0	computer groups of <bes domain>: bes computer group
1f	computer id: integer
1f	computer name: string
a0	computer of <bes action result>: bes computer
a0	computer of <bes fixlet result>: bes computer
a0	computer of <bes property result>: bes computer
10	computer of <event log record>: string
a0	computer set of <bes filter>: bes computer set
2	computer: computer
bf	concatenations <html> of <html>: html
bf	concatenations <html> of <string>: html
bf	concatenations <string> of <html>: html
bf	concatenations <string> of <string>: string
bf	concatenations of <html>: html
bf	concatenations of <string>: string
2	condemned flag of <route>: boolean
4	conflicts of <package>: capability
bf	conjunctions of <boolean>: boolean
10	connection status <integer>: connection status
10	connection status authenticating: connection status
10	connection status authentication failed: connection status
10	connection status authentication succeeded: connection status
10	connection status connected: connection status
10	connection status connecting: connection status
10	connection status disconnected: connection status
10	connection status disconnecting: connection status
10	connection status hardware disabled: connection status
10	connection status hardware malfunction: connection status
10	connection status media disconnected: connection status
10	connection status no hardware present: connection status
1f	connections of <dmi out_of_band_remote_access>: integer
10	connections of <network>: connection
10	console connect of <session state change task trigger>: boolean
10	console disconnect of <session state change task trigger>: boolean
a0	constrain by property name of <bes action>: string
a0	constrain by property relation of <bes action>: string
a0	constrain by property value of <bes action>: string
1f	constrained of <action>: boolean
1f	constraint of <action>: integer
1f	contained_element_count of <dmi system_enclosure_or_chassis>: integer
1f	contained_element_record_length of <dmi system_enclosure_or_chassis>: integer
10	container inherit of <access control entry>: boolean
a0	content id of <bes fixlet action>: string
1f	content of <file>: file content
2	contextual menu items folder of <domain>: folder
2	contextual menu items folder: folder
a0	continue on errors flag of <bes action>: boolean
10	control of <security descriptor>: integer
2	control panels <string>: enableable_file
2	control panels folder of <domain>: folder
2	control panels folder: folder
2	control panels: enableable_file
2	control strip modules folder of <domain>: folder
2	control strip modules folder: folder
1f	controller of <action lock state>: string
1f	cooling_device <integer> of <dmi>: dmi cooling_device
1f	cooling_device_handle of <dmi system_power_supply>: integer
1f	cooling_devices of <dmi>: dmi cooling_device
1f	cooling_unit_group of <dmi cooling_device>: integer
1f	core of <cpupackage>: integer
2	core services folder of <domain>: folder
2	core services folder: folder
1f	core_count of <dmi processor_information>: integer
1f	core_enabled of <dmi processor_information>: integer
a2	correlation coefficient of <exponential projection>: floating point
a2	correlation coefficient of <linear projection>: floating point
a0	correlation flag of <bes computer>: boolean
a0	correlation id of <bes computer>: integer
a0	correlation of <bes computer>: bes computer
a0	count maps of <historical fixlet count>: fixlet count pair
1f	count of <cpupackage>: integer
a0	count of <fixlet count pair>: integer
a0	count of <historical computer count>: integer
12	count of <monitor power interval>: integer
2	country <string>: country
10	country code of <user>: integer
a0	cpu of <bes computer>: string
2	cpu speed: integer
d	cpuid level of <processor>: integer
1f	cpupackage: cpupackage
10	create file permission of <access control entry>: boolean
10	create folder permission of <access control entry>: boolean
10	create link permission of <access control entry>: boolean
10	create permission of <network share>: boolean
10	create subkey permission of <access control entry>: boolean
a0	creation date of <bes site>: time
a0	creation time of <bes activation>: time
a0	creation time of <bes computer group>: time
a0	creation time of <bes fixlet>: time
a0	creation time of <bes user>: time
12	creation time of <filesystem object>: time
10	creation time of <process>: time
10	creator group group: security account
a0	creator of <bes site>: bes user
2	creator of <bundle>: file signature
2	creator of <file>: file signature
10	creator owner group: security account
9	critical of <debianpkg dependency>: boolean
bf	cryptography: cryptography
10	csd version of <operating system>: string
10	csidl folder <integer>: folder
2	cstring <string> of <dictionary>: string
2	cstring of <osxvalue>: string
10	current action of <running task>: string
a0	current analysis: bes fixlet
1f	current analysis: fixlet
a0	current bes servers: bes server
a0	current bes site: bes site
a0	current computer: bes computer
a0	current console user: bes user
bf	current date: date
bf	current day_of_month: day of month
bf	current day_of_week: day of week
bf	current day_of_year: day of year
a0	current domain: bes domain
10	current firewall profile type: firewall profile type
a0	current fixlet: bes fixlet
12	current monitor interval of <power history>: monitor power interval
bf	current month: month
bf	current month_and_year: month and year
12	current network of <wifi>: wifi network
10	current profile of <firewall policy>: firewall profile
10	current profile type of <firewall>: firewall profile type
1f	current relay: current relay
1f	current site: site
d	current status of <SELinux Boolean>: boolean
12	current system interval of <power history>: system power interval
a0	current task: bes fixlet
bf	current time_of_day <time zone>: time of day with time zone
bf	current time_of_day: time of day with time zone
a0	current unmanagedasset: bes unmanagedasset
2	current user folder of <domain>: folder
2	current user folder: folder
10	current user key <logged on user> of <registry>: registry key
10	current user key of <registry>: registry key
1f	current user: logged on user
a0	current wizard: bes wizard
bf	current year: year
1f	current_interleave of <dmi memory_controller_information>: integer
1f	current_language of <dmi bios_language_information>: string
1f	current_memory_type of <dmi memory_module_information>: integer
1f	current_speed of <dmi memory_module_information>: integer
1f	current_speed of <dmi processor_information>: integer
1f	current_sram_type of <dmi cache_information>: integer
1f	current_usage of <dmi system_slots>: integer
10	currently active of <firewall rule>: boolean
9	currently installed of <debian base package>: boolean
9	currently installed of <debian versioned package>: boolean
a0	custom bes fixlet set: bes fixlet set
a0	custom bes fixlets: bes fixlet
a0	custom content flag of <bes user>: boolean
10	custom firewall scope: firewall scope
a0	custom fixlet set of <bes domain>: bes fixlet set
a0	custom fixlets of <bes domain>: bes fixlet
a0	custom flag of <bes fixlet>: boolean
a0	custom flag of <bes property>: boolean
a0	custom refresh interval flag of <bes computer group>: boolean
a0	custom refresh interval of <bes computer group>: time interval
a0	custom site flag of <bes fixlet>: boolean
a0	custom site flag of <bes site>: boolean
a0	custom site of <bes fixlet>: bes site
a0	custom site set of <bes domain>: bes site set
1f	custom site subscription effective date <string>: time
a0	custom sites of <bes domain>: bes site
a0	custom success relevance of <bes action>: string
a0	custom success relevance of <bes fixlet action>: string
10	customized of <firewall service>: boolean
a0	cve id list of <bes fixlet>: string
10	dacl of <security descriptor>: discretionary access control list
10	daily task trigger type: task trigger type
a0	dashboard id of <bes wizard>: string
2	data <string> of <dictionary>: binary_string
10	data file of <site profile>: file
1f	data folder of <client>: folder
2	data fork of <file>: datafork
10	data of <com handler task action>: string
2	data of <osxvalue>: binary_string
10	data of <task definition>: string
1f	data_width of <dmi memory_device>: integer
a0	database id of <bes action>: integer
a0	database id of <bes activation>: integer
a0	database id of <bes computer group>: integer
a0	database id of <bes computer>: integer
a0	database id of <bes deployment option>: integer
a0	database id of <bes property>: integer
a0	database id of <bes server>: integer
a0	database id of <bes wakeonlan status>: integer
a0	database id of <bes wizard>: integer
a0	database id of <historical computer count>: integer
a0	database id of <historical fixlet count>: integer
a0	database name of <bes action>: string
a0	database name of <bes computer>: string
a0	database name of <bes deployment option>: string
a0	database name of <bes server>: string
a0	database name of <bes wakeonlan status>: string
a0	database name of <bes wizard>: string
10	datacenter bit <operating system suite mask>: boolean
a0	datastore inspector: module
2	date <integer> of <array>: time
2	date <string> of <dictionary>: time
2	date <string> of <preference>: time
bf	date <string>: date
bf	date <time zone> of <time>: date
1f	date of <bios>: string
2	date of <osxvalue>: time
10	date of <task registration info>: time
a0	date range end of <bes action>: date
a0	date range start of <bes action>: date
bf	day of <day of year>: day of month
bf	day: time interval
bf	day_of_month <integer>: day of month
bf	day_of_month <string>: day of month
bf	day_of_month of <date>: day of month
bf	day_of_week <string>: day of week
a0	day_of_week constraints of <bes action>: day of week
bf	day_of_week of <date>: day of week
bf	day_of_year of <date>: day of year
10	days interval of <daily task trigger>: time interval
10	days runs of <monthly task trigger>: day of month
10	days runs of <monthlydow task trigger>: day of week
10	days runs of <weekly task trigger>: day of week
bf	dd <string> of <html>: html
bf	dd <string> of <string>: html
bf	dd of <html>: html
bf	dd of <string>: html
9	debian package version <debian package version>: debian package version
9	debian package version <string>: debian package version
9	debian package version epoch <debian package version epoch>: debian package version epoch
9	debian package version epoch <string>: debian package version epoch
9	debian package version revision <debian package version revision>: debian package version revision
9	debian package version revision <string>: debian package version revision
9	debian package version upstream <debian package upstream version>: debian package upstream version
9	debian package version upstream <string>: debian package upstream version
9	debianpackage: debianpackagecache
bf	december <integer> of <integer>: date
bf	december <integer>: day of year
bf	december of <integer>: month and year
bf	december: month
a0	default action of <bes fixlet>: bes fixlet action
a0	default flag of <bes property>: boolean
d	default image of <grub config file>: grub image choice
2	default of <route>: boolean
a0	default page name of <bes wizard>: string
10	default value of <registry key>: registry key value
10	default web browser: application
d	default web browser: file
bf	definition lists <string> of <html>: html
bf	definition lists <string> of <string>: html
bf	definition lists of <html>: html
bf	definition lists of <string>: html
a0	definition of <bes property>: string
10	definition of <scheduled task>: task definition
bf	del <string> of <html>: html
bf	del <string> of <string>: html
bf	del of <html>: html
bf	del of <string>: html
10	delay of <boot task trigger>: time interval
10	delay of <event task trigger>: time interval
10	delay of <logon task trigger>: time interval
10	delay of <registration task trigger>: time interval
10	delay of <session state change task trigger>: time interval
2	delclone flag of <route>: boolean
10	delete child permission of <access control entry>: boolean
10	delete expired task after of <task settings>: time interval
10	delete permission of <access control entry>: boolean
10	delete permission of <network share>: boolean
1f	delete tcb of <tcp state>: boolean
a0	deleted flag of <bes comment>: boolean
10	deny type of <access control entry>: boolean
10	dep enabled of <process>: boolean
9	dependencies of <debian versioned package>: debianpkg dependency
bf	dependency known of <property>: boolean
1f	deployment character set of <client>: string
1f	descendant folders of <folder>: folder
1f	descendants of <folder>: file
10	descendants of <task folder>: scheduled task
10	description of <active device>: string
a0	description of <bes site>: string
1f	description of <dmi electrical_current_probe>: string
1f	description of <dmi management_device>: string
1f	description of <dmi management_device_component>: string
1f	description of <dmi temperature_probe>: string
1f	description of <dmi voltage_probe>: string
10	description of <event log record>: string
10	description of <firewall rule>: string
10	description of <network adapter>: string
10	description of <task registration info>: string
1f	description_string of <dmi on_board_devices_information>: string
1f	design_capacity of <dmi portable_battery>: integer
1f	design_capacity_multiplier of <dmi portable_battery>: integer
1f	design_voltage of <dmi portable_battery>: integer
1f	desired encrypt report of <client_cryptography>: boolean
bf	desired fips mode of <cryptography>: boolean
2	desktop folder of <domain>: folder
2	desktop folder: folder
f	destination of <route>: ipv4or6 address
2	destination string of <route>: string
2	destination type of <route>: string
a0	detailed status of <bes action result>: string
10	detailed tracking category of <audit policy>: audit policy category
2	developer docs folder of <domain>: folder
2	developer docs folder: folder
2	developer folder of <domain>: folder
2	developer folder: folder
2	developer help folder of <domain>: folder
2	developer help folder: folder
1f	device count of <bes product>: integer
d	device file <filesystem object>: device file
d	device file <string> of <folder>: device file
d	device file <string>: device file
d	device file <symlink>: device file
d	device files of <folder>: device file
10	device name of <connection>: string
d	device name of <filesystem>: string
d	device of <grub file location>: grub device
a0	device type of <bes computer>: string
d	device type of <device file>: string
10	device type: string
1f	device_chemistry of <dmi portable_battery>: integer
1f	device_description <integer> of <dmi on_board_devices_information>: string
1f	device_descriptions of <dmi on_board_devices_information>: string
1f	device_error_address of <dmi b32_bit_memory_error_information>: integer
1f	device_error_address of <dmi b64_bit_memory_error_information>: integer
1f	device_function_number of <dmi onboard_devices_extended_information>: integer
1f	device_function_number of <dmi system_slots>: integer
1f	device_locator of <dmi memory_device>: string
1f	device_name of <dmi portable_battery>: string
1f	device_name of <dmi system_power_supply>: string
1f	device_set of <dmi memory_device>: integer
1f	device_type <integer> of <dmi on_board_devices_information>: integer
1f	device_type_and_status of <dmi cooling_device>: integer
1f	device_type_instance of <dmi onboard_devices_extended_information>: integer
1f	device_types of <dmi on_board_devices_information>: integer
2	devicetree plane of <registryroot>: registrynode
bf	dfn <string> of <html>: html
bf	dfn <string> of <string>: html
bf	dfn of <html>: html
bf	dfn of <string>: html
10	dhcp enabled of <network adapter>: boolean
10	dhcp server of <network adapter>: ipv4 address
a0	dialog flag of <bes wizard>: boolean
10	dialup group: security account
2	dictionary <integer> of <array>: dictionary
2	dictionary <string> of <dictionary>: dictionary
2	dictionary <string> of <preference>: dictionary
2	dictionary of <file>: dictionary
2	dictionary of <osxvalue>: dictionary
2	dictionary of <registrynode>: dictionary
2	dictionary of <registryroot>: dictionary
a0	digest file name of <bes fixlet>: string
bf	direct object type of <property>: type
2	directory count of <volume>: integer
2	disabled control panel <string>: enableable_file
2	disabled control panels folder of <domain>: folder
2	disabled control panels folder: folder
2	disabled control panels: enableable_file
2	disabled extension <string>: enableable_file
2	disabled extensions folder of <domain>: folder
2	disabled extensions folder: folder
2	disabled extensions: enableable_file
d	disabled of <Xinetd Service>: boolean
2	disabled of <enableable_file>: boolean
2	disabled shutdown item <string>: enableable_file
2	disabled shutdown items folder of <domain>: folder
2	disabled shutdown items folder: folder
2	disabled shutdown items: enableable_file
2	disabled startup item <string>: enableable_file
2	disabled startup items folder of <domain>: folder
2	disabled startup items folder: folder
2	disabled startup items: enableable_file
10	disabled state of <running task>: boolean
10	disabled state of <scheduled task>: boolean
2	disabled system extensions folder of <domain>: folder
2	disabled system extensions folder: folder
10	disallow start when on battery of <task settings>: boolean
bf	disjunctions of <boolean>: boolean
a0	disk usage of <bes property>: integer
a0	display category of <bes fixlet>: string
a0	display category of <bes property>: string
a0	display message of <bes fixlet>: html
a0	display name of <bes domain>: string
a0	display name of <bes fixlet>: string
a0	display name of <bes property>: string
a0	display name of <bes site>: string
a0	display name of <bes wizard>: string
1a	display name of <operating system>: string
10	display name of <service>: string
10	display name of <task principal>: string
a0	display simple name of <bes property>: string
a0	display source id of <bes fixlet>: string
a0	display source of <bes fixlet>: string
a0	display source severity of <bes fixlet>: string
a0	display value of <bes fixlet field value>: string
10	display version of <operating system>: string
1f	distance of <selected server>: integer range
b0	distinguished name <string>: distinguished name
12	distinguished name error message of <active directory group>: string
12	distinguished name error message of <active directory local computer>: string
12	distinguished name error message of <active directory local user>: string
12	distinguished name of <active directory group>: string
12	distinguished name of <active directory local computer>: string
12	distinguished name of <active directory local user>: string
a0	distinguished name of <bes user>: string
bf	div <string> of <html>: html
bf	div <string> of <string>: html
bf	div of <html>: html
bf	div of <string>: html
bf	divided by zero of <floating point>: boolean
1f	dmi: dmi
12	dns domainname of <active directory local computer>: string
12	dns domainname of <active directory local user>: string
1f	dns name: string
10	dns servers of <network adapter>: network address list
10	dns servers of <network>: network address list
10	dns suffix of <network adapter>: string
a0	document flag of <bes wizard>: boolean
2	documentation folder of <domain>: folder
2	documentation folder: folder
10	documentation of <task registration info>: string
2	documents folder of <domain>: folder
2	documents folder: folder
10	domain firewall profile type: firewall profile type
2	domain library folder of <domain>: folder
2	domain library folder: folder
10	domain name of <security identifier>: string
d	domain name: string
10	domain of <active directory local user>: string
a0	domain of <bes action>: bes domain
a0	domain of <bes computer group>: bes domain
a0	domain of <bes filter>: bes domain
a0	domain of <bes fixlet>: bes domain
10	domain of <user>: string
10	domain profile of <firewall policy>: firewall profile
a0	domain set of <bes site>: bes domain set
2	domain top folder of <domain>: folder
2	domain top folder: folder
10	domain user <string>: user
10	domain user of <active directory local user>: user
10	domain users: user
d	domainname: string
a0	domains of <bes site>: bes domain
2	done flag of <route>: boolean
1f	download failure of <action>: integer
1f	download file <string> of <encoding>: file
1f	download file <string>: file
1f	download folder of <encoding>: folder
1f	download folder: folder
bf	download hash algorithms of <license>: string
1f	download path <string>: string
1f	download server: download server
a0	download size of <bes fixlet>: integer
1d	download storage folder: download storage folder
2	drive <integer>: volume
10	drive <string>: drive
d	drive <string>: filesystem
d	drive of <device file>: filesystem
d	drive of <fifo file>: filesystem
d	drive of <file>: filesystem
2	drive of <file>: volume
10	drive of <filesystem object>: drive
d	drive of <folder>: filesystem
2	drive of <folder>: volume
d	drive of <socket file>: filesystem
d	drive of <symlink>: filesystem
10	driver key of <active device>: registry key
10	driver key of <registry key>: registry key
10	driver key value name of <active device>: string
10	driver running services: service
10	driver services: service
10	driver type of <service>: boolean
2	drives <string>: volume
10	drives: drive
d	drives: filesystem
2	drives: volume
10	ds access category of <audit policy>: audit policy category
bf	dt <string> of <html>: html
bf	dt <string> of <string>: html
bf	dt of <html>: html
bf	dt of <string>: html
10	duration of <task repetition pattern>: time interval
2	dynamic flag of <route>: boolean
10	edge traversal allowed of <firewall rule>: boolean
a0	editable flag of <bes unmanagedasset field>: boolean
10	effective access mode for <security account> of <access control list>: integer
10	effective access mode for <string> of <access control list>: integer
10	effective access system security permission for <security account> of <access control list>: boolean
10	effective access system security permission for <string> of <access control list>: boolean
10	effective append permission for <security account> of <access control list>: boolean
10	effective append permission for <string> of <access control list>: boolean
10	effective change notification permission for <security account> of <access control list>: boolean
10	effective change notification permission for <string> of <access control list>: boolean
10	effective create file permission for <security account> of <access control list>: boolean
10	effective create file permission for <string> of <access control list>: boolean
10	effective create folder permission for <security account> of <access control list>: boolean
10	effective create folder permission for <string> of <access control list>: boolean
10	effective create link permission for <security account> of <access control list>: boolean
10	effective create link permission for <string> of <access control list>: boolean
10	effective create subkey permission for <security account> of <access control list>: boolean
10	effective create subkey permission for <string> of <access control list>: boolean
1f	effective date of <action lock state>: time
14	effective date of <plugin store key>: time
1f	effective date of <setting>: time
10	effective delete child permission for <security account> of <access control list>: boolean
10	effective delete child permission for <string> of <access control list>: boolean
10	effective delete permission for <security account> of <access control list>: boolean
10	effective delete permission for <string> of <access control list>: boolean
bf	effective download hash algorithm of <license>: string
10	effective enumerate subkeys permission for <security account> of <access control list>: boolean
10	effective enumerate subkeys permission for <string> of <access control list>: boolean
10	effective execute permission for <security account> of <access control list>: boolean
10	effective execute permission for <string> of <access control list>: boolean
10	effective generic all permission for <security account> of <access control list>: boolean
10	effective generic all permission for <string> of <access control list>: boolean
10	effective generic execute permission for <security account> of <access control list>: boolean
10	effective generic execute permission for <string> of <access control list>: boolean
10	effective generic read permission for <security account> of <access control list>: boolean
10	effective generic read permission for <string> of <access control list>: boolean
10	effective generic write permission for <security account> of <access control list>: boolean
10	effective generic write permission for <string> of <access control list>: boolean
10	effective list permission for <security account> of <access control list>: boolean
10	effective list permission for <string> of <access control list>: boolean
10	effective maximum allowed permission for <security account> of <access control list>: boolean
10	effective maximum allowed permission for <string> of <access control list>: boolean
10	effective policy <security account> of <audit policy subcategory>: audit policy information
10	effective query value permission for <security account> of <access control list>: boolean
10	effective query value permission for <string> of <access control list>: boolean
10	effective read attributes permission for <security account> of <access control list>: boolean
10	effective read attributes permission for <string> of <access control list>: boolean
10	effective read control permission for <security account> of <access control list>: boolean
10	effective read control permission for <string> of <access control list>: boolean
10	effective read extended attributes permission for <security account> of <access control list>: boolean
10	effective read extended attributes permission for <string> of <access control list>: boolean
10	effective read permission for <security account> of <access control list>: boolean
10	effective read permission for <string> of <access control list>: boolean
10	effective set value permission for <security account> of <access control list>: boolean
10	effective set value permission for <string> of <access control list>: boolean
bf	effective signature hash algorithm of <license>: string
10	effective synchronize permission for <security account> of <access control list>: boolean
10	effective synchronize permission for <string> of <access control list>: boolean
d	effective time of <runlevel>: time
10	effective traverse permission for <security account> of <access control list>: boolean
10	effective traverse permission for <string> of <access control list>: boolean
d	effective user of <process>: user
10	effective write attributes permission for <security account> of <access control list>: boolean
10	effective write attributes permission for <string> of <access control list>: boolean
10	effective write dac permission for <security account> of <access control list>: boolean
10	effective write dac permission for <string> of <access control list>: boolean
10	effective write extended attributes permission for <security account> of <access control list>: boolean
10	effective write extended attributes permission for <string> of <access control list>: boolean
10	effective write owner permission for <security account> of <access control list>: boolean
10	effective write owner permission for <string> of <access control list>: boolean
10	effective write permission for <security account> of <access control list>: boolean
10	effective write permission for <string> of <access control list>: boolean
d	elapsed time of <process>: time interval
1f	electrical_current_probe <integer> of <dmi>: dmi electrical_current_probe
1f	electrical_current_probes of <dmi>: dmi electrical_current_probe
bf	element <integer> of <json value>: json value
a0	elements of <bes action set>: bes action
a0	elements of <bes computer group set>: bes computer group
a0	elements of <bes computer set>: bes computer
a0	elements of <bes domain set>: bes domain
a0	elements of <bes filter set>: bes filter
a0	elements of <bes fixlet set>: bes fixlet
a0	elements of <bes ldap directory set>: bes ldap directory
a0	elements of <bes property set>: bes property
a0	elements of <bes role set>: bes role
a0	elements of <bes site file set>: bes site file
a0	elements of <bes site set>: bes site
a0	elements of <bes unmanagedasset set>: bes unmanagedasset
a0	elements of <bes user set>: bes user
a0	elements of <bes webui app set>: bes webui app
a0	elements of <bes wizard set>: bes wizard
bf	elements of <integer set>: integer
bf	elements of <json value>: json value
bf	elements of <string set>: string
bf	em <string> of <html>: html
bf	em <string> of <string>: html
bf	em of <html>: html
bf	em of <string>: html
bf	email address of <license>: string
10	email task action type: task action type
10	embedded nt bit <operating system suite mask>: boolean
1f	embedded of <operating system>: boolean
10	embedded restricted bit <operating system suite mask>: boolean
1f	embedded_controller_firmware_major_release of <dmi bios_information>: integer
1f	embedded_controller_firmware_minor_release of <dmi bios_information>: integer
2	enabled control panel <string>: enableable_file
2	enabled control panels: enableable_file
2	enabled extension <string>: enableable_file
2	enabled extensions: enableable_file
1f	enabled of <administrative rights>: boolean
a0	enabled of <bes wakeonlan status>: boolean
2	enabled of <enableable_file>: boolean
10	enabled of <firewall authorized application>: boolean
10	enabled of <firewall open port>: boolean
10	enabled of <firewall rule>: boolean
10	enabled of <firewall service>: boolean
2	enabled of <firewall>: boolean
10	enabled of <internet connection firewall>: boolean
10	enabled of <port mapping>: boolean
1f	enabled of <restricted site>: boolean
10	enabled of <scheduled task>: boolean
1f	enabled of <setting>: boolean
10	enabled of <task settings>: boolean
10	enabled of <task trigger>: boolean
12	enabled of <wifi>: boolean
2	enabled shutdown item <string>: enableable_file
2	enabled shutdown items: enableable_file
2	enabled startup item <string>: enableable_file
2	enabled startup items: enableable_file
1f	enabled_size of <dmi memory_module_information>: integer
1f	encoding <string>: encoding
1f	encoding of <sqlite database>: string
1f	encrypt report failure message of <client_cryptography>: string
1f	encrypt report of <client_cryptography>: boolean
14	encrypted of <plugin store key>: boolean
bf	encryption certificate of <license>: x509 certificate
12	encryption of <wifi>: string
10	end boundary of <task trigger>: time
a0	end date of <bes action>: date
a0	end flag of <bes action>: boolean
bf	end of <binary_substring>: binary position
a0	end of <statistic range>: time
a0	end of <statistical bin>: time
bf	end of <substring>: string position
bf	end of <time range>: time
a0	end time of <bes action result>: time
a0	end time_of_day of <bes action>: time of day
1f	end_of_table <integer> of <dmi>: dmi end_of_table
1f	end_of_tables of <dmi>: dmi end_of_table
1f	ending_address of <dmi memory_array_mapped_address>: integer
1f	ending_address of <dmi memory_device_mapped_address>: integer
10	engine pid of <running task>: integer
bf	enhanced security of <license>: boolean
10	enterprise bit <operating system suite mask>: boolean
10	entries of <access control list>: access control entry
2	entries of <dictionary>: dictionaryentry
10	enumerate subkeys permission of <access control entry>: boolean
d	environment of <process>: environment
1f	environment: environment
9	epoch of <debian package version>: debian package version epoch
4	epoch of <rpm package version record>: integer
4	epoch of <short rpm package version record>: integer
bf	error <string>: undefined
12	error code of <agent interface capability>: integer
10	error event log event type: event log event type
a0	error flag of <bes property result>: boolean
a0	error message of <bes property result>: string
1f	error_correcting_capability of <dmi memory_controller_information>: integer
1f	error_correction_type of <dmi cache_information>: integer
1f	error_detecting_method of <dmi memory_controller_information>: integer
1f	error_granularity of <dmi b32_bit_memory_error_information>: integer
1f	error_granularity of <dmi b64_bit_memory_error_information>: integer
1f	error_operation of <dmi b32_bit_memory_error_information>: integer
1f	error_operation of <dmi b64_bit_memory_error_information>: integer
1f	error_resolution of <dmi b32_bit_memory_error_information>: integer
1f	error_resolution of <dmi b64_bit_memory_error_information>: integer
1f	error_status of <dmi memory_module_information>: integer
1f	error_type of <dmi b32_bit_memory_error_information>: integer
1f	error_type of <dmi b64_bit_memory_error_information>: integer
10	escape of <string>: string
1f	established of <tcp state>: boolean
1f	evaluated of <site>: boolean
bf	evaluation of <license>: boolean
a0	evaluation period of <bes property>: time interval
1f	evaluationcycle of <client>: evaluation cycle
10	event id of <event log record>: integer
10	event log <string>: event log
10	event log event type <integer>: event log event type
10	event task trigger type: task trigger type
10	event type of <event log record>: event log event type
10	everyone group: security account
10	exceptions allowed of <firewall profile>: boolean
10	excluded interfaces of <firewall profile>: string
d	exec shield of <process>: boolean
10	exec task action type: task action type
d	exec time of <process>: time interval
10	executable file format of <file>: string
d	execute of <mode_mask>: boolean
10	execute permission of <access control entry>: boolean
10	execute permission of <network share>: boolean
10	execution time limit of <task settings>: time interval
10	execution time limit of <task trigger>: time interval
1f	executions <string>: execution
1f	exit code of <action>: integer
a0	exit code of <bes action result>: integer
10	expand environment string of <string>: string
10	expand x32 environment string of <string>: string
10	expand x64 environment string of <string>: string
1f	expiration date of <action lock state>: time
bf	expiration date of <bes product>: date
bf	expiration date of <license>: time
a0	expiration flag of <bes action>: boolean
bf	expiration state of <license>: string
a0	expiration time of <bes action>: time
2	expiration time of <route>: time
a0	explicit owner set of <bes site>: bes user set
a0	explicit owners of <bes site>: bes user
a0	explicit reader set of <bes site>: bes user set
a0	explicit readers of <bes site>: bes user
a0	explicit writer set of <bes site>: bes user set
a0	explicit writers of <bes site>: bes user
18	explorer service: service
a0	exponential fit of <statistical bin>: exponential projection
12	extended family of <processor>: integer
1f	extended feature mask of <processor>: integer
12	extended model of <processor>: integer
a0	extension flag of <bes computer>: boolean
2	extensions <string>: enableable_file
2	extensions folder of <domain>: folder
2	extensions folder: folder
2	extensions: enableable_file
10	external port of <port mapping>: integer
a0	external site flag of <bes site>: boolean
1f	external_clock of <dmi processor_information>: integer
1f	external_connector_type of <dmi port_connector_information>: integer
1f	external_reference_designator of <dmi port_connector_information>: string
a2	extrapolation <time> of <exponential projection>: floating point
a2	extrapolation <time> of <linear projection>: floating point
bf	extremas of <date>: ( date, date )
bf	extremas of <day of month>: ( day of month, day of month )
bf	extremas of <day of year>: ( day of year, day of year )
9	extremas of <debian package upstream version>: ( debian package upstream version, debian package upstream version )
9	extremas of <debian package version epoch>: ( debian package version epoch, debian package version epoch )
9	extremas of <debian package version revision>: ( debian package version revision, debian package version revision )
9	extremas of <debian package version>: ( debian package version, debian package version )
bf	extremas of <floating point>: ( floating point, floating point )
bf	extremas of <hertz>: ( hertz, hertz )
bf	extremas of <integer>: ( integer, integer )
bf	extremas of <ipv4 address>: ( ipv4 address, ipv4 address )
bf	extremas of <ipv4or6 address>: ( ipv4or6 address, ipv4or6 address )
bf	extremas of <ipv6 address>: ( ipv6 address, ipv6 address )
1a	extremas of <large integer>: ( large integer, large integer )
bf	extremas of <month and year>: ( month and year, month and year )
bf	extremas of <month>: ( month, month )
bf	extremas of <number of months>: ( number of months, number of months )
a2	extremas of <rate>: ( rate, rate )
4	extremas of <rpm package release>: ( rpm package release, rpm package release )
4	extremas of <rpm package version record>: ( rpm package version record, rpm package version record )
4	extremas of <rpm package version>: ( rpm package version, rpm package version )
4	extremas of <short rpm package version record>: ( short rpm package version record, short rpm package version record )
bf	extremas of <site version list>: ( site version list, site version list )
bf	extremas of <time interval>: ( time interval, time interval )
bf	extremas of <time of day>: ( time of day, time of day )
bf	extremas of <time>: ( time, time )
1a	extremas of <uinteger>: ( uinteger, uinteger )
1f	extremas of <uuid>: ( uuid, uuid )
bf	extremas of <version>: ( version, version )
bf	extremas of <year>: ( year, year )
d	f00f bug of <processor>: boolean
a0	failure rate of <statistical bin>: floating point
d	fallback image <integer> of <grub config file>: grub image choice
d	fallback images of <grub config file>: grub image choice
bf	false: boolean
2	family name of <network interface>: string
1f	family name of <processor>: string
10	family name of <winrt package id>: string
1f	family of <dmi system_information>: string
1f	family of <network interface>: integer
1f	family of <processor>: integer
2	fast scsi of <scsibus>: boolean
2	favorites folder of <domain>: folder
2	favorites folder: folder
d	fdiv bug of <processor>: boolean
1f	feature mask of <processor>: integer
1f	feature_flags of <dmi base_board_information>: integer
bf	february <integer> of <integer>: date
bf	february <integer>: day of year
bf	february of <integer>: month and year
bf	february: month
a0	field <string> of <bes fixlet>: bes fixlet field
a0	fields of <bes fixlet>: bes fixlet field
a0	fields of <bes unmanagedasset>: bes unmanagedasset field
d	fifo file <filesystem object>: fifo file
d	fifo file <string> of <folder>: fifo file
d	fifo file <string>: fifo file
d	fifo file <symlink>: fifo file
d	fifo files of <folder>: fifo file
1d	file <binary_string> of <encoding>: file
1f	file <binary_string> of <folder>: file
1f	file <binary_string>: file
1f	file <string> of <encoding>: file
1f	file <string> of <folder>: file
1f	file <string>: file
d	file <symlink>: file
d	file count of <filesystem>: integer
2	file count of <volume>: integer
10	file extension <string> of <registry>: registry key
1d	file of <service>: file
2	file signature <string>: file signature
10	file system type of <drive>: string
10	file type <string> of <registry>: registry key
2	file type <string>: file type
10	file version of <file>: version
10	file_and_print firewall service type: firewall service type
10	file_supports_encryption of <drive>: boolean
10	file_supports_object_ids of <drive>: boolean
10	file_supports_reparse_points of <drive>: boolean
10	file_supports_sparse_files of <drive>: boolean
10	file_volume_quotas of <drive>: boolean
2	files ending in <string> of <folder>: file
1f	files of <folder>: file
2	filesystem <integer>: volume
d	filesystem <string>: filesystem
d	filesystem of <device file>: filesystem
d	filesystem of <fifo file>: filesystem
d	filesystem of <file>: filesystem
2	filesystem of <file>: volume
d	filesystem of <folder>: filesystem
2	filesystem of <folder>: volume
d	filesystem of <socket file>: filesystem
d	filesystem of <symlink>: filesystem
d	filesystem type of <filesystem>: string
2	filesystems <string>: volume
d	filesystems: filesystem
2	filesystems: volume
a0	filter set of <bes domain>: bes filter set
a0	filterable flag of <bes unmanagedasset field>: boolean
a0	filters of <bes domain>: bes filter
1f	fin wait one of <tcp state>: boolean
1f	fin wait two of <tcp state>: boolean
bf	final part <time interval> of <time range>: time range
1f	find adapters <string> of <network>: network adapter
1f	find files <string> of <folder>: file
1f	find folders <string> of <folder>: folder
2	find items <string> of <folder>: filesystem object
bf	finite of <floating point>: boolean
bf	fips mode failure message of <cryptography>: string
bf	fips mode of <cryptography>: boolean
bf	fips mode of <license>: boolean
12	firewall action <integer>: firewall action
10	firewall enabled of <firewall profile>: boolean
10	firewall local policy modify state <integer>: firewall local policy modify state
10	firewall of <connection>: internet connection firewall
10	firewall profile type <integer>: firewall profile type
10	firewall scope <integer>: firewall scope
10	firewall service type <integer>: firewall service type
12	firewall: firewall
2	firewire plane of <registryroot>: registrynode
bf	first <day of week> of <month and year>: date
bf	first <integer> of <binary_string>: binary_substring
bf	first <integer> of <string>: substring
bf	first <string> of <string>: substring
1f	first active count of <action>: integer
a0	first became relevant of <bes fixlet result>: time
bd	first child of <xml dom node>: xml dom node
bf	first friday of <month and year>: date
10	first interface scheduled tasks: scheduled task
1a	first line of <file>: file line
1a	first lines <integer> of <file>: file line
bf	first matches <regular expression> of <string>: regular expression match
bf	first monday of <month and year>: date
10	first raw version block of <file>: file version block
1a	first rawline of <file>: file line
1a	first rawlines <integer> of <file>: file line
bf	first saturday of <month and year>: date
1f	first start time of <application usage summary instance>: time
1f	first start time of <application usage summary>: time
bf	first sunday of <month and year>: date
bf	first thursday of <month and year>: date
bf	first tuesday of <month and year>: date
bf	first wednesday of <month and year>: date
a0	fixlet <integer> of <bes site>: bes fixlet
a0	fixlet flag of <bes filter>: boolean
a0	fixlet flag of <bes fixlet>: boolean
a0	fixlet of <bes fixlet result>: bes fixlet
a0	fixlet set of <bes filter>: bes fixlet set
a0	fixlet set of <bes site>: bes fixlet set
a0	fixlets of <bes site>: bes fixlet
1f	fixlets of <site>: fixlet
d	flag list of <processor>: string
d	flag of <Xinetd Service>: string
2	flag of <volume>: integer
1f	flags of <dmi bios_language_information>: integer
2	flags string of <route>: string
1f	float of <sqlite column type>: boolean
bf	floating point <floating point>: floating point
bf	floating point <string>: floating point
1d	folder <binary_string> of <encoding>: folder
1f	folder <binary_string> of <folder>: folder
1f	folder <binary_string>: folder
10	folder <string> of <drive>: folder
1f	folder <string> of <encoding>: folder
1f	folder <string> of <folder>: folder
1f	folder <string>: folder
d	folder <symlink>: folder
1d	folder of <service>: folder
1f	folder of <site>: folder
2	folders ending in <string> of <folder>: folder
1f	folders of <folder>: folder
bf	following binary_string of <binary position>: binary_substring
bf	following binary_string of <binary_substring>: binary_substring
bf	following text of <string position>: substring
bf	following text of <substring>: substring
2	fonts folder of <domain>: folder
2	fonts folder: folder
10	force logoff interval of <security database>: time interval
d	foreground of <grub color pair>: grub color
1f	form_factor of <dmi memory_device>: integer
bf	format <string>: format
d	fpu exception of <processor>: boolean
d	fpu of <processor>: boolean
2	framework <string> of <domain>: folder
2	framework <string>: folder
2	framework folder of <domain>: folder
2	framework folder: folder
1f	free amount of <ram>: integer
f	free amount of <swap>: integer
d	free file count of <filesystem>: integer
d	free percent of <filesystem>: integer
2	free percent of <volume>: integer
10	free space of <drive>: integer
d	free space of <filesystem>: integer
2	free space of <volume>: integer
bf	friday: day of week
10	friendly name of <active device>: string
1f	friendly name of <network adapter>: string
10	from of <email task action>: string
10	fs_case_is_preserved of <drive>: boolean
10	fs_case_sensitive of <drive>: boolean
10	fs_file_compression of <drive>: boolean
10	fs_persistent_acls of <drive>: boolean
10	fs_unicode_stored_on_disk of <drive>: boolean
10	fs_vol_is_compressed of <drive>: boolean
d	fstype of <filesystem>: string
1f	full gateway addresses of <selected server>: ipv4or6 address
12	full name of <user>: string
10	full name of <winrt package id>: string
1f	full of <power level>: boolean
10	full wmi <string>: wmi
a0	fxf character set of <bes server>: string
1f	fxf character set of <client>: string
bf	fxf encoding concatenations <string> of <string>: string
bf	fxf encoding concatenations of <string>: string
1f	gateway address <integer> of <selected server>: ipv4or6 address
1f	gateway addresses of <selected server>: ipv4or6 address
f	gateway flag of <route>: boolean
10	gateway lists of <network adapter>: network address list
10	gateway of <network adapter>: ipv4 address
f	gateway of <route>: ipv4or6 address
2	gateway string of <route>: string
2	gateway type of <route>: string
1f	gather duration of <evaluation cycle>: time interval
1f	gather percent of <evaluation cycle>: floating point
1f	gather schedule authority of <site>: string
1f	gather schedule time interval of <site>: time interval
bf	gather url of <license>: string
10	gdi object count of <process>: integer
10	generic all permission of <access control entry>: boolean
10	generic execute permission of <access control entry>: boolean
10	generic read permission of <access control entry>: boolean
10	generic write permission of <access control entry>: boolean
a0	geometric mean of <statistical bin>: floating point
2	gestalt <string>: integer
d	gfxmenu of <grub config file>: grub file location
bf	ghz: hertz
d	gid of <filesystem object>: integer
d	gid of <symlink>: integer
a0	global catalog of <bes ldap directory>: boolean
2	global dictionary of <bundle>: dictionary
2	global state of <firewall>: string
a0	globally allowed flag of <bes webui app>: boolean
10	globally open ports of <firewall profile>: firewall open port
10	globally open ports of <firewall service>: firewall open port
a0	globally readable flag of <bes site>: boolean
a0	globally visible flag of <bes fixlet>: boolean
10	gp override firewall local policy modify state: firewall local policy modify state
10	grant type of <access control entry>: boolean
bf	greatest hz: hertz
bf	greatest integer: integer
1a	greatest large integer: large integer
bf	greatest time interval: time interval
1a	greatest uinteger: uinteger
1f	group <integer> of <site>: site group
12	group <string> of <active directory local computer>: active directory group
12	group <string> of <active directory local user>: active directory group
d	group execute of <filesystem object>: boolean
a0	group filter of <bes ldap directory>: string
a0	group flag of <bes filter>: boolean
a0	group flag of <bes fixlet>: boolean
10	group id of <task principal>: string
1f	group leader of <action>: boolean
10	group logon of <task principal>: boolean
d	group mask of <filesystem object>: integer
d	group mask of <mode>: mode_mask
a0	group member flag of <bes action>: boolean
d	group name of <filesystem object>: string
d	group name of <symlink>: string
10	group of <security descriptor>: security identifier
d	group read of <filesystem object>: boolean
d	group write of <filesystem object>: boolean
1f	group_associations <integer> of <dmi>: dmi group_associations
1f	group_associationss of <dmi>: dmi group_associations
1f	group_name of <dmi group_associations>: string
10	grouping of <firewall rule>: string
12	groups error message of <active directory local computer>: string
12	groups error message of <active directory local user>: string
12	groups of <active directory local computer>: active directory group
12	groups of <active directory local user>: active directory group
d	grub config file <string>: grub config file
d	grub config file: grub config file
10	guest privilege of <user>: boolean
10	guid of <audit policy information>: string
10	guid of <audit policy subcategory>: string
10	guid of <connection>: string
bf	h1 <string> of <html>: html
bf	h1 <string> of <string>: html
bf	h1 of <html>: html
bf	h1 of <string>: html
bf	h2 <string> of <html>: html
bf	h2 <string> of <string>: html
bf	h2 of <html>: html
bf	h2 of <string>: html
bf	h3 <string> of <html>: html
bf	h3 <string> of <string>: html
bf	h3 of <html>: html
bf	h3 of <string>: html
bf	h4 <string> of <html>: html
bf	h4 <string> of <string>: html
bf	h4 of <html>: html
bf	h4 of <string>: html
bf	h5 <string> of <html>: html
bf	h5 <string> of <string>: html
bf	h5 of <html>: html
bf	h5 of <string>: html
bf	h6 <string> of <html>: html
bf	h6 <string> of <string>: html
bf	h6 of <html>: html
bf	h6 of <string>: html
10	handle count of <process>: integer
10	hardware ids of <active device>: string
1f	hardware: hardware
1f	hardware_security <integer> of <dmi>: dmi hardware_security
1f	hardware_security_settings of <dmi hardware_security>: integer
1f	hardware_securitys of <dmi>: dmi hardware_security
10	has blank sa password of <local mssql database>: boolean
d	has extended acl of <filesystem object>: boolean
bf	head <string> of <html>: html
bf	head <string> of <string>: html
bf	head of <html>: html
bf	head of <string>: html
10	header fields of <email task action>: task named value pair
1f	headers <string> of <action>: fixlet_header
1f	headers <string> of <fixlet>: fixlet_header
1f	headers of <action>: fixlet_header
1f	headers of <fixlet>: fixlet_header
1f	height of <dmi system_enclosure_or_chassis>: integer
2	help folder of <domain>: folder
2	help folder: folder
bf	hexadecet <integer> of <ipv4or6 address>: integer
bf	hexadecet <integer> of <ipv6 address>: integer
bf	hexadecimal integer <string>: integer
1a	hexadecimal large integer <string>: large integer
1f	hexadecimal of <smbios value>: string
bf	hexadecimal string <string>: string
1a	hexadecimal uinteger <string>: uinteger
1f	hexadecimals <string> of <smbios structure>: string
2	hfs file <string> of <encoding>: file
2	hfs file <string>: file
2	hfs folder <string> of <encoding>: folder
2	hfs folder <string>: folder
2	hfs item <string>: filesystem object
2	hfs path of <filesystem object>: string
2	hfs relative item <string> of <folder>: filesystem object
a0	hidden bes action set: bes action set
a0	hidden bes actions: bes action
a0	hidden flag of <bes action>: boolean
10	hidden of <filesystem object>: boolean
10	hidden of <task settings>: boolean
d	hiddenmenu of <grub config file>: boolean
10	high priority: priority class
10	highest runlevel of <task principal>: boolean
d	highlight of <grub color scheme>: grub color pair
d	hlt bug of <processor>: boolean
10	home directory drive of <user>: string
12	home directory folder of <user>: folder
12	home directory of <user>: string
10	home directory required flag of <user>: boolean
f	host flag of <route>: boolean
1f	host name of <root server>: string
d	host name: string
a0	host of <bes ldap directory server>: string
a0	hostname of <bes computer>: string
1f	hostname: string
bf	hour: time interval
bf	hour_of_day of <time of day with time zone>: integer
bf	hour_of_day of <time of day>: integer
bf	hr <string>: html
bf	hr: html
bf	html <string> of <html>: html
bf	html <string> of <string>: html
bf	html <string>: html
bf	html concatenations <string> of <html>: html
bf	html concatenations of <html>: html
bf	html of <html>: html
bf	html of <string>: html
bf	html tag <( string, html )>: html
bf	html tag <( string, html attribute list )>: html
bf	html tag <( string, html attribute list, html )>: html
bf	html tag <( string, html attribute list, string )>: html
bf	html tag <( string, string )>: html
bf	html tag <string> of <html>: html
bf	html tag <string> of <string>: html
10	hyperthreading capable: boolean
10	hyperthreading enabled: boolean
1f	hypervisor of <operating system>: string
bf	hz: hertz
1f	i2c_slave_address of <dmi ipmi_device_information>: integer
10	ia64 of <operating system>: boolean
12	ibss of <wifi network>: boolean
10	icmp settings of <firewall profile>: firewall icmp settings
10	icmp types_and_codes string of <firewall rule>: string
10	icon index of <file shortcut>: integer
10	icon pathname of <file shortcut>: string
d	id of <Xinetd Service>: string
1f	id of <action>: integer
a0	id of <bes action>: integer
a0	id of <bes activation>: integer
a0	id of <bes baseline component>: integer
a0	id of <bes computer group>: integer
a0	id of <bes computer>: integer
a0	id of <bes domain>: string
a0	id of <bes filter>: integer
a0	id of <bes fixlet>: integer
a0	id of <bes ldap directory>: integer
a0	id of <bes property>: ( integer, integer, integer )
a0	id of <bes site file>: integer
a0	id of <bes site>: integer
a0	id of <bes unmanagedasset>: integer
a0	id of <bes user>: integer
10	id of <file version block>: string
1f	id of <fixlet>: integer
1f	id of <process>: integer
1f	id of <root server>: integer
1f	id of <site group>: integer
10	id of <task action>: string
10	id of <task network settings>: string
10	id of <task principal>: string
10	id of <task trigger>: string
1f	id of <user>: integer
10	id of <winrt package>: winrt package id
10	identifier of <metabase value>: metabase identifier
1f	identity of <execution>: string
10	idle duration of <task idle settings>: time interval
10	idle priority: priority class
10	idle setting of <task settings>: task idle settings
12	idle state: power state
10	idle task trigger type: task trigger type
2	ifref flag of <route>: boolean
2	ifscope flag of <route>: boolean
10	ignore new instance of <task settings>: boolean
1f	image file of <process>: file
1f	image path of <application usage summary instance>: string
1d	image path of <service>: string
1f	in agent context: boolean
a0	in console context: boolean
1f	in plugin portal context: boolean
1f	in proxy agent context: boolean
a0	in web reports context: boolean
1f	inactive <integer> of <dmi>: dmi inactive
1f	inactives of <dmi>: dmi inactive
10	inbound blocked firewall local policy modify state: firewall local policy modify state
10	inbound connections allowed of <firewall profile>: boolean
10	inbound of <firewall rule>: boolean
a0	include in relevance flag of <bes baseline component>: boolean
d	index of <grub image choice>: integer
d	index of <processor>: integer
bf	index of <tuple item>: integer
bf	index type of <property>: type
1f	indices of <sqlite table>: string
bf	inexact of <floating point>: boolean
bf	infinite of <floating point>: boolean
1f	info of <client>: string
2	info of <component>: string
10	information event log event type: event log event type
10	inherit attribute of <metabase value>: boolean
10	inherit only of <access control entry>: boolean
10	inheritance of <access control entry>: integer
10	inherited of <access control entry>: boolean
2	init date of <volume>: time
bf	initial part <time interval> of <time range>: time range
d	initrd of <grub bootable image>: grub file location
1f	input_current_probe_handle of <dmi system_power_supply>: integer
1f	input_voltage_probe_handle of <dmi system_power_supply>: integer
bf	ins <string> of <html>: html
bf	ins <string> of <string>: html
bf	ins of <html>: html
bf	ins of <string>: html
10	insert path attribute of <metabase value>: boolean
10	inspectability of <application>: boolean
10	install folder <integer>: folder
10	install state of <winrt package user information>: winrt enumeration
1f	installable_languages of <dmi bios_language_information>: integer
4	installed <string> of <rpmdatabase>: boolean
4	installed files of <package>: capability
10	installed path of <winrt package>: folder
9	installed version of <debian base package>: debianpkg version
1f	installed_size of <dmi cache_information>: integer
1f	installed_size of <dmi memory_module_information>: integer
1f	instance data of <cloud provider>: instance data
10	instance guid of <running task>: string
10	instance name of <local mssql database>: string
1f	instances of <application usage summary>: application usage summary instance
2	integer <integer> of <array>: integer
bf	integer <integer>: integer
2	integer <string> of <dictionary>: integer
2	integer <string> of <preference>: integer
bf	integer <string>: integer
bf	integer ceiling of <floating point>: integer
bf	integer floor of <floating point>: integer
2	integer of <osxvalue>: integer
1f	integer of <sqlite column type>: boolean
10	integer value <integer> of <wmi select>: integer
1f	integer values <string> of <smbios structure>: smbios value
10	integer values of <wmi select>: integer
1f	integers <string> of <smbios structure>: integer
bf	integers in <( integer, integer )>: integer
bf	integers in <( integer, integer, integer )>: integer
bf	integers to <integer>: integer
10	interactive group: security account
10	interactive token logon of <task principal>: boolean
10	interactive token password logon of <task principal>: boolean
10	interdomain trust account flag of <user>: boolean
1f	interface <integer> of <network>: network interface
1f	interface of <dmi built_in_pointing_device>: integer
f	interface of <route>: string
10	interface types string of <firewall rule>: string
1f	interface_type of <dmi ipmi_device_information>: integer
10	interfaces of <firewall rule>: string
2	interfaces of <network adapter>: network interface
1f	interfaces of <network>: network interface
1f	interleave_position of <dmi memory_device_mapped_address>: integer
1f	interleaved_data_depth of <dmi memory_device_mapped_address>: integer
10	internal port of <port mapping>: integer
1f	internal_connector_type of <dmi port_connector_information>: integer
1f	internal_reference_designator of <dmi port_connector_information>: string
10	internet connection firewall of <network adapter>: internet connection firewall
2	internet plugins folder of <domain>: folder
2	internet plugins folder: folder
10	internet protocol <integer>: internet protocol
a0	intersections of <bes action set>: bes action set
a0	intersections of <bes computer group set>: bes computer group set
a0	intersections of <bes computer set>: bes computer set
a0	intersections of <bes domain set>: bes domain set
a0	intersections of <bes filter set>: bes filter set
a0	intersections of <bes fixlet set>: bes fixlet set
a0	intersections of <bes ldap directory set>: bes ldap directory set
a0	intersections of <bes property set>: bes property set
a0	intersections of <bes role set>: bes role set
a0	intersections of <bes site file set>: bes site file set
a0	intersections of <bes site set>: bes site set
a0	intersections of <bes unmanagedasset set>: bes unmanagedasset set
a0	intersections of <bes user set>: bes user set
a0	intersections of <bes webui app set>: bes webui app set
a0	intersections of <bes wizard set>: bes wizard set
bf	intersections of <integer set>: integer set
bf	intersections of <string set>: string set
10	interval of <task repetition pattern>: time interval
bf	invalid after of <x509 certificate>: time
bf	invalid before of <x509 certificate>: time
bf	invalid of <floating point>: boolean
12	invalid state: power state
10	io other count of <process>: integer
10	io other size of <process>: integer
10	io read count of <process>: integer
10	io read size of <process>: integer
10	io write count of <process>: integer
10	io write size of <process>: integer
2	iokit registry: registryroot
1f	ip address of <selected server>: ipv4or6 address
a0	ip addresses of <bes computer>: ipv4or6 address
2	ip family of <route>: string
1f	ip interface <integer> of <network>: network ip interface
2	ip interfaces of <network adapter>: network ip interface
1f	ip interfaces of <network>: network ip interface
bf	ip version <integer>: ip version
10	ip version of <firewall authorized application>: ip version
10	ip version of <firewall open port>: ip version
10	ip version of <firewall service>: ip version
bf	ip version of <ipv4or6 address>: ip version
1f	ipmi_device_information <integer> of <dmi>: dmi ipmi_device_information
1f	ipmi_device_informations of <dmi>: dmi ipmi_device_information
1f	ipmi_specification_revision of <dmi ipmi_device_information>: integer
bf	ipv4 address <string>: ipv4 address
10	ipv4 interface <integer> of <network adapter>: network adapter interface
10	ipv4 interface <integer> of <network>: network adapter interface
1f	ipv4 interfaces of <network adapter>: network adapter interface
1f	ipv4 interfaces of <network>: network adapter interface
bf	ipv4 part of <ipv4or6 address>: ipv4 address
bf	ipv4 part of <ipv6 address>: ipv4 address
f	ipv4 routing table: routing table
bf	ipv4: ip version
bf	ipv4or6 address <string>: ipv4or6 address
10	ipv4or6 dns servers of <network adapter>: ipv4or6 address
10	ipv4or6 interface <integer> of <network adapter>: network adapter interface
10	ipv4or6 interface <integer> of <network>: network adapter interface
1f	ipv4or6 interfaces of <network adapter>: network adapter interface
1f	ipv4or6 interfaces of <network>: network adapter interface
bf	ipv6 address <string>: ipv6 address
10	ipv6 addresses of <network adapter>: ipv6 address
10	ipv6 dns servers of <network adapter>: ipv6 address
10	ipv6 interface <integer> of <network adapter>: network adapter interface
10	ipv6 interface <integer> of <network>: network adapter interface
1f	ipv6 interfaces of <network adapter>: network adapter interface
1f	ipv6 interfaces of <network>: network adapter interface
2	ipv6 routing table: routing table
bf	ipv6: ip version
d	irtt of <route>: integer
2	isochronous of <usb>: boolean
2	iss download folder of <domain>: folder
2	iss download folder: folder
a0	issued action set of <bes user>: bes action set
a0	issued actions of <bes user>: bes action
a0	issued computer group set of <bes user>: bes computer group set
a0	issued computer groups of <bes user>: bes computer group
a0	issued fixlet set of <bes user>: bes fixlet set
a0	issued fixlets of <bes user>: bes fixlet
a0	issuer of <bes action>: bes user
a0	issuer of <bes activation>: bes user
a0	issuer of <bes computer group>: bes user
a0	issuer of <bes fixlet>: bes user
bf	issuer of <x509 certificate>: string
bf	italic <string> of <html>: html
bf	italic <string> of <string>: html
bf	italic of <html>: html
bf	italic of <string>: html
2	item <string> of <folder>: filesystem object
2	item <string>: filesystem object
1f	item_handle of <dmi group_associations>: integer
1f	item_type of <dmi group_associations>: integer
2	items ending in <string> of <folder>: filesystem object
2	items of <folder>: filesystem object
bf	january <integer> of <integer>: date
bf	january <integer>: day of year
bf	january of <integer>: month and year
bf	january: month
a0	javascript arrays <string> of <boolean>: html
a0	javascript arrays <string> of <integer>: html
a0	javascript arrays <string> of <statistical bin>: html
a0	javascript arrays <string> of <string>: html
a0	join by intersection flag of <bes filter>: boolean
1f	json of <file>: json value
1f	json of <instance data>: json value
bf	json of <string>: json value
bf	july <integer> of <integer>: date
bf	july <integer>: day of year
bf	july of <integer>: month and year
bf	july: month
bf	june <integer> of <integer>: date
bf	june <integer>: day of year
bf	june of <integer>: month and year
bf	june: month
bf	kbd <string> of <html>: html
bf	kbd <string> of <string>: html
bf	kbd of <html>: html
bf	kbd of <string>: html
a0	keep statistics flag of <bes property>: boolean
2	kernel extensions folder of <domain>: folder
2	kernel extensions folder: folder
d	kernel of <grub bootable image>: grub kernel
10	kernel time of <process>: time interval
1f	key <string> of <file section>: string
1f	key <string> of <file>: string
bf	key <string> of <json value>: json key
10	key <string> of <metabase key>: metabase key
10	key <string> of <metabase>: metabase key
14	key <string> of <plugin store>: plugin store key
10	key <string> of <registry key>: registry key
10	key <string> of <registry>: registry key
2	key of <dictionaryentry>: string
2	key of <user attribute>: string
2	keyboard type: integer
2	keys of <dictionary>: string
1f	keys of <instance data>: json key
bf	keys of <json value>: json key
10	keys of <metabase key>: metabase key
10	keys of <metabase>: metabase key
14	keys of <plugin store>: plugin store key
10	keys of <registry key>: registry key
bf	khz: hertz
a0	kurtosis of <statistical bin>: floating point
1f	l1_cache_handle of <dmi processor_information>: integer
1f	l2_cache_handle of <dmi processor_information>: integer
1f	l3_cache_handle of <dmi processor_information>: integer
10	language of <file version block>: string
1a	large integer <integer>: large integer
1a	large integer <string>: large integer
bf	last <integer> of <binary_string>: binary_substring
bf	last <integer> of <string>: substring
bf	last <string> of <string>: substring
1f	last ack of <tcp state>: boolean
1f	last active line number of <action>: integer
1f	last active time of <action>: time
a0	last became nonrelevant of <bes fixlet result>: time
a0	last became relevant of <bes fixlet result>: time
1f	last change time of <action>: time
bd	last child of <xml dom node>: xml dom node
1f	last command time of <client>: time
1f	last gather time of <site>: time
1a	last line of <file>: file line
1a	last lines <integer> of <file>: file line
a0	last login time of <bes user>: time
10	last logoff of <user>: time
10	last logon of <user>: time
12	last monitor interval in <power state> of <power history>: monitor power interval
12	last monitor interval in monitor off state of <power history>: monitor power interval
12	last monitor interval in monitor on state of <power history>: monitor power interval
1a	last rawline of <file>: file line
1a	last rawlines <integer> of <file>: file line
a0	last refresh time of <bes computer group>: time
1f	last relay select time: time
a0	last report time of <bes computer>: time
1f	last report time of <client>: time
10	last run time of <scheduled task>: time
1f	last start time of <application usage summary instance>: time
1f	last start time of <application usage summary>: time
12	last system interval in <power state> of <power history>: system power interval
12	last system interval in active state of <power history>: system power interval
12	last system interval in idle state of <power history>: system power interval
12	last system interval in logged off state of <power history>: system power interval
12	last system interval in off state of <power history>: system power interval
12	last system interval in standby state of <power history>: system power interval
10	last task result of <scheduled task>: integer
1f	last time of <analysis>: time
1f	last time seen of <application usage summary instance>: time
1f	last time seen of <application usage summary>: time
10	last write time of <registry key>: time
a0	ldap directory of <bes user>: bes ldap directory
bf	leap of <year>: boolean
10	lease expires of <network adapter>: time
10	lease obtained of <network adapter>: time
bf	least hz: hertz
bf	least integer: integer
1a	least large integer: large integer
bf	least significant one bit of <bit set>: integer
bf	least time interval: time interval
1a	least uinteger: uinteger
bf	left operand type of <binary operator>: type
bf	left shift <integer> of <bit set>: bit set
bf	legacy of <bes product>: boolean
bf	length of <binary_string>: integer
2	length of <datafork>: integer
1f	length of <dmi additional_information>: integer
1f	length of <dmi b32_bit_memory_error_information>: integer
1f	length of <dmi b64_bit_memory_error_information>: integer
1f	length of <dmi base_board_information>: integer
1f	length of <dmi bios_information>: integer
1f	length of <dmi bios_language_information>: integer
1f	length of <dmi built_in_pointing_device>: integer
1f	length of <dmi cache_information>: integer
1f	length of <dmi cooling_device>: integer
1f	length of <dmi electrical_current_probe>: integer
1f	length of <dmi end_of_table>: integer
1f	length of <dmi group_associations>: integer
1f	length of <dmi hardware_security>: integer
1f	length of <dmi inactive>: integer
1f	length of <dmi ipmi_device_information>: integer
1f	length of <dmi management_device>: integer
1f	length of <dmi management_device_component>: integer
1f	length of <dmi management_device_threshold_data>: integer
1f	length of <dmi memory_array_mapped_address>: integer
1f	length of <dmi memory_channel>: integer
1f	length of <dmi memory_controller_information>: integer
1f	length of <dmi memory_device>: integer
1f	length of <dmi memory_device_mapped_address>: integer
1f	length of <dmi memory_module_information>: integer
1f	length of <dmi on_board_devices_information>: integer
1f	length of <dmi onboard_devices_extended_information>: integer
1f	length of <dmi out_of_band_remote_access>: integer
1f	length of <dmi physical_memory_array>: integer
1f	length of <dmi port_connector_information>: integer
1f	length of <dmi portable_battery>: integer
1f	length of <dmi processor_information>: integer
1f	length of <dmi system_boot_information>: integer
1f	length of <dmi system_enclosure_or_chassis>: integer
1f	length of <dmi system_information>: integer
1f	length of <dmi system_power_controls>: integer
1f	length of <dmi system_power_supply>: integer
1f	length of <dmi system_reset>: integer
1f	length of <dmi system_slots>: integer
1f	length of <dmi temperature_probe>: integer
1f	length of <dmi voltage_probe>: integer
10	length of <event log record>: integer
2	length of <file>: integer
bf	length of <month and year>: time interval
2	length of <resfork>: integer
bf	length of <rope>: integer
1f	length of <smbios structure>: integer
a0	length of <statistical bin>: time interval
bf	length of <string>: integer
bf	length of <time range>: time interval
bf	length of <year>: time interval
bf	less significance <integer> of <floating point>: floating point
bf	li <string> of <html>: html
bf	li <string> of <string>: html
bf	li of <html>: html
bf	li of <string>: html
a0	license type of <bes computer>: string
1f	line <integer> of <file>: file line
a0	line number of <bes action result>: integer
1f	line number of <file line>: integer
a0	linear fit of <statistical bin>: linear projection
1f	lines containing <string> of <file>: file line
1f	lines of <file>: file line
1f	lines starting with <string> of <file>: file line
a0	link <html> of <bes action>: html
a0	link <html> of <bes computer>: html
a0	link <html> of <bes domain>: html
a0	link <html> of <bes fixlet>: html
a0	link <html> of <bes unmanagedasset>: html
a0	link <html> of <bes user>: html
a0	link <html> of <bes wizard>: html
a0	link <string> of <bes action>: html
a0	link <string> of <bes computer>: html
a0	link <string> of <bes domain>: html
a0	link <string> of <bes fixlet>: html
a0	link <string> of <bes unmanagedasset>: html
a0	link <string> of <bes user>: html
a0	link <string> of <bes wizard>: html
bf	link <string> of <html>: html
bf	link <string> of <string>: html
d	link count of <filesystem object>: integer
d	link count of <symlink>: integer
a0	link href of <bes action>: string
a0	link href of <bes computer>: string
a0	link href of <bes domain>: string
a0	link href of <bes fixlet>: string
a0	link href of <bes unmanagedasset>: string
a0	link href of <bes user>: string
a0	link href of <bes wizard>: string
2	link interface <integer> of <network>: network link interface
2	link interfaces of <network adapter>: network link interface
2	link interfaces of <network>: network link interface
a0	link of <bes action>: html
a0	link of <bes computer>: html
a0	link of <bes domain>: html
a0	link of <bes fixlet>: html
a0	link of <bes unmanagedasset>: html
a0	link of <bes user>: html
a0	link of <bes wizard>: html
bf	link of <html>: html
bf	link of <string>: html
10	link speed of <network adapter>: integer
1a	linux of <operating system>: boolean
10	list permission of <access control entry>: boolean
1f	listening of <tcp state>: boolean
1f	little endian of <operating system>: boolean
2	llinfo flag of <route>: boolean
1f	local address of <socket>: ipv4or6 address
10	local addresses string of <firewall rule>: string
10	local administrator: boolean
1f	local character set of <client>: string
12	local computer of <active directory server>: active directory local computer
2	local dictionary of <bundle>: dictionary
2	local domain: domain
bf	local encoding concatenations <string> of <string>: string
bf	local encoding concatenations of <string>: string
2	local flag of <route>: boolean
12	local group <string> of <active directory server>: active directory group
10	local group <string>: local group
10	local groups: local group
10	local mssql database <string>: local mssql database
10	local mssql databases: local mssql database
10	local policy modify state of <firewall>: firewall local policy modify state
10	local policy of <firewall>: firewall policy
1f	local port of <socket>: integer
10	local ports string of <firewall rule>: string
10	local service group: security account
10	local subnet firewall scope: firewall scope
bf	local time <string>: time
bf	local time zone: time zone
12	local user <string> of <active directory server>: active directory local user
12	local user <string>: user
d	local users <string>: user
12	local users of <active directory server>: active directory local user
1f	local users: user
2	locales folder of <domain>: folder
2	locales folder: folder
a0	locally visible flag of <bes fixlet>: boolean
10	location information of <active device>: string
2	location manager modules folder of <domain>: folder
2	location manager modules folder: folder
2	location manager preferences folder of <domain>: folder
2	location manager preferences folder: folder
1f	location of <dmi physical_memory_array>: integer
1f	location of <dmi portable_battery>: string
1f	location of <dmi system_power_supply>: string
2	location of <filesystem object>: folder
1d	location of <filesystem object>: string
d	location of <grub kernel>: grub file location
d	location of <symlink>: string
1f	location_and_status of <dmi electrical_current_probe>: integer
1f	location_and_status of <dmi temperature_probe>: integer
1f	location_and_status of <dmi voltage_probe>: integer
1f	location_in_chassis of <dmi base_board_information>: string
2	locations folder of <domain>: folder
2	locations folder: folder
1f	lock string of <action lock state>: string
1f	locked content of <file>: file content
a0	locked flag of <bes computer>: boolean
1f	locked key <string> of <file>: string
1f	locked line <integer> of <file>: file line
1f	locked lines containing <string> of <file>: file line
1f	locked lines of <file>: file line
1f	locked lines starting with <string> of <file>: file line
1f	locked of <action lock state>: boolean
2	locked of <file>: boolean
10	locked out flag of <user>: boolean
1f	locked rawline <integer> of <file>: file line
1f	locked rawlines containing <string> of <file>: file line
1f	locked rawlines of <file>: file line
1f	locked rawlines starting with <string> of <file>: file line
1f	locked section <string> of <file>: file section
a0	logarithm kurtosis of <statistical bin>: floating point
a0	logarithm skewness of <statistical bin>: floating point
a0	logarithm standard deviation of <statistical bin>: floating point
a0	logarithm variance of <statistical bin>: floating point
12	logged off state: power state
12	logged on group <string> of <active directory server>: active directory group
12	logged on user <string> of <active directory server>: active directory local user
12	logged on user of <user>: logged on user
12	logged on users of <active directory server>: active directory local user
1f	logged on users: logged on user
10	logical processor count: integer
2	logical ram: integer
10	login account of <service>: string
10	login mode of <local mssql database>: integer
a0	login user of <bes ldap directory>: string
d	loginuid of <process>: integer
10	logon count of <user>: integer
10	logon logoff category of <audit policy>: audit policy category
10	logon script of <user>: string
10	logon server of <user>: string
10	logon task trigger type: task trigger type
4	long form of <short rpm package version record>: rpm package version record
2	long name of <client process owner>: string
1f	loopback of <network adapter interface>: boolean
1f	loopback of <network adapter>: boolean
1f	loopback of <network ip interface>: boolean
1f	low of <power level>: boolean
bf	lower bound of <integer range>: integer
1f	lower_threshold_critical of <dmi management_device_threshold_data>: integer
1f	lower_threshold_non_critical of <dmi management_device_threshold_data>: integer
1f	lower_threshold_non_recoverable of <dmi management_device_threshold_data>: integer
10	lua runlevel of <task principal>: boolean
1f	mac address of <network adapter interface>: string
1f	mac address of <network adapter>: string
f	mac address of <network ip interface>: string
2	mac address of <network link interface>: string
1f	mac of <operating system>: boolean
2	machine name: string
1f	machine of <operating system>: string
2	machine type: integer
2	macos read me folder of <domain>: folder
2	macos read me folder: folder
2	main gather service: nothing
1d	main gather service: service
1f	main processor: processor
d	major of <device file>: integer
bf	major revision of <version>: integer
1f	major version of <operating system>: integer
2	maker of <component>: string
a0	management extensions of <bes computer>: bes computer
a0	management rights flag of <bes action>: boolean
1f	management_device <integer> of <dmi>: dmi management_device
1f	management_device_component <integer> of <dmi>: dmi management_device_component
1f	management_device_components of <dmi>: dmi management_device_component
1f	management_device_handle of <dmi management_device_component>: integer
1f	management_device_threshold_data <integer> of <dmi>: dmi management_device_threshold_data
1f	management_device_threshold_datas of <dmi>: dmi management_device_threshold_data
1f	management_devices of <dmi>: dmi management_device
a0	manual flag of <bes computer group>: boolean
1f	manual group <string> of <client>: manual group
1f	manual groups of <client>: manual group
1f	manufacture_date of <dmi portable_battery>: string
10	manufacturer of <active device>: string
1f	manufacturer of <dmi base_board_information>: string
1f	manufacturer of <dmi memory_device>: string
1f	manufacturer of <dmi portable_battery>: string
1f	manufacturer of <dmi system_enclosure_or_chassis>: string
1f	manufacturer of <dmi system_information>: string
1f	manufacturer of <dmi system_power_supply>: string
1f	manufacturer_name of <dmi out_of_band_remote_access>: string
bf	march <integer> of <integer>: date
bf	march <integer>: day of year
bf	march of <integer>: month and year
bf	march: month
f	mask of <route>: ipv4or6 address
a0	master flag of <bes role>: boolean
a0	master flag of <bes user>: boolean
a0	master site flag of <bes fixlet>: boolean
a0	master site flag of <bes site>: boolean
1f	masthead of <site>: file
a0	masthead operator name of <bes user>: string
bf	matches <regular expression> of <string>: regular expression match
1f	max_power_capacity of <dmi system_power_supply>: integer
1f	max_speed of <dmi processor_information>: integer
bf	maxima of <date>: date
bf	maxima of <day of month>: day of month
bf	maxima of <day of year>: day of year
9	maxima of <debian package upstream version>: debian package upstream version
9	maxima of <debian package version epoch>: debian package version epoch
9	maxima of <debian package version revision>: debian package version revision
9	maxima of <debian package version>: debian package version
bf	maxima of <floating point>: floating point
bf	maxima of <hertz>: hertz
bf	maxima of <integer>: integer
bf	maxima of <ipv4 address>: ipv4 address
bf	maxima of <ipv4or6 address>: ipv4or6 address
bf	maxima of <ipv6 address>: ipv6 address
1a	maxima of <large integer>: large integer
bf	maxima of <month and year>: month and year
bf	maxima of <month>: month
bf	maxima of <number of months>: number of months
a2	maxima of <rate>: rate
4	maxima of <rpm package release>: rpm package release
4	maxima of <rpm package version record>: rpm package version record
4	maxima of <rpm package version>: rpm package version
4	maxima of <short rpm package version record>: short rpm package version record
bf	maxima of <site version list>: site version list
bf	maxima of <time interval>: time interval
bf	maxima of <time of day>: time of day
bf	maxima of <time>: time
1a	maxima of <uinteger>: uinteger
1f	maxima of <uuid>: uuid
bf	maxima of <version>: version
bf	maxima of <year>: year
10	maximum allowed permission of <access control entry>: boolean
1f	maximum duration of <evaluation cycle>: time interval
1f	maximum of <evaluation cycle>: integer
10	maximum password age of <security database>: time interval
bf	maximum seat count of <license>: integer
a0	maximum single computer total of <statistical bin>: floating point
10	maximum storage of <user>: integer
10	maximum transmission unit of <network adapter>: integer
a0	maximum value of <statistical bin>: floating point
1f	maximum_cache_size of <dmi cache_information>: integer
1f	maximum_capacity of <dmi physical_memory_array>: integer
1f	maximum_channel_load of <dmi memory_channel>: integer
1f	maximum_error_in_battery_data of <dmi portable_battery>: integer
1f	maximum_memory_module_size of <dmi memory_controller_information>: integer
1f	maximum_value of <dmi electrical_current_probe>: integer
1f	maximum_value of <dmi temperature_probe>: integer
1f	maximum_value of <dmi voltage_probe>: integer
bf	may <integer> of <integer>: date
bf	may <integer>: day of year
bf	may of <integer>: month and year
bf	may: month
1f	md5 of <file>: string
bf	md5 of <string>: string
a0	mean computer count of <statistical bin>: floating point
a0	mean failing computer count of <statistical bin>: floating point
a0	mean logarithm of <statistical bin>: floating point
a0	mean nonzero value count of <statistical bin>: floating point
a0	mean of <statistical bin>: floating point
a0	mean sample interval of <statistical bin>: time interval
a0	mean sample rate of <statistical bin>: rate
a0	mean successful computer count of <statistical bin>: floating point
a0	mean total of <statistical bin>: floating point
a0	mean value count of <statistical bin>: floating point
a0	mean zero value count of <statistical bin>: floating point
bf	means of <floating point>: floating point
bf	means of <integer>: floating point
10	media type <integer>: media type
10	media type bridge: media type
10	media type direct: media type
10	media type isdn: media type
10	media type lan: media type
10	media type of <connection>: media type
10	media type phone: media type
10	media type pppoe: media type
10	media type shared access host lan: media type
10	media type shared access host ras: media type
10	media type tunnel: media type
a0	member action set of <bes action>: bes action set
a0	member actions of <bes action>: bes action
1f	member of <manual group>: boolean
1f	member of <server based group>: boolean
1f	member of <site group>: boolean
a0	member set of <bes computer group>: bes computer set
a0	members of <bes computer group>: bes computer
10	members of <local group>: local group member
a0	memory usage of <bes property>: integer
1f	memory_array_error_address of <dmi b32_bit_memory_error_information>: integer
1f	memory_array_error_address of <dmi b64_bit_memory_error_information>: integer
1f	memory_array_handle of <dmi memory_array_mapped_address>: integer
1f	memory_array_handle of <dmi memory_device>: integer
1f	memory_array_mapped_address <integer> of <dmi>: dmi memory_array_mapped_address
1f	memory_array_mapped_address_handle of <dmi memory_device_mapped_address>: integer
1f	memory_array_mapped_addresss of <dmi>: dmi memory_array_mapped_address
1f	memory_channel <integer> of <dmi>: dmi memory_channel
1f	memory_channels of <dmi>: dmi memory_channel
1f	memory_controller_information <integer> of <dmi>: dmi memory_controller_information
1f	memory_controller_informations of <dmi>: dmi memory_controller_information
1f	memory_device <integer> of <dmi>: dmi memory_device
1f	memory_device_count of <dmi memory_channel>: integer
1f	memory_device_handle of <dmi memory_channel>: integer
1f	memory_device_handle of <dmi memory_device_mapped_address>: integer
1f	memory_device_load of <dmi memory_channel>: integer
1f	memory_device_mapped_address <integer> of <dmi>: dmi memory_device_mapped_address
1f	memory_device_mapped_addresss of <dmi>: dmi memory_device_mapped_address
1f	memory_devices of <dmi>: dmi memory_device
1f	memory_error_correction of <dmi physical_memory_array>: integer
1f	memory_error_information_handle of <dmi memory_device>: integer
1f	memory_error_information_handle of <dmi physical_memory_array>: integer
1f	memory_module_information <integer> of <dmi>: dmi memory_module_information
1f	memory_module_informations of <dmi>: dmi memory_module_information
1f	memory_module_voltage of <dmi memory_controller_information>: integer
1f	memory_type of <dmi memory_device>: integer
a0	menu path of <bes wizard>: string
a0	message action button flag of <bes action>: boolean
a0	message allow cancel flag of <bes action>: boolean
10	message body of <show message task action>: string
a0	message of <bes fixlet>: html
a0	message postpone delay of <bes action>: time interval
a0	message text of <bes action>: string
a0	message timeout delay of <bes action>: time interval
a0	message title of <bes action>: string
bf	meta <string> of <html>: html
bf	meta <string> of <string>: html
bf	meta of <html>: html
bf	meta of <string>: html
10	metabase: metabase
10	metric <integer> of <operating system>: integer
d	metric of <route>: integer
bf	mhz: hertz
bf	microsecond: time interval
a0	middle actions of <bes action>: bes action
bf	midnight: time of day
bf	millisecond: time interval
a0	mime field <string> of <bes action>: string
a0	mime field <string> of <bes fixlet>: string
a0	mime fields of <bes action>: mime field
a0	mime fields of <bes fixlet>: mime field
bf	minima of <date>: date
bf	minima of <day of month>: day of month
bf	minima of <day of year>: day of year
9	minima of <debian package upstream version>: debian package upstream version
9	minima of <debian package version epoch>: debian package version epoch
9	minima of <debian package version revision>: debian package version revision
9	minima of <debian package version>: debian package version
bf	minima of <floating point>: floating point
bf	minima of <hertz>: hertz
bf	minima of <integer>: integer
bf	minima of <ipv4 address>: ipv4 address
bf	minima of <ipv4or6 address>: ipv4or6 address
bf	minima of <ipv6 address>: ipv6 address
1a	minima of <large integer>: large integer
bf	minima of <month and year>: month and year
bf	minima of <month>: month
bf	minima of <number of months>: number of months
a2	minima of <rate>: rate
4	minima of <rpm package release>: rpm package release
4	minima of <rpm package version record>: rpm package version record
4	minima of <rpm package version>: rpm package version
4	minima of <short rpm package version record>: short rpm package version record
bf	minima of <site version list>: site version list
bf	minima of <time interval>: time interval
bf	minima of <time of day>: time of day
bf	minima of <time>: time
1a	minima of <uinteger>: uinteger
1f	minima of <uuid>: uuid
bf	minima of <version>: version
bf	minima of <year>: year
10	minimum password age of <security database>: time interval
10	minimum password length of <security database>: integer
a0	minimum single computer total of <statistical bin>: floating point
a0	minimum value of <statistical bin>: floating point
1f	minimum_value of <dmi electrical_current_probe>: integer
1f	minimum_value of <dmi temperature_probe>: integer
1f	minimum_value of <dmi voltage_probe>: integer
d	minor of <device file>: integer
bf	minor revision of <version>: integer
1f	minor version of <operating system>: integer
bf	minute: time interval
bf	minute_of_hour of <time of day with time zone>: integer
bf	minute_of_hour of <time of day>: integer
10	missed run count of <scheduled task>: integer
bf	mobile count of <bes product>: integer
d	mode of <filesystem object>: mode
1d	model name of <processor>: string
1f	model of <processor>: integer
1f	model_part_number of <dmi system_power_supply>: string
2	modem scripts folder of <domain>: folder
2	modem scripts folder: folder
a0	modification time of <bes activation>: time
a0	modification time of <bes fixlet>: time
1f	modification time of <execution>: time
1f	modification time of <filesystem object>: time
d	modification time of <symlink>: time
2	modification time of <volume>: time
a0	modification user of <bes fixlet>: bes user
2	modified flag of <route>: boolean
d	module <integer> of <grub bootable image>: grub module
bf	module <string>: module
d	modules of <grub bootable image>: grub module
bf	modules: module
bf	monday: day of week
12	monitor intervals of <power history>: monitor power interval
12	monitor invalid state: power state
12	monitor off state: power state
12	monitor on state: power state
12	monitor standby state: power state
bf	month <integer>: month
bf	month <string>: month
bf	month of <date>: month
bf	month of <day of year>: month
bf	month of <month and year>: month
bf	month: number of months
bf	month_and_year of <date>: month and year
10	monthly task trigger type: task trigger type
10	monthlydow task trigger type: task trigger type
10	months runs of <monthly task trigger>: month
10	months runs of <monthlydow task trigger>: month
bf	more significance <integer> of <floating point>: floating point
bf	most significant one bit of <bit set>: integer
d	mount option of <filesystem>: string
d	mount point of <filesystem>: string
f	mtu of <route>: integer
2	multicast flag of <route>: boolean
1f	multicast support of <network adapter interface>: boolean
1f	multicast support of <network adapter>: boolean
1f	multicast support of <network ip interface>: boolean
a0	multiple flag of <bes action>: boolean
a0	multiplicity of <bes action with multiplicity>: integer
a0	multiplicity of <bes computer group with multiplicity>: integer
a0	multiplicity of <bes computer with multiplicity>: integer
a0	multiplicity of <bes domain with multiplicity>: integer
a0	multiplicity of <bes filter with multiplicity>: integer
a0	multiplicity of <bes fixlet with multiplicity>: integer
a0	multiplicity of <bes ldap directory with multiplicity>: integer
a0	multiplicity of <bes property with multiplicity>: integer
a0	multiplicity of <bes role with multiplicity>: integer
a0	multiplicity of <bes site file with multiplicity>: integer
a0	multiplicity of <bes site with multiplicity>: integer
a0	multiplicity of <bes unmanagedasset with multiplicity>: integer
a0	multiplicity of <bes user with multiplicity>: integer
a0	multiplicity of <bes webui app with multiplicity>: integer
a0	multiplicity of <bes wizard with multiplicity>: integer
bf	multiplicity of <date with multiplicity>: integer
bf	multiplicity of <day of month with multiplicity>: integer
bf	multiplicity of <day of week with multiplicity>: integer
bf	multiplicity of <day of year with multiplicity>: integer
9	multiplicity of <debian package upstream version with multiplicity>: integer
9	multiplicity of <debian package version epoch with multiplicity>: integer
9	multiplicity of <debian package version revision with multiplicity>: integer
9	multiplicity of <debian package version with multiplicity>: integer
bf	multiplicity of <floating point with multiplicity>: integer
bf	multiplicity of <hertz with multiplicity>: integer
bf	multiplicity of <integer with multiplicity>: integer
bf	multiplicity of <ipv4 address with multiplicity>: integer
bf	multiplicity of <ipv4or6 address with multiplicity>: integer
bf	multiplicity of <ipv6 address with multiplicity>: integer
1a	multiplicity of <large integer with multiplicity>: integer
bf	multiplicity of <month and year with multiplicity>: integer
bf	multiplicity of <month with multiplicity>: integer
bf	multiplicity of <number of months with multiplicity>: integer
a2	multiplicity of <rate with multiplicity>: integer
4	multiplicity of <rpm package release with multiplicity>: integer
4	multiplicity of <rpm package version record with multiplicity>: integer
4	multiplicity of <rpm package version with multiplicity>: integer
4	multiplicity of <short rpm package version record with multiplicity>: integer
bf	multiplicity of <site version list with multiplicity>: integer
bf	multiplicity of <string with multiplicity>: integer
bf	multiplicity of <time interval with multiplicity>: integer
bf	multiplicity of <time of day with multiplicity>: integer
bf	multiplicity of <time of day with time zone with multiplicity>: integer
bf	multiplicity of <time range with multiplicity>: integer
bf	multiplicity of <time with multiplicity>: integer
bf	multiplicity of <time zone with multiplicity>: integer
1a	multiplicity of <uinteger with multiplicity>: integer
1f	multiplicity of <uuid with multiplicity>: integer
bf	multiplicity of <version with multiplicity>: integer
bf	multiplicity of <year with multiplicity>: integer
bf	multivalued of <property>: boolean
bf	mvs count of <bes product>: integer
d	name of <SELinux Boolean>: string
d	name of <Xinetd Service>: string
12	name of <active directory group>: string
12	name of <active directory local user>: string
12	name of <agent interface capability>: string
1f	name of <application usage summary instance>: string
1f	name of <application usage summary>: string
10	name of <audit policy category>: string
10	name of <audit policy subcategory>: string
a0	name of <bes action parameter>: string
a0	name of <bes action>: string
a0	name of <bes activation>: string
a0	name of <bes baseline component group>: string
a0	name of <bes baseline component>: string
a0	name of <bes client setting>: string
a0	name of <bes computer group>: string
a0	name of <bes computer>: string
a0	name of <bes deployment option>: string
a0	name of <bes domain>: string
a0	name of <bes filter>: string
a0	name of <bes fixlet field>: string
a0	name of <bes fixlet>: string
a0	name of <bes ldap directory>: string
bf	name of <bes product>: string
a0	name of <bes property>: string
a0	name of <bes role>: string
a0	name of <bes site>: string
a0	name of <bes unmanagedasset field>: string
a0	name of <bes user>: string
a0	name of <bes webui app>: string
a0	name of <bes wizard variable>: string
a0	name of <bes wizard>: string
bf	name of <binary operator>: string
4	name of <capability>: string
bf	name of <cast>: string
2	name of <client process owner>: string
1f	name of <cloud provider>: string
2	name of <component>: string
2	name of <computer>: string
10	name of <connection>: string
9	name of <debian base package>: string
9	name of <debian versioned package>: string
1f	name of <download server>: string
10	name of <drive>: string
1f	name of <environment variable>: string
1f	name of <filesystem object>: string
d	name of <filesystem>: string
10	name of <firewall authorized application>: string
10	name of <firewall open port>: string
10	name of <firewall rule>: string
10	name of <firewall service>: string
1f	name of <fixlet_header>: string
bf	name of <json key>: string
10	name of <local group>: string
1f	name of <logged on user>: string
10	name of <metabase key>: string
a0	name of <mime field>: string
bf	name of <module>: string
1f	name of <network adapter>: string
2	name of <network interface>: string
f	name of <network ip interface>: string
10	name of <network share>: string
1f	name of <operating system>: string
4	name of <package>: string
14	name of <plugin store key>: string
10	name of <port mapping>: string
1f	name of <process>: string
1f	name of <registration server>: string
10	name of <registry key value>: string
10	name of <registry key>: string
2	name of <registrynode>: string
10	name of <running task>: string
10	name of <scheduled task>: string
1f	name of <selected server>: string
1f	name of <setting>: string
10	name of <site profile variable>: string
1f	name of <site>: string
1f	name of <smbios structure>: string
1f	name of <smbios value>: string
1f	name of <sqlite column type>: string
1f	name of <sqlite column>: string
1f	name of <sqlite table>: string
d	name of <symlink>: string
10	name of <task folder>: string
10	name of <task named value pair>: string
10	name of <task network settings>: string
bf	name of <type>: string
bf	name of <unary operator>: string
1f	name of <user>: string
2	name of <volume>: string
12	name of <wifi>: string
10	name of <winrt enumeration>: string
10	name of <winrt package id>: string
10	name of <wmi select>: string
2	name registry version: version
bf	nan of <floating point>: boolean
10	native application <string>: application
10	native file <string> of <encoding>: file
10	native file <string>: file
10	native folder <string> of <encoding>: folder
10	native folder <string>: folder
10	native program files folder: folder
10	native registry: registry
10	native system folder: folder
a0	navbar name of <bes wizard>: string
10	netbios domainname of <active directory local computer>: string
10	netbios domainname of <active directory local user>: string
2	netstat flag of <route>: string
2	network domain: domain
10	network group: security account
10	network service group: security account
10	network setting of <task settings>: task network settings
10	network share <string>: network share
10	network shares: network share
1f	network: network
1f	next line of <file line>: file line
1f	next rawline of <file line>: file line
10	next run time of <scheduled task>: time
bd	next sibling of <xml dom node>: xml dom node
1f	next_scheduled_power_on_day_of_month of <dmi system_power_controls>: integer
1f	next_scheduled_power_on_hour of <dmi system_power_controls>: integer
1f	next_scheduled_power_on_minute of <dmi system_power_controls>: integer
1f	next_scheduled_power_on_month of <dmi system_power_controls>: integer
1f	next_scheduled_power_on_second of <dmi system_power_controls>: integer
bf	nil: undefined
d	no access of <Xinetd Service>: string
4	no epoch of <rpm package version record>: rpm package version record
4	no epoch of <short rpm package version record>: short rpm package version record
10	no password required flag of <user>: boolean
10	no propagate inherit of <access control entry>: boolean
2	node <string> of <registrynode>: registrynode
2	node <string> of <registryroot>: registrynode
bd	node name of <xml dom node>: string
bd	node type of <xml dom node>: integer
bd	node value of <xml dom node>: string
2	nodes of <registrynode>: registrynode
1f	nominal_speed of <dmi cooling_device>: integer
1f	nominal_value of <dmi electrical_current_probe>: integer
1f	nominal_value of <dmi temperature_probe>: integer
1f	nominal_value of <dmi voltage_probe>: integer
bf	non windows server count of <bes product>: integer
10	none firewall service type: firewall service type
10	none logon of <task principal>: boolean
bf	noon: time of day
10	normal account flag of <user>: boolean
10	normal of <filesystem object>: boolean
bf	normal of <floating point>: boolean
d	normal of <grub color scheme>: grub color pair
1f	normal of <power level>: boolean
10	normal priority: priority class
10	normalized date of <fixlet_header>: date
10	notifications disabled of <firewall profile>: boolean
d	nounzip of <grub module>: boolean
bf	november <integer> of <integer>: date
bf	november <integer>: day of year
bf	november of <integer>: month and year
bf	november: month
1f	now of <registration server>: time
bf	now: time
10	nt domain controller product type: operating system product type
10	nt server product type: operating system product type
10	nt workstation product type: operating system product type
2	nubus map: integer
10	null dacl of <security descriptor>: boolean
1f	null of <sqlite column type>: boolean
10	null sacl of <security descriptor>: boolean
bf	null: undefined
1f	number_of_additional_information_entries of <dmi additional_information>: integer
1f	number_of_associated_memory_slots of <dmi memory_controller_information>: integer
1f	number_of_buttons of <dmi built_in_pointing_device>: integer
1f	number_of_contained_object_handles of <dmi base_board_information>: integer
1f	number_of_memory_devices of <dmi physical_memory_array>: integer
1f	number_of_power_cords of <dmi system_enclosure_or_chassis>: integer
10	numeric type of <drive>: integer
bf	numeric value of <string>: integer
1f	nv_storage_device_address of <dmi ipmi_device_information>: integer
1d	nx bit of <process>: boolean
10	object access category of <audit policy>: audit policy category
10	object inherit of <access control entry>: boolean
4	obsoletes of <package>: capability
bf	october <integer> of <integer>: date
bf	october <integer>: day of year
bf	october of <integer>: month and year
bf	october: month
10	oem code page: integer
1f	oem_defined of <dmi cooling_device>: integer
1f	oem_defined of <dmi electrical_current_probe>: integer
1f	oem_defined of <dmi system_enclosure_or_chassis>: integer
1f	oem_defined of <dmi temperature_probe>: integer
1f	oem_defined of <dmi voltage_probe>: integer
1f	oem_specific of <dmi portable_battery>: integer
1f	oem_string <integer> of <dmi>: string
1f	oem_strings of <dmi>: string
12	off state: power state
1f	offer accepted of <action>: boolean
a0	offer category of <bes action>: string
a0	offer description html of <bes action>: html
a0	offer flag of <bes action>: boolean
1f	offer of <action>: boolean
10	offline of <filesystem object>: boolean
1f	offset of <smbios value>: integer
10	ok firewall local policy modify state: firewall local policy modify state
bf	ol <string> of <html>: html
bf	ol <string> of <string>: html
bf	ol of <html>: html
bf	ol of <string>: html
10	oldest record number of <event log>: integer
2	on appropriate disk domain: domain
2	on system disk domain: domain
1f	on_board_devices_information <integer> of <dmi>: dmi on_board_devices_information
1f	on_board_devices_informations of <dmi>: dmi on_board_devices_information
1f	onboard_devices_extended_information <integer> of <dmi>: dmi onboard_devices_extended_information
1f	onboard_devices_extended_informations of <dmi>: dmi onboard_devices_extended_information
bf	one bits of <bit set>: integer
d	only from of <Xinetd Service>: string
10	only raw version block of <file>: file version block
10	only version block of <file>: file version block
a0	open action count of <bes fixlet>: integer
bf	operand type of <cast>: type
bf	operand type of <unary operator>: type
a0	operating system of <bes computer>: string
10	operating system product type <integer>: operating system product type
1f	operating system: operating system
a0	operator of <bes site>: bes user
a0	operator site flag of <bes action>: boolean
a0	operator site flag of <bes fixlet>: boolean
a0	operator site flag of <bes site>: boolean
a0	operator site of <bes user>: bes site
10	options of <port mapping>: integer
bf	ordered lists <string> of <html>: html
bf	ordered lists <string> of <string>: html
bf	ordered lists of <html>: html
bf	ordered lists of <string>: html
bf	organization of <license>: string
1f	origin fixlet id of <action>: integer
1f	other duration of <evaluation cycle>: time interval
d	other execute of <filesystem object>: boolean
d	other mask of <filesystem object>: integer
d	other mask of <mode>: mode_mask
1f	other percent of <evaluation cycle>: floating point
d	other read of <filesystem object>: boolean
d	other write of <filesystem object>: boolean
1f	out_of_band_remote_access <integer> of <dmi>: dmi out_of_band_remote_access
1f	out_of_band_remote_accesss of <dmi>: dmi out_of_band_remote_access
10	outbound connections allowed of <firewall profile>: boolean
10	outbound of <firewall rule>: boolean
bf	overflow of <floating point>: boolean
bd	owner document of <xml dom node>: xml dom document
a0	owner flag <bes user> of <bes site>: boolean
10	owner of <security descriptor>: security identifier
a0	owner set of <bes site>: bes user set
a0	owners of <bes site>: bes user
bf	p <string> of <html>: html
bf	p <string> of <string>: html
bf	p of <html>: html
bf	p of <string>: html
9	packages <string> of <debianpackagecache>: debian versioned package
4	packages <string> of <rpmdatabase>: package
4	packages conflicting with <capability> of <rpmdatabase>: package
4	packages installing <capability> of <rpmdatabase>: package
9	packages of <debianpackagecache>: debian versioned package
4	packages of <rpmdatabase>: package
4	packages providing <capability> of <rpmdatabase>: package
4	packages requiring <capability> of <rpmdatabase>: package
bf	pad of <version>: version
bf	padded string of <bit set>: string
10	page fault count of <process>: integer
10	page file usage of <process>: integer
10	parallel instance of <task settings>: boolean
1f	parameter <string> of <action>: string
a0	parameter <string> of <bes action>: string
1f	parameter <string>: string
a0	parameters of <bes action>: bes action parameter
1f	parent folder of <filesystem object>: folder
d	parent folder of <symlink>: folder
a0	parent group of <bes action>: bes action
10	parent key of <registry key value>: registry key
10	parent key of <registry key>: registry key
bd	parent node of <xml dom node>: xml dom node
bf	parent of <type>: type
a0	parent relevances of <bes fixlet>: string
bf	parenthesized part <integer> of <regular expression match>: substring
bf	parenthesized parts of <regular expression match>: substring
1f	part_number of <dmi memory_device>: string
1f	part_number of <dmi processor_information>: string
1f	partition_row_position of <dmi memory_device_mapped_address>: integer
1f	partition_width of <dmi memory_array_mapped_address>: integer
10	password age of <user>: time interval
10	password change disabled flag of <user>: boolean
10	password expiration disabled flag of <user>: boolean
10	password expired of <user>: boolean
10	password history length of <security database>: integer
10	password logon of <task principal>: boolean
10	password of <network share>: string
bf	patch revision of <version>: integer
1f	path <string> of <instance data>: json value
bf	path <string> of <json value>: json value
10	path of <exec task action>: string
1f	path of <execution>: string
d	path of <grub config file>: string
d	path of <grub file location>: string
10	path of <network share>: string
2	path of <registrynode>: string
10	path of <running task>: string
10	path of <scheduled task>: string
10	path of <task folder>: string
10	pathname of <file shortcut>: string
1f	pathname of <filesystem object>: string
10	pathname of <registry key>: string
d	pathname of <symlink>: string
10	peak page file usage of <process>: integer
10	peak working set size of <process>: integer
1d	pem encoded certificate of <file>: x509 certificate
1d	pem encoded certificate string of <string>: x509 certificate
a0	pending license update: boolean
1f	pending login of <action>: boolean
1f	pending login: boolean
1f	pending of <action>: boolean
1f	pending restart <string>: boolean
1f	pending restart names: string
1f	pending restart of <action>: boolean
1f	pending restart: boolean
d	pending status of <SELinux Boolean>: boolean
1f	pending time of <action>: time
10	per user policy <security account> of <audit policy subcategory>: audit policy information
bf	percent decode <string>: string
bf	percent encode <binary_string>: string
bf	percent encode <string>: string
10	performance counter frequency of <operating system>: hertz
10	performance counter of <operating system>: integer
1a	perl regex escape of <string>: string
1a	perl regexes <string>: regular expression
1a	perl regular expressions <string>: regular expression
10	permission permission of <network share>: boolean
bf	perpetual maintenance of <bes product>: boolean
bf	perpetual of <bes product>: boolean
1f	persistent constraint of <action>: integer
10	personal bit <operating system suite mask>: boolean
10	physical processor count: integer
2	physical ram: integer
1f	physical_memory_array <integer> of <dmi>: dmi physical_memory_array
1f	physical_memory_arrays of <dmi>: dmi physical_memory_array
1f	pid of <process>: integer
10	pid of <service>: integer
2	pinned flag of <route>: boolean
9	pkg versions of <debian base package>: debianpkg version
9	pkglibversion of <debianpackagecache>: string
a0	plain bes fixlet set: bes fixlet set
a0	plain bes fixlets: bes fixlet
d	platform id of <language>: string
10	platform id of <operating system>: integer
1f	plugged of <power level>: boolean
1d	plugin portal service: service
14	plugin store <string>: plugin store
a0	plural flag of <bes property result>: boolean
bf	plural name of <property>: string
1f	point to point of <network adapter interface>: boolean
2	point to point of <network adapter>: boolean
1f	point to point of <network ip interface>: boolean
10	policy change category of <audit policy>: audit policy category
d	policy of <process>: string
10	port mappings of <internet connection firewall>: port mapping
1f	port number of <selected server>: integer
d	port of <Xinetd Service>: integer
a0	port of <bes ldap directory server>: integer
10	port of <firewall open port>: integer
1f	port_connector_information <integer> of <dmi>: dmi port_connector_information
1f	port_connector_informations of <dmi>: dmi port_connector_information
1f	port_type of <dmi port_connector_information>: integer
1f	portable_battery <integer> of <dmi>: dmi portable_battery
1f	portable_batterys of <dmi>: dmi portable_battery
bf	position <integer> of <binary_string>: binary position
bf	position <integer> of <string>: string position
bf	positions of <binary_string>: binary position
bf	positions of <string>: string position
d	posix capability of <process>: integer
1a	posix case insensitive regexes <string>: regular expression
1a	posix case insensitive regular expressions <string>: regular expression
2	posix file <string> of <encoding>: file
2	posix file <string>: file
2	posix folder <string> of <encoding>: folder
2	posix folder <string>: folder
2	posix item <string>: filesystem object
2	posix path of <filesystem object>: string
1a	posix regex escape of <string>: string
1a	posix regexes <string>: regular expression
1a	posix regular expressions <string>: regular expression
2	posix relative item <string> of <folder>: filesystem object
a0	postaction allow cancel flag of <bes action>: boolean
a0	postaction force delay of <bes action>: time interval
a0	postaction message text of <bes action>: string
a0	postaction message title of <bes action>: string
a0	postaction postpone delay of <bes action>: time interval
12	power history: power history
1f	power level: power level
2	power plane of <registryroot>: registrynode
1f	power_supply_characteristics of <dmi system_power_supply>: integer
1f	power_supply_state of <dmi system_enclosure_or_chassis>: integer
1f	power_unit_group of <dmi system_power_supply>: integer
2	powerpc: boolean
1f	ppid of <process>: integer
2	prcloning flag of <route>: boolean
bf	pre <string> of <html>: html
bf	pre <string> of <string>: html
bf	pre of <html>: html
bf	pre of <string>: html
a0	pre60 flag of <bes wizard>: boolean
a0	precache flag of <bes action>: boolean
bf	preceding binary_string of <binary position>: binary_substring
bf	preceding binary_string of <binary_substring>: binary_substring
bf	preceding text of <string position>: substring
bf	preceding text of <substring>: substring
2	preference <string>: preference
2	preferences folder of <domain>: folder
2	preferences folder: folder
a0	preferred bes language: string
1f	previous line of <file line>: file line
1f	previous rawline of <file line>: file line
bd	previous sibling of <xml dom node>: xml dom node
d	previous value of <runlevel>: string
d	primary codeset of <language>: string
d	primary country of <language>: string
12	primary group id of <user>: integer
2	primary internet connection: network ip interface
1d	primary language of <language>: primary language
10	primary wins server of <network adapter>: ipv4 address
10	principal of <task definition>: task principal
10	print operator flag of <user>: boolean
2	printer descriptions folder of <domain>: folder
2	printer descriptions folder: folder
2	printer drivers folder of <domain>: folder
2	printer drivers folder: folder
2	printers folder of <domain>: folder
2	printers folder: folder
2	printmonitor documents folder of <domain>: folder
2	printmonitor documents folder: folder
a0	priority of <bes ldap directory server>: integer
d	priority of <process>: integer
1f	priority of <selected server>: integer
10	priority of <task settings>: integer
10	private firewall profile type: firewall profile type
a0	private flag of <bes filter>: boolean
a0	private flag of <bes wizard variable>: boolean
2	private framework folder of <domain>: folder
2	private framework folder: folder
1f	private ip of <cloud provider>: string
10	private profile of <firewall policy>: firewall profile
a0	private variable <( string, string )>: string
a0	private variable <string> of <bes wizard>: string
a0	private variables of <bes wizard>: bes wizard variable
10	privilege use category of <audit policy>: audit policy category
10	privileges of <security account>: string
10	problem id of <active device>: integer
1f	process <integer>: process
d	process id of <logged on user>: integer
1f	process id of <process>: integer
10	process image file name of <firewall authorized application>: string
1f	process of <socket>: process
2	process owner of <client>: client process owner
1f	processes <string>: process
1f	processes: process
1f	processor <integer>: processor
1f	processor_characteristics of <dmi processor_information>: integer
1f	processor_family of <dmi processor_information>: integer
1f	processor_family_2 of <dmi processor_information>: integer
1f	processor_id of <dmi processor_information>: integer
1f	processor_information <integer> of <dmi>: dmi processor_information
1f	processor_informations of <dmi>: dmi processor_information
1f	processor_manufacturer of <dmi processor_information>: string
1f	processor_type of <dmi processor_information>: integer
1f	processor_upgrade of <dmi processor_information>: integer
1f	processor_version of <dmi processor_information>: string
1f	processors: processor
10	product info numeric of <operating system>: integer
1f	product info string of <operating system>: string
1f	product of <dmi base_board_information>: string
2	product of <scsidevice>: string
10	product type of <operating system>: operating system product type
10	product version of <file>: version
1f	product_name of <dmi system_information>: string
bf	products of <floating point>: floating point
bf	products of <integer>: integer
bf	products of <license>: bes product
10	profile <firewall profile type> of <firewall rule>: boolean
10	profile folder of <user>: string
10	profile of <site>: site profile
10	profile types of <firewall>: firewall profile type
10	profiles of <firewall policy>: firewall profile
10	program files folder: folder
10	program files x32 folder: folder
10	program files x64 folder: folder
bf	properties <string> of <type>: property
bf	properties <string>: property
a0	properties of <bes fixlet>: bes property
bf	properties of <type>: property
10	properties of <wmi object>: wmi select
bf	properties returning <type> of <type>: property
bf	properties returning <type>: property
bf	properties: property
a0	property <integer> of <bes fixlet>: bes property
10	property <string> of <wmi object>: wmi select
1f	property duration of <evaluation cycle>: time interval
a0	property of <bes property result>: bes property
1f	property percent of <evaluation cycle>: floating point
a0	property results of <bes computer>: bes property result
2	proto1 flag of <route>: boolean
2	proto2 flag of <route>: boolean
2	proto3 flag of <route>: boolean
d	protocol of <Xinetd Service>: string
10	protocol of <firewall open port>: internet protocol
10	protocol of <firewall rule>: internet protocol
10	protocol of <port mapping>: string
4	provides of <package>: capability
1f	proxied of <hardware>: boolean
1d	proxy agent service: service
2	proxy flag of <route>: boolean
10	public firewall profile type: firewall profile type
bf	public key algorithm of <x509 certificate>: string
10	public profile of <firewall policy>: firewall profile
10	publisher id of <winrt package id>: string
10	publisher of <winrt package id>: string
bf	q <string> of <html>: html
bf	q <string> of <string>: html
bf	q of <html>: html
bf	q of <string>: html
10	query value permission of <access control entry>: boolean
10	queue instance of <task settings>: boolean
10	queued state of <running task>: boolean
10	queued state of <scheduled task>: boolean
2	quickdraw version: version
2	quicktime folder of <domain>: folder
2	quicktime folder: folder
1f	quiet mode duration of <evaluation cycle>: time interval
1f	quiet mode percent of <evaluation cycle>: floating point
d	quiet of <grub bootable image>: boolean
10	quota nonpaged pool usage of <process>: integer
10	quota paged pool usage of <process>: integer
10	quota peak nonpaged pool usage of <process>: integer
10	quota peak paged pool usage of <process>: integer
1f	ram: ram
1f	random access memory: ram
10	random delay of <daily task trigger>: time interval
10	random delay of <monthly task trigger>: time interval
10	random delay of <monthlydow task trigger>: time interval
10	random delay of <time task trigger>: time interval
10	random delay of <weekly task trigger>: time interval
bf	random floating point: floating point
bf	random integer of <integer>: integer
bf	random integer: integer
a0	range <time range> of <statistic range>: statistic range
bf	range after <time> of <time range>: time range
bf	range before <time> of <time range>: time range
12	range of <monitor power interval>: time range
12	range of <system power interval>: time range
a2	rate <time interval> of <exponential projection>: floating point
a2	rate of <linear projection>: rate
10	raw file version of <file>: version
10	raw product version of <file>: version
10	raw version block <integer> of <file>: file version block
10	raw version block <string> of <file>: file version block
10	raw version blocks of <file>: file version block
10	raw version of <file>: version
1f	rawline <integer> of <file>: file line
1f	rawline number of <file line>: integer
1f	rawlines containing <string> of <file>: file line
1f	rawlines of <file>: file line
1f	rawlines starting with <string> of <file>: file line
10	read attributes permission of <access control entry>: boolean
10	read control permission of <access control entry>: boolean
10	read extended attributes permission of <access control entry>: boolean
d	read of <mode_mask>: boolean
10	read permission of <access control entry>: boolean
10	read permission of <network share>: boolean
a0	reader set of <bes site>: bes user set
a0	readers of <bes site>: bes user
10	readonly of <filesystem object>: boolean
10	ready state of <running task>: boolean
10	ready state of <scheduled task>: boolean
2	real <integer> of <array>: floating point
2	real <string> of <dictionary>: floating point
2	real of <osxvalue>: floating point
10	realtime priority: priority class
a0	reapplication interval of <bes action>: time interval
a0	reapplication limit of <bes action>: integer
a0	reapply flag of <bes action>: boolean
2	receipts folder of <domain>: folder
2	receipts folder: folder
1f	recent application <string>: application
1f	recent applications: application
10	record <integer> of <event log>: event log record
10	record count of <event log>: integer
10	record number of <event log record>: integer
10	records of <event log>: event log record
10	reference attribute of <metabase value>: boolean
2	reference of <route>: integer
1f	reference_designation of <dmi onboard_devices_extended_information>: integer
12	regapp <string>: application
12	regapps: application
bf	regex escape of <string>: string
bf	regexes <string>: regular expression
1f	region of <cloud provider>: string
bf	registrar number of <license>: integer
1f	registration address of <client>: ipv4or6 address
1f	registration cidr address of <client>: string
10	registration info of <task definition>: task registration info
1f	registration mac address of <client>: string
1f	registration server: registration server
1f	registration subnet address of <client>: ipv4or6 address
10	registration task trigger type: task trigger type
2	registry: dummy type
10	registry: registry
bf	regular expressions <string>: regular expression
f	reject flag of <route>: boolean
4	relation of <capability>: string
2	relative file <string> of <folder>: file
2	relative folder <binary_string> of <folder>: folder
2	relative folder <string> of <folder>: folder
2	relative hfs file <string> of <folder>: file
2	relative hfs folder <string> of <folder>: folder
2	relative item <string> of <folder>: filesystem object
2	relative posix file <string> of <folder>: file
2	relative posix folder <string> of <folder>: folder
bf	relative significance place <integer> of <floating point>: floating point
bf	relative significance place of <floating point>: floating point
a0	relay distance of <bes computer>: integer
a0	relay hostname of <bes computer>: string
1f	relay select duration of <evaluation cycle>: time interval
1f	relay select percent of <evaluation cycle>: floating point
a0	relay selection method of <bes computer>: string
a0	relay server flag of <bes computer>: boolean
a0	relay server of <bes computer>: string
2	relay service: nothing
1d	relay service: service
9	release of <debian versioned package>: string
1d	release of <operating system>: string
2	release of <operating system>: version
4	release of <rpm package version record>: rpm package release
4	release of <short rpm package version record>: rpm package release
12	releaseid of <operating system>: string
a0	relevance clauses of <bes fixlet>: string
1f	relevance duration of <evaluation cycle>: time interval
a0	relevance of <bes baseline component>: string
a0	relevance of <bes fixlet>: string
1f	relevance of <fixlet>: boolean
1f	relevance percent of <evaluation cycle>: floating point
a0	relevant <( bes computer, bes fixlet )>: boolean
a0	relevant <( bes fixlet, bes computer )>: boolean
a0	relevant <bes computer> of <bes fixlet>: boolean
a0	relevant <bes fixlet> of <bes computer>: boolean
a0	relevant fixlet set of <bes computer>: bes fixlet set
a0	relevant fixlets of <bes computer>: bes fixlet
1f	relevant fixlets of <site>: fixlet
a0	relevant flag of <bes fixlet result>: boolean
1f	relevant offer actions of <site>: action
a0	remediated flag of <bes fixlet result>: boolean
1f	remote address of <socket>: ipv4or6 address
10	remote addresses of <firewall authorized application>: string
10	remote addresses of <firewall open port>: string
10	remote addresses of <firewall service>: string
10	remote addresses string of <firewall rule>: string
10	remote admin settings of <firewall profile>: firewall remote admin settings
10	remote connect of <session state change task trigger>: boolean
10	remote desktop firewall service type: firewall service type
10	remote disconnect of <session state change task trigger>: boolean
10	remote interactive logon group: security account
1f	remote of <logged on user>: boolean
1f	remote port of <socket>: integer
10	remote ports string of <firewall rule>: string
10	repetition of <task trigger>: task repetition pattern
10	replyto of <email task action>: string
1f	report character set of <client>: string
1f	report duration of <evaluation cycle>: time interval
1f	report percent of <evaluation cycle>: floating point
a0	reported action set of <bes computer>: bes action set
a0	reported computer set of <bes action>: bes computer set
a0	reported computer set of <bes property>: bes computer set
a0	reported property set of <bes computer>: bes property set
bf	representable in <string> of <binary_string>: boolean
bf	representable in utf16 of <binary_string>: boolean
bf	representable in utf8 of <binary_string>: boolean
bf	representable of <binary_string>: boolean
bf	representation in <string> of <binary_string>: string
a0	require user absence of <bes action>: boolean
a0	require user presence of <bes action>: boolean
a0	requires authoring flag of <bes wizard>: boolean
4	requires of <package>: capability
a0	reserved flag of <bes property>: boolean
1f	reserved of <dmi bios_language_information>: binary_string
1f	reserved of <dmi system_boot_information>: binary_string
1f	reset_count of <dmi system_reset>: integer
1f	reset_limit of <dmi system_reset>: integer
1f	resolution of <dmi electrical_current_probe>: integer
1f	resolution of <dmi temperature_probe>: integer
1f	resolution of <dmi voltage_probe>: integer
2	resource fork of <file>: resfork
10	restart count of <task settings>: integer
a0	restart flag of <bes action>: boolean
10	restart interval of <task settings>: time interval
10	restart on idle of <task idle settings>: boolean
a0	restartandshutdown actionscript privilege allowboth flag of <bes user>: boolean
a0	restartandshutdown actionscript privilege allowrestartonly flag of <bes user>: boolean
a0	restartandshutdown actionscript privilege none flag of <bes user>: boolean
a0	restartandshutdown postaction privilege allowboth flag of <bes user>: boolean
a0	restartandshutdown postaction privilege allowrestartonly flag of <bes user>: boolean
a0	restartandshutdown postaction privilege none flag of <bes user>: boolean
1f	restricted site: restricted site
a0	result <( bes action, bes computer )>: bes action result
a0	result <( bes computer, bes action )>: bes action result
a0	result <( bes computer, bes fixlet )>: bes fixlet result
a0	result <( bes computer, bes property )>: bes property result
a0	result <( bes fixlet, bes computer )>: bes fixlet result
a0	result <( bes property, bes computer )>: bes property result
a0	result from <bes action> of <bes computer>: bes action result
a0	result from <bes computer> of <bes action>: bes action result
a0	result from <bes computer> of <bes fixlet>: bes fixlet result
a0	result from <bes computer> of <bes property>: bes property result
a0	result from <bes fixlet> of <bes computer>: bes fixlet result
a0	result from <bes property> of <bes computer>: bes property result
bf	result type of <binary operator>: type
bf	result type of <cast>: type
bf	result type of <property>: type
bf	result type of <unary operator>: type
a0	results of <bes action>: bes action result
a0	results of <bes fixlet>: bes fixlet result
a0	results of <bes property>: bes property result
a0	retry count of <bes action result>: integer
a0	retry delay of <bes action>: time interval
a0	retry limit of <bes action>: integer
a0	retry wait for reboot flag of <bes action>: boolean
9	reverse dependencies of <debian versioned package>: debianpkg reverse dependencies
9	revision of <debian package version>: debian package version revision
2	revision of <scsidevice>: string
1f	revision_level of <dmi system_power_supply>: string
bf	right operand type of <binary operator>: type
bf	right shift <integer> of <bit set>: bit set
a0	role set of <bes user>: bes role set
a0	roles of <bes user>: bes role
2	rom version: version
10	root folder of <drive>: folder
d	root folder: folder
d	root of <grub bootable image>: grub device
a0	root server flag of <bes computer>: boolean
a0	root server of <bes computer>: string
1f	root server: root server
d	rootnoverify of <grub bootable image>: grub device
bf	rope <string>: rope
2	router flag of <route>: boolean
f	routes of <routing table>: route
f	routing table: routing table
1f	rows of <sqlite statement>: sqlite row
4	rpm <string>: rpmdatabase
4	rpm package release <rpm package release>: rpm package release
4	rpm package release <string>: rpm package release
4	rpm package version <rpm package version>: rpm package version
4	rpm package version <string>: rpm package version
4	rpm package version record <rpm package version record>: rpm package version record
4	rpm package version record <short rpm package version record>: rpm package version record
4	rpm package version record <string>: rpm package version record
4	rpm version record of <package>: rpm package version record
4	rpm: rpmdatabase
10	rsop computer wmi: wmi
10	rsop user wmi <security identifier>: wmi
12	rssi of <wifi network>: integer
1a	rtt of <socket>: time interval
10	rule group currently enabled <string> of <firewall>: boolean
10	rule group enabled <string> of <firewall profile>: boolean
10	rules of <firewall service restriction>: firewall rule
12	rules of <firewall>: firewall rule
10	run on fifth week in month of <monthlydow task trigger>: boolean
10	run on first week in month of <monthlydow task trigger>: boolean
10	run on fourth week in month of <monthlydow task trigger>: boolean
10	run on last day in month of <monthly task trigger>: boolean
10	run on last week in month of <monthlydow task trigger>: boolean
10	run on second week in month of <monthlydow task trigger>: boolean
10	run on third week in month of <monthlydow task trigger>: boolean
10	run only when idle of <task settings>: boolean
10	run only when network available of <task settings>: boolean
d	runlevel: runlevel
4	runlevels of <service>: string
1f	running application <string>: application
1f	running applications: application
a0	running message text of <bes action>: string
a0	running message title of <bes action>: string
1f	running of <application usage summary>: boolean
10	running of <local mssql database>: boolean
1d	running of <service>: boolean
1d	running service <string>: service
10	running services: service
10	running state of <running task>: boolean
10	running state of <scheduled task>: boolean
10	running tasks: running task
bf	rvu count of <bes product>: integer
10	s4u logon of <task principal>: boolean
10	sacl of <security descriptor>: system access control list
bf	samp <string> of <html>: html
bf	samp <string> of <string>: html
bf	samp of <html>: html
bf	samp of <string>: html
12	sample time of <active directory group>: time
12	sample time of <active directory local computer>: time
12	sample time of <active directory local user>: time
a0	sans id list of <bes fixlet>: string
bf	saturday: day of week
d	savedefault of <grub bootable image>: boolean
1f	sbds_device_chemistry of <dmi portable_battery>: string
1f	sbds_manufacture_date of <dmi portable_battery>: integer
1f	sbds_serial_number of <dmi portable_battery>: integer
1f	sbds_version_number of <dmi portable_battery>: string
d	schedule class of <process>: string
10	scheduled task <string> of <task folder>: scheduled task
10	scheduled task <string>: scheduled task
10	scheduled tasks of <task folder>: scheduled task
10	scheduled tasks: scheduled task
1f	schema of <sqlite table>: string
a0	scope of <bes client setting>: string
10	scope of <firewall authorized application>: firewall scope
10	scope of <firewall open port>: firewall scope
10	scope of <firewall service>: firewall scope
10	script flag of <user>: boolean
a0	script of <bes fixlet action>: string
a0	script type of <bes fixlet action>: string
2	scripting additions folder of <domain>: folder
2	scripting additions folder: folder
2	scsibus <integer>: scsibus
2	scsibuses: scsibus
2	scsidevice <integer> of <scsibus>: scsidevice
2	scsidevice <integer>: scsidevice
2	scsidevices of <scsibus>: scsidevice
2	scsidevices: scsidevice
bf	seat count state of <license>: string
bf	seat of <license>: integer
bf	second: time interval
bf	second_of_minute of <time of day with time zone>: integer
bf	second_of_minute of <time of day>: integer
10	secondary wins server of <network adapter>: ipv4 address
2	seconds to expiration of <route>: integer
1f	section <string> of <file>: file section
9	section of <debian versioned package>: string
9	section of <debianpkg version>: string
10	secure attribute of <metabase value>: boolean
a0	secure parameter flag of <bes action>: boolean
12	secured of <wifi network>: boolean
12	secured of <wifi>: boolean
10	security account <string>: security account
10	security database: security database
10	security descriptor <string>: security descriptor
10	security descriptor of <file>: security descriptor
10	security descriptor of <folder>: security descriptor
10	security descriptor of <network share>: security descriptor
10	security descriptor of <registry key>: security descriptor
10	security descriptor of <scheduled task>: security descriptor
10	security descriptor of <service>: security descriptor
10	security descriptor of <task folder>: security descriptor
10	security descriptor of <task registration info>: security descriptor
10	security event log: event log
1f	security_status of <dmi system_enclosure_or_chassis>: integer
1f	segment_group_number of <dmi onboard_devices_extended_information>: integer
1f	segment_group_number of <dmi system_slots>: integer
10	select objects <string> of <wmi>: wmi object
a0	selected groups string of <bes action>: string
1f	selected server: selected server
10	selects <string> of <wmi>: wmi select
b0	selects <string> of <xml dom node>: xml dom node
d	selinux booleans <string>: SELinux Boolean
d	selinux booleans: SELinux Boolean
d	selinux context of <process>: string
d	selinux domain of <process>: string
2	sent packet count of <route>: integer
d	sep bug of <processor>: boolean
bf	september <integer> of <integer>: date
bf	september <integer>: day of year
bf	september of <integer>: month and year
bf	september: month
bf	serial number of <x509 certificate>: string
1f	serial of <hardware>: string
1f	serial_number of <dmi base_board_information>: string
1f	serial_number of <dmi memory_device>: string
1f	serial_number of <dmi portable_battery>: string
1f	serial_number of <dmi processor_information>: string
1f	serial_number of <dmi system_enclosure_or_chassis>: string
1f	serial_number of <dmi system_information>: string
1f	serial_number of <dmi system_power_supply>: string
d	server arg of <Xinetd Service>: string
a0	server based flag of <bes computer group>: boolean
1f	server based group <string> of <client>: server based group
1f	server based groups of <client>: server based group
d	server of <Xinetd Service>: string
10	server of <email task action>: string
10	server operator flag of <user>: boolean
10	server trust account flag of <user>: boolean
a0	servers of <bes ldap directory>: bes ldap directory server
2	service <string>: dummy
1d	service <string>: service
10	service account logon of <task principal>: boolean
10	service group: security account
10	service key value name of <active device>: string
12	service name of <firewall rule>: string
10	service name of <service>: string
10	service pack major version of <operating system>: integer
10	service pack minor version of <operating system>: integer
2	service plane of <registryroot>: registrynode
10	service restricted <( string, string )> of <firewall service restriction>: boolean
10	service restriction of <firewall>: firewall service restriction
10	service specific exit code of <service>: integer
10	services of <firewall profile>: firewall service
14	services: service
12	session id of <logged on user>: integer
10	session id of <process>: integer
10	session lock of <session state change task trigger>: boolean
d	session of <process>: integer
10	session state change task trigger type: task trigger type
10	session unlock of <session state change task trigger>: boolean
10	set value permission of <access control entry>: boolean
d	setgid of <filesystem object>: boolean
d	setgid of <mode>: boolean
a0	sets of <bes action>: bes action set
a0	sets of <bes computer group>: bes computer group set
a0	sets of <bes computer>: bes computer set
a0	sets of <bes domain>: bes domain set
a0	sets of <bes filter>: bes filter set
a0	sets of <bes fixlet>: bes fixlet set
a0	sets of <bes ldap directory>: bes ldap directory set
a0	sets of <bes property>: bes property set
a0	sets of <bes role>: bes role set
a0	sets of <bes site file>: bes site file set
a0	sets of <bes site>: bes site set
a0	sets of <bes unmanagedasset>: bes unmanagedasset set
a0	sets of <bes user>: bes user set
a0	sets of <bes webui app>: bes webui app set
a0	sets of <bes wizard>: bes wizard set
bf	sets of <integer>: integer set
bf	sets of <string>: string set
1f	setting <string> of <client>: setting
1f	setting <string> of <site>: setting
1f	setting of <manual group>: setting
1f	setting of <server based group>: setting
10	setting of <task definition>: task settings
a0	settings flag of <bes action>: boolean
1f	settings of <client>: setting
1f	settings of <site>: setting
d	setuid of <filesystem object>: boolean
d	setuid of <mode>: boolean
1f	sha1 of <file>: string
bf	sha1 of <string>: string
bf	sha1 of <x509 certificate>: string
1f	sha224 of <file>: string
bf	sha224 of <string>: string
bf	sha256 download of <license>: boolean
1f	sha256 of <file>: string
1f	sha256 of <setting>: string
bf	sha256 of <string>: string
1f	sha2_224 of <file>: string
bf	sha2_224 of <string>: string
1f	sha2_256 of <file>: string
bf	sha2_256 of <string>: string
1f	sha2_384 of <file>: string
bf	sha2_384 of <string>: string
1f	sha2_512 of <file>: string
bf	sha2_512 of <string>: string
1f	sha384 of <file>: string
bf	sha384 of <string>: string
1a	sha384 signature of <license>: boolean
1f	sha512 of <file>: string
bf	sha512 of <string>: string
d	shared amount of <ram>: integer
2	shared folder of <domain>: folder
2	shared folder: folder
2	shared libraries folder of <domain>: folder
2	shared libraries folder: folder
a0	shared variable <( string, string )>: string
a0	shared variable <string> of <bes wizard>: string
a0	shared variables of <bes wizard>: bes wizard variable
4	short form of <rpm package version record>: short rpm package version record
2	short name of <client process owner>: string
4	short rpm package version record <rpm package version record>: short rpm package version record
4	short rpm package version record <short rpm package version record>: short rpm package version record
2	short version of <filesystem object>: version
10	shortcut of <file>: file shortcut
a0	show message flag of <bes action>: boolean
10	show message task action type: task action type
a0	show other action flag of <bes user>: boolean
a0	show running message flag of <bes action>: boolean
a0	shutdown flag of <bes action>: boolean
2	shutdown items <string>: enableable_file
2	shutdown items folder of <domain>: folder
2	shutdown items folder: folder
2	shutdown items: enableable_file
2	sibling file <binary_string> of <filesystem object>: file
2	sibling file <string> of <filesystem object>: file
2	sibling folder <string> of <filesystem object>: folder
2	sibling item <string> of <filesystem object>: filesystem object
10	sid <string>: security identifier
12	sid of <active directory group>: security identifier
10	sid of <logged on user>: security identifier
10	sid of <security account>: security identifier
12	sid of <user>: security identifier
10	sid of <winrt package user information>: security identifier
12	signal strength of <wifi network>: integer
bf	signature algorithm of <x509 certificate>: string
bf	signature hash algorithms of <license>: string
4	signature keyid of <package>: string
bf	significance place <integer> of <floating point>: floating point
bf	significance place of <floating point>: floating point
bf	significance threshold of <floating point>: floating point
bf	significant digits <integer> of <hertz>: hertz
bf	significant digits <integer> of <integer>: integer
a0	simple name of <bes property>: string
a0	single flag of <bes action>: boolean
10	single user ts bit <operating system suite mask>: boolean
bf	singular name of <property>: string
1f	site <string>: site
a0	site file set of <bes site>: bes site file set
a0	site files of <bes site>: bes site file
a0	site level relevance of <bes site>: string
bf	site number of <license>: integer
a0	site of <bes computer group>: bes site
a0	site of <bes fixlet>: bes site
a0	site of <bes wizard>: bes site
1f	site of <fixlet>: site
1f	site tag of <site>: string
bf	site urls of <bes product>: string
bf	site version list <string>: site version list
1f	site version list of <site>: site version list
1f	sites: site
1f	size of <application usage summary instance>: integer
2	size of <array>: integer
a0	size of <bes action set>: integer
a0	size of <bes computer group set>: integer
a0	size of <bes computer set>: integer
a0	size of <bes domain set>: integer
a0	size of <bes filter set>: integer
a0	size of <bes fixlet set>: integer
a0	size of <bes ldap directory set>: integer
a0	size of <bes property set>: integer
a0	size of <bes role set>: integer
a0	size of <bes site file set>: integer
a0	size of <bes site set>: integer
a0	size of <bes unmanagedasset set>: integer
a0	size of <bes user set>: integer
a0	size of <bes webui app set>: integer
a0	size of <bes wizard set>: integer
2	size of <datafork>: integer
2	size of <dictionary>: integer
1f	size of <dmi memory_device>: integer
1f	size of <file>: integer
d	size of <filesystem>: integer
bf	size of <integer set>: integer
1f	size of <ram>: integer
10	size of <registry key value>: integer
2	size of <resfork>: integer
bf	size of <string set>: integer
f	size of <swap>: integer
bf	size of <type>: integer
2	size of <volume>: integer
a0	skewness of <statistical bin>: floating point
1f	sku_number of <dmi system_information>: string
1f	sleep duration of <evaluation cycle>: time interval
1f	sleep percent of <evaluation cycle>: floating point
1f	slot_characteristics_1 of <dmi system_slots>: integer
1f	slot_characteristics_2 of <dmi system_slots>: integer
1f	slot_data_bus_width of <dmi system_slots>: integer
1f	slot_designation of <dmi system_slots>: string
1f	slot_id of <dmi system_slots>: integer
1f	slot_length of <dmi system_slots>: integer
1f	slot_type of <dmi system_slots>: integer
bf	small <string> of <html>: html
bf	small <string> of <string>: html
10	small business bit <operating system suite mask>: boolean
10	small business restricted bit <operating system suite mask>: boolean
bf	small of <html>: html
bf	small of <string>: html
1f	smbios: smbios
1f	smt capable of <cpupackage>: boolean
1f	smt enabled of <cpupackage>: boolean
d	socket file <filesystem object>: socket file
d	socket file <string> of <folder>: socket file
d	socket file <string>: socket file
d	socket file <symlink>: socket file
d	socket files of <folder>: socket file
d	socket type of <Xinetd Service>: string
1f	socket_designation of <dmi cache_information>: string
1f	socket_designation of <dmi memory_module_information>: string
1f	socket_designation of <dmi processor_information>: string
1f	sockets of <network>: socket
2	sound folder of <domain>: folder
2	sound folder: folder
a0	source analysis of <bes property>: bes fixlet
a0	source evaluation period of <bes property>: time interval
a0	source fixlet of <bes action>: bes fixlet
a0	source fixlet of <bes baseline component>: bes fixlet
a0	source id of <bes fixlet>: string
a0	source id of <bes property>: integer
a0	source name of <bes property>: string
a0	source of <bes fixlet>: string
a0	source of <bes unmanagedasset>: string
10	source of <event log record>: string
10	source of <task registration info>: string
a0	source release date of <bes fixlet>: date
a0	source relevance of <bes action>: string
a0	source severity of <bes fixlet>: string
a0	source severity of <fixlet count pair>: string
bf	span <string> of <html>: html
bf	span <string> of <string>: html
bf	span of <html>: html
bf	span of <string>: html
2	speech folder of <domain>: folder
2	speech folder: folder
1f	speed of <dmi memory_device>: integer
1f	speed of <processor>: hertz
d	splashimage of <grub config file>: grub file location
1f	sqlite database of <file>: sqlite database
1f	sqlite version: version
bf	sqrt of <floating point>: floating point
bf	sqrt of <integer>: floating point
12	ssid of <wifi network>: string
12	ssid of <wifi>: string
2	stage <string>: stage
2	stage of <version>: stage
a0	standard deviation of <statistical bin>: floating point
bf	standard deviations of <floating point>: floating point
bf	standard deviations of <integer>: floating point
10	standard firewall profile type: firewall profile type
10	standard profile of <firewall policy>: firewall profile
12	standby state: power state
10	start boundary of <task trigger>: time
a0	start date of <bes action>: date
bf	start date of <license>: time
a0	start flag of <bes action>: boolean
10	start in pathname of <file shortcut>: string
bf	start of <binary_substring>: binary position
a0	start of <statistic range>: time
a0	start of <statistical bin>: time
bf	start of <substring>: string position
bf	start of <time range>: time
a0	start time of <bes action result>: time
d	start time of <process>: time
a0	start time_of_day of <bes action>: time of day
10	start type of <service>: string
10	start when available of <task settings>: boolean
1f	starting_address of <dmi memory_array_mapped_address>: integer
1f	starting_address of <dmi memory_device_mapped_address>: integer
2	startup items <string>: enableable_file
2	startup items folder of <domain>: folder
2	startup items folder: folder
2	startup items: enableable_file
12	state of <agent interface capability>: string
a0	state of <bes action>: string
bf	state of <bes product>: string
2	state of <dummy>: string
12	state of <monitor power interval>: power state
1d	state of <service>: string
12	state of <system power interval>: power state
1f	statement <string> of <sqlite database>: sqlite statement
2	static flag of <route>: boolean
2	stationery of <file>: boolean
a0	statistic range of <bes property>: statistic range
1f	status of <action>: string
10	status of <active device>: integer
a0	status of <bes action result>: bes action status
a0	status of <bes activation>: string
10	status of <connection>: connection status
1f	status of <dmi processor_information>: integer
10	status of <network adapter>: integer
2	stealth enabled of <firewall>: boolean
1f	stepping of <processor>: integer
d	sticky of <mode>: boolean
10	stop at duration end of <task repetition pattern>: boolean
10	stop existing instance of <task settings>: boolean
10	stop on idle end of <task idle settings>: boolean
a0	stop other actions flag of <bes user>: boolean
10	stop when going on battery of <task settings>: boolean
a0	stopper of <bes action>: bes user
1f	storage folder of <client>: folder
2	string <integer> of <array>: string
2	string <string> of <dictionary>: string
2	string <string> of <preference>: string
bf	string <string>: string
1f	string named files of <folder>: file
1f	string named folders of <folder>: folder
2	string of <osxvalue>: string
bf	string of <tuple item>: string
10	string value <integer> of <wmi select>: string
1f	string values <string> of <smbios structure>: smbios value
10	string values of <wmi select>: string
1f	string version of <application usage summary instance>: string
1f	strings <string> of <smbios structure>: string
bf	strong <string> of <html>: html
bf	strong <string> of <string>: html
bf	strong of <html>: html
bf	strong of <string>: html
1f	structure of <smbios value>: smbios structure
1f	structures <string> of <smbios>: smbios structure
1f	structures of <smbios>: smbios structure
d	strverscmp version <string>: strverscmp version
bf	sub <string> of <html>: html
bf	sub <string> of <string>: html
bf	sub of <html>: html
bf	sub of <string>: html
10	subcategories of <audit policy category>: audit policy subcategory
bf	subject common name of <x509 certificate>: string
10	subject of <email task action>: string
bf	subject of <x509 certificate>: string
1f	subnet address of <network adapter interface>: ipv4or6 address
1f	subnet address of <network adapter>: ipv4 address
10	subnet address of <network address list>: ipv4 address
1f	subnet address of <network ip interface>: ipv4 address
1a	subnet mask of <cidr subnet>: ipv4or6 address
1f	subnet mask of <network adapter interface>: ipv4or6 address
1f	subnet mask of <network adapter>: ipv4 address
10	subnet mask of <network address list>: ipv4 address
1f	subnet mask of <network ip interface>: ipv4 address
1f	subscribe time of <site>: time
a0	subscribed <( bes computer, bes site )>: boolean
a0	subscribed <( bes site, bes computer )>: boolean
a0	subscribed <bes computer> of <bes site>: boolean
a0	subscribed <bes site> of <bes computer>: boolean
a0	subscribed computer set of <bes site>: bes computer set
a0	subscribed computers of <bes site>: bes computer
a0	subscribed site set of <bes computer>: bes site set
a0	subscribed sites of <bes computer>: bes site
a0	subscription flag of <bes action>: boolean
a0	subscription mode of <bes site>: string
10	subscription of <event task trigger>: string
bf	substring <( integer, integer )> of <string>: substring
bf	substrings <string> of <string>: substring
bf	substrings after <string> of <string>: substring
bf	substrings before <string> of <string>: substring
bf	substrings between <string> of <string>: substring
bf	substrings separated by <string> of <string>: substring
2	subtype of <component>: string
a0	success on custom relevance of <bes action>: boolean
a0	success on custom relevance of <bes fixlet action>: boolean
a0	success on original relevance of <bes action>: boolean
a0	success on original relevance of <bes fixlet action>: boolean
a0	success on run to completion of <bes action>: boolean
a0	success on run to completion of <bes fixlet action>: boolean
a0	success rate of <statistical bin>: floating point
10	suite mask of <operating system>: operating system suite mask
bf	sums of <floating point>: floating point
bf	sums of <integer>: integer
bf	sums of <time interval>: time interval
bf	sunday: day of week
bf	sup <string> of <html>: html
bf	sup <string> of <string>: html
bf	sup of <html>: html
bf	sup of <string>: html
1f	supported_interleave of <dmi memory_controller_information>: integer
1f	supported_memory_types of <dmi memory_controller_information>: integer
1f	supported_speeds of <dmi memory_controller_information>: integer
1f	supported_sram_type of <dmi cache_information>: integer
f	swap: swap
bf	symbol of <binary operator>: string
bf	symbol of <unary operator>: string
d	symlink <binary_string> of <encoding>: symlink
d	symlink <binary_string> of <folder>: symlink
d	symlink <binary_string>: symlink
d	symlink <filesystem object>: symlink
d	symlink <string> of <encoding>: symlink
d	symlink <string> of <folder>: symlink
d	symlink <string>: symlink
d	symlink <symlink>: symlink
d	symlinks of <folder>: symlink
1f	syn received of <tcp state>: boolean
1f	syn sent of <tcp state>: boolean
10	synchronize permission of <access control entry>: boolean
10	system category of <audit policy>: audit policy category
1f	system constraint of <action>: integer
2	system domain: domain
10	system event log: event log
10	system file <string>: file
2	system folder of <domain>: folder
1f	system folder: folder
10	system group: security account
10	system ini device files <string>: file
10	system ini device files: file
12	system intervals of <power history>: system power interval
1d	system language: string
1d	system locale: language
10	system of <filesystem object>: boolean
10	system policy of <audit policy subcategory>: audit policy information
1d	system ui language: language
2	system version: version
10	system wow64 folder: folder
10	system x32 file <string>: file
10	system x32 folder: folder
10	system x64 file <string>: file
10	system x64 folder: folder
1f	system_bios_major_release of <dmi bios_information>: integer
1f	system_bios_minor_release of <dmi bios_information>: integer
1f	system_boot_information <integer> of <dmi>: dmi system_boot_information
1f	system_boot_informations of <dmi>: dmi system_boot_information
1f	system_cache_type of <dmi cache_information>: integer
1f	system_configuration_option <integer> of <dmi>: string
1f	system_configuration_options of <dmi>: string
1f	system_enclosure_or_chassis <integer> of <dmi>: dmi system_enclosure_or_chassis
1f	system_enclosure_or_chassiss of <dmi>: dmi system_enclosure_or_chassis
1f	system_information <integer> of <dmi>: dmi system_information
1f	system_informations of <dmi>: dmi system_information
1f	system_power_controls <integer> of <dmi>: dmi system_power_controls
1f	system_power_controlss of <dmi>: dmi system_power_controls
1f	system_power_supply <integer> of <dmi>: dmi system_power_supply
1f	system_power_supplys of <dmi>: dmi system_power_supply
1f	system_reset <integer> of <dmi>: dmi system_reset
1f	system_resets of <dmi>: dmi system_reset
1f	system_slots <integer> of <dmi>: dmi system_slots
1f	system_slotss of <dmi>: dmi system_slots
bf	table <string> of <html>: html
1f	table <string> of <sqlite database>: sqlite table
bf	table <string> of <string>: html
bf	table of <html>: html
bf	table of <string>: html
1f	tables of <sqlite database>: sqlite table
a0	tag of <bes site>: string
a0	taken action set of <bes fixlet>: bes action set
a0	taken actions of <bes fixlet>: bes action
10	target ip address of <port mapping>: ipv4 address
10	target ipv4or6 address of <port mapping>: ipv4or6 address
10	target name of <port mapping>: string
a0	targeted by id flag of <bes action>: boolean
a0	targeted by list flag of <bes action>: boolean
a0	targeted by property flag of <bes action>: boolean
a0	targeted computer set of <bes action>: bes computer set
a0	targeted computers of <bes action>: bes computer
a0	targeted list of <bes action>: string
a0	targeted names of <bes action>: string
a0	targeting method of <bes action>: string
a0	targeting relevance of <bes action>: string
10	task action type <integer>: task action type
a0	task flag of <bes filter>: boolean
a0	task flag of <bes fixlet>: boolean
10	task folder <string>: task folder
10	task folders of <task folder>: task folder
10	task name of <application>: string
a0	task set of <bes filter>: bes fixlet set
10	task trigger type <integer>: task trigger type
bf	tbody <string> of <html>: html
bf	tbody <string> of <string>: html
bf	tbody of <html>: html
bf	tbody of <string>: html
1f	tcp of <socket>: boolean
1f	tcp state of <socket>: tcp state
10	tcp: internet protocol
bf	td <string> of <html>: html
bf	td <string> of <string>: html
bf	td of <html>: html
bf	td of <string>: html
1f	temperature_probe <integer> of <dmi>: dmi temperature_probe
1f	temperature_probe_handle of <dmi cooling_device>: integer
1f	temperature_probes of <dmi>: dmi temperature_probe
10	template file of <site profile>: file
a0	temporal distribution of <bes action>: time interval
10	temporary duplicate account flag of <user>: boolean
2	temporary items folder of <domain>: folder
2	temporary items folder: folder
10	temporary of <filesystem object>: boolean
bf	term of <bes product>: boolean
10	terminal bit <operating system suite mask>: boolean
10	terminal server user group: security account
2	text encodings folder of <domain>: folder
2	text encodings folder: folder
a0	text of <bes comment>: string
1f	text of <sqlite column type>: boolean
bf	tfoot <string> of <html>: html
bf	tfoot <string> of <string>: html
bf	tfoot of <html>: html
bf	tfoot of <string>: html
bf	th <string> of <html>: html
bf	th <string> of <string>: html
bf	th of <html>: html
bf	th of <string>: html
bf	thead <string> of <html>: html
bf	thead <string> of <string>: html
bf	thead of <html>: html
bf	thead of <string>: html
2	themes folder of <domain>: folder
2	themes folder: folder
1f	thermal_state of <dmi system_enclosure_or_chassis>: integer
1f	thread of <cpupackage>: integer
1f	thread_count of <dmi processor_information>: integer
1f	threshold_handle of <dmi management_device_component>: integer
bf	thursday: day of week
bf	time <string>: time
bf	time <time zone> of <time>: time of day with time zone
10	time generated of <event log record>: time
bf	time interval <string>: time interval
a0	time issued of <bes action>: time
1f	time of <execution>: time
a0	time of <historical computer count>: time
a0	time of <historical fixlet count>: time
bf	time of <time of day with time zone>: time of day
a0	time range end of <bes action>: time of day
a0	time range start of <bes action>: time of day
a0	time stopped of <bes action>: time
10	time task trigger type: task trigger type
10	time value <integer> of <wmi select>: time
10	time values of <wmi select>: time
1f	time wait of <tcp state>: boolean
10	time written of <event log record>: time
bf	time zone <string>: time zone
bf	time_of_day <string>: time of day
1f	timeout of <dmi system_reset>: integer
d	timeout of <grub config file>: integer
1f	timer_interval of <dmi system_reset>: integer
a0	timestamp of <bes comment>: time
bf	title <string> of <html>: html
bf	title <string> of <string>: html
d	title of <grub bootable image>: string
bf	title of <html>: html
10	title of <show message task action>: string
bf	title of <string>: html
bf	tls cipher list of <license>: string
10	to of <email task action>: string
1f	tolerance of <dmi electrical_current_probe>: integer
1f	tolerance of <dmi temperature_probe>: integer
1f	tolerance of <dmi voltage_probe>: integer
a0	top level bes action set: bes action set
a0	top level bes actions: bes action
a0	top level flag of <bes action>: boolean
1f	total amount of <ram>: integer
f	total amount of <swap>: integer
1f	total duration of <application usage summary instance>: time interval
1f	total duration of <application usage summary>: time interval
1f	total duration of <evaluation cycle>: time interval
a0	total lower bound of <statistical bin>: floating point
a0	total of <statistic range>: statistical bin
10	total processor core count: integer
1f	total run count of <application usage summary instance>: integer
1f	total run count of <application usage summary>: integer
1f	total size of <download storage folder>: integer
10	total space of <drive>: integer
d	total space of <filesystem>: integer
2	total space of <volume>: integer
a0	total upper bound of <statistical bin>: floating point
1f	total_width of <dmi memory_device>: integer
a0	totals <time interval> of <statistic range>: statistical bin
bf	tr <string> of <html>: html
bf	tr <string> of <string>: html
bf	tr of <html>: html
bf	tr of <string>: html
1f	track fixlets of <evaluation cycle>: string
10	traverse permission of <access control entry>: boolean
10	trigger strings of <scheduled task>: string
10	triggers of <task definition>: task trigger
bf	true: boolean
10	trustee of <access control entry>: security identifier
10	trustee type of <access control entry>: integer
bf	tt <string> of <html>: html
bf	tt <string> of <string>: html
bf	tt of <html>: html
bf	tt of <string>: html
1f	tty of <logged on user>: string
d	tty of <process>: string
d	tty of <user>: string
bf	tuesday: day of week
10	tunnel of <network adapter>: boolean
bf	tuple items of <string>: tuple item
bf	tuple string item <integer> of <string>: string
bf	tuple string items of <string>: string
bf	tuple strings of <string>: string
bf	two digit hour of <time of day with time zone>: string
bf	two digit hour of <time of day>: string
bf	two digit minute of <time of day with time zone>: string
bf	two digit minute of <time of day>: string
bf	two digit second of <time of day with time zone>: string
bf	two digit second of <time of day>: string
bf	type <string>: type
d	type of <Xinetd Service>: string
a0	type of <bes fixlet>: string
2	type of <bundle>: file type
2	type of <component>: string
9	type of <debianpkg dependency>: string
b0	type of <distinguished name component>: string
1f	type of <dmi built_in_pointing_device>: integer
1f	type of <dmi management_device>: integer
1f	type of <dmi system_enclosure_or_chassis>: integer
10	type of <drive>: string
1f	type of <execution>: string
2	type of <file>: file type
d	type of <filesystem>: string
10	type of <firewall profile>: firewall profile type
10	type of <firewall service>: firewall service type
bf	type of <json value>: string
bf	type of <license>: string
10	type of <metabase value>: metabase type
10	type of <network adapter>: integer
10	type of <network share>: integer
2	type of <osxvalue>: string
10	type of <processor>: integer
2	type of <processor>: string
10	type of <registry key value>: registry key value type
2	type of <scsidevice>: string
1f	type of <site>: string
1f	type of <smbios structure>: integer
1f	type of <smbios value>: string
1f	type of <sqlite column type>: string
1f	type of <sqlite column>: sqlite column type
10	type of <task action>: task action type
10	type of <task trigger>: task trigger type
2	type of <volume>: string
10	type of <wmi select>: integer
1f	type_detail of <dmi memory_device>: integer
bf	types: type
1f	udp of <socket>: boolean
10	udp: internet protocol
a0	uid attribute of <bes ldap directory>: string
d	uid of <filesystem object>: integer
d	uid of <symlink>: integer
1a	uinteger <integer>: uinteger
1a	uinteger <string>: uinteger
bf	ul <string> of <html>: html
bf	ul <string> of <string>: html
bf	ul of <html>: html
bf	ul of <string>: html
bf	unary operators <string>: unary operator
bf	unary operators returning <type>: unary operator
bf	unary operators: unary operator
d	unavailable amount of <ram>: integer
bf	underflow of <floating point>: boolean
10	unicast responses to multicast broadcast disabled of <firewall profile>: boolean
a0	unions of <bes action set>: bes action set
a0	unions of <bes computer group set>: bes computer group set
a0	unions of <bes computer set>: bes computer set
a0	unions of <bes domain set>: bes domain set
a0	unions of <bes filter set>: bes filter set
a0	unions of <bes fixlet set>: bes fixlet set
a0	unions of <bes ldap directory set>: bes ldap directory set
a0	unions of <bes property set>: bes property set
a0	unions of <bes role set>: bes role set
a0	unions of <bes site file set>: bes site file set
a0	unions of <bes site set>: bes site set
a0	unions of <bes unmanagedasset set>: bes unmanagedasset set
a0	unions of <bes user set>: bes user set
a0	unions of <bes webui app set>: bes webui app set
a0	unions of <bes wizard set>: bes wizard set
bf	unions of <integer set>: integer set
bf	unions of <string set>: string set
1f	unique id of <cloud provider>: string
4	unique name of <package>: string
a0	unique values of <bes action>: bes action with multiplicity
a0	unique values of <bes computer group>: bes computer group with multiplicity
a0	unique values of <bes computer>: bes computer with multiplicity
a0	unique values of <bes domain>: bes domain with multiplicity
a0	unique values of <bes filter>: bes filter with multiplicity
a0	unique values of <bes fixlet>: bes fixlet with multiplicity
a0	unique values of <bes ldap directory>: bes ldap directory with multiplicity
a0	unique values of <bes property>: bes property with multiplicity
a0	unique values of <bes role>: bes role with multiplicity
a0	unique values of <bes site file>: bes site file with multiplicity
a0	unique values of <bes site>: bes site with multiplicity
a0	unique values of <bes unmanagedasset>: bes unmanagedasset with multiplicity
a0	unique values of <bes user>: bes user with multiplicity
a0	unique values of <bes webui app>: bes webui app with multiplicity
a0	unique values of <bes wizard>: bes wizard with multiplicity
bf	unique values of <date>: date with multiplicity
bf	unique values of <day of month>: day of month with multiplicity
bf	unique values of <day of week>: day of week with multiplicity
bf	unique values of <day of year>: day of year with multiplicity
9	unique values of <debian package upstream version>: debian package upstream version with multiplicity
9	unique values of <debian package version epoch>: debian package version epoch with multiplicity
9	unique values of <debian package version revision>: debian package version revision with multiplicity
9	unique values of <debian package version>: debian package version with multiplicity
bf	unique values of <floating point>: floating point with multiplicity
bf	unique values of <hertz>: hertz with multiplicity
bf	unique values of <integer>: integer with multiplicity
bf	unique values of <ipv4 address>: ipv4 address with multiplicity
bf	unique values of <ipv4or6 address>: ipv4or6 address with multiplicity
bf	unique values of <ipv6 address>: ipv6 address with multiplicity
1a	unique values of <large integer>: large integer with multiplicity
bf	unique values of <month and year>: month and year with multiplicity
bf	unique values of <month>: month with multiplicity
bf	unique values of <number of months>: number of months with multiplicity
a2	unique values of <rate>: rate with multiplicity
4	unique values of <rpm package release>: rpm package release with multiplicity
4	unique values of <rpm package version record>: rpm package version record with multiplicity
4	unique values of <rpm package version>: rpm package version with multiplicity
4	unique values of <short rpm package version record>: short rpm package version record with multiplicity
bf	unique values of <site version list>: site version list with multiplicity
bf	unique values of <string>: string with multiplicity
bf	unique values of <time interval>: time interval with multiplicity
bf	unique values of <time of day with time zone>: time of day with time zone with multiplicity
bf	unique values of <time of day>: time of day with multiplicity
bf	unique values of <time range>: time range with multiplicity
bf	unique values of <time zone>: time zone with multiplicity
bf	unique values of <time>: time with multiplicity
1a	unique values of <uinteger>: uinteger with multiplicity
1f	unique values of <uuid>: uuid with multiplicity
bf	unique values of <version>: version with multiplicity
bf	unique values of <year>: year with multiplicity
bf	universal time <string>: time
bf	universal time zone: time zone
1f	unix of <operating system>: boolean
a0	unknown computer count of <bes baseline component>: integer
a0	unknown computer set of <bes baseline component>: bes computer set
10	unknown state of <running task>: boolean
10	unknown state of <scheduled task>: boolean
a0	unlocked computer count of <bes fixlet>: integer
a0	unmanagedasset flag of <bes filter>: boolean
a0	unmanagedasset privilege scanpoint flag of <bes role>: boolean
a0	unmanagedasset privilege scanpoint flag of <bes user>: boolean
a0	unmanagedasset privilege showall flag of <bes role>: boolean
a0	unmanagedasset privilege showall flag of <bes user>: boolean
a0	unmanagedasset privilege shownone flag of <bes role>: boolean
a0	unmanagedasset privilege shownone flag of <bes user>: boolean
bf	unordered lists <string> of <html>: html
bf	unordered lists <string> of <string>: html
bf	unordered lists of <html>: html
bf	unordered lists of <string>: html
a0	untargeted flag of <bes action>: boolean
f	up flag of <route>: boolean
1f	up of <network adapter interface>: boolean
1f	up of <network adapter>: boolean
2	up of <network interface>: boolean
1f	up of <network ip interface>: boolean
d	update level of <operating system>: integer
1f	upload progress of <client>: string
10	upnp firewall service type: firewall service type
bf	upper bound of <integer range>: integer
1f	upper_threshold_critical of <dmi management_device_threshold_data>: integer
1f	upper_threshold_non_critical of <dmi management_device_threshold_data>: integer
1f	upper_threshold_non_recoverable of <dmi management_device_threshold_data>: integer
1f	ups of <power level>: boolean
9	upstream of <debian package version>: debian package upstream version
1f	uptime of <operating system>: time interval
a0	urgent flag of <bes action>: boolean
10	uri of <task registration info>: string
a0	url of <bes server>: string
a0	url of <bes site>: string
a0	url of <bes wizard>: string
1f	url of <site>: string
2	usb plane of <registryroot>: registrynode
2	usb: usb
10	use count of <network share>: integer
10	use limit of <network share>: integer
1f	use of <dmi physical_memory_array>: integer
a0	use ssl of <bes ldap directory>: boolean
1f	used amount of <ram>: integer
f	used amount of <swap>: integer
d	used file count of <filesystem>: integer
d	used percent of <filesystem>: integer
2	used percent of <volume>: integer
d	used space of <filesystem>: integer
2	used space of <volume>: integer
12	user <string>: user
10	user comment of <user>: string
1f	user count of <bes product>: integer
2	user domain: domain
d	user execute of <filesystem object>: boolean
a0	user filter of <bes ldap directory>: string
a0	user flag of <bes filter>: boolean
10	user id of <logon task trigger>: string
10	user id of <session state change task trigger>: string
10	user id of <task principal>: string
1f	user id of <user>: integer
10	user intervals <activity history>: system power interval
10	user key of <logged on user>: registry key
10	user language: string
10	user locale: language
d	user mask of <filesystem object>: integer
d	user mask of <mode>: mode_mask
d	user name of <filesystem object>: string
d	user name of <symlink>: string
10	user object count of <process>: integer
d	user of <Xinetd Service>: string
1f	user of <logged on user>: user
10	user of <process>: security identifier
d	user of <process>: user
12	user of <security identifier>: user
10	user privilege of <user>: boolean
d	user read of <filesystem object>: boolean
a0	user set of <bes filter>: bes user set
a0	user set of <bes role>: bes user set
10	user sid of <event log record>: security identifier
2	user temp folder of <domain>: folder
2	user temp folder: folder
10	user time of <process>: time interval
10	user type of <metabase value>: metabase user type
10	user ui language: language
d	user write of <filesystem object>: boolean
d	users <string>: user
2	users folder of <domain>: folder
2	users folder: folder
a0	users of <bes role>: bes user
1f	users: user
bf	usual name of <property>: string
a0	utc time flag of <bes action>: boolean
2	utilities folder of <domain>: folder
2	utilities folder: folder
1f	uuid <binary_string>: uuid
1f	uuid <string>: uuid
1f	uuid of <dmi system_information>: uuid
d	uuid of <filesystem>: string
1f	uuid of <hardware>: uuid
1f	uuid of <operating system>: uuid
10	v1 compatibility of <task settings>: boolean
10	v2 compatibility of <task settings>: boolean
10	value <string> of <file version block>: string
10	value <string> of <registry key>: registry key value
d	value accessible of <symlink>: boolean
a0	value count of <bes property result>: integer
a0	value of <bes action parameter>: string
a0	value of <bes client setting>: string
a0	value of <bes deployment option>: string
a0	value of <bes unmanagedasset field>: string
a0	value of <bes wizard variable>: string
2	value of <dictionaryentry>: osxvalue
b0	value of <distinguished name component>: string
1f	value of <environment variable>: string
1f	value of <fixlet_header>: string
bf	value of <json key>: json value
a0	value of <mime field>: string
14	value of <plugin store key>: string
d	value of <runlevel>: string
1f	value of <setting>: string
10	value of <site profile variable>: string
d	value of <symlink>: string
10	value of <task named value pair>: string
2	value of <user attribute>: string
10	value of <winrt enumeration>: integer
10	value queries of <event task trigger>: task named value pair
1f	values <string> of <smbios structure>: smbios value
2	values of <array>: osxvalue
a0	values of <bes fixlet field>: bes fixlet field value
a0	values of <bes property result>: string
10	values of <metabase key>: metabase value
10	values of <registry key>: registry key value
1f	values of <smbios structure>: smbios value
bf	var <string> of <html>: html
bf	var <string> of <string>: html
bf	var of <html>: html
bf	var of <string>: html
1f	variable <string> of <environment>: environment variable
10	variables <string> of <site profile>: site profile variable
a0	variables of <bes wizard>: bes wizard variable
1f	variables of <environment>: environment variable
1f	variables of <file>: string
10	variables of <site profile>: site profile variable
a0	variance of <statistical bin>: floating point
1f	vendor name of <processor>: string
1f	vendor of <dmi bios_information>: string
2	vendor of <scsidevice>: string
1f	vendor_syndrome of <dmi b32_bit_memory_error_information>: integer
1f	vendor_syndrome of <dmi b64_bit_memory_error_information>: integer
9	verfiles of <debian versioned package>: debianpkg verfile
2	version <integer> of <file>: version
bf	version <string>: version
10	version block <integer> of <file>: file version block
10	version block <string> of <file>: file version block
10	version blocks of <file>: file version block
1f	version info of <execution>: string
1f	version of <application usage summary instance>: version
a0	version of <bes site>: integer
1f	version of <bios>: string
2	version of <bundle>: version
4	version of <capability>: string
f	version of <client>: version
1f	version of <cloud provider>: string
2	version of <component>: version
bf	version of <cryptography>: string
1f	version of <current relay>: version
9	version of <debian versioned package>: debian package version
9	version of <debianpkg dependency>: debian package version
9	version of <debianpkg reverse dependencies>: string
1f	version of <dmi base_board_information>: string
1f	version of <dmi system_enclosure_or_chassis>: string
1f	version of <dmi system_information>: string
10	version of <file>: version
2	version of <filesystem object>: version
2	version of <folder>: version
bf	version of <module>: version
1f	version of <operating system>: version
4	version of <package>: version
1f	version of <registration server>: version
4	version of <rpm package version record>: rpm package version
2	version of <scsibus>: version
1d	version of <service>: version
4	version of <short rpm package version record>: rpm package version
1f	version of <site>: integer
10	version of <task registration info>: string
2	version of <usb>: version
10	version of <winrt package id>: version
bf	version of <x509 certificate>: integer
bf	version string <string> of <module>: string
10	version strings of <bios>: string
1f	virtual machine of <operating system>: boolean
2	virtual memory: boolean
1f	virtual of <hardware>: boolean
10	virtualizer of <application>: string
a0	visible flag of <bes fixlet>: boolean
12	visible networks of <wifi>: wifi network
2	visible of <file>: boolean
2	voices folder of <domain>: folder
2	voices folder: folder
10	volatile attribute of <metabase value>: boolean
1f	voltage of <dmi processor_information>: integer
1f	voltage_probe <integer> of <dmi>: dmi voltage_probe
1f	voltage_probes of <dmi>: dmi voltage_probe
2	volume <integer>: volume
10	volume of <drive>: string
2	volume of <file>: volume
d	volume of <filesystem>: string
2	volume of <folder>: volume
2	volume settings folder of <domain>: folder
2	volume settings folder: folder
2	volumes <string>: volume
2	volumes: volume
d	wait of <Xinetd Service>: boolean
10	wait timeout of <task idle settings>: time interval
1f	waiting for download of <action>: boolean
1a	wake on lan cidr subnet: cidr subnet
1f	wake on lan subnet cidr string: string
10	wake to run of <task settings>: boolean
1f	wake_up_type of <dmi system_information>: integer
10	wakeonlan enabled of <network adapter>: boolean
10	warning event log event type: event log event type
2	wascloned flag of <route>: boolean
d	web reports service: service
a0	webui enabled: boolean
1d	webui service: service
bf	wednesday: day of week
bf	week: time interval
10	weekly task trigger type: task trigger type
10	weeks interval of <weekly task trigger>: time interval
1f	weight of <selected server>: integer
10	well known account <integer>: security account
2	wide16 scsi of <scsibus>: boolean
2	wide32 scsi of <scsibus>: boolean
12	wifi of <network adapter>: wifi
10	win32 exit code of <service>: integer
10	win32 running services: service
10	win32 services: service
10	win32 type of <service>: boolean
d	window of <route>: integer
10	windows checksum of <file>: integer
b0	windows display time <string>: time
10	windows file <string>: file
10	windows folder: folder
1f	windows of <operating system>: boolean
bf	windows server count of <bes product>: integer
10	winrt package <string>: winrt package
10	winrt package users of <winrt package>: winrt package user information
10	winrt packages of <user>: winrt package
10	winrt packages: winrt package
10	wins enabled of <network adapter>: boolean
10	winsock2 supported of <network>: boolean
a0	wizard data of <bes fixlet>: html
a0	wizard link of <bes fixlet>: string
a0	wizard name of <bes fixlet>: string
a0	wizard of <bes wizard variable>: bes wizard
a0	wizard set of <bes site>: bes wizard set
a0	wizards of <bes site>: bes wizard
10	wmi <string>: wmi
10	wmi: wmi
10	working directory of <exec task action>: string
10	working set size of <process>: integer
bf	workstation count of <bes product>: integer
10	workstation trust account flag of <user>: boolean
10	wow64 of <process>: boolean
10	wow64 of <registry key>: boolean
d	wp of <processor>: boolean
10	write attributes permission of <access control entry>: boolean
10	write dac permission of <access control entry>: boolean
10	write extended attributes permission of <access control entry>: boolean
d	write of <mode_mask>: boolean
10	write owner permission of <access control entry>: boolean
10	write permission of <access control entry>: boolean
10	write permission of <network share>: boolean
a0	writer set of <bes site>: bes user set
a0	writers of <bes site>: bes user
10	x32 application <string>: application
10	x32 file <string> of <encoding>: file
10	x32 file <string>: file
10	x32 folder <string> of <encoding>: folder
10	x32 folder <string>: folder
10	x32 of <operating system>: boolean
10	x32 registry: registry
10	x64 application <string>: application
10	x64 file <string> of <encoding>: file
10	x64 file <string>: file
10	x64 folder <string> of <encoding>: folder
10	x64 folder <string>: folder
10	x64 of <operating system>: boolean
10	x64 registry: registry
10	x64 variable <string> of <environment>: environment variable
10	x64 variables of <environment>: environment variable
d	xinetd services <string>: Xinetd Service
d	xinetd services: Xinetd Service
1d	xml document of <file>: xml dom document
bd	xml document of <string>: xml dom document
10	xml of <event log record>: xml dom node
10	xml of <scheduled task>: string
10	xml of <task definition>: string
10	xml of <task registration info>: string
10	xml of <task settings>: string
bd	xpaths <( string, string )> of <xml dom node>: xml dom node
bd	xpaths <string> of <xml dom node>: xml dom node
2	xresolve flag of <route>: boolean
bf	year <integer>: year
bf	year <string>: year
bf	year of <date>: year
bf	year of <month and year>: year
bf	year: number of months
bf	zone of <time of day with time zone>: time zone
bf	zoned time_of_day <string>: time of day with time zone
"""

# 427 rows
TYPES: str = """\
10	access control entry
10	access control list
12	action
12	action lock state
10	active device
12	active directory group
12	active directory local computer
12	active directory local user
12	active directory server
10	activity history
12	administrative rights
12	agent interface
12	agent interface capability
12	analysis
12	application
12	application usage summary
12	application usage summary instance
2	array
10	audit policy
10	audit policy category
10	audit policy information
10	audit policy subcategory
40	bes action
40	bes action parameter
40	bes action result
40	bes action set
40	bes action status
40	bes action with multiplicity
40	bes activation
40	bes baseline component
40	bes baseline component group
40	bes client setting
40	bes comment
40	bes computer
40	bes computer group
40	bes computer group set
40	bes computer group with multiplicity
40	bes computer set
40	bes computer with multiplicity
40	bes deployment option
40	bes domain
40	bes domain set
40	bes domain with multiplicity
40	bes filter
40	bes filter set
40	bes filter with multiplicity
40	bes fixlet
40	bes fixlet action
40	bes fixlet field
40	bes fixlet field value
40	bes fixlet result
40	bes fixlet set
40	bes fixlet with multiplicity
40	bes idp directory
40	bes idp directory server
40	bes idp directory set
40	bes idp directory with multiplicity
40	bes ldap directory
40	bes ldap directory server
40	bes ldap directory set
40	bes ldap directory with multiplicity
40	bes peer download
40	bes peer download with multiplicity
52	bes product
40	bes property
40	bes property result
40	bes property set
40	bes property with multiplicity
40	bes role
40	bes role set
40	bes role with multiplicity
40	bes server
40	bes site
40	bes site file
40	bes site file set
40	bes site file with multiplicity
40	bes site set
40	bes site with multiplicity
40	bes tag
40	bes unmanagedasset
40	bes unmanagedasset field
40	bes unmanagedasset set
40	bes unmanagedasset with multiplicity
40	bes user
40	bes user set
40	bes user with multiplicity
40	bes wakeonlan status
40	bes webui
40	bes webui app
40	bes webui app set
40	bes webui app with multiplicity
40	bes wizard
40	bes wizard set
40	bes wizard variable
40	bes wizard with multiplicity
52	binary operator
52	binary position
52	binary_string
52	binary_substring
12	bios
52	bit set
52	boolean
10	boot task trigger
2	bundle
52	cast
12	cidr subnet
12	client
2	client process owner
12	client_cryptography
12	cloud provider
10	com handler task action
2	component
2	computer
10	connection
10	connection status
2	country
12	cpupackage
52	cryptography
12	current relay
10	daily task trigger
2	datafork
52	date
52	date with multiplicity
52	day of month
52	day of month with multiplicity
52	day of week
52	day of week with multiplicity
52	day of year
52	day of year with multiplicity
2	dictionary
2	dictionaryentry
10	discretionary access control list
10	distinguished name
10	distinguished name component
10	dmi
12	dmi additional_information
12	dmi b32_bit_memory_error_information
12	dmi b64_bit_memory_error_information
12	dmi base_board_information
12	dmi bios_information
12	dmi bios_language_information
12	dmi built_in_pointing_device
12	dmi cache_information
12	dmi cooling_device
12	dmi electrical_current_probe
12	dmi end_of_table
12	dmi group_associations
12	dmi hardware_security
12	dmi inactive
12	dmi ipmi_device_information
12	dmi management_device
12	dmi management_device_component
12	dmi management_device_threshold_data
12	dmi memory_array_mapped_address
12	dmi memory_channel
12	dmi memory_controller_information
12	dmi memory_device
12	dmi memory_device_mapped_address
12	dmi memory_module_information
12	dmi oem_strings
12	dmi on_board_devices_information
12	dmi onboard_devices_extended_information
12	dmi out_of_band_remote_access
12	dmi physical_memory_array
12	dmi port_connector_information
12	dmi portable_battery
12	dmi processor_information
12	dmi system_boot_information
12	dmi system_configuration_option
12	dmi system_enclosure_or_chassis
12	dmi system_information
12	dmi system_power_controls
12	dmi system_power_supply
12	dmi system_reset
12	dmi system_slots
12	dmi temperature_probe
12	dmi voltage_probe
2	domain
12	download server
12	download storage folder
10	drive
2	dummy
2	dummy type
10	email task action
2	enableable_file
12	encoding
12	environment
12	environment variable
12	evaluation cycle
10	event log
10	event log event type
10	event log record
10	event task trigger
10	exec task action
12	execution
42	exponential projection
12	file
12	file content
12	file line
12	file section
10	file shortcut
2	file signature
2	file type
10	file version block
12	filesystem object
12	firewall
12	firewall action
10	firewall authorized application
10	firewall icmp settings
10	firewall local policy modify state
10	firewall open port
10	firewall policy
10	firewall profile
10	firewall profile type
10	firewall remote admin settings
12	firewall rule
10	firewall scope
10	firewall service
10	firewall service restriction
10	firewall service type
12	fixlet
40	fixlet count pair
12	fixlet_header
52	floating point
52	floating point with multiplicity
12	folder
52	format
12	hardware
52	hertz
52	hertz with multiplicity
40	historical computer count
40	historical fixlet count
52	html
52	html attribute list
10	idle task trigger
12	instance data
52	integer
52	integer range
52	integer set
52	integer with multiplicity
10	internet connection firewall
10	internet protocol
52	ip version
52	ipv4 address
52	ipv4 address with multiplicity
52	ipv4or6 address
52	ipv4or6 address with multiplicity
52	ipv6 address
52	ipv6 address with multiplicity
52	json key
52	json value
10	language
52	large integer
52	large integer with multiplicity
52	license
42	linear projection
10	local group
10	local group member
10	local mssql database
12	logged on user
10	logon task trigger
12	manual group
10	media type
10	metabase
10	metabase identifier
10	metabase key
10	metabase type
10	metabase user type
10	metabase value
40	mime field
52	module
12	monitor power interval
52	month
52	month and year
52	month and year with multiplicity
52	month with multiplicity
10	monthly task trigger
10	monthlydow task trigger
12	network
12	network adapter
12	network adapter interface
10	network address list
12	network interface
12	network ip interface
2	network link interface
10	network share
2	nothing
52	number of months
52	number of months with multiplicity
12	operating system
10	operating system product type
10	operating system suite mask
2	os log entry log
2	os log store
2	osxvalue
10	plugin store
10	plugin store key
10	port mapping
12	power history
12	power level
12	power state
2	preference
10	primary language
10	priority class
12	process
12	processor
52	property
12	ram
42	rate
42	rate with multiplicity
12	registration server
10	registration task trigger
10	registry
10	registry key
10	registry key value
10	registry key value type
2	registrynode
2	registryroot
52	regular expression
52	regular expression match
2	resfork
12	restricted site
12	root server
52	rope
2	route
2	routing table
10	running task
10	scheduled task
2	scsibus
2	scsidevice
10	security account
10	security database
10	security descriptor
12	security identifier
12	selected server
12	server based group
10	service
10	session state change task trigger
12	setting
10	show message task action
12	site
12	site group
10	site profile
10	site profile variable
52	site version list
52	site version list with multiplicity
12	smbios
12	smbios structure
12	smbios value
12	socket
12	sqlite column
12	sqlite column type
12	sqlite database
12	sqlite row
12	sqlite statement
12	sqlite table
2	stage
40	statistic range
40	statistical bin
52	string
52	string position
52	string set
52	string with multiplicity
40	strverscmp version
52	substring
2	swap
10	system access control list
12	system power interval
10	task action
10	task action type
10	task definition
10	task folder
10	task idle settings
10	task named value pair
10	task network settings
10	task principal
10	task registration info
10	task repetition pattern
10	task settings
10	task trigger
10	task trigger type
12	tcp state
52	time
52	time interval
52	time interval with multiplicity
52	time of day
52	time of day with multiplicity
52	time of day with time zone
52	time of day with time zone with multiplicity
52	time range
52	time range with multiplicity
10	time task trigger
52	time with multiplicity
52	time zone
52	time zone with multiplicity
52	tuple item
52	type
52	uinteger
52	uinteger with multiplicity
52	unary operator
52	undefined
2	usb
12	user
2	user attribute
52	utf8 string
12	uuid
12	uuid with multiplicity
52	version
52	version with multiplicity
2	volume
10	weekly task trigger
12	wifi
12	wifi network
10	winrt enumeration
10	winrt package
10	winrt package id
10	winrt package user information
10	wmi
10	wmi object
10	wmi select
52	x509 certificate
10	xml dom document
10	xml dom node
2	yaml key
2	yaml value
52	year
52	year with multiplicity
"""

# 7 rows
UNARY_OPERATORS: str = """\
52	- <floating point>: floating point
52	- <hertz>: hertz
52	- <integer>: integer
52	- <large integer>: large integer
52	- <number of months>: number of months
42	- <rate>: rate
52	- <time interval>: time interval
"""
