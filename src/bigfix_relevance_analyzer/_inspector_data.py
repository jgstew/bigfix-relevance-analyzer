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
40	<bes action set> * <bes action set>: bes action set	times	*	bes action set	bes action set	bes action set
40	<bes action set> + <bes action set>: bes action set	plus	+	bes action set	bes action set	bes action set
40	<bes action set> - <bes action set>: bes action set	minus	-	bes action set	bes action set	bes action set
40	<bes action set> = <bes action set>: boolean	equal	=	bes action set	bes action set	boolean
40	<bes action set> contains <bes action set>: boolean	contains	contains	bes action set	bes action set	boolean
40	<bes action set> contains <bes action>: boolean	contains	contains	bes action set	bes action	boolean
40	<bes action status> = <bes action status>: boolean	equal	=	bes action status	bes action status	boolean
40	<bes action> = <bes action>: boolean	equal	=	bes action	bes action	boolean
40	<bes computer group set> * <bes computer group set>: bes computer group set	times	*	bes computer group set	bes computer group set	bes computer group set
40	<bes computer group set> + <bes computer group set>: bes computer group set	plus	+	bes computer group set	bes computer group set	bes computer group set
40	<bes computer group set> - <bes computer group set>: bes computer group set	minus	-	bes computer group set	bes computer group set	bes computer group set
40	<bes computer group set> = <bes computer group set>: boolean	equal	=	bes computer group set	bes computer group set	boolean
40	<bes computer group set> contains <bes computer group set>: boolean	contains	contains	bes computer group set	bes computer group set	boolean
40	<bes computer group set> contains <bes computer group>: boolean	contains	contains	bes computer group set	bes computer group	boolean
40	<bes computer group> = <bes computer group>: boolean	equal	=	bes computer group	bes computer group	boolean
40	<bes computer set> * <bes computer set>: bes computer set	times	*	bes computer set	bes computer set	bes computer set
40	<bes computer set> + <bes computer set>: bes computer set	plus	+	bes computer set	bes computer set	bes computer set
40	<bes computer set> - <bes computer set>: bes computer set	minus	-	bes computer set	bes computer set	bes computer set
40	<bes computer set> = <bes computer set>: boolean	equal	=	bes computer set	bes computer set	boolean
40	<bes computer set> contains <bes computer set>: boolean	contains	contains	bes computer set	bes computer set	boolean
40	<bes computer set> contains <bes computer>: boolean	contains	contains	bes computer set	bes computer	boolean
40	<bes computer> = <bes computer>: boolean	equal	=	bes computer	bes computer	boolean
40	<bes domain set> * <bes domain set>: bes domain set	times	*	bes domain set	bes domain set	bes domain set
40	<bes domain set> + <bes domain set>: bes domain set	plus	+	bes domain set	bes domain set	bes domain set
40	<bes domain set> - <bes domain set>: bes domain set	minus	-	bes domain set	bes domain set	bes domain set
40	<bes domain set> = <bes domain set>: boolean	equal	=	bes domain set	bes domain set	boolean
40	<bes domain set> contains <bes domain set>: boolean	contains	contains	bes domain set	bes domain set	boolean
40	<bes domain set> contains <bes domain>: boolean	contains	contains	bes domain set	bes domain	boolean
40	<bes domain> = <bes domain>: boolean	equal	=	bes domain	bes domain	boolean
40	<bes filter set> * <bes filter set>: bes filter set	times	*	bes filter set	bes filter set	bes filter set
40	<bes filter set> + <bes filter set>: bes filter set	plus	+	bes filter set	bes filter set	bes filter set
40	<bes filter set> - <bes filter set>: bes filter set	minus	-	bes filter set	bes filter set	bes filter set
40	<bes filter set> = <bes filter set>: boolean	equal	=	bes filter set	bes filter set	boolean
40	<bes filter set> contains <bes filter set>: boolean	contains	contains	bes filter set	bes filter set	boolean
40	<bes filter set> contains <bes filter>: boolean	contains	contains	bes filter set	bes filter	boolean
40	<bes filter> = <bes filter>: boolean	equal	=	bes filter	bes filter	boolean
40	<bes fixlet set> * <bes fixlet set>: bes fixlet set	times	*	bes fixlet set	bes fixlet set	bes fixlet set
40	<bes fixlet set> + <bes fixlet set>: bes fixlet set	plus	+	bes fixlet set	bes fixlet set	bes fixlet set
40	<bes fixlet set> - <bes fixlet set>: bes fixlet set	minus	-	bes fixlet set	bes fixlet set	bes fixlet set
40	<bes fixlet set> = <bes fixlet set>: boolean	equal	=	bes fixlet set	bes fixlet set	boolean
40	<bes fixlet set> contains <bes fixlet set>: boolean	contains	contains	bes fixlet set	bes fixlet set	boolean
40	<bes fixlet set> contains <bes fixlet>: boolean	contains	contains	bes fixlet set	bes fixlet	boolean
40	<bes fixlet> = <bes fixlet>: boolean	equal	=	bes fixlet	bes fixlet	boolean
40	<bes idp directory set> * <bes idp directory set>: bes idp directory set	times	*	bes idp directory set	bes idp directory set	bes idp directory set
40	<bes idp directory set> + <bes idp directory set>: bes idp directory set	plus	+	bes idp directory set	bes idp directory set	bes idp directory set
40	<bes idp directory set> - <bes idp directory set>: bes idp directory set	minus	-	bes idp directory set	bes idp directory set	bes idp directory set
40	<bes idp directory set> = <bes idp directory set>: boolean	equal	=	bes idp directory set	bes idp directory set	boolean
40	<bes idp directory set> contains <bes idp directory set>: boolean	contains	contains	bes idp directory set	bes idp directory set	boolean
40	<bes idp directory set> contains <bes idp directory>: boolean	contains	contains	bes idp directory set	bes idp directory	boolean
40	<bes idp directory> = <bes idp directory>: boolean	equal	=	bes idp directory	bes idp directory	boolean
40	<bes ldap directory set> * <bes ldap directory set>: bes ldap directory set	times	*	bes ldap directory set	bes ldap directory set	bes ldap directory set
40	<bes ldap directory set> + <bes ldap directory set>: bes ldap directory set	plus	+	bes ldap directory set	bes ldap directory set	bes ldap directory set
40	<bes ldap directory set> - <bes ldap directory set>: bes ldap directory set	minus	-	bes ldap directory set	bes ldap directory set	bes ldap directory set
40	<bes ldap directory set> = <bes ldap directory set>: boolean	equal	=	bes ldap directory set	bes ldap directory set	boolean
40	<bes ldap directory set> contains <bes ldap directory set>: boolean	contains	contains	bes ldap directory set	bes ldap directory set	boolean
40	<bes ldap directory set> contains <bes ldap directory>: boolean	contains	contains	bes ldap directory set	bes ldap directory	boolean
40	<bes ldap directory> = <bes ldap directory>: boolean	equal	=	bes ldap directory	bes ldap directory	boolean
40	<bes peer download> < <bes peer download>: boolean	less than	<	bes peer download	bes peer download	boolean
40	<bes peer download> = <bes peer download>: boolean	equal	=	bes peer download	bes peer download	boolean
40	<bes property set> * <bes property set>: bes property set	times	*	bes property set	bes property set	bes property set
40	<bes property set> + <bes property set>: bes property set	plus	+	bes property set	bes property set	bes property set
40	<bes property set> - <bes property set>: bes property set	minus	-	bes property set	bes property set	bes property set
40	<bes property set> = <bes property set>: boolean	equal	=	bes property set	bes property set	boolean
40	<bes property set> contains <bes property set>: boolean	contains	contains	bes property set	bes property set	boolean
40	<bes property set> contains <bes property>: boolean	contains	contains	bes property set	bes property	boolean
40	<bes property> = <bes property>: boolean	equal	=	bes property	bes property	boolean
40	<bes role set> * <bes role set>: bes role set	times	*	bes role set	bes role set	bes role set
40	<bes role set> + <bes role set>: bes role set	plus	+	bes role set	bes role set	bes role set
40	<bes role set> - <bes role set>: bes role set	minus	-	bes role set	bes role set	bes role set
40	<bes role set> = <bes role set>: boolean	equal	=	bes role set	bes role set	boolean
40	<bes role set> contains <bes role set>: boolean	contains	contains	bes role set	bes role set	boolean
40	<bes role set> contains <bes role>: boolean	contains	contains	bes role set	bes role	boolean
40	<bes role> = <bes role>: boolean	equal	=	bes role	bes role	boolean
40	<bes site file set> * <bes site file set>: bes site file set	times	*	bes site file set	bes site file set	bes site file set
40	<bes site file set> + <bes site file set>: bes site file set	plus	+	bes site file set	bes site file set	bes site file set
40	<bes site file set> - <bes site file set>: bes site file set	minus	-	bes site file set	bes site file set	bes site file set
40	<bes site file set> = <bes site file set>: boolean	equal	=	bes site file set	bes site file set	boolean
40	<bes site file set> contains <bes site file set>: boolean	contains	contains	bes site file set	bes site file set	boolean
40	<bes site file set> contains <bes site file>: boolean	contains	contains	bes site file set	bes site file	boolean
40	<bes site file> = <bes site file>: boolean	equal	=	bes site file	bes site file	boolean
40	<bes site set> * <bes site set>: bes site set	times	*	bes site set	bes site set	bes site set
40	<bes site set> + <bes site set>: bes site set	plus	+	bes site set	bes site set	bes site set
40	<bes site set> - <bes site set>: bes site set	minus	-	bes site set	bes site set	bes site set
40	<bes site set> = <bes site set>: boolean	equal	=	bes site set	bes site set	boolean
40	<bes site set> contains <bes site set>: boolean	contains	contains	bes site set	bes site set	boolean
40	<bes site set> contains <bes site>: boolean	contains	contains	bes site set	bes site	boolean
40	<bes site> = <bes site>: boolean	equal	=	bes site	bes site	boolean
40	<bes unmanagedasset set> * <bes unmanagedasset set>: bes unmanagedasset set	times	*	bes unmanagedasset set	bes unmanagedasset set	bes unmanagedasset set
40	<bes unmanagedasset set> + <bes unmanagedasset set>: bes unmanagedasset set	plus	+	bes unmanagedasset set	bes unmanagedasset set	bes unmanagedasset set
40	<bes unmanagedasset set> - <bes unmanagedasset set>: bes unmanagedasset set	minus	-	bes unmanagedasset set	bes unmanagedasset set	bes unmanagedasset set
40	<bes unmanagedasset set> = <bes unmanagedasset set>: boolean	equal	=	bes unmanagedasset set	bes unmanagedasset set	boolean
40	<bes unmanagedasset set> contains <bes unmanagedasset set>: boolean	contains	contains	bes unmanagedasset set	bes unmanagedasset set	boolean
40	<bes unmanagedasset set> contains <bes unmanagedasset>: boolean	contains	contains	bes unmanagedasset set	bes unmanagedasset	boolean
40	<bes unmanagedasset> = <bes unmanagedasset>: boolean	equal	=	bes unmanagedasset	bes unmanagedasset	boolean
40	<bes user set> * <bes user set>: bes user set	times	*	bes user set	bes user set	bes user set
40	<bes user set> + <bes user set>: bes user set	plus	+	bes user set	bes user set	bes user set
40	<bes user set> - <bes user set>: bes user set	minus	-	bes user set	bes user set	bes user set
40	<bes user set> = <bes user set>: boolean	equal	=	bes user set	bes user set	boolean
40	<bes user set> contains <bes user set>: boolean	contains	contains	bes user set	bes user set	boolean
40	<bes user set> contains <bes user>: boolean	contains	contains	bes user set	bes user	boolean
40	<bes user> = <bes user>: boolean	equal	=	bes user	bes user	boolean
40	<bes webui app set> * <bes webui app set>: bes webui app set	times	*	bes webui app set	bes webui app set	bes webui app set
40	<bes webui app set> + <bes webui app set>: bes webui app set	plus	+	bes webui app set	bes webui app set	bes webui app set
40	<bes webui app set> - <bes webui app set>: bes webui app set	minus	-	bes webui app set	bes webui app set	bes webui app set
40	<bes webui app set> = <bes webui app set>: boolean	equal	=	bes webui app set	bes webui app set	boolean
40	<bes webui app set> contains <bes webui app set>: boolean	contains	contains	bes webui app set	bes webui app set	boolean
40	<bes webui app set> contains <bes webui app>: boolean	contains	contains	bes webui app set	bes webui app	boolean
40	<bes webui app> = <bes webui app>: boolean	equal	=	bes webui app	bes webui app	boolean
40	<bes wizard set> * <bes wizard set>: bes wizard set	times	*	bes wizard set	bes wizard set	bes wizard set
40	<bes wizard set> + <bes wizard set>: bes wizard set	plus	+	bes wizard set	bes wizard set	bes wizard set
40	<bes wizard set> - <bes wizard set>: bes wizard set	minus	-	bes wizard set	bes wizard set	bes wizard set
40	<bes wizard set> = <bes wizard set>: boolean	equal	=	bes wizard set	bes wizard set	boolean
40	<bes wizard set> contains <bes wizard set>: boolean	contains	contains	bes wizard set	bes wizard set	boolean
40	<bes wizard set> contains <bes wizard>: boolean	contains	contains	bes wizard set	bes wizard	boolean
40	<bes wizard> = <bes wizard>: boolean	equal	=	bes wizard	bes wizard	boolean
52	<binary_string> & <binary_string>: binary_string	concatenate	&	binary_string	binary_string	binary_string
52	<binary_string> < <binary_string>: boolean	less than	<	binary_string	binary_string	boolean
52	<binary_string> <= <binary_string>: boolean	less than or equal	<=	binary_string	binary_string	boolean
52	<binary_string> = <binary_string>: boolean	equal	=	binary_string	binary_string	boolean
52	<binary_string> contains <binary_string>: boolean	contains	contains	binary_string	binary_string	boolean
52	<binary_string> ends with <binary_string>: boolean	ends with	ends with	binary_string	binary_string	boolean
52	<binary_string> starts with <binary_string>: boolean	starts with	starts with	binary_string	binary_string	boolean
52	<bit set> * <bit set>: bit set	times	*	bit set	bit set	bit set
52	<bit set> + <bit set>: bit set	plus	+	bit set	bit set	bit set
52	<bit set> - <bit set>: bit set	minus	-	bit set	bit set	bit set
52	<bit set> = <bit set>: boolean	equal	=	bit set	bit set	boolean
52	<bit set> contains <bit set>: boolean	contains	contains	bit set	bit set	boolean
52	<boolean> * <time range>: timed( time range, boolean )	times	*	boolean	time range	timed( time range, boolean )
52	<boolean> = <boolean>: boolean	equal	=	boolean	boolean	boolean
12	<cidr subnet> = <cidr subnet>: boolean
12	<cidr subnet> = <string>: boolean
12	<cidr subnet> contains <cidr subnet>: boolean
12	<cidr subnet> contains <ipv4 address>: boolean
12	<cidr subnet> contains <ipv4or6 address>: boolean
12	<cidr subnet> contains <ipv6 address>: boolean
10	<connection status> = <connection status>: boolean
2	<country> = <country>: boolean
52	<date> & <time of day with time zone>: time	concatenate	&	date	time of day with time zone	time
52	<date> + <number of months>: date	plus	+	date	number of months	date
52	<date> + <time interval>: date	plus	+	date	time interval	date
52	<date> - <date>: time interval	minus	-	date	date	time interval
52	<date> - <number of months>: date	minus	-	date	number of months	date
52	<date> - <time interval>: date	minus	-	date	time interval	date
52	<date> < <date>: boolean	less than	<	date	date	boolean
52	<date> <= <date>: boolean	less than or equal	<=	date	date	boolean
52	<date> = <date>: boolean	equal	=	date	date	boolean
52	<day of month> & <month and year>: date	concatenate	&	day of month	month and year	date
52	<day of month> & <month>: day of year	concatenate	&	day of month	month	day of year
52	<day of month> + <time interval>: day of month	plus	+	day of month	time interval	day of month
52	<day of month> - <day of month>: time interval	minus	-	day of month	day of month	time interval
52	<day of month> - <time interval>: day of month	minus	-	day of month	time interval	day of month
52	<day of month> < <day of month>: boolean	less than	<	day of month	day of month	boolean
52	<day of month> <= <day of month>: boolean	less than or equal	<=	day of month	day of month	boolean
52	<day of month> = <day of month>: boolean	equal	=	day of month	day of month	boolean
52	<day of week> + <time interval>: day of week	plus	+	day of week	time interval	day of week
52	<day of week> - <day of week>: time interval	minus	-	day of week	day of week	time interval
52	<day of week> - <time interval>: day of week	minus	-	day of week	time interval	day of week
52	<day of week> = <day of week>: boolean	equal	=	day of week	day of week	boolean
52	<day of year> & <month and year>: date	concatenate	&	day of year	month and year	date
52	<day of year> & <year>: date	concatenate	&	day of year	year	date
52	<day of year> + <number of months>: day of year	plus	+	day of year	number of months	day of year
52	<day of year> + <time interval>: day of year	plus	+	day of year	time interval	day of year
52	<day of year> - <day of year>: time interval	minus	-	day of year	day of year	time interval
52	<day of year> - <number of months>: day of year	minus	-	day of year	number of months	day of year
52	<day of year> - <time interval>: day of year	minus	-	day of year	time interval	day of year
52	<day of year> < <day of year>: boolean	less than	<	day of year	day of year	boolean
52	<day of year> <= <day of year>: boolean	less than or equal	<=	day of year	day of year	boolean
52	<day of year> = <day of year>: boolean	equal	=	day of year	day of year	boolean
10	<event log event type> = <event log event type>: boolean
12	<file content> contains <string>: boolean
2	<file signature> = <file signature>: boolean
2	<file type> = <file type>: boolean
12	<firewall action> = <firewall action>: boolean
10	<firewall local policy modify state> = <firewall local policy modify state>: boolean
10	<firewall profile type> = <firewall profile type>: boolean
10	<firewall scope> = <firewall scope>: boolean
10	<firewall service type> = <firewall service type>: boolean
52	<floating point> * <floating point>: floating point	times	*	floating point	floating point	floating point
52	<floating point> * <integer>: floating point	times	*	floating point	integer	floating point
42	<floating point> * <rate>: rate	times	*	floating point	rate	rate
52	<floating point> + <floating point>: floating point	plus	+	floating point	floating point	floating point
52	<floating point> + <integer>: floating point	plus	+	floating point	integer	floating point
52	<floating point> - <floating point>: floating point	minus	-	floating point	floating point	floating point
52	<floating point> - <integer>: floating point	minus	-	floating point	integer	floating point
52	<floating point> / <floating point>: floating point	divide	/	floating point	floating point	floating point
52	<floating point> / <integer>: floating point	divide	/	floating point	integer	floating point
42	<floating point> / <time interval>: rate	divide	/	floating point	time interval	rate
52	<floating point> < <floating point>: boolean	less than	<	floating point	floating point	boolean
52	<floating point> < <integer>: boolean	less than	<	floating point	integer	boolean
52	<floating point> <= <floating point>: boolean	less than or equal	<=	floating point	floating point	boolean
52	<floating point> <= <integer>: boolean	less than or equal	<=	floating point	integer	boolean
52	<floating point> = <floating point>: boolean	equal	=	floating point	floating point	boolean
52	<floating point> = <integer>: boolean	equal	=	floating point	integer	boolean
52	<format> + <date>: format	plus	+	format	date	format
52	<format> + <day of week>: format	plus	+	format	day of week	format
52	<format> + <format>: format	plus	+	format	format	format
52	<format> + <integer>: format	plus	+	format	integer	format
52	<format> + <string>: format	plus	+	format	string	format
52	<format> + <time interval>: format	plus	+	format	time interval	format
52	<format> + <time of day>: format	plus	+	format	time of day	format
52	<format> + <time>: format	plus	+	format	time	format
50	<hertz> % <hertz>: hertz	mod	%	hertz	hertz	hertz
2	<hertz> %25 <hertz>: hertz
52	<hertz> * <integer>: hertz	times	*	hertz	integer	hertz
52	<hertz> + <hertz>: hertz	plus	+	hertz	hertz	hertz
52	<hertz> - <hertz>: hertz	minus	-	hertz	hertz	hertz
52	<hertz> / <hertz>: integer	divide	/	hertz	hertz	integer
52	<hertz> / <integer>: hertz	divide	/	hertz	integer	hertz
52	<hertz> < <hertz>: boolean	less than	<	hertz	hertz	boolean
52	<hertz> <= <hertz>: boolean	less than or equal	<=	hertz	hertz	boolean
52	<hertz> = <hertz>: boolean	equal	=	hertz	hertz	boolean
52	<html> & <html>: html	concatenate	&	html	html	html
52	<html> & <string>: html	concatenate	&	html	string	html
52	<integer set> * <integer set>: integer set	times	*	integer set	integer set	integer set
52	<integer set> + <integer set>: integer set	plus	+	integer set	integer set	integer set
52	<integer set> - <integer set>: integer set	minus	-	integer set	integer set	integer set
52	<integer set> = <integer set>: boolean	equal	=	integer set	integer set	boolean
52	<integer set> contains <integer set>: boolean	contains	contains	integer set	integer set	boolean
52	<integer set> contains <integer>: boolean	contains	contains	integer set	integer	boolean
50	<integer> % <integer>: integer	mod	%	integer	integer	integer
50	<integer> % <large integer>: large integer	mod	%	integer	large integer	large integer
50	<integer> % <uinteger>: uinteger	mod	%	integer	uinteger	uinteger
2	<integer> %25 <integer>: integer
2	<integer> %25 <large integer>: large integer
2	<integer> %25 <uinteger>: uinteger
52	<integer> * <floating point>: floating point	times	*	integer	floating point	floating point
52	<integer> * <hertz>: hertz	times	*	integer	hertz	hertz
52	<integer> * <integer>: integer	times	*	integer	integer	integer
52	<integer> * <large integer>: large integer	times	*	integer	large integer	large integer
52	<integer> * <number of months>: number of months	times	*	integer	number of months	number of months
52	<integer> * <time interval>: time interval	times	*	integer	time interval	time interval
52	<integer> * <time range>: timed( time range, integer )	times	*	integer	time range	timed( time range, integer )
52	<integer> * <uinteger>: uinteger	times	*	integer	uinteger	uinteger
52	<integer> + <floating point>: floating point	plus	+	integer	floating point	floating point
52	<integer> + <integer>: integer	plus	+	integer	integer	integer
52	<integer> + <large integer>: large integer	plus	+	integer	large integer	large integer
52	<integer> + <uinteger>: uinteger	plus	+	integer	uinteger	uinteger
52	<integer> - <floating point>: floating point	minus	-	integer	floating point	floating point
52	<integer> - <integer>: integer	minus	-	integer	integer	integer
52	<integer> - <large integer>: large integer	minus	-	integer	large integer	large integer
52	<integer> - <uinteger>: uinteger	minus	-	integer	uinteger	uinteger
52	<integer> / <floating point>: floating point	divide	/	integer	floating point	floating point
52	<integer> / <integer>: integer	divide	/	integer	integer	integer
52	<integer> / <large integer>: large integer	divide	/	integer	large integer	large integer
52	<integer> / <uinteger>: uinteger	divide	/	integer	uinteger	uinteger
52	<integer> < <floating point>: boolean	less than	<	integer	floating point	boolean
52	<integer> < <integer>: boolean	less than	<	integer	integer	boolean
52	<integer> < <large integer>: boolean	less than	<	integer	large integer	boolean
10	<integer> < <registry key value type>: boolean
10	<integer> < <registry key value>: boolean
52	<integer> < <uinteger>: boolean	less than	<	integer	uinteger	boolean
52	<integer> <= <floating point>: boolean	less than or equal	<=	integer	floating point	boolean
52	<integer> <= <integer>: boolean	less than or equal	<=	integer	integer	boolean
52	<integer> <= <large integer>: boolean	less than or equal	<=	integer	large integer	boolean
10	<integer> <= <registry key value type>: boolean
10	<integer> <= <registry key value>: boolean
52	<integer> <= <uinteger>: boolean	less than or equal	<=	integer	uinteger	boolean
52	<integer> = <floating point>: boolean	equal	=	integer	floating point	boolean
52	<integer> = <integer>: boolean	equal	=	integer	integer	boolean
52	<integer> = <large integer>: boolean	equal	=	integer	large integer	boolean
10	<integer> = <registry key value type>: boolean
10	<integer> = <registry key value>: boolean
52	<integer> = <uinteger>: boolean	equal	=	integer	uinteger	boolean
10	<internet protocol> = <internet protocol>: boolean
52	<ip version> = <ip version>: boolean	equal	=	ip version	ip version	boolean
52	<ipv4 address> < <ipv4 address>: boolean	less than	<	ipv4 address	ipv4 address	boolean
52	<ipv4 address> < <string>: boolean	less than	<	ipv4 address	string	boolean
52	<ipv4 address> <= <ipv4 address>: boolean	less than or equal	<=	ipv4 address	ipv4 address	boolean
52	<ipv4 address> <= <string>: boolean	less than or equal	<=	ipv4 address	string	boolean
52	<ipv4 address> = <ipv4 address>: boolean	equal	=	ipv4 address	ipv4 address	boolean
52	<ipv4 address> = <string>: boolean	equal	=	ipv4 address	string	boolean
52	<ipv4or6 address> < <ipv4or6 address>: boolean	less than	<	ipv4or6 address	ipv4or6 address	boolean
52	<ipv4or6 address> < <string>: boolean	less than	<	ipv4or6 address	string	boolean
52	<ipv4or6 address> <= <ipv4or6 address>: boolean	less than or equal	<=	ipv4or6 address	ipv4or6 address	boolean
52	<ipv4or6 address> <= <string>: boolean	less than or equal	<=	ipv4or6 address	string	boolean
52	<ipv4or6 address> = <ipv4or6 address>: boolean	equal	=	ipv4or6 address	ipv4or6 address	boolean
52	<ipv4or6 address> = <string>: boolean	equal	=	ipv4or6 address	string	boolean
52	<ipv6 address> < <ipv6 address>: boolean	less than	<	ipv6 address	ipv6 address	boolean
52	<ipv6 address> <= <ipv6 address>: boolean	less than or equal	<=	ipv6 address	ipv6 address	boolean
52	<ipv6 address> = <ipv6 address>: boolean	equal	=	ipv6 address	ipv6 address	boolean
52	<json key> = <json key>: boolean	equal	=	json key	json key	boolean
52	<json value> = <json value>: boolean	equal	=	json value	json value	boolean
50	<large integer> % <integer>: large integer	mod	%	large integer	integer	large integer
50	<large integer> % <large integer>: large integer	mod	%	large integer	large integer	large integer
2	<large integer> %25 <integer>: large integer
2	<large integer> %25 <large integer>: large integer
52	<large integer> * <integer>: large integer	times	*	large integer	integer	large integer
52	<large integer> * <large integer>: large integer	times	*	large integer	large integer	large integer
52	<large integer> + <integer>: large integer	plus	+	large integer	integer	large integer
52	<large integer> + <large integer>: large integer	plus	+	large integer	large integer	large integer
52	<large integer> - <integer>: large integer	minus	-	large integer	integer	large integer
52	<large integer> - <large integer>: large integer	minus	-	large integer	large integer	large integer
52	<large integer> / <integer>: large integer	divide	/	large integer	integer	large integer
52	<large integer> / <large integer>: large integer	divide	/	large integer	large integer	large integer
52	<large integer> < <integer>: boolean	less than	<	large integer	integer	boolean
52	<large integer> < <large integer>: boolean	less than	<	large integer	large integer	boolean
52	<large integer> <= <integer>: boolean	less than or equal	<=	large integer	integer	boolean
52	<large integer> <= <large integer>: boolean	less than or equal	<=	large integer	large integer	boolean
52	<large integer> = <integer>: boolean	equal	=	large integer	integer	boolean
52	<large integer> = <large integer>: boolean	equal	=	large integer	large integer	boolean
10	<media type> = <media type>: boolean
10	<metabase identifier> = <metabase identifier>: boolean
10	<metabase type> = <metabase type>: boolean
10	<metabase user type> = <metabase user type>: boolean
52	<month and year> & <day of month>: date	concatenate	&	month and year	day of month	date
52	<month and year> & <day of year>: date	concatenate	&	month and year	day of year	date
52	<month and year> + <number of months>: month and year	plus	+	month and year	number of months	month and year
52	<month and year> - <month and year>: number of months	minus	-	month and year	month and year	number of months
52	<month and year> - <number of months>: month and year	minus	-	month and year	number of months	month and year
52	<month and year> < <month and year>: boolean	less than	<	month and year	month and year	boolean
52	<month and year> <= <month and year>: boolean	less than or equal	<=	month and year	month and year	boolean
52	<month and year> = <month and year>: boolean	equal	=	month and year	month and year	boolean
52	<month> & <day of month>: day of year	concatenate	&	month	day of month	day of year
52	<month> & <year>: month and year	concatenate	&	month	year	month and year
52	<month> + <number of months>: month	plus	+	month	number of months	month
52	<month> - <month>: number of months	minus	-	month	month	number of months
52	<month> - <number of months>: month	minus	-	month	number of months	month
52	<month> < <month>: boolean	less than	<	month	month	boolean
52	<month> <= <month>: boolean	less than or equal	<=	month	month	boolean
52	<month> = <month>: boolean	equal	=	month	month	boolean
50	<number of months> % <number of months>: number of months	mod	%	number of months	number of months	number of months
2	<number of months> %25 <number of months>: number of months
52	<number of months> * <integer>: number of months	times	*	number of months	integer	number of months
52	<number of months> + <date>: date	plus	+	number of months	date	date
52	<number of months> + <day of year>: day of year	plus	+	number of months	day of year	day of year
52	<number of months> + <month and year>: month and year	plus	+	number of months	month and year	month and year
52	<number of months> + <month>: month	plus	+	number of months	month	month
52	<number of months> + <number of months>: number of months	plus	+	number of months	number of months	number of months
52	<number of months> + <year>: year	plus	+	number of months	year	year
52	<number of months> - <number of months>: number of months	minus	-	number of months	number of months	number of months
52	<number of months> / <integer>: number of months	divide	/	number of months	integer	number of months
52	<number of months> / <number of months>: integer	divide	/	number of months	number of months	integer
52	<number of months> < <number of months>: boolean	less than	<	number of months	number of months	boolean
52	<number of months> <= <number of months>: boolean	less than or equal	<=	number of months	number of months	boolean
52	<number of months> = <number of months>: boolean	equal	=	number of months	number of months	boolean
10	<operating system product type> = <operating system product type>: boolean
10	<plugin store key> = <plugin store key>: boolean
10	<plugin store> = <plugin store>: boolean
12	<power state> = <power state>: boolean
10	<priority class> = <priority class>: boolean
42	<rate> * <floating point>: rate	times	*	rate	floating point	rate
42	<rate> * <time interval>: floating point	times	*	rate	time interval	floating point
42	<rate> + <rate>: rate	plus	+	rate	rate	rate
42	<rate> - <rate>: rate	minus	-	rate	rate	rate
42	<rate> / <floating point>: rate	divide	/	rate	floating point	rate
42	<rate> < <rate>: boolean	less than	<	rate	rate	boolean
42	<rate> <= <rate>: boolean	less than or equal	<=	rate	rate	boolean
42	<rate> = <rate>: boolean	equal	=	rate	rate	boolean
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
52	<regular expression> = <string>: boolean	equal	=	regular expression	string	boolean
52	<rope> & <rope>: rope	concatenate	&	rope	rope	rope
52	<rope> & <string>: rope	concatenate	&	rope	string	rope
52	<rope> contains <string>: boolean	contains	contains	rope	string	boolean
12	<security identifier> = <security identifier>: boolean
52	<site version list> < <site version list>: boolean	less than	<	site version list	site version list	boolean
52	<site version list> <= <site version list>: boolean	less than or equal	<=	site version list	site version list	boolean
52	<site version list> = <site version list>: boolean	equal	=	site version list	site version list	boolean
52	<site version list> contains <site version list>: boolean	contains	contains	site version list	site version list	boolean
2	<stage> = <stage>: boolean
52	<string set> * <string set>: string set	times	*	string set	string set	string set
52	<string set> + <string set>: string set	plus	+	string set	string set	string set
52	<string set> - <string set>: string set	minus	-	string set	string set	string set
52	<string set> = <string set>: boolean	equal	=	string set	string set	boolean
52	<string set> contains <string set>: boolean	contains	contains	string set	string set	boolean
52	<string set> contains <string>: boolean	contains	contains	string set	string	boolean
52	<string> & <html>: html	concatenate	&	string	html	html
52	<string> & <rope>: rope	concatenate	&	string	rope	rope
52	<string> & <string>: string	concatenate	&	string	string	string
52	<string> < <ipv4 address>: boolean	less than	<	string	ipv4 address	boolean
52	<string> < <ipv4or6 address>: boolean	less than	<	string	ipv4or6 address	boolean
10	<string> < <registry key value type>: boolean
10	<string> < <registry key value>: boolean
52	<string> < <string>: boolean	less than	<	string	string	boolean
40	<string> < <strverscmp version>: boolean	less than	<	string	strverscmp version	boolean
12	<string> < <uuid>: boolean
52	<string> < <version>: boolean	less than	<	string	version	boolean
52	<string> <= <ipv4 address>: boolean	less than or equal	<=	string	ipv4 address	boolean
52	<string> <= <ipv4or6 address>: boolean	less than or equal	<=	string	ipv4or6 address	boolean
10	<string> <= <registry key value type>: boolean
10	<string> <= <registry key value>: boolean
52	<string> <= <string>: boolean	less than or equal	<=	string	string	boolean
40	<string> <= <strverscmp version>: boolean	less than or equal	<=	string	strverscmp version	boolean
12	<string> <= <uuid>: boolean
52	<string> <= <version>: boolean	less than or equal	<=	string	version	boolean
12	<string> = <cidr subnet>: boolean
52	<string> = <ipv4 address>: boolean	equal	=	string	ipv4 address	boolean
52	<string> = <ipv4or6 address>: boolean	equal	=	string	ipv4or6 address	boolean
10	<string> = <registry key value type>: boolean
10	<string> = <registry key value>: boolean
52	<string> = <regular expression>: boolean	equal	=	string	regular expression	boolean
52	<string> = <string>: boolean	equal	=	string	string	boolean
40	<string> = <strverscmp version>: boolean	equal	=	string	strverscmp version	boolean
12	<string> = <uuid>: boolean
52	<string> = <version>: boolean	equal	=	string	version	boolean
52	<string> contains <regular expression>: boolean	contains	contains	string	regular expression	boolean
52	<string> contains <string>: boolean	contains	contains	string	string	boolean
52	<string> ends with <regular expression>: boolean	ends with	ends with	string	regular expression	boolean
52	<string> ends with <string>: boolean	ends with	ends with	string	string	boolean
52	<string> starts with <regular expression>: boolean	starts with	starts with	string	regular expression	boolean
52	<string> starts with <string>: boolean	starts with	starts with	string	string	boolean
40	<strverscmp version> < <string>: boolean	less than	<	strverscmp version	string	boolean
40	<strverscmp version> < <strverscmp version>: boolean	less than	<	strverscmp version	strverscmp version	boolean
40	<strverscmp version> <= <string>: boolean	less than or equal	<=	strverscmp version	string	boolean
40	<strverscmp version> <= <strverscmp version>: boolean	less than or equal	<=	strverscmp version	strverscmp version	boolean
40	<strverscmp version> = <string>: boolean	equal	=	strverscmp version	string	boolean
40	<strverscmp version> = <strverscmp version>: boolean	equal	=	strverscmp version	strverscmp version	boolean
10	<task action type> = <task action type>: boolean
10	<task trigger type> = <task trigger type>: boolean
50	<time interval> % <time interval>: time interval	mod	%	time interval	time interval	time interval
2	<time interval> %25 <time interval>: time interval
52	<time interval> & <time>: time range	concatenate	&	time interval	time	time range
52	<time interval> * <integer>: time interval	times	*	time interval	integer	time interval
42	<time interval> * <rate>: floating point	times	*	time interval	rate	floating point
52	<time interval> + <date>: date	plus	+	time interval	date	date
52	<time interval> + <day of month>: day of month	plus	+	time interval	day of month	day of month
52	<time interval> + <day of week>: day of week	plus	+	time interval	day of week	day of week
52	<time interval> + <day of year>: day of year	plus	+	time interval	day of year	day of year
52	<time interval> + <time interval>: time interval	plus	+	time interval	time interval	time interval
52	<time interval> + <time of day with time zone>: time of day with time zone	plus	+	time interval	time of day with time zone	time of day with time zone
52	<time interval> + <time of day>: time of day	plus	+	time interval	time of day	time of day
52	<time interval> + <time zone>: time zone	plus	+	time interval	time zone	time zone
52	<time interval> + <time>: time	plus	+	time interval	time	time
52	<time interval> - <time interval>: time interval	minus	-	time interval	time interval	time interval
52	<time interval> / <integer>: time interval	divide	/	time interval	integer	time interval
52	<time interval> / <time interval>: integer	divide	/	time interval	time interval	integer
52	<time interval> < <time interval>: boolean	less than	<	time interval	time interval	boolean
52	<time interval> <= <time interval>: boolean	less than or equal	<=	time interval	time interval	boolean
52	<time interval> = <time interval>: boolean	equal	=	time interval	time interval	boolean
52	<time of day with time zone> & <date>: time	concatenate	&	time of day with time zone	date	time
52	<time of day with time zone> & <time zone>: time of day with time zone	concatenate	&	time of day with time zone	time zone	time of day with time zone
52	<time of day with time zone> + <time interval>: time of day with time zone	plus	+	time of day with time zone	time interval	time of day with time zone
52	<time of day with time zone> - <time interval>: time of day with time zone	minus	-	time of day with time zone	time interval	time of day with time zone
52	<time of day with time zone> - <time of day with time zone>: time interval	minus	-	time of day with time zone	time of day with time zone	time interval
52	<time of day with time zone> < <time of day with time zone>: boolean	less than	<	time of day with time zone	time of day with time zone	boolean
52	<time of day with time zone> <= <time of day with time zone>: boolean	less than or equal	<=	time of day with time zone	time of day with time zone	boolean
52	<time of day with time zone> = <time of day with time zone>: boolean	equal	=	time of day with time zone	time of day with time zone	boolean
52	<time of day> & <time zone>: time of day with time zone	concatenate	&	time of day	time zone	time of day with time zone
52	<time of day> + <time interval>: time of day	plus	+	time of day	time interval	time of day
52	<time of day> - <time interval>: time of day	minus	-	time of day	time interval	time of day
52	<time of day> - <time of day>: time interval	minus	-	time of day	time of day	time interval
52	<time of day> < <time of day>: boolean	less than	<	time of day	time of day	boolean
52	<time of day> <= <time of day>: boolean	less than or equal	<=	time of day	time of day	boolean
52	<time of day> = <time of day>: boolean	equal	=	time of day	time of day	boolean
52	<time range> & <time range>: time range	concatenate	&	time range	time range	time range
52	<time range> & <time>: time range	concatenate	&	time range	time	time range
52	<time range> * <boolean>: timed( time range, boolean )	times	*	time range	boolean	timed( time range, boolean )
52	<time range> * <integer>: timed( time range, integer )	times	*	time range	integer	timed( time range, integer )
52	<time range> * <time range>: time range	times	*	time range	time range	time range
52	<time range> + <time range>: time range	plus	+	time range	time range	time range
52	<time range> = <time range>: boolean	equal	=	time range	time range	boolean
52	<time range> contains <time range>: boolean	contains	contains	time range	time range	boolean
52	<time range> contains <time>: boolean	contains	contains	time range	time	boolean
52	<time zone> & <time of day with time zone>: time of day with time zone	concatenate	&	time zone	time of day with time zone	time of day with time zone
52	<time zone> & <time of day>: time of day with time zone	concatenate	&	time zone	time of day	time of day with time zone
52	<time zone> + <time interval>: time zone	plus	+	time zone	time interval	time zone
52	<time zone> - <time interval>: time zone	minus	-	time zone	time interval	time zone
52	<time zone> - <time zone>: time interval	minus	-	time zone	time zone	time interval
52	<time zone> = <time zone>: boolean	equal	=	time zone	time zone	boolean
52	<time> & <time interval>: time range	concatenate	&	time	time interval	time range
52	<time> & <time range>: time range	concatenate	&	time	time range	time range
52	<time> & <time>: time range	concatenate	&	time	time	time range
52	<time> + <time interval>: time	plus	+	time	time interval	time
52	<time> - <time interval>: time	minus	-	time	time interval	time
52	<time> - <time>: time interval	minus	-	time	time	time interval
52	<time> < <time>: boolean	less than	<	time	time	boolean
52	<time> <= <time>: boolean	less than or equal	<=	time	time	boolean
52	<time> = <time>: boolean	equal	=	time	time	boolean
52	<type> = <type>: boolean	equal	=	type	type	boolean
50	<uinteger> % <integer>: uinteger	mod	%	uinteger	integer	uinteger
50	<uinteger> % <uinteger>: uinteger	mod	%	uinteger	uinteger	uinteger
2	<uinteger> %25 <integer>: uinteger
2	<uinteger> %25 <uinteger>: uinteger
52	<uinteger> * <integer>: uinteger	times	*	uinteger	integer	uinteger
52	<uinteger> * <uinteger>: uinteger	times	*	uinteger	uinteger	uinteger
52	<uinteger> + <integer>: uinteger	plus	+	uinteger	integer	uinteger
52	<uinteger> + <uinteger>: uinteger	plus	+	uinteger	uinteger	uinteger
52	<uinteger> - <integer>: uinteger	minus	-	uinteger	integer	uinteger
52	<uinteger> - <uinteger>: uinteger	minus	-	uinteger	uinteger	uinteger
52	<uinteger> / <integer>: uinteger	divide	/	uinteger	integer	uinteger
52	<uinteger> / <uinteger>: uinteger	divide	/	uinteger	uinteger	uinteger
52	<uinteger> < <integer>: boolean	less than	<	uinteger	integer	boolean
52	<uinteger> < <uinteger>: boolean	less than	<	uinteger	uinteger	boolean
52	<uinteger> <= <integer>: boolean	less than or equal	<=	uinteger	integer	boolean
52	<uinteger> <= <uinteger>: boolean	less than or equal	<=	uinteger	uinteger	boolean
52	<uinteger> = <integer>: boolean	equal	=	uinteger	integer	boolean
52	<uinteger> = <uinteger>: boolean	equal	=	uinteger	uinteger	boolean
12	<uuid> < <string>: boolean
12	<uuid> < <uuid>: boolean
12	<uuid> <= <string>: boolean
12	<uuid> <= <uuid>: boolean
12	<uuid> = <string>: boolean
12	<uuid> = <uuid>: boolean
52	<version> < <string>: boolean	less than	<	version	string	boolean
52	<version> < <version>: boolean	less than	<	version	version	boolean
52	<version> <= <string>: boolean	less than or equal	<=	version	string	boolean
52	<version> <= <version>: boolean	less than or equal	<=	version	version	boolean
52	<version> = <string>: boolean	equal	=	version	string	boolean
52	<version> = <version>: boolean	equal	=	version	version	boolean
2	<volume> = <volume>: boolean
2	<yaml key> = <yaml key>: boolean
2	<yaml value> = <yaml value>: boolean
52	<year> & <day of year>: date	concatenate	&	year	day of year	date
52	<year> & <month>: month and year	concatenate	&	year	month	month and year
52	<year> + <number of months>: year	plus	+	year	number of months	year
52	<year> - <number of months>: year	minus	-	year	number of months	year
52	<year> - <year>: number of months	minus	-	year	year	number of months
52	<year> < <year>: boolean	less than	<	year	year	boolean
52	<year> <= <year>: boolean	less than or equal	<=	year	year	boolean
52	<year> = <year>: boolean	equal	=	year	year	boolean
"""

# 265 rows
CASTS: str = """\
12	<action lock state> as string: string
12	<action> as string: string
12	<agent interface capability> as string: string
2	<application> as string: string
40	<bes action set> as xml string: string	xml string	bes action set	string
40	<bes action set> as xml: utf8 string	xml	bes action set	utf8 string
40	<bes action status> as string: string	string	bes action status	string
40	<bes action> as xml string: string	xml string	bes action	string
40	<bes action> as xml: utf8 string	xml	bes action	utf8 string
40	<bes computer group set> as xml string: string	xml string	bes computer group set	string
40	<bes computer group set> as xml: utf8 string	xml	bes computer group set	utf8 string
40	<bes computer group> as xml string: string	xml string	bes computer group	string
40	<bes computer group> as xml: utf8 string	xml	bes computer group	utf8 string
40	<bes fixlet field value> as date: date	date	bes fixlet field value	date
40	<bes fixlet field value> as integer: integer	integer	bes fixlet field value	integer
40	<bes fixlet field value> as string: string	string	bes fixlet field value	string
40	<bes fixlet field value> as time: time	time	bes fixlet field value	time
40	<bes fixlet set> as xml string: string	xml string	bes fixlet set	string
40	<bes fixlet set> as xml: utf8 string	xml	bes fixlet set	utf8 string
40	<bes fixlet> as xml string: string	xml string	bes fixlet	string
40	<bes fixlet> as xml: utf8 string	xml	bes fixlet	utf8 string
40	<bes property set> as xml string: string	xml string	bes property set	string
40	<bes property set> as xml: utf8 string	xml	bes property set	utf8 string
40	<bes property> as xml string: string	xml string	bes property	string
40	<bes property> as xml: utf8 string	xml	bes property	utf8 string
52	<binary operator> as string: string	string	binary operator	string
52	<binary_string> as fxf string: string	fxf string	binary_string	string
52	<binary_string> as hexadecimal: string	hexadecimal	binary_string	string
52	<binary_string> as local string: string	local string	binary_string	string
52	<binary_string> as string: string	string	binary_string	string
52	<binary_string> as utf16 string: string	utf16 string	binary_string	string
52	<binary_string> as utf8 string: string	utf8 string	binary_string	string
52	<binary_substring> as binary_substring: binary_substring	binary_substring	binary_substring	binary_substring
52	<binary_substring> as string: string	string	binary_substring	string
12	<bios> as string: string
52	<bit set> as integer: integer	integer	bit set	integer
52	<bit set> as string: string	string	bit set	string
52	<boolean> as boolean: boolean	boolean	boolean	boolean
52	<boolean> as string: string	string	boolean	string
52	<cast> as string: string	string	cast	string
12	<cidr subnet> as string: string
2	<client process owner> as string: string
52	<date> as string: string	string	date	string
52	<day of month> as integer: integer	integer	day of month	integer
52	<day of month> as string: string	string	day of month	string
52	<day of month> as two digits: string	two digits	day of month	string
52	<day of week> as string: string	string	day of week	string
52	<day of week> as three letters: string	three letters	day of week	string
52	<day of year> as string: string	string	day of year	string
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
52	<floating point> as floating point: floating point	floating point	floating point	floating point
52	<floating point> as integer: integer	integer	floating point	integer
52	<floating point> as scientific notation: string	scientific notation	floating point	string
52	<floating point> as standard notation: string	standard notation	floating point	string
52	<floating point> as string: string	string	floating point	string
52	<format> as string: string	string	format	string
52	<hertz> as string: string	string	hertz	string
52	<html> as decoded string: string	decoded string	html	string
52	<html> as html: html	html	html	html
52	<html> as string: string	string	html	string
52	<integer> as bit set: bit set	bit set	integer	bit set
52	<integer> as bits: bit set	bits	integer	bit set
52	<integer> as day_of_month: day of month	day_of_month	integer	day of month
52	<integer> as floating point: floating point	floating point	integer	floating point
52	<integer> as hexadecimal: string	hexadecimal	integer	string
52	<integer> as integer: integer	integer	integer	integer
52	<integer> as large integer: large integer	large integer	integer	large integer
52	<integer> as month: month	month	integer	month
52	<integer> as string: string	string	integer	string
52	<integer> as uinteger: uinteger	uinteger	integer	uinteger
52	<integer> as year: year	year	integer	year
52	<ip version> as string: string	string	ip version	string
52	<ipv4 address> as ipv4or6 address: ipv4or6 address	ipv4or6 address	ipv4 address	ipv4or6 address
52	<ipv4 address> as ipv6 address: ipv6 address	ipv6 address	ipv4 address	ipv6 address
52	<ipv4 address> as string: string	string	ipv4 address	string
52	<ipv4or6 address> as compressed string with ipv4 with zone index: string	compressed string with ipv4 with zone index	ipv4or6 address	string
52	<ipv4or6 address> as compressed string with ipv4: string	compressed string with ipv4	ipv4or6 address	string
52	<ipv4or6 address> as compressed string with zone index: string	compressed string with zone index	ipv4or6 address	string
52	<ipv4or6 address> as compressed string: string	compressed string	ipv4or6 address	string
52	<ipv4or6 address> as string with ipv4 with zone index: string	string with ipv4 with zone index	ipv4or6 address	string
52	<ipv4or6 address> as string with ipv4: string	string with ipv4	ipv4or6 address	string
52	<ipv4or6 address> as string with leading zeros with zone index: string	string with leading zeros with zone index	ipv4or6 address	string
52	<ipv4or6 address> as string with leading zeros: string	string with leading zeros	ipv4or6 address	string
52	<ipv4or6 address> as string with zone index: string	string with zone index	ipv4or6 address	string
52	<ipv4or6 address> as string: string	string	ipv4or6 address	string
52	<ipv6 address> as compressed string with ipv4 with zone index: string	compressed string with ipv4 with zone index	ipv6 address	string
52	<ipv6 address> as compressed string with ipv4: string	compressed string with ipv4	ipv6 address	string
52	<ipv6 address> as compressed string with zone index: string	compressed string with zone index	ipv6 address	string
52	<ipv6 address> as compressed string: string	compressed string	ipv6 address	string
52	<ipv6 address> as ipv4or6 address: ipv4or6 address	ipv4or6 address	ipv6 address	ipv4or6 address
52	<ipv6 address> as string with ipv4 with zone index: string	string with ipv4 with zone index	ipv6 address	string
52	<ipv6 address> as string with ipv4: string	string with ipv4	ipv6 address	string
52	<ipv6 address> as string with leading zeros with zone index: string	string with leading zeros with zone index	ipv6 address	string
52	<ipv6 address> as string with leading zeros: string	string with leading zeros	ipv6 address	string
52	<ipv6 address> as string with zone index: string	string with zone index	ipv6 address	string
52	<ipv6 address> as string: string	string	ipv6 address	string
52	<json key> as string: string	string	json key	string
52	<json value> as boolean: boolean	boolean	json value	boolean
52	<json value> as float: floating point	float	json value	floating point
52	<json value> as integer: integer	integer	json value	integer
52	<json value> as string: string	string	json value	string
10	<language> as string: string
52	<large integer> as hexadecimal: string	hexadecimal	large integer	string
52	<large integer> as integer: integer	integer	large integer	integer
52	<large integer> as large integer: large integer	large integer	large integer	large integer
52	<large integer> as string: string	string	large integer	string
52	<large integer> as uinteger: uinteger	uinteger	large integer	uinteger
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
52	<month and year> as string: string	string	month and year	string
52	<month> as integer: integer	integer	month	integer
52	<month> as string: string	string	month	string
52	<month> as three letters: string	three letters	month	string
52	<month> as two digits: string	two digits	month	string
52	<number of months> as string: string	string	number of months	string
12	<operating system> as string: string
10	<plugin store key> as string: string
10	<plugin store> as string: string
12	<power level> as string: string
12	<power state> as string: string
10	<primary language> as string: string
52	<property> as string: string	string	property	string
42	<rate> as string: string	string	rate	string
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
52	<rope> as string: string	string	rope	string
10	<security descriptor> as string: string
12	<security identifier> as string: string
12	<server based group> as string: string
10	<service> as string: string
12	<setting> as string: string
10	<site profile variable> as string: string
52	<site version list> as string: string	string	site version list	string
12	<smbios value> as hexadecimal: string
12	<smbios value> as string: string
12	<sqlite column type> as string: string
12	<sqlite column> as string: string
12	<sqlite database> as string: string
12	<sqlite row> as string: string
12	<sqlite table> as string: string
2	<stage> as string: string
52	<string> as binary_string: binary_string	binary_string	string	binary_string
52	<string> as boolean: boolean	boolean	string	boolean
52	<string> as date: date	date	string	date
52	<string> as day_of_month: day of month	day_of_month	string	day of month
52	<string> as day_of_week: day of week	day_of_week	string	day of week
52	<string> as floating point: floating point	floating point	string	floating point
52	<string> as fxf binary_string: binary_string	fxf binary_string	string	binary_string
52	<string> as hexadecimal: string	hexadecimal	string	string
52	<string> as html: html	html	string	html
52	<string> as integer: integer	integer	string	integer
52	<string> as ipv4or6 address: ipv4or6 address	ipv4or6 address	string	ipv4or6 address
52	<string> as ipv6 address: ipv6 address	ipv6 address	string	ipv6 address
52	<string> as large integer: large integer	large integer	string	large integer
52	<string> as left trimmed string: string	left trimmed string	string	string
52	<string> as local binary_string: binary_string	local binary_string	string	binary_string
52	<string> as local time: time	local time	string	time
52	<string> as local zoned time_of_day: time of day with time zone	local zoned time_of_day	string	time of day with time zone
52	<string> as lowercase: string	lowercase	string	string
52	<string> as month: month	month	string	month
52	<string> as right trimmed string: string	right trimmed string	string	string
52	<string> as site version list: site version list	site version list	string	site version list
52	<string> as string: string	string	string	string
40	<string> as strverscmp version: strverscmp version	strverscmp version	string	strverscmp version
52	<string> as time interval: time interval	time interval	string	time interval
52	<string> as time zone: time zone	time zone	string	time zone
52	<string> as time: time	time	string	time
52	<string> as time_of_day: time of day	time_of_day	string	time of day
52	<string> as trimmed string: string	trimmed string	string	string
52	<string> as uinteger: uinteger	uinteger	string	uinteger
52	<string> as universal time: time	universal time	string	time
52	<string> as universal zoned time_of_day: time of day with time zone	universal zoned time_of_day	string	time of day with time zone
52	<string> as uppercase: string	uppercase	string	string
52	<string> as utf16 binary_string: binary_string	utf16 binary_string	string	binary_string
52	<string> as utf8 binary_string: binary_string	utf8 binary_string	string	binary_string
52	<string> as version: version	version	string	version
50	<string> as windows display time: time	windows display time	string	time
52	<string> as year: year	year	string	year
52	<string> as zoned time_of_day: time of day with time zone	zoned time_of_day	string	time of day with time zone
52	<substring> as string: string	string	substring	string
52	<substring> as substring: substring	substring	substring	substring
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
52	<time interval> as string: string	string	time interval	string
52	<time of day with time zone> as string: string	string	time of day with time zone	string
52	<time of day> as string: string	string	time of day	string
52	<time range> as string: string	string	time range	string
52	<time zone> as string: string	string	time zone	string
52	<time> as local date: date	local date	time	date
52	<time> as local string: string	local string	time	string
52	<time> as string: string	string	time	string
52	<time> as universal date: date	universal date	time	date
52	<time> as universal string: string	universal string	time	string
52	<tuple item> as string: string	string	tuple item	string
52	<type> as string: string	string	type	string
52	<uinteger> as hexadecimal: string	hexadecimal	uinteger	string
52	<uinteger> as integer: integer	integer	uinteger	integer
52	<uinteger> as large integer: large integer	large integer	uinteger	large integer
52	<uinteger> as string: string	string	uinteger	string
52	<uinteger> as uinteger: uinteger	uinteger	uinteger	uinteger
52	<unary operator> as string: string	string	unary operator	string
52	<undefined> as string: string	string	undefined	string
2	<user attribute> as string: string
12	<uuid> as binary_string: binary_string
12	<uuid> as hexadecimal: string
12	<uuid> as string: string
52	<version> as string: string	string	version	string
52	<version> as version: version	version	version	version
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
52	<year> as integer: integer	integer	year	integer
52	<year> as string: string	string	year	string
"""

# 4626 rows
PROPERTIES: str = """\
ff	abbr <string> of <html>: html	abbr	abbrs	abbr	0	html	html	string
ff	abbr <string> of <string>: html	abbr	abbrs	abbr	0	html	string	string
ff	abbr of <html>: html	abbr	abbrs	abbr	0	html	html	
ff	abbr of <string>: html	abbr	abbrs	abbr	0	html	string	
10	above normal priority: priority class
ff	absolute value of <hertz>: hertz	absolute value	absolute values	absolute value	0	hertz	hertz	
ff	absolute value of <integer>: integer	absolute value	absolute values	absolute value	0	integer	integer	
ff	absolute value of <time interval>: time interval	absolute value	absolute values	absolute value	0	time interval	time interval	
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
ff	acronym <string> of <html>: html	acronym	acronyms	acronym	0	html	html	string
ff	acronym <string> of <string>: html	acronym	acronyms	acronym	0	html	string	string
ff	acronym of <html>: html	acronym	acronyms	acronym	0	html	html	
ff	acronym of <string>: html	acronym	acronyms	acronym	0	html	string	
e0	action <integer> of <bes fixlet>: bes fixlet action	action	actions	action	0	bes fixlet action	bes fixlet	integer
1f	action <integer>: action
e0	action <string> of <bes fixlet>: bes fixlet action	action	actions	action	0	bes fixlet action	bes fixlet	string
e0	action dependencies of <bes action>: bes action	action dependency	action dependencies	action dependencies	1	bes action	bes action	
1f	action duration of <evaluation cycle>: time interval
e0	action flag of <bes filter>: boolean	action flag	action flags	action flag	0	boolean	bes filter	
40	action id of <bes peer download>: integer	action id	action ids	action id	0	integer	bes peer download	
1f	action lock state: action lock state
e0	action of <bes action result>: bes action	action	actions	action	0	bes action	bes action result	
e0	action of <bes baseline component>: bes fixlet action	action	actions	action	0	bes fixlet action	bes baseline component	
40	action of <bes peer download>: bes action	action	actions	action	0	bes action	bes peer download	
12	action of <firewall rule>: firewall action
1f	action percent of <evaluation cycle>: floating point
e0	action results of <bes computer>: bes action result	action result	action results	action results	1	bes action result	bes computer	
e0	action script of <bes action>: string	action script	action scripts	action script	0	string	bes action	
e0	action script type of <bes action>: string	action script type	action script types	action script type	0	string	bes action	
e0	action set of <bes domain>: bes action set	action set	action sets	action set	0	bes action set	bes domain	
e0	action set of <bes filter>: bes action set	action set	action sets	action set	0	bes action set	bes filter	
e0	action set of <bes site>: bes action set	action set	action sets	action set	0	bes action set	bes site	
e0	action site of <bes user>: bes site	action site	action sites	action site	0	bes site	bes user	
1f	action: action
e0	actions of <bes domain>: bes action	action	actions	actions	1	bes action	bes domain	
e0	actions of <bes fixlet>: bes fixlet action	action	actions	actions	1	bes fixlet action	bes fixlet	
e0	actions of <bes site>: bes action	action	actions	actions	1	bes action	bes site	
10	actions of <task definition>: task action
e0	activations of <bes fixlet>: bes activation	activation	activations	activations	1	bes activation	bes fixlet	
1f	active action: action
5f	active container count of <bes product>: integer	active container count	active container counts	active container count	0	integer	bes product	
1f	active count of <action>: integer
10	active device files <string>: file
10	active device files: file
10	active devices: active device
40	active directory of <bes idp directory>: boolean	active directory	active directories	active directory	0	boolean	bes idp directory	
e0	active directory of <bes ldap directory>: boolean	active directory	active directories	active directory	0	boolean	bes ldap directory	
a0	active directory path of <bes computer>: distinguished name
12	active directory user of <user>: active directory local user
12	active directory: active directory server
e0	active flag of <bes activation>: boolean	active flag	active flags	active flag	0	boolean	bes activation	
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
ff	address <string> of <html>: html	address	addresss	address	0	html	html	string
ff	address <string> of <string>: html	address	addresss	address	0	html	string	string
10	address lists of <network adapter>: network address list
1f	address of <dmi management_device>: integer
ff	address of <html>: html	address	addresss	address	0	html	html	
1f	address of <network adapter interface>: ipv4or6 address
1f	address of <network adapter>: ipv4 address
10	address of <network address list>: ipv4 address
1f	address of <network ip interface>: ipv4 address
ff	address of <string>: html	address	addresss	address	0	html	string	
1f	address_type of <dmi management_device>: integer
10	admin privilege of <user>: boolean
e0	administered computer set of <bes user>: bes computer set	administered computer set	administered computer sets	administered computer set	0	bes computer set	bes user	
e0	administered computers of <bes user>: bes computer	administered computer	administered computers	administered computers	1	bes computer	bes user	
1f	administrative rights of <client>: administrative rights
e0	administrator <( bes computer, bes user )>: boolean	administrator	administrators	administrator	0	boolean		( bes computer, bes user )
e0	administrator <( bes user, bes computer )>: boolean	administrator	administrators	administrator	0	boolean		( bes user, bes computer )
e0	administrator <bes computer> of <bes user>: boolean	administrator	administrators	administrator	0	boolean	bes user	bes computer
e0	administrator <bes user> of <bes computer>: boolean	administrator	administrators	administrator	0	boolean	bes computer	bes user
1f	administrator <string> of <client>: setting
e0	administrator set of <bes computer>: bes user set	administrator set	administrator sets	administrator set	0	bes user set	bes computer	
e0	administrators of <bes computer>: bes user	administrator	administrators	administrators	1	bes user	bes computer	
1f	administrators of <client>: setting
12	agent interface <string> of <client>: agent interface
12	agent interfaces of <client>: agent interface
e0	agent type of <bes computer>: string	agent type	agent types	agent type	0	string	bes computer	
e0	agent version of <bes computer>: string	agent version	agent versions	agent version	0	string	bes computer	
2	alias of <file>: boolean
f	alias of <network ip interface>: boolean
e0	all bes sites: bes site	all bes site	all bes sites	all bes sites	1	bes site		
e0	all computer counts: historical computer count	all computer count	all computer counts	all computer counts	1	historical computer count		
10	all firewall scope: firewall scope
e0	all fixlet counts: historical fixlet count	all fixlet count	all fixlet counts	all fixlet counts	1	historical fixlet count		
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
ff	allow unmentioned site of <license>: boolean	allow unmentioned site	allow unmentioned sites	allow unmentioned site	0	boolean	license	
1f	allowed of <site>: boolean
1f	allowed sites of <restricted site>: site
10	allowed workstations string of <user>: string
e0	analysis flag of <bes filter>: boolean	analysis flag	analysis flags	analysis flag	0	boolean	bes filter	
e0	analysis flag of <bes fixlet>: boolean	analysis flag	analysis flags	analysis flag	0	boolean	bes fixlet	
e0	analysis flag of <bes property>: boolean	analysis flag	analysis flags	analysis flag	0	boolean	bes property	
e0	analysis of <bes activation>: bes fixlet	analysis	analyses	analysis	0	bes fixlet	bes activation	
e0	analysis set of <bes filter>: bes fixlet set	analysis set	analysis sets	analysis set	0	bes fixlet set	bes filter	
1f	analysis: analysis
1f	ancestors of <filesystem object>: folder
d	ancestors of <symlink>: folder
ff	anchor <string> of <html>: html	anchor	anchors	anchor	0	html	html	string
ff	anchor <string> of <string>: html	anchor	anchors	anchor	0	html	string	string
ff	anchor of <html>: html	anchor	anchors	anchor	0	html	html	
ff	anchor of <string>: html	anchor	anchors	anchor	0	html	string	
d	android of <operating system>: boolean
10	anonymous logon group: security account
10	ansi code page: integer
10	any adapter <integer> of <network>: network adapter
1f	any adapters of <network>: network adapter
ff	any ip version: ip version	any ip version	any ip versions	any ip version	0	ip version		
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
e0	applicability relevance of <bes action>: string	applicability relevance	applicability relevances	applicability relevance	0	string	bes action	
e0	applicable computer count of <bes baseline component>: integer	applicable computer count	applicable computer counts	applicable computer count	0	integer	bes baseline component	
e0	applicable computer count of <bes fixlet>: integer	applicable computer count	applicable computer counts	applicable computer count	0	integer	bes fixlet	
e0	applicable computer set of <bes baseline component>: bes computer set	applicable computer set	applicable computer sets	applicable computer set	0	bes computer set	bes baseline component	
e0	applicable computer set of <bes fixlet>: bes computer set	applicable computer set	applicable computer sets	applicable computer set	0	bes computer set	bes fixlet	
e0	applicable computers of <bes fixlet>: bes computer	applicable computer	applicable computers	applicable computers	1	bes computer	bes fixlet	
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
e0	apply count of <bes action result>: integer	apply count	apply counts	apply count	0	integer	bes action result	
e0	approver role of <bes user>: bes role	approver role	approver roles	approver role	0	bes role	bes user	
ff	april <integer> of <integer>: date	april	aprils	april	0	date	integer	integer
ff	april <integer>: day of year	april	aprils	april	0	day of year		integer
ff	april of <integer>: month and year	april	aprils	april	0	month and year	integer	
ff	april: month	april	aprils	april	0	month		
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
e0	asset of <bes unmanagedasset field>: bes unmanagedasset	asset	assets	asset	0	bes unmanagedasset	bes unmanagedasset field	
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
ff	attr lists of <( string, string )>: html attribute list	attr list	attr lists	attr lists	1	html attribute list	( string, string )	
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
ff	august <integer> of <integer>: date	august	augusts	august	0	date	integer	integer
ff	august <integer>: day of year	august	augusts	august	0	day of year		integer
ff	august of <integer>: month and year	august	augusts	august	0	month and year	integer	
ff	august: month	august	augusts	august	0	month		
10	authenticated users group: security account
1f	authenticating of <client>: boolean
1f	authenticating of <current relay>: boolean
e0	author of <bes comment>: bes user	author	authors	author	0	bes user	bes comment	
40	author of <bes tag>: bes user	author	authors	author	0	bes user	bes tag	
10	author of <task registration info>: string
10	authorized applications of <firewall profile>: firewall authorized application
e0	automatic flag of <bes computer group>: boolean	automatic flag	automatic flags	automatic flag	0	boolean	bes computer group	
d	available amount of <ram>: integer
1f	average duration of <evaluation cycle>: time interval
1f	average of <evaluation cycle>: integer
40	azure entra id of <bes idp directory>: boolean	azure entra id	azure entra ids	azure entra id	0	boolean	bes idp directory	
ff	b <string> of <html>: html	b	bs	b	0	html	html	string
ff	b <string> of <string>: html	b	bs	b	0	html	string	string
ff	b of <html>: html	b	bs	b	0	html	html	
ff	b of <string>: html	b	bs	b	0	html	string	
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
ff	base <string> of <html>: html	base	bases	base	0	html	html	string
ff	base <string> of <string>: html	base	bases	base	0	html	string	string
40	base distinguished name of <bes idp directory>: string	base distinguished name	base distinguished names	base distinguished name	0	string	bes idp directory	
e0	base distinguished name of <bes ldap directory>: string	base distinguished name	base distinguished names	base distinguished name	0	string	bes ldap directory	
10	base name of <operating system>: string
ff	base of <html>: html	base	bases	base	0	html	html	
ff	base of <string>: html	base	bases	base	0	html	string	
9	base package of <debianpkg version>: debian base package
9	base packages <string> of <debianpackagecache>: debian base package
9	base packages of <debianpackagecache>: debian base package
10	base priority of <process>: priority class
ff	base64 decode <string>: string	base64 decode	base64 decodes	base64 decode	0	string		string
1d	base64 der encoded certificate string of <string>: x509 certificate
ff	base64 encode <string>: string	base64 encode	base64 encodes	base64 encode	0	string		string
1f	base_address of <dmi ipmi_device_information>: integer
1f	base_board_information <integer> of <dmi>: dmi base_board_information
1f	base_board_informations of <dmi>: dmi base_board_information
e0	baseline flag of <bes filter>: boolean	baseline flag	baseline flags	baseline flag	0	boolean	bes filter	
e0	baseline flag of <bes fixlet>: boolean	baseline flag	baseline flags	baseline flag	0	boolean	bes fixlet	
e0	baseline set of <bes filter>: bes fixlet set	baseline set	baseline sets	baseline set	0	bes fixlet set	bes filter	
10	batch group: security account
10	bcc of <email task action>: string
10	below normal priority: priority class
e0	bes action set: bes action set	bes action set	bes action sets	bes action set	0	bes action set		
e0	bes action status constrained: bes action status	bes action status constrained	bes action statuses constrained	bes action status constrained	0	bes action status		
e0	bes action status disk free limited: bes action status	bes action status disk free limited	bes action statuses disk free limited	bes action status disk free limited	0	bes action status		
e0	bes action status disk limited: bes action status	bes action status disk limited	bes action statuses disk limited	bes action status disk limited	0	bes action status		
e0	bes action status download failed: bes action status	bes action status download failed	bes action statuses download failed	bes action status download failed	0	bes action status		
e0	bes action status download size limited: bes action status	bes action status download size limited	bes action statuses download size limited	bes action status download size limited	0	bes action status		
e0	bes action status error: bes action status	bes action status error	bes action statuses error	bes action status error	0	bes action status		
e0	bes action status evaluating: bes action status	bes action status evaluating	bes action statuses evaluating	bes action status evaluating	0	bes action status		
e0	bes action status expired: bes action status	bes action status expired	bes action statuses expired	bes action status expired	0	bes action status		
e0	bes action status failed: bes action status	bes action status failed	bes action statuses failed	bes action status failed	0	bes action status		
e0	bes action status fixed: bes action status	bes action status fixed	bes action statuses fixed	bes action status fixed	0	bes action status		
e0	bes action status hash mismatch: bes action status	bes action status hash mismatch	bes action statuses hash mismatch	bes action status hash mismatch	0	bes action status		
e0	bes action status invalid signature: bes action status	bes action status invalid signature	bes action statuses invalid signature	bes action status invalid signature	0	bes action status		
e0	bes action status irrelevant: bes action status	bes action status irrelevant	bes action statuses irrelevant	bes action status irrelevant	0	bes action status		
e0	bes action status locked site: bes action status	bes action status locked site	bes action statuses locked site	bes action status locked site	0	bes action status		
e0	bes action status locked: bes action status	bes action status locked	bes action statuses locked	bes action status locked	0	bes action status		
40	bes action status no space in active downloads: bes action status	bes action status no space in active downloads	bes action statuses no space in active downloads	bes action status no space in active downloads	0	bes action status		
e0	bes action status offers disabled: bes action status	bes action status offers disabled	bes action statuses offers disabled	bes action status offers disabled	0	bes action status		
e0	bes action status pending downloads: bes action status	bes action status pending downloads	bes action statuses pending downloads	bes action status pending downloads	0	bes action status		
e0	bes action status pending login: bes action status	bes action status pending login	bes action statuses pending login	bes action status pending login	0	bes action status		
e0	bes action status pending message: bes action status	bes action status pending message	bes action statuses pending message	bes action status pending message	0	bes action status		
e0	bes action status pending offer: bes action status	bes action status pending offer	bes action statuses pending offer	bes action status pending offer	0	bes action status		
e0	bes action status pending restart: bes action status	bes action status pending restart	bes action statuses pending restart	bes action status pending restart	0	bes action status		
e0	bes action status plugin interrupted: bes action status	bes action status plugin interrupted	bes action statuses plugin interrupted	bes action status plugin interrupted	0	bes action status		
e0	bes action status postponed: bes action status	bes action status postponed	bes action statuses postponed	bes action status postponed	0	bes action status		
e0	bes action status running: bes action status	bes action status running	bes action statuses running	bes action status running	0	bes action status		
e0	bes action status script unavailable: bes action status	bes action status script unavailable	bes action statuses script unavailable	bes action status script unavailable	0	bes action status		
e0	bes action status timeout reached: bes action status	bes action status timeout reached	bes action statuses timeout reached	bes action status timeout reached	0	bes action status		
e0	bes action status unreported: bes action status	bes action status unreported	bes action statuses unreported	bes action status unreported	0	bes action status		
e0	bes action status user cancelled: bes action status	bes action status user cancelled	bes action statuses user cancelled	bes action status user cancelled	0	bes action status		
e0	bes action status waiting: bes action status	bes action status waiting	bes action statuses waiting	bes action status waiting	0	bes action status		
e0	bes actions: bes action	bes action	bes actions	bes actions	1	bes action		
e0	bes analyses: bes fixlet	bes analysis	bes analyses	bes analyses	1	bes fixlet		
e0	bes analysis set: bes fixlet set	bes analysis set	bes analysis sets	bes analysis set	0	bes fixlet set		
e0	bes baseline set: bes fixlet set	bes baseline set	bes baseline sets	bes baseline set	0	bes fixlet set		
e0	bes baselines: bes fixlet	bes baseline	bes baselines	bes baselines	1	bes fixlet		
e0	bes brand: string	bes brand	bes brands	bes brand	0	string		
e0	bes computer <integer>: bes computer	bes computer	bes computers	bes computer	0	bes computer		integer
e0	bes computer group set of <bes computer>: bes computer group set	bes computer group set	bes computer group sets	bes computer group set	0	bes computer group set	bes computer	
e0	bes computer group set: bes computer group set	bes computer group set	bes computer group sets	bes computer group set	0	bes computer group set		
e0	bes computer groups of <bes computer>: bes computer group	bes computer group	bes computer groups	bes computer groups	1	bes computer group	bes computer	
e0	bes computer groups: bes computer group	bes computer group	bes computer groups	bes computer groups	1	bes computer group		
e0	bes computer set: bes computer set	bes computer set	bes computer sets	bes computer set	0	bes computer set		
e0	bes computer with extensions set: bes computer set	bes computer with extensions set	bes computer with extensions sets	bes computer with extensions set	0	bes computer set		
e0	bes computers with extensions: bes computer	bes computer with extensions	bes computers with extensions	bes computers with extensions	1	bes computer		
e0	bes computers: bes computer	bes computer	bes computers	bes computers	1	bes computer		
e0	bes current wruser: string	bes current wruser	bes current wrusers	bes current wruser	0	string		
e0	bes custom sites: bes site	bes custom site	bes custom sites	bes custom sites	1	bes site		
e0	bes deployment options <string>: bes deployment option	bes deployment option	bes deployment options	bes deployment options	1	bes deployment option		string
e0	bes deployment options: bes deployment option	bes deployment option	bes deployment options	bes deployment options	1	bes deployment option		
e0	bes domain <string>: bes domain	bes domain	bes domains	bes domain	0	bes domain		string
e0	bes domain set: bes domain set	bes domain set	bes domain sets	bes domain set	0	bes domain set		
e0	bes domains: bes domain	bes domain	bes domains	bes domains	1	bes domain		
e0	bes filter <integer>: bes filter	bes filter	bes filters	bes filter	0	bes filter		integer
e0	bes filter set: bes filter set	bes filter set	bes filter sets	bes filter set	0	bes filter set		
e0	bes filters: bes filter	bes filter	bes filters	bes filters	1	bes filter		
e0	bes fixlet set: bes fixlet set	bes fixlet set	bes fixlet sets	bes fixlet set	0	bes fixlet set		
e0	bes fixlets: bes fixlet	bes fixlet	bes fixlets	bes fixlets	1	bes fixlet		
40	bes idp directories: bes idp directory	bes idp directory	bes idp directories	bes idp directories	1	bes idp directory		
40	bes idp directory set: bes idp directory set	bes idp directory set	bes idp directory sets	bes idp directory set	0	bes idp directory set		
e0	bes languages: string	bes language	bes languages	bes languages	1	string		
e0	bes ldap directories: bes ldap directory	bes ldap directory	bes ldap directories	bes ldap directories	1	bes ldap directory		
e0	bes ldap directory set: bes ldap directory set	bes ldap directory set	bes ldap directory sets	bes ldap directory set	0	bes ldap directory set		
ff	bes license: license	bes license	bes licenses	bes license	0	license		
40	bes peer downloads: bes peer download	bes peer download	bes peer downloads	bes peer downloads	1	bes peer download		
e0	bes properties: bes property	bes property	bes properties	bes properties	1	bes property		
e0	bes property <string>: bes property	bes property	bes properties	bes property	0	bes property		string
e0	bes property set: bes property set	bes property set	bes property sets	bes property set	0	bes property set		
e0	bes role set: bes role set	bes role set	bes role sets	bes role set	0	bes role set		
e0	bes roles: bes role	bes role	bes roles	bes roles	1	bes role		
e0	bes sites: bes site	bes site	bes sites	bes sites	1	bes site		
e0	bes task set: bes fixlet set	bes task set	bes task sets	bes task set	0	bes fixlet set		
e0	bes tasks: bes fixlet	bes task	bes tasks	bes tasks	1	bes fixlet		
e0	bes unmanagedasset set: bes unmanagedasset set	bes unmanagedasset set	bes unmanagedasset sets	bes unmanagedasset set	0	bes unmanagedasset set		
e0	bes unmanagedassets: bes unmanagedasset	bes unmanagedasset	bes unmanagedassets	bes unmanagedassets	1	bes unmanagedasset		
e0	bes user set: bes user set	bes user set	bes user sets	bes user set	0	bes user set		
e0	bes users: bes user	bes user	bes users	bes users	1	bes user		
e0	bes wakeonlan statuses: bes wakeonlan status	bes wakeonlan status	bes wakeonlan statuses	bes wakeonlan statuses	1	bes wakeonlan status		
e0	bes webui app set: bes webui app set	bes webui app set	bes webui app sets	bes webui app set	0	bes webui app set		
e0	bes webui apps: bes webui app	bes webui app	bes webui apps	bes webui apps	1	bes webui app		
e0	bes webui: bes webui	bes webui	bes webuis	bes webui	0	bes webui		
e0	bes wizard set: bes wizard set	bes wizard set	bes wizard sets	bes wizard set	0	bes wizard set		
e0	bes wizards: bes wizard	bes wizard	bes wizards	bes wizards	1	bes wizard		
e0	best activation of <bes fixlet>: bes activation	best activation	best activations	best activation	0	bes activation	bes fixlet	
ff	big <string> of <html>: html	big	bigs	big	0	html	html	string
ff	big <string> of <string>: html	big	bigs	big	0	html	string	string
1f	big endian of <operating system>: boolean
ff	big of <html>: html	big	bigs	big	0	html	html	
ff	big of <string>: html	big	bigs	big	0	html	string	
e0	bin at <time> of <statistic range>: statistical bin	bin at	bins at	bin at	0	statistical bin	statistic range	time
1d	binary location of <filesystem object>: binary_string
1f	binary name of <filesystem object>: binary_string
1f	binary named files of <folder>: file
1f	binary named folders of <folder>: folder
ff	binary operators <string>: binary operator	binary operator	binary operators	binary operators	1	binary operator		string
ff	binary operators returning <type>: binary operator	binary operator returning	binary operators returning	binary operators returning	1	binary operator		type
ff	binary operators: binary operator	binary operator	binary operators	binary operators	1	binary operator		
1d	binary pathname of <filesystem object>: binary_string
ff	binary_string <string>: binary_string	binary_string	binary_strings	binary_string	0	binary_string		string
ff	binary_substring <( integer, integer )> of <binary_string>: binary_substring	binary_substring	binary_substrings	binary_substring	0	binary_substring	binary_string	( integer, integer )
ff	binary_substrings <binary_string> of <binary_string>: binary_substring	binary_substring	binary_substrings	binary_substrings	1	binary_substring	binary_string	binary_string
e0	bins of <statistic range>: statistical bin	bin	bins	bins	1	statistical bin	statistic range	
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
ff	bit <integer> of <bit set>: boolean	bit	bits	bit	0	boolean	bit set	integer
ff	bit <integer> of <integer>: boolean	bit	bits	bit	0	boolean	integer	integer
5a	bit <integer> of <large integer>: boolean	bit	bits	bit	0	boolean	large integer	integer
5a	bit <integer> of <uinteger>: boolean	bit	bits	bit	0	boolean	uinteger	integer
ff	bit <integer>: bit set	bit	bits	bit	0	bit set		integer
ff	bit set <string>: bit set	bit set	bit sets	bit set	0	bit set		string
2	blackhole flag of <route>: boolean
10	blade bit <operating system suite mask>: boolean
1f	blob of <sqlite column type>: boolean
12	block firewall action: firewall action
d	block list of <grub file location>: grub block list
d	block size of <filesystem>: integer
ff	blockquote <string> of <html>: html	blockquote	blockquotes	blockquote	0	html	html	string
ff	blockquote <string> of <string>: html	blockquote	blockquotes	blockquote	0	html	string	string
ff	blockquote of <html>: html	blockquote	blockquotes	blockquote	0	html	html	
ff	blockquote of <string>: html	blockquote	blockquotes	blockquote	0	html	string	
1f	board_type of <dmi base_board_information>: integer
ff	body <string> of <html>: html	body	bodys	body	0	html	html	string
ff	body <string> of <string>: html	body	bodys	body	0	html	string	string
e0	body of <bes fixlet>: html	body	bodies	body	0	html	bes fixlet	
10	body of <email task action>: string
ff	body of <html>: html	body	bodys	body	0	html	html	
ff	body of <string>: html	body	bodys	body	0	html	string	
d	bogomips of <processor>: integer
2	boolean <integer> of <array>: boolean
2	boolean <string> of <dictionary>: boolean
2	boolean <string> of <preference>: boolean
ff	boolean <string>: boolean	boolean	booleans	boolean	0	boolean		string
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
ff	br <string>: html	br	brs	br	0	html		string
ff	br: html	br	brs	br	0	html		
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
ff	build revision of <version>: integer	build revision	build revisions	build revision	0	integer	version	
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
ff	byte <integer> of <binary_string>: binary_substring	byte	bytes	byte	0	binary_substring	binary_string	integer
1f	byte <integer> of <file>: integer
ff	byte <integer>: binary_string	byte	bytes	byte	0	binary_string		integer
ff	bytes of <binary_string>: binary_substring	byte	bytes	bytes	1	binary_substring	binary_string	
2	cache folder of <domain>: folder
2	cache folder: folder
1f	cache_configuration of <dmi cache_information>: integer
1f	cache_information <integer> of <dmi>: dmi cache_information
1f	cache_informations of <dmi>: dmi cache_information
1f	cache_speed of <dmi cache_information>: integer
d	cached amount of <ram>: integer
e0	can create actions flag of <bes user>: boolean	can create actions flag	can create actions flags	can create actions flag	0	boolean	bes user	
10	can interact with desktop of <service>: boolean
e0	can lock flag of <bes user>: boolean	can lock flag	can lock flags	can lock flag	0	boolean	bes user	
e0	can send multiple refresh flag of <bes user>: boolean	can send multiple refresh flag	can send multiple refresh flags	can send multiple refresh flag	0	boolean	bes user	
e0	can submit queries flag of <bes role>: boolean	can submit queries flag	can submit queries flags	can submit queries flag	0	boolean	bes role	
e0	can submit queries flag of <bes user>: boolean	can submit queries flag	can submit queries flags	can submit queries flag	0	boolean	bes user	
12	capabilities of <agent interface>: agent interface capability
1f	capabilities of <dmi system_reset>: integer
12	capability <string> of <agent interface>: agent interface capability
4	capability <string> of <rpmdatabase>: capability
4	capability <string>: capability
ff	caption <string> of <html>: html	caption	captions	caption	0	html	html	string
ff	caption <string> of <string>: html	caption	captions	caption	0	html	string	string
ff	caption of <html>: html	caption	captions	caption	0	html	html	
ff	caption of <string>: html	caption	captions	caption	0	html	string	
2	carbon folder of <domain>: folder
2	carbon folder: folder
1a	case insensitive perl regexes <string>: regular expression
1a	case insensitive perl regular expressions <string>: regular expression
ff	case insensitive regexes <string>: regular expression	case insensitive regex	case insensitive regexes	case insensitive regexes	1	regular expression		string
ff	case insensitive regular expressions <string>: regular expression	case insensitive regular expression	case insensitive regular expressions	case insensitive regular expressions	1	regular expression		string
ff	casts <string>: cast	cast	casts	casts	1	cast		string
ff	casts from of <type>: cast	cast from	casts from	casts from	1	cast	type	
ff	casts returning <type>: cast	cast returning	casts returning	casts returning	1	cast		type
ff	casts: cast	cast	casts	casts	1	cast		
10	categories of <audit policy>: audit policy category
e0	category of <bes fixlet>: string	category	categories	category	0	string	bes fixlet	
e0	category of <bes property>: string	category	categories	category	0	string	bes property	
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
ff	character <integer> of <string>: substring	character	characters	character	0	substring	string	integer
ff	character <integer>: string	character	characters	character	0	string		integer
1f	character sets of <client>: string
ff	characters of <string>: substring	character	characters	characters	1	substring	string	
e0	charset of <bes fixlet>: string	charset	charsets	charset	0	string	bes fixlet	
e0	charset of <bes wizard>: string	charset	charsets	charset	0	string	bes wizard	
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
ff	cite <string> of <html>: html	cite	cites	cite	0	html	html	string
ff	cite <string> of <string>: html	cite	cites	cite	0	html	string	string
ff	cite of <html>: html	cite	cites	cite	0	html	html	
ff	cite of <string>: html	cite	cites	cite	0	html	string	
10	class id of <com handler task action>: string
10	class of <active device>: string
2	classic domain: domain
2	classic folder of <domain>: folder
2	classic folder: folder
2	classname of <registrynode>: string
1f	client cryptography: client_cryptography
ff	client device count of <bes product>: integer	client device count	client device counts	client device count	0	integer	bes product	
e0	client evaluated flag of <bes computer group>: boolean	client evaluated flag	client evaluated flags	client evaluated flag	0	boolean	bes computer group	
1f	client folder of <site>: folder
40	client id of <bes idp directory>: string	client id	client ids	client id	0	string	bes idp directory	
e0	client installed flag of <bes unmanagedasset>: boolean	client installed flag	client installed flags	client installed flag	0	boolean	bes unmanagedasset	
ff	client license: license	client license	client licenses	client license	0	license		
12	client product of <agent interface>: string
1f	client query duration of <evaluation cycle>: time interval
1f	client query percent of <evaluation cycle>: floating point
e0	client settings of <bes computer>: bes client setting	client setting	client settings	client settings	1	bes client setting	bes computer	
1f	client: client
2	cloned of <route>: boolean
2	cloning flag of <route>: boolean
1f	close wait of <tcp state>: boolean
1f	closed of <tcp state>: boolean
1f	closing of <tcp state>: boolean
ff	cloud count of <bes product>: integer	cloud count	cloud counts	cloud count	0	integer	bes product	
1f	cloud provider: cloud provider
ff	code <string> of <html>: html	code	codes	code	0	html	html	string
ff	code <string> of <string>: html	code	codes	code	0	html	string	string
ff	code of <html>: html	code	codes	code	0	html	html	
ff	code of <string>: html	code	codes	code	0	html	string	
10	code page of <user>: integer
f	codename of <operating system>: string
10	codepage of <file version block>: string
ff	col <string> of <html>: html	col	cols	col	0	html	html	string
ff	col <string> of <string>: html	col	cols	col	0	html	string	string
ff	col of <html>: html	col	cols	col	0	html	html	
ff	col of <string>: html	col	cols	col	0	html	string	
ff	colgroup <string> of <html>: html	colgroup	colgroups	colgroup	0	html	html	string
ff	colgroup <string> of <string>: html	colgroup	colgroups	colgroup	0	html	string	string
ff	colgroup of <html>: html	colgroup	colgroups	colgroup	0	html	html	
ff	colgroup of <string>: html	colgroup	colgroups	colgroup	0	html	string	
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
e0	comments of <bes action>: bes comment	comment	comments	comments	1	bes comment	bes action	
e0	comments of <bes computer>: bes comment	comment	comments	comments	1	bes comment	bes computer	
e0	comments of <bes fixlet>: bes comment	comment	comments	comments	1	bes comment	bes fixlet	
ff	common name of <license>: string	common name	common names	common name	0	string	license	
10	communications bit <operating system suite mask>: boolean
10	communications operator flag of <user>: boolean
9	compare_op of <debianpkg dependency>: string
1f	competition size of <selected server>: integer
1f	competition weight of <selected server>: integer
1f	complete time of <action>: time
b0	component <integer> of <distinguished name>: distinguished name component
ff	component <integer> of <site version list>: integer	component	components	component	0	integer	site version list	integer
2	component folder of <domain>: folder
2	component folder: folder
e0	component groups of <bes fixlet>: bes baseline component group	component group	component groups	component groups	1	bes baseline component group	bes fixlet	
12	component string of <security identifier>: string
1f	component_handle of <dmi management_device_component>: integer
e0	components of <bes baseline component group>: bes baseline component	component	components	components	1	bes baseline component	bes baseline component group	
b0	components of <distinguished name>: distinguished name component
e0	components xml of <bes fixlet>: string	components xml	components xmls	components xml	0	string	bes fixlet	
2	components: component
10	compressed of <filesystem object>: boolean
ff	computer count of <bes product>: integer	computer count	computer counts	computer count	0	integer	bes product	
e0	computer flag of <bes filter>: boolean	computer flag	computer flags	computer flag	0	boolean	bes filter	
e0	computer group flag of <bes action>: boolean	computer group flag	computer group flags	computer group flag	0	boolean	bes action	
e0	computer group set of <bes domain>: bes computer group set	computer group set	computer group sets	computer group set	0	bes computer group set	bes domain	
e0	computer group set of <bes filter>: bes fixlet set	computer group set	computer group sets	computer group set	0	bes fixlet set	bes filter	
e0	computer groups of <bes domain>: bes computer group	computer group	computer groups	computer groups	1	bes computer group	bes domain	
1f	computer id: integer
1f	computer name: string
e0	computer of <bes action result>: bes computer	computer	computers	computer	0	bes computer	bes action result	
e0	computer of <bes fixlet result>: bes computer	computer	computers	computer	0	bes computer	bes fixlet result	
e0	computer of <bes property result>: bes computer	computer	computers	computer	0	bes computer	bes property result	
10	computer of <event log record>: string
e0	computer set of <bes filter>: bes computer set	computer set	computer sets	computer set	0	bes computer set	bes filter	
2	computer: computer
ff	concatenations <html> of <html>: html	concatenation	concatenations	concatenations	1	html	html	html
ff	concatenations <html> of <string>: html	concatenation	concatenations	concatenations	1	html	string	html
ff	concatenations <string> of <html>: html	concatenation	concatenations	concatenations	1	html	html	string
ff	concatenations <string> of <string>: string	concatenation	concatenations	concatenations	1	string	string	string
ff	concatenations of <html>: html	concatenation	concatenations	concatenations	1	html	html	
ff	concatenations of <string>: string	concatenation	concatenations	concatenations	1	string	string	
2	condemned flag of <route>: boolean
4	conflicts of <package>: capability
ff	conjunctions of <boolean>: boolean	conjunction	conjunctions	conjunctions	1	boolean	boolean	
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
e0	constrain by property name of <bes action>: string	constrain by property name	constrain by property names	constrain by property name	0	string	bes action	
e0	constrain by property relation of <bes action>: string	constrain by property relation	constrain by property relations	constrain by property relation	0	string	bes action	
e0	constrain by property value of <bes action>: string	constrain by property value	constrain by property values	constrain by property value	0	string	bes action	
1f	constrained of <action>: boolean
1f	constraint of <action>: integer
1f	contained_element_count of <dmi system_enclosure_or_chassis>: integer
1f	contained_element_record_length of <dmi system_enclosure_or_chassis>: integer
10	container inherit of <access control entry>: boolean
e0	content id of <bes fixlet action>: string	content id	content ids	content id	0	string	bes fixlet action	
1f	content of <file>: file content
2	contextual menu items folder of <domain>: folder
2	contextual menu items folder: folder
e0	continue on errors flag of <bes action>: boolean	continue on errors flag	continue on errors flags	continue on errors flag	0	boolean	bes action	
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
e2	correlation coefficient of <exponential projection>: floating point	correlation coefficient	correlation coefficients	correlation coefficient	0	floating point	exponential projection	
e2	correlation coefficient of <linear projection>: floating point	correlation coefficient	correlation coefficients	correlation coefficient	0	floating point	linear projection	
e0	correlation flag of <bes computer>: boolean	correlation flag	correlation flags	correlation flag	0	boolean	bes computer	
e0	correlation id of <bes computer>: integer	correlation id	correlation ids	correlation id	0	integer	bes computer	
e0	correlation of <bes computer>: bes computer	correlation	correlations	correlation	0	bes computer	bes computer	
e0	count maps of <historical fixlet count>: fixlet count pair	count map	count maps	count maps	1	fixlet count pair	historical fixlet count	
1f	count of <cpupackage>: integer
e0	count of <fixlet count pair>: integer	count	counts	count	0	integer	fixlet count pair	
e0	count of <historical computer count>: integer	count	counts	count	0	integer	historical computer count	
12	count of <monitor power interval>: integer
2	country <string>: country
10	country code of <user>: integer
e0	cpu of <bes computer>: string	cpu	cpus	cpu	0	string	bes computer	
2	cpu speed: integer
d	cpuid level of <processor>: integer
1f	cpupackage: cpupackage
10	create file permission of <access control entry>: boolean
10	create folder permission of <access control entry>: boolean
10	create link permission of <access control entry>: boolean
10	create permission of <network share>: boolean
10	create subkey permission of <access control entry>: boolean
e0	creation date of <bes site>: time	creation date	creation dates	creation date	0	time	bes site	
e0	creation time of <bes activation>: time	creation time	creation times	creation time	0	time	bes activation	
e0	creation time of <bes computer group>: time	creation time	creation times	creation time	0	time	bes computer group	
e0	creation time of <bes fixlet>: time	creation time	creation times	creation time	0	time	bes fixlet	
e0	creation time of <bes user>: time	creation time	creation times	creation time	0	time	bes user	
12	creation time of <filesystem object>: time
10	creation time of <process>: time
10	creator group group: security account
e0	creator of <bes site>: bes user	creator	creators	creator	0	bes user	bes site	
2	creator of <bundle>: file signature
2	creator of <file>: file signature
10	creator owner group: security account
9	critical of <debianpkg dependency>: boolean
ff	cryptography: cryptography	cryptography	cryptographies	cryptography	0	cryptography		
10	csd version of <operating system>: string
10	csidl folder <integer>: folder
2	cstring <string> of <dictionary>: string
2	cstring of <osxvalue>: string
10	current action of <running task>: string
e0	current analysis: bes fixlet	current analysis	current analyses	current analysis	0	bes fixlet		
1f	current analysis: fixlet
e0	current bes servers: bes server	current bes server	current bes servers	current bes servers	1	bes server		
e0	current bes site: bes site	current bes site	current bes sites	current bes site	0	bes site		
e0	current computer: bes computer	current computer	current computers	current computer	0	bes computer		
e0	current console user: bes user	current console user	current console users	current console user	0	bes user		
ff	current date: date	current date	current dates	current date	0	date		
ff	current day_of_month: day of month	current day_of_month	current days_of_month	current day_of_month	0	day of month		
ff	current day_of_week: day of week	current day_of_week	current days_of_week	current day_of_week	0	day of week		
ff	current day_of_year: day of year	current day_of_year	current days_of_year	current day_of_year	0	day of year		
e0	current domain: bes domain	current domain	current domains	current domain	0	bes domain		
40	current explorer user: bes user	current explorer user	current explorer users	current explorer user	0	bes user		
10	current firewall profile type: firewall profile type
e0	current fixlet: bes fixlet	current fixlet	current fixlets	current fixlet	0	bes fixlet		
12	current monitor interval of <power history>: monitor power interval
ff	current month: month	current month	current months	current month	0	month		
ff	current month_and_year: month and year	current month_and_year	current months_and_years	current month_and_year	0	month and year		
12	current network of <wifi>: wifi network
10	current profile of <firewall policy>: firewall profile
10	current profile type of <firewall>: firewall profile type
1f	current relay: current relay
1f	current site: site
d	current status of <SELinux Boolean>: boolean
12	current system interval of <power history>: system power interval
e0	current task: bes fixlet	current task	current tasks	current task	0	bes fixlet		
ff	current time_of_day <time zone>: time of day with time zone	current time_of_day	current times_of_day	current time_of_day	0	time of day with time zone		time zone
ff	current time_of_day: time of day with time zone	current time_of_day	current times_of_day	current time_of_day	0	time of day with time zone		
e0	current unmanagedasset: bes unmanagedasset	current unmanagedasset	current unmanagedassets	current unmanagedasset	0	bes unmanagedasset		
2	current user folder of <domain>: folder
2	current user folder: folder
10	current user key <logged on user> of <registry>: registry key
10	current user key of <registry>: registry key
1f	current user: logged on user
e0	current wizard: bes wizard	current wizard	current wizards	current wizard	0	bes wizard		
ff	current year: year	current year	current years	current year	0	year		
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
e0	custom bes fixlet set: bes fixlet set	custom bes fixlet set	custom bes fixlet sets	custom bes fixlet set	0	bes fixlet set		
e0	custom bes fixlets: bes fixlet	custom bes fixlet	custom bes fixlets	custom bes fixlets	1	bes fixlet		
e0	custom content flag of <bes user>: boolean	custom content flag	custom content flags	custom content flag	0	boolean	bes user	
10	custom firewall scope: firewall scope
e0	custom fixlet set of <bes domain>: bes fixlet set	custom fixlet set	custom fixlet sets	custom fixlet set	0	bes fixlet set	bes domain	
e0	custom fixlets of <bes domain>: bes fixlet	custom fixlet	custom fixlets	custom fixlets	1	bes fixlet	bes domain	
e0	custom flag of <bes fixlet>: boolean	custom flag	custom flags	custom flag	0	boolean	bes fixlet	
e0	custom flag of <bes property>: boolean	custom flag	custom flags	custom flag	0	boolean	bes property	
e0	custom refresh interval flag of <bes computer group>: boolean	custom refresh interval flag	custom refresh interval flags	custom refresh interval flag	0	boolean	bes computer group	
e0	custom refresh interval of <bes computer group>: time interval	custom refresh interval	custom refresh intervals	custom refresh interval	0	time interval	bes computer group	
e0	custom site flag of <bes fixlet>: boolean	custom site flag	custom site flags	custom site flag	0	boolean	bes fixlet	
e0	custom site flag of <bes site>: boolean	custom site flag	custom site flags	custom site flag	0	boolean	bes site	
e0	custom site of <bes fixlet>: bes site	custom site	custom sites	custom site	0	bes site	bes fixlet	
e0	custom site set of <bes domain>: bes site set	custom site set	custom site sets	custom site set	0	bes site set	bes domain	
1f	custom site subscription effective date <string>: time
e0	custom sites of <bes domain>: bes site	custom site	custom sites	custom sites	1	bes site	bes domain	
e0	custom success relevance of <bes action>: string	custom success relevance	custom success relevances	custom success relevance	0	string	bes action	
e0	custom success relevance of <bes fixlet action>: string	custom success relevance	custom success relevances	custom success relevance	0	string	bes fixlet action	
10	customized of <firewall service>: boolean
e0	cve id list of <bes fixlet>: string	cve id list	cve id lists	cve id list	0	string	bes fixlet	
10	dacl of <security descriptor>: discretionary access control list
10	daily task trigger type: task trigger type
e0	dashboard id of <bes wizard>: string	dashboard id	dashboard ids	dashboard id	0	string	bes wizard	
2	data <string> of <dictionary>: binary_string
10	data file of <site profile>: file
1f	data folder of <client>: folder
2	data fork of <file>: datafork
10	data of <com handler task action>: string
2	data of <osxvalue>: binary_string
10	data of <task definition>: string
1f	data_width of <dmi memory_device>: integer
e0	database id of <bes action>: integer	database id	database ids	database id	0	integer	bes action	
e0	database id of <bes activation>: integer	database id	database ids	database id	0	integer	bes activation	
e0	database id of <bes computer group>: integer	database id	database ids	database id	0	integer	bes computer group	
e0	database id of <bes computer>: integer	database id	database ids	database id	0	integer	bes computer	
e0	database id of <bes deployment option>: integer	database id	database ids	database id	0	integer	bes deployment option	
40	database id of <bes peer download>: integer	database id	database ids	database id	0	integer	bes peer download	
e0	database id of <bes property>: integer	database id	database ids	database id	0	integer	bes property	
e0	database id of <bes server>: integer	database id	database ids	database id	0	integer	bes server	
e0	database id of <bes wakeonlan status>: integer	database id	database ids	database id	0	integer	bes wakeonlan status	
e0	database id of <bes wizard>: integer	database id	database ids	database id	0	integer	bes wizard	
e0	database id of <historical computer count>: integer	database id	database ids	database id	0	integer	historical computer count	
e0	database id of <historical fixlet count>: integer	database id	database ids	database id	0	integer	historical fixlet count	
e0	database name of <bes action>: string	database name	database names	database name	0	string	bes action	
e0	database name of <bes computer>: string	database name	database names	database name	0	string	bes computer	
e0	database name of <bes deployment option>: string	database name	database names	database name	0	string	bes deployment option	
40	database name of <bes peer download>: string	database name	database names	database name	0	string	bes peer download	
e0	database name of <bes server>: string	database name	database names	database name	0	string	bes server	
e0	database name of <bes wakeonlan status>: string	database name	database names	database name	0	string	bes wakeonlan status	
e0	database name of <bes wizard>: string	database name	database names	database name	0	string	bes wizard	
40	database type of <bes server>: string	database type	database types	database type	0	string	bes server	
10	datacenter bit <operating system suite mask>: boolean
e0	datastore inspector: module	datastore inspector	datastore inspectors	datastore inspector	0	module		
2	date <integer> of <array>: time
2	date <string> of <dictionary>: time
2	date <string> of <preference>: time
ff	date <string>: date	date	dates	date	0	date		string
ff	date <time zone> of <time>: date	date	dates	date	0	date	time	time zone
1f	date of <bios>: string
2	date of <osxvalue>: time
10	date of <task registration info>: time
e0	date range end of <bes action>: date	date range end	date range ends	date range end	0	date	bes action	
e0	date range start of <bes action>: date	date range start	date range starts	date range start	0	date	bes action	
ff	day of <day of year>: day of month	day	days	day	0	day of month	day of year	
ff	day: time interval	day	days	day	0	time interval		
ff	day_of_month <integer>: day of month	day_of_month	days_of_month	day_of_month	0	day of month		integer
ff	day_of_month <string>: day of month	day_of_month	days_of_month	day_of_month	0	day of month		string
ff	day_of_month of <date>: day of month	day_of_month	days_of_month	day_of_month	0	day of month	date	
ff	day_of_week <string>: day of week	day_of_week	days_of_week	day_of_week	0	day of week		string
e0	day_of_week constraints of <bes action>: day of week	day_of_week constraint	day_of_week constraints	day_of_week constraints	1	day of week	bes action	
ff	day_of_week of <date>: day of week	day_of_week	days_of_week	day_of_week	0	day of week	date	
ff	day_of_year of <date>: day of year	day_of_year	days_of_year	day_of_year	0	day of year	date	
10	days interval of <daily task trigger>: time interval
10	days runs of <monthly task trigger>: day of month
10	days runs of <monthlydow task trigger>: day of week
10	days runs of <weekly task trigger>: day of week
ff	dd <string> of <html>: html	dd	dds	dd	0	html	html	string
ff	dd <string> of <string>: html	dd	dds	dd	0	html	string	string
ff	dd of <html>: html	dd	dds	dd	0	html	html	
ff	dd of <string>: html	dd	dds	dd	0	html	string	
9	debian package version <debian package version>: debian package version
9	debian package version <string>: debian package version
9	debian package version epoch <debian package version epoch>: debian package version epoch
9	debian package version epoch <string>: debian package version epoch
9	debian package version revision <debian package version revision>: debian package version revision
9	debian package version revision <string>: debian package version revision
9	debian package version upstream <debian package upstream version>: debian package upstream version
9	debian package version upstream <string>: debian package upstream version
9	debianpackage: debianpackagecache
ff	december <integer> of <integer>: date	december	decembers	december	0	date	integer	integer
ff	december <integer>: day of year	december	decembers	december	0	day of year		integer
ff	december of <integer>: month and year	december	decembers	december	0	month and year	integer	
ff	december: month	december	decembers	december	0	month		
e0	default action of <bes fixlet>: bes fixlet action	default action	default actions	default action	0	bes fixlet action	bes fixlet	
e0	default flag of <bes property>: boolean	default flag	default flags	default flag	0	boolean	bes property	
d	default image of <grub config file>: grub image choice
2	default of <route>: boolean
e0	default page name of <bes wizard>: string	default page name	default page names	default page name	0	string	bes wizard	
10	default value of <registry key>: registry key value
10	default web browser: application
d	default web browser: file
ff	definition lists <string> of <html>: html	definition list	definition lists	definition lists	1	html	html	string
ff	definition lists <string> of <string>: html	definition list	definition lists	definition lists	1	html	string	string
ff	definition lists of <html>: html	definition list	definition lists	definition lists	1	html	html	
ff	definition lists of <string>: html	definition list	definition lists	definition lists	1	html	string	
e0	definition of <bes property>: string	definition	definitions	definition	0	string	bes property	
10	definition of <scheduled task>: task definition
ff	del <string> of <html>: html	del	dels	del	0	html	html	string
ff	del <string> of <string>: html	del	dels	del	0	html	string	string
ff	del of <html>: html	del	dels	del	0	html	html	
ff	del of <string>: html	del	dels	del	0	html	string	
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
e0	deleted flag of <bes comment>: boolean	deleted flag	deleted flags	deleted flag	0	boolean	bes comment	
10	deny type of <access control entry>: boolean
10	dep enabled of <process>: boolean
9	dependencies of <debian versioned package>: debianpkg dependency
ff	dependency known of <property>: boolean	dependency known	dependencies known	dependency known	0	boolean	property	
1f	deployment character set of <client>: string
1f	descendant folders of <folder>: folder
1f	descendants of <folder>: file
10	descendants of <task folder>: scheduled task
10	description of <active device>: string
e0	description of <bes site>: string	description	descriptions	description	0	string	bes site	
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
ff	desired fips mode of <cryptography>: boolean	desired fips mode	desired fips modes	desired fips mode	0	boolean	cryptography	
2	desktop folder of <domain>: folder
2	desktop folder: folder
f	destination of <route>: ipv4or6 address
2	destination string of <route>: string
2	destination type of <route>: string
e0	detailed status of <bes action result>: string	detailed status	detailed statuses	detailed status	0	string	bes action result	
10	detailed tracking category of <audit policy>: audit policy category
2	developer docs folder of <domain>: folder
2	developer docs folder: folder
2	developer folder of <domain>: folder
2	developer folder: folder
2	developer help folder of <domain>: folder
2	developer help folder: folder
5f	device count of <bes product>: integer	device count	device counts	device count	0	integer	bes product	
d	device file <filesystem object>: device file
d	device file <string> of <folder>: device file
d	device file <string>: device file
d	device file <symlink>: device file
d	device files of <folder>: device file
10	device name of <connection>: string
d	device name of <filesystem>: string
d	device of <grub file location>: grub device
e0	device type of <bes computer>: string	device type	device types	device type	0	string	bes computer	
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
ff	dfn <string> of <html>: html	dfn	dfns	dfn	0	html	html	string
ff	dfn <string> of <string>: html	dfn	dfns	dfn	0	html	string	string
ff	dfn of <html>: html	dfn	dfns	dfn	0	html	html	
ff	dfn of <string>: html	dfn	dfns	dfn	0	html	string	
10	dhcp enabled of <network adapter>: boolean
10	dhcp server of <network adapter>: ipv4 address
e0	dialog flag of <bes wizard>: boolean	dialog flag	dialog flags	dialog flag	0	boolean	bes wizard	
10	dialup group: security account
2	dictionary <integer> of <array>: dictionary
2	dictionary <string> of <dictionary>: dictionary
2	dictionary <string> of <preference>: dictionary
2	dictionary of <file>: dictionary
2	dictionary of <osxvalue>: dictionary
2	dictionary of <registrynode>: dictionary
2	dictionary of <registryroot>: dictionary
e0	digest file name of <bes fixlet>: string	digest file name	digest file names	digest file name	0	string	bes fixlet	
ff	direct object type of <property>: type	direct object type	direct object types	direct object type	0	type	property	
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
ff	disjunctions of <boolean>: boolean	disjunction	disjunctions	disjunctions	1	boolean	boolean	
e0	disk usage of <bes property>: integer	disk usage	disk usages	disk usage	0	integer	bes property	
e0	display category of <bes fixlet>: string	display category	display categories	display category	0	string	bes fixlet	
e0	display category of <bes property>: string	display category	display categories	display category	0	string	bes property	
e0	display message of <bes fixlet>: html	display message	display messages	display message	0	html	bes fixlet	
e0	display name of <bes domain>: string	display name	display names	display name	0	string	bes domain	
e0	display name of <bes fixlet>: string	display name	display names	display name	0	string	bes fixlet	
e0	display name of <bes property>: string	display name	display names	display name	0	string	bes property	
e0	display name of <bes site>: string	display name	display names	display name	0	string	bes site	
e0	display name of <bes wizard>: string	display name	display names	display name	0	string	bes wizard	
1a	display name of <operating system>: string
10	display name of <service>: string
10	display name of <task principal>: string
e0	display simple name of <bes property>: string	display simple name	display simple names	display simple name	0	string	bes property	
e0	display source id of <bes fixlet>: string	display source id	display source ids	display source id	0	string	bes fixlet	
e0	display source of <bes fixlet>: string	display source	display sources	display source	0	string	bes fixlet	
e0	display source severity of <bes fixlet>: string	display source severity	display source severities	display source severity	0	string	bes fixlet	
e0	display value of <bes fixlet field value>: string	display value	display values	display value	0	string	bes fixlet field value	
10	display version of <operating system>: string
1f	distance of <selected server>: integer range
b0	distinguished name <string>: distinguished name
12	distinguished name error message of <active directory group>: string
12	distinguished name error message of <active directory local computer>: string
12	distinguished name error message of <active directory local user>: string
12	distinguished name of <active directory group>: string
12	distinguished name of <active directory local computer>: string
12	distinguished name of <active directory local user>: string
e0	distinguished name of <bes user>: string	distinguished name	distinguished names	distinguished name	0	string	bes user	
ff	div <string> of <html>: html	div	divs	div	0	html	html	string
ff	div <string> of <string>: html	div	divs	div	0	html	string	string
ff	div of <html>: html	div	divs	div	0	html	html	
ff	div of <string>: html	div	divs	div	0	html	string	
ff	divided by zero of <floating point>: boolean	divided by zero	divided by zeroes	divided by zero	0	boolean	floating point	
1f	dmi: dmi
12	dns domainname of <active directory local computer>: string
12	dns domainname of <active directory local user>: string
1f	dns name: string
10	dns servers of <network adapter>: network address list
10	dns servers of <network>: network address list
10	dns suffix of <network adapter>: string
e0	document flag of <bes wizard>: boolean	document flag	document flags	document flag	0	boolean	bes wizard	
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
e0	domain of <bes action>: bes domain	domain	domains	domain	0	bes domain	bes action	
e0	domain of <bes computer group>: bes domain	domain	domains	domain	0	bes domain	bes computer group	
e0	domain of <bes filter>: bes domain	domain	domains	domain	0	bes domain	bes filter	
e0	domain of <bes fixlet>: bes domain	domain	domains	domain	0	bes domain	bes fixlet	
10	domain of <user>: string
10	domain profile of <firewall policy>: firewall profile
e0	domain set of <bes site>: bes domain set	domain set	domain sets	domain set	0	bes domain set	bes site	
2	domain top folder of <domain>: folder
2	domain top folder: folder
10	domain user <string>: user
10	domain user of <active directory local user>: user
10	domain users: user
d	domainname: string
e0	domains of <bes site>: bes domain	domain	domains	domains	1	bes domain	bes site	
2	done flag of <route>: boolean
1f	download failure of <action>: integer
1f	download file <string> of <encoding>: file
1f	download file <string>: file
1f	download folder of <encoding>: folder
1f	download folder: folder
ff	download hash algorithms of <license>: string	download hash algorithm	download hash algorithms	download hash algorithms	1	string	license	
1f	download path <string>: string
1f	download server: download server
e0	download size of <bes fixlet>: integer	download size	download sizes	download size	0	integer	bes fixlet	
1d	download storage folder: download storage folder
40	downloader computer id of <bes peer download>: integer	downloader computer id	downloader computer ids	downloader computer id	0	integer	bes peer download	
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
ff	dt <string> of <html>: html	dt	dts	dt	0	html	html	string
ff	dt <string> of <string>: html	dt	dts	dt	0	html	string	string
ff	dt of <html>: html	dt	dts	dt	0	html	html	
ff	dt of <string>: html	dt	dts	dt	0	html	string	
10	duration of <task repetition pattern>: time interval
2	dynamic flag of <route>: boolean
10	edge traversal allowed of <firewall rule>: boolean
e0	editable flag of <bes unmanagedasset field>: boolean	editable flag	editable flags	editable flag	0	boolean	bes unmanagedasset field	
10	effective access mode for <security account> of <access control list>: integer
10	effective access mode for <string> of <access control list>: integer
10	effective access system security permission for <security account> of <access control list>: boolean
10	effective access system security permission for <string> of <access control list>: boolean
10	effective append permission for <security account> of <access control list>: boolean
10	effective append permission for <string> of <access control list>: boolean
40	effective can create actions flag of <bes user>: boolean	effective can create actions flag	effective can create actions flags	effective can create actions flag	0	boolean	bes user	
40	effective can lock flag of <bes user>: boolean	effective can lock flag	effective can lock flags	effective can lock flag	0	boolean	bes user	
40	effective can send multiple refresh flag of <bes user>: boolean	effective can send multiple refresh flag	effective can send multiple refresh flags	effective can send multiple refresh flag	0	boolean	bes user	
40	effective can submit queries flag of <bes user>: boolean	effective can submit queries flag	effective can submit queries flags	effective can submit queries flag	0	boolean	bes user	
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
40	effective custom content flag of <bes user>: boolean	effective custom content flag	effective custom content flags	effective custom content flag	0	boolean	bes user	
1f	effective date of <action lock state>: time
14	effective date of <plugin store key>: time
1f	effective date of <setting>: time
10	effective delete child permission for <security account> of <access control list>: boolean
10	effective delete child permission for <string> of <access control list>: boolean
10	effective delete permission for <security account> of <access control list>: boolean
10	effective delete permission for <string> of <access control list>: boolean
ff	effective download hash algorithm of <license>: string	effective download hash algorithm	effective download hash algorithms	effective download hash algorithm	0	string	license	
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
40	effective master flag of <bes user>: boolean	effective master flag	effective master flags	effective master flag	0	boolean	bes user	
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
40	effective restartandshutdown actionscript privilege allowboth flag of <bes user>: boolean	effective restartandshutdown actionscript privilege allowboth flag	effective restartandshutdown actionscript privilege allowboth flags	effective restartandshutdown actionscript privilege allowboth flag	0	boolean	bes user	
40	effective restartandshutdown actionscript privilege allowrestartonly flag of <bes user>: boolean	effective restartandshutdown actionscript privilege allowrestartonly flag	effective restartandshutdown actionscript privilege allowrestartonly flags	effective restartandshutdown actionscript privilege allowrestartonly flag	0	boolean	bes user	
40	effective restartandshutdown actionscript privilege none flag of <bes user>: boolean	effective restartandshutdown actionscript privilege none flag	effective restartandshutdown actionscript privilege none flags	effective restartandshutdown actionscript privilege none flag	0	boolean	bes user	
40	effective restartandshutdown postaction privilege allowboth flag of <bes user>: boolean	effective restartandshutdown postaction privilege allowboth flag	effective restartandshutdown postaction privilege allowboth flags	effective restartandshutdown postaction privilege allowboth flag	0	boolean	bes user	
40	effective restartandshutdown postaction privilege allowrestartonly flag of <bes user>: boolean	effective restartandshutdown postaction privilege allowrestartonly flag	effective restartandshutdown postaction privilege allowrestartonly flags	effective restartandshutdown postaction privilege allowrestartonly flag	0	boolean	bes user	
40	effective restartandshutdown postaction privilege none flag of <bes user>: boolean	effective restartandshutdown postaction privilege none flag	effective restartandshutdown postaction privilege none flags	effective restartandshutdown postaction privilege none flag	0	boolean	bes user	
10	effective set value permission for <security account> of <access control list>: boolean
10	effective set value permission for <string> of <access control list>: boolean
40	effective show other action flag of <bes user>: boolean	effective show other action flag	effective show other action flags	effective show other action flag	0	boolean	bes user	
ff	effective signature hash algorithm of <license>: string	effective signature hash algorithm	effective signature hash algorithms	effective signature hash algorithm	0	string	license	
40	effective stop other actions flag of <bes user>: boolean	effective stop other actions flag	effective stop other actions flags	effective stop other actions flag	0	boolean	bes user	
10	effective synchronize permission for <security account> of <access control list>: boolean
10	effective synchronize permission for <string> of <access control list>: boolean
d	effective time of <runlevel>: time
10	effective traverse permission for <security account> of <access control list>: boolean
10	effective traverse permission for <string> of <access control list>: boolean
40	effective unmanagedasset privilege scanpoint flag of <bes user>: boolean	effective unmanagedasset privilege scanpoint flag	effective unmanagedasset privilege scanpoint flags	effective unmanagedasset privilege scanpoint flag	0	boolean	bes user	
40	effective unmanagedasset privilege showall flag of <bes user>: boolean	effective unmanagedasset privilege showall flag	effective unmanagedasset privilege showall flags	effective unmanagedasset privilege showall flag	0	boolean	bes user	
40	effective unmanagedasset privilege shownone flag of <bes user>: boolean	effective unmanagedasset privilege shownone flag	effective unmanagedasset privilege shownone flags	effective unmanagedasset privilege shownone flag	0	boolean	bes user	
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
ff	element <integer> of <json value>: json value	element	elements	element	0	json value	json value	integer
e0	elements of <bes action set>: bes action	element	elements	elements	1	bes action	bes action set	
e0	elements of <bes computer group set>: bes computer group	element	elements	elements	1	bes computer group	bes computer group set	
e0	elements of <bes computer set>: bes computer	element	elements	elements	1	bes computer	bes computer set	
e0	elements of <bes domain set>: bes domain	element	elements	elements	1	bes domain	bes domain set	
e0	elements of <bes filter set>: bes filter	element	elements	elements	1	bes filter	bes filter set	
e0	elements of <bes fixlet set>: bes fixlet	element	elements	elements	1	bes fixlet	bes fixlet set	
40	elements of <bes idp directory set>: bes idp directory	element	elements	elements	1	bes idp directory	bes idp directory set	
e0	elements of <bes ldap directory set>: bes ldap directory	element	elements	elements	1	bes ldap directory	bes ldap directory set	
e0	elements of <bes property set>: bes property	element	elements	elements	1	bes property	bes property set	
e0	elements of <bes role set>: bes role	element	elements	elements	1	bes role	bes role set	
e0	elements of <bes site file set>: bes site file	element	elements	elements	1	bes site file	bes site file set	
e0	elements of <bes site set>: bes site	element	elements	elements	1	bes site	bes site set	
e0	elements of <bes unmanagedasset set>: bes unmanagedasset	element	elements	elements	1	bes unmanagedasset	bes unmanagedasset set	
e0	elements of <bes user set>: bes user	element	elements	elements	1	bes user	bes user set	
e0	elements of <bes webui app set>: bes webui app	element	elements	elements	1	bes webui app	bes webui app set	
e0	elements of <bes wizard set>: bes wizard	element	elements	elements	1	bes wizard	bes wizard set	
ff	elements of <integer set>: integer	element	elements	elements	1	integer	integer set	
ff	elements of <json value>: json value	element	elements	elements	1	json value	json value	
ff	elements of <string set>: string	element	elements	elements	1	string	string set	
ff	em <string> of <html>: html	em	ems	em	0	html	html	string
ff	em <string> of <string>: html	em	ems	em	0	html	string	string
ff	em of <html>: html	em	ems	em	0	html	html	
ff	em of <string>: html	em	ems	em	0	html	string	
ff	email address of <license>: string	email address	email addresses	email address	0	string	license	
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
e0	enabled of <bes wakeonlan status>: boolean	enabled	enableds	enabled	0	boolean	bes wakeonlan status	
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
ff	encryption certificate of <license>: x509 certificate	encryption certificate	encryption certificates	encryption certificate	0	x509 certificate	license	
12	encryption of <wifi>: string
10	end boundary of <task trigger>: time
e0	end date of <bes action>: date	end date	end dates	end date	0	date	bes action	
e0	end flag of <bes action>: boolean	end flag	end flags	end flag	0	boolean	bes action	
ff	end of <binary_substring>: binary position	end	ends	end	0	binary position	binary_substring	
e0	end of <statistic range>: time	end	ends	end	0	time	statistic range	
e0	end of <statistical bin>: time	end	ends	end	0	time	statistical bin	
ff	end of <substring>: string position	end	ends	end	0	string position	substring	
ff	end of <time range>: time	end	ends	end	0	time	time range	
e0	end time of <bes action result>: time	end time	end times	end time	0	time	bes action result	
e0	end time_of_day of <bes action>: time of day	end time_of_day	end times_of_day	end time_of_day	0	time of day	bes action	
1f	end_of_table <integer> of <dmi>: dmi end_of_table
1f	end_of_tables of <dmi>: dmi end_of_table
1f	ending_address of <dmi memory_array_mapped_address>: integer
1f	ending_address of <dmi memory_device_mapped_address>: integer
10	engine pid of <running task>: integer
ff	enhanced security of <license>: boolean	enhanced security	enhanced securities	enhanced security	0	boolean	license	
10	enterprise bit <operating system suite mask>: boolean
10	entries of <access control list>: access control entry
2	entries of <dictionary>: dictionaryentry
10	enumerate subkeys permission of <access control entry>: boolean
d	environment of <process>: environment
1f	environment: environment
9	epoch of <debian package version>: debian package version epoch
4	epoch of <rpm package version record>: integer
4	epoch of <short rpm package version record>: integer
ff	error <string>: undefined	error	errors	error	0	undefined		string
12	error code of <agent interface capability>: integer
10	error event log event type: event log event type
e0	error flag of <bes property result>: boolean	error flag	error flags	error flag	0	boolean	bes property result	
e0	error message of <bes property result>: string	error message	error messages	error message	0	string	bes property result	
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
ff	evaluation of <license>: boolean	evaluation	evaluations	evaluation	0	boolean	license	
40	evaluation period of <bes fixlet>: time interval	evaluation period	evaluation periods	evaluation period	0	time interval	bes fixlet	
e0	evaluation period of <bes property>: time interval	evaluation period	evaluation periods	evaluation period	0	time interval	bes property	
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
e0	exit code of <bes action result>: integer	exit code	exit codes	exit code	0	integer	bes action result	
10	expand environment string of <string>: string
10	expand x32 environment string of <string>: string
10	expand x64 environment string of <string>: string
1f	expiration date of <action lock state>: time
ff	expiration date of <bes product>: date	expiration date	expiration dates	expiration date	0	date	bes product	
ff	expiration date of <license>: time	expiration date	expiration dates	expiration date	0	time	license	
e0	expiration flag of <bes action>: boolean	expiration flag	expiration flags	expiration flag	0	boolean	bes action	
ff	expiration state of <license>: string	expiration state	expiration states	expiration state	0	string	license	
e0	expiration time of <bes action>: time	expiration time	expiration times	expiration time	0	time	bes action	
2	expiration time of <route>: time
40	explicit can create actions flag of <bes user>: boolean	explicit can create actions flag	explicit can create actions flags	explicit can create actions flag	0	boolean	bes user	
40	explicit can lock flag of <bes user>: boolean	explicit can lock flag	explicit can lock flags	explicit can lock flag	0	boolean	bes user	
40	explicit can send multiple refresh flag of <bes user>: boolean	explicit can send multiple refresh flag	explicit can send multiple refresh flags	explicit can send multiple refresh flag	0	boolean	bes user	
40	explicit can submit queries flag of <bes user>: boolean	explicit can submit queries flag	explicit can submit queries flags	explicit can submit queries flag	0	boolean	bes user	
40	explicit custom content flag of <bes user>: boolean	explicit custom content flag	explicit custom content flags	explicit custom content flag	0	boolean	bes user	
40	explicit master flag of <bes user>: boolean	explicit master flag	explicit master flags	explicit master flag	0	boolean	bes user	
e0	explicit owner set of <bes site>: bes user set	explicit owner set	explicit owner sets	explicit owner set	0	bes user set	bes site	
e0	explicit owners of <bes site>: bes user	explicit owner	explicit owners	explicit owners	1	bes user	bes site	
e0	explicit reader set of <bes site>: bes user set	explicit reader set	explicit reader sets	explicit reader set	0	bes user set	bes site	
e0	explicit readers of <bes site>: bes user	explicit reader	explicit readers	explicit readers	1	bes user	bes site	
40	explicit restartandshutdown actionscript privilege allowboth flag of <bes user>: boolean	explicit restartandshutdown actionscript privilege allowboth flag	explicit restartandshutdown actionscript privilege allowboth flags	explicit restartandshutdown actionscript privilege allowboth flag	0	boolean	bes user	
40	explicit restartandshutdown actionscript privilege allowrestartonly flag of <bes user>: boolean	explicit restartandshutdown actionscript privilege allowrestartonly flag	explicit restartandshutdown actionscript privilege allowrestartonly flags	explicit restartandshutdown actionscript privilege allowrestartonly flag	0	boolean	bes user	
40	explicit restartandshutdown actionscript privilege none flag of <bes user>: boolean	explicit restartandshutdown actionscript privilege none flag	explicit restartandshutdown actionscript privilege none flags	explicit restartandshutdown actionscript privilege none flag	0	boolean	bes user	
40	explicit restartandshutdown postaction privilege allowboth flag of <bes user>: boolean	explicit restartandshutdown postaction privilege allowboth flag	explicit restartandshutdown postaction privilege allowboth flags	explicit restartandshutdown postaction privilege allowboth flag	0	boolean	bes user	
40	explicit restartandshutdown postaction privilege allowrestartonly flag of <bes user>: boolean	explicit restartandshutdown postaction privilege allowrestartonly flag	explicit restartandshutdown postaction privilege allowrestartonly flags	explicit restartandshutdown postaction privilege allowrestartonly flag	0	boolean	bes user	
40	explicit restartandshutdown postaction privilege none flag of <bes user>: boolean	explicit restartandshutdown postaction privilege none flag	explicit restartandshutdown postaction privilege none flags	explicit restartandshutdown postaction privilege none flag	0	boolean	bes user	
40	explicit show other action flag of <bes user>: boolean	explicit show other action flag	explicit show other action flags	explicit show other action flag	0	boolean	bes user	
40	explicit stop other actions flag of <bes user>: boolean	explicit stop other actions flag	explicit stop other actions flags	explicit stop other actions flag	0	boolean	bes user	
40	explicit unmanagedasset privilege scanpoint flag of <bes user>: boolean	explicit unmanagedasset privilege scanpoint flag	explicit unmanagedasset privilege scanpoint flags	explicit unmanagedasset privilege scanpoint flag	0	boolean	bes user	
40	explicit unmanagedasset privilege showall flag of <bes user>: boolean	explicit unmanagedasset privilege showall flag	explicit unmanagedasset privilege showall flags	explicit unmanagedasset privilege showall flag	0	boolean	bes user	
40	explicit unmanagedasset privilege shownone flag of <bes user>: boolean	explicit unmanagedasset privilege shownone flag	explicit unmanagedasset privilege shownone flags	explicit unmanagedasset privilege shownone flag	0	boolean	bes user	
e0	explicit writer set of <bes site>: bes user set	explicit writer set	explicit writer sets	explicit writer set	0	bes user set	bes site	
e0	explicit writers of <bes site>: bes user	explicit writer	explicit writers	explicit writers	1	bes user	bes site	
18	explorer service: service
e0	exponential fit of <statistical bin>: exponential projection	exponential fit	exponential fits	exponential fit	0	exponential projection	statistical bin	
12	extended family of <processor>: integer
1f	extended feature mask of <processor>: integer
12	extended model of <processor>: integer
e0	extension flag of <bes computer>: boolean	extension flag	extension flags	extension flag	0	boolean	bes computer	
2	extensions <string>: enableable_file
2	extensions folder of <domain>: folder
2	extensions folder: folder
2	extensions: enableable_file
10	external port of <port mapping>: integer
e0	external site flag of <bes site>: boolean	external site flag	external site flags	external site flag	0	boolean	bes site	
1f	external_clock of <dmi processor_information>: integer
1f	external_connector_type of <dmi port_connector_information>: integer
1f	external_reference_designator of <dmi port_connector_information>: string
e2	extrapolation <time> of <exponential projection>: floating point	extrapolation	extrapolations	extrapolation	0	floating point	exponential projection	time
e2	extrapolation <time> of <linear projection>: floating point	extrapolation	extrapolations	extrapolation	0	floating point	linear projection	time
ff	extremas of <date>: ( date, date )	extrema	extremas	extremas	1	( date, date )	date	
ff	extremas of <day of month>: ( day of month, day of month )	extrema	extremas	extremas	1	( day of month, day of month )	day of month	
ff	extremas of <day of year>: ( day of year, day of year )	extrema	extremas	extremas	1	( day of year, day of year )	day of year	
9	extremas of <debian package upstream version>: ( debian package upstream version, debian package upstream version )
9	extremas of <debian package version epoch>: ( debian package version epoch, debian package version epoch )
9	extremas of <debian package version revision>: ( debian package version revision, debian package version revision )
9	extremas of <debian package version>: ( debian package version, debian package version )
ff	extremas of <floating point>: ( floating point, floating point )	extrema	extremas	extremas	1	( floating point, floating point )	floating point	
ff	extremas of <hertz>: ( hertz, hertz )	extrema	extremas	extremas	1	( hertz, hertz )	hertz	
ff	extremas of <integer>: ( integer, integer )	extrema	extremas	extremas	1	( integer, integer )	integer	
ff	extremas of <ipv4 address>: ( ipv4 address, ipv4 address )	extrema	extremas	extremas	1	( ipv4 address, ipv4 address )	ipv4 address	
ff	extremas of <ipv4or6 address>: ( ipv4or6 address, ipv4or6 address )	extrema	extremas	extremas	1	( ipv4or6 address, ipv4or6 address )	ipv4or6 address	
ff	extremas of <ipv6 address>: ( ipv6 address, ipv6 address )	extrema	extremas	extremas	1	( ipv6 address, ipv6 address )	ipv6 address	
5a	extremas of <large integer>: ( large integer, large integer )	extrema	extremas	extremas	1	( large integer, large integer )	large integer	
ff	extremas of <month and year>: ( month and year, month and year )	extrema	extremas	extremas	1	( month and year, month and year )	month and year	
ff	extremas of <month>: ( month, month )	extrema	extremas	extremas	1	( month, month )	month	
ff	extremas of <number of months>: ( number of months, number of months )	extrema	extremas	extremas	1	( number of months, number of months )	number of months	
e2	extremas of <rate>: ( rate, rate )	extrema	extremas	extremas	1	( rate, rate )	rate	
4	extremas of <rpm package release>: ( rpm package release, rpm package release )
4	extremas of <rpm package version record>: ( rpm package version record, rpm package version record )
4	extremas of <rpm package version>: ( rpm package version, rpm package version )
4	extremas of <short rpm package version record>: ( short rpm package version record, short rpm package version record )
ff	extremas of <site version list>: ( site version list, site version list )	extrema	extremas	extremas	1	( site version list, site version list )	site version list	
ff	extremas of <time interval>: ( time interval, time interval )	extrema	extremas	extremas	1	( time interval, time interval )	time interval	
ff	extremas of <time of day>: ( time of day, time of day )	extrema	extremas	extremas	1	( time of day, time of day )	time of day	
ff	extremas of <time>: ( time, time )	extrema	extremas	extremas	1	( time, time )	time	
5a	extremas of <uinteger>: ( uinteger, uinteger )	extrema	extremas	extremas	1	( uinteger, uinteger )	uinteger	
1f	extremas of <uuid>: ( uuid, uuid )
ff	extremas of <version>: ( version, version )	extrema	extremas	extremas	1	( version, version )	version	
ff	extremas of <year>: ( year, year )	extrema	extremas	extremas	1	( year, year )	year	
d	f00f bug of <processor>: boolean
e0	failure rate of <statistical bin>: floating point	failure rate	failure rates	failure rate	0	floating point	statistical bin	
d	fallback image <integer> of <grub config file>: grub image choice
d	fallback images of <grub config file>: grub image choice
ff	false: boolean	false	falses	false	0	boolean		
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
ff	february <integer> of <integer>: date	february	februarys	february	0	date	integer	integer
ff	february <integer>: day of year	february	februarys	february	0	day of year		integer
ff	february of <integer>: month and year	february	februarys	february	0	month and year	integer	
ff	february: month	february	februarys	february	0	month		
e0	field <string> of <bes fixlet>: bes fixlet field	field	fields	field	0	bes fixlet field	bes fixlet	string
e0	fields of <bes fixlet>: bes fixlet field	field	fields	fields	1	bes fixlet field	bes fixlet	
e0	fields of <bes unmanagedasset>: bes unmanagedasset field	field	fields	fields	1	bes unmanagedasset field	bes unmanagedasset	
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
e0	filter set of <bes domain>: bes filter set	filter set	filter sets	filter set	0	bes filter set	bes domain	
e0	filterable flag of <bes unmanagedasset field>: boolean	filterable flag	filterable flags	filterable flag	0	boolean	bes unmanagedasset field	
e0	filters of <bes domain>: bes filter	filter	filters	filters	1	bes filter	bes domain	
1f	fin wait one of <tcp state>: boolean
1f	fin wait two of <tcp state>: boolean
ff	final part <time interval> of <time range>: time range	final part	final parts	final part	0	time range	time range	time interval
1f	find adapters <string> of <network>: network adapter
1f	find files <string> of <folder>: file
1f	find folders <string> of <folder>: folder
2	find items <string> of <folder>: filesystem object
ff	finite of <floating point>: boolean	finite	finites	finite	0	boolean	floating point	
ff	fips mode failure message of <cryptography>: string	fips mode failure message	fips mode failure messages	fips mode failure message	0	string	cryptography	
ff	fips mode of <cryptography>: boolean	fips mode	fips modes	fips mode	0	boolean	cryptography	
ff	fips mode of <license>: boolean	fips mode	fips modes	fips mode	0	boolean	license	
12	firewall action <integer>: firewall action
10	firewall enabled of <firewall profile>: boolean
10	firewall local policy modify state <integer>: firewall local policy modify state
10	firewall of <connection>: internet connection firewall
10	firewall profile type <integer>: firewall profile type
10	firewall scope <integer>: firewall scope
10	firewall service type <integer>: firewall service type
12	firewall: firewall
2	firewire plane of <registryroot>: registrynode
ff	first <day of week> of <month and year>: date	first	firsts	first	0	date	month and year	day of week
ff	first <integer> of <binary_string>: binary_substring	first	firsts	first	0	binary_substring	binary_string	integer
ff	first <integer> of <string>: substring	first	firsts	first	0	substring	string	integer
ff	first <string> of <string>: substring	first	firsts	first	0	substring	string	string
1f	first active count of <action>: integer
e0	first became relevant of <bes fixlet result>: time	first became relevant	first became relevants	first became relevant	0	time	bes fixlet result	
bd	first child of <xml dom node>: xml dom node
ff	first friday of <month and year>: date	first friday	first fridays	first friday	0	date	month and year	
10	first interface scheduled tasks: scheduled task
1a	first line of <file>: file line
1a	first lines <integer> of <file>: file line
ff	first matches <regular expression> of <string>: regular expression match	first match	first matches	first matches	1	regular expression match	string	regular expression
ff	first monday of <month and year>: date	first monday	first mondays	first monday	0	date	month and year	
10	first raw version block of <file>: file version block
1a	first rawline of <file>: file line
1a	first rawlines <integer> of <file>: file line
ff	first saturday of <month and year>: date	first saturday	first saturdays	first saturday	0	date	month and year	
1f	first start time of <application usage summary instance>: time
1f	first start time of <application usage summary>: time
ff	first sunday of <month and year>: date	first sunday	first sundays	first sunday	0	date	month and year	
ff	first thursday of <month and year>: date	first thursday	first thursdays	first thursday	0	date	month and year	
ff	first tuesday of <month and year>: date	first tuesday	first tuesdays	first tuesday	0	date	month and year	
ff	first wednesday of <month and year>: date	first wednesday	first wednesdays	first wednesday	0	date	month and year	
e0	fixlet <integer> of <bes site>: bes fixlet	fixlet	fixlets	fixlet	0	bes fixlet	bes site	integer
e0	fixlet flag of <bes filter>: boolean	fixlet flag	fixlet flags	fixlet flag	0	boolean	bes filter	
e0	fixlet flag of <bes fixlet>: boolean	fixlet flag	fixlet flags	fixlet flag	0	boolean	bes fixlet	
e0	fixlet of <bes fixlet result>: bes fixlet	fixlet	fixlets	fixlet	0	bes fixlet	bes fixlet result	
e0	fixlet set of <bes filter>: bes fixlet set	fixlet set	fixlet sets	fixlet set	0	bes fixlet set	bes filter	
e0	fixlet set of <bes site>: bes fixlet set	fixlet set	fixlet sets	fixlet set	0	bes fixlet set	bes site	
e0	fixlets of <bes site>: bes fixlet	fixlet	fixlets	fixlets	1	bes fixlet	bes site	
1f	fixlets of <site>: fixlet
d	flag list of <processor>: string
d	flag of <Xinetd Service>: string
2	flag of <volume>: integer
1f	flags of <dmi bios_language_information>: integer
2	flags string of <route>: string
1f	float of <sqlite column type>: boolean
ff	floating point <floating point>: floating point	floating point	floating points	floating point	0	floating point		floating point
ff	floating point <string>: floating point	floating point	floating points	floating point	0	floating point		string
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
ff	following binary_string of <binary position>: binary_substring	following binary_string	following binary_strings	following binary_string	0	binary_substring	binary position	
ff	following binary_string of <binary_substring>: binary_substring	following binary_string	following binary_strings	following binary_string	0	binary_substring	binary_substring	
ff	following text of <string position>: substring	following text	following texts	following text	0	substring	string position	
ff	following text of <substring>: substring	following text	following texts	following text	0	substring	substring	
2	fonts folder of <domain>: folder
2	fonts folder: folder
10	force logoff interval of <security database>: time interval
d	foreground of <grub color pair>: grub color
1f	form_factor of <dmi memory_device>: integer
ff	format <string>: format	format	formats	format	0	format		string
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
ff	friday: day of week	friday	fridays	friday	0	day of week		
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
e0	fxf character set of <bes server>: string	fxf character set	fxf character sets	fxf character set	0	string	bes server	
1f	fxf character set of <client>: string
ff	fxf encoding concatenations <string> of <string>: string	fxf encoding concatenation	fxf encoding concatenations	fxf encoding concatenations	1	string	string	string
ff	fxf encoding concatenations of <string>: string	fxf encoding concatenation	fxf encoding concatenations	fxf encoding concatenations	1	string	string	
1f	gateway address <integer> of <selected server>: ipv4or6 address
1f	gateway addresses of <selected server>: ipv4or6 address
f	gateway flag of <route>: boolean
10	gateway lists of <network adapter>: network address list
10	gateway of <network adapter>: ipv4 address
f	gateway of <route>: ipv4or6 address
2	gateway string of <route>: string
2	gateway type of <route>: string
1f	gather duration of <evaluation cycle>: time interval
40	gather flag of <bes peer download>: boolean	gather flag	gather flags	gather flag	0	boolean	bes peer download	
1f	gather percent of <evaluation cycle>: floating point
1f	gather schedule authority of <site>: string
1f	gather schedule time interval of <site>: time interval
ff	gather url of <license>: string	gather url	gather urls	gather url	0	string	license	
10	gdi object count of <process>: integer
10	generic all permission of <access control entry>: boolean
10	generic execute permission of <access control entry>: boolean
40	generic ldap of <bes idp directory>: boolean	generic ldap	generic ldaps	generic ldap	0	boolean	bes idp directory	
10	generic read permission of <access control entry>: boolean
10	generic write permission of <access control entry>: boolean
e0	geometric mean of <statistical bin>: floating point	geometric mean	geometric means	geometric mean	0	floating point	statistical bin	
2	gestalt <string>: integer
d	gfxmenu of <grub config file>: grub file location
ff	ghz: hertz	ghz	ghzs	ghz	0	hertz		
d	gid of <filesystem object>: integer
d	gid of <symlink>: integer
40	global catalog of <bes idp directory>: boolean	global catalog	global catalogs	global catalog	0	boolean	bes idp directory	
e0	global catalog of <bes ldap directory>: boolean	global catalog	global catalogs	global catalog	0	boolean	bes ldap directory	
2	global dictionary of <bundle>: dictionary
2	global state of <firewall>: string
e0	globally allowed flag of <bes webui app>: boolean	globally allowed flag	globally allowed flags	globally allowed flag	0	boolean	bes webui app	
10	globally open ports of <firewall profile>: firewall open port
10	globally open ports of <firewall service>: firewall open port
e0	globally readable flag of <bes site>: boolean	globally readable flag	globally readable flags	globally readable flag	0	boolean	bes site	
e0	globally visible flag of <bes fixlet>: boolean	globally visible flag	globally visible flags	globally visible flag	0	boolean	bes fixlet	
10	gp override firewall local policy modify state: firewall local policy modify state
10	grant type of <access control entry>: boolean
ff	greatest hz: hertz	greatest hz	greatest hzs	greatest hz	0	hertz		
ff	greatest integer: integer	greatest integer	greatest integers	greatest integer	0	integer		
5a	greatest large integer: large integer	greatest large integer	greatest large integers	greatest large integer	0	large integer		
ff	greatest time interval: time interval	greatest time interval	greatest time intervals	greatest time interval	0	time interval		
5a	greatest uinteger: uinteger	greatest uinteger	greatest uintegers	greatest uinteger	0	uinteger		
1f	group <integer> of <site>: site group
12	group <string> of <active directory local computer>: active directory group
12	group <string> of <active directory local user>: active directory group
d	group execute of <filesystem object>: boolean
40	group filter of <bes idp directory>: string	group filter	group filters	group filter	0	string	bes idp directory	
e0	group filter of <bes ldap directory>: string	group filter	group filters	group filter	0	string	bes ldap directory	
e0	group flag of <bes filter>: boolean	group flag	group flags	group flag	0	boolean	bes filter	
e0	group flag of <bes fixlet>: boolean	group flag	group flags	group flag	0	boolean	bes fixlet	
10	group id of <task principal>: string
1f	group leader of <action>: boolean
10	group logon of <task principal>: boolean
d	group mask of <filesystem object>: integer
d	group mask of <mode>: mode_mask
e0	group member flag of <bes action>: boolean	group member flag	group member flags	group member flag	0	boolean	bes action	
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
ff	h1 <string> of <html>: html	h1	h1s	h1	0	html	html	string
ff	h1 <string> of <string>: html	h1	h1s	h1	0	html	string	string
ff	h1 of <html>: html	h1	h1s	h1	0	html	html	
ff	h1 of <string>: html	h1	h1s	h1	0	html	string	
ff	h2 <string> of <html>: html	h2	h2s	h2	0	html	html	string
ff	h2 <string> of <string>: html	h2	h2s	h2	0	html	string	string
ff	h2 of <html>: html	h2	h2s	h2	0	html	html	
ff	h2 of <string>: html	h2	h2s	h2	0	html	string	
ff	h3 <string> of <html>: html	h3	h3s	h3	0	html	html	string
ff	h3 <string> of <string>: html	h3	h3s	h3	0	html	string	string
ff	h3 of <html>: html	h3	h3s	h3	0	html	html	
ff	h3 of <string>: html	h3	h3s	h3	0	html	string	
ff	h4 <string> of <html>: html	h4	h4s	h4	0	html	html	string
ff	h4 <string> of <string>: html	h4	h4s	h4	0	html	string	string
ff	h4 of <html>: html	h4	h4s	h4	0	html	html	
ff	h4 of <string>: html	h4	h4s	h4	0	html	string	
ff	h5 <string> of <html>: html	h5	h5s	h5	0	html	html	string
ff	h5 <string> of <string>: html	h5	h5s	h5	0	html	string	string
ff	h5 of <html>: html	h5	h5s	h5	0	html	html	
ff	h5 of <string>: html	h5	h5s	h5	0	html	string	
ff	h6 <string> of <html>: html	h6	h6s	h6	0	html	html	string
ff	h6 <string> of <string>: html	h6	h6s	h6	0	html	string	string
ff	h6 of <html>: html	h6	h6s	h6	0	html	html	
ff	h6 of <string>: html	h6	h6s	h6	0	html	string	
10	handle count of <process>: integer
10	hardware ids of <active device>: string
1f	hardware: hardware
1f	hardware_security <integer> of <dmi>: dmi hardware_security
1f	hardware_security_settings of <dmi hardware_security>: integer
1f	hardware_securitys of <dmi>: dmi hardware_security
10	has blank sa password of <local mssql database>: boolean
d	has extended acl of <filesystem object>: boolean
40	hash of <bes peer download>: string	hash	hashes	hash	0	string	bes peer download	
ff	head <string> of <html>: html	head	heads	head	0	html	html	string
ff	head <string> of <string>: html	head	heads	head	0	html	string	string
ff	head of <html>: html	head	heads	head	0	html	html	
ff	head of <string>: html	head	heads	head	0	html	string	
10	header fields of <email task action>: task named value pair
1f	headers <string> of <action>: fixlet_header
1f	headers <string> of <fixlet>: fixlet_header
1f	headers of <action>: fixlet_header
1f	headers of <fixlet>: fixlet_header
1f	height of <dmi system_enclosure_or_chassis>: integer
2	help folder of <domain>: folder
2	help folder: folder
ff	hexadecet <integer> of <ipv4or6 address>: integer	hexadecet	hexadecets	hexadecet	0	integer	ipv4or6 address	integer
ff	hexadecet <integer> of <ipv6 address>: integer	hexadecet	hexadecets	hexadecet	0	integer	ipv6 address	integer
ff	hexadecimal integer <string>: integer	hexadecimal integer	hexadecimal integers	hexadecimal integer	0	integer		string
5a	hexadecimal large integer <string>: large integer	hexadecimal large integer	hexadecimal large integers	hexadecimal large integer	0	large integer		string
1f	hexadecimal of <smbios value>: string
ff	hexadecimal string <string>: string	hexadecimal string	hexadecimal strings	hexadecimal string	0	string		string
5a	hexadecimal uinteger <string>: uinteger	hexadecimal uinteger	hexadecimal uintegers	hexadecimal uinteger	0	uinteger		string
1f	hexadecimals <string> of <smbios structure>: string
2	hfs file <string> of <encoding>: file
2	hfs file <string>: file
2	hfs folder <string> of <encoding>: folder
2	hfs folder <string>: folder
2	hfs item <string>: filesystem object
2	hfs path of <filesystem object>: string
2	hfs relative item <string> of <folder>: filesystem object
e0	hidden bes action set: bes action set	hidden bes action set	hidden bes action sets	hidden bes action set	0	bes action set		
e0	hidden bes actions: bes action	hidden bes action	hidden bes actions	hidden bes actions	1	bes action		
e0	hidden flag of <bes action>: boolean	hidden flag	hidden flags	hidden flag	0	boolean	bes action	
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
40	host of <bes idp directory server>: string	host	hosts	host	0	string	bes idp directory server	
e0	host of <bes ldap directory server>: string	host	hosts	host	0	string	bes ldap directory server	
e0	hostname of <bes computer>: string	hostname	hostnames	hostname	0	string	bes computer	
1f	hostname: string
ff	hour: time interval	hour	hours	hour	0	time interval		
ff	hour_of_day of <time of day with time zone>: integer	hour_of_day	hours_of_day	hour_of_day	0	integer	time of day with time zone	
ff	hour_of_day of <time of day>: integer	hour_of_day	hours_of_day	hour_of_day	0	integer	time of day	
ff	hr <string>: html	hr	hrs	hr	0	html		string
ff	hr: html	hr	hrs	hr	0	html		
ff	html <string> of <html>: html	html	htmls	html	0	html	html	string
ff	html <string> of <string>: html	html	htmls	html	0	html	string	string
ff	html <string>: html	html	htmls	html	0	html		string
ff	html concatenations <string> of <html>: html	html concatenation	html concatenations	html concatenations	1	html	html	string
ff	html concatenations of <html>: html	html concatenation	html concatenations	html concatenations	1	html	html	
ff	html of <html>: html	html	htmls	html	0	html	html	
ff	html of <string>: html	html	htmls	html	0	html	string	
ff	html tag <( string, html )>: html	html tag	html tags	html tag	0	html		( string, html )
ff	html tag <( string, html attribute list )>: html	html tag	html tags	html tag	0	html		( string, html attribute list )
ff	html tag <( string, html attribute list, html )>: html	html tag	html tags	html tag	0	html		( string, html attribute list, html )
ff	html tag <( string, html attribute list, string )>: html	html tag	html tags	html tag	0	html		( string, html attribute list, string )
ff	html tag <( string, string )>: html	html tag	html tags	html tag	0	html		( string, string )
ff	html tag <string> of <html>: html	html tag	html tags	html tag	0	html	html	string
ff	html tag <string> of <string>: html	html tag	html tags	html tag	0	html	string	string
10	hyperthreading capable: boolean
10	hyperthreading enabled: boolean
1f	hypervisor of <operating system>: string
ff	hz: hertz	hz	hzs	hz	0	hertz		
1f	i2c_slave_address of <dmi ipmi_device_information>: integer
10	ia64 of <operating system>: boolean
12	ibss of <wifi network>: boolean
10	icmp settings of <firewall profile>: firewall icmp settings
10	icmp types_and_codes string of <firewall rule>: string
10	icon index of <file shortcut>: integer
10	icon pathname of <file shortcut>: string
d	id of <Xinetd Service>: string
1f	id of <action>: integer
e0	id of <bes action>: integer	id	ids	id	0	integer	bes action	
e0	id of <bes activation>: integer	id	ids	id	0	integer	bes activation	
e0	id of <bes baseline component>: integer	id	ids	id	0	integer	bes baseline component	
e0	id of <bes computer group>: integer	id	ids	id	0	integer	bes computer group	
e0	id of <bes computer>: integer	id	ids	id	0	integer	bes computer	
e0	id of <bes domain>: string	id	ids	id	0	string	bes domain	
e0	id of <bes filter>: integer	id	ids	id	0	integer	bes filter	
e0	id of <bes fixlet>: integer	id	ids	id	0	integer	bes fixlet	
40	id of <bes idp directory>: integer	id	ids	id	0	integer	bes idp directory	
e0	id of <bes ldap directory>: integer	id	ids	id	0	integer	bes ldap directory	
e0	id of <bes property>: ( integer, integer, integer )	id	ids	id	0	( integer, integer, integer )	bes property	
40	id of <bes role>: integer	id	ids	id	0	integer	bes role	
e0	id of <bes site file>: integer	id	ids	id	0	integer	bes site file	
e0	id of <bes site>: integer	id	ids	id	0	integer	bes site	
40	id of <bes tag>: uinteger	id	ids	id	0	uinteger	bes tag	
e0	id of <bes unmanagedasset>: integer	id	ids	id	0	integer	bes unmanagedasset	
e0	id of <bes user>: integer	id	ids	id	0	integer	bes user	
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
40	idp directory of <bes user>: bes idp directory	idp directory	idp directories	idp directory	0	bes idp directory	bes user	
2	ifref flag of <route>: boolean
2	ifscope flag of <route>: boolean
10	ignore new instance of <task settings>: boolean
1f	image file of <process>: file
1f	image path of <application usage summary instance>: string
1d	image path of <service>: string
1f	in agent context: boolean
e0	in console context: boolean	in console context	in console contexts	in console context	0	boolean		
40	in explorer context: boolean	in explorer context	in explorer contexts	in explorer context	0	boolean		
1f	in plugin portal context: boolean
1f	in proxy agent context: boolean
e0	in web reports context: boolean	in web reports context	in web reports contexts	in web reports context	0	boolean		
1f	inactive <integer> of <dmi>: dmi inactive
1f	inactives of <dmi>: dmi inactive
10	inbound blocked firewall local policy modify state: firewall local policy modify state
10	inbound connections allowed of <firewall profile>: boolean
10	inbound of <firewall rule>: boolean
e0	include in relevance flag of <bes baseline component>: boolean	include in relevance flag	include in relevance flags	include in relevance flag	0	boolean	bes baseline component	
d	index of <grub image choice>: integer
d	index of <processor>: integer
ff	index of <tuple item>: integer	index	indexes	index	0	integer	tuple item	
ff	index type of <property>: type	index type	index types	index type	0	type	property	
1f	indices of <sqlite table>: string
ff	inexact of <floating point>: boolean	inexact	inexacts	inexact	0	boolean	floating point	
ff	infinite of <floating point>: boolean	infinite	infinites	infinite	0	boolean	floating point	
1f	info of <client>: string
2	info of <component>: string
10	information event log event type: event log event type
10	inherit attribute of <metabase value>: boolean
10	inherit only of <access control entry>: boolean
10	inheritance of <access control entry>: integer
10	inherited of <access control entry>: boolean
2	init date of <volume>: time
ff	initial part <time interval> of <time range>: time range	initial part	initial parts	initial part	0	time range	time range	time interval
d	initrd of <grub bootable image>: grub file location
1f	input_current_probe_handle of <dmi system_power_supply>: integer
1f	input_voltage_probe_handle of <dmi system_power_supply>: integer
ff	ins <string> of <html>: html	ins	inss	ins	0	html	html	string
ff	ins <string> of <string>: html	ins	inss	ins	0	html	string	string
ff	ins of <html>: html	ins	inss	ins	0	html	html	
ff	ins of <string>: html	ins	inss	ins	0	html	string	
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
ff	integer <integer>: integer	integer	integers	integer	0	integer		integer
2	integer <string> of <dictionary>: integer
2	integer <string> of <preference>: integer
ff	integer <string>: integer	integer	integers	integer	0	integer		string
ff	integer ceiling of <floating point>: integer	integer ceiling	integer ceilings	integer ceiling	0	integer	floating point	
ff	integer floor of <floating point>: integer	integer floor	integer floors	integer floor	0	integer	floating point	
2	integer of <osxvalue>: integer
1f	integer of <sqlite column type>: boolean
10	integer value <integer> of <wmi select>: integer
1f	integer values <string> of <smbios structure>: smbios value
10	integer values of <wmi select>: integer
1f	integers <string> of <smbios structure>: integer
ff	integers in <( integer, integer )>: integer	integer in	integers in	integers in	1	integer		( integer, integer )
ff	integers in <( integer, integer, integer )>: integer	integer in	integers in	integers in	1	integer		( integer, integer, integer )
ff	integers to <integer>: integer	integer to	integers to	integers to	1	integer		integer
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
e0	intersections of <bes action set>: bes action set	intersection	intersections	intersections	1	bes action set	bes action set	
e0	intersections of <bes computer group set>: bes computer group set	intersection	intersections	intersections	1	bes computer group set	bes computer group set	
e0	intersections of <bes computer set>: bes computer set	intersection	intersections	intersections	1	bes computer set	bes computer set	
e0	intersections of <bes domain set>: bes domain set	intersection	intersections	intersections	1	bes domain set	bes domain set	
e0	intersections of <bes filter set>: bes filter set	intersection	intersections	intersections	1	bes filter set	bes filter set	
e0	intersections of <bes fixlet set>: bes fixlet set	intersection	intersections	intersections	1	bes fixlet set	bes fixlet set	
40	intersections of <bes idp directory set>: bes idp directory set	intersection	intersections	intersections	1	bes idp directory set	bes idp directory set	
e0	intersections of <bes ldap directory set>: bes ldap directory set	intersection	intersections	intersections	1	bes ldap directory set	bes ldap directory set	
e0	intersections of <bes property set>: bes property set	intersection	intersections	intersections	1	bes property set	bes property set	
e0	intersections of <bes role set>: bes role set	intersection	intersections	intersections	1	bes role set	bes role set	
e0	intersections of <bes site file set>: bes site file set	intersection	intersections	intersections	1	bes site file set	bes site file set	
e0	intersections of <bes site set>: bes site set	intersection	intersections	intersections	1	bes site set	bes site set	
e0	intersections of <bes unmanagedasset set>: bes unmanagedasset set	intersection	intersections	intersections	1	bes unmanagedasset set	bes unmanagedasset set	
e0	intersections of <bes user set>: bes user set	intersection	intersections	intersections	1	bes user set	bes user set	
e0	intersections of <bes webui app set>: bes webui app set	intersection	intersections	intersections	1	bes webui app set	bes webui app set	
e0	intersections of <bes wizard set>: bes wizard set	intersection	intersections	intersections	1	bes wizard set	bes wizard set	
ff	intersections of <integer set>: integer set	intersection	intersections	intersections	1	integer set	integer set	
ff	intersections of <string set>: string set	intersection	intersections	intersections	1	string set	string set	
10	interval of <task repetition pattern>: time interval
ff	invalid after of <x509 certificate>: time	invalid after	invalid afters	invalid after	0	time	x509 certificate	
ff	invalid before of <x509 certificate>: time	invalid before	invalid befores	invalid before	0	time	x509 certificate	
ff	invalid of <floating point>: boolean	invalid	invalids	invalid	0	boolean	floating point	
12	invalid state: power state
10	io other count of <process>: integer
10	io other size of <process>: integer
10	io read count of <process>: integer
10	io read size of <process>: integer
10	io write count of <process>: integer
10	io write size of <process>: integer
2	iokit registry: registryroot
1f	ip address of <selected server>: ipv4or6 address
e0	ip addresses of <bes computer>: ipv4or6 address	ip address	ip addresses	ip addresses	1	ipv4or6 address	bes computer	
2	ip family of <route>: string
1f	ip interface <integer> of <network>: network ip interface
2	ip interfaces of <network adapter>: network ip interface
1f	ip interfaces of <network>: network ip interface
ff	ip version <integer>: ip version	ip version	ip versions	ip version	0	ip version		integer
10	ip version of <firewall authorized application>: ip version
10	ip version of <firewall open port>: ip version
10	ip version of <firewall service>: ip version
ff	ip version of <ipv4or6 address>: ip version	ip version	ip versions	ip version	0	ip version	ipv4or6 address	
1f	ipmi_device_information <integer> of <dmi>: dmi ipmi_device_information
1f	ipmi_device_informations of <dmi>: dmi ipmi_device_information
1f	ipmi_specification_revision of <dmi ipmi_device_information>: integer
ff	ipv4 address <string>: ipv4 address	ipv4 address	ipv4 addresses	ipv4 address	0	ipv4 address		string
10	ipv4 interface <integer> of <network adapter>: network adapter interface
10	ipv4 interface <integer> of <network>: network adapter interface
1f	ipv4 interfaces of <network adapter>: network adapter interface
1f	ipv4 interfaces of <network>: network adapter interface
ff	ipv4 part of <ipv4or6 address>: ipv4 address	ipv4 part	ipv4 parts	ipv4 part	0	ipv4 address	ipv4or6 address	
ff	ipv4 part of <ipv6 address>: ipv4 address	ipv4 part	ipv4 parts	ipv4 part	0	ipv4 address	ipv6 address	
f	ipv4 routing table: routing table
ff	ipv4: ip version	ipv4	ipv4s	ipv4	0	ip version		
ff	ipv4or6 address <string>: ipv4or6 address	ipv4or6 address	ipv4or6 addresses	ipv4or6 address	0	ipv4or6 address		string
10	ipv4or6 dns servers of <network adapter>: ipv4or6 address
10	ipv4or6 interface <integer> of <network adapter>: network adapter interface
10	ipv4or6 interface <integer> of <network>: network adapter interface
1f	ipv4or6 interfaces of <network adapter>: network adapter interface
1f	ipv4or6 interfaces of <network>: network adapter interface
ff	ipv6 address <string>: ipv6 address	ipv6 address	ipv6 addresses	ipv6 address	0	ipv6 address		string
10	ipv6 addresses of <network adapter>: ipv6 address
10	ipv6 dns servers of <network adapter>: ipv6 address
10	ipv6 interface <integer> of <network adapter>: network adapter interface
10	ipv6 interface <integer> of <network>: network adapter interface
1f	ipv6 interfaces of <network adapter>: network adapter interface
1f	ipv6 interfaces of <network>: network adapter interface
2	ipv6 routing table: routing table
ff	ipv6: ip version	ipv6	ipv6s	ipv6	0	ip version		
d	irtt of <route>: integer
2	isochronous of <usb>: boolean
2	iss download folder of <domain>: folder
2	iss download folder: folder
e0	issued action set of <bes user>: bes action set	issued action set	issued action sets	issued action set	0	bes action set	bes user	
e0	issued actions of <bes user>: bes action	issued action	issued actions	issued actions	1	bes action	bes user	
e0	issued computer group set of <bes user>: bes computer group set	issued computer group set	issued computer group sets	issued computer group set	0	bes computer group set	bes user	
e0	issued computer groups of <bes user>: bes computer group	issued computer group	issued computer groups	issued computer groups	1	bes computer group	bes user	
e0	issued fixlet set of <bes user>: bes fixlet set	issued fixlet set	issued fixlet sets	issued fixlet set	0	bes fixlet set	bes user	
e0	issued fixlets of <bes user>: bes fixlet	issued fixlet	issued fixlets	issued fixlets	1	bes fixlet	bes user	
e0	issuer of <bes action>: bes user	issuer	issuers	issuer	0	bes user	bes action	
e0	issuer of <bes activation>: bes user	issuer	issuers	issuer	0	bes user	bes activation	
e0	issuer of <bes computer group>: bes user	issuer	issuers	issuer	0	bes user	bes computer group	
e0	issuer of <bes fixlet>: bes user	issuer	issuers	issuer	0	bes user	bes fixlet	
ff	issuer of <x509 certificate>: string	issuer	issuers	issuer	0	string	x509 certificate	
ff	italic <string> of <html>: html	italic	italics	italic	0	html	html	string
ff	italic <string> of <string>: html	italic	italics	italic	0	html	string	string
ff	italic of <html>: html	italic	italics	italic	0	html	html	
ff	italic of <string>: html	italic	italics	italic	0	html	string	
2	item <string> of <folder>: filesystem object
2	item <string>: filesystem object
1f	item_handle of <dmi group_associations>: integer
1f	item_type of <dmi group_associations>: integer
2	items ending in <string> of <folder>: filesystem object
2	items of <folder>: filesystem object
ff	january <integer> of <integer>: date	january	januarys	january	0	date	integer	integer
ff	january <integer>: day of year	january	januarys	january	0	day of year		integer
ff	january of <integer>: month and year	january	januarys	january	0	month and year	integer	
ff	january: month	january	januarys	january	0	month		
e0	javascript arrays <string> of <boolean>: html	javascript array	javascript arrays	javascript arrays	1	html	boolean	string
e0	javascript arrays <string> of <integer>: html	javascript array	javascript arrays	javascript arrays	1	html	integer	string
e0	javascript arrays <string> of <statistical bin>: html	javascript array	javascript arrays	javascript arrays	1	html	statistical bin	string
e0	javascript arrays <string> of <string>: html	javascript array	javascript arrays	javascript arrays	1	html	string	string
e0	join by intersection flag of <bes filter>: boolean	join by intersection flag	join by intersection flags	join by intersection flag	0	boolean	bes filter	
1f	json of <file>: json value
1f	json of <instance data>: json value
ff	json of <string>: json value	json	jsons	json	0	json value	string	
ff	july <integer> of <integer>: date	july	julys	july	0	date	integer	integer
ff	july <integer>: day of year	july	julys	july	0	day of year		integer
ff	july of <integer>: month and year	july	julys	july	0	month and year	integer	
ff	july: month	july	julys	july	0	month		
ff	june <integer> of <integer>: date	june	junes	june	0	date	integer	integer
ff	june <integer>: day of year	june	junes	june	0	day of year		integer
ff	june of <integer>: month and year	june	junes	june	0	month and year	integer	
ff	june: month	june	junes	june	0	month		
ff	kbd <string> of <html>: html	kbd	kbds	kbd	0	html	html	string
ff	kbd <string> of <string>: html	kbd	kbds	kbd	0	html	string	string
ff	kbd of <html>: html	kbd	kbds	kbd	0	html	html	
ff	kbd of <string>: html	kbd	kbds	kbd	0	html	string	
e0	keep statistics flag of <bes property>: boolean	keep statistics flag	keep statistics flags	keep statistics flag	0	boolean	bes property	
2	kernel extensions folder of <domain>: folder
2	kernel extensions folder: folder
d	kernel of <grub bootable image>: grub kernel
10	kernel time of <process>: time interval
1f	key <string> of <file section>: string
1f	key <string> of <file>: string
ff	key <string> of <json value>: json key	key	keys	key	0	json key	json value	string
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
ff	keys of <json value>: json key	key	keys	keys	1	json key	json value	
10	keys of <metabase key>: metabase key
10	keys of <metabase>: metabase key
14	keys of <plugin store>: plugin store key
10	keys of <registry key>: registry key
ff	khz: hertz	khz	khzs	khz	0	hertz		
e0	kurtosis of <statistical bin>: floating point	kurtosis	kurtoses	kurtosis	0	floating point	statistical bin	
1f	l1_cache_handle of <dmi processor_information>: integer
1f	l2_cache_handle of <dmi processor_information>: integer
1f	l3_cache_handle of <dmi processor_information>: integer
10	language of <file version block>: string
5a	large integer <integer>: large integer	large integer	large integers	large integer	0	large integer		integer
5a	large integer <string>: large integer	large integer	large integers	large integer	0	large integer		string
ff	last <integer> of <binary_string>: binary_substring	last	lasts	last	0	binary_substring	binary_string	integer
ff	last <integer> of <string>: substring	last	lasts	last	0	substring	string	integer
ff	last <string> of <string>: substring	last	lasts	last	0	substring	string	string
1f	last ack of <tcp state>: boolean
1f	last active line number of <action>: integer
1f	last active time of <action>: time
e0	last became nonrelevant of <bes fixlet result>: time	last became nonrelevant	last became nonrelevants	last became nonrelevant	0	time	bes fixlet result	
e0	last became relevant of <bes fixlet result>: time	last became relevant	last became relevants	last became relevant	0	time	bes fixlet result	
1f	last change time of <action>: time
bd	last child of <xml dom node>: xml dom node
1f	last command time of <client>: time
1f	last gather time of <site>: time
1a	last line of <file>: file line
1a	last lines <integer> of <file>: file line
e0	last login time of <bes user>: time	last login time	last login times	last login time	0	time	bes user	
10	last logoff of <user>: time
10	last logon of <user>: time
12	last monitor interval in <power state> of <power history>: monitor power interval
12	last monitor interval in monitor off state of <power history>: monitor power interval
12	last monitor interval in monitor on state of <power history>: monitor power interval
1a	last rawline of <file>: file line
1a	last rawlines <integer> of <file>: file line
e0	last refresh time of <bes computer group>: time	last refresh time	last refresh times	last refresh time	0	time	bes computer group	
1f	last relay select time: time
e0	last report time of <bes computer>: time	last report time	last report times	last report time	0	time	bes computer	
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
e0	ldap directory of <bes user>: bes ldap directory	ldap directory	ldap directories	ldap directory	0	bes ldap directory	bes user	
ff	leap of <year>: boolean	leap	leaps	leap	0	boolean	year	
10	lease expires of <network adapter>: time
10	lease obtained of <network adapter>: time
ff	least hz: hertz	least hz	least hzs	least hz	0	hertz		
ff	least integer: integer	least integer	least integers	least integer	0	integer		
5a	least large integer: large integer	least large integer	least large integers	least large integer	0	large integer		
ff	least significant one bit of <bit set>: integer	least significant one bit	least significant one bits	least significant one bit	0	integer	bit set	
ff	least time interval: time interval	least time interval	least time intervals	least time interval	0	time interval		
5a	least uinteger: uinteger	least uinteger	least uintegers	least uinteger	0	uinteger		
ff	left operand type of <binary operator>: type	left operand type	left operand types	left operand type	0	type	binary operator	
ff	left shift <integer> of <bit set>: bit set	left shift	left shifts	left shift	0	bit set	bit set	integer
ff	legacy of <bes product>: boolean	legacy	legacies	legacy	0	boolean	bes product	
ff	length of <binary_string>: integer	length	lengths	length	0	integer	binary_string	
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
ff	length of <month and year>: time interval	length	lengths	length	0	time interval	month and year	
2	length of <resfork>: integer
ff	length of <rope>: integer	length	lengths	length	0	integer	rope	
1f	length of <smbios structure>: integer
e0	length of <statistical bin>: time interval	length	lengths	length	0	time interval	statistical bin	
ff	length of <string>: integer	length	lengths	length	0	integer	string	
ff	length of <time range>: time interval	length	lengths	length	0	time interval	time range	
ff	length of <year>: time interval	length	lengths	length	0	time interval	year	
ff	less significance <integer> of <floating point>: floating point	less significance	less significances	less significance	0	floating point	floating point	integer
ff	li <string> of <html>: html	li	lis	li	0	html	html	string
ff	li <string> of <string>: html	li	lis	li	0	html	string	string
ff	li of <html>: html	li	lis	li	0	html	html	
ff	li of <string>: html	li	lis	li	0	html	string	
e0	license type of <bes computer>: string	license type	license types	license type	0	string	bes computer	
1f	line <integer> of <file>: file line
e0	line number of <bes action result>: integer	line number	line numbers	line number	0	integer	bes action result	
1f	line number of <file line>: integer
e0	linear fit of <statistical bin>: linear projection	linear fit	linear fits	linear fit	0	linear projection	statistical bin	
1f	lines containing <string> of <file>: file line
1f	lines of <file>: file line
1f	lines starting with <string> of <file>: file line
e0	link <html> of <bes action>: html	link	links	link	0	html	bes action	html
e0	link <html> of <bes computer>: html	link	links	link	0	html	bes computer	html
e0	link <html> of <bes domain>: html	link	links	link	0	html	bes domain	html
e0	link <html> of <bes fixlet>: html	link	links	link	0	html	bes fixlet	html
e0	link <html> of <bes unmanagedasset>: html	link	links	link	0	html	bes unmanagedasset	html
e0	link <html> of <bes user>: html	link	links	link	0	html	bes user	html
e0	link <html> of <bes wizard>: html	link	links	link	0	html	bes wizard	html
e0	link <string> of <bes action>: html	link	links	link	0	html	bes action	string
e0	link <string> of <bes computer>: html	link	links	link	0	html	bes computer	string
e0	link <string> of <bes domain>: html	link	links	link	0	html	bes domain	string
e0	link <string> of <bes fixlet>: html	link	links	link	0	html	bes fixlet	string
e0	link <string> of <bes unmanagedasset>: html	link	links	link	0	html	bes unmanagedasset	string
e0	link <string> of <bes user>: html	link	links	link	0	html	bes user	string
e0	link <string> of <bes wizard>: html	link	links	link	0	html	bes wizard	string
ff	link <string> of <html>: html	link	links	link	0	html	html	string
ff	link <string> of <string>: html	link	links	link	0	html	string	string
d	link count of <filesystem object>: integer
d	link count of <symlink>: integer
e0	link href of <bes action>: string	link href	link hrefs	link href	0	string	bes action	
e0	link href of <bes computer>: string	link href	link hrefs	link href	0	string	bes computer	
e0	link href of <bes domain>: string	link href	link hrefs	link href	0	string	bes domain	
e0	link href of <bes fixlet>: string	link href	link hrefs	link href	0	string	bes fixlet	
e0	link href of <bes unmanagedasset>: string	link href	link hrefs	link href	0	string	bes unmanagedasset	
e0	link href of <bes user>: string	link href	link hrefs	link href	0	string	bes user	
e0	link href of <bes wizard>: string	link href	link hrefs	link href	0	string	bes wizard	
2	link interface <integer> of <network>: network link interface
2	link interfaces of <network adapter>: network link interface
2	link interfaces of <network>: network link interface
e0	link of <bes action>: html	link	links	link	0	html	bes action	
e0	link of <bes computer>: html	link	links	link	0	html	bes computer	
e0	link of <bes domain>: html	link	links	link	0	html	bes domain	
e0	link of <bes fixlet>: html	link	links	link	0	html	bes fixlet	
e0	link of <bes unmanagedasset>: html	link	links	link	0	html	bes unmanagedasset	
e0	link of <bes user>: html	link	links	link	0	html	bes user	
e0	link of <bes wizard>: html	link	links	link	0	html	bes wizard	
ff	link of <html>: html	link	links	link	0	html	html	
ff	link of <string>: html	link	links	link	0	html	string	
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
ff	local encoding concatenations <string> of <string>: string	local encoding concatenation	local encoding concatenations	local encoding concatenations	1	string	string	string
ff	local encoding concatenations of <string>: string	local encoding concatenation	local encoding concatenations	local encoding concatenations	1	string	string	
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
ff	local time <string>: time	local time	local times	local time	0	time		string
ff	local time zone: time zone	local time zone	local time zones	local time zone	0	time zone		
12	local user <string> of <active directory server>: active directory local user
12	local user <string>: user
d	local users <string>: user
12	local users of <active directory server>: active directory local user
1f	local users: user
2	locales folder of <domain>: folder
2	locales folder: folder
e0	locally visible flag of <bes fixlet>: boolean	locally visible flag	locally visible flags	locally visible flag	0	boolean	bes fixlet	
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
e0	locked flag of <bes computer>: boolean	locked flag	locked flags	locked flag	0	boolean	bes computer	
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
e0	logarithm kurtosis of <statistical bin>: floating point	logarithm kurtosis	logarithm kurtoses	logarithm kurtosis	0	floating point	statistical bin	
e0	logarithm skewness of <statistical bin>: floating point	logarithm skewness	logarithm skewnesses	logarithm skewness	0	floating point	statistical bin	
e0	logarithm standard deviation of <statistical bin>: floating point	logarithm standard deviation	logarithm standard deviations	logarithm standard deviation	0	floating point	statistical bin	
e0	logarithm variance of <statistical bin>: floating point	logarithm variance	logarithm variances	logarithm variance	0	floating point	statistical bin	
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
40	login user of <bes idp directory>: string	login user	login users	login user	0	string	bes idp directory	
e0	login user of <bes ldap directory>: string	login user	login users	login user	0	string	bes ldap directory	
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
ff	lower bound of <integer range>: integer	lower bound	lower bounds	lower bound	0	integer	integer range	
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
ff	major revision of <version>: integer	major revision	major revisions	major revision	0	integer	version	
1f	major version of <operating system>: integer
2	maker of <component>: string
e0	management extensions of <bes computer>: bes computer	management extension	management extensions	management extensions	1	bes computer	bes computer	
e0	management rights flag of <bes action>: boolean	management rights flag	management rights flags	management rights flag	0	boolean	bes action	
1f	management_device <integer> of <dmi>: dmi management_device
1f	management_device_component <integer> of <dmi>: dmi management_device_component
1f	management_device_components of <dmi>: dmi management_device_component
1f	management_device_handle of <dmi management_device_component>: integer
1f	management_device_threshold_data <integer> of <dmi>: dmi management_device_threshold_data
1f	management_device_threshold_datas of <dmi>: dmi management_device_threshold_data
1f	management_devices of <dmi>: dmi management_device
e0	manual flag of <bes computer group>: boolean	manual flag	manual flags	manual flag	0	boolean	bes computer group	
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
ff	march <integer> of <integer>: date	march	marchs	march	0	date	integer	integer
ff	march <integer>: day of year	march	marchs	march	0	day of year		integer
ff	march of <integer>: month and year	march	marchs	march	0	month and year	integer	
ff	march: month	march	marchs	march	0	month		
f	mask of <route>: ipv4or6 address
e0	master flag of <bes role>: boolean	master flag	master flags	master flag	0	boolean	bes role	
e0	master flag of <bes user>: boolean	master flag	master flags	master flag	0	boolean	bes user	
e0	master site flag of <bes fixlet>: boolean	master site flag	master site flags	master site flag	0	boolean	bes fixlet	
e0	master site flag of <bes site>: boolean	master site flag	master site flags	master site flag	0	boolean	bes site	
1f	masthead of <site>: file
e0	masthead operator name of <bes user>: string	masthead operator name	masthead operator names	masthead operator name	0	string	bes user	
ff	matches <regular expression> of <string>: regular expression match	match	matches	matches	1	regular expression match	string	regular expression
1f	max_power_capacity of <dmi system_power_supply>: integer
1f	max_speed of <dmi processor_information>: integer
ff	maxima of <date>: date	maximum	maxima	maxima	1	date	date	
ff	maxima of <day of month>: day of month	maximum	maxima	maxima	1	day of month	day of month	
ff	maxima of <day of year>: day of year	maximum	maxima	maxima	1	day of year	day of year	
9	maxima of <debian package upstream version>: debian package upstream version
9	maxima of <debian package version epoch>: debian package version epoch
9	maxima of <debian package version revision>: debian package version revision
9	maxima of <debian package version>: debian package version
ff	maxima of <floating point>: floating point	maximum	maxima	maxima	1	floating point	floating point	
ff	maxima of <hertz>: hertz	maximum	maxima	maxima	1	hertz	hertz	
ff	maxima of <integer>: integer	maximum	maxima	maxima	1	integer	integer	
ff	maxima of <ipv4 address>: ipv4 address	maximum	maxima	maxima	1	ipv4 address	ipv4 address	
ff	maxima of <ipv4or6 address>: ipv4or6 address	maximum	maxima	maxima	1	ipv4or6 address	ipv4or6 address	
ff	maxima of <ipv6 address>: ipv6 address	maximum	maxima	maxima	1	ipv6 address	ipv6 address	
5a	maxima of <large integer>: large integer	maximum	maxima	maxima	1	large integer	large integer	
ff	maxima of <month and year>: month and year	maximum	maxima	maxima	1	month and year	month and year	
ff	maxima of <month>: month	maximum	maxima	maxima	1	month	month	
ff	maxima of <number of months>: number of months	maximum	maxima	maxima	1	number of months	number of months	
e2	maxima of <rate>: rate	maximum	maxima	maxima	1	rate	rate	
4	maxima of <rpm package release>: rpm package release
4	maxima of <rpm package version record>: rpm package version record
4	maxima of <rpm package version>: rpm package version
4	maxima of <short rpm package version record>: short rpm package version record
ff	maxima of <site version list>: site version list	maximum	maxima	maxima	1	site version list	site version list	
ff	maxima of <time interval>: time interval	maximum	maxima	maxima	1	time interval	time interval	
ff	maxima of <time of day>: time of day	maximum	maxima	maxima	1	time of day	time of day	
ff	maxima of <time>: time	maximum	maxima	maxima	1	time	time	
5a	maxima of <uinteger>: uinteger	maximum	maxima	maxima	1	uinteger	uinteger	
1f	maxima of <uuid>: uuid
ff	maxima of <version>: version	maximum	maxima	maxima	1	version	version	
ff	maxima of <year>: year	maximum	maxima	maxima	1	year	year	
10	maximum allowed permission of <access control entry>: boolean
1f	maximum duration of <evaluation cycle>: time interval
1f	maximum of <evaluation cycle>: integer
10	maximum password age of <security database>: time interval
ff	maximum seat count of <license>: integer	maximum seat count	maximum seat counts	maximum seat count	0	integer	license	
e0	maximum single computer total of <statistical bin>: floating point	maximum single computer total	maximum single computer totals	maximum single computer total	0	floating point	statistical bin	
10	maximum storage of <user>: integer
10	maximum transmission unit of <network adapter>: integer
e0	maximum value of <statistical bin>: floating point	maximum value	maximum values	maximum value	0	floating point	statistical bin	
1f	maximum_cache_size of <dmi cache_information>: integer
1f	maximum_capacity of <dmi physical_memory_array>: integer
1f	maximum_channel_load of <dmi memory_channel>: integer
1f	maximum_error_in_battery_data of <dmi portable_battery>: integer
1f	maximum_memory_module_size of <dmi memory_controller_information>: integer
1f	maximum_value of <dmi electrical_current_probe>: integer
1f	maximum_value of <dmi temperature_probe>: integer
1f	maximum_value of <dmi voltage_probe>: integer
ff	may <integer> of <integer>: date	may	mays	may	0	date	integer	integer
ff	may <integer>: day of year	may	mays	may	0	day of year		integer
ff	may of <integer>: month and year	may	mays	may	0	month and year	integer	
ff	may: month	may	mays	may	0	month		
1f	md5 of <file>: string
ff	md5 of <string>: string	md5	md5s	md5	0	string	string	
e0	mean computer count of <statistical bin>: floating point	mean computer count	mean computer counts	mean computer count	0	floating point	statistical bin	
e0	mean failing computer count of <statistical bin>: floating point	mean failing computer count	mean failing computer counts	mean failing computer count	0	floating point	statistical bin	
e0	mean logarithm of <statistical bin>: floating point	mean logarithm	mean logarithms	mean logarithm	0	floating point	statistical bin	
e0	mean nonzero value count of <statistical bin>: floating point	mean nonzero value count	mean nonzero value counts	mean nonzero value count	0	floating point	statistical bin	
e0	mean of <statistical bin>: floating point	mean	means	mean	0	floating point	statistical bin	
e0	mean sample interval of <statistical bin>: time interval	mean sample interval	mean sample intervals	mean sample interval	0	time interval	statistical bin	
e0	mean sample rate of <statistical bin>: rate	mean sample rate	mean sample rates	mean sample rate	0	rate	statistical bin	
e0	mean successful computer count of <statistical bin>: floating point	mean successful computer count	mean successful computer counts	mean successful computer count	0	floating point	statistical bin	
e0	mean total of <statistical bin>: floating point	mean total	mean totals	mean total	0	floating point	statistical bin	
e0	mean value count of <statistical bin>: floating point	mean value count	mean value counts	mean value count	0	floating point	statistical bin	
e0	mean zero value count of <statistical bin>: floating point	mean zero value count	mean zero value counts	mean zero value count	0	floating point	statistical bin	
ff	means of <floating point>: floating point	mean	means	means	1	floating point	floating point	
ff	means of <integer>: floating point	mean	means	means	1	floating point	integer	
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
e0	member action set of <bes action>: bes action set	member action set	member action sets	member action set	0	bes action set	bes action	
e0	member actions of <bes action>: bes action	member action	member actions	member actions	1	bes action	bes action	
1f	member of <manual group>: boolean
1f	member of <server based group>: boolean
1f	member of <site group>: boolean
e0	member set of <bes computer group>: bes computer set	member set	member sets	member set	0	bes computer set	bes computer group	
e0	members of <bes computer group>: bes computer	member	members	members	1	bes computer	bes computer group	
10	members of <local group>: local group member
e0	memory usage of <bes property>: integer	memory usage	memory usages	memory usage	0	integer	bes property	
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
e0	menu path of <bes wizard>: string	menu path	menu paths	menu path	0	string	bes wizard	
e0	message action button flag of <bes action>: boolean	message action button flag	message action button flags	message action button flag	0	boolean	bes action	
e0	message allow cancel flag of <bes action>: boolean	message allow cancel flag	message allow cancel flags	message allow cancel flag	0	boolean	bes action	
10	message body of <show message task action>: string
e0	message of <bes fixlet>: html	message	messages	message	0	html	bes fixlet	
e0	message postpone delay of <bes action>: time interval	message postpone delay	message postpone delays	message postpone delay	0	time interval	bes action	
e0	message text of <bes action>: string	message text	message texts	message text	0	string	bes action	
e0	message timeout delay of <bes action>: time interval	message timeout delay	message timeout delays	message timeout delay	0	time interval	bes action	
e0	message title of <bes action>: string	message title	message titles	message title	0	string	bes action	
ff	meta <string> of <html>: html	meta	metas	meta	0	html	html	string
ff	meta <string> of <string>: html	meta	metas	meta	0	html	string	string
ff	meta of <html>: html	meta	metas	meta	0	html	html	
ff	meta of <string>: html	meta	metas	meta	0	html	string	
10	metabase: metabase
10	metric <integer> of <operating system>: integer
d	metric of <route>: integer
ff	mhz: hertz	mhz	mhzs	mhz	0	hertz		
ff	microsecond: time interval	microsecond	microseconds	microsecond	0	time interval		
e0	middle actions of <bes action>: bes action	middle action	middle actions	middle actions	1	bes action	bes action	
ff	midnight: time of day	midnight	midnights	midnight	0	time of day		
ff	millisecond: time interval	millisecond	milliseconds	millisecond	0	time interval		
e0	mime field <string> of <bes action>: string	mime field	mime fields	mime field	0	string	bes action	string
e0	mime field <string> of <bes fixlet>: string	mime field	mime fields	mime field	0	string	bes fixlet	string
e0	mime fields of <bes action>: mime field	mime field	mime fields	mime fields	1	mime field	bes action	
e0	mime fields of <bes fixlet>: mime field	mime field	mime fields	mime fields	1	mime field	bes fixlet	
ff	minima of <date>: date	minimum	minima	minima	1	date	date	
ff	minima of <day of month>: day of month	minimum	minima	minima	1	day of month	day of month	
ff	minima of <day of year>: day of year	minimum	minima	minima	1	day of year	day of year	
9	minima of <debian package upstream version>: debian package upstream version
9	minima of <debian package version epoch>: debian package version epoch
9	minima of <debian package version revision>: debian package version revision
9	minima of <debian package version>: debian package version
ff	minima of <floating point>: floating point	minimum	minima	minima	1	floating point	floating point	
ff	minima of <hertz>: hertz	minimum	minima	minima	1	hertz	hertz	
ff	minima of <integer>: integer	minimum	minima	minima	1	integer	integer	
ff	minima of <ipv4 address>: ipv4 address	minimum	minima	minima	1	ipv4 address	ipv4 address	
ff	minima of <ipv4or6 address>: ipv4or6 address	minimum	minima	minima	1	ipv4or6 address	ipv4or6 address	
ff	minima of <ipv6 address>: ipv6 address	minimum	minima	minima	1	ipv6 address	ipv6 address	
5a	minima of <large integer>: large integer	minimum	minima	minima	1	large integer	large integer	
ff	minima of <month and year>: month and year	minimum	minima	minima	1	month and year	month and year	
ff	minima of <month>: month	minimum	minima	minima	1	month	month	
ff	minima of <number of months>: number of months	minimum	minima	minima	1	number of months	number of months	
e2	minima of <rate>: rate	minimum	minima	minima	1	rate	rate	
4	minima of <rpm package release>: rpm package release
4	minima of <rpm package version record>: rpm package version record
4	minima of <rpm package version>: rpm package version
4	minima of <short rpm package version record>: short rpm package version record
ff	minima of <site version list>: site version list	minimum	minima	minima	1	site version list	site version list	
ff	minima of <time interval>: time interval	minimum	minima	minima	1	time interval	time interval	
ff	minima of <time of day>: time of day	minimum	minima	minima	1	time of day	time of day	
ff	minima of <time>: time	minimum	minima	minima	1	time	time	
5a	minima of <uinteger>: uinteger	minimum	minima	minima	1	uinteger	uinteger	
1f	minima of <uuid>: uuid
ff	minima of <version>: version	minimum	minima	minima	1	version	version	
ff	minima of <year>: year	minimum	minima	minima	1	year	year	
10	minimum password age of <security database>: time interval
10	minimum password length of <security database>: integer
e0	minimum single computer total of <statistical bin>: floating point	minimum single computer total	minimum single computer totals	minimum single computer total	0	floating point	statistical bin	
e0	minimum value of <statistical bin>: floating point	minimum value	minimum values	minimum value	0	floating point	statistical bin	
1f	minimum_value of <dmi electrical_current_probe>: integer
1f	minimum_value of <dmi temperature_probe>: integer
1f	minimum_value of <dmi voltage_probe>: integer
d	minor of <device file>: integer
ff	minor revision of <version>: integer	minor revision	minor revisions	minor revision	0	integer	version	
1f	minor version of <operating system>: integer
ff	minute: time interval	minute	minutes	minute	0	time interval		
ff	minute_of_hour of <time of day with time zone>: integer	minute_of_hour	minutes_of_hour	minute_of_hour	0	integer	time of day with time zone	
ff	minute_of_hour of <time of day>: integer	minute_of_hour	minutes_of_hour	minute_of_hour	0	integer	time of day	
10	missed run count of <scheduled task>: integer
ff	mobile count of <bes product>: integer	mobile count	mobile counts	mobile count	0	integer	bes product	
d	mode of <filesystem object>: mode
1d	model name of <processor>: string
1f	model of <processor>: integer
1f	model_part_number of <dmi system_power_supply>: string
2	modem scripts folder of <domain>: folder
2	modem scripts folder: folder
e0	modification time of <bes activation>: time	modification time	modification times	modification time	0	time	bes activation	
e0	modification time of <bes fixlet>: time	modification time	modification times	modification time	0	time	bes fixlet	
1f	modification time of <execution>: time
1f	modification time of <filesystem object>: time
d	modification time of <symlink>: time
2	modification time of <volume>: time
e0	modification user of <bes fixlet>: bes user	modification user	modification users	modification user	0	bes user	bes fixlet	
2	modified flag of <route>: boolean
d	module <integer> of <grub bootable image>: grub module
ff	module <string>: module	module	modules	module	0	module		string
d	modules of <grub bootable image>: grub module
ff	modules: module	module	modules	modules	1	module		
ff	monday: day of week	monday	mondays	monday	0	day of week		
12	monitor intervals of <power history>: monitor power interval
12	monitor invalid state: power state
12	monitor off state: power state
12	monitor on state: power state
12	monitor standby state: power state
ff	month <integer>: month	month	months	month	0	month		integer
ff	month <string>: month	month	months	month	0	month		string
ff	month of <date>: month	month	months	month	0	month	date	
ff	month of <day of year>: month	month	months	month	0	month	day of year	
ff	month of <month and year>: month	month	months	month	0	month	month and year	
ff	month: number of months	month	months	month	0	number of months		
ff	month_and_year of <date>: month and year	month_and_year	months_and_years	month_and_year	0	month and year	date	
10	monthly task trigger type: task trigger type
10	monthlydow task trigger type: task trigger type
10	months runs of <monthly task trigger>: month
10	months runs of <monthlydow task trigger>: month
ff	more significance <integer> of <floating point>: floating point	more significance	more significances	more significance	0	floating point	floating point	integer
ff	most significant one bit of <bit set>: integer	most significant one bit	most significant one bits	most significant one bit	0	integer	bit set	
d	mount option of <filesystem>: string
d	mount point of <filesystem>: string
f	mtu of <route>: integer
2	multicast flag of <route>: boolean
1f	multicast support of <network adapter interface>: boolean
1f	multicast support of <network adapter>: boolean
1f	multicast support of <network ip interface>: boolean
e0	multiple flag of <bes action>: boolean	multiple flag	multiple flags	multiple flag	0	boolean	bes action	
e0	multiplicity of <bes action with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes action with multiplicity	
e0	multiplicity of <bes computer group with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes computer group with multiplicity	
e0	multiplicity of <bes computer with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes computer with multiplicity	
e0	multiplicity of <bes domain with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes domain with multiplicity	
e0	multiplicity of <bes filter with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes filter with multiplicity	
e0	multiplicity of <bes fixlet with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes fixlet with multiplicity	
40	multiplicity of <bes idp directory with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes idp directory with multiplicity	
e0	multiplicity of <bes ldap directory with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes ldap directory with multiplicity	
40	multiplicity of <bes peer download with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes peer download with multiplicity	
e0	multiplicity of <bes property with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes property with multiplicity	
e0	multiplicity of <bes role with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes role with multiplicity	
e0	multiplicity of <bes site file with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes site file with multiplicity	
e0	multiplicity of <bes site with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes site with multiplicity	
e0	multiplicity of <bes unmanagedasset with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes unmanagedasset with multiplicity	
e0	multiplicity of <bes user with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes user with multiplicity	
e0	multiplicity of <bes webui app with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes webui app with multiplicity	
e0	multiplicity of <bes wizard with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	bes wizard with multiplicity	
ff	multiplicity of <date with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	date with multiplicity	
ff	multiplicity of <day of month with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	day of month with multiplicity	
ff	multiplicity of <day of week with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	day of week with multiplicity	
ff	multiplicity of <day of year with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	day of year with multiplicity	
9	multiplicity of <debian package upstream version with multiplicity>: integer
9	multiplicity of <debian package version epoch with multiplicity>: integer
9	multiplicity of <debian package version revision with multiplicity>: integer
9	multiplicity of <debian package version with multiplicity>: integer
ff	multiplicity of <floating point with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	floating point with multiplicity	
ff	multiplicity of <hertz with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	hertz with multiplicity	
ff	multiplicity of <integer with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	integer with multiplicity	
ff	multiplicity of <ipv4 address with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	ipv4 address with multiplicity	
ff	multiplicity of <ipv4or6 address with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	ipv4or6 address with multiplicity	
ff	multiplicity of <ipv6 address with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	ipv6 address with multiplicity	
5a	multiplicity of <large integer with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	large integer with multiplicity	
ff	multiplicity of <month and year with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	month and year with multiplicity	
ff	multiplicity of <month with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	month with multiplicity	
ff	multiplicity of <number of months with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	number of months with multiplicity	
e2	multiplicity of <rate with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	rate with multiplicity	
4	multiplicity of <rpm package release with multiplicity>: integer
4	multiplicity of <rpm package version record with multiplicity>: integer
4	multiplicity of <rpm package version with multiplicity>: integer
4	multiplicity of <short rpm package version record with multiplicity>: integer
ff	multiplicity of <site version list with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	site version list with multiplicity	
ff	multiplicity of <string with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	string with multiplicity	
ff	multiplicity of <time interval with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time interval with multiplicity	
ff	multiplicity of <time of day with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time of day with multiplicity	
ff	multiplicity of <time of day with time zone with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time of day with time zone with multiplicity	
ff	multiplicity of <time range with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time range with multiplicity	
ff	multiplicity of <time with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time with multiplicity	
ff	multiplicity of <time zone with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time zone with multiplicity	
5a	multiplicity of <uinteger with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	uinteger with multiplicity	
1f	multiplicity of <uuid with multiplicity>: integer
ff	multiplicity of <version with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	version with multiplicity	
ff	multiplicity of <year with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	year with multiplicity	
ff	multivalued of <property>: boolean	multivalued	multivalueds	multivalued	0	boolean	property	
ff	mvs count of <bes product>: integer	mvs count	mvs counts	mvs count	0	integer	bes product	
d	name of <SELinux Boolean>: string
d	name of <Xinetd Service>: string
12	name of <active directory group>: string
12	name of <active directory local user>: string
12	name of <agent interface capability>: string
1f	name of <application usage summary instance>: string
1f	name of <application usage summary>: string
10	name of <audit policy category>: string
10	name of <audit policy subcategory>: string
e0	name of <bes action parameter>: string	name	names	name	0	string	bes action parameter	
e0	name of <bes action>: string	name	names	name	0	string	bes action	
e0	name of <bes activation>: string	name	names	name	0	string	bes activation	
e0	name of <bes baseline component group>: string	name	names	name	0	string	bes baseline component group	
e0	name of <bes baseline component>: string	name	names	name	0	string	bes baseline component	
e0	name of <bes client setting>: string	name	names	name	0	string	bes client setting	
e0	name of <bes computer group>: string	name	names	name	0	string	bes computer group	
e0	name of <bes computer>: string	name	names	name	0	string	bes computer	
e0	name of <bes deployment option>: string	name	names	name	0	string	bes deployment option	
e0	name of <bes domain>: string	name	names	name	0	string	bes domain	
e0	name of <bes filter>: string	name	names	name	0	string	bes filter	
e0	name of <bes fixlet field>: string	name	names	name	0	string	bes fixlet field	
e0	name of <bes fixlet>: string	name	names	name	0	string	bes fixlet	
40	name of <bes idp directory>: string	name	names	name	0	string	bes idp directory	
e0	name of <bes ldap directory>: string	name	names	name	0	string	bes ldap directory	
ff	name of <bes product>: string	name	names	name	0	string	bes product	
e0	name of <bes property>: string	name	names	name	0	string	bes property	
e0	name of <bes role>: string	name	names	name	0	string	bes role	
e0	name of <bes site>: string	name	names	name	0	string	bes site	
e0	name of <bes unmanagedasset field>: string	name	names	name	0	string	bes unmanagedasset field	
e0	name of <bes user>: string	name	names	name	0	string	bes user	
e0	name of <bes webui app>: string	name	names	name	0	string	bes webui app	
e0	name of <bes wizard variable>: string	name	names	name	0	string	bes wizard variable	
e0	name of <bes wizard>: string	name	names	name	0	string	bes wizard	
ff	name of <binary operator>: string	name	names	name	0	string	binary operator	
4	name of <capability>: string
ff	name of <cast>: string	name	names	name	0	string	cast	
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
ff	name of <json key>: string	name	names	name	0	string	json key	
10	name of <local group>: string
1f	name of <logged on user>: string
10	name of <metabase key>: string
e0	name of <mime field>: string	name	names	name	0	string	mime field	
ff	name of <module>: string	name	names	name	0	string	module	
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
ff	name of <type>: string	name	names	name	0	string	type	
ff	name of <unary operator>: string	name	names	name	0	string	unary operator	
1f	name of <user>: string
2	name of <volume>: string
12	name of <wifi>: string
10	name of <winrt enumeration>: string
10	name of <winrt package id>: string
10	name of <wmi select>: string
2	name registry version: version
ff	nan of <floating point>: boolean	nan	nans	nan	0	boolean	floating point	
10	native application <string>: application
10	native file <string> of <encoding>: file
10	native file <string>: file
10	native folder <string> of <encoding>: folder
10	native folder <string>: folder
10	native program files folder: folder
10	native registry: registry
10	native system folder: folder
e0	navbar name of <bes wizard>: string	navbar name	navbar names	navbar name	0	string	bes wizard	
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
ff	nil: undefined	nil	nothings	nil	0	undefined		
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
ff	non windows server count of <bes product>: integer	non windows server count	non windows server counts	non windows server count	0	integer	bes product	
10	none firewall service type: firewall service type
10	none logon of <task principal>: boolean
ff	noon: time of day	noon	noons	noon	0	time of day		
10	normal account flag of <user>: boolean
10	normal of <filesystem object>: boolean
ff	normal of <floating point>: boolean	normal	normals	normal	0	boolean	floating point	
d	normal of <grub color scheme>: grub color pair
1f	normal of <power level>: boolean
10	normal priority: priority class
10	normalized date of <fixlet_header>: date
10	notifications disabled of <firewall profile>: boolean
d	nounzip of <grub module>: boolean
ff	november <integer> of <integer>: date	november	novembers	november	0	date	integer	integer
ff	november <integer>: day of year	november	novembers	november	0	day of year		integer
ff	november of <integer>: month and year	november	novembers	november	0	month and year	integer	
ff	november: month	november	novembers	november	0	month		
1f	now of <registration server>: time
ff	now: time	now	nows	now	0	time		
10	nt domain controller product type: operating system product type
10	nt server product type: operating system product type
10	nt workstation product type: operating system product type
2	nubus map: integer
10	null dacl of <security descriptor>: boolean
1f	null of <sqlite column type>: boolean
10	null sacl of <security descriptor>: boolean
ff	null: undefined	null	nothing	null	0	undefined		
1f	number_of_additional_information_entries of <dmi additional_information>: integer
1f	number_of_associated_memory_slots of <dmi memory_controller_information>: integer
1f	number_of_buttons of <dmi built_in_pointing_device>: integer
1f	number_of_contained_object_handles of <dmi base_board_information>: integer
1f	number_of_memory_devices of <dmi physical_memory_array>: integer
1f	number_of_power_cords of <dmi system_enclosure_or_chassis>: integer
10	numeric type of <drive>: integer
ff	numeric value of <string>: integer	numeric value	numeric values	numeric value	0	integer	string	
1f	nv_storage_device_address of <dmi ipmi_device_information>: integer
1d	nx bit of <process>: boolean
10	object access category of <audit policy>: audit policy category
10	object inherit of <access control entry>: boolean
4	obsoletes of <package>: capability
ff	october <integer> of <integer>: date	october	octobers	october	0	date	integer	integer
ff	october <integer>: day of year	october	octobers	october	0	day of year		integer
ff	october of <integer>: month and year	october	octobers	october	0	month and year	integer	
ff	october: month	october	octobers	october	0	month		
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
e0	offer category of <bes action>: string	offer category	offer categories	offer category	0	string	bes action	
e0	offer description html of <bes action>: html	offer description html	offer description htmls	offer description html	0	html	bes action	
e0	offer flag of <bes action>: boolean	offer flag	offer flags	offer flag	0	boolean	bes action	
1f	offer of <action>: boolean
10	offline of <filesystem object>: boolean
1f	offset of <smbios value>: integer
10	ok firewall local policy modify state: firewall local policy modify state
ff	ol <string> of <html>: html	ol	ols	ol	0	html	html	string
ff	ol <string> of <string>: html	ol	ols	ol	0	html	string	string
ff	ol of <html>: html	ol	ols	ol	0	html	html	
ff	ol of <string>: html	ol	ols	ol	0	html	string	
10	oldest record number of <event log>: integer
2	on appropriate disk domain: domain
2	on system disk domain: domain
1f	on_board_devices_information <integer> of <dmi>: dmi on_board_devices_information
1f	on_board_devices_informations of <dmi>: dmi on_board_devices_information
1f	onboard_devices_extended_information <integer> of <dmi>: dmi onboard_devices_extended_information
1f	onboard_devices_extended_informations of <dmi>: dmi onboard_devices_extended_information
ff	one bits of <bit set>: integer	one bit	one bits	one bits	1	integer	bit set	
d	only from of <Xinetd Service>: string
10	only raw version block of <file>: file version block
10	only version block of <file>: file version block
e0	open action count of <bes fixlet>: integer	open action count	open action counts	open action count	0	integer	bes fixlet	
ff	operand type of <cast>: type	operand type	operand types	operand type	0	type	cast	
ff	operand type of <unary operator>: type	operand type	operand types	operand type	0	type	unary operator	
e0	operating system of <bes computer>: string	operating system	operating systems	operating system	0	string	bes computer	
10	operating system product type <integer>: operating system product type
1f	operating system: operating system
e0	operator of <bes site>: bes user	operator	operators	operator	0	bes user	bes site	
e0	operator site flag of <bes action>: boolean	operator site flag	operator site flags	operator site flag	0	boolean	bes action	
e0	operator site flag of <bes fixlet>: boolean	operator site flag	operator site flags	operator site flag	0	boolean	bes fixlet	
e0	operator site flag of <bes site>: boolean	operator site flag	operator site flags	operator site flag	0	boolean	bes site	
e0	operator site of <bes user>: bes site	operator site	operator sites	operator site	0	bes site	bes user	
10	options of <port mapping>: integer
ff	ordered lists <string> of <html>: html	ordered list	ordered lists	ordered lists	1	html	html	string
ff	ordered lists <string> of <string>: html	ordered list	ordered lists	ordered lists	1	html	string	string
ff	ordered lists of <html>: html	ordered list	ordered lists	ordered lists	1	html	html	
ff	ordered lists of <string>: html	ordered list	ordered lists	ordered lists	1	html	string	
ff	organization of <license>: string	organization	organizations	organization	0	string	license	
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
ff	overflow of <floating point>: boolean	overflow	overflows	overflow	0	boolean	floating point	
bd	owner document of <xml dom node>: xml dom document
e0	owner flag <bes user> of <bes site>: boolean	owner flag	owner flags	owner flag	0	boolean	bes site	bes user
10	owner of <security descriptor>: security identifier
e0	owner set of <bes site>: bes user set	owner set	owner sets	owner set	0	bes user set	bes site	
e0	owners of <bes site>: bes user	owner	owners	owners	1	bes user	bes site	
ff	p <string> of <html>: html	p	ps	p	0	html	html	string
ff	p <string> of <string>: html	p	ps	p	0	html	string	string
ff	p of <html>: html	p	ps	p	0	html	html	
ff	p of <string>: html	p	ps	p	0	html	string	
9	packages <string> of <debianpackagecache>: debian versioned package
4	packages <string> of <rpmdatabase>: package
4	packages conflicting with <capability> of <rpmdatabase>: package
4	packages installing <capability> of <rpmdatabase>: package
9	packages of <debianpackagecache>: debian versioned package
4	packages of <rpmdatabase>: package
4	packages providing <capability> of <rpmdatabase>: package
4	packages requiring <capability> of <rpmdatabase>: package
ff	pad of <version>: version	pad	pads	pad	0	version	version	
ff	padded string of <bit set>: string	padded string	padded strings	padded string	0	string	bit set	
10	page fault count of <process>: integer
10	page file usage of <process>: integer
10	parallel instance of <task settings>: boolean
1f	parameter <string> of <action>: string
e0	parameter <string> of <bes action>: string	parameter	parameters	parameter	0	string	bes action	string
1f	parameter <string>: string
e0	parameters of <bes action>: bes action parameter	parameter	parameters	parameters	1	bes action parameter	bes action	
1f	parent folder of <filesystem object>: folder
d	parent folder of <symlink>: folder
e0	parent group of <bes action>: bes action	parent group	parent groups	parent group	0	bes action	bes action	
10	parent key of <registry key value>: registry key
10	parent key of <registry key>: registry key
bd	parent node of <xml dom node>: xml dom node
ff	parent of <type>: type	parent	parents	parent	0	type	type	
e0	parent relevances of <bes fixlet>: string	parent relevance	parent relevances	parent relevances	1	string	bes fixlet	
ff	parenthesized part <integer> of <regular expression match>: substring	parenthesized part	parenthesized parts	parenthesized part	0	substring	regular expression match	integer
ff	parenthesized parts of <regular expression match>: substring	parenthesized part	parenthesized parts	parenthesized parts	1	substring	regular expression match	
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
ff	patch revision of <version>: integer	patch revision	patch revisions	patch revision	0	integer	version	
1f	path <string> of <instance data>: json value
ff	path <string> of <json value>: json value	path	paths	path	0	json value	json value	string
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
40	peer flag of <bes peer download>: boolean	peer flag	peer flags	peer flag	0	boolean	bes peer download	
1d	pem encoded certificate of <file>: x509 certificate
1d	pem encoded certificate string of <string>: x509 certificate
e0	pending license update: boolean	pending license update	pending license updates	pending license update	0	boolean		
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
ff	percent decode <string>: string	percent decode	percent decodes	percent decode	0	string		string
ff	percent encode <binary_string>: string	percent encode	percent encodes	percent encode	0	string		binary_string
ff	percent encode <string>: string	percent encode	percent encodes	percent encode	0	string		string
10	performance counter frequency of <operating system>: hertz
10	performance counter of <operating system>: integer
1a	perl regex escape of <string>: string
1a	perl regexes <string>: regular expression
1a	perl regular expressions <string>: regular expression
10	permission permission of <network share>: boolean
ff	perpetual maintenance of <bes product>: boolean	perpetual maintenance	perpetual maintenances	perpetual maintenance	0	boolean	bes product	
ff	perpetual of <bes product>: boolean	perpetual	perpetuals	perpetual	0	boolean	bes product	
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
e0	plain bes fixlet set: bes fixlet set	plain bes fixlet set	plain bes fixlet sets	plain bes fixlet set	0	bes fixlet set		
e0	plain bes fixlets: bes fixlet	plain bes fixlet	plain bes fixlets	plain bes fixlets	1	bes fixlet		
d	platform id of <language>: string
10	platform id of <operating system>: integer
1f	plugged of <power level>: boolean
1d	plugin portal service: service
14	plugin store <string>: plugin store
e0	plural flag of <bes property result>: boolean	plural flag	plural flags	plural flag	0	boolean	bes property result	
ff	plural name of <property>: string	plural name	plural names	plural name	0	string	property	
1f	point to point of <network adapter interface>: boolean
2	point to point of <network adapter>: boolean
1f	point to point of <network ip interface>: boolean
10	policy change category of <audit policy>: audit policy category
d	policy of <process>: string
10	port mappings of <internet connection firewall>: port mapping
1f	port number of <selected server>: integer
d	port of <Xinetd Service>: integer
40	port of <bes idp directory server>: integer	port	ports	port	0	integer	bes idp directory server	
e0	port of <bes ldap directory server>: integer	port	ports	port	0	integer	bes ldap directory server	
10	port of <firewall open port>: integer
1f	port_connector_information <integer> of <dmi>: dmi port_connector_information
1f	port_connector_informations of <dmi>: dmi port_connector_information
1f	port_type of <dmi port_connector_information>: integer
1f	portable_battery <integer> of <dmi>: dmi portable_battery
1f	portable_batterys of <dmi>: dmi portable_battery
ff	position <integer> of <binary_string>: binary position	position	positions	position	0	binary position	binary_string	integer
ff	position <integer> of <string>: string position	position	positions	position	0	string position	string	integer
ff	positions of <binary_string>: binary position	position	positions	positions	1	binary position	binary_string	
ff	positions of <string>: string position	position	positions	positions	1	string position	string	
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
e0	postaction allow cancel flag of <bes action>: boolean	postaction allow cancel flag	postaction allow cancel flags	postaction allow cancel flag	0	boolean	bes action	
e0	postaction force delay of <bes action>: time interval	postaction force delay	postaction force delays	postaction force delay	0	time interval	bes action	
e0	postaction message text of <bes action>: string	postaction message text	postaction message texts	postaction message text	0	string	bes action	
e0	postaction message title of <bes action>: string	postaction message title	postaction message titles	postaction message title	0	string	bes action	
e0	postaction postpone delay of <bes action>: time interval	postaction postpone delay	postaction postpone delays	postaction postpone delay	0	time interval	bes action	
12	power history: power history
1f	power level: power level
2	power plane of <registryroot>: registrynode
1f	power_supply_characteristics of <dmi system_power_supply>: integer
1f	power_supply_state of <dmi system_enclosure_or_chassis>: integer
1f	power_unit_group of <dmi system_power_supply>: integer
2	powerpc: boolean
1f	ppid of <process>: integer
2	prcloning flag of <route>: boolean
ff	pre <string> of <html>: html	pre	pres	pre	0	html	html	string
ff	pre <string> of <string>: html	pre	pres	pre	0	html	string	string
ff	pre of <html>: html	pre	pres	pre	0	html	html	
ff	pre of <string>: html	pre	pres	pre	0	html	string	
e0	pre60 flag of <bes wizard>: boolean	pre60 flag	pre60 flags	pre60 flag	0	boolean	bes wizard	
e0	precache flag of <bes action>: boolean	precache flag	precache flags	precache flag	0	boolean	bes action	
ff	preceding binary_string of <binary position>: binary_substring	preceding binary_string	preceding binary_strings	preceding binary_string	0	binary_substring	binary position	
ff	preceding binary_string of <binary_substring>: binary_substring	preceding binary_string	preceding binary_strings	preceding binary_string	0	binary_substring	binary_substring	
ff	preceding text of <string position>: substring	preceding text	preceding texts	preceding text	0	substring	string position	
ff	preceding text of <substring>: substring	preceding text	preceding texts	preceding text	0	substring	substring	
2	preference <string>: preference
2	preferences folder of <domain>: folder
2	preferences folder: folder
e0	preferred bes language: string	preferred bes language	preferred bes languages	preferred bes language	0	string		
40	prefetch flag of <bes peer download>: boolean	prefetch flag	prefetch flags	prefetch flag	0	boolean	bes peer download	
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
40	priority of <bes idp directory server>: integer	priority	priorities	priority	0	integer	bes idp directory server	
e0	priority of <bes ldap directory server>: integer	priority	priorities	priority	0	integer	bes ldap directory server	
d	priority of <process>: integer
1f	priority of <selected server>: integer
10	priority of <task settings>: integer
10	private firewall profile type: firewall profile type
e0	private flag of <bes filter>: boolean	private flag	private flags	private flag	0	boolean	bes filter	
40	private flag of <bes tag>: boolean	private flag	private flags	private flag	0	boolean	bes tag	
e0	private flag of <bes wizard variable>: boolean	private flag	private flags	private flag	0	boolean	bes wizard variable	
2	private framework folder of <domain>: folder
2	private framework folder: folder
1f	private ip of <cloud provider>: string
10	private profile of <firewall policy>: firewall profile
e0	private variable <( string, string )>: string	private variable	private variables	private variable	0	string		( string, string )
e0	private variable <string> of <bes wizard>: string	private variable	private variables	private variable	0	string	bes wizard	string
e0	private variables of <bes wizard>: bes wizard variable	private variable	private variables	private variables	1	bes wizard variable	bes wizard	
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
ff	products of <floating point>: floating point	product	products	products	1	floating point	floating point	
ff	products of <integer>: integer	product	products	products	1	integer	integer	
ff	products of <license>: bes product	product	products	products	1	bes product	license	
10	profile <firewall profile type> of <firewall rule>: boolean
10	profile folder of <user>: string
10	profile of <site>: site profile
10	profile types of <firewall>: firewall profile type
10	profiles of <firewall policy>: firewall profile
10	program files folder: folder
10	program files x32 folder: folder
10	program files x64 folder: folder
ff	properties <string> of <type>: property	property	properties	properties	1	property	type	string
ff	properties <string>: property	property	properties	properties	1	property		string
e0	properties of <bes fixlet>: bes property	property	properties	properties	1	bes property	bes fixlet	
ff	properties of <type>: property	property	properties	properties	1	property	type	
10	properties of <wmi object>: wmi select
ff	properties returning <type> of <type>: property	property returning	properties returning	properties returning	1	property	type	type
ff	properties returning <type>: property	property returning	properties returning	properties returning	1	property		type
ff	properties: property	property	properties	properties	1	property		
e0	property <integer> of <bes fixlet>: bes property	property	properties	property	0	bes property	bes fixlet	integer
10	property <string> of <wmi object>: wmi select
1f	property duration of <evaluation cycle>: time interval
e0	property of <bes property result>: bes property	property	properties	property	0	bes property	bes property result	
1f	property percent of <evaluation cycle>: floating point
e0	property results of <bes computer>: bes property result	property result	property results	property results	1	bes property result	bes computer	
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
40	public flag of <bes tag>: boolean	public flag	public flags	public flag	0	boolean	bes tag	
ff	public key algorithm of <x509 certificate>: string	public key algorithm	public key algorithms	public key algorithm	0	string	x509 certificate	
10	public profile of <firewall policy>: firewall profile
10	publisher id of <winrt package id>: string
10	publisher of <winrt package id>: string
ff	q <string> of <html>: html	q	qs	q	0	html	html	string
ff	q <string> of <string>: html	q	qs	q	0	html	string	string
ff	q of <html>: html	q	qs	q	0	html	html	
ff	q of <string>: html	q	qs	q	0	html	string	
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
ff	random floating point: floating point	random floating point	random floating points	random floating point	0	floating point		
ff	random integer of <integer>: integer	random integer	random integers	random integer	0	integer	integer	
ff	random integer: integer	random integer	random integers	random integer	0	integer		
e0	range <time range> of <statistic range>: statistic range	range	ranges	range	0	statistic range	statistic range	time range
ff	range after <time> of <time range>: time range	range after	ranges after	range after	0	time range	time range	time
ff	range before <time> of <time range>: time range	range before	ranges before	range before	0	time range	time range	time
12	range of <monitor power interval>: time range
12	range of <system power interval>: time range
e2	rate <time interval> of <exponential projection>: floating point	rate	rates	rate	0	floating point	exponential projection	time interval
e2	rate of <linear projection>: rate	rate	rates	rate	0	rate	linear projection	
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
e0	reader set of <bes site>: bes user set	reader set	reader sets	reader set	0	bes user set	bes site	
e0	readers of <bes site>: bes user	reader	readers	readers	1	bes user	bes site	
10	readonly of <filesystem object>: boolean
10	ready state of <running task>: boolean
10	ready state of <scheduled task>: boolean
2	real <integer> of <array>: floating point
2	real <string> of <dictionary>: floating point
2	real of <osxvalue>: floating point
10	realtime priority: priority class
e0	reapplication interval of <bes action>: time interval	reapplication interval	reapplication intervals	reapplication interval	0	time interval	bes action	
e0	reapplication limit of <bes action>: integer	reapplication limit	reapplication limits	reapplication limit	0	integer	bes action	
e0	reapply flag of <bes action>: boolean	reapply flag	reapply flags	reapply flag	0	boolean	bes action	
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
ff	regex escape of <string>: string	regex escape	regex escapes	regex escape	0	string	string	
ff	regexes <string>: regular expression	regex	regexes	regexes	1	regular expression		string
1f	region of <cloud provider>: string
ff	registrar number of <license>: integer	registrar number	registrar numbers	registrar number	0	integer	license	
1f	registration address of <client>: ipv4or6 address
1f	registration cidr address of <client>: string
10	registration info of <task definition>: task registration info
1f	registration mac address of <client>: string
1f	registration server: registration server
1f	registration subnet address of <client>: ipv4or6 address
10	registration task trigger type: task trigger type
2	registry: dummy type
10	registry: registry
ff	regular expressions <string>: regular expression	regular expression	regular expressions	regular expressions	1	regular expression		string
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
ff	relative significance place <integer> of <floating point>: floating point	relative significance place	relative significance places	relative significance place	0	floating point	floating point	integer
ff	relative significance place of <floating point>: floating point	relative significance place	relative significance places	relative significance place	0	floating point	floating point	
e0	relay distance of <bes computer>: integer	relay distance	relay distances	relay distance	0	integer	bes computer	
e0	relay hostname of <bes computer>: string	relay hostname	relay hostnames	relay hostname	0	string	bes computer	
40	relay of <bes peer download>: string	relay	relays	relay	0	string	bes peer download	
1f	relay select duration of <evaluation cycle>: time interval
1f	relay select percent of <evaluation cycle>: floating point
e0	relay selection method of <bes computer>: string	relay selection method	relay selection methods	relay selection method	0	string	bes computer	
e0	relay server flag of <bes computer>: boolean	relay server flag	relay server flags	relay server flag	0	boolean	bes computer	
e0	relay server of <bes computer>: string	relay server	relay servers	relay server	0	string	bes computer	
2	relay service: nothing
1d	relay service: service
9	release of <debian versioned package>: string
1d	release of <operating system>: string
2	release of <operating system>: version
4	release of <rpm package version record>: rpm package release
4	release of <short rpm package version record>: rpm package release
12	releaseid of <operating system>: string
e0	relevance clauses of <bes fixlet>: string	relevance clause	relevance clauses	relevance clauses	1	string	bes fixlet	
1f	relevance duration of <evaluation cycle>: time interval
e0	relevance of <bes baseline component>: string	relevance	relevances	relevance	0	string	bes baseline component	
e0	relevance of <bes fixlet>: string	relevance	relevances	relevance	0	string	bes fixlet	
1f	relevance of <fixlet>: boolean
1f	relevance percent of <evaluation cycle>: floating point
e0	relevant <( bes computer, bes fixlet )>: boolean	relevant	relevants	relevant	0	boolean		( bes computer, bes fixlet )
e0	relevant <( bes fixlet, bes computer )>: boolean	relevant	relevants	relevant	0	boolean		( bes fixlet, bes computer )
e0	relevant <bes computer> of <bes fixlet>: boolean	relevant	relevants	relevant	0	boolean	bes fixlet	bes computer
e0	relevant <bes fixlet> of <bes computer>: boolean	relevant	relevants	relevant	0	boolean	bes computer	bes fixlet
40	relevant fixlet count of <bes computer>: integer	relevant fixlet count	relevant fixlet counts	relevant fixlet count	0	integer	bes computer	
e0	relevant fixlet set of <bes computer>: bes fixlet set	relevant fixlet set	relevant fixlet sets	relevant fixlet set	0	bes fixlet set	bes computer	
e0	relevant fixlets of <bes computer>: bes fixlet	relevant fixlet	relevant fixlets	relevant fixlets	1	bes fixlet	bes computer	
1f	relevant fixlets of <site>: fixlet
e0	relevant flag of <bes fixlet result>: boolean	relevant flag	relevant flags	relevant flag	0	boolean	bes fixlet result	
1f	relevant offer actions of <site>: action
40	remediated <( bes computer, bes fixlet )>: boolean	remediated	remediateds	remediated	0	boolean		( bes computer, bes fixlet )
40	remediated <( bes fixlet, bes computer )>: boolean	remediated	remediateds	remediated	0	boolean		( bes fixlet, bes computer )
40	remediated <bes computer> of <bes fixlet>: boolean	remediated	remediateds	remediated	0	boolean	bes fixlet	bes computer
40	remediated <bes fixlet> of <bes computer>: boolean	remediated	remediateds	remediated	0	boolean	bes computer	bes fixlet
40	remediated computer count of <bes fixlet>: integer	remediated computer count	remediated computer counts	remediated computer count	0	integer	bes fixlet	
40	remediated computer set of <bes fixlet>: bes computer set	remediated computer set	remediated computer sets	remediated computer set	0	bes computer set	bes fixlet	
40	remediated computers of <bes fixlet>: bes computer	remediated computer	remediated computers	remediated computers	1	bes computer	bes fixlet	
40	remediated fixlet count of <bes computer>: integer	remediated fixlet count	remediated fixlet counts	remediated fixlet count	0	integer	bes computer	
40	remediated fixlet set of <bes computer>: bes fixlet set	remediated fixlet set	remediated fixlet sets	remediated fixlet set	0	bes fixlet set	bes computer	
40	remediated fixlets of <bes computer>: bes fixlet	remediated fixlet	remediated fixlets	remediated fixlets	1	bes fixlet	bes computer	
e0	remediated flag of <bes fixlet result>: boolean	remediated flag	remediated flags	remediated flag	0	boolean	bes fixlet result	
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
40	report time of <bes peer download>: time	report time	report times	report time	0	time	bes peer download	
e0	reported action set of <bes computer>: bes action set	reported action set	reported action sets	reported action set	0	bes action set	bes computer	
e0	reported computer set of <bes action>: bes computer set	reported computer set	reported computer sets	reported computer set	0	bes computer set	bes action	
e0	reported computer set of <bes property>: bes computer set	reported computer set	reported computer sets	reported computer set	0	bes computer set	bes property	
e0	reported property set of <bes computer>: bes property set	reported property set	reported property sets	reported property set	0	bes property set	bes computer	
ff	representable in <string> of <binary_string>: boolean	representable in	representables in	representable in	0	boolean	binary_string	string
ff	representable in utf16 of <binary_string>: boolean	representable in utf16	representables in utf16	representable in utf16	0	boolean	binary_string	
ff	representable in utf8 of <binary_string>: boolean	representable in utf8	representables in utf8	representable in utf8	0	boolean	binary_string	
ff	representable of <binary_string>: boolean	representable	representables	representable	0	boolean	binary_string	
ff	representation in <string> of <binary_string>: string	representation in	representations in	representation in	0	string	binary_string	string
e0	require user absence of <bes action>: boolean	require user absence	require user absences	require user absence	0	boolean	bes action	
e0	require user presence of <bes action>: boolean	require user presence	require user presences	require user presence	0	boolean	bes action	
e0	requires authoring flag of <bes wizard>: boolean	requires authoring flag	requires authoring flags	requires authoring flag	0	boolean	bes wizard	
4	requires of <package>: capability
e0	reserved flag of <bes property>: boolean	reserved flag	reserved flags	reserved flag	0	boolean	bes property	
1f	reserved of <dmi bios_language_information>: binary_string
1f	reserved of <dmi system_boot_information>: binary_string
1f	reset_count of <dmi system_reset>: integer
1f	reset_limit of <dmi system_reset>: integer
1f	resolution of <dmi electrical_current_probe>: integer
1f	resolution of <dmi temperature_probe>: integer
1f	resolution of <dmi voltage_probe>: integer
2	resource fork of <file>: resfork
10	restart count of <task settings>: integer
e0	restart flag of <bes action>: boolean	restart flag	restart flags	restart flag	0	boolean	bes action	
10	restart interval of <task settings>: time interval
10	restart on idle of <task idle settings>: boolean
e0	restartandshutdown actionscript privilege allowboth flag of <bes user>: boolean	restartandshutdown actionscript privilege allowboth flag	restartandshutdown actionscript privilege allowboth flags	restartandshutdown actionscript privilege allowboth flag	0	boolean	bes user	
e0	restartandshutdown actionscript privilege allowrestartonly flag of <bes user>: boolean	restartandshutdown actionscript privilege allowrestartonly flag	restartandshutdown actionscript privilege allowrestartonly flags	restartandshutdown actionscript privilege allowrestartonly flag	0	boolean	bes user	
e0	restartandshutdown actionscript privilege none flag of <bes user>: boolean	restartandshutdown actionscript privilege none flag	restartandshutdown actionscript privilege none flags	restartandshutdown actionscript privilege none flag	0	boolean	bes user	
e0	restartandshutdown postaction privilege allowboth flag of <bes user>: boolean	restartandshutdown postaction privilege allowboth flag	restartandshutdown postaction privilege allowboth flags	restartandshutdown postaction privilege allowboth flag	0	boolean	bes user	
e0	restartandshutdown postaction privilege allowrestartonly flag of <bes user>: boolean	restartandshutdown postaction privilege allowrestartonly flag	restartandshutdown postaction privilege allowrestartonly flags	restartandshutdown postaction privilege allowrestartonly flag	0	boolean	bes user	
e0	restartandshutdown postaction privilege none flag of <bes user>: boolean	restartandshutdown postaction privilege none flag	restartandshutdown postaction privilege none flags	restartandshutdown postaction privilege none flag	0	boolean	bes user	
1f	restricted site: restricted site
e0	result <( bes action, bes computer )>: bes action result	result	results	result	0	bes action result		( bes action, bes computer )
e0	result <( bes computer, bes action )>: bes action result	result	results	result	0	bes action result		( bes computer, bes action )
e0	result <( bes computer, bes fixlet )>: bes fixlet result	result	results	result	0	bes fixlet result		( bes computer, bes fixlet )
e0	result <( bes computer, bes property )>: bes property result	result	results	result	0	bes property result		( bes computer, bes property )
e0	result <( bes fixlet, bes computer )>: bes fixlet result	result	results	result	0	bes fixlet result		( bes fixlet, bes computer )
e0	result <( bes property, bes computer )>: bes property result	result	results	result	0	bes property result		( bes property, bes computer )
e0	result from <bes action> of <bes computer>: bes action result	result from	results from	result from	0	bes action result	bes computer	bes action
e0	result from <bes computer> of <bes action>: bes action result	result from	results from	result from	0	bes action result	bes action	bes computer
e0	result from <bes computer> of <bes fixlet>: bes fixlet result	result from	results from	result from	0	bes fixlet result	bes fixlet	bes computer
e0	result from <bes computer> of <bes property>: bes property result	result from	results from	result from	0	bes property result	bes property	bes computer
e0	result from <bes fixlet> of <bes computer>: bes fixlet result	result from	results from	result from	0	bes fixlet result	bes computer	bes fixlet
e0	result from <bes property> of <bes computer>: bes property result	result from	results from	result from	0	bes property result	bes computer	bes property
ff	result type of <binary operator>: type	result type	result types	result type	0	type	binary operator	
ff	result type of <cast>: type	result type	result types	result type	0	type	cast	
ff	result type of <property>: type	result type	result types	result type	0	type	property	
ff	result type of <unary operator>: type	result type	result types	result type	0	type	unary operator	
e0	results of <bes action>: bes action result	result	results	results	1	bes action result	bes action	
e0	results of <bes fixlet>: bes fixlet result	result	results	results	1	bes fixlet result	bes fixlet	
e0	results of <bes property>: bes property result	result	results	results	1	bes property result	bes property	
e0	retry count of <bes action result>: integer	retry count	retry counts	retry count	0	integer	bes action result	
e0	retry delay of <bes action>: time interval	retry delay	retry delays	retry delay	0	time interval	bes action	
e0	retry limit of <bes action>: integer	retry limit	retry limits	retry limit	0	integer	bes action	
e0	retry wait for reboot flag of <bes action>: boolean	retry wait for reboot flag	retry wait for reboot flags	retry wait for reboot flag	0	boolean	bes action	
9	reverse dependencies of <debian versioned package>: debianpkg reverse dependencies
9	revision of <debian package version>: debian package version revision
2	revision of <scsidevice>: string
1f	revision_level of <dmi system_power_supply>: string
ff	right operand type of <binary operator>: type	right operand type	right operand types	right operand type	0	type	binary operator	
ff	right shift <integer> of <bit set>: bit set	right shift	right shifts	right shift	0	bit set	bit set	integer
e0	role set of <bes user>: bes role set	role set	role sets	role set	0	bes role set	bes user	
e0	roles of <bes user>: bes role	role	roles	roles	1	bes role	bes user	
2	rom version: version
10	root folder of <drive>: folder
d	root folder: folder
d	root of <grub bootable image>: grub device
e0	root server flag of <bes computer>: boolean	root server flag	root server flags	root server flag	0	boolean	bes computer	
e0	root server of <bes computer>: string	root server	root servers	root server	0	string	bes computer	
1f	root server: root server
d	rootnoverify of <grub bootable image>: grub device
ff	rope <string>: rope	rope	ropes	rope	0	rope		string
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
e0	running message text of <bes action>: string	running message text	running message texts	running message text	0	string	bes action	
e0	running message title of <bes action>: string	running message title	running message titles	running message title	0	string	bes action	
1f	running of <application usage summary>: boolean
10	running of <local mssql database>: boolean
1d	running of <service>: boolean
1d	running service <string>: service
10	running services: service
10	running state of <running task>: boolean
10	running state of <scheduled task>: boolean
10	running tasks: running task
ff	rvu count of <bes product>: integer	rvu count	rvu counts	rvu count	0	integer	bes product	
10	s4u logon of <task principal>: boolean
10	sacl of <security descriptor>: system access control list
ff	samp <string> of <html>: html	samp	samps	samp	0	html	html	string
ff	samp <string> of <string>: html	samp	samps	samp	0	html	string	string
ff	samp of <html>: html	samp	samps	samp	0	html	html	
ff	samp of <string>: html	samp	samps	samp	0	html	string	
12	sample time of <active directory group>: time
12	sample time of <active directory local computer>: time
12	sample time of <active directory local user>: time
e0	sans id list of <bes fixlet>: string	sans id list	sans id lists	sans id list	0	string	bes fixlet	
ff	saturday: day of week	saturday	saturdays	saturday	0	day of week		
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
e0	scope of <bes client setting>: string	scope	scopes	scope	0	string	bes client setting	
10	scope of <firewall authorized application>: firewall scope
10	scope of <firewall open port>: firewall scope
10	scope of <firewall service>: firewall scope
10	script flag of <user>: boolean
e0	script of <bes fixlet action>: string	script	scripts	script	0	string	bes fixlet action	
e0	script type of <bes fixlet action>: string	script type	script types	script type	0	string	bes fixlet action	
2	scripting additions folder of <domain>: folder
2	scripting additions folder: folder
2	scsibus <integer>: scsibus
2	scsibuses: scsibus
2	scsidevice <integer> of <scsibus>: scsidevice
2	scsidevice <integer>: scsidevice
2	scsidevices of <scsibus>: scsidevice
2	scsidevices: scsidevice
ff	seat count state of <license>: string	seat count state	seat count states	seat count state	0	string	license	
ff	seat of <license>: integer	seat	seats	seat	0	integer	license	
ff	second: time interval	second	seconds	second	0	time interval		
ff	second_of_minute of <time of day with time zone>: integer	second_of_minute	seconds_of_minute	second_of_minute	0	integer	time of day with time zone	
ff	second_of_minute of <time of day>: integer	second_of_minute	seconds_of_minute	second_of_minute	0	integer	time of day	
10	secondary wins server of <network adapter>: ipv4 address
2	seconds to expiration of <route>: integer
1f	section <string> of <file>: file section
9	section of <debian versioned package>: string
9	section of <debianpkg version>: string
10	secure attribute of <metabase value>: boolean
e0	secure parameter flag of <bes action>: boolean	secure parameter flag	secure parameter flags	secure parameter flag	0	boolean	bes action	
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
e0	selected groups string of <bes action>: string	selected groups string	selected groups strings	selected groups string	0	string	bes action	
1f	selected server: selected server
10	selects <string> of <wmi>: wmi select
b0	selects <string> of <xml dom node>: xml dom node
d	selinux booleans <string>: SELinux Boolean
d	selinux booleans: SELinux Boolean
d	selinux context of <process>: string
d	selinux domain of <process>: string
2	sent packet count of <route>: integer
d	sep bug of <processor>: boolean
ff	september <integer> of <integer>: date	september	septembers	september	0	date	integer	integer
ff	september <integer>: day of year	september	septembers	september	0	day of year		integer
ff	september of <integer>: month and year	september	septembers	september	0	month and year	integer	
ff	september: month	september	septembers	september	0	month		
ff	serial number of <x509 certificate>: string	serial number	serial numbers	serial number	0	string	x509 certificate	
1f	serial of <hardware>: string
1f	serial_number of <dmi base_board_information>: string
1f	serial_number of <dmi memory_device>: string
1f	serial_number of <dmi portable_battery>: string
1f	serial_number of <dmi processor_information>: string
1f	serial_number of <dmi system_enclosure_or_chassis>: string
1f	serial_number of <dmi system_information>: string
1f	serial_number of <dmi system_power_supply>: string
d	server arg of <Xinetd Service>: string
e0	server based flag of <bes computer group>: boolean	server based flag	server based flags	server based flag	0	boolean	bes computer group	
1f	server based group <string> of <client>: server based group
1f	server based groups of <client>: server based group
d	server of <Xinetd Service>: string
10	server of <email task action>: string
10	server operator flag of <user>: boolean
10	server trust account flag of <user>: boolean
40	servers of <bes idp directory>: bes idp directory server	server	servers	servers	1	bes idp directory server	bes idp directory	
e0	servers of <bes ldap directory>: bes ldap directory server	server	servers	servers	1	bes ldap directory server	bes ldap directory	
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
e0	sets of <bes action>: bes action set	set	sets	sets	1	bes action set	bes action	
e0	sets of <bes computer group>: bes computer group set	set	sets	sets	1	bes computer group set	bes computer group	
e0	sets of <bes computer>: bes computer set	set	sets	sets	1	bes computer set	bes computer	
e0	sets of <bes domain>: bes domain set	set	sets	sets	1	bes domain set	bes domain	
e0	sets of <bes filter>: bes filter set	set	sets	sets	1	bes filter set	bes filter	
e0	sets of <bes fixlet>: bes fixlet set	set	sets	sets	1	bes fixlet set	bes fixlet	
40	sets of <bes idp directory>: bes idp directory set	set	sets	sets	1	bes idp directory set	bes idp directory	
e0	sets of <bes ldap directory>: bes ldap directory set	set	sets	sets	1	bes ldap directory set	bes ldap directory	
e0	sets of <bes property>: bes property set	set	sets	sets	1	bes property set	bes property	
e0	sets of <bes role>: bes role set	set	sets	sets	1	bes role set	bes role	
e0	sets of <bes site file>: bes site file set	set	sets	sets	1	bes site file set	bes site file	
e0	sets of <bes site>: bes site set	set	sets	sets	1	bes site set	bes site	
e0	sets of <bes unmanagedasset>: bes unmanagedasset set	set	sets	sets	1	bes unmanagedasset set	bes unmanagedasset	
e0	sets of <bes user>: bes user set	set	sets	sets	1	bes user set	bes user	
e0	sets of <bes webui app>: bes webui app set	set	sets	sets	1	bes webui app set	bes webui app	
e0	sets of <bes wizard>: bes wizard set	set	sets	sets	1	bes wizard set	bes wizard	
ff	sets of <integer>: integer set	set	sets	sets	1	integer set	integer	
ff	sets of <string>: string set	set	sets	sets	1	string set	string	
1f	setting <string> of <client>: setting
1f	setting <string> of <site>: setting
1f	setting of <manual group>: setting
1f	setting of <server based group>: setting
10	setting of <task definition>: task settings
e0	settings flag of <bes action>: boolean	settings flag	settings flags	settings flag	0	boolean	bes action	
1f	settings of <client>: setting
1f	settings of <site>: setting
d	setuid of <filesystem object>: boolean
d	setuid of <mode>: boolean
1f	sha1 of <file>: string
ff	sha1 of <string>: string	sha1	sha1s	sha1	0	string	string	
ff	sha1 of <x509 certificate>: string	sha1	sha1s	sha1	0	string	x509 certificate	
1f	sha224 of <file>: string
ff	sha224 of <string>: string	sha224	sha224s	sha224	0	string	string	
ff	sha256 download of <license>: boolean	sha256 download	sha256 downloads	sha256 download	0	boolean	license	
1f	sha256 of <file>: string
1f	sha256 of <setting>: string
ff	sha256 of <string>: string	sha256	sha256s	sha256	0	string	string	
1f	sha2_224 of <file>: string
ff	sha2_224 of <string>: string	sha2_224	sha2_224s	sha2_224	0	string	string	
1f	sha2_256 of <file>: string
ff	sha2_256 of <string>: string	sha2_256	sha2_256s	sha2_256	0	string	string	
1f	sha2_384 of <file>: string
ff	sha2_384 of <string>: string	sha2_384	sha2_384s	sha2_384	0	string	string	
1f	sha2_512 of <file>: string
ff	sha2_512 of <string>: string	sha2_512	sha2_512s	sha2_512	0	string	string	
1f	sha384 of <file>: string
ff	sha384 of <string>: string	sha384	sha384s	sha384	0	string	string	
5a	sha384 signature of <license>: boolean	sha384 signature	sha384 signatures	sha384 signature	0	boolean	license	
1f	sha512 of <file>: string
ff	sha512 of <string>: string	sha512	sha512s	sha512	0	string	string	
d	shared amount of <ram>: integer
2	shared folder of <domain>: folder
2	shared folder: folder
2	shared libraries folder of <domain>: folder
2	shared libraries folder: folder
e0	shared variable <( string, string )>: string	shared variable	shared variables	shared variable	0	string		( string, string )
e0	shared variable <string> of <bes wizard>: string	shared variable	shared variables	shared variable	0	string	bes wizard	string
e0	shared variables of <bes wizard>: bes wizard variable	shared variable	shared variables	shared variables	1	bes wizard variable	bes wizard	
4	short form of <rpm package version record>: short rpm package version record
2	short name of <client process owner>: string
4	short rpm package version record <rpm package version record>: short rpm package version record
4	short rpm package version record <short rpm package version record>: short rpm package version record
2	short version of <filesystem object>: version
10	shortcut of <file>: file shortcut
e0	show message flag of <bes action>: boolean	show message flag	show message flags	show message flag	0	boolean	bes action	
10	show message task action type: task action type
e0	show other action flag of <bes user>: boolean	show other action flag	show other action flags	show other action flag	0	boolean	bes user	
e0	show running message flag of <bes action>: boolean	show running message flag	show running message flags	show running message flag	0	boolean	bes action	
e0	shutdown flag of <bes action>: boolean	shutdown flag	shutdown flags	shutdown flag	0	boolean	bes action	
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
ff	signature algorithm of <x509 certificate>: string	signature algorithm	signature algorithms	signature algorithm	0	string	x509 certificate	
ff	signature hash algorithms of <license>: string	signature hash algorithm	signature hash algorithms	signature hash algorithms	1	string	license	
4	signature keyid of <package>: string
ff	significance place <integer> of <floating point>: floating point	significance place	significance places	significance place	0	floating point	floating point	integer
ff	significance place of <floating point>: floating point	significance place	significance places	significance place	0	floating point	floating point	
ff	significance threshold of <floating point>: floating point	significance threshold	significance thresholds	significance threshold	0	floating point	floating point	
ff	significant digits <integer> of <hertz>: hertz	significant digits	significant digitss	significant digits	0	hertz	hertz	integer
ff	significant digits <integer> of <integer>: integer	significant digits	significant digitss	significant digits	0	integer	integer	integer
e0	simple name of <bes property>: string	simple name	simple names	simple name	0	string	bes property	
e0	single flag of <bes action>: boolean	single flag	single flags	single flag	0	boolean	bes action	
10	single user ts bit <operating system suite mask>: boolean
ff	singular name of <property>: string	singular name	singular names	singular name	0	string	property	
1f	site <string>: site
e0	site file set of <bes site>: bes site file set	site file set	site files sets	site file set	0	bes site file set	bes site	
e0	site files of <bes site>: bes site file	site file	site files	site files	1	bes site file	bes site	
40	site id of <bes peer download>: integer	site id	site ids	site id	0	integer	bes peer download	
e0	site level relevance of <bes site>: string	site level relevance	site level relevances	site level relevance	0	string	bes site	
ff	site number of <license>: integer	site number	site numbers	site number	0	integer	license	
e0	site of <bes computer group>: bes site	site	sites	site	0	bes site	bes computer group	
e0	site of <bes fixlet>: bes site	site	sites	site	0	bes site	bes fixlet	
40	site of <bes peer download>: bes site	site	sites	site	0	bes site	bes peer download	
e0	site of <bes wizard>: bes site	site	sites	site	0	bes site	bes wizard	
1f	site of <fixlet>: site
1f	site tag of <site>: string
ff	site urls of <bes product>: string	site url	site urls	site urls	1	string	bes product	
ff	site version list <string>: site version list	site version list	site version lists	site version list	0	site version list		string
1f	site version list of <site>: site version list
40	site version of <bes peer download>: integer	site version	site versions	site version	0	integer	bes peer download	
1f	sites: site
1f	size of <application usage summary instance>: integer
2	size of <array>: integer
e0	size of <bes action set>: integer	size	sizes	size	0	integer	bes action set	
e0	size of <bes computer group set>: integer	size	sizes	size	0	integer	bes computer group set	
e0	size of <bes computer set>: integer	size	sizes	size	0	integer	bes computer set	
e0	size of <bes domain set>: integer	size	sizes	size	0	integer	bes domain set	
e0	size of <bes filter set>: integer	size	sizes	size	0	integer	bes filter set	
e0	size of <bes fixlet set>: integer	size	sizes	size	0	integer	bes fixlet set	
40	size of <bes idp directory set>: integer	size	sizes	size	0	integer	bes idp directory set	
e0	size of <bes ldap directory set>: integer	size	sizes	size	0	integer	bes ldap directory set	
40	size of <bes peer download>: integer	size	sizes	size	0	integer	bes peer download	
e0	size of <bes property set>: integer	size	sizes	size	0	integer	bes property set	
e0	size of <bes role set>: integer	size	sizes	size	0	integer	bes role set	
e0	size of <bes site file set>: integer	size	sizes	size	0	integer	bes site file set	
e0	size of <bes site set>: integer	size	sizes	size	0	integer	bes site set	
e0	size of <bes unmanagedasset set>: integer	size	sizes	size	0	integer	bes unmanagedasset set	
e0	size of <bes user set>: integer	size	sizes	size	0	integer	bes user set	
e0	size of <bes webui app set>: integer	size	sizes	size	0	integer	bes webui app set	
e0	size of <bes wizard set>: integer	size	sizes	size	0	integer	bes wizard set	
2	size of <datafork>: integer
2	size of <dictionary>: integer
1f	size of <dmi memory_device>: integer
1f	size of <file>: integer
d	size of <filesystem>: integer
ff	size of <integer set>: integer	size	sizes	size	0	integer	integer set	
1f	size of <ram>: integer
10	size of <registry key value>: integer
2	size of <resfork>: integer
ff	size of <string set>: integer	size	sizes	size	0	integer	string set	
f	size of <swap>: integer
ff	size of <type>: integer	size	sizes	size	0	integer	type	
2	size of <volume>: integer
e0	skewness of <statistical bin>: floating point	skewness	skewnesses	skewness	0	floating point	statistical bin	
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
ff	small <string> of <html>: html	small	smalls	small	0	html	html	string
ff	small <string> of <string>: html	small	smalls	small	0	html	string	string
10	small business bit <operating system suite mask>: boolean
10	small business restricted bit <operating system suite mask>: boolean
ff	small of <html>: html	small	smalls	small	0	html	html	
ff	small of <string>: html	small	smalls	small	0	html	string	
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
e0	source analysis of <bes property>: bes fixlet	source analysis	source analyses	source analysis	0	bes fixlet	bes property	
e0	source evaluation period of <bes property>: time interval	source evaluation period	source evaluation periods	source evaluation period	0	time interval	bes property	
e0	source fixlet of <bes action>: bes fixlet	source fixlet	source fixlets	source fixlet	0	bes fixlet	bes action	
e0	source fixlet of <bes baseline component>: bes fixlet	source fixlet	source fixlets	source fixlet	0	bes fixlet	bes baseline component	
40	source host of <bes peer download>: string	source host	source hosts	source host	0	string	bes peer download	
e0	source id of <bes fixlet>: string	source id	source ids	source id	0	string	bes fixlet	
e0	source id of <bes property>: integer	source id	source ids	source id	0	integer	bes property	
e0	source name of <bes property>: string	source name	source names	source name	0	string	bes property	
e0	source of <bes fixlet>: string	source	sources	source	0	string	bes fixlet	
e0	source of <bes unmanagedasset>: string	source	sources	source	0	string	bes unmanagedasset	
10	source of <event log record>: string
10	source of <task registration info>: string
e0	source release date of <bes fixlet>: date	source release date	source release dates	source release date	0	date	bes fixlet	
e0	source relevance of <bes action>: string	source relevance	source relevances	source relevance	0	string	bes action	
e0	source severity of <bes fixlet>: string	source severity	source severities	source severity	0	string	bes fixlet	
e0	source severity of <fixlet count pair>: string	source severity	source severitys	source severity	0	string	fixlet count pair	
ff	span <string> of <html>: html	span	spans	span	0	html	html	string
ff	span <string> of <string>: html	span	spans	span	0	html	string	string
ff	span of <html>: html	span	spans	span	0	html	html	
ff	span of <string>: html	span	spans	span	0	html	string	
2	speech folder of <domain>: folder
2	speech folder: folder
1f	speed of <dmi memory_device>: integer
1f	speed of <processor>: hertz
d	splashimage of <grub config file>: grub file location
1f	sqlite database of <file>: sqlite database
1f	sqlite version: version
ff	sqrt of <floating point>: floating point	sqrt	sqrts	sqrt	0	floating point	floating point	
ff	sqrt of <integer>: floating point	sqrt	sqrts	sqrt	0	floating point	integer	
12	ssid of <wifi network>: string
12	ssid of <wifi>: string
2	stage <string>: stage
2	stage of <version>: stage
e0	standard deviation of <statistical bin>: floating point	standard deviation	standard deviations	standard deviation	0	floating point	statistical bin	
ff	standard deviations of <floating point>: floating point	standard deviation	standard deviations	standard deviations	1	floating point	floating point	
ff	standard deviations of <integer>: floating point	standard deviation	standard deviations	standard deviations	1	floating point	integer	
10	standard firewall profile type: firewall profile type
10	standard profile of <firewall policy>: firewall profile
12	standby state: power state
10	start boundary of <task trigger>: time
e0	start date of <bes action>: date	start date	start dates	start date	0	date	bes action	
ff	start date of <license>: time	start date	start dates	start date	0	time	license	
e0	start flag of <bes action>: boolean	start flag	start flags	start flag	0	boolean	bes action	
10	start in pathname of <file shortcut>: string
ff	start of <binary_substring>: binary position	start	starts	start	0	binary position	binary_substring	
e0	start of <statistic range>: time	start	starts	start	0	time	statistic range	
e0	start of <statistical bin>: time	start	starts	start	0	time	statistical bin	
ff	start of <substring>: string position	start	starts	start	0	string position	substring	
ff	start of <time range>: time	start	starts	start	0	time	time range	
e0	start time of <bes action result>: time	start time	start times	start time	0	time	bes action result	
d	start time of <process>: time
e0	start time_of_day of <bes action>: time of day	start time_of_day	start times_of_day	start time_of_day	0	time of day	bes action	
10	start type of <service>: string
10	start when available of <task settings>: boolean
1f	starting_address of <dmi memory_array_mapped_address>: integer
1f	starting_address of <dmi memory_device_mapped_address>: integer
2	startup items <string>: enableable_file
2	startup items folder of <domain>: folder
2	startup items folder: folder
2	startup items: enableable_file
12	state of <agent interface capability>: string
e0	state of <bes action>: string	state	states	state	0	string	bes action	
ff	state of <bes product>: string	state	states	state	0	string	bes product	
2	state of <dummy>: string
12	state of <monitor power interval>: power state
1d	state of <service>: string
12	state of <system power interval>: power state
1f	statement <string> of <sqlite database>: sqlite statement
2	static flag of <route>: boolean
2	stationery of <file>: boolean
e0	statistic range of <bes property>: statistic range	statistic range	statistic ranges	statistic range	0	statistic range	bes property	
1f	status of <action>: string
10	status of <active device>: integer
e0	status of <bes action result>: bes action status	status	statuses	status	0	bes action status	bes action result	
e0	status of <bes activation>: string	status	statuses	status	0	string	bes activation	
10	status of <connection>: connection status
1f	status of <dmi processor_information>: integer
10	status of <network adapter>: integer
2	stealth enabled of <firewall>: boolean
1f	stepping of <processor>: integer
d	sticky of <mode>: boolean
10	stop at duration end of <task repetition pattern>: boolean
10	stop existing instance of <task settings>: boolean
10	stop on idle end of <task idle settings>: boolean
e0	stop other actions flag of <bes user>: boolean	stop other actions flag	stop other actions flags	stop other actions flag	0	boolean	bes user	
10	stop when going on battery of <task settings>: boolean
e0	stopper of <bes action>: bes user	stopper	stoppers	stopper	0	bes user	bes action	
1f	storage folder of <client>: folder
2	string <integer> of <array>: string
2	string <string> of <dictionary>: string
2	string <string> of <preference>: string
ff	string <string>: string	string	strings	string	0	string		string
1f	string named files of <folder>: file
1f	string named folders of <folder>: folder
2	string of <osxvalue>: string
ff	string of <tuple item>: string	string	strings	string	0	string	tuple item	
10	string value <integer> of <wmi select>: string
1f	string values <string> of <smbios structure>: smbios value
10	string values of <wmi select>: string
1f	string version of <application usage summary instance>: string
1f	strings <string> of <smbios structure>: string
ff	strong <string> of <html>: html	strong	strongs	strong	0	html	html	string
ff	strong <string> of <string>: html	strong	strongs	strong	0	html	string	string
ff	strong of <html>: html	strong	strongs	strong	0	html	html	
ff	strong of <string>: html	strong	strongs	strong	0	html	string	
1f	structure of <smbios value>: smbios structure
1f	structures <string> of <smbios>: smbios structure
1f	structures of <smbios>: smbios structure
4d	strverscmp version <string>: strverscmp version	strverscmp version	strverscmp versions	strverscmp version	0	strverscmp version		string
ff	sub <string> of <html>: html	sub	subs	sub	0	html	html	string
ff	sub <string> of <string>: html	sub	subs	sub	0	html	string	string
ff	sub of <html>: html	sub	subs	sub	0	html	html	
ff	sub of <string>: html	sub	subs	sub	0	html	string	
10	subcategories of <audit policy category>: audit policy subcategory
ff	subject common name of <x509 certificate>: string	subject common name	subject common names	subject common name	0	string	x509 certificate	
10	subject of <email task action>: string
ff	subject of <x509 certificate>: string	subject	subjects	subject	0	string	x509 certificate	
1f	subnet address of <network adapter interface>: ipv4or6 address
1f	subnet address of <network adapter>: ipv4 address
10	subnet address of <network address list>: ipv4 address
1f	subnet address of <network ip interface>: ipv4 address
1a	subnet mask of <cidr subnet>: ipv4or6 address
1f	subnet mask of <network adapter interface>: ipv4or6 address
1f	subnet mask of <network adapter>: ipv4 address
10	subnet mask of <network address list>: ipv4 address
1f	subnet mask of <network ip interface>: ipv4 address
40	subnet of <bes peer download>: string	subnet	subnets	subnet	0	string	bes peer download	
1f	subscribe time of <site>: time
e0	subscribed <( bes computer, bes site )>: boolean	subscribed	subscribeds	subscribed	0	boolean		( bes computer, bes site )
e0	subscribed <( bes site, bes computer )>: boolean	subscribed	subscribeds	subscribed	0	boolean		( bes site, bes computer )
e0	subscribed <bes computer> of <bes site>: boolean	subscribed	subscribeds	subscribed	0	boolean	bes site	bes computer
e0	subscribed <bes site> of <bes computer>: boolean	subscribed	subscribeds	subscribed	0	boolean	bes computer	bes site
e0	subscribed computer set of <bes site>: bes computer set	subscribed computer set	subscribed computer sets	subscribed computer set	0	bes computer set	bes site	
e0	subscribed computers of <bes site>: bes computer	subscribed computer	subscribed computers	subscribed computers	1	bes computer	bes site	
e0	subscribed site set of <bes computer>: bes site set	subscribed site set	subscribed site sets	subscribed site set	0	bes site set	bes computer	
e0	subscribed sites of <bes computer>: bes site	subscribed site	subscribed sites	subscribed sites	1	bes site	bes computer	
e0	subscription flag of <bes action>: boolean	subscription flag	subscription flags	subscription flag	0	boolean	bes action	
e0	subscription mode of <bes site>: string	subscription mode	subscription modes	subscription mode	0	string	bes site	
10	subscription of <event task trigger>: string
ff	substring <( integer, integer )> of <string>: substring	substring	substrings	substring	0	substring	string	( integer, integer )
ff	substrings <string> of <string>: substring	substring	substrings	substrings	1	substring	string	string
ff	substrings after <string> of <string>: substring	substring after	substrings after	substrings after	1	substring	string	string
ff	substrings before <string> of <string>: substring	substring before	substrings before	substrings before	1	substring	string	string
ff	substrings between <string> of <string>: substring	substring between	substrings between	substrings between	1	substring	string	string
ff	substrings separated by <string> of <string>: substring	substring separated by	substrings separated by	substrings separated by	1	substring	string	string
2	subtype of <component>: string
e0	success on custom relevance of <bes action>: boolean	success on custom relevance	success on custom relevances	success on custom relevance	0	boolean	bes action	
e0	success on custom relevance of <bes fixlet action>: boolean	success on custom relevance	success on custom relevances	success on custom relevance	0	boolean	bes fixlet action	
e0	success on original relevance of <bes action>: boolean	success on original relevance	success on original relevances	success on original relevance	0	boolean	bes action	
e0	success on original relevance of <bes fixlet action>: boolean	success on original relevance	success on original relevances	success on original relevance	0	boolean	bes fixlet action	
e0	success on run to completion of <bes action>: boolean	success on run to completion	success on run to completions	success on run to completion	0	boolean	bes action	
e0	success on run to completion of <bes fixlet action>: boolean	success on run to completion	success on run to completions	success on run to completion	0	boolean	bes fixlet action	
e0	success rate of <statistical bin>: floating point	success rate	success rates	success rate	0	floating point	statistical bin	
10	suite mask of <operating system>: operating system suite mask
ff	sums of <floating point>: floating point	sum	sums	sums	1	floating point	floating point	
ff	sums of <integer>: integer	sum	sums	sums	1	integer	integer	
ff	sums of <time interval>: time interval	sum	sums	sums	1	time interval	time interval	
ff	sunday: day of week	sunday	sundays	sunday	0	day of week		
ff	sup <string> of <html>: html	sup	sups	sup	0	html	html	string
ff	sup <string> of <string>: html	sup	sups	sup	0	html	string	string
ff	sup of <html>: html	sup	sups	sup	0	html	html	
ff	sup of <string>: html	sup	sups	sup	0	html	string	
1f	supported_interleave of <dmi memory_controller_information>: integer
1f	supported_memory_types of <dmi memory_controller_information>: integer
1f	supported_speeds of <dmi memory_controller_information>: integer
1f	supported_sram_type of <dmi cache_information>: integer
f	swap: swap
ff	symbol of <binary operator>: string	symbol	symbols	symbol	0	string	binary operator	
ff	symbol of <unary operator>: string	symbol	symbols	symbol	0	string	unary operator	
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
ff	table <string> of <html>: html	table	tables	table	0	html	html	string
1f	table <string> of <sqlite database>: sqlite table
ff	table <string> of <string>: html	table	tables	table	0	html	string	string
ff	table of <html>: html	table	tables	table	0	html	html	
ff	table of <string>: html	table	tables	table	0	html	string	
1f	tables of <sqlite database>: sqlite table
e0	tag of <bes site>: string	tag	tags	tag	0	string	bes site	
40	tagged actions of <string>: bes action	tagged action	tagged actions	tagged actions	1	bes action	string	
40	tagged fixlets of <string>: bes fixlet	tagged fixlet	tagged fixlets	tagged fixlets	1	bes fixlet	string	
40	tags of <bes action>: bes tag	tag	tags	tags	1	bes tag	bes action	
40	tags of <bes fixlet>: bes tag	tag	tags	tags	1	bes tag	bes fixlet	
e0	taken action set of <bes fixlet>: bes action set	taken action set	taken action sets	taken action set	0	bes action set	bes fixlet	
e0	taken actions of <bes fixlet>: bes action	taken action	taken actions	taken actions	1	bes action	bes fixlet	
10	target ip address of <port mapping>: ipv4 address
10	target ipv4or6 address of <port mapping>: ipv4or6 address
10	target name of <port mapping>: string
e0	targeted by id flag of <bes action>: boolean	targeted by id flag	targeted by id flags	targeted by id flag	0	boolean	bes action	
e0	targeted by list flag of <bes action>: boolean	targeted by list flag	targeted by list flags	targeted by list flag	0	boolean	bes action	
e0	targeted by property flag of <bes action>: boolean	targeted by property flag	targeted by property flags	targeted by property flag	0	boolean	bes action	
e0	targeted computer set of <bes action>: bes computer set	targeted computer set	targeted computer sets	targeted computer set	0	bes computer set	bes action	
e0	targeted computers of <bes action>: bes computer	targeted computer	targeted computers	targeted computers	1	bes computer	bes action	
e0	targeted list of <bes action>: string	targeted list	targeted lists	targeted list	0	string	bes action	
e0	targeted names of <bes action>: string	targeted name	targeted names	targeted names	1	string	bes action	
e0	targeting method of <bes action>: string	targeting method	targeting methods	targeting method	0	string	bes action	
e0	targeting relevance of <bes action>: string	targeting relevance	targeting relevances	targeting relevance	0	string	bes action	
10	task action type <integer>: task action type
e0	task flag of <bes filter>: boolean	task flag	task flags	task flag	0	boolean	bes filter	
e0	task flag of <bes fixlet>: boolean	task flag	task flags	task flag	0	boolean	bes fixlet	
10	task folder <string>: task folder
10	task folders of <task folder>: task folder
10	task name of <application>: string
e0	task set of <bes filter>: bes fixlet set	task set	task sets	task set	0	bes fixlet set	bes filter	
10	task trigger type <integer>: task trigger type
ff	tbody <string> of <html>: html	tbody	tbodys	tbody	0	html	html	string
ff	tbody <string> of <string>: html	tbody	tbodys	tbody	0	html	string	string
ff	tbody of <html>: html	tbody	tbodys	tbody	0	html	html	
ff	tbody of <string>: html	tbody	tbodys	tbody	0	html	string	
1f	tcp of <socket>: boolean
1f	tcp state of <socket>: tcp state
10	tcp: internet protocol
ff	td <string> of <html>: html	td	tds	td	0	html	html	string
ff	td <string> of <string>: html	td	tds	td	0	html	string	string
ff	td of <html>: html	td	tds	td	0	html	html	
ff	td of <string>: html	td	tds	td	0	html	string	
1f	temperature_probe <integer> of <dmi>: dmi temperature_probe
1f	temperature_probe_handle of <dmi cooling_device>: integer
1f	temperature_probes of <dmi>: dmi temperature_probe
10	template file of <site profile>: file
e0	temporal distribution of <bes action>: time interval	temporal distribution	temporal distributions	temporal distribution	0	time interval	bes action	
10	temporary duplicate account flag of <user>: boolean
2	temporary items folder of <domain>: folder
2	temporary items folder: folder
10	temporary of <filesystem object>: boolean
40	tenant id of <bes idp directory>: string	tenant id	tenant ids	tenant id	0	string	bes idp directory	
ff	term of <bes product>: boolean	term	terms	term	0	boolean	bes product	
10	terminal bit <operating system suite mask>: boolean
10	terminal server user group: security account
2	text encodings folder of <domain>: folder
2	text encodings folder: folder
e0	text of <bes comment>: string	text	texts	text	0	string	bes comment	
1f	text of <sqlite column type>: boolean
ff	tfoot <string> of <html>: html	tfoot	tfoots	tfoot	0	html	html	string
ff	tfoot <string> of <string>: html	tfoot	tfoots	tfoot	0	html	string	string
ff	tfoot of <html>: html	tfoot	tfoots	tfoot	0	html	html	
ff	tfoot of <string>: html	tfoot	tfoots	tfoot	0	html	string	
ff	th <string> of <html>: html	th	ths	th	0	html	html	string
ff	th <string> of <string>: html	th	ths	th	0	html	string	string
ff	th of <html>: html	th	ths	th	0	html	html	
ff	th of <string>: html	th	ths	th	0	html	string	
ff	thead <string> of <html>: html	thead	theads	thead	0	html	html	string
ff	thead <string> of <string>: html	thead	theads	thead	0	html	string	string
ff	thead of <html>: html	thead	theads	thead	0	html	html	
ff	thead of <string>: html	thead	theads	thead	0	html	string	
2	themes folder of <domain>: folder
2	themes folder: folder
1f	thermal_state of <dmi system_enclosure_or_chassis>: integer
1f	thread of <cpupackage>: integer
1f	thread_count of <dmi processor_information>: integer
1f	threshold_handle of <dmi management_device_component>: integer
ff	thursday: day of week	thursday	thursdays	thursday	0	day of week		
ff	time <string>: time	time	times	time	0	time		string
ff	time <time zone> of <time>: time of day with time zone	time	times	time	0	time of day with time zone	time	time zone
10	time generated of <event log record>: time
ff	time interval <string>: time interval	time interval	time intervals	time interval	0	time interval		string
e0	time issued of <bes action>: time	time issued	times issued	time issued	0	time	bes action	
1f	time of <execution>: time
e0	time of <historical computer count>: time	time	times	time	0	time	historical computer count	
e0	time of <historical fixlet count>: time	time	times	time	0	time	historical fixlet count	
ff	time of <time of day with time zone>: time of day	time	times	time	0	time of day	time of day with time zone	
e0	time range end of <bes action>: time of day	time range end	time range ends	time range end	0	time of day	bes action	
e0	time range start of <bes action>: time of day	time range start	time range starts	time range start	0	time of day	bes action	
e0	time stopped of <bes action>: time	time stopped	times stopped	time stopped	0	time	bes action	
10	time task trigger type: task trigger type
10	time value <integer> of <wmi select>: time
10	time values of <wmi select>: time
1f	time wait of <tcp state>: boolean
10	time written of <event log record>: time
ff	time zone <string>: time zone	time zone	time zones	time zone	0	time zone		string
ff	time_of_day <string>: time of day	time_of_day	times_of_day	time_of_day	0	time of day		string
1f	timeout of <dmi system_reset>: integer
d	timeout of <grub config file>: integer
1f	timer_interval of <dmi system_reset>: integer
e0	timestamp of <bes comment>: time	timestamp	timestamps	timestamp	0	time	bes comment	
ff	title <string> of <html>: html	title	titles	title	0	html	html	string
ff	title <string> of <string>: html	title	titles	title	0	html	string	string
d	title of <grub bootable image>: string
ff	title of <html>: html	title	titles	title	0	html	html	
10	title of <show message task action>: string
ff	title of <string>: html	title	titles	title	0	html	string	
ff	tls cipher list of <license>: string	tls cipher list	tls cipher lists	tls cipher list	0	string	license	
10	to of <email task action>: string
1f	tolerance of <dmi electrical_current_probe>: integer
1f	tolerance of <dmi temperature_probe>: integer
1f	tolerance of <dmi voltage_probe>: integer
e0	top level bes action set: bes action set	top level bes action set	top level bes action sets	top level bes action set	0	bes action set		
e0	top level bes actions: bes action	top level bes action	top level bes actions	top level bes actions	1	bes action		
e0	top level flag of <bes action>: boolean	top level flag	top level flags	top level flag	0	boolean	bes action	
1f	total amount of <ram>: integer
f	total amount of <swap>: integer
1f	total duration of <application usage summary instance>: time interval
1f	total duration of <application usage summary>: time interval
1f	total duration of <evaluation cycle>: time interval
e0	total lower bound of <statistical bin>: floating point	total lower bound	total lower bounds	total lower bound	0	floating point	statistical bin	
e0	total of <statistic range>: statistical bin	total	totals	total	0	statistical bin	statistic range	
10	total processor core count: integer
1f	total run count of <application usage summary instance>: integer
1f	total run count of <application usage summary>: integer
1f	total size of <download storage folder>: integer
10	total space of <drive>: integer
d	total space of <filesystem>: integer
2	total space of <volume>: integer
e0	total upper bound of <statistical bin>: floating point	total upper bound	total upper bounds	total upper bound	0	floating point	statistical bin	
1f	total_width of <dmi memory_device>: integer
e0	totals <time interval> of <statistic range>: statistical bin	total	totals	totals	1	statistical bin	statistic range	time interval
ff	tr <string> of <html>: html	tr	trs	tr	0	html	html	string
ff	tr <string> of <string>: html	tr	trs	tr	0	html	string	string
ff	tr of <html>: html	tr	trs	tr	0	html	html	
ff	tr of <string>: html	tr	trs	tr	0	html	string	
1f	track fixlets of <evaluation cycle>: string
10	traverse permission of <access control entry>: boolean
10	trigger strings of <scheduled task>: string
10	triggers of <task definition>: task trigger
ff	true: boolean	true	trues	true	0	boolean		
10	trustee of <access control entry>: security identifier
10	trustee type of <access control entry>: integer
ff	tt <string> of <html>: html	tt	tts	tt	0	html	html	string
ff	tt <string> of <string>: html	tt	tts	tt	0	html	string	string
ff	tt of <html>: html	tt	tts	tt	0	html	html	
ff	tt of <string>: html	tt	tts	tt	0	html	string	
1f	tty of <logged on user>: string
d	tty of <process>: string
d	tty of <user>: string
ff	tuesday: day of week	tuesday	tuesdays	tuesday	0	day of week		
10	tunnel of <network adapter>: boolean
ff	tuple items of <string>: tuple item	tuple item	tuple items	tuple items	1	tuple item	string	
ff	tuple string item <integer> of <string>: string	tuple string item	tuple string items	tuple string item	0	string	string	integer
ff	tuple string items of <string>: string	tuple string item	tuple string items	tuple string items	1	string	string	
ff	tuple strings of <string>: string	tuple string	tuple strings	tuple strings	1	string	string	
ff	two digit hour of <time of day with time zone>: string	two digit hour	two digit hours	two digit hour	0	string	time of day with time zone	
ff	two digit hour of <time of day>: string	two digit hour	two digit hours	two digit hour	0	string	time of day	
ff	two digit minute of <time of day with time zone>: string	two digit minute	two digit minutes	two digit minute	0	string	time of day with time zone	
ff	two digit minute of <time of day>: string	two digit minute	two digit minutes	two digit minute	0	string	time of day	
ff	two digit second of <time of day with time zone>: string	two digit second	two digit seconds	two digit second	0	string	time of day with time zone	
ff	two digit second of <time of day>: string	two digit second	two digit seconds	two digit second	0	string	time of day	
ff	type <string>: type	type	types	type	0	type		string
d	type of <Xinetd Service>: string
e0	type of <bes fixlet>: string	type	types	type	0	string	bes fixlet	
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
ff	type of <json value>: string	type	types	type	0	string	json value	
ff	type of <license>: string	type	types	type	0	string	license	
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
ff	types: type	type	types	types	1	type		
1f	udp of <socket>: boolean
10	udp: internet protocol
40	uid attribute of <bes idp directory>: string	uid attribute	uid attributes	uid attribute	0	string	bes idp directory	
e0	uid attribute of <bes ldap directory>: string	uid attribute	uid attributes	uid attribute	0	string	bes ldap directory	
d	uid of <filesystem object>: integer
d	uid of <symlink>: integer
5a	uinteger <integer>: uinteger	uinteger	uintegers	uinteger	0	uinteger		integer
5a	uinteger <string>: uinteger	uinteger	uintegers	uinteger	0	uinteger		string
ff	ul <string> of <html>: html	ul	uls	ul	0	html	html	string
ff	ul <string> of <string>: html	ul	uls	ul	0	html	string	string
ff	ul of <html>: html	ul	uls	ul	0	html	html	
ff	ul of <string>: html	ul	uls	ul	0	html	string	
ff	unary operators <string>: unary operator	unary operator	unary operators	unary operators	1	unary operator		string
ff	unary operators returning <type>: unary operator	unary operator returning	unary operators returning	unary operators returning	1	unary operator		type
ff	unary operators: unary operator	unary operator	unary operators	unary operators	1	unary operator		
d	unavailable amount of <ram>: integer
ff	underflow of <floating point>: boolean	underflow	underflows	underflow	0	boolean	floating point	
10	unicast responses to multicast broadcast disabled of <firewall profile>: boolean
40	unified id of <bes site>: integer	unified id	unified ids	unified id	0	integer	bes site	
e0	unions of <bes action set>: bes action set	union	unions	unions	1	bes action set	bes action set	
e0	unions of <bes computer group set>: bes computer group set	union	unions	unions	1	bes computer group set	bes computer group set	
e0	unions of <bes computer set>: bes computer set	union	unions	unions	1	bes computer set	bes computer set	
e0	unions of <bes domain set>: bes domain set	union	unions	unions	1	bes domain set	bes domain set	
e0	unions of <bes filter set>: bes filter set	union	unions	unions	1	bes filter set	bes filter set	
e0	unions of <bes fixlet set>: bes fixlet set	union	unions	unions	1	bes fixlet set	bes fixlet set	
40	unions of <bes idp directory set>: bes idp directory set	union	unions	unions	1	bes idp directory set	bes idp directory set	
e0	unions of <bes ldap directory set>: bes ldap directory set	union	unions	unions	1	bes ldap directory set	bes ldap directory set	
e0	unions of <bes property set>: bes property set	union	unions	unions	1	bes property set	bes property set	
e0	unions of <bes role set>: bes role set	union	unions	unions	1	bes role set	bes role set	
e0	unions of <bes site file set>: bes site file set	union	unions	unions	1	bes site file set	bes site file set	
e0	unions of <bes site set>: bes site set	union	unions	unions	1	bes site set	bes site set	
e0	unions of <bes unmanagedasset set>: bes unmanagedasset set	union	unions	unions	1	bes unmanagedasset set	bes unmanagedasset set	
e0	unions of <bes user set>: bes user set	union	unions	unions	1	bes user set	bes user set	
e0	unions of <bes webui app set>: bes webui app set	union	unions	unions	1	bes webui app set	bes webui app set	
e0	unions of <bes wizard set>: bes wizard set	union	unions	unions	1	bes wizard set	bes wizard set	
ff	unions of <integer set>: integer set	union	unions	unions	1	integer set	integer set	
ff	unions of <string set>: string set	union	unions	unions	1	string set	string set	
1f	unique id of <cloud provider>: string
4	unique name of <package>: string
e0	unique values of <bes action>: bes action with multiplicity	unique value	unique values	unique values	1	bes action with multiplicity	bes action	
e0	unique values of <bes computer group>: bes computer group with multiplicity	unique value	unique values	unique values	1	bes computer group with multiplicity	bes computer group	
e0	unique values of <bes computer>: bes computer with multiplicity	unique value	unique values	unique values	1	bes computer with multiplicity	bes computer	
e0	unique values of <bes domain>: bes domain with multiplicity	unique value	unique values	unique values	1	bes domain with multiplicity	bes domain	
e0	unique values of <bes filter>: bes filter with multiplicity	unique value	unique values	unique values	1	bes filter with multiplicity	bes filter	
e0	unique values of <bes fixlet>: bes fixlet with multiplicity	unique value	unique values	unique values	1	bes fixlet with multiplicity	bes fixlet	
40	unique values of <bes idp directory>: bes idp directory with multiplicity	unique value	unique values	unique values	1	bes idp directory with multiplicity	bes idp directory	
e0	unique values of <bes ldap directory>: bes ldap directory with multiplicity	unique value	unique values	unique values	1	bes ldap directory with multiplicity	bes ldap directory	
40	unique values of <bes peer download>: bes peer download with multiplicity	unique value	unique values	unique values	1	bes peer download with multiplicity	bes peer download	
e0	unique values of <bes property>: bes property with multiplicity	unique value	unique values	unique values	1	bes property with multiplicity	bes property	
e0	unique values of <bes role>: bes role with multiplicity	unique value	unique values	unique values	1	bes role with multiplicity	bes role	
e0	unique values of <bes site file>: bes site file with multiplicity	unique value	unique values	unique values	1	bes site file with multiplicity	bes site file	
e0	unique values of <bes site>: bes site with multiplicity	unique value	unique values	unique values	1	bes site with multiplicity	bes site	
e0	unique values of <bes unmanagedasset>: bes unmanagedasset with multiplicity	unique value	unique values	unique values	1	bes unmanagedasset with multiplicity	bes unmanagedasset	
e0	unique values of <bes user>: bes user with multiplicity	unique value	unique values	unique values	1	bes user with multiplicity	bes user	
e0	unique values of <bes webui app>: bes webui app with multiplicity	unique value	unique values	unique values	1	bes webui app with multiplicity	bes webui app	
e0	unique values of <bes wizard>: bes wizard with multiplicity	unique value	unique values	unique values	1	bes wizard with multiplicity	bes wizard	
ff	unique values of <date>: date with multiplicity	unique value	unique values	unique values	1	date with multiplicity	date	
ff	unique values of <day of month>: day of month with multiplicity	unique value	unique values	unique values	1	day of month with multiplicity	day of month	
ff	unique values of <day of week>: day of week with multiplicity	unique value	unique values	unique values	1	day of week with multiplicity	day of week	
ff	unique values of <day of year>: day of year with multiplicity	unique value	unique values	unique values	1	day of year with multiplicity	day of year	
9	unique values of <debian package upstream version>: debian package upstream version with multiplicity
9	unique values of <debian package version epoch>: debian package version epoch with multiplicity
9	unique values of <debian package version revision>: debian package version revision with multiplicity
9	unique values of <debian package version>: debian package version with multiplicity
ff	unique values of <floating point>: floating point with multiplicity	unique value	unique values	unique values	1	floating point with multiplicity	floating point	
ff	unique values of <hertz>: hertz with multiplicity	unique value	unique values	unique values	1	hertz with multiplicity	hertz	
ff	unique values of <integer>: integer with multiplicity	unique value	unique values	unique values	1	integer with multiplicity	integer	
ff	unique values of <ipv4 address>: ipv4 address with multiplicity	unique value	unique values	unique values	1	ipv4 address with multiplicity	ipv4 address	
ff	unique values of <ipv4or6 address>: ipv4or6 address with multiplicity	unique value	unique values	unique values	1	ipv4or6 address with multiplicity	ipv4or6 address	
ff	unique values of <ipv6 address>: ipv6 address with multiplicity	unique value	unique values	unique values	1	ipv6 address with multiplicity	ipv6 address	
5a	unique values of <large integer>: large integer with multiplicity	unique value	unique values	unique values	1	large integer with multiplicity	large integer	
ff	unique values of <month and year>: month and year with multiplicity	unique value	unique values	unique values	1	month and year with multiplicity	month and year	
ff	unique values of <month>: month with multiplicity	unique value	unique values	unique values	1	month with multiplicity	month	
ff	unique values of <number of months>: number of months with multiplicity	unique value	unique values	unique values	1	number of months with multiplicity	number of months	
e2	unique values of <rate>: rate with multiplicity	unique value	unique values	unique values	1	rate with multiplicity	rate	
4	unique values of <rpm package release>: rpm package release with multiplicity
4	unique values of <rpm package version record>: rpm package version record with multiplicity
4	unique values of <rpm package version>: rpm package version with multiplicity
4	unique values of <short rpm package version record>: short rpm package version record with multiplicity
ff	unique values of <site version list>: site version list with multiplicity	unique value	unique values	unique values	1	site version list with multiplicity	site version list	
ff	unique values of <string>: string with multiplicity	unique value	unique values	unique values	1	string with multiplicity	string	
ff	unique values of <time interval>: time interval with multiplicity	unique value	unique values	unique values	1	time interval with multiplicity	time interval	
ff	unique values of <time of day with time zone>: time of day with time zone with multiplicity	unique value	unique values	unique values	1	time of day with time zone with multiplicity	time of day with time zone	
ff	unique values of <time of day>: time of day with multiplicity	unique value	unique values	unique values	1	time of day with multiplicity	time of day	
ff	unique values of <time range>: time range with multiplicity	unique value	unique values	unique values	1	time range with multiplicity	time range	
ff	unique values of <time zone>: time zone with multiplicity	unique value	unique values	unique values	1	time zone with multiplicity	time zone	
ff	unique values of <time>: time with multiplicity	unique value	unique values	unique values	1	time with multiplicity	time	
5a	unique values of <uinteger>: uinteger with multiplicity	unique value	unique values	unique values	1	uinteger with multiplicity	uinteger	
1f	unique values of <uuid>: uuid with multiplicity
ff	unique values of <version>: version with multiplicity	unique value	unique values	unique values	1	version with multiplicity	version	
ff	unique values of <year>: year with multiplicity	unique value	unique values	unique values	1	year with multiplicity	year	
ff	universal time <string>: time	universal time	universal times	universal time	0	time		string
ff	universal time zone: time zone	universal time zone	universal time zones	universal time zone	0	time zone		
1f	unix of <operating system>: boolean
e0	unknown computer count of <bes baseline component>: integer	unknown computer count	unknown computer counts	unknown computer count	0	integer	bes baseline component	
e0	unknown computer set of <bes baseline component>: bes computer set	unknown computer set	unknown computer sets	unknown computer set	0	bes computer set	bes baseline component	
10	unknown state of <running task>: boolean
10	unknown state of <scheduled task>: boolean
e0	unlocked computer count of <bes fixlet>: integer	unlocked computer count	unlocked computer counts	unlocked computer count	0	integer	bes fixlet	
e0	unmanagedasset flag of <bes filter>: boolean	unmanagedasset flag	unmanagedasset flags	unmanagedasset flag	0	boolean	bes filter	
e0	unmanagedasset privilege scanpoint flag of <bes role>: boolean	unmanagedasset privilege scanpoint flag	unmanagedasset privilege scanpoint flags	unmanagedasset privilege scanpoint flag	0	boolean	bes role	
e0	unmanagedasset privilege scanpoint flag of <bes user>: boolean	unmanagedasset privilege scanpoint flag	unmanagedasset privilege scanpoint flags	unmanagedasset privilege scanpoint flag	0	boolean	bes user	
e0	unmanagedasset privilege showall flag of <bes role>: boolean	unmanagedasset privilege showall flag	unmanagedasset privilege showall flags	unmanagedasset privilege showall flag	0	boolean	bes role	
e0	unmanagedasset privilege showall flag of <bes user>: boolean	unmanagedasset privilege showall flag	unmanagedasset privilege showall flags	unmanagedasset privilege showall flag	0	boolean	bes user	
e0	unmanagedasset privilege shownone flag of <bes role>: boolean	unmanagedasset privilege shownone flag	unmanagedasset privilege shownone flags	unmanagedasset privilege shownone flag	0	boolean	bes role	
e0	unmanagedasset privilege shownone flag of <bes user>: boolean	unmanagedasset privilege shownone flag	unmanagedasset privilege shownone flags	unmanagedasset privilege shownone flag	0	boolean	bes user	
ff	unordered lists <string> of <html>: html	unordered list	unordered lists	unordered lists	1	html	html	string
ff	unordered lists <string> of <string>: html	unordered list	unordered lists	unordered lists	1	html	string	string
ff	unordered lists of <html>: html	unordered list	unordered lists	unordered lists	1	html	html	
ff	unordered lists of <string>: html	unordered list	unordered lists	unordered lists	1	html	string	
e0	untargeted flag of <bes action>: boolean	untargeted flag	untargeted flags	untargeted flag	0	boolean	bes action	
f	up flag of <route>: boolean
1f	up of <network adapter interface>: boolean
1f	up of <network adapter>: boolean
2	up of <network interface>: boolean
1f	up of <network ip interface>: boolean
d	update level of <operating system>: integer
1f	upload progress of <client>: string
10	upnp firewall service type: firewall service type
ff	upper bound of <integer range>: integer	upper bound	upper bounds	upper bound	0	integer	integer range	
1f	upper_threshold_critical of <dmi management_device_threshold_data>: integer
1f	upper_threshold_non_critical of <dmi management_device_threshold_data>: integer
1f	upper_threshold_non_recoverable of <dmi management_device_threshold_data>: integer
1f	ups of <power level>: boolean
9	upstream of <debian package version>: debian package upstream version
1f	uptime of <operating system>: time interval
e0	urgent flag of <bes action>: boolean	urgent flag	urgent flags	urgent flag	0	boolean	bes action	
10	uri of <task registration info>: string
e0	url of <bes server>: string	url	urls	url	0	string	bes server	
e0	url of <bes site>: string	url	urls	url	0	string	bes site	
e0	url of <bes wizard>: string	url	urls	url	0	string	bes wizard	
1f	url of <site>: string
2	usb plane of <registryroot>: registrynode
2	usb: usb
10	use count of <network share>: integer
10	use limit of <network share>: integer
1f	use of <dmi physical_memory_array>: integer
40	use ssl of <bes idp directory>: boolean	use ssl	use ssls	use ssl	0	boolean	bes idp directory	
e0	use ssl of <bes ldap directory>: boolean	use ssl	use ssls	use ssl	0	boolean	bes ldap directory	
1f	used amount of <ram>: integer
f	used amount of <swap>: integer
d	used file count of <filesystem>: integer
d	used percent of <filesystem>: integer
2	used percent of <volume>: integer
d	used space of <filesystem>: integer
2	used space of <volume>: integer
12	user <string>: user
10	user comment of <user>: string
5f	user count of <bes product>: integer	user count	user counts	user count	0	integer	bes product	
2	user domain: domain
d	user execute of <filesystem object>: boolean
40	user filter of <bes idp directory>: string	user filter	user filters	user filter	0	string	bes idp directory	
e0	user filter of <bes ldap directory>: string	user filter	user filters	user filter	0	string	bes ldap directory	
e0	user flag of <bes filter>: boolean	user flag	user flags	user flag	0	boolean	bes filter	
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
e0	user set of <bes filter>: bes user set	user set	user sets	user set	0	bes user set	bes filter	
e0	user set of <bes role>: bes user set	user set	user sets	user set	0	bes user set	bes role	
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
e0	users of <bes role>: bes user	user	users	users	1	bes user	bes role	
1f	users: user
ff	usual name of <property>: string	usual name	usual names	usual name	0	string	property	
e0	utc time flag of <bes action>: boolean	utc time flag	utc time flags	utc time flag	0	boolean	bes action	
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
e0	value count of <bes property result>: integer	value count	value counts	value count	0	integer	bes property result	
e0	value of <bes action parameter>: string	value	values	value	0	string	bes action parameter	
e0	value of <bes client setting>: string	value	values	value	0	string	bes client setting	
e0	value of <bes deployment option>: string	value	values	value	0	string	bes deployment option	
40	value of <bes tag>: string	value	values	value	0	string	bes tag	
e0	value of <bes unmanagedasset field>: string	value	values	value	0	string	bes unmanagedasset field	
e0	value of <bes wizard variable>: string	value	values	value	0	string	bes wizard variable	
2	value of <dictionaryentry>: osxvalue
b0	value of <distinguished name component>: string
1f	value of <environment variable>: string
1f	value of <fixlet_header>: string
ff	value of <json key>: json value	value	values	value	0	json value	json key	
e0	value of <mime field>: string	value	values	value	0	string	mime field	
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
e0	values of <bes fixlet field>: bes fixlet field value	value	values	values	1	bes fixlet field value	bes fixlet field	
e0	values of <bes property result>: string	value	values	values	1	string	bes property result	
10	values of <metabase key>: metabase value
10	values of <registry key>: registry key value
1f	values of <smbios structure>: smbios value
ff	var <string> of <html>: html	var	vars	var	0	html	html	string
ff	var <string> of <string>: html	var	vars	var	0	html	string	string
ff	var of <html>: html	var	vars	var	0	html	html	
ff	var of <string>: html	var	vars	var	0	html	string	
1f	variable <string> of <environment>: environment variable
10	variables <string> of <site profile>: site profile variable
e0	variables of <bes wizard>: bes wizard variable	variable	variables	variables	1	bes wizard variable	bes wizard	
1f	variables of <environment>: environment variable
1f	variables of <file>: string
10	variables of <site profile>: site profile variable
e0	variance of <statistical bin>: floating point	variance	variances	variance	0	floating point	statistical bin	
1f	vendor name of <processor>: string
1f	vendor of <dmi bios_information>: string
2	vendor of <scsidevice>: string
1f	vendor_syndrome of <dmi b32_bit_memory_error_information>: integer
1f	vendor_syndrome of <dmi b64_bit_memory_error_information>: integer
9	verfiles of <debian versioned package>: debianpkg verfile
2	version <integer> of <file>: version
ff	version <string>: version	version	versions	version	0	version		string
10	version block <integer> of <file>: file version block
10	version block <string> of <file>: file version block
10	version blocks of <file>: file version block
1f	version info of <execution>: string
1f	version of <application usage summary instance>: version
e0	version of <bes site>: integer	version	versions	version	0	integer	bes site	
1f	version of <bios>: string
2	version of <bundle>: version
4	version of <capability>: string
f	version of <client>: version
1f	version of <cloud provider>: string
2	version of <component>: version
ff	version of <cryptography>: string	version	versions	version	0	string	cryptography	
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
ff	version of <module>: version	version	versions	version	0	version	module	
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
ff	version of <x509 certificate>: integer	version	versions	version	0	integer	x509 certificate	
ff	version string <string> of <module>: string	version string	version strings	version string	0	string	module	string
10	version strings of <bios>: string
1f	virtual machine of <operating system>: boolean
2	virtual memory: boolean
1f	virtual of <hardware>: boolean
10	virtualizer of <application>: string
e0	visible flag of <bes fixlet>: boolean	visible flag	visible flags	visible flag	0	boolean	bes fixlet	
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
e0	webui enabled: boolean	webui enabled	webuis enabled	webui enabled	0	boolean		
1d	webui service: service
ff	wednesday: day of week	wednesday	wednesdays	wednesday	0	day of week		
ff	week: time interval	week	weeks	week	0	time interval		
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
f0	windows display time <string>: time	windows display time	windows display times	windows display time	0	time		string
10	windows file <string>: file
10	windows folder: folder
1f	windows of <operating system>: boolean
ff	windows server count of <bes product>: integer	windows server count	windows server counts	windows server count	0	integer	bes product	
10	winrt package <string>: winrt package
10	winrt package users of <winrt package>: winrt package user information
10	winrt packages of <user>: winrt package
10	winrt packages: winrt package
10	wins enabled of <network adapter>: boolean
10	winsock2 supported of <network>: boolean
e0	wizard data of <bes fixlet>: html	wizard data	wizard datas	wizard data	0	html	bes fixlet	
e0	wizard link of <bes fixlet>: string	wizard link	wizard links	wizard link	0	string	bes fixlet	
e0	wizard name of <bes fixlet>: string	wizard name	wizard names	wizard name	0	string	bes fixlet	
e0	wizard of <bes wizard variable>: bes wizard	wizard	wizards	wizard	0	bes wizard	bes wizard variable	
e0	wizard set of <bes site>: bes wizard set	wizard set	wizard sets	wizard set	0	bes wizard set	bes site	
e0	wizards of <bes site>: bes wizard	wizard	wizards	wizards	1	bes wizard	bes site	
10	wmi <string>: wmi
10	wmi: wmi
10	working directory of <exec task action>: string
10	working set size of <process>: integer
ff	workstation count of <bes product>: integer	workstation count	workstation counts	workstation count	0	integer	bes product	
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
e0	writer set of <bes site>: bes user set	writer set	writer sets	writer set	0	bes user set	bes site	
e0	writers of <bes site>: bes user	writer	writers	writers	1	bes user	bes site	
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
ff	year <integer>: year	year	years	year	0	year		integer
ff	year <string>: year	year	years	year	0	year		string
ff	year of <date>: year	year	years	year	0	year	date	
ff	year of <month and year>: year	year	years	year	0	year	month and year	
ff	year: number of months	year	years	year	0	number of months		
ff	zone of <time of day with time zone>: time zone	zone	zones	zone	0	time zone	time of day with time zone	
ff	zoned time_of_day <string>: time of day with time zone	zoned time_of_day	zoned times_of_day	zoned time_of_day	0	time of day with time zone		string
"""

# 428 rows
TYPES: str = """\
40			1
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
40	bes action		16
40	bes action parameter		192
40	bes action result		24
40	bes action set		24
40	bes action status		4
40	bes action with multiplicity	bes action	24
40	bes activation		16
40	bes baseline component		40
40	bes baseline component group		40
40	bes client setting		8
40	bes comment		16
40	bes computer		8
40	bes computer group		24
40	bes computer group set		24
40	bes computer group with multiplicity	bes computer group	32
40	bes computer set		24
40	bes computer with multiplicity	bes computer	16
40	bes deployment option		200
40	bes domain		16
40	bes domain set		24
40	bes domain with multiplicity	bes domain	24
40	bes filter		24
40	bes filter set		24
40	bes filter with multiplicity	bes filter	32
40	bes fixlet		24
40	bes fixlet action		608
40	bes fixlet field		136
40	bes fixlet field value		24
40	bes fixlet result		24
40	bes fixlet set		24
40	bes fixlet with multiplicity	bes fixlet	32
40	bes idp directory		16
40	bes idp directory server		8
40	bes idp directory set		24
40	bes idp directory with multiplicity	bes idp directory	24
40	bes ldap directory		16
40	bes ldap directory server		8
40	bes ldap directory set		24
40	bes ldap directory with multiplicity	bes ldap directory	24
40	bes peer download		448
40	bes peer download with multiplicity	bes peer download	456
52	bes product		8
40	bes property		24
40	bes property result		40
40	bes property set		24
40	bes property with multiplicity	bes property	32
40	bes role		16
40	bes role set		24
40	bes role with multiplicity	bes role	24
40	bes server		104
40	bes site		264
40	bes site file		216
40	bes site file set		24
40	bes site file with multiplicity	bes site file	224
40	bes site set		24
40	bes site with multiplicity	bes site	272
40	bes tag		16
40	bes unmanagedasset		16
40	bes unmanagedasset field		112
40	bes unmanagedasset set		24
40	bes unmanagedasset with multiplicity	bes unmanagedasset	24
40	bes user		112
40	bes user set		24
40	bes user with multiplicity	bes user	120
40	bes wakeonlan status		8
40	bes webui		1
40	bes webui app		112
40	bes webui app set		24
40	bes webui app with multiplicity	bes webui app	120
40	bes wizard		232
40	bes wizard set		24
40	bes wizard variable		240
40	bes wizard with multiplicity	bes wizard	240
52	binary operator		8
52	binary position	integer	144
52	binary_string		136
52	binary_substring	binary_string	136
12	bios
52	bit set		8
52	boolean		1
10	boot task trigger
2	bundle
52	cast		8
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
52	cryptography		24
12	current relay
10	daily task trigger
2	datafork
52	date		24
52	date with multiplicity	date	32
52	day of month		8
52	day of month with multiplicity	day of month	16
52	day of week		4
52	day of week with multiplicity	day of week	16
52	day of year		16
52	day of year with multiplicity	day of year	24
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
42	exponential projection		32
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
40	fixlet count pair		104
12	fixlet_header
52	floating point		24
52	floating point with multiplicity	floating point	32
12	folder
52	format		128
12	hardware
52	hertz		8
52	hertz with multiplicity	hertz	16
40	historical computer count		24
40	historical fixlet count		64
52	html		160
52	html attribute list		16
10	idle task trigger
12	instance data
52	integer		8
52	integer range		16
52	integer set		24
52	integer with multiplicity	integer	16
10	internet connection firewall
10	internet protocol
52	ip version		4
52	ipv4 address	ipv4or6 address	28
52	ipv4 address with multiplicity	ipv4 address	40
52	ipv4or6 address		28
52	ipv4or6 address with multiplicity	ipv4or6 address	40
52	ipv6 address	ipv4or6 address	28
52	ipv6 address with multiplicity	ipv6 address	40
52	json key		160
52	json value		16
10	language
52	large integer		24
52	large integer with multiplicity	large integer	32
52	license		2016
42	linear projection		32
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
40	mime field		8
52	module		8
12	monitor power interval
52	month		4
52	month and year		16
52	month and year with multiplicity	month and year	24
52	month with multiplicity	month	16
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
52	number of months		8
52	number of months with multiplicity	number of months	16
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
52	property		8
12	ram
42	rate		24
42	rate with multiplicity	rate	32
12	registration server
10	registration task trigger
10	registry
10	registry key
10	registry key value
10	registry key value type
2	registrynode
2	registryroot
52	regular expression		8
52	regular expression match	substring	152
2	resfork
12	restricted site
12	root server
52	rope		160
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
52	site version list		512
52	site version list with multiplicity	site version list	520
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
40	statistic range		16
40	statistical bin		240
52	string		144
52	string position	integer	152
52	string set		24
52	string with multiplicity	string	152
40	strverscmp version	version	32
52	substring	string	144
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
52	time		8
52	time interval		8
52	time interval with multiplicity	time interval	16
52	time of day		8
52	time of day with multiplicity	time of day	16
52	time of day with time zone		16
52	time of day with time zone with multiplicity	time of day with time zone	24
52	time range		16
52	time range with multiplicity	time range	24
10	time task trigger
52	time with multiplicity	time	16
52	time zone		8
52	time zone with multiplicity	time zone	16
52	tuple item		152
52	type		8
52	uinteger		8
52	uinteger with multiplicity	uinteger	16
52	unary operator		8
52	undefined		1
2	usb
12	user
2	user attribute
52	utf8 string		16
12	uuid
12	uuid with multiplicity
52	version		32
52	version with multiplicity	version	40
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
52	x509 certificate		712
10	xml dom document
10	xml dom node
2	yaml key
2	yaml value
52	year		8
52	year with multiplicity	year	16
"""

# 7 rows
UNARY_OPERATORS: str = """\
52	- <floating point>: floating point	minus	-	floating point	floating point
52	- <hertz>: hertz	minus	-	hertz	hertz
52	- <integer>: integer	minus	-	integer	integer
52	- <large integer>: large integer	minus	-	large integer	large integer
52	- <number of months>: number of months	minus	-	number of months	number of months
42	- <rate>: rate	minus	-	rate	rate
52	- <time interval>: time interval	minus	-	time interval	time interval
"""
