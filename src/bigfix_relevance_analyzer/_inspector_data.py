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

# 599 rows
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
5f	<binary_string> & <binary_string>: binary_string	concatenate	&	binary_string	binary_string	binary_string
5f	<binary_string> < <binary_string>: boolean	less than	<	binary_string	binary_string	boolean
5f	<binary_string> <= <binary_string>: boolean	less than or equal	<=	binary_string	binary_string	boolean
5f	<binary_string> = <binary_string>: boolean	equal	=	binary_string	binary_string	boolean
5f	<binary_string> contains <binary_string>: boolean	contains	contains	binary_string	binary_string	boolean
5f	<binary_string> ends with <binary_string>: boolean	ends with	ends with	binary_string	binary_string	boolean
5f	<binary_string> starts with <binary_string>: boolean	starts with	starts with	binary_string	binary_string	boolean
5f	<bit set> * <bit set>: bit set	times	*	bit set	bit set	bit set
5f	<bit set> + <bit set>: bit set	plus	+	bit set	bit set	bit set
5f	<bit set> - <bit set>: bit set	minus	-	bit set	bit set	bit set
5f	<bit set> = <bit set>: boolean	equal	=	bit set	bit set	boolean
5f	<bit set> contains <bit set>: boolean	contains	contains	bit set	bit set	boolean
5f	<boolean> * <time range>: timed( time range, boolean )	times	*	boolean	time range	timed( time range, boolean )
5f	<boolean> = <boolean>: boolean	equal	=	boolean	boolean	boolean
4	<capability> contains <capability>: boolean	contains	contains	capability	capability	boolean
1f	<cidr subnet> = <cidr subnet>: boolean	equal	=	cidr subnet	cidr subnet	boolean
1f	<cidr subnet> = <string>: boolean	equal	=	cidr subnet	string	boolean
1f	<cidr subnet> contains <cidr subnet>: boolean	contains	contains	cidr subnet	cidr subnet	boolean
1f	<cidr subnet> contains <ipv4 address>: boolean	contains	contains	cidr subnet	ipv4 address	boolean
1f	<cidr subnet> contains <ipv4or6 address>: boolean	contains	contains	cidr subnet	ipv4or6 address	boolean
1f	<cidr subnet> contains <ipv6 address>: boolean	contains	contains	cidr subnet	ipv6 address	boolean
10	<connection status> = <connection status>: boolean	equal	=	connection status	connection status	boolean
2	<country> = <country>: boolean	equal	=	country	country	boolean
5f	<date> & <time of day with time zone>: time	concatenate	&	date	time of day with time zone	time
5f	<date> + <number of months>: date	plus	+	date	number of months	date
5f	<date> + <time interval>: date	plus	+	date	time interval	date
5f	<date> - <date>: time interval	minus	-	date	date	time interval
5f	<date> - <number of months>: date	minus	-	date	number of months	date
5f	<date> - <time interval>: date	minus	-	date	time interval	date
5f	<date> < <date>: boolean	less than	<	date	date	boolean
5f	<date> <= <date>: boolean	less than or equal	<=	date	date	boolean
5f	<date> = <date>: boolean	equal	=	date	date	boolean
5f	<day of month> & <month and year>: date	concatenate	&	day of month	month and year	date
5f	<day of month> & <month>: day of year	concatenate	&	day of month	month	day of year
5f	<day of month> + <time interval>: day of month	plus	+	day of month	time interval	day of month
5f	<day of month> - <day of month>: time interval	minus	-	day of month	day of month	time interval
5f	<day of month> - <time interval>: day of month	minus	-	day of month	time interval	day of month
5f	<day of month> < <day of month>: boolean	less than	<	day of month	day of month	boolean
5f	<day of month> <= <day of month>: boolean	less than or equal	<=	day of month	day of month	boolean
5f	<day of month> = <day of month>: boolean	equal	=	day of month	day of month	boolean
5f	<day of week> + <time interval>: day of week	plus	+	day of week	time interval	day of week
5f	<day of week> - <day of week>: time interval	minus	-	day of week	day of week	time interval
5f	<day of week> - <time interval>: day of week	minus	-	day of week	time interval	day of week
5f	<day of week> = <day of week>: boolean	equal	=	day of week	day of week	boolean
5f	<day of year> & <month and year>: date	concatenate	&	day of year	month and year	date
5f	<day of year> & <year>: date	concatenate	&	day of year	year	date
5f	<day of year> + <number of months>: day of year	plus	+	day of year	number of months	day of year
5f	<day of year> + <time interval>: day of year	plus	+	day of year	time interval	day of year
5f	<day of year> - <day of year>: time interval	minus	-	day of year	day of year	time interval
5f	<day of year> - <number of months>: day of year	minus	-	day of year	number of months	day of year
5f	<day of year> - <time interval>: day of year	minus	-	day of year	time interval	day of year
5f	<day of year> < <day of year>: boolean	less than	<	day of year	day of year	boolean
5f	<day of year> <= <day of year>: boolean	less than or equal	<=	day of year	day of year	boolean
5f	<day of year> = <day of year>: boolean	equal	=	day of year	day of year	boolean
9	<debian package upstream version> < <debian package upstream version>: boolean	less than	<	debian package upstream version	debian package upstream version	boolean
9	<debian package upstream version> < <string>: boolean	less than	<	debian package upstream version	string	boolean
9	<debian package upstream version> <= <debian package upstream version>: boolean	less than or equal	<=	debian package upstream version	debian package upstream version	boolean
9	<debian package upstream version> <= <string>: boolean	less than or equal	<=	debian package upstream version	string	boolean
9	<debian package upstream version> = <debian package upstream version>: boolean	equal	=	debian package upstream version	debian package upstream version	boolean
9	<debian package upstream version> = <string>: boolean	equal	=	debian package upstream version	string	boolean
9	<debian package version epoch> < <debian package version epoch>: boolean	less than	<	debian package version epoch	debian package version epoch	boolean
9	<debian package version epoch> < <string>: boolean	less than	<	debian package version epoch	string	boolean
9	<debian package version epoch> <= <debian package version epoch>: boolean	less than or equal	<=	debian package version epoch	debian package version epoch	boolean
9	<debian package version epoch> <= <string>: boolean	less than or equal	<=	debian package version epoch	string	boolean
9	<debian package version epoch> = <debian package version epoch>: boolean	equal	=	debian package version epoch	debian package version epoch	boolean
9	<debian package version epoch> = <string>: boolean	equal	=	debian package version epoch	string	boolean
9	<debian package version revision> < <debian package version revision>: boolean	less than	<	debian package version revision	debian package version revision	boolean
9	<debian package version revision> < <string>: boolean	less than	<	debian package version revision	string	boolean
9	<debian package version revision> <= <debian package version revision>: boolean	less than or equal	<=	debian package version revision	debian package version revision	boolean
9	<debian package version revision> <= <string>: boolean	less than or equal	<=	debian package version revision	string	boolean
9	<debian package version revision> = <debian package version revision>: boolean	equal	=	debian package version revision	debian package version revision	boolean
9	<debian package version revision> = <string>: boolean	equal	=	debian package version revision	string	boolean
9	<debian package version> < <debian package version>: boolean	less than	<	debian package version	debian package version	boolean
9	<debian package version> < <string>: boolean	less than	<	debian package version	string	boolean
9	<debian package version> <= <debian package version>: boolean	less than or equal	<=	debian package version	debian package version	boolean
9	<debian package version> <= <string>: boolean	less than or equal	<=	debian package version	string	boolean
9	<debian package version> = <debian package version>: boolean	equal	=	debian package version	debian package version	boolean
9	<debian package version> = <string>: boolean	equal	=	debian package version	string	boolean
10	<event log event type> = <event log event type>: boolean	equal	=	event log event type	event log event type	boolean
1f	<file content> contains <string>: boolean	contains	contains	file content	string	boolean
2	<file signature> = <file signature>: boolean	equal	=	file signature	file signature	boolean
2	<file type> = <file type>: boolean	equal	=	file type	file type	boolean
12	<firewall action> = <firewall action>: boolean	equal	=	firewall action	firewall action	boolean
10	<firewall local policy modify state> = <firewall local policy modify state>: boolean	equal	=	firewall local policy modify state	firewall local policy modify state	boolean
10	<firewall profile type> = <firewall profile type>: boolean	equal	=	firewall profile type	firewall profile type	boolean
10	<firewall scope> = <firewall scope>: boolean	equal	=	firewall scope	firewall scope	boolean
10	<firewall service type> = <firewall service type>: boolean	equal	=	firewall service type	firewall service type	boolean
5f	<floating point> * <floating point>: floating point	times	*	floating point	floating point	floating point
5f	<floating point> * <integer>: floating point	times	*	floating point	integer	floating point
42	<floating point> * <rate>: rate	times	*	floating point	rate	rate
5f	<floating point> + <floating point>: floating point	plus	+	floating point	floating point	floating point
5f	<floating point> + <integer>: floating point	plus	+	floating point	integer	floating point
5f	<floating point> - <floating point>: floating point	minus	-	floating point	floating point	floating point
5f	<floating point> - <integer>: floating point	minus	-	floating point	integer	floating point
5f	<floating point> / <floating point>: floating point	divide	/	floating point	floating point	floating point
5f	<floating point> / <integer>: floating point	divide	/	floating point	integer	floating point
42	<floating point> / <time interval>: rate	divide	/	floating point	time interval	rate
5f	<floating point> < <floating point>: boolean	less than	<	floating point	floating point	boolean
5f	<floating point> < <integer>: boolean	less than	<	floating point	integer	boolean
5f	<floating point> <= <floating point>: boolean	less than or equal	<=	floating point	floating point	boolean
5f	<floating point> <= <integer>: boolean	less than or equal	<=	floating point	integer	boolean
5f	<floating point> = <floating point>: boolean	equal	=	floating point	floating point	boolean
5f	<floating point> = <integer>: boolean	equal	=	floating point	integer	boolean
5f	<format> + <date>: format	plus	+	format	date	format
5f	<format> + <day of week>: format	plus	+	format	day of week	format
5f	<format> + <format>: format	plus	+	format	format	format
5f	<format> + <integer>: format	plus	+	format	integer	format
5f	<format> + <string>: format	plus	+	format	string	format
5f	<format> + <time interval>: format	plus	+	format	time interval	format
5f	<format> + <time of day>: format	plus	+	format	time of day	format
5f	<format> + <time>: format	plus	+	format	time	format
52	<hertz> % <hertz>: hertz	mod	%	hertz	hertz	hertz
d	<hertz> %25 <hertz>: hertz	mod	%25	hertz	hertz	hertz
5f	<hertz> * <integer>: hertz	times	*	hertz	integer	hertz
5f	<hertz> + <hertz>: hertz	plus	+	hertz	hertz	hertz
5f	<hertz> - <hertz>: hertz	minus	-	hertz	hertz	hertz
5f	<hertz> / <hertz>: integer	divide	/	hertz	hertz	integer
5f	<hertz> / <integer>: hertz	divide	/	hertz	integer	hertz
5f	<hertz> < <hertz>: boolean	less than	<	hertz	hertz	boolean
5f	<hertz> <= <hertz>: boolean	less than or equal	<=	hertz	hertz	boolean
5f	<hertz> = <hertz>: boolean	equal	=	hertz	hertz	boolean
5f	<html> & <html>: html	concatenate	&	html	html	html
5f	<html> & <string>: html	concatenate	&	html	string	html
5f	<integer set> * <integer set>: integer set	times	*	integer set	integer set	integer set
5f	<integer set> + <integer set>: integer set	plus	+	integer set	integer set	integer set
5f	<integer set> - <integer set>: integer set	minus	-	integer set	integer set	integer set
5f	<integer set> = <integer set>: boolean	equal	=	integer set	integer set	boolean
5f	<integer set> contains <integer set>: boolean	contains	contains	integer set	integer set	boolean
5f	<integer set> contains <integer>: boolean	contains	contains	integer set	integer	boolean
52	<integer> % <integer>: integer	mod	%	integer	integer	integer
52	<integer> % <large integer>: large integer	mod	%	integer	large integer	large integer
52	<integer> % <uinteger>: uinteger	mod	%	integer	uinteger	uinteger
d	<integer> %25 <integer>: integer	mod	%25	integer	integer	integer
d	<integer> %25 <large integer>: large integer	mod	%25	integer	large integer	large integer
d	<integer> %25 <uinteger>: uinteger	mod	%25	integer	uinteger	uinteger
5f	<integer> * <floating point>: floating point	times	*	integer	floating point	floating point
5f	<integer> * <hertz>: hertz	times	*	integer	hertz	hertz
5f	<integer> * <integer>: integer	times	*	integer	integer	integer
5f	<integer> * <large integer>: large integer	times	*	integer	large integer	large integer
5f	<integer> * <number of months>: number of months	times	*	integer	number of months	number of months
5f	<integer> * <time interval>: time interval	times	*	integer	time interval	time interval
5f	<integer> * <time range>: timed( time range, integer )	times	*	integer	time range	timed( time range, integer )
5f	<integer> * <uinteger>: uinteger	times	*	integer	uinteger	uinteger
5f	<integer> + <floating point>: floating point	plus	+	integer	floating point	floating point
5f	<integer> + <integer>: integer	plus	+	integer	integer	integer
5f	<integer> + <large integer>: large integer	plus	+	integer	large integer	large integer
5f	<integer> + <uinteger>: uinteger	plus	+	integer	uinteger	uinteger
5f	<integer> - <floating point>: floating point	minus	-	integer	floating point	floating point
5f	<integer> - <integer>: integer	minus	-	integer	integer	integer
5f	<integer> - <large integer>: large integer	minus	-	integer	large integer	large integer
5f	<integer> - <uinteger>: uinteger	minus	-	integer	uinteger	uinteger
5f	<integer> / <floating point>: floating point	divide	/	integer	floating point	floating point
5f	<integer> / <integer>: integer	divide	/	integer	integer	integer
5f	<integer> / <large integer>: large integer	divide	/	integer	large integer	large integer
5f	<integer> / <uinteger>: uinteger	divide	/	integer	uinteger	uinteger
5f	<integer> < <floating point>: boolean	less than	<	integer	floating point	boolean
5f	<integer> < <integer>: boolean	less than	<	integer	integer	boolean
5f	<integer> < <large integer>: boolean	less than	<	integer	large integer	boolean
10	<integer> < <registry key value type>: boolean	less than	<	integer	registry key value type	boolean
10	<integer> < <registry key value>: boolean	less than	<	integer	registry key value	boolean
5f	<integer> < <uinteger>: boolean	less than	<	integer	uinteger	boolean
5f	<integer> <= <floating point>: boolean	less than or equal	<=	integer	floating point	boolean
5f	<integer> <= <integer>: boolean	less than or equal	<=	integer	integer	boolean
5f	<integer> <= <large integer>: boolean	less than or equal	<=	integer	large integer	boolean
10	<integer> <= <registry key value type>: boolean	less than or equal	<=	integer	registry key value type	boolean
10	<integer> <= <registry key value>: boolean	less than or equal	<=	integer	registry key value	boolean
5f	<integer> <= <uinteger>: boolean	less than or equal	<=	integer	uinteger	boolean
5f	<integer> = <floating point>: boolean	equal	=	integer	floating point	boolean
5f	<integer> = <integer>: boolean	equal	=	integer	integer	boolean
5f	<integer> = <large integer>: boolean	equal	=	integer	large integer	boolean
10	<integer> = <registry key value type>: boolean	equal	=	integer	registry key value type	boolean
10	<integer> = <registry key value>: boolean	equal	=	integer	registry key value	boolean
5f	<integer> = <uinteger>: boolean	equal	=	integer	uinteger	boolean
10	<internet protocol> = <internet protocol>: boolean	equal	=	internet protocol	internet protocol	boolean
5f	<ip version> = <ip version>: boolean	equal	=	ip version	ip version	boolean
5f	<ipv4 address> < <ipv4 address>: boolean	less than	<	ipv4 address	ipv4 address	boolean
5f	<ipv4 address> < <string>: boolean	less than	<	ipv4 address	string	boolean
5f	<ipv4 address> <= <ipv4 address>: boolean	less than or equal	<=	ipv4 address	ipv4 address	boolean
5f	<ipv4 address> <= <string>: boolean	less than or equal	<=	ipv4 address	string	boolean
5f	<ipv4 address> = <ipv4 address>: boolean	equal	=	ipv4 address	ipv4 address	boolean
5f	<ipv4 address> = <string>: boolean	equal	=	ipv4 address	string	boolean
5f	<ipv4or6 address> < <ipv4or6 address>: boolean	less than	<	ipv4or6 address	ipv4or6 address	boolean
5f	<ipv4or6 address> < <string>: boolean	less than	<	ipv4or6 address	string	boolean
5f	<ipv4or6 address> <= <ipv4or6 address>: boolean	less than or equal	<=	ipv4or6 address	ipv4or6 address	boolean
5f	<ipv4or6 address> <= <string>: boolean	less than or equal	<=	ipv4or6 address	string	boolean
5f	<ipv4or6 address> = <ipv4or6 address>: boolean	equal	=	ipv4or6 address	ipv4or6 address	boolean
5f	<ipv4or6 address> = <string>: boolean	equal	=	ipv4or6 address	string	boolean
5f	<ipv6 address> < <ipv6 address>: boolean	less than	<	ipv6 address	ipv6 address	boolean
5f	<ipv6 address> <= <ipv6 address>: boolean	less than or equal	<=	ipv6 address	ipv6 address	boolean
5f	<ipv6 address> = <ipv6 address>: boolean	equal	=	ipv6 address	ipv6 address	boolean
5f	<json key> = <json key>: boolean	equal	=	json key	json key	boolean
5f	<json value> = <json value>: boolean	equal	=	json value	json value	boolean
52	<large integer> % <integer>: large integer	mod	%	large integer	integer	large integer
52	<large integer> % <large integer>: large integer	mod	%	large integer	large integer	large integer
d	<large integer> %25 <integer>: large integer	mod	%25	large integer	integer	large integer
d	<large integer> %25 <large integer>: large integer	mod	%25	large integer	large integer	large integer
5f	<large integer> * <integer>: large integer	times	*	large integer	integer	large integer
5f	<large integer> * <large integer>: large integer	times	*	large integer	large integer	large integer
5f	<large integer> + <integer>: large integer	plus	+	large integer	integer	large integer
5f	<large integer> + <large integer>: large integer	plus	+	large integer	large integer	large integer
5f	<large integer> - <integer>: large integer	minus	-	large integer	integer	large integer
5f	<large integer> - <large integer>: large integer	minus	-	large integer	large integer	large integer
5f	<large integer> / <integer>: large integer	divide	/	large integer	integer	large integer
5f	<large integer> / <large integer>: large integer	divide	/	large integer	large integer	large integer
5f	<large integer> < <integer>: boolean	less than	<	large integer	integer	boolean
5f	<large integer> < <large integer>: boolean	less than	<	large integer	large integer	boolean
5f	<large integer> <= <integer>: boolean	less than or equal	<=	large integer	integer	boolean
5f	<large integer> <= <large integer>: boolean	less than or equal	<=	large integer	large integer	boolean
5f	<large integer> = <integer>: boolean	equal	=	large integer	integer	boolean
5f	<large integer> = <large integer>: boolean	equal	=	large integer	large integer	boolean
10	<media type> = <media type>: boolean	equal	=	media type	media type	boolean
10	<metabase identifier> = <metabase identifier>: boolean	equal	=	metabase identifier	metabase identifier	boolean
10	<metabase type> = <metabase type>: boolean	equal	=	metabase type	metabase type	boolean
10	<metabase user type> = <metabase user type>: boolean	equal	=	metabase user type	metabase user type	boolean
5f	<month and year> & <day of month>: date	concatenate	&	month and year	day of month	date
5f	<month and year> & <day of year>: date	concatenate	&	month and year	day of year	date
5f	<month and year> + <number of months>: month and year	plus	+	month and year	number of months	month and year
5f	<month and year> - <month and year>: number of months	minus	-	month and year	month and year	number of months
5f	<month and year> - <number of months>: month and year	minus	-	month and year	number of months	month and year
5f	<month and year> < <month and year>: boolean	less than	<	month and year	month and year	boolean
5f	<month and year> <= <month and year>: boolean	less than or equal	<=	month and year	month and year	boolean
5f	<month and year> = <month and year>: boolean	equal	=	month and year	month and year	boolean
5f	<month> & <day of month>: day of year	concatenate	&	month	day of month	day of year
5f	<month> & <year>: month and year	concatenate	&	month	year	month and year
5f	<month> + <number of months>: month	plus	+	month	number of months	month
5f	<month> - <month>: number of months	minus	-	month	month	number of months
5f	<month> - <number of months>: month	minus	-	month	number of months	month
5f	<month> < <month>: boolean	less than	<	month	month	boolean
5f	<month> <= <month>: boolean	less than or equal	<=	month	month	boolean
5f	<month> = <month>: boolean	equal	=	month	month	boolean
52	<number of months> % <number of months>: number of months	mod	%	number of months	number of months	number of months
d	<number of months> %25 <number of months>: number of months	mod	%25	number of months	number of months	number of months
5f	<number of months> * <integer>: number of months	times	*	number of months	integer	number of months
5f	<number of months> + <date>: date	plus	+	number of months	date	date
5f	<number of months> + <day of year>: day of year	plus	+	number of months	day of year	day of year
5f	<number of months> + <month and year>: month and year	plus	+	number of months	month and year	month and year
5f	<number of months> + <month>: month	plus	+	number of months	month	month
5f	<number of months> + <number of months>: number of months	plus	+	number of months	number of months	number of months
5f	<number of months> + <year>: year	plus	+	number of months	year	year
5f	<number of months> - <number of months>: number of months	minus	-	number of months	number of months	number of months
5f	<number of months> / <integer>: number of months	divide	/	number of months	integer	number of months
5f	<number of months> / <number of months>: integer	divide	/	number of months	number of months	integer
5f	<number of months> < <number of months>: boolean	less than	<	number of months	number of months	boolean
5f	<number of months> <= <number of months>: boolean	less than or equal	<=	number of months	number of months	boolean
5f	<number of months> = <number of months>: boolean	equal	=	number of months	number of months	boolean
10	<operating system product type> = <operating system product type>: boolean	equal	=	operating system product type	operating system product type	boolean
14	<plugin store key> = <plugin store key>: boolean	equal	=	plugin store key	plugin store key	boolean
14	<plugin store> = <plugin store>: boolean	equal	=	plugin store	plugin store	boolean
12	<power state> = <power state>: boolean	equal	=	power state	power state	boolean
10	<priority class> = <priority class>: boolean	equal	=	priority class	priority class	boolean
42	<rate> * <floating point>: rate	times	*	rate	floating point	rate
42	<rate> * <time interval>: floating point	times	*	rate	time interval	floating point
42	<rate> + <rate>: rate	plus	+	rate	rate	rate
42	<rate> - <rate>: rate	minus	-	rate	rate	rate
42	<rate> / <floating point>: rate	divide	/	rate	floating point	rate
42	<rate> < <rate>: boolean	less than	<	rate	rate	boolean
42	<rate> <= <rate>: boolean	less than or equal	<=	rate	rate	boolean
42	<rate> = <rate>: boolean	equal	=	rate	rate	boolean
10	<registry key value type> < <integer>: boolean	less than	<	registry key value type	integer	boolean
10	<registry key value type> < <registry key value type>: boolean	less than	<	registry key value type	registry key value type	boolean
10	<registry key value type> < <string>: boolean	less than	<	registry key value type	string	boolean
10	<registry key value type> <= <integer>: boolean	less than or equal	<=	registry key value type	integer	boolean
10	<registry key value type> <= <registry key value type>: boolean	less than or equal	<=	registry key value type	registry key value type	boolean
10	<registry key value type> <= <string>: boolean	less than or equal	<=	registry key value type	string	boolean
10	<registry key value type> = <integer>: boolean	equal	=	registry key value type	integer	boolean
10	<registry key value type> = <registry key value type>: boolean	equal	=	registry key value type	registry key value type	boolean
10	<registry key value type> = <string>: boolean	equal	=	registry key value type	string	boolean
10	<registry key value> < <integer>: boolean	less than	<	registry key value	integer	boolean
10	<registry key value> < <registry key value>: boolean	less than	<	registry key value	registry key value	boolean
10	<registry key value> < <string>: boolean	less than	<	registry key value	string	boolean
10	<registry key value> <= <integer>: boolean	less than or equal	<=	registry key value	integer	boolean
10	<registry key value> <= <registry key value>: boolean	less than or equal	<=	registry key value	registry key value	boolean
10	<registry key value> <= <string>: boolean	less than or equal	<=	registry key value	string	boolean
10	<registry key value> = <integer>: boolean	equal	=	registry key value	integer	boolean
10	<registry key value> = <registry key value>: boolean	equal	=	registry key value	registry key value	boolean
10	<registry key value> = <string>: boolean	equal	=	registry key value	string	boolean
5f	<regular expression> = <string>: boolean	equal	=	regular expression	string	boolean
5f	<rope> & <rope>: rope	concatenate	&	rope	rope	rope
5f	<rope> & <string>: rope	concatenate	&	rope	string	rope
5f	<rope> contains <string>: boolean	contains	contains	rope	string	boolean
4	<rpm package release> < <rpm package release>: boolean	less than	<	rpm package release	rpm package release	boolean
4	<rpm package release> < <string>: boolean	less than	<	rpm package release	string	boolean
4	<rpm package release> <= <rpm package release>: boolean	less than or equal	<=	rpm package release	rpm package release	boolean
4	<rpm package release> <= <string>: boolean	less than or equal	<=	rpm package release	string	boolean
4	<rpm package release> = <rpm package release>: boolean	equal	=	rpm package release	rpm package release	boolean
4	<rpm package release> = <string>: boolean	equal	=	rpm package release	string	boolean
4	<rpm package version record> < <rpm package version record>: boolean	less than	<	rpm package version record	rpm package version record	boolean
4	<rpm package version record> < <short rpm package version record>: boolean	less than	<	rpm package version record	short rpm package version record	boolean
4	<rpm package version record> < <string>: boolean	less than	<	rpm package version record	string	boolean
4	<rpm package version record> <= <rpm package version record>: boolean	less than or equal	<=	rpm package version record	rpm package version record	boolean
4	<rpm package version record> <= <short rpm package version record>: boolean	less than or equal	<=	rpm package version record	short rpm package version record	boolean
4	<rpm package version record> <= <string>: boolean	less than or equal	<=	rpm package version record	string	boolean
4	<rpm package version record> = <rpm package version record>: boolean	equal	=	rpm package version record	rpm package version record	boolean
4	<rpm package version record> = <short rpm package version record>: boolean	equal	=	rpm package version record	short rpm package version record	boolean
4	<rpm package version record> = <string>: boolean	equal	=	rpm package version record	string	boolean
4	<rpm package version> < <rpm package version>: boolean	less than	<	rpm package version	rpm package version	boolean
4	<rpm package version> < <string>: boolean	less than	<	rpm package version	string	boolean
4	<rpm package version> <= <rpm package version>: boolean	less than or equal	<=	rpm package version	rpm package version	boolean
4	<rpm package version> <= <string>: boolean	less than or equal	<=	rpm package version	string	boolean
4	<rpm package version> = <rpm package version>: boolean	equal	=	rpm package version	rpm package version	boolean
4	<rpm package version> = <string>: boolean	equal	=	rpm package version	string	boolean
12	<security identifier> = <security identifier>: boolean	equal	=	security identifier	security identifier	boolean
4	<short rpm package version record> < <rpm package version record>: boolean	less than	<	short rpm package version record	rpm package version record	boolean
4	<short rpm package version record> < <short rpm package version record>: boolean	less than	<	short rpm package version record	short rpm package version record	boolean
4	<short rpm package version record> <= <rpm package version record>: boolean	less than or equal	<=	short rpm package version record	rpm package version record	boolean
4	<short rpm package version record> <= <short rpm package version record>: boolean	less than or equal	<=	short rpm package version record	short rpm package version record	boolean
4	<short rpm package version record> = <rpm package version record>: boolean	equal	=	short rpm package version record	rpm package version record	boolean
4	<short rpm package version record> = <short rpm package version record>: boolean	equal	=	short rpm package version record	short rpm package version record	boolean
5f	<site version list> < <site version list>: boolean	less than	<	site version list	site version list	boolean
5f	<site version list> <= <site version list>: boolean	less than or equal	<=	site version list	site version list	boolean
5f	<site version list> = <site version list>: boolean	equal	=	site version list	site version list	boolean
5f	<site version list> contains <site version list>: boolean	contains	contains	site version list	site version list	boolean
2	<stage> = <stage>: boolean	equal	=	stage	stage	boolean
5f	<string set> * <string set>: string set	times	*	string set	string set	string set
5f	<string set> + <string set>: string set	plus	+	string set	string set	string set
5f	<string set> - <string set>: string set	minus	-	string set	string set	string set
5f	<string set> = <string set>: boolean	equal	=	string set	string set	boolean
5f	<string set> contains <string set>: boolean	contains	contains	string set	string set	boolean
5f	<string set> contains <string>: boolean	contains	contains	string set	string	boolean
5f	<string> & <html>: html	concatenate	&	string	html	html
5f	<string> & <rope>: rope	concatenate	&	string	rope	rope
5f	<string> & <string>: string	concatenate	&	string	string	string
9	<string> < <debian package upstream version>: boolean	less than	<	string	debian package upstream version	boolean
9	<string> < <debian package version epoch>: boolean	less than	<	string	debian package version epoch	boolean
9	<string> < <debian package version revision>: boolean	less than	<	string	debian package version revision	boolean
9	<string> < <debian package version>: boolean	less than	<	string	debian package version	boolean
5f	<string> < <ipv4 address>: boolean	less than	<	string	ipv4 address	boolean
5f	<string> < <ipv4or6 address>: boolean	less than	<	string	ipv4or6 address	boolean
10	<string> < <registry key value type>: boolean	less than	<	string	registry key value type	boolean
10	<string> < <registry key value>: boolean	less than	<	string	registry key value	boolean
4	<string> < <rpm package release>: boolean	less than	<	string	rpm package release	boolean
4	<string> < <rpm package version record>: boolean	less than	<	string	rpm package version record	boolean
4	<string> < <rpm package version>: boolean	less than	<	string	rpm package version	boolean
5f	<string> < <string>: boolean	less than	<	string	string	boolean
4d	<string> < <strverscmp version>: boolean	less than	<	string	strverscmp version	boolean
1f	<string> < <uuid>: boolean	less than	<	string	uuid	boolean
5f	<string> < <version>: boolean	less than	<	string	version	boolean
9	<string> <= <debian package upstream version>: boolean	less than or equal	<=	string	debian package upstream version	boolean
9	<string> <= <debian package version epoch>: boolean	less than or equal	<=	string	debian package version epoch	boolean
9	<string> <= <debian package version revision>: boolean	less than or equal	<=	string	debian package version revision	boolean
9	<string> <= <debian package version>: boolean	less than or equal	<=	string	debian package version	boolean
5f	<string> <= <ipv4 address>: boolean	less than or equal	<=	string	ipv4 address	boolean
5f	<string> <= <ipv4or6 address>: boolean	less than or equal	<=	string	ipv4or6 address	boolean
10	<string> <= <registry key value type>: boolean	less than or equal	<=	string	registry key value type	boolean
10	<string> <= <registry key value>: boolean	less than or equal	<=	string	registry key value	boolean
4	<string> <= <rpm package release>: boolean	less than or equal	<=	string	rpm package release	boolean
4	<string> <= <rpm package version record>: boolean	less than or equal	<=	string	rpm package version record	boolean
4	<string> <= <rpm package version>: boolean	less than or equal	<=	string	rpm package version	boolean
5f	<string> <= <string>: boolean	less than or equal	<=	string	string	boolean
4d	<string> <= <strverscmp version>: boolean	less than or equal	<=	string	strverscmp version	boolean
1f	<string> <= <uuid>: boolean	less than or equal	<=	string	uuid	boolean
5f	<string> <= <version>: boolean	less than or equal	<=	string	version	boolean
1f	<string> = <cidr subnet>: boolean	equal	=	string	cidr subnet	boolean
9	<string> = <debian package upstream version>: boolean	equal	=	string	debian package upstream version	boolean
9	<string> = <debian package version epoch>: boolean	equal	=	string	debian package version epoch	boolean
9	<string> = <debian package version revision>: boolean	equal	=	string	debian package version revision	boolean
9	<string> = <debian package version>: boolean	equal	=	string	debian package version	boolean
5f	<string> = <ipv4 address>: boolean	equal	=	string	ipv4 address	boolean
5f	<string> = <ipv4or6 address>: boolean	equal	=	string	ipv4or6 address	boolean
10	<string> = <registry key value type>: boolean	equal	=	string	registry key value type	boolean
10	<string> = <registry key value>: boolean	equal	=	string	registry key value	boolean
5f	<string> = <regular expression>: boolean	equal	=	string	regular expression	boolean
4	<string> = <rpm package release>: boolean	equal	=	string	rpm package release	boolean
4	<string> = <rpm package version record>: boolean	equal	=	string	rpm package version record	boolean
4	<string> = <rpm package version>: boolean	equal	=	string	rpm package version	boolean
5f	<string> = <string>: boolean	equal	=	string	string	boolean
4d	<string> = <strverscmp version>: boolean	equal	=	string	strverscmp version	boolean
1f	<string> = <uuid>: boolean	equal	=	string	uuid	boolean
5f	<string> = <version>: boolean	equal	=	string	version	boolean
5f	<string> contains <regular expression>: boolean	contains	contains	string	regular expression	boolean
5f	<string> contains <string>: boolean	contains	contains	string	string	boolean
5f	<string> ends with <regular expression>: boolean	ends with	ends with	string	regular expression	boolean
5f	<string> ends with <string>: boolean	ends with	ends with	string	string	boolean
5f	<string> starts with <regular expression>: boolean	starts with	starts with	string	regular expression	boolean
5f	<string> starts with <string>: boolean	starts with	starts with	string	string	boolean
4d	<strverscmp version> < <string>: boolean	less than	<	strverscmp version	string	boolean
4d	<strverscmp version> < <strverscmp version>: boolean	less than	<	strverscmp version	strverscmp version	boolean
4d	<strverscmp version> <= <string>: boolean	less than or equal	<=	strverscmp version	string	boolean
4d	<strverscmp version> <= <strverscmp version>: boolean	less than or equal	<=	strverscmp version	strverscmp version	boolean
4d	<strverscmp version> = <string>: boolean	equal	=	strverscmp version	string	boolean
4d	<strverscmp version> = <strverscmp version>: boolean	equal	=	strverscmp version	strverscmp version	boolean
10	<task action type> = <task action type>: boolean	equal	=	task action type	task action type	boolean
10	<task trigger type> = <task trigger type>: boolean	equal	=	task trigger type	task trigger type	boolean
52	<time interval> % <time interval>: time interval	mod	%	time interval	time interval	time interval
d	<time interval> %25 <time interval>: time interval	mod	%25	time interval	time interval	time interval
5f	<time interval> & <time>: time range	concatenate	&	time interval	time	time range
5f	<time interval> * <integer>: time interval	times	*	time interval	integer	time interval
42	<time interval> * <rate>: floating point	times	*	time interval	rate	floating point
5f	<time interval> + <date>: date	plus	+	time interval	date	date
5f	<time interval> + <day of month>: day of month	plus	+	time interval	day of month	day of month
5f	<time interval> + <day of week>: day of week	plus	+	time interval	day of week	day of week
5f	<time interval> + <day of year>: day of year	plus	+	time interval	day of year	day of year
5f	<time interval> + <time interval>: time interval	plus	+	time interval	time interval	time interval
5f	<time interval> + <time of day with time zone>: time of day with time zone	plus	+	time interval	time of day with time zone	time of day with time zone
5f	<time interval> + <time of day>: time of day	plus	+	time interval	time of day	time of day
5f	<time interval> + <time zone>: time zone	plus	+	time interval	time zone	time zone
5f	<time interval> + <time>: time	plus	+	time interval	time	time
5f	<time interval> - <time interval>: time interval	minus	-	time interval	time interval	time interval
5f	<time interval> / <integer>: time interval	divide	/	time interval	integer	time interval
5f	<time interval> / <time interval>: integer	divide	/	time interval	time interval	integer
5f	<time interval> < <time interval>: boolean	less than	<	time interval	time interval	boolean
5f	<time interval> <= <time interval>: boolean	less than or equal	<=	time interval	time interval	boolean
5f	<time interval> = <time interval>: boolean	equal	=	time interval	time interval	boolean
5f	<time of day with time zone> & <date>: time	concatenate	&	time of day with time zone	date	time
5f	<time of day with time zone> & <time zone>: time of day with time zone	concatenate	&	time of day with time zone	time zone	time of day with time zone
5f	<time of day with time zone> + <time interval>: time of day with time zone	plus	+	time of day with time zone	time interval	time of day with time zone
5f	<time of day with time zone> - <time interval>: time of day with time zone	minus	-	time of day with time zone	time interval	time of day with time zone
5f	<time of day with time zone> - <time of day with time zone>: time interval	minus	-	time of day with time zone	time of day with time zone	time interval
5f	<time of day with time zone> < <time of day with time zone>: boolean	less than	<	time of day with time zone	time of day with time zone	boolean
5f	<time of day with time zone> <= <time of day with time zone>: boolean	less than or equal	<=	time of day with time zone	time of day with time zone	boolean
5f	<time of day with time zone> = <time of day with time zone>: boolean	equal	=	time of day with time zone	time of day with time zone	boolean
5f	<time of day> & <time zone>: time of day with time zone	concatenate	&	time of day	time zone	time of day with time zone
5f	<time of day> + <time interval>: time of day	plus	+	time of day	time interval	time of day
5f	<time of day> - <time interval>: time of day	minus	-	time of day	time interval	time of day
5f	<time of day> - <time of day>: time interval	minus	-	time of day	time of day	time interval
5f	<time of day> < <time of day>: boolean	less than	<	time of day	time of day	boolean
5f	<time of day> <= <time of day>: boolean	less than or equal	<=	time of day	time of day	boolean
5f	<time of day> = <time of day>: boolean	equal	=	time of day	time of day	boolean
5f	<time range> & <time range>: time range	concatenate	&	time range	time range	time range
5f	<time range> & <time>: time range	concatenate	&	time range	time	time range
5f	<time range> * <boolean>: timed( time range, boolean )	times	*	time range	boolean	timed( time range, boolean )
5f	<time range> * <integer>: timed( time range, integer )	times	*	time range	integer	timed( time range, integer )
5f	<time range> * <time range>: time range	times	*	time range	time range	time range
5f	<time range> + <time range>: time range	plus	+	time range	time range	time range
5f	<time range> = <time range>: boolean	equal	=	time range	time range	boolean
5f	<time range> contains <time range>: boolean	contains	contains	time range	time range	boolean
5f	<time range> contains <time>: boolean	contains	contains	time range	time	boolean
5f	<time zone> & <time of day with time zone>: time of day with time zone	concatenate	&	time zone	time of day with time zone	time of day with time zone
5f	<time zone> & <time of day>: time of day with time zone	concatenate	&	time zone	time of day	time of day with time zone
5f	<time zone> + <time interval>: time zone	plus	+	time zone	time interval	time zone
5f	<time zone> - <time interval>: time zone	minus	-	time zone	time interval	time zone
5f	<time zone> - <time zone>: time interval	minus	-	time zone	time zone	time interval
5f	<time zone> = <time zone>: boolean	equal	=	time zone	time zone	boolean
5f	<time> & <time interval>: time range	concatenate	&	time	time interval	time range
5f	<time> & <time range>: time range	concatenate	&	time	time range	time range
5f	<time> & <time>: time range	concatenate	&	time	time	time range
5f	<time> + <time interval>: time	plus	+	time	time interval	time
5f	<time> - <time interval>: time	minus	-	time	time interval	time
5f	<time> - <time>: time interval	minus	-	time	time	time interval
5f	<time> < <time>: boolean	less than	<	time	time	boolean
5f	<time> <= <time>: boolean	less than or equal	<=	time	time	boolean
5f	<time> = <time>: boolean	equal	=	time	time	boolean
5f	<type> = <type>: boolean	equal	=	type	type	boolean
52	<uinteger> % <integer>: uinteger	mod	%	uinteger	integer	uinteger
52	<uinteger> % <uinteger>: uinteger	mod	%	uinteger	uinteger	uinteger
d	<uinteger> %25 <integer>: uinteger	mod	%25	uinteger	integer	uinteger
d	<uinteger> %25 <uinteger>: uinteger	mod	%25	uinteger	uinteger	uinteger
5f	<uinteger> * <integer>: uinteger	times	*	uinteger	integer	uinteger
5f	<uinteger> * <uinteger>: uinteger	times	*	uinteger	uinteger	uinteger
5f	<uinteger> + <integer>: uinteger	plus	+	uinteger	integer	uinteger
5f	<uinteger> + <uinteger>: uinteger	plus	+	uinteger	uinteger	uinteger
5f	<uinteger> - <integer>: uinteger	minus	-	uinteger	integer	uinteger
5f	<uinteger> - <uinteger>: uinteger	minus	-	uinteger	uinteger	uinteger
5f	<uinteger> / <integer>: uinteger	divide	/	uinteger	integer	uinteger
5f	<uinteger> / <uinteger>: uinteger	divide	/	uinteger	uinteger	uinteger
5f	<uinteger> < <integer>: boolean	less than	<	uinteger	integer	boolean
5f	<uinteger> < <uinteger>: boolean	less than	<	uinteger	uinteger	boolean
5f	<uinteger> <= <integer>: boolean	less than or equal	<=	uinteger	integer	boolean
5f	<uinteger> <= <uinteger>: boolean	less than or equal	<=	uinteger	uinteger	boolean
5f	<uinteger> = <integer>: boolean	equal	=	uinteger	integer	boolean
5f	<uinteger> = <uinteger>: boolean	equal	=	uinteger	uinteger	boolean
1f	<uuid> < <string>: boolean	less than	<	uuid	string	boolean
1f	<uuid> < <uuid>: boolean	less than	<	uuid	uuid	boolean
1f	<uuid> <= <string>: boolean	less than or equal	<=	uuid	string	boolean
1f	<uuid> <= <uuid>: boolean	less than or equal	<=	uuid	uuid	boolean
1f	<uuid> = <string>: boolean	equal	=	uuid	string	boolean
1f	<uuid> = <uuid>: boolean	equal	=	uuid	uuid	boolean
5f	<version> < <string>: boolean	less than	<	version	string	boolean
5f	<version> < <version>: boolean	less than	<	version	version	boolean
5f	<version> <= <string>: boolean	less than or equal	<=	version	string	boolean
5f	<version> <= <version>: boolean	less than or equal	<=	version	version	boolean
5f	<version> = <string>: boolean	equal	=	version	string	boolean
5f	<version> = <version>: boolean	equal	=	version	version	boolean
2	<volume> = <volume>: boolean	equal	=	volume	volume	boolean
1f	<yaml key> = <yaml key>: boolean	equal	=	yaml key	yaml key	boolean
1f	<yaml value> = <yaml value>: boolean	equal	=	yaml value	yaml value	boolean
5f	<year> & <day of year>: date	concatenate	&	year	day of year	date
5f	<year> & <month>: month and year	concatenate	&	year	month	month and year
5f	<year> + <number of months>: year	plus	+	year	number of months	year
5f	<year> - <number of months>: year	minus	-	year	number of months	year
5f	<year> - <year>: number of months	minus	-	year	year	number of months
5f	<year> < <year>: boolean	less than	<	year	year	boolean
5f	<year> <= <year>: boolean	less than or equal	<=	year	year	boolean
5f	<year> = <year>: boolean	equal	=	year	year	boolean
"""

# 317 rows
CASTS: str = """\
1f	<action lock state> as string: string	string	action lock state	string
1f	<action> as string: string	string	action	string
12	<agent interface capability> as string: string	string	agent interface capability	string
2	<application> as string: string	string	application	string
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
5f	<binary operator> as string: string	string	binary operator	string
5f	<binary_string> as fxf string: string	fxf string	binary_string	string
5f	<binary_string> as hexadecimal: string	hexadecimal	binary_string	string
5f	<binary_string> as local string: string	local string	binary_string	string
5f	<binary_string> as string: string	string	binary_string	string
5f	<binary_string> as utf16 string: string	utf16 string	binary_string	string
5f	<binary_string> as utf8 string: string	utf8 string	binary_string	string
5f	<binary_substring> as binary_substring: binary_substring	binary_substring	binary_substring	binary_substring
5f	<binary_substring> as string: string	string	binary_substring	string
1f	<bios> as string: string	string	bios	string
5f	<bit set> as integer: integer	integer	bit set	integer
5f	<bit set> as string: string	string	bit set	string
5f	<boolean> as boolean: boolean	boolean	boolean	boolean
5f	<boolean> as string: string	string	boolean	string
4	<capability> as string: string	string	capability	string
5f	<cast> as string: string	string	cast	string
1f	<cidr subnet> as string: string	string	cidr subnet	string
2	<client process owner> as string: string	string	client process owner	string
5f	<date> as string: string	string	date	string
5f	<day of month> as integer: integer	integer	day of month	integer
5f	<day of month> as string: string	string	day of month	string
5f	<day of month> as two digits: string	two digits	day of month	string
5f	<day of week> as string: string	string	day of week	string
5f	<day of week> as three letters: string	three letters	day of week	string
5f	<day of year> as string: string	string	day of year	string
9	<debian base package> as string: string	string	debian base package	string
9	<debian package upstream version> as debian package version upstream: debian package upstream version	debian package version upstream	debian package upstream version	debian package upstream version
9	<debian package upstream version> as string: string	string	debian package upstream version	string
9	<debian package version epoch> as debian package version epoch: debian package version epoch	debian package version epoch	debian package version epoch	debian package version epoch
9	<debian package version epoch> as string: string	string	debian package version epoch	string
9	<debian package version revision> as debian package version revision: debian package version revision	debian package version revision	debian package version revision	debian package version revision
9	<debian package version revision> as string: string	string	debian package version revision	string
9	<debian package version> as debian package version: debian package version	debian package version	debian package version	debian package version
9	<debian package version> as string: string	string	debian package version	string
9	<debian versioned package> as string: string	string	debian versioned package	string
9	<debianpkg dependency> as string: string	string	debianpkg dependency	string
9	<debianpkg reverse dependencies> as string: string	string	debianpkg reverse dependencies	string
9	<debianpkg verfile> as string: string	string	debianpkg verfile	string
9	<debianpkg version> as debian package version: debian package version	debian package version	debianpkg version	debian package version
9	<debianpkg version> as string: string	string	debianpkg version	string
10	<discretionary access control list> as string: string	string	discretionary access control list	string
2	<dummy type> as string: string	string	dummy type	string
1f	<environment variable> as string: string	string	environment variable	string
1f	<file content> as lowercase: file content	lowercase	file content	file content
1f	<file content> as uppercase: file content	uppercase	file content	file content
12	<file> as string: string	string	file	string
d	<filesystem object> as device file: device file	device file	filesystem object	device file
d	<filesystem object> as fifo file: fifo file	fifo file	filesystem object	fifo file
2	<filesystem object> as file: file	file	filesystem object	file
2	<filesystem object> as folder: folder	folder	filesystem object	folder
d	<filesystem object> as socket file: socket file	socket file	filesystem object	socket file
1f	<filesystem object> as string: string	string	filesystem object	string
d	<filesystem object> as symlink: symlink	symlink	filesystem object	symlink
10	<firewall profile type> as string: string	string	firewall profile type	string
5f	<floating point> as floating point: floating point	floating point	floating point	floating point
5f	<floating point> as integer: integer	integer	floating point	integer
5f	<floating point> as scientific notation: string	scientific notation	floating point	string
5f	<floating point> as standard notation: string	standard notation	floating point	string
5f	<floating point> as string: string	string	floating point	string
5f	<format> as string: string	string	format	string
d	<grub block list> as string: string	string	grub block list	string
d	<grub bootable image> as string: string	string	grub bootable image	string
d	<grub color pair> as string: string	string	grub color pair	string
d	<grub color> as string: string	string	grub color	string
d	<grub device> as string: string	string	grub device	string
d	<grub file location> as string: string	string	grub file location	string
d	<grub image choice> as string: string	string	grub image choice	string
d	<grub module> as string: string	string	grub module	string
5f	<hertz> as string: string	string	hertz	string
5f	<html> as decoded string: string	decoded string	html	string
5f	<html> as html: html	html	html	html
5f	<html> as string: string	string	html	string
5f	<integer> as bit set: bit set	bit set	integer	bit set
5f	<integer> as bits: bit set	bits	integer	bit set
5f	<integer> as day_of_month: day of month	day_of_month	integer	day of month
5f	<integer> as floating point: floating point	floating point	integer	floating point
5f	<integer> as hexadecimal: string	hexadecimal	integer	string
5f	<integer> as integer: integer	integer	integer	integer
5f	<integer> as large integer: large integer	large integer	integer	large integer
5f	<integer> as month: month	month	integer	month
5f	<integer> as string: string	string	integer	string
5f	<integer> as uinteger: uinteger	uinteger	integer	uinteger
5f	<integer> as year: year	year	integer	year
5f	<ip version> as string: string	string	ip version	string
5f	<ipv4 address> as ipv4or6 address: ipv4or6 address	ipv4or6 address	ipv4 address	ipv4or6 address
5f	<ipv4 address> as ipv6 address: ipv6 address	ipv6 address	ipv4 address	ipv6 address
5f	<ipv4 address> as string: string	string	ipv4 address	string
5f	<ipv4or6 address> as compressed string with ipv4 with zone index: string	compressed string with ipv4 with zone index	ipv4or6 address	string
5f	<ipv4or6 address> as compressed string with ipv4: string	compressed string with ipv4	ipv4or6 address	string
5f	<ipv4or6 address> as compressed string with zone index: string	compressed string with zone index	ipv4or6 address	string
5f	<ipv4or6 address> as compressed string: string	compressed string	ipv4or6 address	string
5f	<ipv4or6 address> as string with ipv4 with zone index: string	string with ipv4 with zone index	ipv4or6 address	string
5f	<ipv4or6 address> as string with ipv4: string	string with ipv4	ipv4or6 address	string
5f	<ipv4or6 address> as string with leading zeros with zone index: string	string with leading zeros with zone index	ipv4or6 address	string
5f	<ipv4or6 address> as string with leading zeros: string	string with leading zeros	ipv4or6 address	string
5f	<ipv4or6 address> as string with zone index: string	string with zone index	ipv4or6 address	string
5f	<ipv4or6 address> as string: string	string	ipv4or6 address	string
5f	<ipv6 address> as compressed string with ipv4 with zone index: string	compressed string with ipv4 with zone index	ipv6 address	string
5f	<ipv6 address> as compressed string with ipv4: string	compressed string with ipv4	ipv6 address	string
5f	<ipv6 address> as compressed string with zone index: string	compressed string with zone index	ipv6 address	string
5f	<ipv6 address> as compressed string: string	compressed string	ipv6 address	string
5f	<ipv6 address> as ipv4or6 address: ipv4or6 address	ipv4or6 address	ipv6 address	ipv4or6 address
5f	<ipv6 address> as string with ipv4 with zone index: string	string with ipv4 with zone index	ipv6 address	string
5f	<ipv6 address> as string with ipv4: string	string with ipv4	ipv6 address	string
5f	<ipv6 address> as string with leading zeros with zone index: string	string with leading zeros with zone index	ipv6 address	string
5f	<ipv6 address> as string with leading zeros: string	string with leading zeros	ipv6 address	string
5f	<ipv6 address> as string with zone index: string	string with zone index	ipv6 address	string
5f	<ipv6 address> as string: string	string	ipv6 address	string
5f	<json key> as string: string	string	json key	string
5f	<json value> as boolean: boolean	boolean	json value	boolean
5f	<json value> as float: floating point	float	json value	floating point
5f	<json value> as integer: integer	integer	json value	integer
5f	<json value> as string: string	string	json value	string
1d	<language> as string: string	string	language	string
5f	<large integer> as hexadecimal: string	hexadecimal	large integer	string
5f	<large integer> as integer: integer	integer	large integer	integer
5f	<large integer> as large integer: large integer	large integer	large integer	large integer
5f	<large integer> as string: string	string	large integer	string
5f	<large integer> as uinteger: uinteger	uinteger	large integer	uinteger
10	<local group member> as string: string	string	local group member	string
1f	<manual group> as string: string	string	manual group	string
10	<metabase identifier> as integer: integer	integer	metabase identifier	integer
10	<metabase identifier> as string: string	string	metabase identifier	string
10	<metabase type> as integer: integer	integer	metabase type	integer
10	<metabase type> as string: string	string	metabase type	string
10	<metabase user type> as integer: integer	integer	metabase user type	integer
10	<metabase user type> as string: string	string	metabase user type	string
10	<metabase value> as integer: integer	integer	metabase value	integer
10	<metabase value> as string: string	string	metabase value	string
d	<mode> as octal string: string	octal string	mode	string
d	<mode> as string: string	string	mode	string
d	<mode_mask> as integer: integer	integer	mode_mask	integer
d	<mode_mask> as string: string	string	mode_mask	string
5f	<month and year> as string: string	string	month and year	string
5f	<month> as integer: integer	integer	month	integer
5f	<month> as string: string	string	month	string
5f	<month> as three letters: string	three letters	month	string
5f	<month> as two digits: string	two digits	month	string
5f	<number of months> as string: string	string	number of months	string
1f	<operating system> as string: string	string	operating system	string
4	<package> as string: string	string	package	string
14	<plugin store key> as string: string	string	plugin store key	string
14	<plugin store> as string: string	string	plugin store	string
1f	<power level> as string: string	string	power level	string
12	<power state> as string: string	string	power state	string
1d	<primary language> as string: string	string	primary language	string
5f	<property> as string: string	string	property	string
42	<rate> as string: string	string	rate	string
10	<registry key value type> as string: string	string	registry key value type	string
10	<registry key value> as application: application	application	registry key value	application
10	<registry key value> as file: file	file	registry key value	file
10	<registry key value> as folder: folder	folder	registry key value	folder
10	<registry key value> as integer: integer	integer	registry key value	integer
10	<registry key value> as large integer: large integer	large integer	registry key value	large integer
10	<registry key value> as string: string	string	registry key value	string
10	<registry key value> as system file: file	system file	registry key value	file
10	<registry key value> as system x32 file: file	system x32 file	registry key value	file
10	<registry key value> as system x64 file: file	system x64 file	registry key value	file
10	<registry key value> as time: time	time	registry key value	time
10	<registry key value> as uinteger: uinteger	uinteger	registry key value	uinteger
10	<registry key> as string: string	string	registry key	string
5f	<rope> as string: string	string	rope	string
4	<rpm package release> as rpm package release: rpm package release	rpm package release	rpm package release	rpm package release
4	<rpm package release> as string: string	string	rpm package release	string
4	<rpm package version record> as rpm package version record: rpm package version record	rpm package version record	rpm package version record	rpm package version record
4	<rpm package version record> as short rpm package version record: short rpm package version record	short rpm package version record	rpm package version record	short rpm package version record
4	<rpm package version record> as string: string	string	rpm package version record	string
4	<rpm package version> as rpm package version: rpm package version	rpm package version	rpm package version	rpm package version
4	<rpm package version> as string: string	string	rpm package version	string
d	<runlevel> as string: string	string	runlevel	string
10	<security descriptor> as string: string	string	security descriptor	string
12	<security identifier> as string: string	string	security identifier	string
1f	<server based group> as string: string	string	server based group	string
1d	<service> as string: string	string	service	string
1f	<setting> as string: string	string	setting	string
4	<short rpm package version record> as rpm package version record: rpm package version record	rpm package version record	short rpm package version record	rpm package version record
4	<short rpm package version record> as short rpm package version record: short rpm package version record	short rpm package version record	short rpm package version record	short rpm package version record
4	<short rpm package version record> as string: string	string	short rpm package version record	string
10	<site profile variable> as string: string	string	site profile variable	string
5f	<site version list> as string: string	string	site version list	string
1f	<smbios value> as hexadecimal: string	hexadecimal	smbios value	string
1f	<smbios value> as string: string	string	smbios value	string
1f	<sqlite column type> as string: string	string	sqlite column type	string
1f	<sqlite column> as string: string	string	sqlite column	string
1f	<sqlite database> as string: string	string	sqlite database	string
1f	<sqlite row> as string: string	string	sqlite row	string
1f	<sqlite table> as string: string	string	sqlite table	string
2	<stage> as string: string	string	stage	string
5f	<string> as binary_string: binary_string	binary_string	string	binary_string
5f	<string> as boolean: boolean	boolean	string	boolean
5f	<string> as date: date	date	string	date
5f	<string> as day_of_month: day of month	day_of_month	string	day of month
5f	<string> as day_of_week: day of week	day_of_week	string	day of week
5f	<string> as floating point: floating point	floating point	string	floating point
5f	<string> as fxf binary_string: binary_string	fxf binary_string	string	binary_string
5f	<string> as hexadecimal: string	hexadecimal	string	string
5f	<string> as html: html	html	string	html
5f	<string> as integer: integer	integer	string	integer
5f	<string> as ipv4or6 address: ipv4or6 address	ipv4or6 address	string	ipv4or6 address
5f	<string> as ipv6 address: ipv6 address	ipv6 address	string	ipv6 address
5f	<string> as large integer: large integer	large integer	string	large integer
5f	<string> as left trimmed string: string	left trimmed string	string	string
5f	<string> as local binary_string: binary_string	local binary_string	string	binary_string
5f	<string> as local time: time	local time	string	time
5f	<string> as local zoned time_of_day: time of day with time zone	local zoned time_of_day	string	time of day with time zone
5f	<string> as lowercase: string	lowercase	string	string
5f	<string> as month: month	month	string	month
5f	<string> as right trimmed string: string	right trimmed string	string	string
5f	<string> as site version list: site version list	site version list	string	site version list
5f	<string> as string: string	string	string	string
4d	<string> as strverscmp version: strverscmp version	strverscmp version	string	strverscmp version
5f	<string> as time interval: time interval	time interval	string	time interval
5f	<string> as time zone: time zone	time zone	string	time zone
5f	<string> as time: time	time	string	time
5f	<string> as time_of_day: time of day	time_of_day	string	time of day
5f	<string> as trimmed string: string	trimmed string	string	string
5f	<string> as uinteger: uinteger	uinteger	string	uinteger
5f	<string> as universal time: time	universal time	string	time
5f	<string> as universal zoned time_of_day: time of day with time zone	universal zoned time_of_day	string	time of day with time zone
5f	<string> as uppercase: string	uppercase	string	string
5f	<string> as utf16 binary_string: binary_string	utf16 binary_string	string	binary_string
5f	<string> as utf8 binary_string: binary_string	utf8 binary_string	string	binary_string
5f	<string> as version: version	version	string	version
50	<string> as windows display time: time	windows display time	string	time
5f	<string> as year: year	year	string	year
5f	<string> as zoned time_of_day: time of day with time zone	zoned time_of_day	string	time of day with time zone
5f	<substring> as string: string	string	substring	string
5f	<substring> as substring: substring	substring	substring	substring
d	<symlink> as binary_string: binary_string	binary_string	symlink	binary_string
d	<symlink> as device file: device file	device file	symlink	device file
d	<symlink> as fifo file: fifo file	fifo file	symlink	fifo file
d	<symlink> as file: file	file	symlink	file
d	<symlink> as folder: folder	folder	symlink	folder
d	<symlink> as socket file: socket file	socket file	symlink	socket file
d	<symlink> as string: string	string	symlink	string
d	<symlink> as symlink: symlink	symlink	symlink	symlink
10	<system access control list> as string: string	string	system access control list	string
10	<task action> as com handler task action: com handler task action	com handler task action	task action	com handler task action
10	<task action> as email task action: email task action	email task action	task action	email task action
10	<task action> as exec task action: exec task action	exec task action	task action	exec task action
10	<task action> as show message task action: show message task action	show message task action	task action	show message task action
10	<task trigger> as boot task trigger: boot task trigger	boot task trigger	task trigger	boot task trigger
10	<task trigger> as daily task trigger: daily task trigger	daily task trigger	task trigger	daily task trigger
10	<task trigger> as event task trigger: event task trigger	event task trigger	task trigger	event task trigger
10	<task trigger> as idle task trigger: idle task trigger	idle task trigger	task trigger	idle task trigger
10	<task trigger> as logon task trigger: logon task trigger	logon task trigger	task trigger	logon task trigger
10	<task trigger> as monthly task trigger: monthly task trigger	monthly task trigger	task trigger	monthly task trigger
10	<task trigger> as monthlydow task trigger: monthlydow task trigger	monthlydow task trigger	task trigger	monthlydow task trigger
10	<task trigger> as registration task trigger: registration task trigger	registration task trigger	task trigger	registration task trigger
10	<task trigger> as session state change task trigger: session state change task trigger	session state change task trigger	task trigger	session state change task trigger
10	<task trigger> as time task trigger: time task trigger	time task trigger	task trigger	time task trigger
10	<task trigger> as weekly task trigger: weekly task trigger	weekly task trigger	task trigger	weekly task trigger
1f	<tcp state> as string: string	string	tcp state	string
5f	<time interval> as string: string	string	time interval	string
5f	<time of day with time zone> as string: string	string	time of day with time zone	string
5f	<time of day> as string: string	string	time of day	string
5f	<time range> as string: string	string	time range	string
5f	<time zone> as string: string	string	time zone	string
5f	<time> as local date: date	local date	time	date
5f	<time> as local string: string	local string	time	string
5f	<time> as string: string	string	time	string
5f	<time> as universal date: date	universal date	time	date
5f	<time> as universal string: string	universal string	time	string
5f	<tuple item> as string: string	string	tuple item	string
5f	<type> as string: string	string	type	string
5f	<uinteger> as hexadecimal: string	hexadecimal	uinteger	string
5f	<uinteger> as integer: integer	integer	uinteger	integer
5f	<uinteger> as large integer: large integer	large integer	uinteger	large integer
5f	<uinteger> as string: string	string	uinteger	string
5f	<uinteger> as uinteger: uinteger	uinteger	uinteger	uinteger
5f	<unary operator> as string: string	string	unary operator	string
5f	<undefined> as string: string	string	undefined	string
2	<user attribute> as string: string	string	user attribute	string
1f	<uuid> as binary_string: binary_string	binary_string	uuid	binary_string
1f	<uuid> as hexadecimal: string	hexadecimal	uuid	string
1f	<uuid> as string: string	string	uuid	string
5f	<version> as string: string	string	version	string
5f	<version> as version: version	version	version	version
10	<winrt enumeration> as string: string	string	winrt enumeration	string
10	<winrt package user information> as string: string	string	winrt package user information	string
10	<winrt package> as string: string	string	winrt package	string
10	<wmi object> as string: string	string	wmi object	string
10	<wmi select> as string: string	string	wmi select	string
1d	<xml dom node> as text: string	text	xml dom node	string
1d	<xml dom node> as xml: string	xml	xml dom node	string
1f	<yaml key> as string: string	string	yaml key	string
1f	<yaml value> as boolean: boolean	boolean	yaml value	boolean
1f	<yaml value> as float: floating point	float	yaml value	floating point
1f	<yaml value> as integer: integer	integer	yaml value	integer
1f	<yaml value> as string: string	string	yaml value	string
5f	<year> as integer: integer	integer	year	integer
5f	<year> as string: string	string	year	string
"""

# 4661 rows
PROPERTIES: str = """\
ff	abbr <string> of <html>: html	abbr	abbrs	abbr	0	html	html	string
ff	abbr <string> of <string>: html	abbr	abbrs	abbr	0	html	string	string
ff	abbr of <html>: html	abbr	abbrs	abbr	0	html	html	
ff	abbr of <string>: html	abbr	abbrs	abbr	0	html	string	
10	above normal priority: priority class	above normal priority	above normal priorities	above normal priority	0	priority class		
ff	absolute value of <hertz>: hertz	absolute value	absolute values	absolute value	0	hertz	hertz	
ff	absolute value of <integer>: integer	absolute value	absolute values	absolute value	0	integer	integer	
ff	absolute value of <time interval>: time interval	absolute value	absolute values	absolute value	0	time interval	time interval	
10	access mode of <access control entry>: integer	access mode	access modes	access mode	0	integer	access control entry	
10	access system security permission of <access control entry>: boolean	access system security permission	access system security permissions	access system security permission	0	boolean	access control entry	
1d	accessed time of <filesystem object>: time	accessed time	accessed times	accessed time	0	time	filesystem object	
d	accessed time of <symlink>: time	accessed time	accessed times	accessed time	0	time	symlink	
10	account disabled flag of <user>: boolean	account disabled flag	account disabled flags	account disabled flag	0	boolean	user	
10	account expiration of <user>: time	account expiration	account expirations	account expiration	0	time	user	
10	account lockout duration of <security database>: time interval	account lockout duration	account lockout durations	account lockout duration	0	time interval	security database	
10	account lockout observation window of <security database>: time interval	account lockout observation window	account lockout observation windows	account lockout observation window	0	time interval	security database	
10	account lockout threshold of <security database>: integer	account lockout threshold	account lockout thresholds	account lockout threshold	0	integer	security database	
10	account logon category of <audit policy>: audit policy category	account logon category	account logon categories	account logon category	0	audit policy category	audit policy	
10	account management category of <audit policy>: audit policy category	account management category	account management categories	account management category	0	audit policy category	audit policy	
10	account name of <security identifier>: string	account name	account names	account name	0	string	security identifier	
10	accounts operator flag of <user>: boolean	accounts operator flag	accounts operator flags	accounts operator flag	0	boolean	user	
10	accounts with privilege <string>: security account	account with privilege	accounts with privilege	accounts with privilege	1	security account		string
10	accounts with privileges: security account	account with privileges	accounts with privileges	accounts with privileges	1	security account		
1f	accuracy of <dmi electrical_current_probe>: integer	accuracy	accuracys	accuracy	0	integer	dmi electrical_current_probe	
1f	accuracy of <dmi temperature_probe>: integer	accuracy	accuracys	accuracy	0	integer	dmi temperature_probe	
1f	accuracy of <dmi voltage_probe>: integer	accuracy	accuracys	accuracy	0	integer	dmi voltage_probe	
10	ace flag of <access control entry>: integer	ace flag	ace flags	ace flag	0	integer	access control entry	
10	ace type of <access control entry>: integer	ace type	ace types	ace type	0	integer	access control entry	
ff	acronym <string> of <html>: html	acronym	acronyms	acronym	0	html	html	string
ff	acronym <string> of <string>: html	acronym	acronyms	acronym	0	html	string	string
ff	acronym of <html>: html	acronym	acronyms	acronym	0	html	html	
ff	acronym of <string>: html	acronym	acronyms	acronym	0	html	string	
e0	action <integer> of <bes fixlet>: bes fixlet action	action	actions	action	0	bes fixlet action	bes fixlet	integer
1f	action <integer>: action	action	actions	action	0	action		integer
e0	action <string> of <bes fixlet>: bes fixlet action	action	actions	action	0	bes fixlet action	bes fixlet	string
e0	action dependencies of <bes action>: bes action	action dependency	action dependencies	action dependencies	1	bes action	bes action	
1f	action duration of <evaluation cycle>: time interval	action duration	action durations	action duration	0	time interval	evaluation cycle	
e0	action flag of <bes filter>: boolean	action flag	action flags	action flag	0	boolean	bes filter	
40	action id of <bes peer download>: integer	action id	action ids	action id	0	integer	bes peer download	
1f	action lock state: action lock state	action lock state	action lock states	action lock state	0	action lock state		
e0	action of <bes action result>: bes action	action	actions	action	0	bes action	bes action result	
e0	action of <bes baseline component>: bes fixlet action	action	actions	action	0	bes fixlet action	bes baseline component	
40	action of <bes peer download>: bes action	action	actions	action	0	bes action	bes peer download	
12	action of <firewall rule>: firewall action	action	actions	action	0	firewall action	firewall rule	
1f	action percent of <evaluation cycle>: floating point	action percent	action percents	action percent	0	floating point	evaluation cycle	
e0	action results of <bes computer>: bes action result	action result	action results	action results	1	bes action result	bes computer	
e0	action script of <bes action>: string	action script	action scripts	action script	0	string	bes action	
e0	action script type of <bes action>: string	action script type	action script types	action script type	0	string	bes action	
e0	action set of <bes domain>: bes action set	action set	action sets	action set	0	bes action set	bes domain	
e0	action set of <bes filter>: bes action set	action set	action sets	action set	0	bes action set	bes filter	
e0	action set of <bes site>: bes action set	action set	action sets	action set	0	bes action set	bes site	
e0	action site of <bes user>: bes site	action site	action sites	action site	0	bes site	bes user	
1f	action: action	action	actions	action	0	action		
e0	actions of <bes domain>: bes action	action	actions	actions	1	bes action	bes domain	
e0	actions of <bes fixlet>: bes fixlet action	action	actions	actions	1	bes fixlet action	bes fixlet	
e0	actions of <bes site>: bes action	action	actions	actions	1	bes action	bes site	
10	actions of <task definition>: task action	action	actions	actions	1	task action	task definition	
e0	activations of <bes fixlet>: bes activation	activation	activations	activations	1	bes activation	bes fixlet	
1f	active action: action	active action	active actions	active action	0	action		
5f	active container count of <bes product>: integer	active container count	active container counts	active container count	0	integer	bes product	
1f	active count of <action>: integer	active count	active counts	active count	0	integer	action	
10	active device files <string>: file	active device file	active device files	active device files	1	file		string
10	active device files: file	active device file	active device files	active device files	1	file		
10	active devices: active device	active device	active devices	active devices	1	active device		
40	active directory of <bes idp directory>: boolean	active directory	active directories	active directory	0	boolean	bes idp directory	
e0	active directory of <bes ldap directory>: boolean	active directory	active directories	active directory	0	boolean	bes ldap directory	
a0	active directory path of <bes computer>: distinguished name
12	active directory user of <user>: active directory local user	active directory user	active directory users	active directory user	0	active directory local user	user	
12	active directory: active directory server	active directory	active directories	active directory	0	active directory server		
e0	active flag of <bes activation>: boolean	active flag	active flags	active flag	0	boolean	bes activation	
1f	active line number of <action>: integer	active line number	active line numbers	active line number	0	integer	action	
1f	active of <action>: boolean	active	actives	active	0	boolean	action	
1f	active of <logged on user>: boolean	active	actives	active	0	boolean	logged on user	
1f	active start time of <action>: time	active start time	active start times	active start time	0	time	action	
12	active state: power state	active state	active states	active state	0	power state		
10	activity history of <logged on user>: activity history	activity history	activity histories	activity history	0	activity history	logged on user	
2	activity identifier of <os log entry log>: integer	activity identifier	activity identifiers	activity identifier	0	integer	os log entry log	
12	adapter <integer> of <network>: network adapter	adapter	adapters	adapter	0	network adapter	network	integer
2	adapter <string> of <network>: network adapter	adapter	adapters	adapter	0	network adapter	network	string
1f	adapter of <network adapter interface>: network adapter	adapter	adapters	adapter	0	network adapter	network adapter interface	
1f	adapters of <network>: network adapter	adapter	adapters	adapters	1	network adapter	network	
1f	additional_information <integer> of <dmi>: dmi additional_information	additional_information	additional_informations	additional_information	0	dmi additional_information	dmi	integer
1f	additional_informations of <dmi>: dmi additional_information	additional_information	additional_informations	additional_informations	1	dmi additional_information	dmi	
ff	address <string> of <html>: html	address	addresss	address	0	html	html	string
ff	address <string> of <string>: html	address	addresss	address	0	html	string	string
10	address lists of <network adapter>: network address list	address list	address lists	address lists	1	network address list	network adapter	
1f	address of <dmi management_device>: integer	address	addresss	address	0	integer	dmi management_device	
ff	address of <html>: html	address	addresss	address	0	html	html	
1f	address of <network adapter interface>: ipv4or6 address	address	addresses	address	0	ipv4or6 address	network adapter interface	
1f	address of <network adapter>: ipv4 address	address	addresses	address	0	ipv4 address	network adapter	
10	address of <network address list>: ipv4 address	address	addresses	address	0	ipv4 address	network address list	
1f	address of <network ip interface>: ipv4 address	address	addresses	address	0	ipv4 address	network ip interface	
ff	address of <string>: html	address	addresss	address	0	html	string	
1f	address_type of <dmi management_device>: integer	address_type	address_types	address_type	0	integer	dmi management_device	
10	admin privilege of <user>: boolean	admin privilege	admin privileges	admin privilege	0	boolean	user	
e0	administered computer set of <bes user>: bes computer set	administered computer set	administered computer sets	administered computer set	0	bes computer set	bes user	
e0	administered computers of <bes user>: bes computer	administered computer	administered computers	administered computers	1	bes computer	bes user	
1f	administrative rights of <client>: administrative rights	administrative rights	administrative rightss	administrative rights	0	administrative rights	client	
e0	administrator <( bes computer, bes user )>: boolean	administrator	administrators	administrator	0	boolean		( bes computer, bes user )
e0	administrator <( bes user, bes computer )>: boolean	administrator	administrators	administrator	0	boolean		( bes user, bes computer )
e0	administrator <bes computer> of <bes user>: boolean	administrator	administrators	administrator	0	boolean	bes user	bes computer
e0	administrator <bes user> of <bes computer>: boolean	administrator	administrators	administrator	0	boolean	bes computer	bes user
1f	administrator <string> of <client>: setting	administrator	administrators	administrator	0	setting	client	string
e0	administrator set of <bes computer>: bes user set	administrator set	administrator sets	administrator set	0	bes user set	bes computer	
e0	administrators of <bes computer>: bes user	administrator	administrators	administrators	1	bes user	bes computer	
1f	administrators of <client>: setting	administrator	administrators	administrators	1	setting	client	
12	agent interface <string> of <client>: agent interface	agent interface	agent interfaces	agent interface	0	agent interface	client	string
12	agent interfaces of <client>: agent interface	agent interface	agent interfaces	agent interfaces	1	agent interface	client	
e0	agent type of <bes computer>: string	agent type	agent types	agent type	0	string	bes computer	
e0	agent version of <bes computer>: string	agent version	agent versions	agent version	0	string	bes computer	
2	alias of <file>: boolean	alias	aliases	alias	0	boolean	file	
f	alias of <network ip interface>: boolean	alias	aliases	alias	0	boolean	network ip interface	
e0	all bes sites: bes site	all bes site	all bes sites	all bes sites	1	bes site		
e0	all computer counts: historical computer count	all computer count	all computer counts	all computer counts	1	historical computer count		
10	all firewall scope: firewall scope	all firewall scope	all firewall scopes	all firewall scope	0	firewall scope		
e0	all fixlet counts: historical fixlet count	all fixlet count	all fixlet counts	all fixlet counts	1	historical fixlet count		
10	all running services: service	all running service	all running services	all running services	1	service		
10	all services: service	all service	all services	all services	1	service		
2	allocation block count of <volume>: integer	allocation block count	allocation block counts	allocation block count	0	integer	volume	
10	allow demand start of <task settings>: boolean	allow demand start	allow demand starts	allow demand start	0	boolean	task settings	
12	allow firewall action: firewall action	allow firewall action	allow firewall actions	allow firewall action	0	firewall action		
10	allow hard terminate of <task settings>: boolean	allow hard terminate	allow hard terminates	allow hard terminate	0	boolean	task settings	
10	allow inbound echo request of <firewall icmp settings>: boolean	allow inbound echo request	allow inbound echo requests	allow inbound echo request	0	boolean	firewall icmp settings	
10	allow inbound mask request of <firewall icmp settings>: boolean	allow inbound mask request	allow inbound mask requests	allow inbound mask request	0	boolean	firewall icmp settings	
10	allow inbound router request of <firewall icmp settings>: boolean	allow inbound router request	allow inbound router requests	allow inbound router request	0	boolean	firewall icmp settings	
10	allow inbound timestamp request of <firewall icmp settings>: boolean	allow inbound timestamp request	allow inbound timestamp requests	allow inbound timestamp request	0	boolean	firewall icmp settings	
10	allow outbound destination unreachable of <firewall icmp settings>: boolean	allow outbound destination unreachable	allow outbound destination unreachables	allow outbound destination unreachable	0	boolean	firewall icmp settings	
10	allow outbound packet too big of <firewall icmp settings>: boolean	allow outbound packet too big	allow outbound packet too bigs	allow outbound packet too big	0	boolean	firewall icmp settings	
10	allow outbound parameter problem of <firewall icmp settings>: boolean	allow outbound parameter problem	allow outbound parameter problems	allow outbound parameter problem	0	boolean	firewall icmp settings	
10	allow outbound source quench of <firewall icmp settings>: boolean	allow outbound source quench	allow outbound source quenches	allow outbound source quench	0	boolean	firewall icmp settings	
10	allow outbound time exceeded of <firewall icmp settings>: boolean	allow outbound time exceeded	allow outbound time exceededs	allow outbound time exceeded	0	boolean	firewall icmp settings	
10	allow redirect of <firewall icmp settings>: boolean	allow redirect	allow redirects	allow redirect	0	boolean	firewall icmp settings	
ff	allow unmentioned site of <license>: boolean	allow unmentioned site	allow unmentioned sites	allow unmentioned site	0	boolean	license	
1f	allowed of <site>: boolean	allowed	alloweds	allowed	0	boolean	site	
1f	allowed sites of <restricted site>: site	allowed site	allowed sites	allowed sites	1	site	restricted site	
10	allowed workstations string of <user>: string	allowed workstations string	allowed workstations strings	allowed workstations string	0	string	user	
e0	analysis flag of <bes filter>: boolean	analysis flag	analysis flags	analysis flag	0	boolean	bes filter	
e0	analysis flag of <bes fixlet>: boolean	analysis flag	analysis flags	analysis flag	0	boolean	bes fixlet	
e0	analysis flag of <bes property>: boolean	analysis flag	analysis flags	analysis flag	0	boolean	bes property	
e0	analysis of <bes activation>: bes fixlet	analysis	analyses	analysis	0	bes fixlet	bes activation	
e0	analysis set of <bes filter>: bes fixlet set	analysis set	analysis sets	analysis set	0	bes fixlet set	bes filter	
1f	analysis: analysis	analysis	analysiss	analysis	0	analysis		
1f	ancestors of <filesystem object>: folder	ancestor	ancestors	ancestors	1	folder	filesystem object	
d	ancestors of <symlink>: folder	ancestor	ancestors	ancestors	1	folder	symlink	
ff	anchor <string> of <html>: html	anchor	anchors	anchor	0	html	html	string
ff	anchor <string> of <string>: html	anchor	anchors	anchor	0	html	string	string
ff	anchor of <html>: html	anchor	anchors	anchor	0	html	html	
ff	anchor of <string>: html	anchor	anchors	anchor	0	html	string	
d	android of <operating system>: boolean	android	androids	android	0	boolean	operating system	
10	anonymous logon group: security account	anonymous logon group	anonymous logon groups	anonymous logon group	0	security account		
10	ansi code page: integer	ansi code page	ansi code pages	ansi code page	0	integer		
10	any adapter <integer> of <network>: network adapter	any adapter	any adapters	any adapter	0	network adapter	network	integer
1f	any adapters of <network>: network adapter	any adapter	any adapters	any adapters	1	network adapter	network	
ff	any ip version: ip version	any ip version	any ip versions	any ip version	0	ip version		
10	aol error of <file>: string	aol error	aol errors	aol error	0	string	file	
10	aol error time of <file>: time	aol error time	aol error times	aol error time	0	time	file	
1f	api duration of <evaluation cycle>: time interval	api duration	api durations	api duration	0	time interval	evaluation cycle	
1f	api percent of <evaluation cycle>: floating point	api percent	api percents	api percent	0	floating point	evaluation cycle	
1f	apparent registration server time: time	apparent registration server time	apparent registration server times	apparent registration server time	0	time		
10	append permission of <access control entry>: boolean	append permission	append permissions	append permission	0	boolean	access control entry	
2	apple extras folder of <domain>: folder	apple extras folder	apple extras folders	apple extras folder	0	folder	domain	
2	apple extras folder: folder	apple extras folder	apple extras folders	apple extras folder	0	folder		
2	apple menu items folder of <domain>: folder	apple menu items folder	apple menu items folders	apple menu items folder	0	folder	domain	
2	apple menu items folder: folder	apple menu items folder	apple menu items folders	apple menu items folder	0	folder		
e0	applicability relevance of <bes action>: string	applicability relevance	applicability relevances	applicability relevance	0	string	bes action	
e0	applicable computer count of <bes baseline component>: integer	applicable computer count	applicable computer counts	applicable computer count	0	integer	bes baseline component	
e0	applicable computer count of <bes fixlet>: integer	applicable computer count	applicable computer counts	applicable computer count	0	integer	bes fixlet	
e0	applicable computer set of <bes baseline component>: bes computer set	applicable computer set	applicable computer sets	applicable computer set	0	bes computer set	bes baseline component	
e0	applicable computer set of <bes fixlet>: bes computer set	applicable computer set	applicable computer sets	applicable computer set	0	bes computer set	bes fixlet	
e0	applicable computers of <bes fixlet>: bes computer	applicable computer	applicable computers	applicable computers	1	bes computer	bes fixlet	
1d	application <binary_string> of <folder>: application	application	applications	application	0	application	folder	binary_string
1f	application <binary_string>: application	application	applications	application	0	application		binary_string
1d	application <string> of <folder>: application	application	applications	application	0	application	folder	string
10	application <string> of <registry key>: application	application	applications	application	0	application	registry key	string
10	application <string> of <registry>: application	application	applications	application	0	application	registry	string
1f	application <string>: application	application	applications	application	0	application		string
10	application event log: event log	application event log	application event logs	application event log	0	event log		
10	application folder <string> of <registry key>: folder	application folder	application folders	application folder	0	folder	registry key	string
10	application folder <string> of <registry>: folder	application folder	application folders	application folder	0	folder	registry	string
10	application folder of <registry key>: folder	application folder	application folders	application folder	0	folder	registry key	
12	application name of <firewall rule>: string	application name	application names	application name	0	string	firewall rule	
10	application of <registry key>: application	application	applications	application	0	application	registry key	
10	application parameter string of <user>: string	application parameter string	application parameter strings	application parameter string	0	string	user	
2	application support folder of <domain>: folder	application support folder	application support folders	application support folder	0	folder	domain	
2	application support folder: folder	application support folder	application support folders	application support folder	0	folder		
1f	application usage summaries: application usage summary	application usage summary	application usage summaries	application usage summaries	1	application usage summary		
1f	application usage summary <string>: application usage summary	application usage summary	application usage summaries	application usage summary	0	application usage summary		string
1f	application usages <string>: timed( time range, integer )	application usage	application usages	application usages	1	timed( time range, integer )		string
2	applications folder of <domain>: folder	applications folder	applications folders	applications folder	0	folder	domain	
2	applications folder: folder	applications folder	applications folders	applications folder	0	folder		
2	applications of <folder>: application	application	applications	applications	1	application	folder	
10	applications of <registry>: application	application	applications	applications	1	application	registry	
2	applications: application	application	applications	applications	1	application		
e0	apply count of <bes action result>: integer	apply count	apply counts	apply count	0	integer	bes action result	
e0	approver role of <bes user>: bes role	approver role	approver roles	approver role	0	bes role	bes user	
ff	april <integer> of <integer>: date	april	aprils	april	0	date	integer	integer
ff	april <integer>: day of year	april	aprils	april	0	day of year		integer
ff	april of <integer>: month and year	april	aprils	april	0	month and year	integer	
ff	april: month	april	aprils	april	0	month		
9	architecture of <debian versioned package>: string	architecture	architectures	architecture	0	string	debian versioned package	
9	architecture of <debianpkg version>: string	architecture	architectures	architecture	0	string	debianpkg version	
1f	architecture of <operating system>: string	architecture	architectures	architecture	0	string	operating system	
4	architecture of <package>: string	architecture	architectures	architecture	0	string	package	
10	architecture of <winrt package id>: winrt enumeration	architecture	architectures	architecture	0	winrt enumeration	winrt package id	
1f	archive duration of <evaluation cycle>: time interval	archive duration	archive durations	archive duration	0	time interval	evaluation cycle	
10	archive of <filesystem object>: boolean	archive	archives	archive	0	boolean	filesystem object	
1f	archive percent of <evaluation cycle>: floating point	archive percent	archive percents	archive percent	0	floating point	evaluation cycle	
10	argument string of <exec task action>: string	argument string	argument strings	argument string	0	string	exec task action	
10	argument string of <file shortcut>: string	argument string	argument strings	argument string	0	string	file shortcut	
2	array <integer> of <array>: array	array	arrays	array	0	array	array	integer
2	array <string> of <dictionary>: array	array	arrays	array	0	array	dictionary	string
2	array <string> of <preference>: array	array	arrays	array	0	array	preference	string
2	array of <file>: array	array	arrays	array	0	array	file	
2	array of <osxvalue>: array	array	arrays	array	0	array	osxvalue	
e0	asset of <bes unmanagedasset field>: bes unmanagedasset	asset	assets	asset	0	bes unmanagedasset	bes unmanagedasset field	
1f	asset_tag of <dmi base_board_information>: string	asset_tag	asset_tags	asset_tag	0	string	dmi base_board_information	
1f	asset_tag of <dmi memory_device>: string	asset_tag	asset_tags	asset_tag	0	string	dmi memory_device	
1f	asset_tag of <dmi processor_information>: string	asset_tag	asset_tags	asset_tag	0	string	dmi processor_information	
1f	asset_tag_number of <dmi system_enclosure_or_chassis>: string	asset_tag_number	asset_tag_numbers	asset_tag_number	0	string	dmi system_enclosure_or_chassis	
1f	asset_tag_number of <dmi system_power_supply>: string	asset_tag_number	asset_tag_numbers	asset_tag_number	0	string	dmi system_power_supply	
2	assistants folder of <domain>: folder	assistants folder	assistants folders	assistants folder	0	folder	domain	
2	assistants folder: folder	assistants folder	assistants folders	assistants folder	0	folder		
1f	associativity of <dmi cache_information>: integer	associativity	associativitys	associativity	0	integer	dmi cache_information	
10	at compatibility of <task settings>: boolean	at compatibility	at compatibilities	at compatibility	0	boolean	task settings	
10	attachments of <email task action>: string	attachment	attachments	attachments	1	string	email task action	
ff	attr lists of <( string, string )>: html attribute list	attr list	attr lists	attr lists	1	html attribute list	( string, string )	
bd	attribute <integer> of <xml dom node>: xml dom node	attribute	attributes	attribute	0	xml dom node	xml dom node	integer
2	attribute <string> of <user>: user attribute	attribute	attributes	attribute	0	user attribute	user	string
bd	attribute <string> of <xml dom node>: xml dom node	attribute	attributes	attribute	0	xml dom node	xml dom node	string
10	attribute permission of <network share>: boolean	attribute permission	attribute permissions	attribute permission	0	boolean	network share	
1f	attributes of <dmi memory_device>: integer	attributes	attributess	attributes	0	integer	dmi memory_device	
2	attributes of <user>: user attribute	attribute	attributes	attributes	1	user attribute	user	
bd	attributes of <xml dom node>: xml dom node	attribute	attributes	attributes	1	xml dom node	xml dom node	
2	audio folder of <domain>: folder	audio folder	audio folders	audio folder	0	folder	domain	
2	audio folder: folder	audio folder	audio folders	audio folder	0	folder		
2	audio plane of <registryroot>: registrynode	audio plane	audio planes	audio plane	0	registrynode	registryroot	
10	audit failure event log event type: event log event type	audit failure event log event type	audit failure event log event types	audit failure event log event type	0	event log event type		
10	audit failure of <access control entry>: boolean	audit failure	audit failures	audit failure	0	boolean	access control entry	
10	audit failure of <audit policy information>: boolean	audit failure	audit failures	audit failure	0	boolean	audit policy information	
10	audit level of <local mssql database>: integer	audit level	audit levels	audit level	0	integer	local mssql database	
10	audit policy: audit policy	audit policy	audit policies	audit policy	0	audit policy		
10	audit success event log event type: event log event type	audit success event log event type	audit success event log event types	audit success event log event type	0	event log event type		
10	audit success of <access control entry>: boolean	audit success	audit successes	audit success	0	boolean	access control entry	
10	audit success of <audit policy information>: boolean	audit success	audit successes	audit success	0	boolean	audit policy information	
ff	august <integer> of <integer>: date	august	augusts	august	0	date	integer	integer
ff	august <integer>: day of year	august	augusts	august	0	day of year		integer
ff	august of <integer>: month and year	august	augusts	august	0	month and year	integer	
ff	august: month	august	augusts	august	0	month		
10	authenticated users group: security account	authenticated users group	authenticated users groups	authenticated users group	0	security account		
1f	authenticating of <client>: boolean	authenticating	authenticatings	authenticating	0	boolean	client	
1f	authenticating of <current relay>: boolean	authenticating	authenticatings	authenticating	0	boolean	current relay	
e0	author of <bes comment>: bes user	author	authors	author	0	bes user	bes comment	
40	author of <bes tag>: bes user	author	authors	author	0	bes user	bes tag	
10	author of <task registration info>: string	author	authors	author	0	string	task registration info	
10	authorized applications of <firewall profile>: firewall authorized application	authorized application	authorized applications	authorized applications	1	firewall authorized application	firewall profile	
e0	automatic flag of <bes computer group>: boolean	automatic flag	automatic flags	automatic flag	0	boolean	bes computer group	
d	available amount of <ram>: integer	available amount	available amounts	available amount	0	integer	ram	
1f	average duration of <evaluation cycle>: time interval	average duration	average durations	average duration	0	time interval	evaluation cycle	
1f	average of <evaluation cycle>: integer	average	averages	average	0	integer	evaluation cycle	
40	azure entra id of <bes idp directory>: boolean	azure entra id	azure entra ids	azure entra id	0	boolean	bes idp directory	
ff	b <string> of <html>: html	b	bs	b	0	html	html	string
ff	b <string> of <string>: html	b	bs	b	0	html	string	string
ff	b of <html>: html	b	bs	b	0	html	html	
ff	b of <string>: html	b	bs	b	0	html	string	
1f	b32_bit_memory_error_information <integer> of <dmi>: dmi b32_bit_memory_error_information	b32_bit_memory_error_information	b32_bit_memory_error_informations	b32_bit_memory_error_information	0	dmi b32_bit_memory_error_information	dmi	integer
1f	b32_bit_memory_error_informations of <dmi>: dmi b32_bit_memory_error_information	b32_bit_memory_error_information	b32_bit_memory_error_informations	b32_bit_memory_error_informations	1	dmi b32_bit_memory_error_information	dmi	
1f	b64_bit_memory_error_information <integer> of <dmi>: dmi b64_bit_memory_error_information	b64_bit_memory_error_information	b64_bit_memory_error_informations	b64_bit_memory_error_information	0	dmi b64_bit_memory_error_information	dmi	integer
1f	b64_bit_memory_error_informations of <dmi>: dmi b64_bit_memory_error_information	b64_bit_memory_error_information	b64_bit_memory_error_informations	b64_bit_memory_error_informations	1	dmi b64_bit_memory_error_information	dmi	
d	background of <grub color pair>: grub color	background	backgrounds	background	0	grub color	grub color pair	
10	backoffice bit <operating system suite mask>: boolean	backoffice bit	backoffice bits	backoffice bit	0	boolean		operating system suite mask
2	backup time of <filesystem object>: time	backup time	backup times	backup time	0	time	filesystem object	
10	bad password count of <user>: integer	bad password count	bad password counts	bad password count	0	integer	user	
1f	bank_connections of <dmi memory_module_information>: integer	bank_connections	bank_connectionss	bank_connections	0	integer	dmi memory_module_information	
1f	bank_locator of <dmi memory_device>: string	bank_locator	bank_locators	bank_locator	0	string	dmi memory_device	
1f	banned prefetch plugins of <client>: string	banned prefetch plugin	banned prefetch plugins	banned prefetch plugins	1	string	client	
ff	base <string> of <html>: html	base	bases	base	0	html	html	string
ff	base <string> of <string>: html	base	bases	base	0	html	string	string
40	base distinguished name of <bes idp directory>: string	base distinguished name	base distinguished names	base distinguished name	0	string	bes idp directory	
e0	base distinguished name of <bes ldap directory>: string	base distinguished name	base distinguished names	base distinguished name	0	string	bes ldap directory	
10	base name of <operating system>: string	base name	base names	base name	0	string	operating system	
ff	base of <html>: html	base	bases	base	0	html	html	
ff	base of <string>: html	base	bases	base	0	html	string	
9	base package of <debianpkg version>: debian base package	base package	base packages	base package	0	debian base package	debianpkg version	
9	base packages <string> of <debianpackagecache>: debian base package	base package	base packages	base packages	1	debian base package	debianpackagecache	string
9	base packages of <debianpackagecache>: debian base package	base package	base packages	base packages	1	debian base package	debianpackagecache	
10	base priority of <process>: priority class	base priority	base priorities	base priority	0	priority class	process	
ff	base64 decode <string>: string	base64 decode	base64 decodes	base64 decode	0	string		string
1d	base64 der encoded certificate string of <string>: x509 certificate	base64 der encoded certificate string	base64 der encoded certificates string	base64 der encoded certificate string	0	x509 certificate	string	
ff	base64 encode <string>: string	base64 encode	base64 encodes	base64 encode	0	string		string
1f	base_address of <dmi ipmi_device_information>: integer	base_address	base_addresss	base_address	0	integer	dmi ipmi_device_information	
1f	base_board_information <integer> of <dmi>: dmi base_board_information	base_board_information	base_board_informations	base_board_information	0	dmi base_board_information	dmi	integer
1f	base_board_informations of <dmi>: dmi base_board_information	base_board_information	base_board_informations	base_board_informations	1	dmi base_board_information	dmi	
e0	baseline flag of <bes filter>: boolean	baseline flag	baseline flags	baseline flag	0	boolean	bes filter	
e0	baseline flag of <bes fixlet>: boolean	baseline flag	baseline flags	baseline flag	0	boolean	bes fixlet	
e0	baseline set of <bes filter>: bes fixlet set	baseline set	baseline sets	baseline set	0	bes fixlet set	bes filter	
10	batch group: security account	batch group	batch groups	batch group	0	security account		
10	bcc of <email task action>: string	bcc	bccs	bcc	0	string	email task action	
10	below normal priority: priority class	below normal priority	below normal priorities	below normal priority	0	priority class		
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
1f	big endian of <operating system>: boolean	big endian	big endians	big endian	0	boolean	operating system	
ff	big of <html>: html	big	bigs	big	0	html	html	
ff	big of <string>: html	big	bigs	big	0	html	string	
e0	bin at <time> of <statistic range>: statistical bin	bin at	bins at	bin at	0	statistical bin	statistic range	time
1d	binary location of <filesystem object>: binary_string	binary location	binary locations	binary location	0	binary_string	filesystem object	
1f	binary name of <filesystem object>: binary_string	binary name	binary names	binary name	0	binary_string	filesystem object	
1f	binary named files of <folder>: file	binary named file	binary named files	binary named files	1	file	folder	
1f	binary named folders of <folder>: folder	binary named folder	binary named folders	binary named folders	1	folder	folder	
ff	binary operators <string>: binary operator	binary operator	binary operators	binary operators	1	binary operator		string
ff	binary operators returning <type>: binary operator	binary operator returning	binary operators returning	binary operators returning	1	binary operator		type
ff	binary operators: binary operator	binary operator	binary operators	binary operators	1	binary operator		
1d	binary pathname of <filesystem object>: binary_string	binary pathname	binary pathnames	binary pathname	0	binary_string	filesystem object	
ff	binary_string <string>: binary_string	binary_string	binary_strings	binary_string	0	binary_string		string
ff	binary_substring <( integer, integer )> of <binary_string>: binary_substring	binary_substring	binary_substrings	binary_substring	0	binary_substring	binary_string	( integer, integer )
ff	binary_substrings <binary_string> of <binary_string>: binary_substring	binary_substring	binary_substrings	binary_substrings	1	binary_substring	binary_string	binary_string
e0	bins of <statistic range>: statistical bin	bin	bins	bins	1	statistical bin	statistic range	
1f	bios: bios	bios	bioses	bios	0	bios		
1f	bios_characteristics of <dmi bios_information>: integer	bios_characteristics	bios_characteristicss	bios_characteristics	0	integer	dmi bios_information	
1f	bios_information <integer> of <dmi>: dmi bios_information	bios_information	bios_informations	bios_information	0	dmi bios_information	dmi	integer
1f	bios_informations of <dmi>: dmi bios_information	bios_information	bios_informations	bios_informations	1	dmi bios_information	dmi	
1f	bios_language_information <integer> of <dmi>: dmi bios_language_information	bios_language_information	bios_language_informations	bios_language_information	0	dmi bios_language_information	dmi	integer
1f	bios_language_informations of <dmi>: dmi bios_language_information	bios_language_information	bios_language_informations	bios_language_informations	1	dmi bios_language_information	dmi	
1f	bios_release_date of <dmi bios_information>: string	bios_release_date	bios_release_dates	bios_release_date	0	string	dmi bios_information	
1f	bios_rom_size of <dmi bios_information>: integer	bios_rom_size	bios_rom_sizes	bios_rom_size	0	integer	dmi bios_information	
1f	bios_starting_address_segment of <dmi bios_information>: integer	bios_starting_address_segment	bios_starting_address_segments	bios_starting_address_segment	0	integer	dmi bios_information	
1f	bios_version of <dmi bios_information>: string	bios_version	bios_versions	bios_version	0	string	dmi bios_information	
ff	bit <integer> of <bit set>: boolean	bit	bits	bit	0	boolean	bit set	integer
ff	bit <integer> of <integer>: boolean	bit	bits	bit	0	boolean	integer	integer
5f	bit <integer> of <large integer>: boolean	bit	bits	bit	0	boolean	large integer	integer
5f	bit <integer> of <uinteger>: boolean	bit	bits	bit	0	boolean	uinteger	integer
ff	bit <integer>: bit set	bit	bits	bit	0	bit set		integer
ff	bit set <string>: bit set	bit set	bit sets	bit set	0	bit set		string
2	blackhole flag of <route>: boolean	blackhole flag	blackhole flags	blackhole flag	0	boolean	route	
10	blade bit <operating system suite mask>: boolean	blade bit	blade bits	blade bit	0	boolean		operating system suite mask
1f	blob of <sqlite column type>: boolean	blob	blobs	blob	0	boolean	sqlite column type	
12	block firewall action: firewall action	block firewall action	block firewall actions	block firewall action	0	firewall action		
d	block list of <grub file location>: grub block list	block list	block lists	block list	0	grub block list	grub file location	
d	block size of <filesystem>: integer	block size	block sizes	block size	0	integer	filesystem	
ff	blockquote <string> of <html>: html	blockquote	blockquotes	blockquote	0	html	html	string
ff	blockquote <string> of <string>: html	blockquote	blockquotes	blockquote	0	html	string	string
ff	blockquote of <html>: html	blockquote	blockquotes	blockquote	0	html	html	
ff	blockquote of <string>: html	blockquote	blockquotes	blockquote	0	html	string	
1f	board_type of <dmi base_board_information>: integer	board_type	board_types	board_type	0	integer	dmi base_board_information	
ff	body <string> of <html>: html	body	bodys	body	0	html	html	string
ff	body <string> of <string>: html	body	bodys	body	0	html	string	string
e0	body of <bes fixlet>: html	body	bodies	body	0	html	bes fixlet	
10	body of <email task action>: string	body	bodies	body	0	string	email task action	
ff	body of <html>: html	body	bodys	body	0	html	html	
ff	body of <string>: html	body	bodys	body	0	html	string	
d	bogomips of <processor>: integer	bogomips	bogomipses	bogomips	0	integer	processor	
2	boolean <integer> of <array>: boolean	boolean	booleans	boolean	0	boolean	array	integer
2	boolean <string> of <dictionary>: boolean	boolean	booleans	boolean	0	boolean	dictionary	string
2	boolean <string> of <preference>: boolean	boolean	booleans	boolean	0	boolean	preference	string
ff	boolean <string>: boolean	boolean	booleans	boolean	0	boolean		string
2	boolean of <osxvalue>: boolean	boolean	booleans	boolean	0	boolean	osxvalue	
10	boolean value <integer> of <wmi select>: boolean	boolean value	boolean values	boolean value	0	boolean	wmi select	integer
10	boolean values of <wmi select>: boolean	boolean value	boolean values	boolean values	1	boolean	wmi select	
d	boot argument <integer> of <grub kernel>: string	boot argument	boot arguments	boot argument	0	string	grub kernel	integer
d	boot arguments of <grub kernel>: string	boot argument	boot arguments	boot arguments	1	string	grub kernel	
10	boot task trigger type: task trigger type	boot task trigger type	boot task trigger types	boot task trigger type	0	task trigger type		
1f	boot time of <operating system>: time	boot time	boot times	boot time	0	time	operating system	
d	bootable image <integer> of <grub config file>: grub bootable image	bootable image	bootable images	bootable image	0	grub bootable image	grub config file	integer
d	bootable image <string> of <grub config file>: grub bootable image	bootable image	bootable images	bootable image	0	grub bootable image	grub config file	string
d	bootable images of <grub config file>: grub bootable image	bootable image	bootable images	bootable images	1	grub bootable image	grub config file	
1f	bootup_state of <dmi system_enclosure_or_chassis>: integer	bootup_state	bootup_states	bootup_state	0	integer	dmi system_enclosure_or_chassis	
ff	br <string>: html	br	brs	br	0	html		string
ff	br: html	br	brs	br	0	html		
12	brand id of <processor>: integer	brand id	brand ids	brand id	0	integer	processor	
1f	brand of <client>: string	brand	brands	brand	0	string	client	
1f	brand string of <processor>: string	brand string	brand strings	brand string	0	string	processor	
1f	broadcast address of <network adapter interface>: ipv4or6 address	broadcast address	broadcast addresses	broadcast address	0	ipv4or6 address	network adapter interface	
2	broadcast address of <network adapter>: ipv4 address	broadcast address	broadcast addresses	broadcast address	0	ipv4 address	network adapter	
1f	broadcast address of <network ip interface>: ipv4 address	broadcast address	broadcast addresses	broadcast address	0	ipv4 address	network ip interface	
2	broadcast flag of <route>: boolean	broadcast flag	broadcast flags	broadcast flag	0	boolean	route	
1f	broadcast support of <network adapter interface>: boolean	broadcast support	broadcast supports	broadcast support	0	boolean	network adapter interface	
2	broadcast support of <network adapter>: boolean	broadcast support	broadcast supports	broadcast support	0	boolean	network adapter	
1f	broadcast support of <network ip interface>: boolean	broadcast support	broadcast supports	broadcast support	0	boolean	network ip interface	
12	bssid of <wifi network>: string	bssid	bssids	bssid	0	string	wifi network	
d	buffered amount of <ram>: integer	buffered amount	buffered amounts	buffered amount	0	integer	ram	
2	bug revision of <version>: integer	bug revision	bug revisions	bug revision	0	integer	version	
1f	build number high of <operating system>: integer	build number high	build number highs	build number high	0	integer	operating system	
1f	build number low of <operating system>: integer	build number low	build number lows	build number low	0	integer	operating system	
1f	build number of <operating system>: integer	build number	build numbers	build number	0	integer	operating system	
1f	build of <operating system>: string	build	builds	build	0	string	operating system	
ff	build revision of <version>: integer	build revision	build revisions	build revision	0	integer	version	
1f	build target of <client>: string	build target	build targets	build target	0	string	client	
10	built in of <firewall open port>: boolean	built in	built ins	built in	0	boolean	firewall open port	
1f	built_in_pointing_device <integer> of <dmi>: dmi built_in_pointing_device	built_in_pointing_device	built_in_pointing_devices	built_in_pointing_device	0	dmi built_in_pointing_device	dmi	integer
1f	built_in_pointing_devices of <dmi>: dmi built_in_pointing_device	built_in_pointing_device	built_in_pointing_devices	built_in_pointing_devices	1	dmi built_in_pointing_device	dmi	
10	builtin administrators group: security account	builtin administrators group	builtin administrators groups	builtin administrators group	0	security account		
10	builtin backup operators group: security account	builtin backup operators group	builtin backup operators groups	builtin backup operators group	0	security account		
10	builtin guests group: security account	builtin guests group	builtin guests groups	builtin guests group	0	security account		
10	builtin network configuration operators group: security account	builtin network configuration operators group	builtin network configuration operators groups	builtin network configuration operators group	0	security account		
10	builtin power users group: security account	builtin power users group	builtin power users groups	builtin power users group	0	security account		
10	builtin remote desktop users group: security account	builtin remote desktop users group	builtin remote desktop users groups	builtin remote desktop users group	0	security account		
10	builtin replicator group: security account	builtin replicator group	builtin replicator groups	builtin replicator group	0	security account		
10	builtin users group: security account	builtin users group	builtin users groups	builtin users group	0	security account		
2	bundle <string>: bundle	bundle	bundles	bundle	0	bundle		string
2	bundle of <folder>: bundle	bundle	bundles	bundle	0	bundle	folder	
2	bundle version of <bundle>: version	bundle version	bundle versions	bundle version	0	version	bundle	
2	bundle version of <filesystem object>: version	bundle version	bundle versions	bundle version	0	version	filesystem object	
2	bundle version of <folder>: version	bundle version	bundle versions	bundle version	0	version	folder	
1f	bus_number of <dmi onboard_devices_extended_information>: integer	bus_number	bus_numbers	bus_number	0	integer	dmi onboard_devices_extended_information	
1f	bus_number of <dmi system_slots>: integer	bus_number	bus_numbers	bus_number	0	integer	dmi system_slots	
ff	byte <integer> of <binary_string>: binary_substring	byte	bytes	byte	0	binary_substring	binary_string	integer
1f	byte <integer> of <file>: integer	byte	bytes	byte	0	integer	file	integer
ff	byte <integer>: binary_string	byte	bytes	byte	0	binary_string		integer
ff	bytes of <binary_string>: binary_substring	byte	bytes	bytes	1	binary_substring	binary_string	
2	cache folder of <domain>: folder	cache folder	cache folders	cache folder	0	folder	domain	
2	cache folder: folder	cache folder	cache folders	cache folder	0	folder		
1f	cache_configuration of <dmi cache_information>: integer	cache_configuration	cache_configurations	cache_configuration	0	integer	dmi cache_information	
1f	cache_information <integer> of <dmi>: dmi cache_information	cache_information	cache_informations	cache_information	0	dmi cache_information	dmi	integer
1f	cache_informations of <dmi>: dmi cache_information	cache_information	cache_informations	cache_informations	1	dmi cache_information	dmi	
1f	cache_speed of <dmi cache_information>: integer	cache_speed	cache_speeds	cache_speed	0	integer	dmi cache_information	
d	cached amount of <ram>: integer	cached amount	cached amounts	cached amount	0	integer	ram	
e0	can create actions flag of <bes user>: boolean	can create actions flag	can create actions flags	can create actions flag	0	boolean	bes user	
10	can interact with desktop of <service>: boolean	can interact with desktop	can interact with desktops	can interact with desktop	0	boolean	service	
e0	can lock flag of <bes user>: boolean	can lock flag	can lock flags	can lock flag	0	boolean	bes user	
e0	can send multiple refresh flag of <bes user>: boolean	can send multiple refresh flag	can send multiple refresh flags	can send multiple refresh flag	0	boolean	bes user	
e0	can submit queries flag of <bes role>: boolean	can submit queries flag	can submit queries flags	can submit queries flag	0	boolean	bes role	
e0	can submit queries flag of <bes user>: boolean	can submit queries flag	can submit queries flags	can submit queries flag	0	boolean	bes user	
12	capabilities of <agent interface>: agent interface capability	capability	capabilities	capabilities	1	agent interface capability	agent interface	
1f	capabilities of <dmi system_reset>: integer	capabilities	capabilitiess	capabilities	0	integer	dmi system_reset	
12	capability <string> of <agent interface>: agent interface capability	capability	capabilities	capability	0	agent interface capability	agent interface	string
4	capability <string> of <rpmdatabase>: capability	capability	capabilities	capability	0	capability	rpmdatabase	string
4	capability <string>: capability	capability	capabilities	capability	0	capability		string
ff	caption <string> of <html>: html	caption	captions	caption	0	html	html	string
ff	caption <string> of <string>: html	caption	captions	caption	0	html	string	string
ff	caption of <html>: html	caption	captions	caption	0	html	html	
ff	caption of <string>: html	caption	captions	caption	0	html	string	
2	carbon folder of <domain>: folder	carbon folder	carbon folders	carbon folder	0	folder	domain	
2	carbon folder: folder	carbon folder	carbon folders	carbon folder	0	folder		
1f	case insensitive perl regexes <string>: regular expression	case insensitive perl regex	case insensitive perl regexes	case insensitive perl regexes	1	regular expression		string
1f	case insensitive perl regular expressions <string>: regular expression	case insensitive perl regular expression	case insensitive perl regular expressions	case insensitive perl regular expressions	1	regular expression		string
ff	case insensitive regexes <string>: regular expression	case insensitive regex	case insensitive regexes	case insensitive regexes	1	regular expression		string
ff	case insensitive regular expressions <string>: regular expression	case insensitive regular expression	case insensitive regular expressions	case insensitive regular expressions	1	regular expression		string
ff	casts <string>: cast	cast	casts	casts	1	cast		string
ff	casts from of <type>: cast	cast from	casts from	casts from	1	cast	type	
ff	casts returning <type>: cast	cast returning	casts returning	casts returning	1	cast		type
ff	casts: cast	cast	casts	casts	1	cast		
10	categories of <audit policy>: audit policy category	category	categories	categories	1	audit policy category	audit policy	
e0	category of <bes fixlet>: string	category	categories	category	0	string	bes fixlet	
e0	category of <bes property>: string	category	categories	category	0	string	bes property	
10	category of <event log record>: integer	category	categories	category	0	integer	event log record	
2	category of <os log entry log>: string	category	categories	category	0	string	os log entry log	
10	cc of <email task action>: string	cc	ccs	cc	0	string	email task action	
1f	certificate of <client>: x509 certificate	certificate	certificates	certificate	0	x509 certificate	client	
d	chainloader of <grub bootable image>: grub file location	chainloader	chainloaders	chainloader	0	grub file location	grub bootable image	
10	change notification permission of <access control entry>: boolean	change notification permission	change notification permissions	change notification permission	0	boolean	access control entry	
d	change time of <filesystem object>: time	change time	change times	change time	0	time	filesystem object	
d	change time of <symlink>: time	change time	change times	change time	0	time	symlink	
12	channel band of <wifi network>: string	channel band	channel bands	channel band	0	string	wifi network	
12	channel number of <wifi network>: integer	channel number	channel numbers	channel number	0	integer	wifi network	
1f	channel_type of <dmi memory_channel>: integer	channel_type	channel_types	channel_type	0	integer	dmi memory_channel	
ff	character <integer> of <string>: substring	character	characters	character	0	substring	string	integer
ff	character <integer>: string	character	characters	character	0	string		integer
1f	character sets of <client>: string	character set	character sets	character sets	1	string	client	
ff	characters of <string>: substring	character	characters	characters	1	substring	string	
e0	charset of <bes fixlet>: string	charset	charsets	charset	0	string	bes fixlet	
e0	charset of <bes wizard>: string	charset	charsets	charset	0	string	bes wizard	
1f	chassis_handle of <dmi base_board_information>: integer	chassis_handle	chassis_handles	chassis_handle	0	integer	dmi base_board_information	
10	checkpoint of <service>: integer	checkpoint	checkpoints	checkpoint	0	integer	service	
2	chewable items folder of <domain>: folder	chewable items folder	chewable items folders	chewable items folder	0	folder	domain	
2	chewable items folder: folder	chewable items folder	chewable items folders	chewable items folder	0	folder		
bd	child node <integer> of <xml dom node>: xml dom node	child node	child nodes	child node	0	xml dom node	xml dom node	integer
bd	child nodes of <xml dom node>: xml dom node	child node	child nodes	child nodes	1	xml dom node	xml dom node	
1f	cidr address of <network adapter interface>: string	cidr address	cidr addresses	cidr address	0	string	network adapter interface	
1f	cidr address of <network adapter>: string	cidr address	cidr addresses	cidr address	0	string	network adapter	
10	cidr address of <network address list>: string	cidr address	cidr addresses	cidr address	0	string	network address list	
1f	cidr address of <network ip interface>: string	cidr address	cidr addresses	cidr address	0	string	network ip interface	
1f	cidr string of <network adapter interface>: string	cidr string	cidr strings	cidr string	0	string	network adapter interface	
1f	cidr string of <network adapter>: string	cidr string	cidr strings	cidr string	0	string	network adapter	
10	cidr string of <network address list>: string	cidr string	cidr strings	cidr string	0	string	network address list	
1f	cidr string of <network ip interface>: string	cidr string	cidr strings	cidr string	0	string	network ip interface	
1f	cidr subnet <string>: cidr subnet	cidr subnet	cidr subnets	cidr subnet	0	cidr subnet		string
1f	cidr subnet of <network adapter interface>: cidr subnet	cidr subnet	cidr subnets	cidr subnet	0	cidr subnet	network adapter interface	
1f	cidr subnet of <network adapter>: cidr subnet	cidr subnet	cidr subnets	cidr subnet	0	cidr subnet	network adapter	
10	cidr subnet of <network address list>: cidr subnet	cidr subnet	cidr subnets	cidr subnet	0	cidr subnet	network address list	
1f	cidr subnet of <network ip interface>: cidr subnet	cidr subnet	cidr subnets	cidr subnet	0	cidr subnet	network ip interface	
ff	cite <string> of <html>: html	cite	cites	cite	0	html	html	string
ff	cite <string> of <string>: html	cite	cites	cite	0	html	string	string
ff	cite of <html>: html	cite	cites	cite	0	html	html	
ff	cite of <string>: html	cite	cites	cite	0	html	string	
10	class id of <com handler task action>: string	class id	class ids	class id	0	string	com handler task action	
10	class of <active device>: string	class	classes	class	0	string	active device	
2	classic domain: domain	classic domain	classic domains	classic domain	0	domain		
2	classic folder of <domain>: folder	classic folder	classic folders	classic folder	0	folder	domain	
2	classic folder: folder	classic folder	classic folders	classic folder	0	folder		
2	classname of <registrynode>: string	classname	classnames	classname	0	string	registrynode	
1f	client cryptography: client_cryptography	client cryptography	client cryptographies	client cryptography	0	client_cryptography		
ff	client device count of <bes product>: integer	client device count	client device counts	client device count	0	integer	bes product	
e0	client evaluated flag of <bes computer group>: boolean	client evaluated flag	client evaluated flags	client evaluated flag	0	boolean	bes computer group	
1f	client folder of <site>: folder	client folder	client folders	client folder	0	folder	site	
40	client id of <bes idp directory>: string	client id	client ids	client id	0	string	bes idp directory	
e0	client installed flag of <bes unmanagedasset>: boolean	client installed flag	client installed flags	client installed flag	0	boolean	bes unmanagedasset	
ff	client license: license	client license	client licenses	client license	0	license		
12	client product of <agent interface>: string	client product	client products	client product	0	string	agent interface	
1f	client query duration of <evaluation cycle>: time interval	client query duration	client query durations	client query duration	0	time interval	evaluation cycle	
1f	client query percent of <evaluation cycle>: floating point	client query percent	client query percents	client query percent	0	floating point	evaluation cycle	
e0	client settings of <bes computer>: bes client setting	client setting	client settings	client settings	1	bes client setting	bes computer	
1f	client: client	client	clients	client	0	client		
2	cloned of <route>: boolean	cloned	cloneds	cloned	0	boolean	route	
2	cloning flag of <route>: boolean	cloning flag	cloning flags	cloning flag	0	boolean	route	
1f	close wait of <tcp state>: boolean	close wait	close waits	close wait	0	boolean	tcp state	
1f	closed of <tcp state>: boolean	closed	closeds	closed	0	boolean	tcp state	
1f	closing of <tcp state>: boolean	closing	closings	closing	0	boolean	tcp state	
ff	cloud count of <bes product>: integer	cloud count	cloud counts	cloud count	0	integer	bes product	
1f	cloud provider: cloud provider	cloud provider	cloud providers	cloud provider	0	cloud provider		
ff	code <string> of <html>: html	code	codes	code	0	html	html	string
ff	code <string> of <string>: html	code	codes	code	0	html	string	string
ff	code of <html>: html	code	codes	code	0	html	html	
ff	code of <string>: html	code	codes	code	0	html	string	
10	code page of <user>: integer	code page	code pages	code page	0	integer	user	
f	codename of <operating system>: string	codename	codenames	codename	0	string	operating system	
10	codepage of <file version block>: string	codepage	codepages	codepage	0	string	file version block	
ff	col <string> of <html>: html	col	cols	col	0	html	html	string
ff	col <string> of <string>: html	col	cols	col	0	html	string	string
ff	col of <html>: html	col	cols	col	0	html	html	
ff	col of <string>: html	col	cols	col	0	html	string	
ff	colgroup <string> of <html>: html	colgroup	colgroups	colgroup	0	html	html	string
ff	colgroup <string> of <string>: html	colgroup	colgroups	colgroup	0	html	string	string
ff	colgroup of <html>: html	colgroup	colgroups	colgroup	0	html	html	
ff	colgroup of <string>: html	colgroup	colgroups	colgroup	0	html	string	
d	color scheme of <grub config file>: grub color scheme	color scheme	color schemes	color scheme	0	grub color scheme	grub config file	
2	color sync folder of <domain>: folder	color sync folder	color sync folders	color sync folder	0	folder	domain	
2	color sync folder: folder	color sync folder	color sync folders	color sync folder	0	folder		
2	colorsync profiles folder of <domain>: folder	colorsync profiles folder	colorsync profiles folders	colorsync profiles folder	0	folder	domain	
2	colorsync profiles folder: folder	colorsync profiles folder	colorsync profiles folders	colorsync profiles folder	0	folder		
1f	column <integer> of <sqlite row>: sqlite column	column	columns	column	0	sqlite column	sqlite row	integer
1f	column <string> of <sqlite row>: sqlite column	column	columns	column	0	sqlite column	sqlite row	string
1f	column type <integer> of <sqlite table>: sqlite column type	column type	column types	column type	0	sqlite column type	sqlite table	integer
1f	column type <string> of <sqlite table>: sqlite column type	column type	column types	column type	0	sqlite column type	sqlite table	string
1f	column types of <sqlite table>: sqlite column type	column type	column types	column types	1	sqlite column type	sqlite table	
10	com handler task action type: task action type	com handler task action type	com handler task action types	com handler task action type	0	task action type		
d	coma bug of <processor>: boolean	coma bug	coma bugs	coma bug	0	boolean	processor	
d	command line argument <integer> of <process>: string	command line argument	command line arguments	command line argument	0	string	process	integer
d	command line arguments of <process>: string	command line argument	command line arguments	command line arguments	1	string	process	
10	comment of <local group>: string	comment	comments	comment	0	string	local group	
10	comment of <network share>: string	comment	comments	comment	0	string	network share	
12	comment of <user>: string	comment	comments	comment	0	string	user	
e0	comments of <bes action>: bes comment	comment	comments	comments	1	bes comment	bes action	
e0	comments of <bes computer>: bes comment	comment	comments	comments	1	bes comment	bes computer	
e0	comments of <bes fixlet>: bes comment	comment	comments	comments	1	bes comment	bes fixlet	
ff	common name of <license>: string	common name	common names	common name	0	string	license	
10	communications bit <operating system suite mask>: boolean	communications bit	communications bits	communications bit	0	boolean		operating system suite mask
10	communications operator flag of <user>: boolean	communications operator flag	communications operator flags	communications operator flag	0	boolean	user	
9	compare_op of <debianpkg dependency>: string	compare_op	compare_ops	compare_op	0	string	debianpkg dependency	
1f	competition size of <selected server>: integer	competition size	competition sizes	competition size	0	integer	selected server	
1f	competition weight of <selected server>: integer	competition weight	competition weights	competition weight	0	integer	selected server	
1f	complete time of <action>: time	complete time	complete times	complete time	0	time	action	
b0	component <integer> of <distinguished name>: distinguished name component	component	components	component	0	distinguished name component	distinguished name	integer
ff	component <integer> of <site version list>: integer	component	components	component	0	integer	site version list	integer
2	component folder of <domain>: folder	component folder	component folders	component folder	0	folder	domain	
2	component folder: folder	component folder	component folders	component folder	0	folder		
e0	component groups of <bes fixlet>: bes baseline component group	component group	component groups	component groups	1	bes baseline component group	bes fixlet	
12	component string of <security identifier>: string	component string	component strings	component string	0	string	security identifier	
1f	component_handle of <dmi management_device_component>: integer	component_handle	component_handles	component_handle	0	integer	dmi management_device_component	
e0	components of <bes baseline component group>: bes baseline component	component	components	components	1	bes baseline component	bes baseline component group	
b0	components of <distinguished name>: distinguished name component	component	components	components	1	distinguished name component	distinguished name	
e0	components xml of <bes fixlet>: string	components xml	components xmls	components xml	0	string	bes fixlet	
2	components: component	component	components	components	1	component		
2	composed message of <os log entry log>: string	composed message	composed messages	composed message	0	string	os log entry log	
10	compressed of <filesystem object>: boolean	compressed	compresseds	compressed	0	boolean	filesystem object	
ff	computer count of <bes product>: integer	computer count	computer counts	computer count	0	integer	bes product	
e0	computer flag of <bes filter>: boolean	computer flag	computer flags	computer flag	0	boolean	bes filter	
e0	computer group flag of <bes action>: boolean	computer group flag	computer group flags	computer group flag	0	boolean	bes action	
e0	computer group set of <bes domain>: bes computer group set	computer group set	computer group sets	computer group set	0	bes computer group set	bes domain	
e0	computer group set of <bes filter>: bes fixlet set	computer group set	computer group sets	computer group set	0	bes fixlet set	bes filter	
e0	computer groups of <bes domain>: bes computer group	computer group	computer groups	computer groups	1	bes computer group	bes domain	
1f	computer id: integer	computer id	computer ids	computer id	0	integer		
1f	computer name: string	computer name	computer names	computer name	0	string		
e0	computer of <bes action result>: bes computer	computer	computers	computer	0	bes computer	bes action result	
e0	computer of <bes fixlet result>: bes computer	computer	computers	computer	0	bes computer	bes fixlet result	
e0	computer of <bes property result>: bes computer	computer	computers	computer	0	bes computer	bes property result	
10	computer of <event log record>: string	computer	computers	computer	0	string	event log record	
e0	computer set of <bes filter>: bes computer set	computer set	computer sets	computer set	0	bes computer set	bes filter	
2	computer: computer	computer	computers	computer	0	computer		
ff	concatenations <html> of <html>: html	concatenation	concatenations	concatenations	1	html	html	html
ff	concatenations <html> of <string>: html	concatenation	concatenations	concatenations	1	html	string	html
ff	concatenations <string> of <html>: html	concatenation	concatenations	concatenations	1	html	html	string
ff	concatenations <string> of <string>: string	concatenation	concatenations	concatenations	1	string	string	string
ff	concatenations of <html>: html	concatenation	concatenations	concatenations	1	html	html	
ff	concatenations of <string>: string	concatenation	concatenations	concatenations	1	string	string	
2	condemned flag of <route>: boolean	condemned flag	condemned flags	condemned flag	0	boolean	route	
4	conflicts of <package>: capability	conflict	conflicts	conflicts	1	capability	package	
ff	conjunctions of <boolean>: boolean	conjunction	conjunctions	conjunctions	1	boolean	boolean	
10	connection status <integer>: connection status	connection status	connection statuses	connection status	0	connection status		integer
10	connection status authenticating: connection status	connection status authenticating	connection statuses authenticating	connection status authenticating	0	connection status		
10	connection status authentication failed: connection status	connection status authentication failed	connection statuses authentication failed	connection status authentication failed	0	connection status		
10	connection status authentication succeeded: connection status	connection status authentication succeeded	connection statuses authentication succeeded	connection status authentication succeeded	0	connection status		
10	connection status connected: connection status	connection status connected	connection statuses connected	connection status connected	0	connection status		
10	connection status connecting: connection status	connection status connecting	connection statuses connecting	connection status connecting	0	connection status		
10	connection status disconnected: connection status	connection status disconnected	connection statuses disconnected	connection status disconnected	0	connection status		
10	connection status disconnecting: connection status	connection status disconnecting	connection statuses disconnecting	connection status disconnecting	0	connection status		
10	connection status hardware disabled: connection status	connection status hardware disabled	connection statuses hardware disabled	connection status hardware disabled	0	connection status		
10	connection status hardware malfunction: connection status	connection status hardware malfunction	connection statuses hardware malfunction	connection status hardware malfunction	0	connection status		
10	connection status media disconnected: connection status	connection status media disconnected	connection statuses media disconnected	connection status media disconnected	0	connection status		
10	connection status no hardware present: connection status	connection status no hardware present	connection statuses no hardware present	connection status no hardware present	0	connection status		
1f	connections of <dmi out_of_band_remote_access>: integer	connections	connectionss	connections	0	integer	dmi out_of_band_remote_access	
10	connections of <network>: connection	connection	connections	connections	1	connection	network	
10	console connect of <session state change task trigger>: boolean	console connect	console connects	console connect	0	boolean	session state change task trigger	
10	console disconnect of <session state change task trigger>: boolean	console disconnect	console disconnects	console disconnect	0	boolean	session state change task trigger	
e0	constrain by property name of <bes action>: string	constrain by property name	constrain by property names	constrain by property name	0	string	bes action	
e0	constrain by property relation of <bes action>: string	constrain by property relation	constrain by property relations	constrain by property relation	0	string	bes action	
e0	constrain by property value of <bes action>: string	constrain by property value	constrain by property values	constrain by property value	0	string	bes action	
1f	constrained of <action>: boolean	constrained	constraineds	constrained	0	boolean	action	
1f	constraint of <action>: integer	constraint	constraints	constraint	0	integer	action	
1f	contained_element_count of <dmi system_enclosure_or_chassis>: integer	contained_element_count	contained_element_counts	contained_element_count	0	integer	dmi system_enclosure_or_chassis	
1f	contained_element_record_length of <dmi system_enclosure_or_chassis>: integer	contained_element_record_length	contained_element_record_lengths	contained_element_record_length	0	integer	dmi system_enclosure_or_chassis	
10	container inherit of <access control entry>: boolean	container inherit	container inherits	container inherit	0	boolean	access control entry	
e0	content id of <bes fixlet action>: string	content id	content ids	content id	0	string	bes fixlet action	
1f	content of <file>: file content	content	contents	content	0	file content	file	
2	contextual menu items folder of <domain>: folder	contextual menu items folder	contextual menu items folders	contextual menu items folder	0	folder	domain	
2	contextual menu items folder: folder	contextual menu items folder	contextual menu items folders	contextual menu items folder	0	folder		
e0	continue on errors flag of <bes action>: boolean	continue on errors flag	continue on errors flags	continue on errors flag	0	boolean	bes action	
10	control of <security descriptor>: integer	control	controls	control	0	integer	security descriptor	
2	control panels <string>: enableable_file	control panel	control panels	control panels	1	enableable_file		string
2	control panels folder of <domain>: folder	control panels folder	control panels folders	control panels folder	0	folder	domain	
2	control panels folder: folder	control panels folder	control panels folders	control panels folder	0	folder		
2	control panels: enableable_file	control panel	control panels	control panels	1	enableable_file		
2	control strip modules folder of <domain>: folder	control strip modules folder	control strip modules folders	control strip modules folder	0	folder	domain	
2	control strip modules folder: folder	control strip modules folder	control strip modules folders	control strip modules folder	0	folder		
1f	controller of <action lock state>: string	controller	controllers	controller	0	string	action lock state	
1f	cooling_device <integer> of <dmi>: dmi cooling_device	cooling_device	cooling_devices	cooling_device	0	dmi cooling_device	dmi	integer
1f	cooling_device_handle of <dmi system_power_supply>: integer	cooling_device_handle	cooling_device_handles	cooling_device_handle	0	integer	dmi system_power_supply	
1f	cooling_devices of <dmi>: dmi cooling_device	cooling_device	cooling_devices	cooling_devices	1	dmi cooling_device	dmi	
1f	cooling_unit_group of <dmi cooling_device>: integer	cooling_unit_group	cooling_unit_groups	cooling_unit_group	0	integer	dmi cooling_device	
1f	core of <cpupackage>: integer	core	cores	core	0	integer	cpupackage	
2	core services folder of <domain>: folder	core services folder	core services folders	core services folder	0	folder	domain	
2	core services folder: folder	core services folder	core services folders	core services folder	0	folder		
1f	core_count of <dmi processor_information>: integer	core_count	core_counts	core_count	0	integer	dmi processor_information	
1f	core_enabled of <dmi processor_information>: integer	core_enabled	core_enableds	core_enabled	0	integer	dmi processor_information	
e2	correlation coefficient of <exponential projection>: floating point	correlation coefficient	correlation coefficients	correlation coefficient	0	floating point	exponential projection	
e2	correlation coefficient of <linear projection>: floating point	correlation coefficient	correlation coefficients	correlation coefficient	0	floating point	linear projection	
e0	correlation flag of <bes computer>: boolean	correlation flag	correlation flags	correlation flag	0	boolean	bes computer	
e0	correlation id of <bes computer>: integer	correlation id	correlation ids	correlation id	0	integer	bes computer	
e0	correlation of <bes computer>: bes computer	correlation	correlations	correlation	0	bes computer	bes computer	
e0	count maps of <historical fixlet count>: fixlet count pair	count map	count maps	count maps	1	fixlet count pair	historical fixlet count	
1f	count of <cpupackage>: integer	count	counts	count	0	integer	cpupackage	
e0	count of <fixlet count pair>: integer	count	counts	count	0	integer	fixlet count pair	
e0	count of <historical computer count>: integer	count	counts	count	0	integer	historical computer count	
12	count of <monitor power interval>: integer	count	counts	count	0	integer	monitor power interval	
2	country <string>: country	country	countries	country	0	country		string
10	country code of <user>: integer	country code	country codes	country code	0	integer	user	
e0	cpu of <bes computer>: string	cpu	cpus	cpu	0	string	bes computer	
2	cpu speed: integer	cpu speed	cpu speeds	cpu speed	0	integer		
d	cpuid level of <processor>: integer	cpuid level	cpuid levels	cpuid level	0	integer	processor	
1f	cpupackage: cpupackage	cpupackage	cpupackages	cpupackage	0	cpupackage		
10	create file permission of <access control entry>: boolean	create file permission	create file permissions	create file permission	0	boolean	access control entry	
10	create folder permission of <access control entry>: boolean	create folder permission	create folder permissions	create folder permission	0	boolean	access control entry	
10	create link permission of <access control entry>: boolean	create link permission	create link permissions	create link permission	0	boolean	access control entry	
10	create permission of <network share>: boolean	create permission	create permissions	create permission	0	boolean	network share	
10	create subkey permission of <access control entry>: boolean	create subkey permission	create subkey permissions	create subkey permission	0	boolean	access control entry	
e0	creation date of <bes site>: time	creation date	creation dates	creation date	0	time	bes site	
e0	creation time of <bes activation>: time	creation time	creation times	creation time	0	time	bes activation	
e0	creation time of <bes computer group>: time	creation time	creation times	creation time	0	time	bes computer group	
e0	creation time of <bes fixlet>: time	creation time	creation times	creation time	0	time	bes fixlet	
e0	creation time of <bes user>: time	creation time	creation times	creation time	0	time	bes user	
12	creation time of <filesystem object>: time	creation time	creation times	creation time	0	time	filesystem object	
10	creation time of <process>: time	creation time	creation times	creation time	0	time	process	
10	creator group group: security account	creator group group	creator group groups	creator group group	0	security account		
e0	creator of <bes site>: bes user	creator	creators	creator	0	bes user	bes site	
2	creator of <bundle>: file signature	creator	creators	creator	0	file signature	bundle	
2	creator of <file>: file signature	creator	creators	creator	0	file signature	file	
10	creator owner group: security account	creator owner group	creator owner groups	creator owner group	0	security account		
9	critical of <debianpkg dependency>: boolean	critical	criticals	critical	0	boolean	debianpkg dependency	
ff	cryptography: cryptography	cryptography	cryptographies	cryptography	0	cryptography		
10	csd version of <operating system>: string	csd version	csd versions	csd version	0	string	operating system	
10	csidl folder <integer>: folder	csidl folder	csidl folders	csidl folder	0	folder		integer
2	cstring <string> of <dictionary>: string	cstring	cstrings	cstring	0	string	dictionary	string
2	cstring of <osxvalue>: string	cstring	csrings	cstring	0	string	osxvalue	
10	current action of <running task>: string	current action	current actions	current action	0	string	running task	
e0	current analysis: bes fixlet	current analysis	current analyses	current analysis	0	bes fixlet		
1f	current analysis: fixlet	current analysis	current analyses	current analysis	0	fixlet		
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
10	current firewall profile type: firewall profile type	current firewall profile type	current firewall profile types	current firewall profile type	0	firewall profile type		
e0	current fixlet: bes fixlet	current fixlet	current fixlets	current fixlet	0	bes fixlet		
12	current monitor interval of <power history>: monitor power interval	current monitor interval	current monitor intervals	current monitor interval	0	monitor power interval	power history	
ff	current month: month	current month	current months	current month	0	month		
ff	current month_and_year: month and year	current month_and_year	current months_and_years	current month_and_year	0	month and year		
12	current network of <wifi>: wifi network	current network	current networks	current network	0	wifi network	wifi	
10	current profile of <firewall policy>: firewall profile	current profile	current profiles	current profile	0	firewall profile	firewall policy	
10	current profile type of <firewall>: firewall profile type	current profile type	current profile types	current profile type	0	firewall profile type	firewall	
1f	current relay: current relay	current relay	current relays	current relay	0	current relay		
1f	current site: site	current site	current sites	current site	0	site		
d	current status of <SELinux Boolean>: boolean	current status	current statuses	current status	0	boolean	SELinux Boolean	
12	current system interval of <power history>: system power interval	current system interval	current system intervals	current system interval	0	system power interval	power history	
e0	current task: bes fixlet	current task	current tasks	current task	0	bes fixlet		
ff	current time_of_day <time zone>: time of day with time zone	current time_of_day	current times_of_day	current time_of_day	0	time of day with time zone		time zone
ff	current time_of_day: time of day with time zone	current time_of_day	current times_of_day	current time_of_day	0	time of day with time zone		
e0	current unmanagedasset: bes unmanagedasset	current unmanagedasset	current unmanagedassets	current unmanagedasset	0	bes unmanagedasset		
2	current user folder of <domain>: folder	current user folder	current user folders	current user folder	0	folder	domain	
2	current user folder: folder	current user folder	current user folders	current user folder	0	folder		
10	current user key <logged on user> of <registry>: registry key	current user key	current user keys	current user key	0	registry key	registry	logged on user
10	current user key of <registry>: registry key	current user key	current user keys	current user key	0	registry key	registry	
1f	current user: logged on user	current user	current users	current user	0	logged on user		
e0	current wizard: bes wizard	current wizard	current wizards	current wizard	0	bes wizard		
ff	current year: year	current year	current years	current year	0	year		
1f	current_interleave of <dmi memory_controller_information>: integer	current_interleave	current_interleaves	current_interleave	0	integer	dmi memory_controller_information	
1f	current_language of <dmi bios_language_information>: string	current_language	current_languages	current_language	0	string	dmi bios_language_information	
1f	current_memory_type of <dmi memory_module_information>: integer	current_memory_type	current_memory_types	current_memory_type	0	integer	dmi memory_module_information	
1f	current_speed of <dmi memory_module_information>: integer	current_speed	current_speeds	current_speed	0	integer	dmi memory_module_information	
1f	current_speed of <dmi processor_information>: integer	current_speed	current_speeds	current_speed	0	integer	dmi processor_information	
1f	current_sram_type of <dmi cache_information>: integer	current_sram_type	current_sram_types	current_sram_type	0	integer	dmi cache_information	
1f	current_usage of <dmi system_slots>: integer	current_usage	current_usages	current_usage	0	integer	dmi system_slots	
10	currently active of <firewall rule>: boolean	currently active	currently actives	currently active	0	boolean	firewall rule	
9	currently installed of <debian base package>: boolean	currently installed	currently installeds	currently installed	0	boolean	debian base package	
9	currently installed of <debian versioned package>: boolean	currently installed	currently installeds	currently installed	0	boolean	debian versioned package	
e0	custom bes fixlet set: bes fixlet set	custom bes fixlet set	custom bes fixlet sets	custom bes fixlet set	0	bes fixlet set		
e0	custom bes fixlets: bes fixlet	custom bes fixlet	custom bes fixlets	custom bes fixlets	1	bes fixlet		
e0	custom content flag of <bes user>: boolean	custom content flag	custom content flags	custom content flag	0	boolean	bes user	
10	custom firewall scope: firewall scope	custom firewall scope	custom firewall scopes	custom firewall scope	0	firewall scope		
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
1f	custom site subscription effective date <string>: time	custom site subscription effective date	custom site subscription effective dates	custom site subscription effective date	0	time		string
e0	custom sites of <bes domain>: bes site	custom site	custom sites	custom sites	1	bes site	bes domain	
e0	custom success relevance of <bes action>: string	custom success relevance	custom success relevances	custom success relevance	0	string	bes action	
e0	custom success relevance of <bes fixlet action>: string	custom success relevance	custom success relevances	custom success relevance	0	string	bes fixlet action	
10	customized of <firewall service>: boolean	customized	customizeds	customized	0	boolean	firewall service	
e0	cve id list of <bes fixlet>: string	cve id list	cve id lists	cve id list	0	string	bes fixlet	
10	dacl of <security descriptor>: discretionary access control list	dacl	dacls	dacl	0	discretionary access control list	security descriptor	
10	daily task trigger type: task trigger type	daily task trigger type	daily task trigger types	daily task trigger type	0	task trigger type		
e0	dashboard id of <bes wizard>: string	dashboard id	dashboard ids	dashboard id	0	string	bes wizard	
2	data <string> of <dictionary>: binary_string	data	datas	data	0	binary_string	dictionary	string
10	data file of <site profile>: file	data file	data files	data file	0	file	site profile	
1f	data folder of <client>: folder	data folder	data folders	data folder	0	folder	client	
2	data fork of <file>: datafork	data fork	data forks	data fork	0	datafork	file	
10	data of <com handler task action>: string	data	datas	data	0	string	com handler task action	
2	data of <osxvalue>: binary_string	data	datas	data	0	binary_string	osxvalue	
10	data of <task definition>: string	data	datas	data	0	string	task definition	
1f	data_width of <dmi memory_device>: integer	data_width	data_widths	data_width	0	integer	dmi memory_device	
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
10	datacenter bit <operating system suite mask>: boolean	datacenter bit	datacenter bits	datacenter bit	0	boolean		operating system suite mask
e0	datastore inspector: module	datastore inspector	datastore inspectors	datastore inspector	0	module		
2	date <integer> of <array>: time	date	dates	date	0	time	array	integer
2	date <string> of <dictionary>: time	date	dates	date	0	time	dictionary	string
2	date <string> of <preference>: time	date	dates	date	0	time	preference	string
ff	date <string>: date	date	dates	date	0	date		string
ff	date <time zone> of <time>: date	date	dates	date	0	date	time	time zone
1f	date of <bios>: string	date	dates	date	0	string	bios	
2	date of <osxvalue>: time	date	dates	date	0	time	osxvalue	
10	date of <task registration info>: time	date	dates	date	0	time	task registration info	
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
10	days interval of <daily task trigger>: time interval	days interval	days intervals	days interval	0	time interval	daily task trigger	
10	days runs of <monthly task trigger>: day of month	days run	days runs	days runs	1	day of month	monthly task trigger	
10	days runs of <monthlydow task trigger>: day of week	days run	days runs	days runs	1	day of week	monthlydow task trigger	
10	days runs of <weekly task trigger>: day of week	days run	days runs	days runs	1	day of week	weekly task trigger	
ff	dd <string> of <html>: html	dd	dds	dd	0	html	html	string
ff	dd <string> of <string>: html	dd	dds	dd	0	html	string	string
ff	dd of <html>: html	dd	dds	dd	0	html	html	
ff	dd of <string>: html	dd	dds	dd	0	html	string	
9	debian package version <debian package version>: debian package version	debian package version	debian package versions	debian package version	0	debian package version		debian package version
9	debian package version <string>: debian package version	debian package version	debian package versions	debian package version	0	debian package version		string
9	debian package version epoch <debian package version epoch>: debian package version epoch	debian package version epoch	debian package version epochs	debian package version epoch	0	debian package version epoch		debian package version epoch
9	debian package version epoch <string>: debian package version epoch	debian package version epoch	debian package version epochs	debian package version epoch	0	debian package version epoch		string
9	debian package version revision <debian package version revision>: debian package version revision	debian package version revision	debian package version revisions	debian package version revision	0	debian package version revision		debian package version revision
9	debian package version revision <string>: debian package version revision	debian package version revision	debian package version revisions	debian package version revision	0	debian package version revision		string
9	debian package version upstream <debian package upstream version>: debian package upstream version	debian package version upstream	debian package version upstreams	debian package version upstream	0	debian package upstream version		debian package upstream version
9	debian package version upstream <string>: debian package upstream version	debian package version upstream	debian package version upstreams	debian package version upstream	0	debian package upstream version		string
9	debianpackage: debianpackagecache	debianpackage	debianpackages	debianpackage	0	debianpackagecache		
ff	december <integer> of <integer>: date	december	decembers	december	0	date	integer	integer
ff	december <integer>: day of year	december	decembers	december	0	day of year		integer
ff	december of <integer>: month and year	december	decembers	december	0	month and year	integer	
ff	december: month	december	decembers	december	0	month		
e0	default action of <bes fixlet>: bes fixlet action	default action	default actions	default action	0	bes fixlet action	bes fixlet	
e0	default flag of <bes property>: boolean	default flag	default flags	default flag	0	boolean	bes property	
d	default image of <grub config file>: grub image choice	default image	default images	default image	0	grub image choice	grub config file	
2	default of <route>: boolean	default	defaults	default	0	boolean	route	
e0	default page name of <bes wizard>: string	default page name	default page names	default page name	0	string	bes wizard	
10	default value of <registry key>: registry key value	default value	default values	default value	0	registry key value	registry key	
10	default web browser: application	default web browser	default web browsers	default web browser	0	application		
d	default web browser: file	default web browser	default web browsers	default web browser	0	file		
ff	definition lists <string> of <html>: html	definition list	definition lists	definition lists	1	html	html	string
ff	definition lists <string> of <string>: html	definition list	definition lists	definition lists	1	html	string	string
ff	definition lists of <html>: html	definition list	definition lists	definition lists	1	html	html	
ff	definition lists of <string>: html	definition list	definition lists	definition lists	1	html	string	
e0	definition of <bes property>: string	definition	definitions	definition	0	string	bes property	
10	definition of <scheduled task>: task definition	definition	definitions	definition	0	task definition	scheduled task	
ff	del <string> of <html>: html	del	dels	del	0	html	html	string
ff	del <string> of <string>: html	del	dels	del	0	html	string	string
ff	del of <html>: html	del	dels	del	0	html	html	
ff	del of <string>: html	del	dels	del	0	html	string	
10	delay of <boot task trigger>: time interval	delay	delays	delay	0	time interval	boot task trigger	
10	delay of <event task trigger>: time interval	delay	delays	delay	0	time interval	event task trigger	
10	delay of <logon task trigger>: time interval	delay	delays	delay	0	time interval	logon task trigger	
10	delay of <registration task trigger>: time interval	delay	delays	delay	0	time interval	registration task trigger	
10	delay of <session state change task trigger>: time interval	delay	delays	delay	0	time interval	session state change task trigger	
2	delclone flag of <route>: boolean	delclone flag	delclone flags	delclone flag	0	boolean	route	
10	delete child permission of <access control entry>: boolean	delete child permission	delete child permissions	delete child permission	0	boolean	access control entry	
10	delete expired task after of <task settings>: time interval	delete expired task after	delete expired task afters	delete expired task after	0	time interval	task settings	
10	delete permission of <access control entry>: boolean	delete permission	delete permissions	delete permission	0	boolean	access control entry	
10	delete permission of <network share>: boolean	delete permission	delete permissions	delete permission	0	boolean	network share	
1f	delete tcb of <tcp state>: boolean	delete tcb	delete tcbs	delete tcb	0	boolean	tcp state	
e0	deleted flag of <bes comment>: boolean	deleted flag	deleted flags	deleted flag	0	boolean	bes comment	
10	deny type of <access control entry>: boolean	deny type	deny types	deny type	0	boolean	access control entry	
10	dep enabled of <process>: boolean	dep enabled	dep enableds	dep enabled	0	boolean	process	
9	dependencies of <debian versioned package>: debianpkg dependency	dependency	dependencies	dependencies	1	debianpkg dependency	debian versioned package	
ff	dependency known of <property>: boolean	dependency known	dependencies known	dependency known	0	boolean	property	
1f	deployment character set of <client>: string	deployment character set	deployment character sets	deployment character set	0	string	client	
1f	descendant folders of <folder>: folder	descendant folder	descendant folders	descendant folders	1	folder	folder	
1f	descendants of <folder>: file	descendant	descendants	descendants	1	file	folder	
10	descendants of <task folder>: scheduled task	descendant	descendants	descendants	1	scheduled task	task folder	
10	description of <active device>: string	description	descriptions	description	0	string	active device	
e0	description of <bes site>: string	description	descriptions	description	0	string	bes site	
1f	description of <dmi electrical_current_probe>: string	description	descriptions	description	0	string	dmi electrical_current_probe	
1f	description of <dmi management_device>: string	description	descriptions	description	0	string	dmi management_device	
1f	description of <dmi management_device_component>: string	description	descriptions	description	0	string	dmi management_device_component	
1f	description of <dmi temperature_probe>: string	description	descriptions	description	0	string	dmi temperature_probe	
1f	description of <dmi voltage_probe>: string	description	descriptions	description	0	string	dmi voltage_probe	
10	description of <event log record>: string	description	descriptions	description	0	string	event log record	
10	description of <firewall rule>: string	description	descriptions	description	0	string	firewall rule	
10	description of <network adapter>: string	description	descriptions	description	0	string	network adapter	
10	description of <task registration info>: string	description	descriptions	description	0	string	task registration info	
1f	description_string of <dmi on_board_devices_information>: string	description_string	description_strings	description_string	0	string	dmi on_board_devices_information	
1f	design_capacity of <dmi portable_battery>: integer	design_capacity	design_capacitys	design_capacity	0	integer	dmi portable_battery	
1f	design_capacity_multiplier of <dmi portable_battery>: integer	design_capacity_multiplier	design_capacity_multipliers	design_capacity_multiplier	0	integer	dmi portable_battery	
1f	design_voltage of <dmi portable_battery>: integer	design_voltage	design_voltages	design_voltage	0	integer	dmi portable_battery	
1f	desired encrypt report of <client_cryptography>: boolean	desired encrypt report	desired encrypt reports	desired encrypt report	0	boolean	client_cryptography	
ff	desired fips mode of <cryptography>: boolean	desired fips mode	desired fips modes	desired fips mode	0	boolean	cryptography	
2	desktop folder of <domain>: folder	desktop folder	desktop folders	desktop folder	0	folder	domain	
2	desktop folder: folder	desktop folder	desktop folders	desktop folder	0	folder		
f	destination of <route>: ipv4or6 address	destination	destinations	destination	0	ipv4or6 address	route	
2	destination string of <route>: string	destination string	destination strings	destination string	0	string	route	
2	destination type of <route>: string	destination type	destination types	destination type	0	string	route	
e0	detailed status of <bes action result>: string	detailed status	detailed statuses	detailed status	0	string	bes action result	
10	detailed tracking category of <audit policy>: audit policy category	detailed tracking category	detailed tracking categories	detailed tracking category	0	audit policy category	audit policy	
2	developer docs folder of <domain>: folder	developer docs folder	developer docs folders	developer docs folder	0	folder	domain	
2	developer docs folder: folder	developer docs folder	developer docs folders	developer docs folder	0	folder		
2	developer folder of <domain>: folder	developer folder	developer folders	developer folder	0	folder	domain	
2	developer folder: folder	developer folder	developer folders	developer folder	0	folder		
2	developer help folder of <domain>: folder	developer help folder	developer help folders	developer help folder	0	folder	domain	
2	developer help folder: folder	developer help folder	developer help folders	developer help folder	0	folder		
5f	device count of <bes product>: integer	device count	device counts	device count	0	integer	bes product	
d	device file <filesystem object>: device file	device file	device files	device file	0	device file		filesystem object
d	device file <string> of <folder>: device file	device file	device files	device file	0	device file	folder	string
d	device file <string>: device file	device file	device files	device file	0	device file		string
d	device file <symlink>: device file	device file	device files	device file	0	device file		symlink
d	device files of <folder>: device file	device file	device files	device files	1	device file	folder	
10	device name of <connection>: string	device name	device names	device name	0	string	connection	
d	device name of <filesystem>: string	device name	device names	device name	0	string	filesystem	
d	device of <grub file location>: grub device	device	devices	device	0	grub device	grub file location	
e0	device type of <bes computer>: string	device type	device types	device type	0	string	bes computer	
d	device type of <device file>: string	device type	device types	device type	0	string	device file	
10	device type: string	device type	device types	device type	0	string		
1f	device_chemistry of <dmi portable_battery>: integer	device_chemistry	device_chemistrys	device_chemistry	0	integer	dmi portable_battery	
1f	device_description <integer> of <dmi on_board_devices_information>: string	device_description	device_descriptions	device_description	0	string	dmi on_board_devices_information	integer
1f	device_descriptions of <dmi on_board_devices_information>: string	device_description	device_descriptions	device_descriptions	1	string	dmi on_board_devices_information	
1f	device_error_address of <dmi b32_bit_memory_error_information>: integer	device_error_address	device_error_addresss	device_error_address	0	integer	dmi b32_bit_memory_error_information	
1f	device_error_address of <dmi b64_bit_memory_error_information>: integer	device_error_address	device_error_addresss	device_error_address	0	integer	dmi b64_bit_memory_error_information	
1f	device_function_number of <dmi onboard_devices_extended_information>: integer	device_function_number	device_function_numbers	device_function_number	0	integer	dmi onboard_devices_extended_information	
1f	device_function_number of <dmi system_slots>: integer	device_function_number	device_function_numbers	device_function_number	0	integer	dmi system_slots	
1f	device_locator of <dmi memory_device>: string	device_locator	device_locators	device_locator	0	string	dmi memory_device	
1f	device_name of <dmi portable_battery>: string	device_name	device_names	device_name	0	string	dmi portable_battery	
1f	device_name of <dmi system_power_supply>: string	device_name	device_names	device_name	0	string	dmi system_power_supply	
1f	device_set of <dmi memory_device>: integer	device_set	device_sets	device_set	0	integer	dmi memory_device	
1f	device_type <integer> of <dmi on_board_devices_information>: integer	device_type	device_types	device_type	0	integer	dmi on_board_devices_information	integer
1f	device_type_and_status of <dmi cooling_device>: integer	device_type_and_status	device_type_and_statuss	device_type_and_status	0	integer	dmi cooling_device	
1f	device_type_instance of <dmi onboard_devices_extended_information>: integer	device_type_instance	device_type_instances	device_type_instance	0	integer	dmi onboard_devices_extended_information	
1f	device_types of <dmi on_board_devices_information>: integer	device_type	device_types	device_types	1	integer	dmi on_board_devices_information	
2	devicetree plane of <registryroot>: registrynode	devicetree plane	devicetree planes	devicetree plane	0	registrynode	registryroot	
ff	dfn <string> of <html>: html	dfn	dfns	dfn	0	html	html	string
ff	dfn <string> of <string>: html	dfn	dfns	dfn	0	html	string	string
ff	dfn of <html>: html	dfn	dfns	dfn	0	html	html	
ff	dfn of <string>: html	dfn	dfns	dfn	0	html	string	
10	dhcp enabled of <network adapter>: boolean	dhcp enabled	dhcp enableds	dhcp enabled	0	boolean	network adapter	
10	dhcp server of <network adapter>: ipv4 address	dhcp server	dhcp servers	dhcp server	0	ipv4 address	network adapter	
e0	dialog flag of <bes wizard>: boolean	dialog flag	dialog flags	dialog flag	0	boolean	bes wizard	
10	dialup group: security account	dialup group	dialup groups	dialup group	0	security account		
2	dictionary <integer> of <array>: dictionary	dictionary	dictionaries	dictionary	0	dictionary	array	integer
2	dictionary <string> of <dictionary>: dictionary	dictionary	dictionaries	dictionary	0	dictionary	dictionary	string
2	dictionary <string> of <preference>: dictionary	dictionary	dictionaries	dictionary	0	dictionary	preference	string
2	dictionary of <file>: dictionary	dictionary	dictionaries	dictionary	0	dictionary	file	
2	dictionary of <osxvalue>: dictionary	dictionary	dictionaries	dictionary	0	dictionary	osxvalue	
2	dictionary of <registrynode>: dictionary	dictionary	dictionaries	dictionary	0	dictionary	registrynode	
2	dictionary of <registryroot>: dictionary	dictionary	dictionaries	dictionary	0	dictionary	registryroot	
e0	digest file name of <bes fixlet>: string	digest file name	digest file names	digest file name	0	string	bes fixlet	
ff	direct object type of <property>: type	direct object type	direct object types	direct object type	0	type	property	
2	directory count of <volume>: integer	directory count	directory counts	directory count	0	integer	volume	
2	disabled control panel <string>: enableable_file	disabled control panel	disabled control panels	disabled control panel	0	enableable_file		string
2	disabled control panels folder of <domain>: folder	disabled control panels folder	disabled control panels folders	disabled control panels folder	0	folder	domain	
2	disabled control panels folder: folder	disabled control panels folder	disabled control panels folders	disabled control panels folder	0	folder		
2	disabled control panels: enableable_file	disabled control panel	disabled control panels	disabled control panels	1	enableable_file		
2	disabled extension <string>: enableable_file	disabled extension	disabled extensions	disabled extension	0	enableable_file		string
2	disabled extensions folder of <domain>: folder	disabled extensions folder	disabled extensions folders	disabled extensions folder	0	folder	domain	
2	disabled extensions folder: folder	disabled extensions folder	disabled extensions folders	disabled extensions folder	0	folder		
2	disabled extensions: enableable_file	disabled extension	disabled extensions	disabled extensions	1	enableable_file		
d	disabled of <Xinetd Service>: boolean	disabled	disableds	disabled	0	boolean	Xinetd Service	
2	disabled of <enableable_file>: boolean	disabled	disableds	disabled	0	boolean	enableable_file	
2	disabled shutdown item <string>: enableable_file	disabled shutdown item	disabled shutdown items	disabled shutdown item	0	enableable_file		string
2	disabled shutdown items folder of <domain>: folder	disabled shutdown items folder	disabled shutdown items folders	disabled shutdown items folder	0	folder	domain	
2	disabled shutdown items folder: folder	disabled shutdown items folder	disabled shutdown items folders	disabled shutdown items folder	0	folder		
2	disabled shutdown items: enableable_file	disabled shutdown item	disabled shutdown items	disabled shutdown items	1	enableable_file		
2	disabled startup item <string>: enableable_file	disabled startup item	disabled startup items	disabled startup item	0	enableable_file		string
2	disabled startup items folder of <domain>: folder	disabled startup items folder	disabled startup items folders	disabled startup items folder	0	folder	domain	
2	disabled startup items folder: folder	disabled startup items folder	disabled startup items folders	disabled startup items folder	0	folder		
2	disabled startup items: enableable_file	disabled startup item	disabled startup items	disabled startup items	1	enableable_file		
10	disabled state of <running task>: boolean	disabled state	disabled states	disabled state	0	boolean	running task	
10	disabled state of <scheduled task>: boolean	disabled state	disabled states	disabled state	0	boolean	scheduled task	
2	disabled system extensions folder of <domain>: folder	disabled system extensions folder	disabled system extensions folders	disabled system extensions folder	0	folder	domain	
2	disabled system extensions folder: folder	disabled system extensions folder	disabled system extensions folders	disabled system extensions folder	0	folder		
10	disallow start when on battery of <task settings>: boolean	disallow start when on battery	disallow start when on batteries	disallow start when on battery	0	boolean	task settings	
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
1f	display name of <operating system>: string	display name	display names	display name	0	string	operating system	
10	display name of <service>: string	display name	display names	display name	0	string	service	
10	display name of <task principal>: string	display name	display names	display name	0	string	task principal	
e0	display simple name of <bes property>: string	display simple name	display simple names	display simple name	0	string	bes property	
e0	display source id of <bes fixlet>: string	display source id	display source ids	display source id	0	string	bes fixlet	
e0	display source of <bes fixlet>: string	display source	display sources	display source	0	string	bes fixlet	
e0	display source severity of <bes fixlet>: string	display source severity	display source severities	display source severity	0	string	bes fixlet	
e0	display value of <bes fixlet field value>: string	display value	display values	display value	0	string	bes fixlet field value	
10	display version of <operating system>: string	display version	display versions	display version	0	string	operating system	
1f	distance of <selected server>: integer range	distance	distances	distance	0	integer range	selected server	
b0	distinguished name <string>: distinguished name	distinguished name	distinguished names	distinguished name	0	distinguished name		string
12	distinguished name error message of <active directory group>: string	distinguished name error message	distinguished name error messages	distinguished name error message	0	string	active directory group	
12	distinguished name error message of <active directory local computer>: string	distinguished name error message	distinguished name error messages	distinguished name error message	0	string	active directory local computer	
12	distinguished name error message of <active directory local user>: string	distinguished name error message	distinguished name error messages	distinguished name error message	0	string	active directory local user	
12	distinguished name of <active directory group>: string	distinguished name	distinguished names	distinguished name	0	string	active directory group	
12	distinguished name of <active directory local computer>: string	distinguished name	distinguished names	distinguished name	0	string	active directory local computer	
12	distinguished name of <active directory local user>: string	distinguished name	distinguished names	distinguished name	0	string	active directory local user	
e0	distinguished name of <bes user>: string	distinguished name	distinguished names	distinguished name	0	string	bes user	
ff	div <string> of <html>: html	div	divs	div	0	html	html	string
ff	div <string> of <string>: html	div	divs	div	0	html	string	string
ff	div of <html>: html	div	divs	div	0	html	html	
ff	div of <string>: html	div	divs	div	0	html	string	
ff	divided by zero of <floating point>: boolean	divided by zero	divided by zeroes	divided by zero	0	boolean	floating point	
1f	dmi: dmi	dmi	dmis	dmi	0	dmi		
12	dns domainname of <active directory local computer>: string	dns domainname	dns domainnames	dns domainname	0	string	active directory local computer	
12	dns domainname of <active directory local user>: string	dns domainname	dns domainnames	dns domainname	0	string	active directory local user	
1f	dns name: string	dns name	dns names	dns name	0	string		
10	dns servers of <network adapter>: network address list	dns server	dns servers	dns servers	1	network address list	network adapter	
10	dns servers of <network>: network address list	dns server	dns servers	dns servers	1	network address list	network	
10	dns suffix of <network adapter>: string	dns suffix	dns suffixes	dns suffix	0	string	network adapter	
e0	document flag of <bes wizard>: boolean	document flag	document flags	document flag	0	boolean	bes wizard	
2	documentation folder of <domain>: folder	documentation folder	documentation folders	documentation folder	0	folder	domain	
2	documentation folder: folder	documentation folder	documentation folders	documentation folder	0	folder		
10	documentation of <task registration info>: string	documentation	documentations	documentation	0	string	task registration info	
2	documents folder of <domain>: folder	documents folder	documents folders	documents folder	0	folder	domain	
2	documents folder: folder	documents folder	documents folders	documents folder	0	folder		
10	domain firewall profile type: firewall profile type	domain firewall profile type	domain firewall profile types	domain firewall profile type	0	firewall profile type		
2	domain library folder of <domain>: folder	domain library folder	domain library folders	domain library folder	0	folder	domain	
2	domain library folder: folder	domain library folder	domain library folders	domain library folder	0	folder		
10	domain name of <security identifier>: string	domain name	domain names	domain name	0	string	security identifier	
d	domain name: string	domain name	domain names	domain name	0	string		
10	domain of <active directory local user>: string	domain	domains	domain	0	string	active directory local user	
e0	domain of <bes action>: bes domain	domain	domains	domain	0	bes domain	bes action	
e0	domain of <bes computer group>: bes domain	domain	domains	domain	0	bes domain	bes computer group	
e0	domain of <bes filter>: bes domain	domain	domains	domain	0	bes domain	bes filter	
e0	domain of <bes fixlet>: bes domain	domain	domains	domain	0	bes domain	bes fixlet	
10	domain of <user>: string	domain	domains	domain	0	string	user	
10	domain profile of <firewall policy>: firewall profile	domain profile	domain profiles	domain profile	0	firewall profile	firewall policy	
e0	domain set of <bes site>: bes domain set	domain set	domain sets	domain set	0	bes domain set	bes site	
2	domain top folder of <domain>: folder	domain top folder	domain top folders	domain top folder	0	folder	domain	
2	domain top folder: folder	domain top folder	domain top folders	domain top folder	0	folder		
10	domain user <string>: user	domain user	domain users	domain user	0	user		string
10	domain user of <active directory local user>: user	domain user	domain users	domain user	0	user	active directory local user	
10	domain users: user	domain user	domain users	domain users	1	user		
d	domainname: string	domainname	domainnames	domainname	0	string		
e0	domains of <bes site>: bes domain	domain	domains	domains	1	bes domain	bes site	
2	done flag of <route>: boolean	done flag	done flags	done flag	0	boolean	route	
1f	download failure of <action>: integer	download failure	download failures	download failure	0	integer	action	
1f	download file <string> of <encoding>: file	download file	download files	download file	0	file	encoding	string
1f	download file <string>: file	download file	download files	download file	0	file		string
1f	download folder of <encoding>: folder	download folder	download folders	download folder	0	folder	encoding	
1f	download folder: folder	download folder	download folders	download folder	0	folder		
ff	download hash algorithms of <license>: string	download hash algorithm	download hash algorithms	download hash algorithms	1	string	license	
1f	download path <string>: string	download path	download paths	download path	0	string		string
1f	download server: download server	download server	download servers	download server	0	download server		
e0	download size of <bes fixlet>: integer	download size	download sizes	download size	0	integer	bes fixlet	
1d	download storage folder: download storage folder	download storage folder	download storage folders	download storage folder	0	download storage folder		
40	downloader computer id of <bes peer download>: integer	downloader computer id	downloader computer ids	downloader computer id	0	integer	bes peer download	
2	drive <integer>: volume	drive	drives	drive	0	volume		integer
10	drive <string>: drive	drive	drives	drive	0	drive		string
d	drive <string>: filesystem	drive	drives	drive	0	filesystem		string
d	drive of <device file>: filesystem	drive	drives	drive	0	filesystem	device file	
d	drive of <fifo file>: filesystem	drive	drives	drive	0	filesystem	fifo file	
d	drive of <file>: filesystem	drive	drives	drive	0	filesystem	file	
2	drive of <file>: volume	drive	drives	drive	0	volume	file	
10	drive of <filesystem object>: drive	drive	drives	drive	0	drive	filesystem object	
d	drive of <folder>: filesystem	drive	drives	drive	0	filesystem	folder	
2	drive of <folder>: volume	drive	drives	drive	0	volume	folder	
d	drive of <socket file>: filesystem	drive	drives	drive	0	filesystem	socket file	
d	drive of <symlink>: filesystem	drive	drives	drive	0	filesystem	symlink	
10	driver key of <active device>: registry key	driver key	driver keys	driver key	0	registry key	active device	
10	driver key of <registry key>: registry key	driver key	driver keys	driver key	0	registry key	registry key	
10	driver key value name of <active device>: string	driver key value name	driver key value names	driver key value name	0	string	active device	
10	driver running services: service	driver running service	driver running services	driver running services	1	service		
10	driver services: service	driver service	driver services	driver services	1	service		
10	driver type of <service>: boolean	driver type	driver types	driver type	0	boolean	service	
2	drives <string>: volume	drive	drives	drives	1	volume		string
10	drives: drive	drive	drives	drives	1	drive		
d	drives: filesystem	drive	drives	drives	1	filesystem		
2	drives: volume	drive	drives	drives	1	volume		
10	ds access category of <audit policy>: audit policy category	ds access category	ds access categories	ds access category	0	audit policy category	audit policy	
ff	dt <string> of <html>: html	dt	dts	dt	0	html	html	string
ff	dt <string> of <string>: html	dt	dts	dt	0	html	string	string
ff	dt of <html>: html	dt	dts	dt	0	html	html	
ff	dt of <string>: html	dt	dts	dt	0	html	string	
10	duration of <task repetition pattern>: time interval	duration	durations	duration	0	time interval	task repetition pattern	
2	dynamic flag of <route>: boolean	dynamic flag	dynamic flags	dynamic flag	0	boolean	route	
10	edge traversal allowed of <firewall rule>: boolean	edge traversal allowed	edge traversal alloweds	edge traversal allowed	0	boolean	firewall rule	
e0	editable flag of <bes unmanagedasset field>: boolean	editable flag	editable flags	editable flag	0	boolean	bes unmanagedasset field	
10	effective access mode for <security account> of <access control list>: integer	effective access mode for	effective access modes for	effective access mode for	0	integer	access control list	security account
10	effective access mode for <string> of <access control list>: integer	effective access mode for	effective access modes for	effective access mode for	0	integer	access control list	string
10	effective access system security permission for <security account> of <access control list>: boolean	effective access system security permission for	effective access system security permissions for	effective access system security permission for	0	boolean	access control list	security account
10	effective access system security permission for <string> of <access control list>: boolean	effective access system security permission for	effective access system security permissions for	effective access system security permission for	0	boolean	access control list	string
10	effective append permission for <security account> of <access control list>: boolean	effective append permission for	effective append permissions for	effective append permission for	0	boolean	access control list	security account
10	effective append permission for <string> of <access control list>: boolean	effective append permission for	effective append permissions for	effective append permission for	0	boolean	access control list	string
40	effective can create actions flag of <bes user>: boolean	effective can create actions flag	effective can create actions flags	effective can create actions flag	0	boolean	bes user	
40	effective can lock flag of <bes user>: boolean	effective can lock flag	effective can lock flags	effective can lock flag	0	boolean	bes user	
40	effective can send multiple refresh flag of <bes user>: boolean	effective can send multiple refresh flag	effective can send multiple refresh flags	effective can send multiple refresh flag	0	boolean	bes user	
40	effective can submit queries flag of <bes user>: boolean	effective can submit queries flag	effective can submit queries flags	effective can submit queries flag	0	boolean	bes user	
10	effective change notification permission for <security account> of <access control list>: boolean	effective change notification permission for	effective change notification permissions for	effective change notification permission for	0	boolean	access control list	security account
10	effective change notification permission for <string> of <access control list>: boolean	effective change notification permission for	effective change notification permissions for	effective change notification permission for	0	boolean	access control list	string
10	effective create file permission for <security account> of <access control list>: boolean	effective create file permission for	effective create file permissions for	effective create file permission for	0	boolean	access control list	security account
10	effective create file permission for <string> of <access control list>: boolean	effective create file permission for	effective create file permissions for	effective create file permission for	0	boolean	access control list	string
10	effective create folder permission for <security account> of <access control list>: boolean	effective create folder permission for	effective create folder permissions for	effective create folder permission for	0	boolean	access control list	security account
10	effective create folder permission for <string> of <access control list>: boolean	effective create folder permission for	effective create folder permissions for	effective create folder permission for	0	boolean	access control list	string
10	effective create link permission for <security account> of <access control list>: boolean	effective create link permission for	effective create link permissions for	effective create link permission for	0	boolean	access control list	security account
10	effective create link permission for <string> of <access control list>: boolean	effective create link permission for	effective create link permissions for	effective create link permission for	0	boolean	access control list	string
10	effective create subkey permission for <security account> of <access control list>: boolean	effective create subkey permission for	effective create subkey permissions for	effective create subkey permission for	0	boolean	access control list	security account
10	effective create subkey permission for <string> of <access control list>: boolean	effective create subkey permission for	effective create subkey permissions for	effective create subkey permission for	0	boolean	access control list	string
40	effective custom content flag of <bes user>: boolean	effective custom content flag	effective custom content flags	effective custom content flag	0	boolean	bes user	
1f	effective date of <action lock state>: time	effective date	effective dates	effective date	0	time	action lock state	
14	effective date of <plugin store key>: time	effective date	effective dates	effective date	0	time	plugin store key	
1f	effective date of <setting>: time	effective date	effective dates	effective date	0	time	setting	
10	effective delete child permission for <security account> of <access control list>: boolean	effective delete child permission for	effective delete child permissions for	effective delete child permission for	0	boolean	access control list	security account
10	effective delete child permission for <string> of <access control list>: boolean	effective delete child permission for	effective delete child permissions for	effective delete child permission for	0	boolean	access control list	string
10	effective delete permission for <security account> of <access control list>: boolean	effective delete permission for	effective delete permissions for	effective delete permission for	0	boolean	access control list	security account
10	effective delete permission for <string> of <access control list>: boolean	effective delete permission for	effective delete permissions for	effective delete permission for	0	boolean	access control list	string
ff	effective download hash algorithm of <license>: string	effective download hash algorithm	effective download hash algorithms	effective download hash algorithm	0	string	license	
10	effective enumerate subkeys permission for <security account> of <access control list>: boolean	effective enumerate subkeys permission for	effective enumerate subkeys permissions for	effective enumerate subkeys permission for	0	boolean	access control list	security account
10	effective enumerate subkeys permission for <string> of <access control list>: boolean	effective enumerate subkeys permission for	effective enumerate subkeys permissions for	effective enumerate subkeys permission for	0	boolean	access control list	string
10	effective execute permission for <security account> of <access control list>: boolean	effective execute permission for	effective execute permissions for	effective execute permission for	0	boolean	access control list	security account
10	effective execute permission for <string> of <access control list>: boolean	effective execute permission for	effective execute permissions for	effective execute permission for	0	boolean	access control list	string
10	effective generic all permission for <security account> of <access control list>: boolean	effective generic all permission for	effective generic all permissions for	effective generic all permission for	0	boolean	access control list	security account
10	effective generic all permission for <string> of <access control list>: boolean	effective generic all permission for	effective generic all permissions for	effective generic all permission for	0	boolean	access control list	string
10	effective generic execute permission for <security account> of <access control list>: boolean	effective generic execute permission for	effective generic execute permissions for	effective generic execute permission for	0	boolean	access control list	security account
10	effective generic execute permission for <string> of <access control list>: boolean	effective generic execute permission for	effective generic execute permissions for	effective generic execute permission for	0	boolean	access control list	string
10	effective generic read permission for <security account> of <access control list>: boolean	effective generic read permission for	effective generic read permissions for	effective generic read permission for	0	boolean	access control list	security account
10	effective generic read permission for <string> of <access control list>: boolean	effective generic read permission for	effective generic read permissions for	effective generic read permission for	0	boolean	access control list	string
10	effective generic write permission for <security account> of <access control list>: boolean	effective generic write permission for	effective generic write permissions for	effective generic write permission for	0	boolean	access control list	security account
10	effective generic write permission for <string> of <access control list>: boolean	effective generic write permission for	effective generic write permissions for	effective generic write permission for	0	boolean	access control list	string
10	effective list permission for <security account> of <access control list>: boolean	effective list permission for	effective list permissions for	effective list permission for	0	boolean	access control list	security account
10	effective list permission for <string> of <access control list>: boolean	effective list permission for	effective list permissions for	effective list permission for	0	boolean	access control list	string
40	effective master flag of <bes user>: boolean	effective master flag	effective master flags	effective master flag	0	boolean	bes user	
10	effective maximum allowed permission for <security account> of <access control list>: boolean	effective maximum allowed permission for	effective maximum allowed permissions for	effective maximum allowed permission for	0	boolean	access control list	security account
10	effective maximum allowed permission for <string> of <access control list>: boolean	effective maximum allowed permission for	effective maximum allowed permissions for	effective maximum allowed permission for	0	boolean	access control list	string
10	effective policy <security account> of <audit policy subcategory>: audit policy information	effective policy	effective policies	effective policy	0	audit policy information	audit policy subcategory	security account
10	effective query value permission for <security account> of <access control list>: boolean	effective query value permission for	effective query value permissions for	effective query value permission for	0	boolean	access control list	security account
10	effective query value permission for <string> of <access control list>: boolean	effective query value permission for	effective query value permissions for	effective query value permission for	0	boolean	access control list	string
10	effective read attributes permission for <security account> of <access control list>: boolean	effective read attributes permission for	effective read attributes permissions for	effective read attributes permission for	0	boolean	access control list	security account
10	effective read attributes permission for <string> of <access control list>: boolean	effective read attributes permission for	effective read attributes permissions for	effective read attributes permission for	0	boolean	access control list	string
10	effective read control permission for <security account> of <access control list>: boolean	effective read control permission for	effective read control permissions for	effective read control permission for	0	boolean	access control list	security account
10	effective read control permission for <string> of <access control list>: boolean	effective read control permission for	effective read control permissions for	effective read control permission for	0	boolean	access control list	string
10	effective read extended attributes permission for <security account> of <access control list>: boolean	effective read extended attributes permission for	effective read extended attributes permissions for	effective read extended attributes permission for	0	boolean	access control list	security account
10	effective read extended attributes permission for <string> of <access control list>: boolean	effective read extended attributes permission for	effective read extended attributes permissions for	effective read extended attributes permission for	0	boolean	access control list	string
10	effective read permission for <security account> of <access control list>: boolean	effective read permission for	effective read permissions for	effective read permission for	0	boolean	access control list	security account
10	effective read permission for <string> of <access control list>: boolean	effective read permission for	effective read permissions for	effective read permission for	0	boolean	access control list	string
40	effective restartandshutdown actionscript privilege allowboth flag of <bes user>: boolean	effective restartandshutdown actionscript privilege allowboth flag	effective restartandshutdown actionscript privilege allowboth flags	effective restartandshutdown actionscript privilege allowboth flag	0	boolean	bes user	
40	effective restartandshutdown actionscript privilege allowrestartonly flag of <bes user>: boolean	effective restartandshutdown actionscript privilege allowrestartonly flag	effective restartandshutdown actionscript privilege allowrestartonly flags	effective restartandshutdown actionscript privilege allowrestartonly flag	0	boolean	bes user	
40	effective restartandshutdown actionscript privilege none flag of <bes user>: boolean	effective restartandshutdown actionscript privilege none flag	effective restartandshutdown actionscript privilege none flags	effective restartandshutdown actionscript privilege none flag	0	boolean	bes user	
40	effective restartandshutdown postaction privilege allowboth flag of <bes user>: boolean	effective restartandshutdown postaction privilege allowboth flag	effective restartandshutdown postaction privilege allowboth flags	effective restartandshutdown postaction privilege allowboth flag	0	boolean	bes user	
40	effective restartandshutdown postaction privilege allowrestartonly flag of <bes user>: boolean	effective restartandshutdown postaction privilege allowrestartonly flag	effective restartandshutdown postaction privilege allowrestartonly flags	effective restartandshutdown postaction privilege allowrestartonly flag	0	boolean	bes user	
40	effective restartandshutdown postaction privilege none flag of <bes user>: boolean	effective restartandshutdown postaction privilege none flag	effective restartandshutdown postaction privilege none flags	effective restartandshutdown postaction privilege none flag	0	boolean	bes user	
10	effective set value permission for <security account> of <access control list>: boolean	effective set value permission for	effective set value permissions for	effective set value permission for	0	boolean	access control list	security account
10	effective set value permission for <string> of <access control list>: boolean	effective set value permission for	effective set value permissions for	effective set value permission for	0	boolean	access control list	string
40	effective show other action flag of <bes user>: boolean	effective show other action flag	effective show other action flags	effective show other action flag	0	boolean	bes user	
ff	effective signature hash algorithm of <license>: string	effective signature hash algorithm	effective signature hash algorithms	effective signature hash algorithm	0	string	license	
40	effective stop other actions flag of <bes user>: boolean	effective stop other actions flag	effective stop other actions flags	effective stop other actions flag	0	boolean	bes user	
10	effective synchronize permission for <security account> of <access control list>: boolean	effective synchronize permission for	effective synchronize permissions for	effective synchronize permission for	0	boolean	access control list	security account
10	effective synchronize permission for <string> of <access control list>: boolean	effective synchronize permission for	effective synchronize permissions for	effective synchronize permission for	0	boolean	access control list	string
d	effective time of <runlevel>: time	effective time	effective times	effective time	0	time	runlevel	
10	effective traverse permission for <security account> of <access control list>: boolean	effective traverse permission for	effective traverse permissions for	effective traverse permission for	0	boolean	access control list	security account
10	effective traverse permission for <string> of <access control list>: boolean	effective traverse permission for	effective traverse permissions for	effective traverse permission for	0	boolean	access control list	string
40	effective unmanagedasset privilege scanpoint flag of <bes user>: boolean	effective unmanagedasset privilege scanpoint flag	effective unmanagedasset privilege scanpoint flags	effective unmanagedasset privilege scanpoint flag	0	boolean	bes user	
40	effective unmanagedasset privilege showall flag of <bes user>: boolean	effective unmanagedasset privilege showall flag	effective unmanagedasset privilege showall flags	effective unmanagedasset privilege showall flag	0	boolean	bes user	
40	effective unmanagedasset privilege shownone flag of <bes user>: boolean	effective unmanagedasset privilege shownone flag	effective unmanagedasset privilege shownone flags	effective unmanagedasset privilege shownone flag	0	boolean	bes user	
d	effective user of <process>: user	effective user	effective users	effective user	0	user	process	
10	effective write attributes permission for <security account> of <access control list>: boolean	effective write attributes permission for	effective write attributes permissions for	effective write attributes permission for	0	boolean	access control list	security account
10	effective write attributes permission for <string> of <access control list>: boolean	effective write attributes permission for	effective write attributes permissions for	effective write attributes permission for	0	boolean	access control list	string
10	effective write dac permission for <security account> of <access control list>: boolean	effective write dac permission for	effective write dac permissions for	effective write dac permission for	0	boolean	access control list	security account
10	effective write dac permission for <string> of <access control list>: boolean	effective write dac permission for	effective write dac permissions for	effective write dac permission for	0	boolean	access control list	string
10	effective write extended attributes permission for <security account> of <access control list>: boolean	effective write extended attributes permission for	effective write extended attributes permissions for	effective write extended attributes permission for	0	boolean	access control list	security account
10	effective write extended attributes permission for <string> of <access control list>: boolean	effective write extended attributes permission for	effective write extended attributes permissions for	effective write extended attributes permission for	0	boolean	access control list	string
10	effective write owner permission for <security account> of <access control list>: boolean	effective write owner permission for	effective write owner permissions for	effective write owner permission for	0	boolean	access control list	security account
10	effective write owner permission for <string> of <access control list>: boolean	effective write owner permission for	effective write owner permissions for	effective write owner permission for	0	boolean	access control list	string
10	effective write permission for <security account> of <access control list>: boolean	effective write permission for	effective write permissions for	effective write permission for	0	boolean	access control list	security account
10	effective write permission for <string> of <access control list>: boolean	effective write permission for	effective write permissions for	effective write permission for	0	boolean	access control list	string
d	elapsed time of <process>: time interval	elapsed time	elapsed times	elapsed time	0	time interval	process	
1f	electrical_current_probe <integer> of <dmi>: dmi electrical_current_probe	electrical_current_probe	electrical_current_probes	electrical_current_probe	0	dmi electrical_current_probe	dmi	integer
1f	electrical_current_probes of <dmi>: dmi electrical_current_probe	electrical_current_probe	electrical_current_probes	electrical_current_probes	1	dmi electrical_current_probe	dmi	
ff	element <integer> of <json value>: json value	element	elements	element	0	json value	json value	integer
1f	element <integer> of <yaml value>: yaml value	element	elements	element	0	yaml value	yaml value	integer
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
1f	elements of <yaml value>: yaml value	element	elements	elements	1	yaml value	yaml value	
ff	em <string> of <html>: html	em	ems	em	0	html	html	string
ff	em <string> of <string>: html	em	ems	em	0	html	string	string
ff	em of <html>: html	em	ems	em	0	html	html	
ff	em of <string>: html	em	ems	em	0	html	string	
ff	email address of <license>: string	email address	email addresses	email address	0	string	license	
10	email task action type: task action type	email task action type	email task action types	email task action type	0	task action type		
10	embedded nt bit <operating system suite mask>: boolean	embedded nt bit	embedded nt bits	embedded nt bit	0	boolean		operating system suite mask
1f	embedded of <operating system>: boolean	embedded	embeddeds	embedded	0	boolean	operating system	
10	embedded restricted bit <operating system suite mask>: boolean	embedded restricted bit	embedded restricted bits	embedded restricted bit	0	boolean		operating system suite mask
1f	embedded_controller_firmware_major_release of <dmi bios_information>: integer	embedded_controller_firmware_major_release	embedded_controller_firmware_major_releases	embedded_controller_firmware_major_release	0	integer	dmi bios_information	
1f	embedded_controller_firmware_minor_release of <dmi bios_information>: integer	embedded_controller_firmware_minor_release	embedded_controller_firmware_minor_releases	embedded_controller_firmware_minor_release	0	integer	dmi bios_information	
2	enabled control panel <string>: enableable_file	enabled control panel	enabled control panels	enabled control panel	0	enableable_file		string
2	enabled control panels: enableable_file	enabled control panel	enabled control panels	enabled control panels	1	enableable_file		
2	enabled extension <string>: enableable_file	enabled extension	enabled extensions	enabled extension	0	enableable_file		string
2	enabled extensions: enableable_file	enabled extension	enabled extensions	enabled extensions	1	enableable_file		
1f	enabled of <administrative rights>: boolean	enabled	enableds	enabled	0	boolean	administrative rights	
e0	enabled of <bes wakeonlan status>: boolean	enabled	enableds	enabled	0	boolean	bes wakeonlan status	
2	enabled of <enableable_file>: boolean	enabled	enableds	enabled	0	boolean	enableable_file	
10	enabled of <firewall authorized application>: boolean	enabled	enableds	enabled	0	boolean	firewall authorized application	
10	enabled of <firewall open port>: boolean	enabled	enableds	enabled	0	boolean	firewall open port	
10	enabled of <firewall rule>: boolean	enabled	enableds	enabled	0	boolean	firewall rule	
10	enabled of <firewall service>: boolean	enabled	enableds	enabled	0	boolean	firewall service	
2	enabled of <firewall>: boolean	enabled	enableds	enabled	0	boolean	firewall	
10	enabled of <internet connection firewall>: boolean	enabled	enableds	enabled	0	boolean	internet connection firewall	
10	enabled of <port mapping>: boolean	enabled	enableds	enabled	0	boolean	port mapping	
1f	enabled of <restricted site>: boolean	enabled	enableds	enabled	0	boolean	restricted site	
10	enabled of <scheduled task>: boolean	enabled	enableds	enabled	0	boolean	scheduled task	
1f	enabled of <setting>: boolean	enabled	enableds	enabled	0	boolean	setting	
10	enabled of <task settings>: boolean	enabled	enableds	enabled	0	boolean	task settings	
10	enabled of <task trigger>: boolean	enabled	enableds	enabled	0	boolean	task trigger	
12	enabled of <wifi>: boolean	enabled	enableds	enabled	0	boolean	wifi	
2	enabled shutdown item <string>: enableable_file	enabled shutdown item	enabled shutdown items	enabled shutdown item	0	enableable_file		string
2	enabled shutdown items: enableable_file	enabled shutdown item	enabled shutdown items	enabled shutdown items	1	enableable_file		
2	enabled startup item <string>: enableable_file	enabled startup item	enabled startup items	enabled startup item	0	enableable_file		string
2	enabled startup items: enableable_file	enabled startup item	enabled startup items	enabled startup items	1	enableable_file		
1f	enabled_size of <dmi memory_module_information>: integer	enabled_size	enabled_sizes	enabled_size	0	integer	dmi memory_module_information	
1f	encoding <string>: encoding	encoding	encodings	encoding	0	encoding		string
1f	encoding of <sqlite database>: string	encoding	encodings	encoding	0	string	sqlite database	
1f	encrypt report failure message of <client_cryptography>: string	encrypt report failure message	encrypt report failure messages	encrypt report failure message	0	string	client_cryptography	
1f	encrypt report of <client_cryptography>: boolean	encrypt report	encrypt reports	encrypt report	0	boolean	client_cryptography	
14	encrypted of <plugin store key>: boolean	encrypted	encrypteds	encrypted	0	boolean	plugin store key	
ff	encryption certificate of <license>: x509 certificate	encryption certificate	encryption certificates	encryption certificate	0	x509 certificate	license	
12	encryption of <wifi>: string	encryption	encryptions	encryption	0	string	wifi	
10	end boundary of <task trigger>: time	end boundary	end boundaries	end boundary	0	time	task trigger	
e0	end date of <bes action>: date	end date	end dates	end date	0	date	bes action	
e0	end flag of <bes action>: boolean	end flag	end flags	end flag	0	boolean	bes action	
ff	end of <binary_substring>: binary position	end	ends	end	0	binary position	binary_substring	
e0	end of <statistic range>: time	end	ends	end	0	time	statistic range	
e0	end of <statistical bin>: time	end	ends	end	0	time	statistical bin	
ff	end of <substring>: string position	end	ends	end	0	string position	substring	
ff	end of <time range>: time	end	ends	end	0	time	time range	
e0	end time of <bes action result>: time	end time	end times	end time	0	time	bes action result	
e0	end time_of_day of <bes action>: time of day	end time_of_day	end times_of_day	end time_of_day	0	time of day	bes action	
1f	end_of_table <integer> of <dmi>: dmi end_of_table	end_of_table	end_of_tables	end_of_table	0	dmi end_of_table	dmi	integer
1f	end_of_tables of <dmi>: dmi end_of_table	end_of_table	end_of_tables	end_of_tables	1	dmi end_of_table	dmi	
1f	ending_address of <dmi memory_array_mapped_address>: integer	ending_address	ending_addresss	ending_address	0	integer	dmi memory_array_mapped_address	
1f	ending_address of <dmi memory_device_mapped_address>: integer	ending_address	ending_addresss	ending_address	0	integer	dmi memory_device_mapped_address	
10	engine pid of <running task>: integer	engine pid	engine pids	engine pid	0	integer	running task	
ff	enhanced security of <license>: boolean	enhanced security	enhanced securities	enhanced security	0	boolean	license	
10	enterprise bit <operating system suite mask>: boolean	enterprise bit	enterprise bits	enterprise bit	0	boolean		operating system suite mask
10	entries of <access control list>: access control entry	entry	entries	entries	1	access control entry	access control list	
2	entries of <dictionary>: dictionaryentry	entry	entries	entries	1	dictionaryentry	dictionary	
10	enumerate subkeys permission of <access control entry>: boolean	enumerate subkeys permission	enumerate subkeys permissions	enumerate subkeys permission	0	boolean	access control entry	
d	environment of <process>: environment	environment	environments	environment	0	environment	process	
1f	environment: environment	environment	environments	environment	0	environment		
9	epoch of <debian package version>: debian package version epoch	epoch	epochs	epoch	0	debian package version epoch	debian package version	
4	epoch of <rpm package version record>: integer	epoch	epochs	epoch	0	integer	rpm package version record	
4	epoch of <short rpm package version record>: integer	epoch	epochs	epoch	0	integer	short rpm package version record	
ff	error <string>: undefined	error	errors	error	0	undefined		string
12	error code of <agent interface capability>: integer	error code	error codes	error code	0	integer	agent interface capability	
10	error event log event type: event log event type	error event log event type	error event log event types	error event log event type	0	event log event type		
e0	error flag of <bes property result>: boolean	error flag	error flags	error flag	0	boolean	bes property result	
e0	error message of <bes property result>: string	error message	error messages	error message	0	string	bes property result	
1f	error_correcting_capability of <dmi memory_controller_information>: integer	error_correcting_capability	error_correcting_capabilitys	error_correcting_capability	0	integer	dmi memory_controller_information	
1f	error_correction_type of <dmi cache_information>: integer	error_correction_type	error_correction_types	error_correction_type	0	integer	dmi cache_information	
1f	error_detecting_method of <dmi memory_controller_information>: integer	error_detecting_method	error_detecting_methods	error_detecting_method	0	integer	dmi memory_controller_information	
1f	error_granularity of <dmi b32_bit_memory_error_information>: integer	error_granularity	error_granularitys	error_granularity	0	integer	dmi b32_bit_memory_error_information	
1f	error_granularity of <dmi b64_bit_memory_error_information>: integer	error_granularity	error_granularitys	error_granularity	0	integer	dmi b64_bit_memory_error_information	
1f	error_operation of <dmi b32_bit_memory_error_information>: integer	error_operation	error_operations	error_operation	0	integer	dmi b32_bit_memory_error_information	
1f	error_operation of <dmi b64_bit_memory_error_information>: integer	error_operation	error_operations	error_operation	0	integer	dmi b64_bit_memory_error_information	
1f	error_resolution of <dmi b32_bit_memory_error_information>: integer	error_resolution	error_resolutions	error_resolution	0	integer	dmi b32_bit_memory_error_information	
1f	error_resolution of <dmi b64_bit_memory_error_information>: integer	error_resolution	error_resolutions	error_resolution	0	integer	dmi b64_bit_memory_error_information	
1f	error_status of <dmi memory_module_information>: integer	error_status	error_statuss	error_status	0	integer	dmi memory_module_information	
1f	error_type of <dmi b32_bit_memory_error_information>: integer	error_type	error_types	error_type	0	integer	dmi b32_bit_memory_error_information	
1f	error_type of <dmi b64_bit_memory_error_information>: integer	error_type	error_types	error_type	0	integer	dmi b64_bit_memory_error_information	
10	escape of <string>: string	escape	escapes	escape	0	string	string	
1f	established of <tcp state>: boolean	established	establisheds	established	0	boolean	tcp state	
1f	evaluated of <site>: boolean	evaluated	evaluateds	evaluated	0	boolean	site	
ff	evaluation of <license>: boolean	evaluation	evaluations	evaluation	0	boolean	license	
40	evaluation period of <bes fixlet>: time interval	evaluation period	evaluation periods	evaluation period	0	time interval	bes fixlet	
e0	evaluation period of <bes property>: time interval	evaluation period	evaluation periods	evaluation period	0	time interval	bes property	
1f	evaluationcycle of <client>: evaluation cycle	evaluationcycle	evaluationcycles	evaluationcycle	0	evaluation cycle	client	
10	event id of <event log record>: integer	event id	event ids	event id	0	integer	event log record	
10	event log <string>: event log	event log	event logs	event log	0	event log		string
10	event log event type <integer>: event log event type	event log event type	event log event types	event log event type	0	event log event type		integer
10	event task trigger type: task trigger type	event task trigger type	event task trigger types	event task trigger type	0	task trigger type		
10	event type of <event log record>: event log event type	event type	event types	event type	0	event log event type	event log record	
10	everyone group: security account	everyone group	everyone groups	everyone group	0	security account		
10	exceptions allowed of <firewall profile>: boolean	exceptions allowed	exceptions alloweds	exceptions allowed	0	boolean	firewall profile	
10	excluded interfaces of <firewall profile>: string	excluded interface	excluded interfaces	excluded interfaces	1	string	firewall profile	
d	exec shield of <process>: boolean	exec shield	exec shields	exec shield	0	boolean	process	
10	exec task action type: task action type	exec task action type	exec task action types	exec task action type	0	task action type		
d	exec time of <process>: time interval	exec time	exec times	exec time	0	time interval	process	
10	executable file format of <file>: string	executable file format	executable file formats	executable file format	0	string	file	
d	execute of <mode_mask>: boolean	execute	executes	execute	0	boolean	mode_mask	
10	execute permission of <access control entry>: boolean	execute permission	execute permissions	execute permission	0	boolean	access control entry	
10	execute permission of <network share>: boolean	execute permission	execute permissions	execute permission	0	boolean	network share	
10	execution time limit of <task settings>: time interval	execution time limit	execution time limits	execution time limit	0	time interval	task settings	
10	execution time limit of <task trigger>: time interval	execution time limit	execution time limits	execution time limit	0	time interval	task trigger	
1f	executions <string>: execution	execution	executions	executions	1	execution		string
1f	exit code of <action>: integer	exit code	exit codes	exit code	0	integer	action	
e0	exit code of <bes action result>: integer	exit code	exit codes	exit code	0	integer	bes action result	
10	expand environment string of <string>: string	expand environment string	expand environment strings	expand environment string	0	string	string	
10	expand x32 environment string of <string>: string	expand x32 environment string	expand x32 environment strings	expand x32 environment string	0	string	string	
10	expand x64 environment string of <string>: string	expand x64 environment string	expand x64 environment strings	expand x64 environment string	0	string	string	
1f	expiration date of <action lock state>: time	expiration date	expiration dates	expiration date	0	time	action lock state	
ff	expiration date of <bes product>: date	expiration date	expiration dates	expiration date	0	date	bes product	
ff	expiration date of <license>: time	expiration date	expiration dates	expiration date	0	time	license	
e0	expiration flag of <bes action>: boolean	expiration flag	expiration flags	expiration flag	0	boolean	bes action	
ff	expiration state of <license>: string	expiration state	expiration states	expiration state	0	string	license	
e0	expiration time of <bes action>: time	expiration time	expiration times	expiration time	0	time	bes action	
2	expiration time of <route>: time	expiration time	expiration times	expiration time	0	time	route	
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
1d	explorer service: service	explorer service	explorer services	explorer service	0	service		
e0	exponential fit of <statistical bin>: exponential projection	exponential fit	exponential fits	exponential fit	0	exponential projection	statistical bin	
12	extended family of <processor>: integer	extended family	extended families	extended family	0	integer	processor	
1f	extended feature mask of <processor>: integer	extended feature mask	extended feature masks	extended feature mask	0	integer	processor	
12	extended model of <processor>: integer	extended model	extended models	extended model	0	integer	processor	
e0	extension flag of <bes computer>: boolean	extension flag	extension flags	extension flag	0	boolean	bes computer	
2	extensions <string>: enableable_file	extension	extensions	extensions	1	enableable_file		string
2	extensions folder of <domain>: folder	extensions folder	extensions folders	extensions folder	0	folder	domain	
2	extensions folder: folder	extensions folder	extensions folders	extensions folder	0	folder		
2	extensions: enableable_file	extension	extensions	extensions	1	enableable_file		
10	external port of <port mapping>: integer	external port	external ports	external port	0	integer	port mapping	
e0	external site flag of <bes site>: boolean	external site flag	external site flags	external site flag	0	boolean	bes site	
1f	external_clock of <dmi processor_information>: integer	external_clock	external_clocks	external_clock	0	integer	dmi processor_information	
1f	external_connector_type of <dmi port_connector_information>: integer	external_connector_type	external_connector_types	external_connector_type	0	integer	dmi port_connector_information	
1f	external_reference_designator of <dmi port_connector_information>: string	external_reference_designator	external_reference_designators	external_reference_designator	0	string	dmi port_connector_information	
e2	extrapolation <time> of <exponential projection>: floating point	extrapolation	extrapolations	extrapolation	0	floating point	exponential projection	time
e2	extrapolation <time> of <linear projection>: floating point	extrapolation	extrapolations	extrapolation	0	floating point	linear projection	time
ff	extremas of <date>: ( date, date )	extrema	extremas	extremas	1	( date, date )	date	
ff	extremas of <day of month>: ( day of month, day of month )	extrema	extremas	extremas	1	( day of month, day of month )	day of month	
ff	extremas of <day of year>: ( day of year, day of year )	extrema	extremas	extremas	1	( day of year, day of year )	day of year	
9	extremas of <debian package upstream version>: ( debian package upstream version, debian package upstream version )	extrema	extremas	extremas	1	( debian package upstream version, debian package upstream version )	debian package upstream version	
9	extremas of <debian package version epoch>: ( debian package version epoch, debian package version epoch )	extrema	extremas	extremas	1	( debian package version epoch, debian package version epoch )	debian package version epoch	
9	extremas of <debian package version revision>: ( debian package version revision, debian package version revision )	extrema	extremas	extremas	1	( debian package version revision, debian package version revision )	debian package version revision	
9	extremas of <debian package version>: ( debian package version, debian package version )	extrema	extremas	extremas	1	( debian package version, debian package version )	debian package version	
ff	extremas of <floating point>: ( floating point, floating point )	extrema	extremas	extremas	1	( floating point, floating point )	floating point	
ff	extremas of <hertz>: ( hertz, hertz )	extrema	extremas	extremas	1	( hertz, hertz )	hertz	
ff	extremas of <integer>: ( integer, integer )	extrema	extremas	extremas	1	( integer, integer )	integer	
ff	extremas of <ipv4 address>: ( ipv4 address, ipv4 address )	extrema	extremas	extremas	1	( ipv4 address, ipv4 address )	ipv4 address	
ff	extremas of <ipv4or6 address>: ( ipv4or6 address, ipv4or6 address )	extrema	extremas	extremas	1	( ipv4or6 address, ipv4or6 address )	ipv4or6 address	
ff	extremas of <ipv6 address>: ( ipv6 address, ipv6 address )	extrema	extremas	extremas	1	( ipv6 address, ipv6 address )	ipv6 address	
5f	extremas of <large integer>: ( large integer, large integer )	extrema	extremas	extremas	1	( large integer, large integer )	large integer	
ff	extremas of <month and year>: ( month and year, month and year )	extrema	extremas	extremas	1	( month and year, month and year )	month and year	
ff	extremas of <month>: ( month, month )	extrema	extremas	extremas	1	( month, month )	month	
ff	extremas of <number of months>: ( number of months, number of months )	extrema	extremas	extremas	1	( number of months, number of months )	number of months	
e2	extremas of <rate>: ( rate, rate )	extrema	extremas	extremas	1	( rate, rate )	rate	
4	extremas of <rpm package release>: ( rpm package release, rpm package release )	extrema	extremas	extremas	1	( rpm package release, rpm package release )	rpm package release	
4	extremas of <rpm package version record>: ( rpm package version record, rpm package version record )	extrema	extremas	extremas	1	( rpm package version record, rpm package version record )	rpm package version record	
4	extremas of <rpm package version>: ( rpm package version, rpm package version )	extrema	extremas	extremas	1	( rpm package version, rpm package version )	rpm package version	
4	extremas of <short rpm package version record>: ( short rpm package version record, short rpm package version record )	extrema	extremas	extremas	1	( short rpm package version record, short rpm package version record )	short rpm package version record	
ff	extremas of <site version list>: ( site version list, site version list )	extrema	extremas	extremas	1	( site version list, site version list )	site version list	
ff	extremas of <time interval>: ( time interval, time interval )	extrema	extremas	extremas	1	( time interval, time interval )	time interval	
ff	extremas of <time of day>: ( time of day, time of day )	extrema	extremas	extremas	1	( time of day, time of day )	time of day	
ff	extremas of <time>: ( time, time )	extrema	extremas	extremas	1	( time, time )	time	
5f	extremas of <uinteger>: ( uinteger, uinteger )	extrema	extremas	extremas	1	( uinteger, uinteger )	uinteger	
1f	extremas of <uuid>: ( uuid, uuid )	extrema	extremas	extremas	1	( uuid, uuid )	uuid	
ff	extremas of <version>: ( version, version )	extrema	extremas	extremas	1	( version, version )	version	
ff	extremas of <year>: ( year, year )	extrema	extremas	extremas	1	( year, year )	year	
d	f00f bug of <processor>: boolean	f00f bug	f00f bugs	f00f bug	0	boolean	processor	
e0	failure rate of <statistical bin>: floating point	failure rate	failure rates	failure rate	0	floating point	statistical bin	
d	fallback image <integer> of <grub config file>: grub image choice	fallback image	fallback images	fallback image	0	grub image choice	grub config file	integer
d	fallback images of <grub config file>: grub image choice	fallback image	fallback images	fallback images	1	grub image choice	grub config file	
ff	false: boolean	false	falses	false	0	boolean		
2	family name of <network interface>: string	family name	family names	family name	0	string	network interface	
1f	family name of <processor>: string	family name	family names	family name	0	string	processor	
10	family name of <winrt package id>: string	family name	family names	family name	0	string	winrt package id	
1f	family of <dmi system_information>: string	family	familys	family	0	string	dmi system_information	
1f	family of <network interface>: integer	family	families	family	0	integer	network interface	
1f	family of <processor>: integer	family	families	family	0	integer	processor	
2	fast scsi of <scsibus>: boolean	fast scsi	fast scsis	fast scsi	0	boolean	scsibus	
2	favorites folder of <domain>: folder	favorites folder	favorites folders	favorites folder	0	folder	domain	
2	favorites folder: folder	favorites folder	favorites folders	favorites folder	0	folder		
d	fdiv bug of <processor>: boolean	fdiv bug	fdiv bugs	fdiv bug	0	boolean	processor	
1f	feature mask of <processor>: integer	feature mask	feature masks	feature mask	0	integer	processor	
1f	feature_flags of <dmi base_board_information>: integer	feature_flags	feature_flagss	feature_flags	0	integer	dmi base_board_information	
ff	february <integer> of <integer>: date	february	februarys	february	0	date	integer	integer
ff	february <integer>: day of year	february	februarys	february	0	day of year		integer
ff	february of <integer>: month and year	february	februarys	february	0	month and year	integer	
ff	february: month	february	februarys	february	0	month		
e0	field <string> of <bes fixlet>: bes fixlet field	field	fields	field	0	bes fixlet field	bes fixlet	string
e0	fields of <bes fixlet>: bes fixlet field	field	fields	fields	1	bes fixlet field	bes fixlet	
e0	fields of <bes unmanagedasset>: bes unmanagedasset field	field	fields	fields	1	bes unmanagedasset field	bes unmanagedasset	
d	fifo file <filesystem object>: fifo file	fifo file	fifo files	fifo file	0	fifo file		filesystem object
d	fifo file <string> of <folder>: fifo file	fifo file	fifo files	fifo file	0	fifo file	folder	string
d	fifo file <string>: fifo file	fifo file	fifo files	fifo file	0	fifo file		string
d	fifo file <symlink>: fifo file	fifo file	fifo files	fifo file	0	fifo file		symlink
d	fifo files of <folder>: fifo file	fifo file	fifo files	fifo files	1	fifo file	folder	
1d	file <binary_string> of <encoding>: file	file	files	file	0	file	encoding	binary_string
1f	file <binary_string> of <folder>: file	file	files	file	0	file	folder	binary_string
1f	file <binary_string>: file	file	files	file	0	file		binary_string
1f	file <string> of <encoding>: file	file	files	file	0	file	encoding	string
1f	file <string> of <folder>: file	file	files	file	0	file	folder	string
1f	file <string>: file	file	files	file	0	file		string
d	file <symlink>: file	file	files	file	0	file		symlink
d	file count of <filesystem>: integer	file count	file counts	file count	0	integer	filesystem	
2	file count of <volume>: integer	file count	file counts	file count	0	integer	volume	
10	file extension <string> of <registry>: registry key	file extension	file extensions	file extension	0	registry key	registry	string
1d	file of <service>: file	file	files	file	0	file	service	
2	file signature <string>: file signature	file signature	file signatures	file signature	0	file signature		string
10	file system type of <drive>: string	file system type	file system types	file system type	0	string	drive	
10	file type <string> of <registry>: registry key	file type	file types	file type	0	registry key	registry	string
2	file type <string>: file type	file type	file types	file type	0	file type		string
10	file version of <file>: version	file version	file versions	file version	0	version	file	
10	file_and_print firewall service type: firewall service type	file_and_print firewall service type	file_and_print firewall service types	file_and_print firewall service type	0	firewall service type		
10	file_supports_encryption of <drive>: boolean	file_supports_encryption	file_supports_encryptions	file_supports_encryption	0	boolean	drive	
10	file_supports_object_ids of <drive>: boolean	file_supports_object_ids	file_supports_object_idss	file_supports_object_ids	0	boolean	drive	
10	file_supports_reparse_points of <drive>: boolean	file_supports_reparse_points	file_supports_reparse_pointss	file_supports_reparse_points	0	boolean	drive	
10	file_supports_sparse_files of <drive>: boolean	file_supports_sparse_files	file_supports_sparse_filess	file_supports_sparse_files	0	boolean	drive	
10	file_volume_quotas of <drive>: boolean	file_volume_quotas	file_volume_quotass	file_volume_quotas	0	boolean	drive	
2	files ending in <string> of <folder>: file	file ending in	files ending in	files ending in	1	file	folder	string
1f	files of <folder>: file	file	files	files	1	file	folder	
2	filesystem <integer>: volume	filesystem	filesystems	filesystem	0	volume		integer
d	filesystem <string>: filesystem	filesystem	filesystems	filesystem	0	filesystem		string
d	filesystem of <device file>: filesystem	filesystem	filesystems	filesystem	0	filesystem	device file	
d	filesystem of <fifo file>: filesystem	filesystem	filesystems	filesystem	0	filesystem	fifo file	
d	filesystem of <file>: filesystem	filesystem	filesystems	filesystem	0	filesystem	file	
2	filesystem of <file>: volume	filesystem	filesystems	filesystem	0	volume	file	
d	filesystem of <folder>: filesystem	filesystem	filesystems	filesystem	0	filesystem	folder	
2	filesystem of <folder>: volume	filesystem	filesystems	filesystem	0	volume	folder	
d	filesystem of <socket file>: filesystem	filesystem	filesystems	filesystem	0	filesystem	socket file	
d	filesystem of <symlink>: filesystem	filesystem	filesystems	filesystem	0	filesystem	symlink	
d	filesystem type of <filesystem>: string	filesystem type	filesystem types	filesystem type	0	string	filesystem	
2	filesystems <string>: volume	filesystem	filesystems	filesystems	1	volume		string
d	filesystems: filesystem	filesystem	filesystems	filesystems	1	filesystem		
2	filesystems: volume	filesystem	filesystems	filesystems	1	volume		
e0	filter set of <bes domain>: bes filter set	filter set	filter sets	filter set	0	bes filter set	bes domain	
e0	filterable flag of <bes unmanagedasset field>: boolean	filterable flag	filterable flags	filterable flag	0	boolean	bes unmanagedasset field	
e0	filters of <bes domain>: bes filter	filter	filters	filters	1	bes filter	bes domain	
1f	fin wait one of <tcp state>: boolean	fin wait one	fin wait ones	fin wait one	0	boolean	tcp state	
1f	fin wait two of <tcp state>: boolean	fin wait two	fin wait twos	fin wait two	0	boolean	tcp state	
ff	final part <time interval> of <time range>: time range	final part	final parts	final part	0	time range	time range	time interval
1f	find adapters <string> of <network>: network adapter	find adapter	find adapters	find adapters	1	network adapter	network	string
1f	find files <string> of <folder>: file	find file	find files	find files	1	file	folder	string
1f	find folders <string> of <folder>: folder	find folder	find folders	find folders	1	folder	folder	string
2	find items <string> of <folder>: filesystem object	find item	find items	find items	1	filesystem object	folder	string
ff	finite of <floating point>: boolean	finite	finites	finite	0	boolean	floating point	
ff	fips mode failure message of <cryptography>: string	fips mode failure message	fips mode failure messages	fips mode failure message	0	string	cryptography	
ff	fips mode of <cryptography>: boolean	fips mode	fips modes	fips mode	0	boolean	cryptography	
ff	fips mode of <license>: boolean	fips mode	fips modes	fips mode	0	boolean	license	
12	firewall action <integer>: firewall action	firewall action	firewall actions	firewall action	0	firewall action		integer
10	firewall enabled of <firewall profile>: boolean	firewall enabled	firewalls enabled	firewall enabled	0	boolean	firewall profile	
10	firewall local policy modify state <integer>: firewall local policy modify state	firewall local policy modify state	firewall local policy modify states	firewall local policy modify state	0	firewall local policy modify state		integer
10	firewall of <connection>: internet connection firewall	firewall	firewalls	firewall	0	internet connection firewall	connection	
10	firewall profile type <integer>: firewall profile type	firewall profile type	firewall profile types	firewall profile type	0	firewall profile type		integer
10	firewall scope <integer>: firewall scope	firewall scope	firewall scopes	firewall scope	0	firewall scope		integer
10	firewall service type <integer>: firewall service type	firewall service type	firewall service types	firewall service type	0	firewall service type		integer
12	firewall: firewall	firewall	firewalls	firewall	0	firewall		
2	firewire plane of <registryroot>: registrynode	firewire plane	firewire planes	firewire plane	0	registrynode	registryroot	
ff	first <day of week> of <month and year>: date	first	firsts	first	0	date	month and year	day of week
ff	first <integer> of <binary_string>: binary_substring	first	firsts	first	0	binary_substring	binary_string	integer
ff	first <integer> of <string>: substring	first	firsts	first	0	substring	string	integer
ff	first <string> of <string>: substring	first	firsts	first	0	substring	string	string
1f	first active count of <action>: integer	first active count	first active counts	first active count	0	integer	action	
e0	first became relevant of <bes fixlet result>: time	first became relevant	first became relevants	first became relevant	0	time	bes fixlet result	
bd	first child of <xml dom node>: xml dom node	first child	first children	first child	0	xml dom node	xml dom node	
ff	first friday of <month and year>: date	first friday	first fridays	first friday	0	date	month and year	
10	first interface scheduled tasks: scheduled task	first interface scheduled task	first interface scheduled tasks	first interface scheduled tasks	1	scheduled task		
1f	first line of <file>: file line	first line	first lines	first line	0	file line	file	
1f	first lines <integer> of <file>: file line	first line	first lines	first lines	1	file line	file	integer
ff	first matches <regular expression> of <string>: regular expression match	first match	first matches	first matches	1	regular expression match	string	regular expression
ff	first monday of <month and year>: date	first monday	first mondays	first monday	0	date	month and year	
10	first raw version block of <file>: file version block	first raw version block	first raw version blocks	first raw version block	0	file version block	file	
1f	first rawline of <file>: file line	first rawline	first rawlines	first rawline	0	file line	file	
1f	first rawlines <integer> of <file>: file line	first rawline	first rawlines	first rawlines	1	file line	file	integer
ff	first saturday of <month and year>: date	first saturday	first saturdays	first saturday	0	date	month and year	
1f	first start time of <application usage summary instance>: time	first start time	first start times	first start time	0	time	application usage summary instance	
1f	first start time of <application usage summary>: time	first start time	first start times	first start time	0	time	application usage summary	
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
1f	fixlets of <site>: fixlet	fixlet	fixlets	fixlets	1	fixlet	site	
d	flag list of <processor>: string	flag list	flag lists	flag list	0	string	processor	
d	flag of <Xinetd Service>: string	flag	flags	flag	0	string	Xinetd Service	
2	flag of <volume>: integer	flag	flags	flag	0	integer	volume	
1f	flags of <dmi bios_language_information>: integer	flags	flagss	flags	0	integer	dmi bios_language_information	
2	flags string of <route>: string	flags string	flags strings	flags string	0	string	route	
1f	float of <sqlite column type>: boolean	float	floats	float	0	boolean	sqlite column type	
ff	floating point <floating point>: floating point	floating point	floating points	floating point	0	floating point		floating point
ff	floating point <string>: floating point	floating point	floating points	floating point	0	floating point		string
1d	folder <binary_string> of <encoding>: folder	folder	folders	folder	0	folder	encoding	binary_string
1f	folder <binary_string> of <folder>: folder	folder	folders	folder	0	folder	folder	binary_string
1f	folder <binary_string>: folder	folder	folders	folder	0	folder		binary_string
10	folder <string> of <drive>: folder	folder	folders	folder	0	folder	drive	string
1f	folder <string> of <encoding>: folder	folder	folders	folder	0	folder	encoding	string
1f	folder <string> of <folder>: folder	folder	folders	folder	0	folder	folder	string
1f	folder <string>: folder	folder	folders	folder	0	folder		string
d	folder <symlink>: folder	folder	folders	folder	0	folder		symlink
1d	folder of <service>: folder	folder	folders	folder	0	folder	service	
1f	folder of <site>: folder	folder	folders	folder	0	folder	site	
2	folders ending in <string> of <folder>: folder	folder ending in	folders ending in	folders ending in	1	folder	folder	string
1f	folders of <folder>: folder	folder	folders	folders	1	folder	folder	
ff	following binary_string of <binary position>: binary_substring	following binary_string	following binary_strings	following binary_string	0	binary_substring	binary position	
ff	following binary_string of <binary_substring>: binary_substring	following binary_string	following binary_strings	following binary_string	0	binary_substring	binary_substring	
ff	following text of <string position>: substring	following text	following texts	following text	0	substring	string position	
ff	following text of <substring>: substring	following text	following texts	following text	0	substring	substring	
2	fonts folder of <domain>: folder	fonts folder	fonts folders	fonts folder	0	folder	domain	
2	fonts folder: folder	fonts folder	fonts folders	fonts folder	0	folder		
10	force logoff interval of <security database>: time interval	force logoff interval	force logoff intervals	force logoff interval	0	time interval	security database	
d	foreground of <grub color pair>: grub color	foreground	foregrounds	foreground	0	grub color	grub color pair	
1f	form_factor of <dmi memory_device>: integer	form_factor	form_factors	form_factor	0	integer	dmi memory_device	
ff	format <string>: format	format	formats	format	0	format		string
d	fpu exception of <processor>: boolean	fpu exception	fpu exceptions	fpu exception	0	boolean	processor	
d	fpu of <processor>: boolean	fpu	fpus	fpu	0	boolean	processor	
2	framework <string> of <domain>: folder	framework	frameworks	framework	0	folder	domain	string
2	framework <string>: folder	framework	frameworks	framework	0	folder		string
2	framework folder of <domain>: folder	framework folder	framework folders	framework folder	0	folder	domain	
2	framework folder: folder	framework folder	framework folders	framework folder	0	folder		
1f	free amount of <ram>: integer	free amount	free amounts	free amount	0	integer	ram	
f	free amount of <swap>: integer	free amount	free amounts	free amount	0	integer	swap	
d	free file count of <filesystem>: integer	free file count	free file counts	free file count	0	integer	filesystem	
d	free percent of <filesystem>: integer	free percent	free percents	free percent	0	integer	filesystem	
2	free percent of <volume>: integer	free percent	free percents	free percent	0	integer	volume	
10	free space of <drive>: integer	free space	free spaces	free space	0	integer	drive	
d	free space of <filesystem>: integer	free space	free spaces	free space	0	integer	filesystem	
2	free space of <volume>: integer	free space	free spaces	free space	0	integer	volume	
ff	friday: day of week	friday	fridays	friday	0	day of week		
10	friendly name of <active device>: string	friendly name	friendly names	friendly name	0	string	active device	
1f	friendly name of <network adapter>: string	friendly name	friendly names	friendly name	0	string	network adapter	
10	from of <email task action>: string	from	froms	from	0	string	email task action	
10	fs_case_is_preserved of <drive>: boolean	fs_case_is_preserved	fs_case_is_preserveds	fs_case_is_preserved	0	boolean	drive	
10	fs_case_sensitive of <drive>: boolean	fs_case_sensitive	fs_case_sensitives	fs_case_sensitive	0	boolean	drive	
10	fs_file_compression of <drive>: boolean	fs_file_compression	fs_file_compressions	fs_file_compression	0	boolean	drive	
10	fs_persistent_acls of <drive>: boolean	fs_persistent_acls	fs_persistent_aclss	fs_persistent_acls	0	boolean	drive	
10	fs_unicode_stored_on_disk of <drive>: boolean	fs_unicode_stored_on_disk	fs_unicode_stored_on_disks	fs_unicode_stored_on_disk	0	boolean	drive	
10	fs_vol_is_compressed of <drive>: boolean	fs_vol_is_compressed	fs_vol_is_compresseds	fs_vol_is_compressed	0	boolean	drive	
d	fstype of <filesystem>: string	fstype	fstypes	fstype	0	string	filesystem	
1f	full gateway addresses of <selected server>: ipv4or6 address	full gateway address	full gateway addresses	full gateway addresses	1	ipv4or6 address	selected server	
12	full name of <user>: string	full name	full names	full name	0	string	user	
10	full name of <winrt package id>: string	full name	full names	full name	0	string	winrt package id	
1f	full of <power level>: boolean	full	fulls	full	0	boolean	power level	
10	full wmi <string>: wmi	full wmi	full wmis	full wmi	0	wmi		string
e0	fxf character set of <bes server>: string	fxf character set	fxf character sets	fxf character set	0	string	bes server	
1f	fxf character set of <client>: string	fxf character set	fxf character sets	fxf character set	0	string	client	
ff	fxf encoding concatenations <string> of <string>: string	fxf encoding concatenation	fxf encoding concatenations	fxf encoding concatenations	1	string	string	string
ff	fxf encoding concatenations of <string>: string	fxf encoding concatenation	fxf encoding concatenations	fxf encoding concatenations	1	string	string	
1f	gateway address <integer> of <selected server>: ipv4or6 address	gateway address	gateway addresses	gateway address	0	ipv4or6 address	selected server	integer
1f	gateway addresses of <selected server>: ipv4or6 address	gateway address	gateway addresses	gateway addresses	1	ipv4or6 address	selected server	
f	gateway flag of <route>: boolean	gateway flag	gateway flags	gateway flag	0	boolean	route	
10	gateway lists of <network adapter>: network address list	gateway list	gateway lists	gateway lists	1	network address list	network adapter	
10	gateway of <network adapter>: ipv4 address	gateway	gateways	gateway	0	ipv4 address	network adapter	
f	gateway of <route>: ipv4or6 address	gateway	gateways	gateway	0	ipv4or6 address	route	
2	gateway string of <route>: string	gateway string	gateway strings	gateway string	0	string	route	
2	gateway type of <route>: string	gateway type	gateways types	gateway type	0	string	route	
1f	gather duration of <evaluation cycle>: time interval	gather duration	gather durations	gather duration	0	time interval	evaluation cycle	
40	gather flag of <bes peer download>: boolean	gather flag	gather flags	gather flag	0	boolean	bes peer download	
1f	gather percent of <evaluation cycle>: floating point	gather percent	gather percents	gather percent	0	floating point	evaluation cycle	
1f	gather schedule authority of <site>: string	gather schedule authority	gather schedule authoritys	gather schedule authority	0	string	site	
1f	gather schedule time interval of <site>: time interval	gather schedule time interval	gather schedule time intervals	gather schedule time interval	0	time interval	site	
ff	gather url of <license>: string	gather url	gather urls	gather url	0	string	license	
10	gdi object count of <process>: integer	gdi object count	gdi object counts	gdi object count	0	integer	process	
10	generic all permission of <access control entry>: boolean	generic all permission	generic all permissions	generic all permission	0	boolean	access control entry	
10	generic execute permission of <access control entry>: boolean	generic execute permission	generic execute permissions	generic execute permission	0	boolean	access control entry	
40	generic ldap of <bes idp directory>: boolean	generic ldap	generic ldaps	generic ldap	0	boolean	bes idp directory	
10	generic read permission of <access control entry>: boolean	generic read permission	generic read permissions	generic read permission	0	boolean	access control entry	
10	generic write permission of <access control entry>: boolean	generic write permission	generic write permissions	generic write permission	0	boolean	access control entry	
e0	geometric mean of <statistical bin>: floating point	geometric mean	geometric means	geometric mean	0	floating point	statistical bin	
2	gestalt <string>: integer	gestalt	gestalts	gestalt	0	integer		string
d	gfxmenu of <grub config file>: grub file location	gfxmenu	gfxmenus	gfxmenu	0	grub file location	grub config file	
ff	ghz: hertz	ghz	ghzs	ghz	0	hertz		
d	gid of <filesystem object>: integer	gid	gids	gid	0	integer	filesystem object	
d	gid of <symlink>: integer	gid	gids	gid	0	integer	symlink	
40	global catalog of <bes idp directory>: boolean	global catalog	global catalogs	global catalog	0	boolean	bes idp directory	
e0	global catalog of <bes ldap directory>: boolean	global catalog	global catalogs	global catalog	0	boolean	bes ldap directory	
2	global dictionary of <bundle>: dictionary	global dictionary	global dictionaries	global dictionary	0	dictionary	bundle	
2	global state of <firewall>: string	global state	global states	global state	0	string	firewall	
e0	globally allowed flag of <bes webui app>: boolean	globally allowed flag	globally allowed flags	globally allowed flag	0	boolean	bes webui app	
10	globally open ports of <firewall profile>: firewall open port	globally open port	globally open ports	globally open ports	1	firewall open port	firewall profile	
10	globally open ports of <firewall service>: firewall open port	globally open port	globally open ports	globally open ports	1	firewall open port	firewall service	
e0	globally readable flag of <bes site>: boolean	globally readable flag	globally readable flags	globally readable flag	0	boolean	bes site	
e0	globally visible flag of <bes fixlet>: boolean	globally visible flag	globally visible flags	globally visible flag	0	boolean	bes fixlet	
10	gp override firewall local policy modify state: firewall local policy modify state	gp override firewall local policy modify state	gp override firewall local policy modify states	gp override firewall local policy modify state	0	firewall local policy modify state		
10	grant type of <access control entry>: boolean	grant type	grant types	grant type	0	boolean	access control entry	
ff	greatest hz: hertz	greatest hz	greatest hzs	greatest hz	0	hertz		
ff	greatest integer: integer	greatest integer	greatest integers	greatest integer	0	integer		
5f	greatest large integer: large integer	greatest large integer	greatest large integers	greatest large integer	0	large integer		
ff	greatest time interval: time interval	greatest time interval	greatest time intervals	greatest time interval	0	time interval		
5f	greatest uinteger: uinteger	greatest uinteger	greatest uintegers	greatest uinteger	0	uinteger		
1f	group <integer> of <site>: site group	group	groups	group	0	site group	site	integer
12	group <string> of <active directory local computer>: active directory group	group	groups	group	0	active directory group	active directory local computer	string
12	group <string> of <active directory local user>: active directory group	group	groups	group	0	active directory group	active directory local user	string
d	group execute of <filesystem object>: boolean	group execute	group executes	group execute	0	boolean	filesystem object	
40	group filter of <bes idp directory>: string	group filter	group filters	group filter	0	string	bes idp directory	
e0	group filter of <bes ldap directory>: string	group filter	group filters	group filter	0	string	bes ldap directory	
e0	group flag of <bes filter>: boolean	group flag	group flags	group flag	0	boolean	bes filter	
e0	group flag of <bes fixlet>: boolean	group flag	group flags	group flag	0	boolean	bes fixlet	
10	group id of <task principal>: string	group id	group ids	group id	0	string	task principal	
1f	group leader of <action>: boolean	group leader	group leaders	group leader	0	boolean	action	
10	group logon of <task principal>: boolean	group logon	group logons	group logon	0	boolean	task principal	
d	group mask of <filesystem object>: integer	group mask	group masks	group mask	0	integer	filesystem object	
d	group mask of <mode>: mode_mask	group mask	group masks	group mask	0	mode_mask	mode	
e0	group member flag of <bes action>: boolean	group member flag	group member flags	group member flag	0	boolean	bes action	
d	group name of <filesystem object>: string	group name	group names	group name	0	string	filesystem object	
d	group name of <symlink>: string	group name	group names	group name	0	string	symlink	
10	group of <security descriptor>: security identifier	group	groups	group	0	security identifier	security descriptor	
d	group read of <filesystem object>: boolean	group read	group reads	group read	0	boolean	filesystem object	
d	group write of <filesystem object>: boolean	group write	group writes	group write	0	boolean	filesystem object	
1f	group_associations <integer> of <dmi>: dmi group_associations	group_associations	group_associationss	group_associations	0	dmi group_associations	dmi	integer
1f	group_associationss of <dmi>: dmi group_associations	group_associations	group_associationss	group_associationss	1	dmi group_associations	dmi	
1f	group_name of <dmi group_associations>: string	group_name	group_names	group_name	0	string	dmi group_associations	
10	grouping of <firewall rule>: string	grouping	groupings	grouping	0	string	firewall rule	
12	groups error message of <active directory local computer>: string	groups error message	groups error messages	groups error message	0	string	active directory local computer	
12	groups error message of <active directory local user>: string	groups error message	groups error messages	groups error message	0	string	active directory local user	
12	groups of <active directory local computer>: active directory group	group	groups	groups	1	active directory group	active directory local computer	
12	groups of <active directory local user>: active directory group	group	groups	groups	1	active directory group	active directory local user	
d	grub config file <string>: grub config file	grub config file	grub config files	grub config file	0	grub config file		string
d	grub config file: grub config file	grub config file	grub config files	grub config file	0	grub config file		
10	guest privilege of <user>: boolean	guest privilege	guest privileges	guest privilege	0	boolean	user	
10	guid of <audit policy information>: string	guid	guids	guid	0	string	audit policy information	
10	guid of <audit policy subcategory>: string	guid	guids	guid	0	string	audit policy subcategory	
10	guid of <connection>: string	guid	guids	guid	0	string	connection	
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
10	handle count of <process>: integer	handle count	handle counts	handle count	0	integer	process	
10	hardware ids of <active device>: string	hardware id	hardware ids	hardware ids	1	string	active device	
1f	hardware: hardware	hardware	hardwares	hardware	0	hardware		
1f	hardware_security <integer> of <dmi>: dmi hardware_security	hardware_security	hardware_securitys	hardware_security	0	dmi hardware_security	dmi	integer
1f	hardware_security_settings of <dmi hardware_security>: integer	hardware_security_settings	hardware_security_settingss	hardware_security_settings	0	integer	dmi hardware_security	
1f	hardware_securitys of <dmi>: dmi hardware_security	hardware_security	hardware_securitys	hardware_securitys	1	dmi hardware_security	dmi	
10	has blank sa password of <local mssql database>: boolean	has blank sa password	has blank sa passwords	has blank sa password	0	boolean	local mssql database	
d	has extended acl of <filesystem object>: boolean	has extended acl	has extended acls	has extended acl	0	boolean	filesystem object	
40	hash of <bes peer download>: string	hash	hashes	hash	0	string	bes peer download	
ff	head <string> of <html>: html	head	heads	head	0	html	html	string
ff	head <string> of <string>: html	head	heads	head	0	html	string	string
ff	head of <html>: html	head	heads	head	0	html	html	
ff	head of <string>: html	head	heads	head	0	html	string	
10	header fields of <email task action>: task named value pair	header field	header fields	header fields	1	task named value pair	email task action	
1f	headers <string> of <action>: fixlet_header	header	headers	headers	1	fixlet_header	action	string
1f	headers <string> of <fixlet>: fixlet_header	header	headers	headers	1	fixlet_header	fixlet	string
1f	headers of <action>: fixlet_header	header	headers	headers	1	fixlet_header	action	
1f	headers of <fixlet>: fixlet_header	header	headers	headers	1	fixlet_header	fixlet	
1f	height of <dmi system_enclosure_or_chassis>: integer	height	heights	height	0	integer	dmi system_enclosure_or_chassis	
2	help folder of <domain>: folder	help folder	help folders	help folder	0	folder	domain	
2	help folder: folder	help folder	help folders	help folder	0	folder		
ff	hexadecet <integer> of <ipv4or6 address>: integer	hexadecet	hexadecets	hexadecet	0	integer	ipv4or6 address	integer
ff	hexadecet <integer> of <ipv6 address>: integer	hexadecet	hexadecets	hexadecet	0	integer	ipv6 address	integer
ff	hexadecimal integer <string>: integer	hexadecimal integer	hexadecimal integers	hexadecimal integer	0	integer		string
5f	hexadecimal large integer <string>: large integer	hexadecimal large integer	hexadecimal large integers	hexadecimal large integer	0	large integer		string
1f	hexadecimal of <smbios value>: string	hexadecimal	hexadecimals	hexadecimal	0	string	smbios value	
ff	hexadecimal string <string>: string	hexadecimal string	hexadecimal strings	hexadecimal string	0	string		string
5f	hexadecimal uinteger <string>: uinteger	hexadecimal uinteger	hexadecimal uintegers	hexadecimal uinteger	0	uinteger		string
1f	hexadecimals <string> of <smbios structure>: string	hexadecimal	hexadecimals	hexadecimals	1	string	smbios structure	string
2	hfs file <string> of <encoding>: file	hfs file	hfs files	hfs file	0	file	encoding	string
2	hfs file <string>: file	hfs file	hfs files	hfs file	0	file		string
2	hfs folder <string> of <encoding>: folder	hfs folder	hfs folders	hfs folder	0	folder	encoding	string
2	hfs folder <string>: folder	hfs folder	hfs folders	hfs folder	0	folder		string
2	hfs item <string>: filesystem object	hfs item	hfs items	hfs item	0	filesystem object		string
2	hfs path of <filesystem object>: string	hfs path	hfs paths	hfs path	0	string	filesystem object	
2	hfs relative item <string> of <folder>: filesystem object	hfs relative item	hfs relative items	hfs relative item	0	filesystem object	folder	string
e0	hidden bes action set: bes action set	hidden bes action set	hidden bes action sets	hidden bes action set	0	bes action set		
e0	hidden bes actions: bes action	hidden bes action	hidden bes actions	hidden bes actions	1	bes action		
e0	hidden flag of <bes action>: boolean	hidden flag	hidden flags	hidden flag	0	boolean	bes action	
10	hidden of <filesystem object>: boolean	hidden	hiddens	hidden	0	boolean	filesystem object	
10	hidden of <task settings>: boolean	hidden	hiddens	hidden	0	boolean	task settings	
d	hiddenmenu of <grub config file>: boolean	hiddenmenu	hiddenmenus	hiddenmenu	0	boolean	grub config file	
10	high priority: priority class	high priority	high priorities	high priority	0	priority class		
10	highest runlevel of <task principal>: boolean	highest runlevel	highest runlevels	highest runlevel	0	boolean	task principal	
d	highlight of <grub color scheme>: grub color pair	highlight	highlights	highlight	0	grub color pair	grub color scheme	
d	hlt bug of <processor>: boolean	hlt bug	hlt bugs	hlt bug	0	boolean	processor	
10	home directory drive of <user>: string	home directory drive	home directory drives	home directory drive	0	string	user	
12	home directory folder of <user>: folder	home directory folder	home directory folders	home directory folder	0	folder	user	
12	home directory of <user>: string	home directory	home directories	home directory	0	string	user	
10	home directory required flag of <user>: boolean	home directory required flag	home directory required flags	home directory required flag	0	boolean	user	
f	host flag of <route>: boolean	host flag	host flags	host flag	0	boolean	route	
1f	host name of <root server>: string	host name	host names	host name	0	string	root server	
d	host name: string	host name	host names	host name	0	string		
40	host of <bes idp directory server>: string	host	hosts	host	0	string	bes idp directory server	
e0	host of <bes ldap directory server>: string	host	hosts	host	0	string	bes ldap directory server	
e0	hostname of <bes computer>: string	hostname	hostnames	hostname	0	string	bes computer	
1f	hostname: string	hostname	hostnames	hostname	0	string		
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
10	hyperthreading capable: boolean	hyperthreading capable	hyperthreading capables	hyperthreading capable	0	boolean		
10	hyperthreading enabled: boolean	hyperthreading enabled	hyperthreading enableds	hyperthreading enabled	0	boolean		
1f	hypervisor of <operating system>: string	hypervisor	hypervisors	hypervisor	0	string	operating system	
ff	hz: hertz	hz	hzs	hz	0	hertz		
1f	i2c_slave_address of <dmi ipmi_device_information>: integer	i2c_slave_address	i2c_slave_addresss	i2c_slave_address	0	integer	dmi ipmi_device_information	
10	ia64 of <operating system>: boolean	ia64	ia64s	ia64	0	boolean	operating system	
12	ibss of <wifi network>: boolean	ibss	ibsss	ibss	0	boolean	wifi network	
10	icmp settings of <firewall profile>: firewall icmp settings	icmp settings	icmp settingses	icmp settings	0	firewall icmp settings	firewall profile	
10	icmp types_and_codes string of <firewall rule>: string	icmp types_and_codes string	icmp types_and_codes strings	icmp types_and_codes string	0	string	firewall rule	
10	icon index of <file shortcut>: integer	icon index	icon indexes	icon index	0	integer	file shortcut	
10	icon pathname of <file shortcut>: string	icon pathname	icon pathnames	icon pathname	0	string	file shortcut	
d	id of <Xinetd Service>: string	id	ids	id	0	string	Xinetd Service	
1f	id of <action>: integer	id	ids	id	0	integer	action	
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
10	id of <file version block>: string	id	ids	id	0	string	file version block	
1f	id of <fixlet>: integer	id	ids	id	0	integer	fixlet	
1f	id of <process>: integer	id	ids	id	0	integer	process	
1f	id of <root server>: integer	id	ids	id	0	integer	root server	
1f	id of <site group>: integer	id	ids	id	0	integer	site group	
10	id of <task action>: string	id	ids	id	0	string	task action	
10	id of <task network settings>: string	id	ids	id	0	string	task network settings	
10	id of <task principal>: string	id	ids	id	0	string	task principal	
10	id of <task trigger>: string	id	ids	id	0	string	task trigger	
1f	id of <user>: integer	id	ids	id	0	integer	user	
10	id of <winrt package>: winrt package id	id	ids	id	0	winrt package id	winrt package	
10	identifier of <metabase value>: metabase identifier	identifier	identifiers	identifier	0	metabase identifier	metabase value	
1f	identity of <execution>: string	identity	identites	identity	0	string	execution	
10	idle duration of <task idle settings>: time interval	idle duration	idle durations	idle duration	0	time interval	task idle settings	
10	idle priority: priority class	idle priority	idle priorities	idle priority	0	priority class		
10	idle setting of <task settings>: task idle settings	idle setting	idle settings	idle setting	0	task idle settings	task settings	
12	idle state: power state	idle state	idle states	idle state	0	power state		
10	idle task trigger type: task trigger type	idle task trigger type	idle task trigger types	idle task trigger type	0	task trigger type		
40	idp directory of <bes user>: bes idp directory	idp directory	idp directories	idp directory	0	bes idp directory	bes user	
2	ifref flag of <route>: boolean	ifref flag	ifref flags	ifref flag	0	boolean	route	
2	ifscope flag of <route>: boolean	ifscope flag	ifscope flags	ifscope flag	0	boolean	route	
10	ignore new instance of <task settings>: boolean	ignore new instance	ignore new instances	ignore new instance	0	boolean	task settings	
1f	image file of <process>: file	image file	image files	image file	0	file	process	
1f	image path of <application usage summary instance>: string	image path	image paths	image path	0	string	application usage summary instance	
1d	image path of <service>: string	image path	image paths	image path	0	string	service	
1f	in agent context: boolean	in agent context	in agent contexts	in agent context	0	boolean		
e0	in console context: boolean	in console context	in console contexts	in console context	0	boolean		
40	in explorer context: boolean	in explorer context	in explorer contexts	in explorer context	0	boolean		
1f	in plugin portal context: boolean	in plugin portal context	in plugin portal contexts	in plugin portal context	0	boolean		
1f	in proxy agent context: boolean	in proxy agent context	in proxy agent contexts	in proxy agent context	0	boolean		
e0	in web reports context: boolean	in web reports context	in web reports contexts	in web reports context	0	boolean		
1f	inactive <integer> of <dmi>: dmi inactive	inactive	inactives	inactive	0	dmi inactive	dmi	integer
1f	inactives of <dmi>: dmi inactive	inactive	inactives	inactives	1	dmi inactive	dmi	
10	inbound blocked firewall local policy modify state: firewall local policy modify state	inbound blocked firewall local policy modify state	inbound blocked firewall local policy modify states	inbound blocked firewall local policy modify state	0	firewall local policy modify state		
10	inbound connections allowed of <firewall profile>: boolean	inbound connections allowed	inbound connections alloweds	inbound connections allowed	0	boolean	firewall profile	
10	inbound of <firewall rule>: boolean	inbound	inbounds	inbound	0	boolean	firewall rule	
e0	include in relevance flag of <bes baseline component>: boolean	include in relevance flag	include in relevance flags	include in relevance flag	0	boolean	bes baseline component	
d	index of <grub image choice>: integer	index	indexes	index	0	integer	grub image choice	
d	index of <processor>: integer	index	indexes	index	0	integer	processor	
ff	index of <tuple item>: integer	index	indexes	index	0	integer	tuple item	
ff	index type of <property>: type	index type	index types	index type	0	type	property	
1f	indices of <sqlite table>: string	index	indices	indices	1	string	sqlite table	
ff	inexact of <floating point>: boolean	inexact	inexacts	inexact	0	boolean	floating point	
ff	infinite of <floating point>: boolean	infinite	infinites	infinite	0	boolean	floating point	
1f	info of <client>: string	info	infos	info	0	string	client	
2	info of <component>: string	info	infos	info	0	string	component	
10	information event log event type: event log event type	information event log event type	information event log event types	information event log event type	0	event log event type		
10	inherit attribute of <metabase value>: boolean	inherit attribute	inherit attributes	inherit attribute	0	boolean	metabase value	
10	inherit only of <access control entry>: boolean	inherit only	inherit onlys	inherit only	0	boolean	access control entry	
10	inheritance of <access control entry>: integer	inheritance	inheritances	inheritance	0	integer	access control entry	
10	inherited of <access control entry>: boolean	inherited	inheriteds	inherited	0	boolean	access control entry	
2	init date of <volume>: time	init date	init dates	init date	0	time	volume	
ff	initial part <time interval> of <time range>: time range	initial part	initial parts	initial part	0	time range	time range	time interval
d	initrd of <grub bootable image>: grub file location	initrd	initrds	initrd	0	grub file location	grub bootable image	
1f	input_current_probe_handle of <dmi system_power_supply>: integer	input_current_probe_handle	input_current_probe_handles	input_current_probe_handle	0	integer	dmi system_power_supply	
1f	input_voltage_probe_handle of <dmi system_power_supply>: integer	input_voltage_probe_handle	input_voltage_probe_handles	input_voltage_probe_handle	0	integer	dmi system_power_supply	
ff	ins <string> of <html>: html	ins	inss	ins	0	html	html	string
ff	ins <string> of <string>: html	ins	inss	ins	0	html	string	string
ff	ins of <html>: html	ins	inss	ins	0	html	html	
ff	ins of <string>: html	ins	inss	ins	0	html	string	
10	insert path attribute of <metabase value>: boolean	insert path attribute	insert path attributes	insert path attribute	0	boolean	metabase value	
10	inspectability of <application>: boolean	inspectability	inspectabilities	inspectability	0	boolean	application	
10	install folder <integer>: folder	install folder	install folders	install folder	0	folder		integer
10	install state of <winrt package user information>: winrt enumeration	install state	install states	install state	0	winrt enumeration	winrt package user information	
1f	installable_languages of <dmi bios_language_information>: integer	installable_languages	installable_languagess	installable_languages	0	integer	dmi bios_language_information	
4	installed <string> of <rpmdatabase>: boolean	installed	installeds	installed	0	boolean	rpmdatabase	string
4	installed files of <package>: capability	installed file	installed files	installed files	1	capability	package	
10	installed path of <winrt package>: folder	installed path	installed paths	installed path	0	folder	winrt package	
9	installed version of <debian base package>: debianpkg version	installed version	installed versions	installed version	0	debianpkg version	debian base package	
1f	installed_size of <dmi cache_information>: integer	installed_size	installed_sizes	installed_size	0	integer	dmi cache_information	
1f	installed_size of <dmi memory_module_information>: integer	installed_size	installed_sizes	installed_size	0	integer	dmi memory_module_information	
1f	instance data of <cloud provider>: instance data	instance data	instances data	instance data	0	instance data	cloud provider	
10	instance guid of <running task>: string	instance guid	instance guids	instance guid	0	string	running task	
10	instance name of <local mssql database>: string	instance name	instance names	instance name	0	string	local mssql database	
1f	instances of <application usage summary>: application usage summary instance	instance	instances	instances	1	application usage summary instance	application usage summary	
2	integer <integer> of <array>: integer	integer	integers	integer	0	integer	array	integer
ff	integer <integer>: integer	integer	integers	integer	0	integer		integer
2	integer <string> of <dictionary>: integer	integer	integers	integer	0	integer	dictionary	string
2	integer <string> of <preference>: integer	integer	integers	integer	0	integer	preference	string
ff	integer <string>: integer	integer	integers	integer	0	integer		string
ff	integer ceiling of <floating point>: integer	integer ceiling	integer ceilings	integer ceiling	0	integer	floating point	
ff	integer floor of <floating point>: integer	integer floor	integer floors	integer floor	0	integer	floating point	
2	integer of <osxvalue>: integer	integer	integers	integer	0	integer	osxvalue	
1f	integer of <sqlite column type>: boolean	integer	integers	integer	0	boolean	sqlite column type	
10	integer value <integer> of <wmi select>: integer	integer value	integer values	integer value	0	integer	wmi select	integer
1f	integer values <string> of <smbios structure>: smbios value	integer value	integer values	integer values	1	smbios value	smbios structure	string
10	integer values of <wmi select>: integer	integer value	integer values	integer values	1	integer	wmi select	
1f	integers <string> of <smbios structure>: integer	integer	integers	integers	1	integer	smbios structure	string
ff	integers in <( integer, integer )>: integer	integer in	integers in	integers in	1	integer		( integer, integer )
ff	integers in <( integer, integer, integer )>: integer	integer in	integers in	integers in	1	integer		( integer, integer, integer )
ff	integers to <integer>: integer	integer to	integers to	integers to	1	integer		integer
10	interactive group: security account	interactive group	interactive groups	interactive group	0	security account		
10	interactive token logon of <task principal>: boolean	interactive token logon	interactive token logons	interactive token logon	0	boolean	task principal	
10	interactive token password logon of <task principal>: boolean	interactive token password logon	interactive token password logons	interactive token password logon	0	boolean	task principal	
10	interdomain trust account flag of <user>: boolean	interdomain trust account flag	interdomain trust account flags	interdomain trust account flag	0	boolean	user	
1f	interface <integer> of <network>: network interface	interface	interfaces	interface	0	network interface	network	integer
1f	interface of <dmi built_in_pointing_device>: integer	interface	interfaces	interface	0	integer	dmi built_in_pointing_device	
f	interface of <route>: string	interface	interfaces	interface	0	string	route	
10	interface types string of <firewall rule>: string	interface types string	interface types strings	interface types string	0	string	firewall rule	
1f	interface_type of <dmi ipmi_device_information>: integer	interface_type	interface_types	interface_type	0	integer	dmi ipmi_device_information	
10	interfaces of <firewall rule>: string	interface	interfaces	interfaces	1	string	firewall rule	
2	interfaces of <network adapter>: network interface	interface	interfaces	interfaces	1	network interface	network adapter	
1f	interfaces of <network>: network interface	interface	interfaces	interfaces	1	network interface	network	
1f	interleave_position of <dmi memory_device_mapped_address>: integer	interleave_position	interleave_positions	interleave_position	0	integer	dmi memory_device_mapped_address	
1f	interleaved_data_depth of <dmi memory_device_mapped_address>: integer	interleaved_data_depth	interleaved_data_depths	interleaved_data_depth	0	integer	dmi memory_device_mapped_address	
10	internal port of <port mapping>: integer	internal port	internal ports	internal port	0	integer	port mapping	
1f	internal_connector_type of <dmi port_connector_information>: integer	internal_connector_type	internal_connector_types	internal_connector_type	0	integer	dmi port_connector_information	
1f	internal_reference_designator of <dmi port_connector_information>: string	internal_reference_designator	internal_reference_designators	internal_reference_designator	0	string	dmi port_connector_information	
10	internet connection firewall of <network adapter>: internet connection firewall	internet connection firewall	internet connection firewalls	internet connection firewall	0	internet connection firewall	network adapter	
2	internet plugins folder of <domain>: folder	internet plugins folder	internet plugins folders	internet plugins folder	0	folder	domain	
2	internet plugins folder: folder	internet plugins folder	internet plugins folders	internet plugins folder	0	folder		
10	internet protocol <integer>: internet protocol	internet protocol	internet protocols	internet protocol	0	internet protocol		integer
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
10	interval of <task repetition pattern>: time interval	interval	intervals	interval	0	time interval	task repetition pattern	
ff	invalid after of <x509 certificate>: time	invalid after	invalid afters	invalid after	0	time	x509 certificate	
ff	invalid before of <x509 certificate>: time	invalid before	invalid befores	invalid before	0	time	x509 certificate	
ff	invalid of <floating point>: boolean	invalid	invalids	invalid	0	boolean	floating point	
12	invalid state: power state	invalid state	invalid states	invalid state	0	power state		
10	io other count of <process>: integer	io other count	io other counts	io other count	0	integer	process	
10	io other size of <process>: integer	io other size	io other sizes	io other size	0	integer	process	
10	io read count of <process>: integer	io read count	io read counts	io read count	0	integer	process	
10	io read size of <process>: integer	io read size	io read sizes	io read size	0	integer	process	
10	io write count of <process>: integer	io write count	io write counts	io write count	0	integer	process	
10	io write size of <process>: integer	io write size	io write sizes	io write size	0	integer	process	
2	iokit registry: registryroot	iokit registry	iokit registries	iokit registry	0	registryroot		
1f	ip address of <selected server>: ipv4or6 address	ip address	ip addresses	ip address	0	ipv4or6 address	selected server	
e0	ip addresses of <bes computer>: ipv4or6 address	ip address	ip addresses	ip addresses	1	ipv4or6 address	bes computer	
2	ip family of <route>: string	ip family	ip families	ip family	0	string	route	
1f	ip interface <integer> of <network>: network ip interface	ip interface	ip interfaces	ip interface	0	network ip interface	network	integer
2	ip interfaces of <network adapter>: network ip interface	ip interface	ip interfaces	ip interfaces	1	network ip interface	network adapter	
1f	ip interfaces of <network>: network ip interface	ip interface	ip interfaces	ip interfaces	1	network ip interface	network	
ff	ip version <integer>: ip version	ip version	ip versions	ip version	0	ip version		integer
10	ip version of <firewall authorized application>: ip version	ip version	ip versions	ip version	0	ip version	firewall authorized application	
10	ip version of <firewall open port>: ip version	ip version	ip versions	ip version	0	ip version	firewall open port	
10	ip version of <firewall service>: ip version	ip version	ip versions	ip version	0	ip version	firewall service	
ff	ip version of <ipv4or6 address>: ip version	ip version	ip versions	ip version	0	ip version	ipv4or6 address	
1f	ipmi_device_information <integer> of <dmi>: dmi ipmi_device_information	ipmi_device_information	ipmi_device_informations	ipmi_device_information	0	dmi ipmi_device_information	dmi	integer
1f	ipmi_device_informations of <dmi>: dmi ipmi_device_information	ipmi_device_information	ipmi_device_informations	ipmi_device_informations	1	dmi ipmi_device_information	dmi	
1f	ipmi_specification_revision of <dmi ipmi_device_information>: integer	ipmi_specification_revision	ipmi_specification_revisions	ipmi_specification_revision	0	integer	dmi ipmi_device_information	
ff	ipv4 address <string>: ipv4 address	ipv4 address	ipv4 addresses	ipv4 address	0	ipv4 address		string
10	ipv4 interface <integer> of <network adapter>: network adapter interface	ipv4 interface	ipv4 interfaces	ipv4 interface	0	network adapter interface	network adapter	integer
10	ipv4 interface <integer> of <network>: network adapter interface	ipv4 interface	ipv4 interfaces	ipv4 interface	0	network adapter interface	network	integer
1f	ipv4 interfaces of <network adapter>: network adapter interface	ipv4 interface	ipv4 interfaces	ipv4 interfaces	1	network adapter interface	network adapter	
1f	ipv4 interfaces of <network>: network adapter interface	ipv4 interface	ipv4 interfaces	ipv4 interfaces	1	network adapter interface	network	
ff	ipv4 part of <ipv4or6 address>: ipv4 address	ipv4 part	ipv4 parts	ipv4 part	0	ipv4 address	ipv4or6 address	
ff	ipv4 part of <ipv6 address>: ipv4 address	ipv4 part	ipv4 parts	ipv4 part	0	ipv4 address	ipv6 address	
f	ipv4 routing table: routing table	ipv4 routing table	ipv4 routing tables	ipv4 routing table	0	routing table		
ff	ipv4: ip version	ipv4	ipv4s	ipv4	0	ip version		
ff	ipv4or6 address <string>: ipv4or6 address	ipv4or6 address	ipv4or6 addresses	ipv4or6 address	0	ipv4or6 address		string
10	ipv4or6 dns servers of <network adapter>: ipv4or6 address	ipv4or6 dns server	ipv4or6 dns servers	ipv4or6 dns servers	1	ipv4or6 address	network adapter	
10	ipv4or6 interface <integer> of <network adapter>: network adapter interface	ipv4or6 interface	ipv4or6 interfaces	ipv4or6 interface	0	network adapter interface	network adapter	integer
10	ipv4or6 interface <integer> of <network>: network adapter interface	ipv4or6 interface	ipv4or6 interfaces	ipv4or6 interface	0	network adapter interface	network	integer
1f	ipv4or6 interfaces of <network adapter>: network adapter interface	ipv4or6 interface	ipv4or6 interfaces	ipv4or6 interfaces	1	network adapter interface	network adapter	
1f	ipv4or6 interfaces of <network>: network adapter interface	ipv4or6 interface	ipv4or6 interfaces	ipv4or6 interfaces	1	network adapter interface	network	
ff	ipv6 address <string>: ipv6 address	ipv6 address	ipv6 addresses	ipv6 address	0	ipv6 address		string
10	ipv6 addresses of <network adapter>: ipv6 address	ipv6 address	ipv6 addresses	ipv6 addresses	1	ipv6 address	network adapter	
10	ipv6 dns servers of <network adapter>: ipv6 address	ipv6 dns server	ipv6 dns servers	ipv6 dns servers	1	ipv6 address	network adapter	
10	ipv6 interface <integer> of <network adapter>: network adapter interface	ipv6 interface	ipv6 interfaces	ipv6 interface	0	network adapter interface	network adapter	integer
10	ipv6 interface <integer> of <network>: network adapter interface	ipv6 interface	ipv6 interfaces	ipv6 interface	0	network adapter interface	network	integer
1f	ipv6 interfaces of <network adapter>: network adapter interface	ipv6 interface	ipv6 interfaces	ipv6 interfaces	1	network adapter interface	network adapter	
1f	ipv6 interfaces of <network>: network adapter interface	ipv6 interface	ipv6 interfaces	ipv6 interfaces	1	network adapter interface	network	
2	ipv6 routing table: routing table	ipv6 routing table	ipv6 routing tables	ipv6 routing table	0	routing table		
ff	ipv6: ip version	ipv6	ipv6s	ipv6	0	ip version		
d	irtt of <route>: integer	irtt	irtts	irtt	0	integer	route	
2	isochronous of <usb>: boolean	isochronous	isochronouses	isochronous	0	boolean	usb	
2	iss download folder of <domain>: folder	iss download folder	iss download folders	iss download folder	0	folder	domain	
2	iss download folder: folder	iss download folder	iss download folders	iss download folder	0	folder		
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
2	item <string> of <folder>: filesystem object	item	items	item	0	filesystem object	folder	string
2	item <string>: filesystem object	item	items	item	0	filesystem object		string
1f	item_handle of <dmi group_associations>: integer	item_handle	item_handles	item_handle	0	integer	dmi group_associations	
1f	item_type of <dmi group_associations>: integer	item_type	item_types	item_type	0	integer	dmi group_associations	
2	items ending in <string> of <folder>: filesystem object	item ending in	items ending in	items ending in	1	filesystem object	folder	string
2	items of <folder>: filesystem object	item	items	items	1	filesystem object	folder	
ff	january <integer> of <integer>: date	january	januarys	january	0	date	integer	integer
ff	january <integer>: day of year	january	januarys	january	0	day of year		integer
ff	january of <integer>: month and year	january	januarys	january	0	month and year	integer	
ff	january: month	january	januarys	january	0	month		
e0	javascript arrays <string> of <boolean>: html	javascript array	javascript arrays	javascript arrays	1	html	boolean	string
e0	javascript arrays <string> of <integer>: html	javascript array	javascript arrays	javascript arrays	1	html	integer	string
e0	javascript arrays <string> of <statistical bin>: html	javascript array	javascript arrays	javascript arrays	1	html	statistical bin	string
e0	javascript arrays <string> of <string>: html	javascript array	javascript arrays	javascript arrays	1	html	string	string
e0	join by intersection flag of <bes filter>: boolean	join by intersection flag	join by intersection flags	join by intersection flag	0	boolean	bes filter	
1f	json of <file>: json value	json	jsons	json	0	json value	file	
1f	json of <instance data>: json value	json	jsons	json	0	json value	instance data	
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
2	kernel extensions folder of <domain>: folder	kernel extensions folder	kernel extensions folders	kernel extensions folder	0	folder	domain	
2	kernel extensions folder: folder	kernel extensions folder	kernel extensions folders	kernel extensions folder	0	folder		
d	kernel of <grub bootable image>: grub kernel	kernel	kernels	kernel	0	grub kernel	grub bootable image	
10	kernel time of <process>: time interval	kernel time	kernel times	kernel time	0	time interval	process	
1f	key <string> of <file section>: string	key	keys	key	0	string	file section	string
1f	key <string> of <file>: string	key	keys	key	0	string	file	string
ff	key <string> of <json value>: json key	key	keys	key	0	json key	json value	string
10	key <string> of <metabase key>: metabase key	key	keys	key	0	metabase key	metabase key	string
10	key <string> of <metabase>: metabase key	key	keys	key	0	metabase key	metabase	string
14	key <string> of <plugin store>: plugin store key	key	keys	key	0	plugin store key	plugin store	string
10	key <string> of <registry key>: registry key	key	keys	key	0	registry key	registry key	string
10	key <string> of <registry>: registry key	key	keys	key	0	registry key	registry	string
1f	key <string> of <yaml value>: yaml key	key	keys	key	0	yaml key	yaml value	string
2	key of <dictionaryentry>: string	key	keys	key	0	string	dictionaryentry	
2	key of <user attribute>: string	key	keys	key	0	string	user attribute	
2	keyboard type: integer	keyboard type	keyboard types	keyboard type	0	integer		
2	keys of <dictionary>: string	key	keys	keys	1	string	dictionary	
1f	keys of <instance data>: json key	key	keys	keys	1	json key	instance data	
ff	keys of <json value>: json key	key	keys	keys	1	json key	json value	
10	keys of <metabase key>: metabase key	key	keys	keys	1	metabase key	metabase key	
10	keys of <metabase>: metabase key	key	keys	keys	1	metabase key	metabase	
14	keys of <plugin store>: plugin store key	key	keys	keys	1	plugin store key	plugin store	
10	keys of <registry key>: registry key	key	keys	keys	1	registry key	registry key	
1f	keys of <yaml value>: yaml key	key	keys	keys	1	yaml key	yaml value	
ff	khz: hertz	khz	khzs	khz	0	hertz		
e0	kurtosis of <statistical bin>: floating point	kurtosis	kurtoses	kurtosis	0	floating point	statistical bin	
1f	l1_cache_handle of <dmi processor_information>: integer	l1_cache_handle	l1_cache_handles	l1_cache_handle	0	integer	dmi processor_information	
1f	l2_cache_handle of <dmi processor_information>: integer	l2_cache_handle	l2_cache_handles	l2_cache_handle	0	integer	dmi processor_information	
1f	l3_cache_handle of <dmi processor_information>: integer	l3_cache_handle	l3_cache_handles	l3_cache_handle	0	integer	dmi processor_information	
10	language of <file version block>: string	language	languages	language	0	string	file version block	
5f	large integer <integer>: large integer	large integer	large integers	large integer	0	large integer		integer
5f	large integer <string>: large integer	large integer	large integers	large integer	0	large integer		string
ff	last <integer> of <binary_string>: binary_substring	last	lasts	last	0	binary_substring	binary_string	integer
ff	last <integer> of <string>: substring	last	lasts	last	0	substring	string	integer
ff	last <string> of <string>: substring	last	lasts	last	0	substring	string	string
1f	last ack of <tcp state>: boolean	last ack	last acks	last ack	0	boolean	tcp state	
1f	last active line number of <action>: integer	last active line number	last active line numbers	last active line number	0	integer	action	
1f	last active time of <action>: time	last active time	last active times	last active time	0	time	action	
e0	last became nonrelevant of <bes fixlet result>: time	last became nonrelevant	last became nonrelevants	last became nonrelevant	0	time	bes fixlet result	
e0	last became relevant of <bes fixlet result>: time	last became relevant	last became relevants	last became relevant	0	time	bes fixlet result	
1f	last change time of <action>: time	last change time	last change times	last change time	0	time	action	
bd	last child of <xml dom node>: xml dom node	last child	last children	last child	0	xml dom node	xml dom node	
1f	last command time of <client>: time	last command time	last command times	last command time	0	time	client	
1f	last gather time of <site>: time	last gather time	last gather times	last gather time	0	time	site	
1f	last line of <file>: file line	last line	last lines	last line	0	file line	file	
1f	last lines <integer> of <file>: file line	last line	last lines	last lines	1	file line	file	integer
e0	last login time of <bes user>: time	last login time	last login times	last login time	0	time	bes user	
10	last logoff of <user>: time	last logoff	last logoffs	last logoff	0	time	user	
10	last logon of <user>: time	last logon	last logons	last logon	0	time	user	
10	last logon time of <logged on user>: time	last logon time	last logon times	last logon time	0	time	logged on user	
10	last logon type number of <logged on user>: integer	last logon type number	last logon type numbers	last logon type number	0	integer	logged on user	
10	last logon type of <logged on user>: string	last logon type	last logon types	last logon type	0	string	logged on user	
12	last monitor interval in <power state> of <power history>: monitor power interval	last monitor interval in	last monitor intervals in	last monitor interval in	0	monitor power interval	power history	power state
12	last monitor interval in monitor off state of <power history>: monitor power interval	last monitor interval in monitor off state	last monitor intervals in monitor off state	last monitor interval in monitor off state	0	monitor power interval	power history	
12	last monitor interval in monitor on state of <power history>: monitor power interval	last monitor interval in monitor on state	last monitor intervals in monitor on state	last monitor interval in monitor on state	0	monitor power interval	power history	
1f	last rawline of <file>: file line	last rawline	last rawlines	last rawline	0	file line	file	
1f	last rawlines <integer> of <file>: file line	last rawline	last rawlines	last rawlines	1	file line	file	integer
e0	last refresh time of <bes computer group>: time	last refresh time	last refresh times	last refresh time	0	time	bes computer group	
1f	last relay select time: time	last relay select time	last relay select times	last relay select time	0	time		
e0	last report time of <bes computer>: time	last report time	last report times	last report time	0	time	bes computer	
1f	last report time of <client>: time	last report time	last report times	last report time	0	time	client	
10	last run time of <scheduled task>: time	last run time	last run times	last run time	0	time	scheduled task	
1f	last start time of <application usage summary instance>: time	last start time	last start times	last start time	0	time	application usage summary instance	
1f	last start time of <application usage summary>: time	last start time	last start times	last start time	0	time	application usage summary	
12	last system interval in <power state> of <power history>: system power interval	last system interval in	last system intervals in	last system interval in	0	system power interval	power history	power state
12	last system interval in active state of <power history>: system power interval	last system interval in active state	last system intervals in active state	last system interval in active state	0	system power interval	power history	
12	last system interval in idle state of <power history>: system power interval	last system interval in idle state	last system intervals in idle state	last system interval in idle state	0	system power interval	power history	
12	last system interval in logged off state of <power history>: system power interval	last system interval in logged off state	last system intervals in logged off state	last system interval in logged off state	0	system power interval	power history	
12	last system interval in off state of <power history>: system power interval	last system interval in off state	last system intervals in off state	last system interval in off state	0	system power interval	power history	
12	last system interval in standby state of <power history>: system power interval	last system interval in standby state	last system intervals in standby state	last system interval in standby state	0	system power interval	power history	
10	last task result of <scheduled task>: integer	last task result	last task results	last task result	0	integer	scheduled task	
1f	last time of <analysis>: time	last time	last times	last time	0	time	analysis	
1f	last time seen of <application usage summary instance>: time	last time seen	last times seen	last time seen	0	time	application usage summary instance	
1f	last time seen of <application usage summary>: time	last time seen	last times seen	last time seen	0	time	application usage summary	
10	last write time of <registry key>: time	last write time	last write times	last write time	0	time	registry key	
e0	ldap directory of <bes user>: bes ldap directory	ldap directory	ldap directories	ldap directory	0	bes ldap directory	bes user	
ff	leap of <year>: boolean	leap	leaps	leap	0	boolean	year	
10	lease expires of <network adapter>: time	lease expires	leases expire	lease expires	0	time	network adapter	
10	lease obtained of <network adapter>: time	lease obtained	leases obtained	lease obtained	0	time	network adapter	
ff	least hz: hertz	least hz	least hzs	least hz	0	hertz		
ff	least integer: integer	least integer	least integers	least integer	0	integer		
5f	least large integer: large integer	least large integer	least large integers	least large integer	0	large integer		
ff	least significant one bit of <bit set>: integer	least significant one bit	least significant one bits	least significant one bit	0	integer	bit set	
ff	least time interval: time interval	least time interval	least time intervals	least time interval	0	time interval		
5f	least uinteger: uinteger	least uinteger	least uintegers	least uinteger	0	uinteger		
ff	left operand type of <binary operator>: type	left operand type	left operand types	left operand type	0	type	binary operator	
ff	left shift <integer> of <bit set>: bit set	left shift	left shifts	left shift	0	bit set	bit set	integer
ff	legacy of <bes product>: boolean	legacy	legacies	legacy	0	boolean	bes product	
ff	length of <binary_string>: integer	length	lengths	length	0	integer	binary_string	
2	length of <datafork>: integer	length	lengths	length	0	integer	datafork	
1f	length of <dmi additional_information>: integer	length	lengths	length	0	integer	dmi additional_information	
1f	length of <dmi b32_bit_memory_error_information>: integer	length	lengths	length	0	integer	dmi b32_bit_memory_error_information	
1f	length of <dmi b64_bit_memory_error_information>: integer	length	lengths	length	0	integer	dmi b64_bit_memory_error_information	
1f	length of <dmi base_board_information>: integer	length	lengths	length	0	integer	dmi base_board_information	
1f	length of <dmi bios_information>: integer	length	lengths	length	0	integer	dmi bios_information	
1f	length of <dmi bios_language_information>: integer	length	lengths	length	0	integer	dmi bios_language_information	
1f	length of <dmi built_in_pointing_device>: integer	length	lengths	length	0	integer	dmi built_in_pointing_device	
1f	length of <dmi cache_information>: integer	length	lengths	length	0	integer	dmi cache_information	
1f	length of <dmi cooling_device>: integer	length	lengths	length	0	integer	dmi cooling_device	
1f	length of <dmi electrical_current_probe>: integer	length	lengths	length	0	integer	dmi electrical_current_probe	
1f	length of <dmi end_of_table>: integer	length	lengths	length	0	integer	dmi end_of_table	
1f	length of <dmi group_associations>: integer	length	lengths	length	0	integer	dmi group_associations	
1f	length of <dmi hardware_security>: integer	length	lengths	length	0	integer	dmi hardware_security	
1f	length of <dmi inactive>: integer	length	lengths	length	0	integer	dmi inactive	
1f	length of <dmi ipmi_device_information>: integer	length	lengths	length	0	integer	dmi ipmi_device_information	
1f	length of <dmi management_device>: integer	length	lengths	length	0	integer	dmi management_device	
1f	length of <dmi management_device_component>: integer	length	lengths	length	0	integer	dmi management_device_component	
1f	length of <dmi management_device_threshold_data>: integer	length	lengths	length	0	integer	dmi management_device_threshold_data	
1f	length of <dmi memory_array_mapped_address>: integer	length	lengths	length	0	integer	dmi memory_array_mapped_address	
1f	length of <dmi memory_channel>: integer	length	lengths	length	0	integer	dmi memory_channel	
1f	length of <dmi memory_controller_information>: integer	length	lengths	length	0	integer	dmi memory_controller_information	
1f	length of <dmi memory_device>: integer	length	lengths	length	0	integer	dmi memory_device	
1f	length of <dmi memory_device_mapped_address>: integer	length	lengths	length	0	integer	dmi memory_device_mapped_address	
1f	length of <dmi memory_module_information>: integer	length	lengths	length	0	integer	dmi memory_module_information	
1f	length of <dmi on_board_devices_information>: integer	length	lengths	length	0	integer	dmi on_board_devices_information	
1f	length of <dmi onboard_devices_extended_information>: integer	length	lengths	length	0	integer	dmi onboard_devices_extended_information	
1f	length of <dmi out_of_band_remote_access>: integer	length	lengths	length	0	integer	dmi out_of_band_remote_access	
1f	length of <dmi physical_memory_array>: integer	length	lengths	length	0	integer	dmi physical_memory_array	
1f	length of <dmi port_connector_information>: integer	length	lengths	length	0	integer	dmi port_connector_information	
1f	length of <dmi portable_battery>: integer	length	lengths	length	0	integer	dmi portable_battery	
1f	length of <dmi processor_information>: integer	length	lengths	length	0	integer	dmi processor_information	
1f	length of <dmi system_boot_information>: integer	length	lengths	length	0	integer	dmi system_boot_information	
1f	length of <dmi system_enclosure_or_chassis>: integer	length	lengths	length	0	integer	dmi system_enclosure_or_chassis	
1f	length of <dmi system_information>: integer	length	lengths	length	0	integer	dmi system_information	
1f	length of <dmi system_power_controls>: integer	length	lengths	length	0	integer	dmi system_power_controls	
1f	length of <dmi system_power_supply>: integer	length	lengths	length	0	integer	dmi system_power_supply	
1f	length of <dmi system_reset>: integer	length	lengths	length	0	integer	dmi system_reset	
1f	length of <dmi system_slots>: integer	length	lengths	length	0	integer	dmi system_slots	
1f	length of <dmi temperature_probe>: integer	length	lengths	length	0	integer	dmi temperature_probe	
1f	length of <dmi voltage_probe>: integer	length	lengths	length	0	integer	dmi voltage_probe	
10	length of <event log record>: integer	length	lengths	length	0	integer	event log record	
2	length of <file>: integer	length	lengths	length	0	integer	file	
ff	length of <month and year>: time interval	length	lengths	length	0	time interval	month and year	
2	length of <resfork>: integer	length	lengths	length	0	integer	resfork	
ff	length of <rope>: integer	length	lengths	length	0	integer	rope	
1f	length of <smbios structure>: integer	length	lengths	length	0	integer	smbios structure	
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
1f	line <integer> of <file>: file line	line	lines	line	0	file line	file	integer
e0	line number of <bes action result>: integer	line number	line numbers	line number	0	integer	bes action result	
1f	line number of <file line>: integer	line number	line numbers	line number	0	integer	file line	
e0	linear fit of <statistical bin>: linear projection	linear fit	linear fits	linear fit	0	linear projection	statistical bin	
1f	lines containing <string> of <file>: file line	line containing	lines containing	lines containing	1	file line	file	string
1f	lines of <file>: file line	line	lines	lines	1	file line	file	
1f	lines starting with <string> of <file>: file line	line starting with	lines starting with	lines starting with	1	file line	file	string
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
d	link count of <filesystem object>: integer	link count	link counts	link count	0	integer	filesystem object	
d	link count of <symlink>: integer	link count	link counts	link count	0	integer	symlink	
e0	link href of <bes action>: string	link href	link hrefs	link href	0	string	bes action	
e0	link href of <bes computer>: string	link href	link hrefs	link href	0	string	bes computer	
e0	link href of <bes domain>: string	link href	link hrefs	link href	0	string	bes domain	
e0	link href of <bes fixlet>: string	link href	link hrefs	link href	0	string	bes fixlet	
e0	link href of <bes unmanagedasset>: string	link href	link hrefs	link href	0	string	bes unmanagedasset	
e0	link href of <bes user>: string	link href	link hrefs	link href	0	string	bes user	
e0	link href of <bes wizard>: string	link href	link hrefs	link href	0	string	bes wizard	
2	link interface <integer> of <network>: network link interface	link interface	link interfaces	link interface	0	network link interface	network	integer
2	link interfaces of <network adapter>: network link interface	link interface	link interfaces	link interfaces	1	network link interface	network adapter	
2	link interfaces of <network>: network link interface	link interface	link interfaces	link interfaces	1	network link interface	network	
e0	link of <bes action>: html	link	links	link	0	html	bes action	
e0	link of <bes computer>: html	link	links	link	0	html	bes computer	
e0	link of <bes domain>: html	link	links	link	0	html	bes domain	
e0	link of <bes fixlet>: html	link	links	link	0	html	bes fixlet	
e0	link of <bes unmanagedasset>: html	link	links	link	0	html	bes unmanagedasset	
e0	link of <bes user>: html	link	links	link	0	html	bes user	
e0	link of <bes wizard>: html	link	links	link	0	html	bes wizard	
ff	link of <html>: html	link	links	link	0	html	html	
ff	link of <string>: html	link	links	link	0	html	string	
10	link speed of <network adapter>: integer	link speed	link speeds	link speed	0	integer	network adapter	
1f	linux of <operating system>: boolean	linux	linuxes	linux	0	boolean	operating system	
10	list permission of <access control entry>: boolean	list permission	list permissions	list permission	0	boolean	access control entry	
1f	listening of <tcp state>: boolean	listening	listenings	listening	0	boolean	tcp state	
1f	little endian of <operating system>: boolean	little endian	little endians	little endian	0	boolean	operating system	
2	llinfo flag of <route>: boolean	llinfo flag	llinfo flags	llinfo flag	0	boolean	route	
1f	local address of <socket>: ipv4or6 address	local address	local addresses	local address	0	ipv4or6 address	socket	
10	local addresses string of <firewall rule>: string	local addresses string	local addresses strings	local addresses string	0	string	firewall rule	
10	local administrator: boolean	local administrator	local administrators	local administrator	0	boolean		
1f	local character set of <client>: string	local character set	local character sets	local character set	0	string	client	
12	local computer of <active directory server>: active directory local computer	local computer	local computers	local computer	0	active directory local computer	active directory server	
2	local dictionary of <bundle>: dictionary	local dictionary	local dictionaries	local dictionary	0	dictionary	bundle	
2	local domain: domain	local domain	local domains	local domain	0	domain		
ff	local encoding concatenations <string> of <string>: string	local encoding concatenation	local encoding concatenations	local encoding concatenations	1	string	string	string
ff	local encoding concatenations of <string>: string	local encoding concatenation	local encoding concatenations	local encoding concatenations	1	string	string	
2	local flag of <route>: boolean	local flag	local flags	local flag	0	boolean	route	
12	local group <string> of <active directory server>: active directory group	local group	local groups	local group	0	active directory group	active directory server	string
10	local group <string>: local group	local group	local groups	local group	0	local group		string
10	local groups: local group	local group	local groups	local groups	1	local group		
10	local mssql database <string>: local mssql database	local mssql database	local mssql databases	local mssql database	0	local mssql database		string
10	local mssql databases: local mssql database	local mssql database	local mssql databases	local mssql databases	1	local mssql database		
2	local os log store: os log store	local os log store	local os log stores	local os log store	0	os log store		
10	local policy modify state of <firewall>: firewall local policy modify state	local policy modify state	local policy modify states	local policy modify state	0	firewall local policy modify state	firewall	
10	local policy of <firewall>: firewall policy	local policy	local policies	local policy	0	firewall policy	firewall	
1f	local port of <socket>: integer	local port	local ports	local port	0	integer	socket	
10	local ports string of <firewall rule>: string	local ports string	local ports strings	local ports string	0	string	firewall rule	
10	local service group: security account	local service group	local service groups	local service group	0	security account		
10	local subnet firewall scope: firewall scope	local subnet firewall scope	local subnet firewall scopes	local subnet firewall scope	0	firewall scope		
ff	local time <string>: time	local time	local times	local time	0	time		string
ff	local time zone: time zone	local time zone	local time zones	local time zone	0	time zone		
12	local user <string> of <active directory server>: active directory local user	local user	local users	local user	0	active directory local user	active directory server	string
12	local user <string>: user	local user	local users	local user	0	user		string
d	local users <string>: user	local user	local users	local users	1	user		string
12	local users of <active directory server>: active directory local user	local user	local users	local users	1	active directory local user	active directory server	
1f	local users: user	local user	local users	local users	1	user		
2	locales folder of <domain>: folder	locales folder	locales folders	locales folder	0	folder	domain	
2	locales folder: folder	locales folder	locales folders	locales folder	0	folder		
e0	locally visible flag of <bes fixlet>: boolean	locally visible flag	locally visible flags	locally visible flag	0	boolean	bes fixlet	
10	location information of <active device>: string	location information	location informations	location information	0	string	active device	
2	location manager modules folder of <domain>: folder	location manager modules folder	location manager modules folders	location manager modules folder	0	folder	domain	
2	location manager modules folder: folder	location manager modules folder	location manager modules folders	location manager modules folder	0	folder		
2	location manager preferences folder of <domain>: folder	location manager preferences folder	location manager preferences folders	location manager preferences folder	0	folder	domain	
2	location manager preferences folder: folder	location manager preferences folder	location manager preferences folders	location manager preferences folder	0	folder		
1f	location of <dmi physical_memory_array>: integer	location	locations	location	0	integer	dmi physical_memory_array	
1f	location of <dmi portable_battery>: string	location	locations	location	0	string	dmi portable_battery	
1f	location of <dmi system_power_supply>: string	location	locations	location	0	string	dmi system_power_supply	
2	location of <filesystem object>: folder	location	locations	location	0	folder	filesystem object	
1d	location of <filesystem object>: string	location	locations	location	0	string	filesystem object	
d	location of <grub kernel>: grub file location	location	locations	location	0	grub file location	grub kernel	
d	location of <symlink>: string	location	locations	location	0	string	symlink	
1f	location_and_status of <dmi electrical_current_probe>: integer	location_and_status	location_and_statuss	location_and_status	0	integer	dmi electrical_current_probe	
1f	location_and_status of <dmi temperature_probe>: integer	location_and_status	location_and_statuss	location_and_status	0	integer	dmi temperature_probe	
1f	location_and_status of <dmi voltage_probe>: integer	location_and_status	location_and_statuss	location_and_status	0	integer	dmi voltage_probe	
1f	location_in_chassis of <dmi base_board_information>: string	location_in_chassis	location_in_chassiss	location_in_chassis	0	string	dmi base_board_information	
2	locations folder of <domain>: folder	locations folder	locations folders	locations folder	0	folder	domain	
2	locations folder: folder	locations folder	locations folders	locations folder	0	folder		
1f	lock string of <action lock state>: string	lock string	lock strings	lock string	0	string	action lock state	
1f	locked content of <file>: file content	locked content	locked contents	locked content	0	file content	file	
e0	locked flag of <bes computer>: boolean	locked flag	locked flags	locked flag	0	boolean	bes computer	
1f	locked key <string> of <file>: string	locked key	locked keys	locked key	0	string	file	string
1f	locked line <integer> of <file>: file line	locked line	locked lines	locked line	0	file line	file	integer
1f	locked lines containing <string> of <file>: file line	locked line containing	locked lines containing	locked lines containing	1	file line	file	string
1f	locked lines of <file>: file line	locked line	locked lines	locked lines	1	file line	file	
1f	locked lines starting with <string> of <file>: file line	locked line starting with	locked lines starting with	locked lines starting with	1	file line	file	string
1f	locked of <action lock state>: boolean	locked	lockeds	locked	0	boolean	action lock state	
2	locked of <file>: boolean	locked	lockeds	locked	0	boolean	file	
10	locked out flag of <user>: boolean	locked out flag	locked out flags	locked out flag	0	boolean	user	
1f	locked rawline <integer> of <file>: file line	locked rawline	locked rawlines	locked rawline	0	file line	file	integer
1f	locked rawlines containing <string> of <file>: file line	locked rawline containing	locked rawlines containing	locked rawlines containing	1	file line	file	string
1f	locked rawlines of <file>: file line	locked rawline	locked rawlines	locked rawlines	1	file line	file	
1f	locked rawlines starting with <string> of <file>: file line	locked rawline starting with	locked rawlines starting with	locked rawlines starting with	1	file line	file	string
1f	locked section <string> of <file>: file section	locked section	locked sections	locked section	0	file section	file	string
2	log level of <os log entry log>: string	log level	log levels	log level	0	string	os log entry log	
e0	logarithm kurtosis of <statistical bin>: floating point	logarithm kurtosis	logarithm kurtoses	logarithm kurtosis	0	floating point	statistical bin	
e0	logarithm skewness of <statistical bin>: floating point	logarithm skewness	logarithm skewnesses	logarithm skewness	0	floating point	statistical bin	
e0	logarithm standard deviation of <statistical bin>: floating point	logarithm standard deviation	logarithm standard deviations	logarithm standard deviation	0	floating point	statistical bin	
e0	logarithm variance of <statistical bin>: floating point	logarithm variance	logarithm variances	logarithm variance	0	floating point	statistical bin	
12	logged off state: power state	logged off state	logged off states	logged off state	0	power state		
12	logged on group <string> of <active directory server>: active directory group	logged on group	logged on groups	logged on group	0	active directory group	active directory server	string
12	logged on user <string> of <active directory server>: active directory local user	logged on user	logged on users	logged on user	0	active directory local user	active directory server	string
12	logged on user of <user>: logged on user	logged on user	logged on users	logged on user	0	logged on user	user	
12	logged on users of <active directory server>: active directory local user	logged on user	logged on users	logged on users	1	active directory local user	active directory server	
1f	logged on users: logged on user	logged on user	logged on users	logged on users	1	logged on user		
10	logical processor count: integer	logical processor count	logical processor counts	logical processor count	0	integer		
2	logical ram: integer	logical ram	logical rams	logical ram	0	integer		
10	login account of <service>: string	login account	login accounts	login account	0	string	service	
10	login mode of <local mssql database>: integer	login mode	login modes	login mode	0	integer	local mssql database	
40	login user of <bes idp directory>: string	login user	login users	login user	0	string	bes idp directory	
e0	login user of <bes ldap directory>: string	login user	login users	login user	0	string	bes ldap directory	
d	loginuid of <process>: integer	loginuid	loginuids	loginuid	0	integer	process	
10	logon completion time of <logged on user>: time interval	logon completion time	logon completion times	logon completion time	0	time interval	logged on user	
10	logon count of <user>: integer	logon count	logon counts	logon count	0	integer	user	
10	logon logoff category of <audit policy>: audit policy category	logon logoff category	logon logoff categories	logon logoff category	0	audit policy category	audit policy	
10	logon script of <user>: string	logon script	logon scripts	logon script	0	string	user	
10	logon server of <user>: string	logon server	logon servers	logon server	0	string	user	
10	logon session time of <logged on user>: time	logon session time	logon session times	logon session time	0	time	logged on user	
10	logon session type number of <logged on user>: integer	logon session type number	logon session type numbers	logon session type number	0	integer	logged on user	
10	logon session type of <logged on user>: string	logon session type	logon session types	logon session type	0	string	logged on user	
10	logon task trigger type: task trigger type	logon task trigger type	logon task trigger types	logon task trigger type	0	task trigger type		
4	long form of <short rpm package version record>: rpm package version record	long form	long forms	long form	0	rpm package version record	short rpm package version record	
2	long name of <client process owner>: string	long name	long names	long name	0	string	client process owner	
1f	loopback of <network adapter interface>: boolean	loopback	loopbacks	loopback	0	boolean	network adapter interface	
1f	loopback of <network adapter>: boolean	loopback	loopbacks	loopback	0	boolean	network adapter	
1f	loopback of <network ip interface>: boolean	loopback	loopbacks	loopback	0	boolean	network ip interface	
1f	low of <power level>: boolean	low	lows	low	0	boolean	power level	
ff	lower bound of <integer range>: integer	lower bound	lower bounds	lower bound	0	integer	integer range	
1f	lower_threshold_critical of <dmi management_device_threshold_data>: integer	lower_threshold_critical	lower_threshold_criticals	lower_threshold_critical	0	integer	dmi management_device_threshold_data	
1f	lower_threshold_non_critical of <dmi management_device_threshold_data>: integer	lower_threshold_non_critical	lower_threshold_non_criticals	lower_threshold_non_critical	0	integer	dmi management_device_threshold_data	
1f	lower_threshold_non_recoverable of <dmi management_device_threshold_data>: integer	lower_threshold_non_recoverable	lower_threshold_non_recoverables	lower_threshold_non_recoverable	0	integer	dmi management_device_threshold_data	
10	lua runlevel of <task principal>: boolean	lua runlevel	lua runlevels	lua runlevel	0	boolean	task principal	
1f	mac address of <network adapter interface>: string	mac address	mac addresses	mac address	0	string	network adapter interface	
1f	mac address of <network adapter>: string	mac address	mac addresses	mac address	0	string	network adapter	
f	mac address of <network ip interface>: string	mac address	mac addresses	mac address	0	string	network ip interface	
2	mac address of <network link interface>: string	mac address	mac addresses	mac address	0	string	network link interface	
1f	mac of <operating system>: boolean	mac	macs	mac	0	boolean	operating system	
2	machine name: string	machine name	machine names	machine name	0	string		
1f	machine of <operating system>: string	machine	machines	machine	0	string	operating system	
2	machine type: integer	machine type	machine types	machine type	0	integer		
2	macos read me folder of <domain>: folder	macos read me folder	macos read me folders	macos read me folder	0	folder	domain	
2	macos read me folder: folder	macos read me folder	macos read me folders	macos read me folder	0	folder		
2	main gather service: nothing	main gather service	main gather services	main gather service	0	nothing		
1d	main gather service: service	main gather service	main gather services	main gather service	0	service		
1f	main processor: processor	main processor	main processors	main processor	0	processor		
d	major of <device file>: integer	major	majors	major	0	integer	device file	
ff	major revision of <version>: integer	major revision	major revisions	major revision	0	integer	version	
1f	major version of <operating system>: integer	major version	major versions	major version	0	integer	operating system	
2	maker of <component>: string	maker	makers	maker	0	string	component	
e0	management extensions of <bes computer>: bes computer	management extension	management extensions	management extensions	1	bes computer	bes computer	
e0	management rights flag of <bes action>: boolean	management rights flag	management rights flags	management rights flag	0	boolean	bes action	
1f	management_device <integer> of <dmi>: dmi management_device	management_device	management_devices	management_device	0	dmi management_device	dmi	integer
1f	management_device_component <integer> of <dmi>: dmi management_device_component	management_device_component	management_device_components	management_device_component	0	dmi management_device_component	dmi	integer
1f	management_device_components of <dmi>: dmi management_device_component	management_device_component	management_device_components	management_device_components	1	dmi management_device_component	dmi	
1f	management_device_handle of <dmi management_device_component>: integer	management_device_handle	management_device_handles	management_device_handle	0	integer	dmi management_device_component	
1f	management_device_threshold_data <integer> of <dmi>: dmi management_device_threshold_data	management_device_threshold_data	management_device_threshold_datas	management_device_threshold_data	0	dmi management_device_threshold_data	dmi	integer
1f	management_device_threshold_datas of <dmi>: dmi management_device_threshold_data	management_device_threshold_data	management_device_threshold_datas	management_device_threshold_datas	1	dmi management_device_threshold_data	dmi	
1f	management_devices of <dmi>: dmi management_device	management_device	management_devices	management_devices	1	dmi management_device	dmi	
e0	manual flag of <bes computer group>: boolean	manual flag	manual flags	manual flag	0	boolean	bes computer group	
1f	manual group <string> of <client>: manual group	manual group	manual groups	manual group	0	manual group	client	string
1f	manual groups of <client>: manual group	manual group	manual groups	manual groups	1	manual group	client	
1f	manufacture_date of <dmi portable_battery>: string	manufacture_date	manufacture_dates	manufacture_date	0	string	dmi portable_battery	
10	manufacturer of <active device>: string	manufacturer	manufacturers	manufacturer	0	string	active device	
1f	manufacturer of <dmi base_board_information>: string	manufacturer	manufacturers	manufacturer	0	string	dmi base_board_information	
1f	manufacturer of <dmi memory_device>: string	manufacturer	manufacturers	manufacturer	0	string	dmi memory_device	
1f	manufacturer of <dmi portable_battery>: string	manufacturer	manufacturers	manufacturer	0	string	dmi portable_battery	
1f	manufacturer of <dmi system_enclosure_or_chassis>: string	manufacturer	manufacturers	manufacturer	0	string	dmi system_enclosure_or_chassis	
1f	manufacturer of <dmi system_information>: string	manufacturer	manufacturers	manufacturer	0	string	dmi system_information	
1f	manufacturer of <dmi system_power_supply>: string	manufacturer	manufacturers	manufacturer	0	string	dmi system_power_supply	
1f	manufacturer_name of <dmi out_of_band_remote_access>: string	manufacturer_name	manufacturer_names	manufacturer_name	0	string	dmi out_of_band_remote_access	
ff	march <integer> of <integer>: date	march	marchs	march	0	date	integer	integer
ff	march <integer>: day of year	march	marchs	march	0	day of year		integer
ff	march of <integer>: month and year	march	marchs	march	0	month and year	integer	
ff	march: month	march	marchs	march	0	month		
f	mask of <route>: ipv4or6 address	mask	masks	mask	0	ipv4or6 address	route	
e0	master flag of <bes role>: boolean	master flag	master flags	master flag	0	boolean	bes role	
e0	master flag of <bes user>: boolean	master flag	master flags	master flag	0	boolean	bes user	
e0	master site flag of <bes fixlet>: boolean	master site flag	master site flags	master site flag	0	boolean	bes fixlet	
e0	master site flag of <bes site>: boolean	master site flag	master site flags	master site flag	0	boolean	bes site	
1f	masthead of <site>: file	masthead	mastheads	masthead	0	file	site	
e0	masthead operator name of <bes user>: string	masthead operator name	masthead operator names	masthead operator name	0	string	bes user	
ff	matches <regular expression> of <string>: regular expression match	match	matches	matches	1	regular expression match	string	regular expression
1f	max_power_capacity of <dmi system_power_supply>: integer	max_power_capacity	max_power_capacitys	max_power_capacity	0	integer	dmi system_power_supply	
1f	max_speed of <dmi processor_information>: integer	max_speed	max_speeds	max_speed	0	integer	dmi processor_information	
ff	maxima of <date>: date	maximum	maxima	maxima	1	date	date	
ff	maxima of <day of month>: day of month	maximum	maxima	maxima	1	day of month	day of month	
ff	maxima of <day of year>: day of year	maximum	maxima	maxima	1	day of year	day of year	
9	maxima of <debian package upstream version>: debian package upstream version	maximum	maxima	maxima	1	debian package upstream version	debian package upstream version	
9	maxima of <debian package version epoch>: debian package version epoch	maximum	maxima	maxima	1	debian package version epoch	debian package version epoch	
9	maxima of <debian package version revision>: debian package version revision	maximum	maxima	maxima	1	debian package version revision	debian package version revision	
9	maxima of <debian package version>: debian package version	maximum	maxima	maxima	1	debian package version	debian package version	
ff	maxima of <floating point>: floating point	maximum	maxima	maxima	1	floating point	floating point	
ff	maxima of <hertz>: hertz	maximum	maxima	maxima	1	hertz	hertz	
ff	maxima of <integer>: integer	maximum	maxima	maxima	1	integer	integer	
ff	maxima of <ipv4 address>: ipv4 address	maximum	maxima	maxima	1	ipv4 address	ipv4 address	
ff	maxima of <ipv4or6 address>: ipv4or6 address	maximum	maxima	maxima	1	ipv4or6 address	ipv4or6 address	
ff	maxima of <ipv6 address>: ipv6 address	maximum	maxima	maxima	1	ipv6 address	ipv6 address	
5f	maxima of <large integer>: large integer	maximum	maxima	maxima	1	large integer	large integer	
ff	maxima of <month and year>: month and year	maximum	maxima	maxima	1	month and year	month and year	
ff	maxima of <month>: month	maximum	maxima	maxima	1	month	month	
ff	maxima of <number of months>: number of months	maximum	maxima	maxima	1	number of months	number of months	
e2	maxima of <rate>: rate	maximum	maxima	maxima	1	rate	rate	
4	maxima of <rpm package release>: rpm package release	maximum	maxima	maxima	1	rpm package release	rpm package release	
4	maxima of <rpm package version record>: rpm package version record	maximum	maxima	maxima	1	rpm package version record	rpm package version record	
4	maxima of <rpm package version>: rpm package version	maximum	maxima	maxima	1	rpm package version	rpm package version	
4	maxima of <short rpm package version record>: short rpm package version record	maximum	maxima	maxima	1	short rpm package version record	short rpm package version record	
ff	maxima of <site version list>: site version list	maximum	maxima	maxima	1	site version list	site version list	
ff	maxima of <time interval>: time interval	maximum	maxima	maxima	1	time interval	time interval	
ff	maxima of <time of day>: time of day	maximum	maxima	maxima	1	time of day	time of day	
ff	maxima of <time>: time	maximum	maxima	maxima	1	time	time	
5f	maxima of <uinteger>: uinteger	maximum	maxima	maxima	1	uinteger	uinteger	
1f	maxima of <uuid>: uuid	maximum	maxima	maxima	1	uuid	uuid	
ff	maxima of <version>: version	maximum	maxima	maxima	1	version	version	
ff	maxima of <year>: year	maximum	maxima	maxima	1	year	year	
10	maximum allowed permission of <access control entry>: boolean	maximum allowed permission	maximum allowed permissions	maximum allowed permission	0	boolean	access control entry	
1f	maximum duration of <evaluation cycle>: time interval	maximum duration	maximum durations	maximum duration	0	time interval	evaluation cycle	
1f	maximum of <evaluation cycle>: integer	maximum	maximums	maximum	0	integer	evaluation cycle	
10	maximum password age of <security database>: time interval	maximum password age	maximum password ages	maximum password age	0	time interval	security database	
ff	maximum seat count of <license>: integer	maximum seat count	maximum seat counts	maximum seat count	0	integer	license	
e0	maximum single computer total of <statistical bin>: floating point	maximum single computer total	maximum single computer totals	maximum single computer total	0	floating point	statistical bin	
10	maximum storage of <user>: integer	maximum storage	maximum storages	maximum storage	0	integer	user	
10	maximum transmission unit of <network adapter>: integer	maximum transmission unit	maximum transmission units	maximum transmission unit	0	integer	network adapter	
e0	maximum value of <statistical bin>: floating point	maximum value	maximum values	maximum value	0	floating point	statistical bin	
1f	maximum_cache_size of <dmi cache_information>: integer	maximum_cache_size	maximum_cache_sizes	maximum_cache_size	0	integer	dmi cache_information	
1f	maximum_capacity of <dmi physical_memory_array>: integer	maximum_capacity	maximum_capacitys	maximum_capacity	0	integer	dmi physical_memory_array	
1f	maximum_channel_load of <dmi memory_channel>: integer	maximum_channel_load	maximum_channel_loads	maximum_channel_load	0	integer	dmi memory_channel	
1f	maximum_error_in_battery_data of <dmi portable_battery>: integer	maximum_error_in_battery_data	maximum_error_in_battery_datas	maximum_error_in_battery_data	0	integer	dmi portable_battery	
1f	maximum_memory_module_size of <dmi memory_controller_information>: integer	maximum_memory_module_size	maximum_memory_module_sizes	maximum_memory_module_size	0	integer	dmi memory_controller_information	
1f	maximum_value of <dmi electrical_current_probe>: integer	maximum_value	maximum_values	maximum_value	0	integer	dmi electrical_current_probe	
1f	maximum_value of <dmi temperature_probe>: integer	maximum_value	maximum_values	maximum_value	0	integer	dmi temperature_probe	
1f	maximum_value of <dmi voltage_probe>: integer	maximum_value	maximum_values	maximum_value	0	integer	dmi voltage_probe	
ff	may <integer> of <integer>: date	may	mays	may	0	date	integer	integer
ff	may <integer>: day of year	may	mays	may	0	day of year		integer
ff	may of <integer>: month and year	may	mays	may	0	month and year	integer	
ff	may: month	may	mays	may	0	month		
1f	md5 of <file>: string	md5	md5s	md5	0	string	file	
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
10	media type <integer>: media type	media type	media types	media type	0	media type		integer
10	media type bridge: media type	media type bridge	media types bridge	media type bridge	0	media type		
10	media type direct: media type	media type direct	media types direct	media type direct	0	media type		
10	media type isdn: media type	media type isdn	media types isdn	media type isdn	0	media type		
10	media type lan: media type	media type lan	media types lans	media type lan	0	media type		
10	media type of <connection>: media type	media type	media types	media type	0	media type	connection	
10	media type phone: media type	media type phone	media types phone	media type phone	0	media type		
10	media type pppoe: media type	media type pppoe	media types pppoe	media type pppoe	0	media type		
10	media type shared access host lan: media type	media type shared access host lan	media types shared access host lan	media type shared access host lan	0	media type		
10	media type shared access host ras: media type	media type shared access host ras	media types shared access host ras	media type shared access host ras	0	media type		
10	media type tunnel: media type	media type tunnel	media types tunnel	media type tunnel	0	media type		
e0	member action set of <bes action>: bes action set	member action set	member action sets	member action set	0	bes action set	bes action	
e0	member actions of <bes action>: bes action	member action	member actions	member actions	1	bes action	bes action	
1f	member of <manual group>: boolean	member	members	member	0	boolean	manual group	
1f	member of <server based group>: boolean	member	members	member	0	boolean	server based group	
1f	member of <site group>: boolean	member	members	member	0	boolean	site group	
e0	member set of <bes computer group>: bes computer set	member set	member sets	member set	0	bes computer set	bes computer group	
e0	members of <bes computer group>: bes computer	member	members	members	1	bes computer	bes computer group	
10	members of <local group>: local group member	member	members	members	1	local group member	local group	
e0	memory usage of <bes property>: integer	memory usage	memory usages	memory usage	0	integer	bes property	
1f	memory_array_error_address of <dmi b32_bit_memory_error_information>: integer	memory_array_error_address	memory_array_error_addresss	memory_array_error_address	0	integer	dmi b32_bit_memory_error_information	
1f	memory_array_error_address of <dmi b64_bit_memory_error_information>: integer	memory_array_error_address	memory_array_error_addresss	memory_array_error_address	0	integer	dmi b64_bit_memory_error_information	
1f	memory_array_handle of <dmi memory_array_mapped_address>: integer	memory_array_handle	memory_array_handles	memory_array_handle	0	integer	dmi memory_array_mapped_address	
1f	memory_array_handle of <dmi memory_device>: integer	memory_array_handle	memory_array_handles	memory_array_handle	0	integer	dmi memory_device	
1f	memory_array_mapped_address <integer> of <dmi>: dmi memory_array_mapped_address	memory_array_mapped_address	memory_array_mapped_addresss	memory_array_mapped_address	0	dmi memory_array_mapped_address	dmi	integer
1f	memory_array_mapped_address_handle of <dmi memory_device_mapped_address>: integer	memory_array_mapped_address_handle	memory_array_mapped_address_handles	memory_array_mapped_address_handle	0	integer	dmi memory_device_mapped_address	
1f	memory_array_mapped_addresss of <dmi>: dmi memory_array_mapped_address	memory_array_mapped_address	memory_array_mapped_addresss	memory_array_mapped_addresss	1	dmi memory_array_mapped_address	dmi	
1f	memory_channel <integer> of <dmi>: dmi memory_channel	memory_channel	memory_channels	memory_channel	0	dmi memory_channel	dmi	integer
1f	memory_channels of <dmi>: dmi memory_channel	memory_channel	memory_channels	memory_channels	1	dmi memory_channel	dmi	
1f	memory_controller_information <integer> of <dmi>: dmi memory_controller_information	memory_controller_information	memory_controller_informations	memory_controller_information	0	dmi memory_controller_information	dmi	integer
1f	memory_controller_informations of <dmi>: dmi memory_controller_information	memory_controller_information	memory_controller_informations	memory_controller_informations	1	dmi memory_controller_information	dmi	
1f	memory_device <integer> of <dmi>: dmi memory_device	memory_device	memory_devices	memory_device	0	dmi memory_device	dmi	integer
1f	memory_device_count of <dmi memory_channel>: integer	memory_device_count	memory_device_counts	memory_device_count	0	integer	dmi memory_channel	
1f	memory_device_handle of <dmi memory_channel>: integer	memory_device_handle	memory_device_handles	memory_device_handle	0	integer	dmi memory_channel	
1f	memory_device_handle of <dmi memory_device_mapped_address>: integer	memory_device_handle	memory_device_handles	memory_device_handle	0	integer	dmi memory_device_mapped_address	
1f	memory_device_load of <dmi memory_channel>: integer	memory_device_load	memory_device_loads	memory_device_load	0	integer	dmi memory_channel	
1f	memory_device_mapped_address <integer> of <dmi>: dmi memory_device_mapped_address	memory_device_mapped_address	memory_device_mapped_addresss	memory_device_mapped_address	0	dmi memory_device_mapped_address	dmi	integer
1f	memory_device_mapped_addresss of <dmi>: dmi memory_device_mapped_address	memory_device_mapped_address	memory_device_mapped_addresss	memory_device_mapped_addresss	1	dmi memory_device_mapped_address	dmi	
1f	memory_devices of <dmi>: dmi memory_device	memory_device	memory_devices	memory_devices	1	dmi memory_device	dmi	
1f	memory_error_correction of <dmi physical_memory_array>: integer	memory_error_correction	memory_error_corrections	memory_error_correction	0	integer	dmi physical_memory_array	
1f	memory_error_information_handle of <dmi memory_device>: integer	memory_error_information_handle	memory_error_information_handles	memory_error_information_handle	0	integer	dmi memory_device	
1f	memory_error_information_handle of <dmi physical_memory_array>: integer	memory_error_information_handle	memory_error_information_handles	memory_error_information_handle	0	integer	dmi physical_memory_array	
1f	memory_module_information <integer> of <dmi>: dmi memory_module_information	memory_module_information	memory_module_informations	memory_module_information	0	dmi memory_module_information	dmi	integer
1f	memory_module_informations of <dmi>: dmi memory_module_information	memory_module_information	memory_module_informations	memory_module_informations	1	dmi memory_module_information	dmi	
1f	memory_module_voltage of <dmi memory_controller_information>: integer	memory_module_voltage	memory_module_voltages	memory_module_voltage	0	integer	dmi memory_controller_information	
1f	memory_type of <dmi memory_device>: integer	memory_type	memory_types	memory_type	0	integer	dmi memory_device	
e0	menu path of <bes wizard>: string	menu path	menu paths	menu path	0	string	bes wizard	
e0	message action button flag of <bes action>: boolean	message action button flag	message action button flags	message action button flag	0	boolean	bes action	
e0	message allow cancel flag of <bes action>: boolean	message allow cancel flag	message allow cancel flags	message allow cancel flag	0	boolean	bes action	
10	message body of <show message task action>: string	message body	message bodies	message body	0	string	show message task action	
e0	message of <bes fixlet>: html	message	messages	message	0	html	bes fixlet	
e0	message postpone delay of <bes action>: time interval	message postpone delay	message postpone delays	message postpone delay	0	time interval	bes action	
e0	message text of <bes action>: string	message text	message texts	message text	0	string	bes action	
e0	message timeout delay of <bes action>: time interval	message timeout delay	message timeout delays	message timeout delay	0	time interval	bes action	
e0	message title of <bes action>: string	message title	message titles	message title	0	string	bes action	
ff	meta <string> of <html>: html	meta	metas	meta	0	html	html	string
ff	meta <string> of <string>: html	meta	metas	meta	0	html	string	string
ff	meta of <html>: html	meta	metas	meta	0	html	html	
ff	meta of <string>: html	meta	metas	meta	0	html	string	
10	metabase: metabase	metabase	metabases	metabase	0	metabase		
10	metered connection of <network adapter>: boolean	metered connection	metered connections	metered connection	0	boolean	network adapter	
10	metric <integer> of <operating system>: integer	metric	metrics	metric	0	integer	operating system	integer
d	metric of <route>: integer	metric	metrics	metric	0	integer	route	
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
9	minima of <debian package upstream version>: debian package upstream version	minimum	minima	minima	1	debian package upstream version	debian package upstream version	
9	minima of <debian package version epoch>: debian package version epoch	minimum	minima	minima	1	debian package version epoch	debian package version epoch	
9	minima of <debian package version revision>: debian package version revision	minimum	minima	minima	1	debian package version revision	debian package version revision	
9	minima of <debian package version>: debian package version	minimum	minima	minima	1	debian package version	debian package version	
ff	minima of <floating point>: floating point	minimum	minima	minima	1	floating point	floating point	
ff	minima of <hertz>: hertz	minimum	minima	minima	1	hertz	hertz	
ff	minima of <integer>: integer	minimum	minima	minima	1	integer	integer	
ff	minima of <ipv4 address>: ipv4 address	minimum	minima	minima	1	ipv4 address	ipv4 address	
ff	minima of <ipv4or6 address>: ipv4or6 address	minimum	minima	minima	1	ipv4or6 address	ipv4or6 address	
ff	minima of <ipv6 address>: ipv6 address	minimum	minima	minima	1	ipv6 address	ipv6 address	
5f	minima of <large integer>: large integer	minimum	minima	minima	1	large integer	large integer	
ff	minima of <month and year>: month and year	minimum	minima	minima	1	month and year	month and year	
ff	minima of <month>: month	minimum	minima	minima	1	month	month	
ff	minima of <number of months>: number of months	minimum	minima	minima	1	number of months	number of months	
e2	minima of <rate>: rate	minimum	minima	minima	1	rate	rate	
4	minima of <rpm package release>: rpm package release	minimum	minima	minima	1	rpm package release	rpm package release	
4	minima of <rpm package version record>: rpm package version record	minimum	minima	minima	1	rpm package version record	rpm package version record	
4	minima of <rpm package version>: rpm package version	minimum	minima	minima	1	rpm package version	rpm package version	
4	minima of <short rpm package version record>: short rpm package version record	minimum	minima	minima	1	short rpm package version record	short rpm package version record	
ff	minima of <site version list>: site version list	minimum	minima	minima	1	site version list	site version list	
ff	minima of <time interval>: time interval	minimum	minima	minima	1	time interval	time interval	
ff	minima of <time of day>: time of day	minimum	minima	minima	1	time of day	time of day	
ff	minima of <time>: time	minimum	minima	minima	1	time	time	
5f	minima of <uinteger>: uinteger	minimum	minima	minima	1	uinteger	uinteger	
1f	minima of <uuid>: uuid	minimum	minima	minima	1	uuid	uuid	
ff	minima of <version>: version	minimum	minima	minima	1	version	version	
ff	minima of <year>: year	minimum	minima	minima	1	year	year	
10	minimum password age of <security database>: time interval	minimum password age	minimum password ages	minimum password age	0	time interval	security database	
10	minimum password length of <security database>: integer	minimum password length	minimum password lengths	minimum password length	0	integer	security database	
e0	minimum single computer total of <statistical bin>: floating point	minimum single computer total	minimum single computer totals	minimum single computer total	0	floating point	statistical bin	
e0	minimum value of <statistical bin>: floating point	minimum value	minimum values	minimum value	0	floating point	statistical bin	
1f	minimum_value of <dmi electrical_current_probe>: integer	minimum_value	minimum_values	minimum_value	0	integer	dmi electrical_current_probe	
1f	minimum_value of <dmi temperature_probe>: integer	minimum_value	minimum_values	minimum_value	0	integer	dmi temperature_probe	
1f	minimum_value of <dmi voltage_probe>: integer	minimum_value	minimum_values	minimum_value	0	integer	dmi voltage_probe	
d	minor of <device file>: integer	minor	minors	minor	0	integer	device file	
ff	minor revision of <version>: integer	minor revision	minor revisions	minor revision	0	integer	version	
1f	minor version of <operating system>: integer	minor version	minor versions	minor version	0	integer	operating system	
ff	minute: time interval	minute	minutes	minute	0	time interval		
ff	minute_of_hour of <time of day with time zone>: integer	minute_of_hour	minutes_of_hour	minute_of_hour	0	integer	time of day with time zone	
ff	minute_of_hour of <time of day>: integer	minute_of_hour	minutes_of_hour	minute_of_hour	0	integer	time of day	
10	missed run count of <scheduled task>: integer	missed run count	missed run counts	missed run count	0	integer	scheduled task	
ff	mobile count of <bes product>: integer	mobile count	mobile counts	mobile count	0	integer	bes product	
d	mode of <filesystem object>: mode	mode	modes	mode	0	mode	filesystem object	
1d	model name of <processor>: string	model name	model names	model name	0	string	processor	
1f	model of <processor>: integer	model	models	model	0	integer	processor	
1f	model_part_number of <dmi system_power_supply>: string	model_part_number	model_part_numbers	model_part_number	0	string	dmi system_power_supply	
2	modem scripts folder of <domain>: folder	modem scripts folder	modem scripts folders	modem scripts folder	0	folder	domain	
2	modem scripts folder: folder	modem scripts folder	modem scripts folders	modem scripts folder	0	folder		
e0	modification time of <bes activation>: time	modification time	modification times	modification time	0	time	bes activation	
e0	modification time of <bes fixlet>: time	modification time	modification times	modification time	0	time	bes fixlet	
1f	modification time of <execution>: time	modification time	modification times	modification time	0	time	execution	
1f	modification time of <filesystem object>: time	modification time	modification times	modification time	0	time	filesystem object	
d	modification time of <symlink>: time	modification time	modification times	modification time	0	time	symlink	
2	modification time of <volume>: time	modification time	modification times	modification time	0	time	volume	
e0	modification user of <bes fixlet>: bes user	modification user	modification users	modification user	0	bes user	bes fixlet	
2	modified flag of <route>: boolean	modified flag	modified flags	modified flag	0	boolean	route	
d	module <integer> of <grub bootable image>: grub module	module	modules	module	0	grub module	grub bootable image	integer
ff	module <string>: module	module	modules	module	0	module		string
d	modules of <grub bootable image>: grub module	module	modules	modules	1	grub module	grub bootable image	
ff	modules: module	module	modules	modules	1	module		
ff	monday: day of week	monday	mondays	monday	0	day of week		
12	monitor intervals of <power history>: monitor power interval	monitor interval	monitor intervals	monitor intervals	1	monitor power interval	power history	
12	monitor invalid state: power state	monitor invalid state	monitor invalid states	monitor invalid state	0	power state		
12	monitor off state: power state	monitor off state	monitor off states	monitor off state	0	power state		
12	monitor on state: power state	monitor on state	monitor on states	monitor on state	0	power state		
12	monitor standby state: power state	monitor standby state	monitor standby states	monitor standby state	0	power state		
ff	month <integer>: month	month	months	month	0	month		integer
ff	month <string>: month	month	months	month	0	month		string
ff	month of <date>: month	month	months	month	0	month	date	
ff	month of <day of year>: month	month	months	month	0	month	day of year	
ff	month of <month and year>: month	month	months	month	0	month	month and year	
ff	month: number of months	month	months	month	0	number of months		
ff	month_and_year of <date>: month and year	month_and_year	months_and_years	month_and_year	0	month and year	date	
10	monthly task trigger type: task trigger type	monthly task trigger type	monthly task trigger types	monthly task trigger type	0	task trigger type		
10	monthlydow task trigger type: task trigger type	monthlydow task trigger type	monthlydow task trigger types	monthlydow task trigger type	0	task trigger type		
10	months runs of <monthly task trigger>: month	months run	months runs	months runs	1	month	monthly task trigger	
10	months runs of <monthlydow task trigger>: month	months run	months runs	months runs	1	month	monthlydow task trigger	
ff	more significance <integer> of <floating point>: floating point	more significance	more significances	more significance	0	floating point	floating point	integer
ff	most significant one bit of <bit set>: integer	most significant one bit	most significant one bits	most significant one bit	0	integer	bit set	
d	mount option of <filesystem>: string	mount option	mount options	mount option	0	string	filesystem	
d	mount point of <filesystem>: string	mount point	mount points	mount point	0	string	filesystem	
f	mtu of <route>: integer	mtu	mtus	mtu	0	integer	route	
2	multicast flag of <route>: boolean	multicast flag	multicast flags	multicast flag	0	boolean	route	
1f	multicast support of <network adapter interface>: boolean	multicast support	multicast supports	multicast support	0	boolean	network adapter interface	
1f	multicast support of <network adapter>: boolean	multicast support	multicast supports	multicast support	0	boolean	network adapter	
1f	multicast support of <network ip interface>: boolean	multicast support	multicast supports	multicast support	0	boolean	network ip interface	
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
9	multiplicity of <debian package upstream version with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	debian package upstream version with multiplicity	
9	multiplicity of <debian package version epoch with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	debian package version epoch with multiplicity	
9	multiplicity of <debian package version revision with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	debian package version revision with multiplicity	
9	multiplicity of <debian package version with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	debian package version with multiplicity	
ff	multiplicity of <floating point with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	floating point with multiplicity	
ff	multiplicity of <hertz with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	hertz with multiplicity	
ff	multiplicity of <integer with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	integer with multiplicity	
ff	multiplicity of <ipv4 address with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	ipv4 address with multiplicity	
ff	multiplicity of <ipv4or6 address with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	ipv4or6 address with multiplicity	
ff	multiplicity of <ipv6 address with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	ipv6 address with multiplicity	
5f	multiplicity of <large integer with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	large integer with multiplicity	
ff	multiplicity of <month and year with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	month and year with multiplicity	
ff	multiplicity of <month with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	month with multiplicity	
ff	multiplicity of <number of months with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	number of months with multiplicity	
e2	multiplicity of <rate with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	rate with multiplicity	
4	multiplicity of <rpm package release with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	rpm package release with multiplicity	
4	multiplicity of <rpm package version record with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	rpm package version record with multiplicity	
4	multiplicity of <rpm package version with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	rpm package version with multiplicity	
4	multiplicity of <short rpm package version record with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	short rpm package version record with multiplicity	
ff	multiplicity of <site version list with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	site version list with multiplicity	
ff	multiplicity of <string with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	string with multiplicity	
ff	multiplicity of <time interval with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time interval with multiplicity	
ff	multiplicity of <time of day with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time of day with multiplicity	
ff	multiplicity of <time of day with time zone with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time of day with time zone with multiplicity	
ff	multiplicity of <time range with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time range with multiplicity	
ff	multiplicity of <time with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time with multiplicity	
ff	multiplicity of <time zone with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	time zone with multiplicity	
5f	multiplicity of <uinteger with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	uinteger with multiplicity	
1f	multiplicity of <uuid with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	uuid with multiplicity	
ff	multiplicity of <version with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	version with multiplicity	
ff	multiplicity of <year with multiplicity>: integer	multiplicity	multiplicities	multiplicity	0	integer	year with multiplicity	
ff	multivalued of <property>: boolean	multivalued	multivalueds	multivalued	0	boolean	property	
ff	mvs count of <bes product>: integer	mvs count	mvs counts	mvs count	0	integer	bes product	
d	name of <SELinux Boolean>: string	name	names	name	0	string	SELinux Boolean	
d	name of <Xinetd Service>: string	name	names	name	0	string	Xinetd Service	
12	name of <active directory group>: string	name	names	name	0	string	active directory group	
12	name of <active directory local user>: string	name	names	name	0	string	active directory local user	
12	name of <agent interface capability>: string	name	names	name	0	string	agent interface capability	
1f	name of <application usage summary instance>: string	name	names	name	0	string	application usage summary instance	
1f	name of <application usage summary>: string	name	names	name	0	string	application usage summary	
10	name of <audit policy category>: string	name	names	name	0	string	audit policy category	
10	name of <audit policy subcategory>: string	name	names	name	0	string	audit policy subcategory	
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
4	name of <capability>: string	name	names	name	0	string	capability	
ff	name of <cast>: string	name	names	name	0	string	cast	
2	name of <client process owner>: string	name	names	name	0	string	client process owner	
1f	name of <cloud provider>: string	name	names	name	0	string	cloud provider	
2	name of <component>: string	name	names	name	0	string	component	
2	name of <computer>: string	name	names	name	0	string	computer	
10	name of <connection>: string	name	names	name	0	string	connection	
9	name of <debian base package>: string	name	names	name	0	string	debian base package	
9	name of <debian versioned package>: string	name	names	name	0	string	debian versioned package	
1f	name of <download server>: string	name	names	name	0	string	download server	
10	name of <drive>: string	name	names	name	0	string	drive	
1f	name of <environment variable>: string	name	names	name	0	string	environment variable	
1f	name of <filesystem object>: string	name	names	name	0	string	filesystem object	
d	name of <filesystem>: string	name	names	name	0	string	filesystem	
10	name of <firewall authorized application>: string	name	names	name	0	string	firewall authorized application	
10	name of <firewall open port>: string	name	names	name	0	string	firewall open port	
10	name of <firewall rule>: string	name	names	name	0	string	firewall rule	
10	name of <firewall service>: string	name	names	name	0	string	firewall service	
1f	name of <fixlet_header>: string	name	names	name	0	string	fixlet_header	
ff	name of <json key>: string	name	names	name	0	string	json key	
10	name of <local group>: string	name	names	name	0	string	local group	
1f	name of <logged on user>: string	name	names	name	0	string	logged on user	
10	name of <metabase key>: string	name	names	name	0	string	metabase key	
e0	name of <mime field>: string	name	names	name	0	string	mime field	
ff	name of <module>: string	name	names	name	0	string	module	
1f	name of <network adapter>: string	name	names	name	0	string	network adapter	
2	name of <network interface>: string	name	names	name	0	string	network interface	
f	name of <network ip interface>: string	name	names	name	0	string	network ip interface	
10	name of <network share>: string	name	names	name	0	string	network share	
1f	name of <operating system>: string	name	names	name	0	string	operating system	
4	name of <package>: string	name	names	name	0	string	package	
14	name of <plugin store key>: string	name	names	name	0	string	plugin store key	
10	name of <port mapping>: string	name	names	name	0	string	port mapping	
1f	name of <process>: string	name	names	name	0	string	process	
1f	name of <registration server>: string	name	names	name	0	string	registration server	
10	name of <registry key value>: string	name	names	name	0	string	registry key value	
10	name of <registry key>: string	name	names	name	0	string	registry key	
2	name of <registrynode>: string	name	names	name	0	string	registrynode	
10	name of <running task>: string	name	names	name	0	string	running task	
10	name of <scheduled task>: string	name	names	name	0	string	scheduled task	
1f	name of <selected server>: string	name	names	name	0	string	selected server	
1f	name of <setting>: string	name	names	name	0	string	setting	
10	name of <site profile variable>: string	name	names	name	0	string	site profile variable	
1f	name of <site>: string	name	names	name	0	string	site	
1f	name of <smbios structure>: string	name	names	name	0	string	smbios structure	
1f	name of <smbios value>: string	name	names	name	0	string	smbios value	
1f	name of <sqlite column type>: string	name	names	name	0	string	sqlite column type	
1f	name of <sqlite column>: string	name	names	name	0	string	sqlite column	
1f	name of <sqlite table>: string	name	names	name	0	string	sqlite table	
d	name of <symlink>: string	name	names	name	0	string	symlink	
10	name of <task folder>: string	name	names	name	0	string	task folder	
10	name of <task named value pair>: string	name	names	name	0	string	task named value pair	
10	name of <task network settings>: string	name	names	name	0	string	task network settings	
ff	name of <type>: string	name	names	name	0	string	type	
ff	name of <unary operator>: string	name	names	name	0	string	unary operator	
1f	name of <user>: string	name	names	name	0	string	user	
2	name of <volume>: string	name	names	name	0	string	volume	
12	name of <wifi>: string	name	names	name	0	string	wifi	
10	name of <winrt enumeration>: string	name	names	name	0	string	winrt enumeration	
10	name of <winrt package id>: string	name	names	name	0	string	winrt package id	
10	name of <wmi select>: string	name	names	name	0	string	wmi select	
1f	name of <yaml key>: string	name	names	name	0	string	yaml key	
2	name registry version: version	name registry version	name registry versions	name registry version	0	version		
ff	nan of <floating point>: boolean	nan	nans	nan	0	boolean	floating point	
10	native application <string>: application	native application	native applications	native application	0	application		string
10	native file <string> of <encoding>: file	native file	native files	native file	0	file	encoding	string
10	native file <string>: file	native file	native files	native file	0	file		string
10	native folder <string> of <encoding>: folder	native folder	native folders	native folder	0	folder	encoding	string
10	native folder <string>: folder	native folder	native folders	native folder	0	folder		string
10	native program files folder: folder	native program files folder	native program files folders	native program files folder	0	folder		
10	native registry: registry	native registry	native registries	native registry	0	registry		
10	native system folder: folder	native system folder	native system folders	native system folder	0	folder		
e0	navbar name of <bes wizard>: string	navbar name	navbar names	navbar name	0	string	bes wizard	
10	netbios domainname of <active directory local computer>: string	netbios domainname	netbios domainnames	netbios domainname	0	string	active directory local computer	
10	netbios domainname of <active directory local user>: string	netbios domainname	netbios domainnames	netbios domainname	0	string	active directory local user	
2	netstat flag of <route>: string	netstat flag	netstat flags	netstat flag	0	string	route	
2	network domain: domain	network domain	network domains	network domain	0	domain		
10	network group: security account	network group	network groups	network group	0	security account		
10	network service group: security account	network service group	network service groups	network service group	0	security account		
10	network setting of <task settings>: task network settings	network setting	network settings	network setting	0	task network settings	task settings	
10	network share <string>: network share	network share	network shares	network share	0	network share		string
10	network shares: network share	network share	network shares	network shares	1	network share		
1f	network: network	network	networks	network	0	network		
1f	next line of <file line>: file line	next line	next lines	next line	0	file line	file line	
1f	next rawline of <file line>: file line	next rawline	next rawlines	next rawline	0	file line	file line	
10	next run time of <scheduled task>: time	next run time	next run times	next run time	0	time	scheduled task	
bd	next sibling of <xml dom node>: xml dom node	next sibling	next siblings	next sibling	0	xml dom node	xml dom node	
1f	next_scheduled_power_on_day_of_month of <dmi system_power_controls>: integer	next_scheduled_power_on_day_of_month	next_scheduled_power_on_day_of_months	next_scheduled_power_on_day_of_month	0	integer	dmi system_power_controls	
1f	next_scheduled_power_on_hour of <dmi system_power_controls>: integer	next_scheduled_power_on_hour	next_scheduled_power_on_hours	next_scheduled_power_on_hour	0	integer	dmi system_power_controls	
1f	next_scheduled_power_on_minute of <dmi system_power_controls>: integer	next_scheduled_power_on_minute	next_scheduled_power_on_minutes	next_scheduled_power_on_minute	0	integer	dmi system_power_controls	
1f	next_scheduled_power_on_month of <dmi system_power_controls>: integer	next_scheduled_power_on_month	next_scheduled_power_on_months	next_scheduled_power_on_month	0	integer	dmi system_power_controls	
1f	next_scheduled_power_on_second of <dmi system_power_controls>: integer	next_scheduled_power_on_second	next_scheduled_power_on_seconds	next_scheduled_power_on_second	0	integer	dmi system_power_controls	
ff	nil: undefined	nil	nothings	nil	0	undefined		
d	no access of <Xinetd Service>: string	no access	no accesses	no access	0	string	Xinetd Service	
4	no epoch of <rpm package version record>: rpm package version record	no epoch	no epochs	no epoch	0	rpm package version record	rpm package version record	
4	no epoch of <short rpm package version record>: short rpm package version record	no epoch	no epochs	no epoch	0	short rpm package version record	short rpm package version record	
10	no password required flag of <user>: boolean	no password required flag	no password required flags	no password required flag	0	boolean	user	
10	no propagate inherit of <access control entry>: boolean	no propagate inherit	no propagate inherits	no propagate inherit	0	boolean	access control entry	
2	node <string> of <registrynode>: registrynode	node	nodes	node	0	registrynode	registrynode	string
2	node <string> of <registryroot>: registrynode	node	nodes	node	0	registrynode	registryroot	string
bd	node name of <xml dom node>: string	node name	node names	node name	0	string	xml dom node	
bd	node type of <xml dom node>: integer	node type	node types	node type	0	integer	xml dom node	
bd	node value of <xml dom node>: string	node value	node values	node value	0	string	xml dom node	
2	nodes of <registrynode>: registrynode	node	nodes	nodes	1	registrynode	registrynode	
1f	nominal_speed of <dmi cooling_device>: integer	nominal_speed	nominal_speeds	nominal_speed	0	integer	dmi cooling_device	
1f	nominal_value of <dmi electrical_current_probe>: integer	nominal_value	nominal_values	nominal_value	0	integer	dmi electrical_current_probe	
1f	nominal_value of <dmi temperature_probe>: integer	nominal_value	nominal_values	nominal_value	0	integer	dmi temperature_probe	
1f	nominal_value of <dmi voltage_probe>: integer	nominal_value	nominal_values	nominal_value	0	integer	dmi voltage_probe	
ff	non windows server count of <bes product>: integer	non windows server count	non windows server counts	non windows server count	0	integer	bes product	
10	none firewall service type: firewall service type	none firewall service type	none firewall service types	none firewall service type	0	firewall service type		
10	none logon of <task principal>: boolean	none logon	none logons	none logon	0	boolean	task principal	
ff	noon: time of day	noon	noons	noon	0	time of day		
10	normal account flag of <user>: boolean	normal account flag	normal account flags	normal account flag	0	boolean	user	
10	normal of <filesystem object>: boolean	normal	normals	normal	0	boolean	filesystem object	
ff	normal of <floating point>: boolean	normal	normals	normal	0	boolean	floating point	
d	normal of <grub color scheme>: grub color pair	normal	normals	normal	0	grub color pair	grub color scheme	
1f	normal of <power level>: boolean	normal	normals	normal	0	boolean	power level	
10	normal priority: priority class	normal priority	normal priorities	normal priority	0	priority class		
10	normalized date of <fixlet_header>: date	normalized date	normalized dates	normalized date	0	date	fixlet_header	
10	notifications disabled of <firewall profile>: boolean	notifications disabled	notifications disableds	notifications disabled	0	boolean	firewall profile	
d	nounzip of <grub module>: boolean	nounzip	nounzips	nounzip	0	boolean	grub module	
ff	november <integer> of <integer>: date	november	novembers	november	0	date	integer	integer
ff	november <integer>: day of year	november	novembers	november	0	day of year		integer
ff	november of <integer>: month and year	november	novembers	november	0	month and year	integer	
ff	november: month	november	novembers	november	0	month		
1f	now of <registration server>: time	now	nows	now	0	time	registration server	
ff	now: time	now	nows	now	0	time		
10	nt domain controller product type: operating system product type	nt domain controller product type	nt domain controller product types	nt domain controller product type	0	operating system product type		
10	nt server product type: operating system product type	nt server product type	nt server product types	nt server product type	0	operating system product type		
10	nt workstation product type: operating system product type	nt workstation product type	nt workstation product types	nt workstation product type	0	operating system product type		
2	nubus map: integer	nubus map	nubus maps	nubus map	0	integer		
10	null dacl of <security descriptor>: boolean	null dacl	null dacls	null dacl	0	boolean	security descriptor	
1f	null of <sqlite column type>: boolean	null	nulls	null	0	boolean	sqlite column type	
10	null sacl of <security descriptor>: boolean	null sacl	null sacls	null sacl	0	boolean	security descriptor	
ff	null: undefined	null	nothing	null	0	undefined		
1f	number_of_additional_information_entries of <dmi additional_information>: integer	number_of_additional_information_entries	number_of_additional_information_entriess	number_of_additional_information_entries	0	integer	dmi additional_information	
1f	number_of_associated_memory_slots of <dmi memory_controller_information>: integer	number_of_associated_memory_slots	number_of_associated_memory_slotss	number_of_associated_memory_slots	0	integer	dmi memory_controller_information	
1f	number_of_buttons of <dmi built_in_pointing_device>: integer	number_of_buttons	number_of_buttonss	number_of_buttons	0	integer	dmi built_in_pointing_device	
1f	number_of_contained_object_handles of <dmi base_board_information>: integer	number_of_contained_object_handles	number_of_contained_object_handless	number_of_contained_object_handles	0	integer	dmi base_board_information	
1f	number_of_memory_devices of <dmi physical_memory_array>: integer	number_of_memory_devices	number_of_memory_devicess	number_of_memory_devices	0	integer	dmi physical_memory_array	
1f	number_of_power_cords of <dmi system_enclosure_or_chassis>: integer	number_of_power_cords	number_of_power_cordss	number_of_power_cords	0	integer	dmi system_enclosure_or_chassis	
10	numeric type of <drive>: integer	numeric type	numeric types	numeric type	0	integer	drive	
ff	numeric value of <string>: integer	numeric value	numeric values	numeric value	0	integer	string	
1f	nv_storage_device_address of <dmi ipmi_device_information>: integer	nv_storage_device_address	nv_storage_device_addresss	nv_storage_device_address	0	integer	dmi ipmi_device_information	
1d	nx bit of <process>: boolean	nx bit	nx bits	nx bit	0	boolean	process	
10	object access category of <audit policy>: audit policy category	object access category	object access categories	object access category	0	audit policy category	audit policy	
10	object inherit of <access control entry>: boolean	object inherit	object inherits	object inherit	0	boolean	access control entry	
4	obsoletes of <package>: capability	obsolete	obsoletes	obsoletes	1	capability	package	
ff	october <integer> of <integer>: date	october	octobers	october	0	date	integer	integer
ff	october <integer>: day of year	october	octobers	october	0	day of year		integer
ff	october of <integer>: month and year	october	octobers	october	0	month and year	integer	
ff	october: month	october	octobers	october	0	month		
10	oem code page: integer	oem code page	oem code pages	oem code page	0	integer		
1f	oem_defined of <dmi cooling_device>: integer	oem_defined	oem_defineds	oem_defined	0	integer	dmi cooling_device	
1f	oem_defined of <dmi electrical_current_probe>: integer	oem_defined	oem_defineds	oem_defined	0	integer	dmi electrical_current_probe	
1f	oem_defined of <dmi system_enclosure_or_chassis>: integer	oem_defined	oem_defineds	oem_defined	0	integer	dmi system_enclosure_or_chassis	
1f	oem_defined of <dmi temperature_probe>: integer	oem_defined	oem_defineds	oem_defined	0	integer	dmi temperature_probe	
1f	oem_defined of <dmi voltage_probe>: integer	oem_defined	oem_defineds	oem_defined	0	integer	dmi voltage_probe	
1f	oem_specific of <dmi portable_battery>: integer	oem_specific	oem_specifics	oem_specific	0	integer	dmi portable_battery	
1f	oem_string <integer> of <dmi>: string	oem_string	oem_strings	oem_string	0	string	dmi	integer
1f	oem_strings of <dmi>: string	oem_string	oem_strings	oem_strings	1	string	dmi	
12	off state: power state	off state	off states	off state	0	power state		
1f	offer accepted of <action>: boolean	offer accepted	offer accepteds	offer accepted	0	boolean	action	
e0	offer category of <bes action>: string	offer category	offer categories	offer category	0	string	bes action	
e0	offer description html of <bes action>: html	offer description html	offer description htmls	offer description html	0	html	bes action	
e0	offer flag of <bes action>: boolean	offer flag	offer flags	offer flag	0	boolean	bes action	
1f	offer of <action>: boolean	offer	offers	offer	0	boolean	action	
10	offline of <filesystem object>: boolean	offline	offlines	offline	0	boolean	filesystem object	
1f	offset of <smbios value>: integer	offset	offsets	offset	0	integer	smbios value	
10	ok firewall local policy modify state: firewall local policy modify state	ok firewall local policy modify state	ok firewall local policy modify states	ok firewall local policy modify state	0	firewall local policy modify state		
ff	ol <string> of <html>: html	ol	ols	ol	0	html	html	string
ff	ol <string> of <string>: html	ol	ols	ol	0	html	string	string
ff	ol of <html>: html	ol	ols	ol	0	html	html	
ff	ol of <string>: html	ol	ols	ol	0	html	string	
10	oldest record number of <event log>: integer	oldest record number	oldest record numbers	oldest record number	0	integer	event log	
2	on appropriate disk domain: domain	on appropriate disk domain	on appropriate disk domains	on appropriate disk domain	0	domain		
2	on system disk domain: domain	on system disk domain	on system disk domains	on system disk domain	0	domain		
1f	on_board_devices_information <integer> of <dmi>: dmi on_board_devices_information	on_board_devices_information	on_board_devices_informations	on_board_devices_information	0	dmi on_board_devices_information	dmi	integer
1f	on_board_devices_informations of <dmi>: dmi on_board_devices_information	on_board_devices_information	on_board_devices_informations	on_board_devices_informations	1	dmi on_board_devices_information	dmi	
1f	onboard_devices_extended_information <integer> of <dmi>: dmi onboard_devices_extended_information	onboard_devices_extended_information	onboard_devices_extended_informations	onboard_devices_extended_information	0	dmi onboard_devices_extended_information	dmi	integer
1f	onboard_devices_extended_informations of <dmi>: dmi onboard_devices_extended_information	onboard_devices_extended_information	onboard_devices_extended_informations	onboard_devices_extended_informations	1	dmi onboard_devices_extended_information	dmi	
ff	one bits of <bit set>: integer	one bit	one bits	one bits	1	integer	bit set	
d	only from of <Xinetd Service>: string	only from	only froms	only from	0	string	Xinetd Service	
10	only raw version block of <file>: file version block	only raw version block	only raw version blocks	only raw version block	0	file version block	file	
10	only version block of <file>: file version block	only version block	only version blocks	only version block	0	file version block	file	
e0	open action count of <bes fixlet>: integer	open action count	open action counts	open action count	0	integer	bes fixlet	
ff	operand type of <cast>: type	operand type	operand types	operand type	0	type	cast	
ff	operand type of <unary operator>: type	operand type	operand types	operand type	0	type	unary operator	
e0	operating system of <bes computer>: string	operating system	operating systems	operating system	0	string	bes computer	
10	operating system product type <integer>: operating system product type	operating system product type	operating system product types	operating system product type	0	operating system product type		integer
1f	operating system: operating system	operating system	operating systems	operating system	0	operating system		
e0	operator of <bes site>: bes user	operator	operators	operator	0	bes user	bes site	
e0	operator site flag of <bes action>: boolean	operator site flag	operator site flags	operator site flag	0	boolean	bes action	
e0	operator site flag of <bes fixlet>: boolean	operator site flag	operator site flags	operator site flag	0	boolean	bes fixlet	
e0	operator site flag of <bes site>: boolean	operator site flag	operator site flags	operator site flag	0	boolean	bes site	
e0	operator site of <bes user>: bes site	operator site	operator sites	operator site	0	bes site	bes user	
10	options of <port mapping>: integer	options	optionss	options	0	integer	port mapping	
ff	ordered lists <string> of <html>: html	ordered list	ordered lists	ordered lists	1	html	html	string
ff	ordered lists <string> of <string>: html	ordered list	ordered lists	ordered lists	1	html	string	string
ff	ordered lists of <html>: html	ordered list	ordered lists	ordered lists	1	html	html	
ff	ordered lists of <string>: html	ordered list	ordered lists	ordered lists	1	html	string	
ff	organization of <license>: string	organization	organizations	organization	0	string	license	
1f	origin fixlet id of <action>: integer	origin fixlet id	origin fixlet ids	origin fixlet id	0	integer	action	
2	os log store <string>: os log store	os log store	os log stores	os log store	0	os log store		string
1f	other duration of <evaluation cycle>: time interval	other duration	other durations	other duration	0	time interval	evaluation cycle	
d	other execute of <filesystem object>: boolean	other execute	other executes	other execute	0	boolean	filesystem object	
d	other mask of <filesystem object>: integer	other mask	other masks	other mask	0	integer	filesystem object	
d	other mask of <mode>: mode_mask	other mask	other masks	other mask	0	mode_mask	mode	
1f	other percent of <evaluation cycle>: floating point	other percent	other percents	other percent	0	floating point	evaluation cycle	
d	other read of <filesystem object>: boolean	other read	other reads	other read	0	boolean	filesystem object	
d	other write of <filesystem object>: boolean	other write	other writes	other write	0	boolean	filesystem object	
1f	out_of_band_remote_access <integer> of <dmi>: dmi out_of_band_remote_access	out_of_band_remote_access	out_of_band_remote_accesss	out_of_band_remote_access	0	dmi out_of_band_remote_access	dmi	integer
1f	out_of_band_remote_accesss of <dmi>: dmi out_of_band_remote_access	out_of_band_remote_access	out_of_band_remote_accesss	out_of_band_remote_accesss	1	dmi out_of_band_remote_access	dmi	
10	outbound connections allowed of <firewall profile>: boolean	outbound connections allowed	outbound connections alloweds	outbound connections allowed	0	boolean	firewall profile	
10	outbound of <firewall rule>: boolean	outbound	outbounds	outbound	0	boolean	firewall rule	
ff	overflow of <floating point>: boolean	overflow	overflows	overflow	0	boolean	floating point	
bd	owner document of <xml dom node>: xml dom document	owner document	owner documents	owner document	0	xml dom document	xml dom node	
e0	owner flag <bes user> of <bes site>: boolean	owner flag	owner flags	owner flag	0	boolean	bes site	bes user
10	owner of <security descriptor>: security identifier	owner	owners	owner	0	security identifier	security descriptor	
e0	owner set of <bes site>: bes user set	owner set	owner sets	owner set	0	bes user set	bes site	
e0	owners of <bes site>: bes user	owner	owners	owners	1	bes user	bes site	
ff	p <string> of <html>: html	p	ps	p	0	html	html	string
ff	p <string> of <string>: html	p	ps	p	0	html	string	string
ff	p of <html>: html	p	ps	p	0	html	html	
ff	p of <string>: html	p	ps	p	0	html	string	
9	packages <string> of <debianpackagecache>: debian versioned package	package	packages	packages	1	debian versioned package	debianpackagecache	string
4	packages <string> of <rpmdatabase>: package	package	packages	packages	1	package	rpmdatabase	string
4	packages conflicting with <capability> of <rpmdatabase>: package	package conflicting with	packages conflicting with	packages conflicting with	1	package	rpmdatabase	capability
4	packages installing <capability> of <rpmdatabase>: package	package installing	packages installing	packages installing	1	package	rpmdatabase	capability
9	packages of <debianpackagecache>: debian versioned package	package	packages	packages	1	debian versioned package	debianpackagecache	
4	packages of <rpmdatabase>: package	package	packages	packages	1	package	rpmdatabase	
4	packages providing <capability> of <rpmdatabase>: package	package providing	packages providing	packages providing	1	package	rpmdatabase	capability
4	packages requiring <capability> of <rpmdatabase>: package	package requiring	packages requiring	packages requiring	1	package	rpmdatabase	capability
ff	pad of <version>: version	pad	pads	pad	0	version	version	
ff	padded string of <bit set>: string	padded string	padded strings	padded string	0	string	bit set	
10	page fault count of <process>: integer	page fault count	page fault counts	page fault count	0	integer	process	
10	page file usage of <process>: integer	page file usage	page file usages	page file usage	0	integer	process	
10	parallel instance of <task settings>: boolean	parallel instance	parallel instances	parallel instance	0	boolean	task settings	
1f	parameter <string> of <action>: string	parameter	parameters	parameter	0	string	action	string
e0	parameter <string> of <bes action>: string	parameter	parameters	parameter	0	string	bes action	string
1f	parameter <string>: string	parameter	parameters	parameter	0	string		string
e0	parameters of <bes action>: bes action parameter	parameter	parameters	parameters	1	bes action parameter	bes action	
1f	parent folder of <filesystem object>: folder	parent folder	parent folders	parent folder	0	folder	filesystem object	
d	parent folder of <symlink>: folder	parent folder	parent folders	parent folder	0	folder	symlink	
e0	parent group of <bes action>: bes action	parent group	parent groups	parent group	0	bes action	bes action	
10	parent key of <registry key value>: registry key	parent key	parent keys	parent key	0	registry key	registry key value	
10	parent key of <registry key>: registry key	parent key	parent keys	parent key	0	registry key	registry key	
bd	parent node of <xml dom node>: xml dom node	parent node	parent nodes	parent node	0	xml dom node	xml dom node	
ff	parent of <type>: type	parent	parents	parent	0	type	type	
e0	parent relevances of <bes fixlet>: string	parent relevance	parent relevances	parent relevances	1	string	bes fixlet	
ff	parenthesized part <integer> of <regular expression match>: substring	parenthesized part	parenthesized parts	parenthesized part	0	substring	regular expression match	integer
ff	parenthesized parts of <regular expression match>: substring	parenthesized part	parenthesized parts	parenthesized parts	1	substring	regular expression match	
1f	part_number of <dmi memory_device>: string	part_number	part_numbers	part_number	0	string	dmi memory_device	
1f	part_number of <dmi processor_information>: string	part_number	part_numbers	part_number	0	string	dmi processor_information	
1f	partition_row_position of <dmi memory_device_mapped_address>: integer	partition_row_position	partition_row_positions	partition_row_position	0	integer	dmi memory_device_mapped_address	
1f	partition_width of <dmi memory_array_mapped_address>: integer	partition_width	partition_widths	partition_width	0	integer	dmi memory_array_mapped_address	
10	password age of <user>: time interval	password age	password ages	password age	0	time interval	user	
10	password change disabled flag of <user>: boolean	password change disabled flag	password change disabled flags	password change disabled flag	0	boolean	user	
10	password expiration disabled flag of <user>: boolean	password expiration disabled flag	password expiration disabled flags	password expiration disabled flag	0	boolean	user	
10	password expired of <user>: boolean	password expired	passwords expired	password expired	0	boolean	user	
10	password history length of <security database>: integer	password history length	password history lengths	password history length	0	integer	security database	
10	password logon of <task principal>: boolean	password logon	password logons	password logon	0	boolean	task principal	
10	password of <network share>: string	password	passwords	password	0	string	network share	
ff	patch revision of <version>: integer	patch revision	patch revisions	patch revision	0	integer	version	
1f	path <string> of <instance data>: json value	path	paths	path	0	json value	instance data	string
ff	path <string> of <json value>: json value	path	paths	path	0	json value	json value	string
1f	path <string> of <yaml value>: yaml value	path	paths	path	0	yaml value	yaml value	string
10	path of <exec task action>: string	path	paths	path	0	string	exec task action	
1f	path of <execution>: string	path	paths	path	0	string	execution	
d	path of <grub config file>: string	path	paths	path	0	string	grub config file	
d	path of <grub file location>: string	path	paths	path	0	string	grub file location	
10	path of <network share>: string	path	paths	path	0	string	network share	
2	path of <registrynode>: string	path	paths	path	0	string	registrynode	
10	path of <running task>: string	path	paths	path	0	string	running task	
10	path of <scheduled task>: string	path	paths	path	0	string	scheduled task	
10	path of <task folder>: string	path	paths	path	0	string	task folder	
10	pathname of <file shortcut>: string	pathname	pathnames	pathname	0	string	file shortcut	
1f	pathname of <filesystem object>: string	pathname	pathnames	pathname	0	string	filesystem object	
10	pathname of <registry key>: string	pathname	pathnames	pathname	0	string	registry key	
d	pathname of <symlink>: string	pathname	pathnames	pathname	0	string	symlink	
10	peak page file usage of <process>: integer	peak page file usage	peak page file usages	peak page file usage	0	integer	process	
10	peak working set size of <process>: integer	peak working set size	peak working set sizes	peak working set size	0	integer	process	
40	peer flag of <bes peer download>: boolean	peer flag	peer flags	peer flag	0	boolean	bes peer download	
1d	pem encoded certificate of <file>: x509 certificate	pem encoded certificate	pem encoded certificates	pem encoded certificate	0	x509 certificate	file	
1d	pem encoded certificate string of <string>: x509 certificate	pem encoded certificate string	pem encoded certificates string	pem encoded certificate string	0	x509 certificate	string	
e0	pending license update: boolean	pending license update	pending license updates	pending license update	0	boolean		
1f	pending login of <action>: boolean	pending login	pending logins	pending login	0	boolean	action	
1f	pending login: boolean	pending login	pending logins	pending login	0	boolean		
1f	pending of <action>: boolean	pending	pendings	pending	0	boolean	action	
1f	pending restart <string>: boolean	pending restart	pending restarts	pending restart	0	boolean		string
1f	pending restart names: string	pending restart name	pending restart names	pending restart names	1	string		
1f	pending restart of <action>: boolean	pending restart	pending restarts	pending restart	0	boolean	action	
1f	pending restart: boolean	pending restart	pending restarts	pending restart	0	boolean		
d	pending status of <SELinux Boolean>: boolean	pending status	pending statuses	pending status	0	boolean	SELinux Boolean	
1f	pending time of <action>: time	pending time	pending times	pending time	0	time	action	
10	per user policy <security account> of <audit policy subcategory>: audit policy information	per user policy	per user policies	per user policy	0	audit policy information	audit policy subcategory	security account
ff	percent decode <string>: string	percent decode	percent decodes	percent decode	0	string		string
ff	percent encode <binary_string>: string	percent encode	percent encodes	percent encode	0	string		binary_string
ff	percent encode <string>: string	percent encode	percent encodes	percent encode	0	string		string
10	performance counter frequency of <operating system>: hertz	performance counter frequency	performance counter frequencies	performance counter frequency	0	hertz	operating system	
10	performance counter of <operating system>: integer	performance counter	performance counters	performance counter	0	integer	operating system	
1f	perl regex escape of <string>: string	perl regex escape	perl regex escapes	perl regex escape	0	string	string	
1f	perl regexes <string>: regular expression	perl regex	perl regexes	perl regexes	1	regular expression		string
1f	perl regular expressions <string>: regular expression	perl regular expression	perl regular expressions	perl regular expressions	1	regular expression		string
10	permission permission of <network share>: boolean	permission permission	permission permissions	permission permission	0	boolean	network share	
ff	perpetual maintenance of <bes product>: boolean	perpetual maintenance	perpetual maintenances	perpetual maintenance	0	boolean	bes product	
ff	perpetual of <bes product>: boolean	perpetual	perpetuals	perpetual	0	boolean	bes product	
1f	persistent constraint of <action>: integer	persistent constraint	persistent constraints	persistent constraint	0	integer	action	
10	personal bit <operating system suite mask>: boolean	personal bit	personal bits	personal bit	0	boolean		operating system suite mask
10	physical processor count: integer	physical processor count	physical processor counts	physical processor count	0	integer		
2	physical ram: integer	physical ram	physical rams	physical ram	0	integer		
1f	physical_memory_array <integer> of <dmi>: dmi physical_memory_array	physical_memory_array	physical_memory_arrays	physical_memory_array	0	dmi physical_memory_array	dmi	integer
1f	physical_memory_arrays of <dmi>: dmi physical_memory_array	physical_memory_array	physical_memory_arrays	physical_memory_arrays	1	dmi physical_memory_array	dmi	
1f	pid of <process>: integer	pid	pids	pid	0	integer	process	
10	pid of <service>: integer	pid	pids	pid	0	integer	service	
4	pids of <service>: integer	pid	pids	pids	1	integer	service	
2	pinned flag of <route>: boolean	pinned flag	pinned flags	pinned flag	0	boolean	route	
9	pkg versions of <debian base package>: debianpkg version	pkg version	pkg versions	pkg versions	1	debianpkg version	debian base package	
9	pkglibversion of <debianpackagecache>: string	pkglibversion	pkglibversions	pkglibversion	0	string	debianpackagecache	
e0	plain bes fixlet set: bes fixlet set	plain bes fixlet set	plain bes fixlet sets	plain bes fixlet set	0	bes fixlet set		
e0	plain bes fixlets: bes fixlet	plain bes fixlet	plain bes fixlets	plain bes fixlets	1	bes fixlet		
d	platform id of <language>: string	platform id	platform ids	platform id	0	string	language	
10	platform id of <operating system>: integer	platform id	platform ids	platform id	0	integer	operating system	
1f	plugged of <power level>: boolean	plugged	pluggeds	plugged	0	boolean	power level	
1d	plugin portal service: service	plugin portal service	plugin portal services	plugin portal service	0	service		
14	plugin store <string>: plugin store	plugin store	plugin stores	plugin store	0	plugin store		string
e0	plural flag of <bes property result>: boolean	plural flag	plural flags	plural flag	0	boolean	bes property result	
ff	plural name of <property>: string	plural name	plural names	plural name	0	string	property	
1f	point to point of <network adapter interface>: boolean	point to point	point to points	point to point	0	boolean	network adapter interface	
2	point to point of <network adapter>: boolean	point to point	point to points	point to point	0	boolean	network adapter	
1f	point to point of <network ip interface>: boolean	point to point	point to points	point to point	0	boolean	network ip interface	
10	policy change category of <audit policy>: audit policy category	policy change category	policy change categories	policy change category	0	audit policy category	audit policy	
d	policy of <process>: string	policy	policies	policy	0	string	process	
10	port mappings of <internet connection firewall>: port mapping	port mapping	port mappings	port mappings	1	port mapping	internet connection firewall	
1f	port number of <selected server>: integer	port number	port numbers	port number	0	integer	selected server	
d	port of <Xinetd Service>: integer	port	ports	port	0	integer	Xinetd Service	
40	port of <bes idp directory server>: integer	port	ports	port	0	integer	bes idp directory server	
e0	port of <bes ldap directory server>: integer	port	ports	port	0	integer	bes ldap directory server	
10	port of <firewall open port>: integer	port	ports	port	0	integer	firewall open port	
1f	port_connector_information <integer> of <dmi>: dmi port_connector_information	port_connector_information	port_connector_informations	port_connector_information	0	dmi port_connector_information	dmi	integer
1f	port_connector_informations of <dmi>: dmi port_connector_information	port_connector_information	port_connector_informations	port_connector_informations	1	dmi port_connector_information	dmi	
1f	port_type of <dmi port_connector_information>: integer	port_type	port_types	port_type	0	integer	dmi port_connector_information	
1f	portable_battery <integer> of <dmi>: dmi portable_battery	portable_battery	portable_batterys	portable_battery	0	dmi portable_battery	dmi	integer
1f	portable_batterys of <dmi>: dmi portable_battery	portable_battery	portable_batterys	portable_batterys	1	dmi portable_battery	dmi	
ff	position <integer> of <binary_string>: binary position	position	positions	position	0	binary position	binary_string	integer
ff	position <integer> of <string>: string position	position	positions	position	0	string position	string	integer
ff	positions of <binary_string>: binary position	position	positions	positions	1	binary position	binary_string	
ff	positions of <string>: string position	position	positions	positions	1	string position	string	
d	posix capability of <process>: integer	posix capability	posix capabilities	posix capability	0	integer	process	
1f	posix case insensitive regexes <string>: regular expression	posix case insensitive regex	posix case insensitive regexes	posix case insensitive regexes	1	regular expression		string
1f	posix case insensitive regular expressions <string>: regular expression	posix case insensitive regular expression	posix case insensitive regular expressions	posix case insensitive regular expressions	1	regular expression		string
2	posix file <string> of <encoding>: file	posix file	posix files	posix file	0	file	encoding	string
2	posix file <string>: file	posix file	posix files	posix file	0	file		string
2	posix folder <string> of <encoding>: folder	posix folder	posix folders	posix folder	0	folder	encoding	string
2	posix folder <string>: folder	posix folder	posix folders	posix folder	0	folder		string
2	posix item <string>: filesystem object	posix item	posix items	posix item	0	filesystem object		string
2	posix path of <filesystem object>: string	posix path	posix paths	posix path	0	string	filesystem object	
1f	posix regex escape of <string>: string	posix regex escape	posix regex escapes	posix regex escape	0	string	string	
1f	posix regexes <string>: regular expression	posix regex	posix regexes	posix regexes	1	regular expression		string
1f	posix regular expressions <string>: regular expression	posix regular expression	posix regular expressions	posix regular expressions	1	regular expression		string
2	posix relative item <string> of <folder>: filesystem object	posix relative item	posix relative items	posix relative item	0	filesystem object	folder	string
e0	postaction allow cancel flag of <bes action>: boolean	postaction allow cancel flag	postaction allow cancel flags	postaction allow cancel flag	0	boolean	bes action	
e0	postaction force delay of <bes action>: time interval	postaction force delay	postaction force delays	postaction force delay	0	time interval	bes action	
e0	postaction message text of <bes action>: string	postaction message text	postaction message texts	postaction message text	0	string	bes action	
e0	postaction message title of <bes action>: string	postaction message title	postaction message titles	postaction message title	0	string	bes action	
e0	postaction postpone delay of <bes action>: time interval	postaction postpone delay	postaction postpone delays	postaction postpone delay	0	time interval	bes action	
12	power history: power history	power history	power histories	power history	0	power history		
1f	power level: power level	power level	power levels	power level	0	power level		
2	power plane of <registryroot>: registrynode	power plane	power planes	power plane	0	registrynode	registryroot	
1f	power_supply_characteristics of <dmi system_power_supply>: integer	power_supply_characteristics	power_supply_characteristicss	power_supply_characteristics	0	integer	dmi system_power_supply	
1f	power_supply_state of <dmi system_enclosure_or_chassis>: integer	power_supply_state	power_supply_states	power_supply_state	0	integer	dmi system_enclosure_or_chassis	
1f	power_unit_group of <dmi system_power_supply>: integer	power_unit_group	power_unit_groups	power_unit_group	0	integer	dmi system_power_supply	
2	powerpc: boolean	powerpc	powerpcs	powerpc	0	boolean		
1f	ppid of <process>: integer	ppid	ppids	ppid	0	integer	process	
2	prcloning flag of <route>: boolean	prcloning flag	prcloning flags	prcloning flag	0	boolean	route	
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
2	preference <string>: preference	preference	preferences	preference	0	preference		string
2	preferences folder of <domain>: folder	preferences folder	preferences folders	preferences folder	0	folder	domain	
2	preferences folder: folder	preferences folder	preferences folders	preferences folder	0	folder		
e0	preferred bes language: string	preferred bes language	preferred bes languages	preferred bes language	0	string		
40	prefetch flag of <bes peer download>: boolean	prefetch flag	prefetch flags	prefetch flag	0	boolean	bes peer download	
1f	previous line of <file line>: file line	previous line	previous lines	previous line	0	file line	file line	
1f	previous rawline of <file line>: file line	previous rawline	previous rawlines	previous rawline	0	file line	file line	
bd	previous sibling of <xml dom node>: xml dom node	previous sibling	previous siblings	previous sibling	0	xml dom node	xml dom node	
d	previous value of <runlevel>: string	previous value	previous values	previous value	0	string	runlevel	
d	primary codeset of <language>: string	primary codeset	primary codesets	primary codeset	0	string	language	
d	primary country of <language>: string	primary country	primary countries	primary country	0	string	language	
12	primary group id of <user>: integer	primary group id	primary group ids	primary group id	0	integer	user	
2	primary internet connection: network ip interface	primary internet connection	primary internet connections	primary internet connection	0	network ip interface		
1d	primary language of <language>: primary language	primary language	primary languages	primary language	0	primary language	language	
10	primary wins server of <network adapter>: ipv4 address	primary wins server	primary wins servers	primary wins server	0	ipv4 address	network adapter	
10	principal of <task definition>: task principal	principal	principals	principal	0	task principal	task definition	
10	print operator flag of <user>: boolean	print operator flag	print operator flags	print operator flag	0	boolean	user	
2	printer descriptions folder of <domain>: folder	printer descriptions folder	printer descriptions folders	printer descriptions folder	0	folder	domain	
2	printer descriptions folder: folder	printer descriptions folder	printer descriptions folders	printer descriptions folder	0	folder		
2	printer drivers folder of <domain>: folder	printer drivers folder	printer drivers folders	printer drivers folder	0	folder	domain	
2	printer drivers folder: folder	printer drivers folder	printer drivers folders	printer drivers folder	0	folder		
2	printers folder of <domain>: folder	printers folder	printers folders	printers folder	0	folder	domain	
2	printers folder: folder	printers folder	printers folders	printers folder	0	folder		
2	printmonitor documents folder of <domain>: folder	printmonitor documents folder	printmonitor documents folders	printmonitor documents folder	0	folder	domain	
2	printmonitor documents folder: folder	printmonitor documents folder	printmonitor documents folders	printmonitor documents folder	0	folder		
40	priority of <bes idp directory server>: integer	priority	priorities	priority	0	integer	bes idp directory server	
e0	priority of <bes ldap directory server>: integer	priority	priorities	priority	0	integer	bes ldap directory server	
d	priority of <process>: integer	priority	priorities	priority	0	integer	process	
1f	priority of <selected server>: integer	priority	priorities	priority	0	integer	selected server	
10	priority of <task settings>: integer	priority	priorities	priority	0	integer	task settings	
10	private firewall profile type: firewall profile type	private firewall profile type	private firewall profile types	private firewall profile type	0	firewall profile type		
e0	private flag of <bes filter>: boolean	private flag	private flags	private flag	0	boolean	bes filter	
40	private flag of <bes tag>: boolean	private flag	private flags	private flag	0	boolean	bes tag	
e0	private flag of <bes wizard variable>: boolean	private flag	private flags	private flag	0	boolean	bes wizard variable	
2	private framework folder of <domain>: folder	private framework folder	private framework folders	private framework folder	0	folder	domain	
2	private framework folder: folder	private framework folder	private framework folders	private framework folder	0	folder		
1f	private ip of <cloud provider>: string	private ip	private ips	private ip	0	string	cloud provider	
10	private profile of <firewall policy>: firewall profile	private profile	private profiles	private profile	0	firewall profile	firewall policy	
e0	private variable <( string, string )>: string	private variable	private variables	private variable	0	string		( string, string )
e0	private variable <string> of <bes wizard>: string	private variable	private variables	private variable	0	string	bes wizard	string
e0	private variables of <bes wizard>: bes wizard variable	private variable	private variables	private variables	1	bes wizard variable	bes wizard	
10	privilege use category of <audit policy>: audit policy category	privilege use category	privilege use categories	privilege use category	0	audit policy category	audit policy	
10	privileges of <security account>: string	privilege	privileges	privileges	1	string	security account	
10	problem id of <active device>: integer	problem id	problem ids	problem id	0	integer	active device	
1f	process <integer>: process	process	processes	process	0	process		integer
d	process id of <logged on user>: integer	process id	process ids	process id	0	integer	logged on user	
1f	process id of <process>: integer	process id	process ids	process id	0	integer	process	
2	process identifier of <os log entry log>: integer	process identifier	process identifiers	process identifier	0	integer	os log entry log	
10	process image file name of <firewall authorized application>: string	process image file name	process image file names	process image file name	0	string	firewall authorized application	
2	process name of <os log entry log>: string	process name	process names	process name	0	string	os log entry log	
1f	process of <socket>: process	process	processes	process	0	process	socket	
2	process owner of <client>: client process owner	process owner	process owners	process owner	0	client process owner	client	
1f	processes <string>: process	process	processes	processes	1	process		string
1f	processes: process	process	processes	processes	1	process		
1f	processor <integer>: processor	processor	processors	processor	0	processor		integer
1f	processor_characteristics of <dmi processor_information>: integer	processor_characteristics	processor_characteristicss	processor_characteristics	0	integer	dmi processor_information	
1f	processor_family of <dmi processor_information>: integer	processor_family	processor_familys	processor_family	0	integer	dmi processor_information	
1f	processor_family_2 of <dmi processor_information>: integer	processor_family_2	processor_family_2s	processor_family_2	0	integer	dmi processor_information	
1f	processor_id of <dmi processor_information>: integer	processor_id	processor_ids	processor_id	0	integer	dmi processor_information	
1f	processor_information <integer> of <dmi>: dmi processor_information	processor_information	processor_informations	processor_information	0	dmi processor_information	dmi	integer
1f	processor_informations of <dmi>: dmi processor_information	processor_information	processor_informations	processor_informations	1	dmi processor_information	dmi	
1f	processor_manufacturer of <dmi processor_information>: string	processor_manufacturer	processor_manufacturers	processor_manufacturer	0	string	dmi processor_information	
1f	processor_type of <dmi processor_information>: integer	processor_type	processor_types	processor_type	0	integer	dmi processor_information	
1f	processor_upgrade of <dmi processor_information>: integer	processor_upgrade	processor_upgrades	processor_upgrade	0	integer	dmi processor_information	
1f	processor_version of <dmi processor_information>: string	processor_version	processor_versions	processor_version	0	string	dmi processor_information	
1f	processors: processor	processor	processors	processors	1	processor		
10	product info numeric of <operating system>: integer	product info numeric	product info numerics	product info numeric	0	integer	operating system	
1f	product info string of <operating system>: string	product info string	product info strings	product info string	0	string	operating system	
1f	product of <dmi base_board_information>: string	product	products	product	0	string	dmi base_board_information	
2	product of <scsidevice>: string	product	products	product	0	string	scsidevice	
10	product type of <operating system>: operating system product type	product type	product types	product type	0	operating system product type	operating system	
10	product version of <file>: version	product version	product versions	product version	0	version	file	
1f	product_name of <dmi system_information>: string	product_name	product_names	product_name	0	string	dmi system_information	
ff	products of <floating point>: floating point	product	products	products	1	floating point	floating point	
ff	products of <integer>: integer	product	products	products	1	integer	integer	
ff	products of <license>: bes product	product	products	products	1	bes product	license	
10	profile <firewall profile type> of <firewall rule>: boolean	profile	profiles	profile	0	boolean	firewall rule	firewall profile type
10	profile folder of <user>: string	profile folder	profile folders	profile folder	0	string	user	
10	profile of <site>: site profile	profile	profiles	profile	0	site profile	site	
10	profile types of <firewall>: firewall profile type	profile type	profile types	profile types	1	firewall profile type	firewall	
10	profiles of <firewall policy>: firewall profile	profile	profiles	profiles	1	firewall profile	firewall policy	
10	program files folder: folder	program files folder	program files folders	program files folder	0	folder		
10	program files x32 folder: folder	program files x32 folder	program files x32 folders	program files x32 folder	0	folder		
10	program files x64 folder: folder	program files x64 folder	program files x64 folders	program files x64 folder	0	folder		
ff	properties <string> of <type>: property	property	properties	properties	1	property	type	string
ff	properties <string>: property	property	properties	properties	1	property		string
e0	properties of <bes fixlet>: bes property	property	properties	properties	1	bes property	bes fixlet	
ff	properties of <type>: property	property	properties	properties	1	property	type	
10	properties of <wmi object>: wmi select	property	properties	properties	1	wmi select	wmi object	
ff	properties returning <type> of <type>: property	property returning	properties returning	properties returning	1	property	type	type
ff	properties returning <type>: property	property returning	properties returning	properties returning	1	property		type
ff	properties: property	property	properties	properties	1	property		
e0	property <integer> of <bes fixlet>: bes property	property	properties	property	0	bes property	bes fixlet	integer
10	property <string> of <wmi object>: wmi select	property	properties	property	0	wmi select	wmi object	string
1f	property duration of <evaluation cycle>: time interval	property duration	property durations	property duration	0	time interval	evaluation cycle	
e0	property of <bes property result>: bes property	property	properties	property	0	bes property	bes property result	
1f	property percent of <evaluation cycle>: floating point	property percent	property percents	property percent	0	floating point	evaluation cycle	
e0	property results of <bes computer>: bes property result	property result	property results	property results	1	bes property result	bes computer	
2	proto1 flag of <route>: boolean	proto1 flag	proto1 flags	proto1 flag	0	boolean	route	
2	proto2 flag of <route>: boolean	proto2 flag	proto2 flags	proto2 flag	0	boolean	route	
2	proto3 flag of <route>: boolean	proto3 flag	proto3 flags	proto3 flag	0	boolean	route	
d	protocol of <Xinetd Service>: string	protocol	protocols	protocol	0	string	Xinetd Service	
10	protocol of <firewall open port>: internet protocol	protocol	protocols	protocol	0	internet protocol	firewall open port	
10	protocol of <firewall rule>: internet protocol	protocol	protocols	protocol	0	internet protocol	firewall rule	
10	protocol of <port mapping>: string	protocol	protocols	protocol	0	string	port mapping	
10	protocol type of <wifi network>: string	protocol type	protocol types	protocol type	0	string	wifi network	
4	provides of <package>: capability	provide	provides	provides	1	capability	package	
1f	proxied of <hardware>: boolean	proxied	proxieds	proxied	0	boolean	hardware	
1d	proxy agent service: service	proxy agent service	proxy agent services	proxy agent service	0	service		
2	proxy flag of <route>: boolean	proxy flag	proxy flags	proxy flag	0	boolean	route	
10	public firewall profile type: firewall profile type	public firewall profile type	public firewall profile types	public firewall profile type	0	firewall profile type		
40	public flag of <bes tag>: boolean	public flag	public flags	public flag	0	boolean	bes tag	
ff	public key algorithm of <x509 certificate>: string	public key algorithm	public key algorithms	public key algorithm	0	string	x509 certificate	
10	public profile of <firewall policy>: firewall profile	public profile	public profiles	public profile	0	firewall profile	firewall policy	
10	publisher id of <winrt package id>: string	publisher id	publisher ids	publisher id	0	string	winrt package id	
10	publisher of <winrt package id>: string	publisher	publishers	publisher	0	string	winrt package id	
ff	q <string> of <html>: html	q	qs	q	0	html	html	string
ff	q <string> of <string>: html	q	qs	q	0	html	string	string
ff	q of <html>: html	q	qs	q	0	html	html	
ff	q of <string>: html	q	qs	q	0	html	string	
10	query value permission of <access control entry>: boolean	query value permission	query value permissions	query value permission	0	boolean	access control entry	
10	queue instance of <task settings>: boolean	queue instance	queue instances	queue instance	0	boolean	task settings	
10	queued state of <running task>: boolean	queued state	queued states	queued state	0	boolean	running task	
10	queued state of <scheduled task>: boolean	queued state	queued states	queued state	0	boolean	scheduled task	
2	quickdraw version: version	quickdraw version	quickdraw versions	quickdraw version	0	version		
2	quicktime folder of <domain>: folder	quicktime folder	quicktime folders	quicktime folder	0	folder	domain	
2	quicktime folder: folder	quicktime folder	quicktime folders	quicktime folder	0	folder		
1f	quiet mode duration of <evaluation cycle>: time interval	quiet mode duration	quiet mode durations	quiet mode duration	0	time interval	evaluation cycle	
1f	quiet mode percent of <evaluation cycle>: floating point	quiet mode percent	quiet mode percents	quiet mode percent	0	floating point	evaluation cycle	
d	quiet of <grub bootable image>: boolean	quiet	quiets	quiet	0	boolean	grub bootable image	
10	quota nonpaged pool usage of <process>: integer	quota nonpaged pool usage	quota nonpaged pool usages	quota nonpaged pool usage	0	integer	process	
10	quota paged pool usage of <process>: integer	quota paged pool usage	quota paged pool usages	quota paged pool usage	0	integer	process	
10	quota peak nonpaged pool usage of <process>: integer	quota peak nonpaged pool usage	quota peak nonpaged pool usages	quota peak nonpaged pool usage	0	integer	process	
10	quota peak paged pool usage of <process>: integer	quota peak paged pool usage	quota peak paged pool usages	quota peak paged pool usage	0	integer	process	
1f	ram: ram	ram	rams	ram	0	ram		
1f	random access memory: ram	random access memory	random access memories	random access memory	0	ram		
10	random delay of <daily task trigger>: time interval	random delay	random delays	random delay	0	time interval	daily task trigger	
10	random delay of <monthly task trigger>: time interval	random delay	random delays	random delay	0	time interval	monthly task trigger	
10	random delay of <monthlydow task trigger>: time interval	random delay	random delays	random delay	0	time interval	monthlydow task trigger	
10	random delay of <time task trigger>: time interval	random delay	random delays	random delay	0	time interval	time task trigger	
10	random delay of <weekly task trigger>: time interval	random delay	random delays	random delay	0	time interval	weekly task trigger	
ff	random floating point: floating point	random floating point	random floating points	random floating point	0	floating point		
ff	random integer of <integer>: integer	random integer	random integers	random integer	0	integer	integer	
ff	random integer: integer	random integer	random integers	random integer	0	integer		
e0	range <time range> of <statistic range>: statistic range	range	ranges	range	0	statistic range	statistic range	time range
ff	range after <time> of <time range>: time range	range after	ranges after	range after	0	time range	time range	time
ff	range before <time> of <time range>: time range	range before	ranges before	range before	0	time range	time range	time
12	range of <monitor power interval>: time range	range	ranges	range	0	time range	monitor power interval	
12	range of <system power interval>: time range	range	ranges	range	0	time range	system power interval	
e2	rate <time interval> of <exponential projection>: floating point	rate	rates	rate	0	floating point	exponential projection	time interval
e2	rate of <linear projection>: rate	rate	rates	rate	0	rate	linear projection	
10	raw file version of <file>: version	raw file version	raw file versions	raw file version	0	version	file	
10	raw product version of <file>: version	raw product version	raw product versions	raw product version	0	version	file	
10	raw version block <integer> of <file>: file version block	raw version block	raw version blocks	raw version block	0	file version block	file	integer
10	raw version block <string> of <file>: file version block	raw version block	raw version blocks	raw version block	0	file version block	file	string
10	raw version blocks of <file>: file version block	raw version block	raw version blocks	raw version blocks	1	file version block	file	
10	raw version of <file>: version	raw version	raw versions	raw version	0	version	file	
1f	rawline <integer> of <file>: file line	rawline	rawlines	rawline	0	file line	file	integer
1f	rawline number of <file line>: integer	rawline number	rawline numbers	rawline number	0	integer	file line	
1f	rawlines containing <string> of <file>: file line	rawline containing	rawlines containing	rawlines containing	1	file line	file	string
1f	rawlines of <file>: file line	rawline	rawlines	rawlines	1	file line	file	
1f	rawlines starting with <string> of <file>: file line	rawline starting with	rawlines starting with	rawlines starting with	1	file line	file	string
10	read attributes permission of <access control entry>: boolean	read attributes permission	read attributes permissions	read attributes permission	0	boolean	access control entry	
10	read control permission of <access control entry>: boolean	read control permission	read control permissions	read control permission	0	boolean	access control entry	
10	read extended attributes permission of <access control entry>: boolean	read extended attributes permission	read extended attributes permissions	read extended attributes permission	0	boolean	access control entry	
d	read of <mode_mask>: boolean	read	reads	read	0	boolean	mode_mask	
10	read permission of <access control entry>: boolean	read permission	read permissions	read permission	0	boolean	access control entry	
10	read permission of <network share>: boolean	read permission	read permissions	read permission	0	boolean	network share	
e0	reader set of <bes site>: bes user set	reader set	reader sets	reader set	0	bes user set	bes site	
e0	readers of <bes site>: bes user	reader	readers	readers	1	bes user	bes site	
10	readonly of <filesystem object>: boolean	readonly	readonlys	readonly	0	boolean	filesystem object	
10	ready state of <running task>: boolean	ready state	ready states	ready state	0	boolean	running task	
10	ready state of <scheduled task>: boolean	ready state	ready states	ready state	0	boolean	scheduled task	
2	real <integer> of <array>: floating point	real	reals	real	0	floating point	array	integer
2	real <string> of <dictionary>: floating point	real	reals	real	0	floating point	dictionary	string
2	real of <osxvalue>: floating point	real	reals	real	0	floating point	osxvalue	
10	realtime priority: priority class	realtime priority	realtime priorities	realtime priority	0	priority class		
e0	reapplication interval of <bes action>: time interval	reapplication interval	reapplication intervals	reapplication interval	0	time interval	bes action	
e0	reapplication limit of <bes action>: integer	reapplication limit	reapplication limits	reapplication limit	0	integer	bes action	
e0	reapply flag of <bes action>: boolean	reapply flag	reapply flags	reapply flag	0	boolean	bes action	
2	receipts folder of <domain>: folder	receipts folder	receipts folders	receipts folder	0	folder	domain	
2	receipts folder: folder	receipts folder	receipts folders	receipts folder	0	folder		
1f	recent application <string>: application	recent application	recent applications	recent application	0	application		string
1f	recent applications: application	recent application	recent applications	recent applications	1	application		
10	record <integer> of <event log>: event log record	record	records	record	0	event log record	event log	integer
10	record count of <event log>: integer	record count	record counts	record count	0	integer	event log	
10	record number of <event log record>: integer	record number	record numbers	record number	0	integer	event log record	
10	records of <event log>: event log record	record	records	records	1	event log record	event log	
10	reference attribute of <metabase value>: boolean	reference attribute	reference attributes	reference attribute	0	boolean	metabase value	
2	reference of <route>: integer	reference	references	reference	0	integer	route	
1f	reference_designation of <dmi onboard_devices_extended_information>: integer	reference_designation	reference_designations	reference_designation	0	integer	dmi onboard_devices_extended_information	
12	regapp <string>: application	regapp	regapps	regapp	0	application		string
12	regapps: application	regapp	regapps	regapps	1	application		
ff	regex escape of <string>: string	regex escape	regex escapes	regex escape	0	string	string	
ff	regexes <string>: regular expression	regex	regexes	regexes	1	regular expression		string
1f	region of <cloud provider>: string	region	regions	region	0	string	cloud provider	
ff	registrar number of <license>: integer	registrar number	registrar numbers	registrar number	0	integer	license	
1f	registration address of <client>: ipv4or6 address	registration address	registration addresses	registration address	0	ipv4or6 address	client	
1f	registration cidr address of <client>: string	registration cidr address	registration cidr addresses	registration cidr address	0	string	client	
10	registration info of <task definition>: task registration info	registration info	registration infos	registration info	0	task registration info	task definition	
1f	registration mac address of <client>: string	registration mac address	registration mac addresses	registration mac address	0	string	client	
1f	registration server: registration server	registration server	registration servers	registration server	0	registration server		
1f	registration subnet address of <client>: ipv4or6 address	registration subnet address	registration subnet addresses	registration subnet address	0	ipv4or6 address	client	
10	registration task trigger type: task trigger type	registration task trigger type	registration task trigger types	registration task trigger type	0	task trigger type		
2	registry: dummy type	registry	registries	registry	0	dummy type		
10	registry: registry	registry	registries	registry	0	registry		
ff	regular expressions <string>: regular expression	regular expression	regular expressions	regular expressions	1	regular expression		string
f	reject flag of <route>: boolean	reject flag	reject flags	reject flag	0	boolean	route	
4	relation of <capability>: string	relation	relations	relation	0	string	capability	
2	relative file <string> of <folder>: file	relative file	relative files	relative file	0	file	folder	string
2	relative folder <binary_string> of <folder>: folder	relative folder	relative folders	relative folder	0	folder	folder	binary_string
2	relative folder <string> of <folder>: folder	relative folder	relative folders	relative folder	0	folder	folder	string
2	relative hfs file <string> of <folder>: file	relative hfs file	relative hfs files	relative hfs file	0	file	folder	string
2	relative hfs folder <string> of <folder>: folder	relative hfs folder	relative hfs folders	relative hfs folder	0	folder	folder	string
2	relative item <string> of <folder>: filesystem object	relative item	relative items	relative item	0	filesystem object	folder	string
2	relative posix file <string> of <folder>: file	relative posix file	relative posix files	relative posix file	0	file	folder	string
2	relative posix folder <string> of <folder>: folder	relative posix folder	relative posix folders	relative posix folder	0	folder	folder	string
ff	relative significance place <integer> of <floating point>: floating point	relative significance place	relative significance places	relative significance place	0	floating point	floating point	integer
ff	relative significance place of <floating point>: floating point	relative significance place	relative significance places	relative significance place	0	floating point	floating point	
e0	relay distance of <bes computer>: integer	relay distance	relay distances	relay distance	0	integer	bes computer	
e0	relay hostname of <bes computer>: string	relay hostname	relay hostnames	relay hostname	0	string	bes computer	
40	relay of <bes peer download>: string	relay	relays	relay	0	string	bes peer download	
1f	relay select duration of <evaluation cycle>: time interval	relay select duration	relay select durations	relay select duration	0	time interval	evaluation cycle	
1f	relay select percent of <evaluation cycle>: floating point	relay select percent	relay select percents	relay select percent	0	floating point	evaluation cycle	
e0	relay selection method of <bes computer>: string	relay selection method	relay selection methods	relay selection method	0	string	bes computer	
e0	relay server flag of <bes computer>: boolean	relay server flag	relay server flags	relay server flag	0	boolean	bes computer	
e0	relay server of <bes computer>: string	relay server	relay servers	relay server	0	string	bes computer	
2	relay service: nothing	relay service	relay services	relay service	0	nothing		
1d	relay service: service	relay service	relay services	relay service	0	service		
9	release of <debian versioned package>: string	release	releases	release	0	string	debian versioned package	
1d	release of <operating system>: string	release	releases	release	0	string	operating system	
2	release of <operating system>: version	release	releases	release	0	version	operating system	
4	release of <rpm package version record>: rpm package release	release	releases	release	0	rpm package release	rpm package version record	
4	release of <short rpm package version record>: rpm package release	release	releases	release	0	rpm package release	short rpm package version record	
12	releaseid of <operating system>: string	releaseid	releaseids	releaseid	0	string	operating system	
e0	relevance clauses of <bes fixlet>: string	relevance clause	relevance clauses	relevance clauses	1	string	bes fixlet	
1f	relevance duration of <evaluation cycle>: time interval	relevance duration	relevance durations	relevance duration	0	time interval	evaluation cycle	
e0	relevance of <bes baseline component>: string	relevance	relevances	relevance	0	string	bes baseline component	
e0	relevance of <bes fixlet>: string	relevance	relevances	relevance	0	string	bes fixlet	
1f	relevance of <fixlet>: boolean	relevance	relevances	relevance	0	boolean	fixlet	
1f	relevance percent of <evaluation cycle>: floating point	relevance percent	relevance percents	relevance percent	0	floating point	evaluation cycle	
e0	relevant <( bes computer, bes fixlet )>: boolean	relevant	relevants	relevant	0	boolean		( bes computer, bes fixlet )
e0	relevant <( bes fixlet, bes computer )>: boolean	relevant	relevants	relevant	0	boolean		( bes fixlet, bes computer )
e0	relevant <bes computer> of <bes fixlet>: boolean	relevant	relevants	relevant	0	boolean	bes fixlet	bes computer
e0	relevant <bes fixlet> of <bes computer>: boolean	relevant	relevants	relevant	0	boolean	bes computer	bes fixlet
40	relevant fixlet count of <bes computer>: integer	relevant fixlet count	relevant fixlet counts	relevant fixlet count	0	integer	bes computer	
e0	relevant fixlet set of <bes computer>: bes fixlet set	relevant fixlet set	relevant fixlet sets	relevant fixlet set	0	bes fixlet set	bes computer	
e0	relevant fixlets of <bes computer>: bes fixlet	relevant fixlet	relevant fixlets	relevant fixlets	1	bes fixlet	bes computer	
1f	relevant fixlets of <site>: fixlet	relevant fixlet	relevant fixlets	relevant fixlets	1	fixlet	site	
e0	relevant flag of <bes fixlet result>: boolean	relevant flag	relevant flags	relevant flag	0	boolean	bes fixlet result	
1f	relevant offer actions of <site>: action	relevant offer action	relevant offer actions	relevant offer actions	1	action	site	
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
1f	remote address of <socket>: ipv4or6 address	remote address	remote addresses	remote address	0	ipv4or6 address	socket	
10	remote addresses of <firewall authorized application>: string	remote addresses	remote addresseses	remote addresses	0	string	firewall authorized application	
10	remote addresses of <firewall open port>: string	remote addresses	remote addresseses	remote addresses	0	string	firewall open port	
10	remote addresses of <firewall service>: string	remote addresses	remote addresseses	remote addresses	0	string	firewall service	
10	remote addresses string of <firewall rule>: string	remote addresses string	remote addresses strings	remote addresses string	0	string	firewall rule	
10	remote admin settings of <firewall profile>: firewall remote admin settings	remote admin settings	remote admin settingses	remote admin settings	0	firewall remote admin settings	firewall profile	
10	remote connect of <session state change task trigger>: boolean	remote connect	remote connects	remote connect	0	boolean	session state change task trigger	
10	remote desktop firewall service type: firewall service type	remote desktop firewall service type	remote desktop firewall service types	remote desktop firewall service type	0	firewall service type		
10	remote disconnect of <session state change task trigger>: boolean	remote disconnect	remote disconnects	remote disconnect	0	boolean	session state change task trigger	
10	remote interactive logon group: security account	remote interactive logon group	remote interactive logon groups	remote interactive logon group	0	security account		
1f	remote of <logged on user>: boolean	remote	remotes	remote	0	boolean	logged on user	
1f	remote port of <socket>: integer	remote port	remote ports	remote port	0	integer	socket	
10	remote ports string of <firewall rule>: string	remote ports string	remote ports strings	remote ports string	0	string	firewall rule	
10	repetition of <task trigger>: task repetition pattern	repetition	repetitions	repetition	0	task repetition pattern	task trigger	
10	replyto of <email task action>: string	replyto	replytos	replyto	0	string	email task action	
1f	report character set of <client>: string	report character set	report character sets	report character set	0	string	client	
1f	report duration of <evaluation cycle>: time interval	report duration	report durations	report duration	0	time interval	evaluation cycle	
1f	report percent of <evaluation cycle>: floating point	report percent	report percents	report percent	0	floating point	evaluation cycle	
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
4	requires of <package>: capability	require	requires	requires	1	capability	package	
e0	reserved flag of <bes property>: boolean	reserved flag	reserved flags	reserved flag	0	boolean	bes property	
1f	reserved of <dmi bios_language_information>: binary_string	reserved	reserveds	reserved	0	binary_string	dmi bios_language_information	
1f	reserved of <dmi system_boot_information>: binary_string	reserved	reserveds	reserved	0	binary_string	dmi system_boot_information	
1f	reset_count of <dmi system_reset>: integer	reset_count	reset_counts	reset_count	0	integer	dmi system_reset	
1f	reset_limit of <dmi system_reset>: integer	reset_limit	reset_limits	reset_limit	0	integer	dmi system_reset	
1f	resolution of <dmi electrical_current_probe>: integer	resolution	resolutions	resolution	0	integer	dmi electrical_current_probe	
1f	resolution of <dmi temperature_probe>: integer	resolution	resolutions	resolution	0	integer	dmi temperature_probe	
1f	resolution of <dmi voltage_probe>: integer	resolution	resolutions	resolution	0	integer	dmi voltage_probe	
2	resource fork of <file>: resfork	resource fork	resource forks	resource fork	0	resfork	file	
10	restart count of <task settings>: integer	restart count	restart counts	restart count	0	integer	task settings	
e0	restart flag of <bes action>: boolean	restart flag	restart flags	restart flag	0	boolean	bes action	
10	restart interval of <task settings>: time interval	restart interval	restart intervals	restart interval	0	time interval	task settings	
10	restart on idle of <task idle settings>: boolean	restart on idle	restart on idles	restart on idle	0	boolean	task idle settings	
e0	restartandshutdown actionscript privilege allowboth flag of <bes user>: boolean	restartandshutdown actionscript privilege allowboth flag	restartandshutdown actionscript privilege allowboth flags	restartandshutdown actionscript privilege allowboth flag	0	boolean	bes user	
e0	restartandshutdown actionscript privilege allowrestartonly flag of <bes user>: boolean	restartandshutdown actionscript privilege allowrestartonly flag	restartandshutdown actionscript privilege allowrestartonly flags	restartandshutdown actionscript privilege allowrestartonly flag	0	boolean	bes user	
e0	restartandshutdown actionscript privilege none flag of <bes user>: boolean	restartandshutdown actionscript privilege none flag	restartandshutdown actionscript privilege none flags	restartandshutdown actionscript privilege none flag	0	boolean	bes user	
e0	restartandshutdown postaction privilege allowboth flag of <bes user>: boolean	restartandshutdown postaction privilege allowboth flag	restartandshutdown postaction privilege allowboth flags	restartandshutdown postaction privilege allowboth flag	0	boolean	bes user	
e0	restartandshutdown postaction privilege allowrestartonly flag of <bes user>: boolean	restartandshutdown postaction privilege allowrestartonly flag	restartandshutdown postaction privilege allowrestartonly flags	restartandshutdown postaction privilege allowrestartonly flag	0	boolean	bes user	
e0	restartandshutdown postaction privilege none flag of <bes user>: boolean	restartandshutdown postaction privilege none flag	restartandshutdown postaction privilege none flags	restartandshutdown postaction privilege none flag	0	boolean	bes user	
1f	restricted site: restricted site	restricted site	restricted sites	restricted site	0	restricted site		
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
9	reverse dependencies of <debian versioned package>: debianpkg reverse dependencies	reverse dependency	reverse dependencies	reverse dependencies	1	debianpkg reverse dependencies	debian versioned package	
9	revision of <debian package version>: debian package version revision	revision	revisions	revision	0	debian package version revision	debian package version	
2	revision of <scsidevice>: string	revision	revisions	revision	0	string	scsidevice	
1f	revision_level of <dmi system_power_supply>: string	revision_level	revision_levels	revision_level	0	string	dmi system_power_supply	
ff	right operand type of <binary operator>: type	right operand type	right operand types	right operand type	0	type	binary operator	
ff	right shift <integer> of <bit set>: bit set	right shift	right shifts	right shift	0	bit set	bit set	integer
e0	role set of <bes user>: bes role set	role set	role sets	role set	0	bes role set	bes user	
e0	roles of <bes user>: bes role	role	roles	roles	1	bes role	bes user	
2	rom version: version	rom version	rom versions	rom version	0	version		
10	root folder of <drive>: folder	root folder	root folders	root folder	0	folder	drive	
d	root folder: folder	root folder	root folders	root folder	0	folder		
d	root of <grub bootable image>: grub device	root	roots	root	0	grub device	grub bootable image	
e0	root server flag of <bes computer>: boolean	root server flag	root server flags	root server flag	0	boolean	bes computer	
e0	root server of <bes computer>: string	root server	root servers	root server	0	string	bes computer	
1f	root server: root server	root server	root servers	root server	0	root server		
d	rootnoverify of <grub bootable image>: grub device	rootnoverify	rootnoverifys	rootnoverify	0	grub device	grub bootable image	
ff	rope <string>: rope	rope	ropes	rope	0	rope		string
2	router flag of <route>: boolean	router flag	router flags	router flag	0	boolean	route	
f	routes of <routing table>: route	route	routes	routes	1	route	routing table	
f	routing table: routing table	routing table	routing tables	routing table	0	routing table		
1f	rows of <sqlite statement>: sqlite row	row	rows	rows	1	sqlite row	sqlite statement	
4	rpm <string>: rpmdatabase	rpm	rpms	rpm	0	rpmdatabase		string
4	rpm package release <rpm package release>: rpm package release	rpm package release	rpm package releases	rpm package release	0	rpm package release		rpm package release
4	rpm package release <string>: rpm package release	rpm package release	rpm package releases	rpm package release	0	rpm package release		string
4	rpm package version <rpm package version>: rpm package version	rpm package version	rpm package versions	rpm package version	0	rpm package version		rpm package version
4	rpm package version <string>: rpm package version	rpm package version	rpm package versions	rpm package version	0	rpm package version		string
4	rpm package version record <rpm package version record>: rpm package version record	rpm package version record	rpm package version records	rpm package version record	0	rpm package version record		rpm package version record
4	rpm package version record <short rpm package version record>: rpm package version record	rpm package version record	rpm package version records	rpm package version record	0	rpm package version record		short rpm package version record
4	rpm package version record <string>: rpm package version record	rpm package version record	rpm package version records	rpm package version record	0	rpm package version record		string
4	rpm version record of <package>: rpm package version record	rpm version record	rpm version records	rpm version record	0	rpm package version record	package	
4	rpm: rpmdatabase	rpm	rpms	rpm	0	rpmdatabase		
10	rsop computer wmi: wmi	rsop computer wmi	rsop computer wmis	rsop computer wmi	0	wmi		
10	rsop user wmi <security identifier>: wmi	rsop user wmi	rsop user wmis	rsop user wmi	0	wmi		security identifier
12	rssi of <wifi network>: integer	rssi	rssis	rssi	0	integer	wifi network	
1f	rtt of <socket>: time interval	rtt	rtts	rtt	0	time interval	socket	
10	rule group currently enabled <string> of <firewall>: boolean	rule group currently enabled	rule group currently enableds	rule group currently enabled	0	boolean	firewall	string
10	rule group enabled <string> of <firewall profile>: boolean	rule group enabled	rule group enableds	rule group enabled	0	boolean	firewall profile	string
10	rules of <firewall service restriction>: firewall rule	rule	rules	rules	1	firewall rule	firewall service restriction	
12	rules of <firewall>: firewall rule	rule	rules	rules	1	firewall rule	firewall	
10	run on fifth week in month of <monthlydow task trigger>: boolean	run on fifth week in month	run on fifth week in months	run on fifth week in month	0	boolean	monthlydow task trigger	
10	run on first week in month of <monthlydow task trigger>: boolean	run on first week in month	run on first week in months	run on first week in month	0	boolean	monthlydow task trigger	
10	run on fourth week in month of <monthlydow task trigger>: boolean	run on fourth week in month	run on fourth week in months	run on fourth week in month	0	boolean	monthlydow task trigger	
10	run on last day in month of <monthly task trigger>: boolean	run on last day in month	run on last day in months	run on last day in month	0	boolean	monthly task trigger	
10	run on last week in month of <monthlydow task trigger>: boolean	run on last week in month	run on last week in months	run on last week in month	0	boolean	monthlydow task trigger	
10	run on second week in month of <monthlydow task trigger>: boolean	run on second week in month	run on second week in months	run on second week in month	0	boolean	monthlydow task trigger	
10	run on third week in month of <monthlydow task trigger>: boolean	run on third week in month	run on third week in months	run on third week in month	0	boolean	monthlydow task trigger	
10	run only when idle of <task settings>: boolean	run only when idle	run only when idles	run only when idle	0	boolean	task settings	
10	run only when network available of <task settings>: boolean	run only when network available	run only when network availables	run only when network available	0	boolean	task settings	
d	runlevel: runlevel	runlevel	runlevels	runlevel	0	runlevel		
4	runlevels of <service>: string	runlevel	runlevels	runlevels	1	string	service	
1f	running application <string>: application	running application	running applications	running application	0	application		string
1f	running applications: application	running application	running applications	running applications	1	application		
e0	running message text of <bes action>: string	running message text	running message texts	running message text	0	string	bes action	
e0	running message title of <bes action>: string	running message title	running message titles	running message title	0	string	bes action	
1f	running of <application usage summary>: boolean	running	runnings	running	0	boolean	application usage summary	
10	running of <local mssql database>: boolean	running	runnings	running	0	boolean	local mssql database	
1d	running of <service>: boolean	running	runnings	running	0	boolean	service	
1d	running service <string>: service	running service	running services	running service	0	service		string
10	running services: service	running service	running services	running services	1	service		
10	running state of <running task>: boolean	running state	running states	running state	0	boolean	running task	
10	running state of <scheduled task>: boolean	running state	running states	running state	0	boolean	scheduled task	
10	running tasks: running task	running task	running tasks	running tasks	1	running task		
ff	rvu count of <bes product>: integer	rvu count	rvu counts	rvu count	0	integer	bes product	
10	s4u logon of <task principal>: boolean	s4u logon	s4u logons	s4u logon	0	boolean	task principal	
10	sacl of <security descriptor>: system access control list	sacl	sacls	sacl	0	system access control list	security descriptor	
ff	samp <string> of <html>: html	samp	samps	samp	0	html	html	string
ff	samp <string> of <string>: html	samp	samps	samp	0	html	string	string
ff	samp of <html>: html	samp	samps	samp	0	html	html	
ff	samp of <string>: html	samp	samps	samp	0	html	string	
12	sample time of <active directory group>: time	sample time	sample times	sample time	0	time	active directory group	
12	sample time of <active directory local computer>: time	sample time	sample times	sample time	0	time	active directory local computer	
12	sample time of <active directory local user>: time	sample time	sample times	sample time	0	time	active directory local user	
e0	sans id list of <bes fixlet>: string	sans id list	sans id lists	sans id list	0	string	bes fixlet	
ff	saturday: day of week	saturday	saturdays	saturday	0	day of week		
d	savedefault of <grub bootable image>: boolean	savedefault	savedefaults	savedefault	0	boolean	grub bootable image	
1f	sbds_device_chemistry of <dmi portable_battery>: string	sbds_device_chemistry	sbds_device_chemistrys	sbds_device_chemistry	0	string	dmi portable_battery	
1f	sbds_manufacture_date of <dmi portable_battery>: integer	sbds_manufacture_date	sbds_manufacture_dates	sbds_manufacture_date	0	integer	dmi portable_battery	
1f	sbds_serial_number of <dmi portable_battery>: integer	sbds_serial_number	sbds_serial_numbers	sbds_serial_number	0	integer	dmi portable_battery	
1f	sbds_version_number of <dmi portable_battery>: string	sbds_version_number	sbds_version_numbers	sbds_version_number	0	string	dmi portable_battery	
d	schedule class of <process>: string	schedule class	schedule classes	schedule class	0	string	process	
10	scheduled task <string> of <task folder>: scheduled task	scheduled task	scheduled tasks	scheduled task	0	scheduled task	task folder	string
10	scheduled task <string>: scheduled task	scheduled task	scheduled tasks	scheduled task	0	scheduled task		string
10	scheduled tasks of <task folder>: scheduled task	scheduled task	scheduled tasks	scheduled tasks	1	scheduled task	task folder	
10	scheduled tasks: scheduled task	scheduled task	scheduled tasks	scheduled tasks	1	scheduled task		
1f	schema of <sqlite table>: string	schema	schemas	schema	0	string	sqlite table	
e0	scope of <bes client setting>: string	scope	scopes	scope	0	string	bes client setting	
10	scope of <firewall authorized application>: firewall scope	scope	scopes	scope	0	firewall scope	firewall authorized application	
10	scope of <firewall open port>: firewall scope	scope	scopes	scope	0	firewall scope	firewall open port	
10	scope of <firewall service>: firewall scope	scope	scopes	scope	0	firewall scope	firewall service	
10	script flag of <user>: boolean	script flag	script flags	script flag	0	boolean	user	
e0	script of <bes fixlet action>: string	script	scripts	script	0	string	bes fixlet action	
e0	script type of <bes fixlet action>: string	script type	script types	script type	0	string	bes fixlet action	
2	scripting additions folder of <domain>: folder	scripting additions folder	scripting additions folders	scripting additions folder	0	folder	domain	
2	scripting additions folder: folder	scripting additions folder	scripting additions folders	scripting additions folder	0	folder		
2	scsibus <integer>: scsibus	scsibus	scsibuses	scsibus	0	scsibus		integer
2	scsibuses: scsibus	scsibus	scsibuses	scsibuses	1	scsibus		
2	scsidevice <integer> of <scsibus>: scsidevice	scsidevice	scsidevices	scsidevice	0	scsidevice	scsibus	integer
2	scsidevice <integer>: scsidevice	scsidevice	scsidevices	scsidevice	0	scsidevice		integer
2	scsidevices of <scsibus>: scsidevice	scsidevice	scsidevices	scsidevices	1	scsidevice	scsibus	
2	scsidevices: scsidevice	scsidevice	scsidevices	scsidevices	1	scsidevice		
2	searches since boot <string> of <os log store>: os log entry log	search since boot	searches since boot	searches since boot	1	os log entry log	os log store	string
2	searches since days <string> of <os log store>: os log entry log	search since days	searches since days	searches since days	1	os log entry log	os log store	string
ff	seat count state of <license>: string	seat count state	seat count states	seat count state	0	string	license	
ff	seat of <license>: integer	seat	seats	seat	0	integer	license	
ff	second: time interval	second	seconds	second	0	time interval		
ff	second_of_minute of <time of day with time zone>: integer	second_of_minute	seconds_of_minute	second_of_minute	0	integer	time of day with time zone	
ff	second_of_minute of <time of day>: integer	second_of_minute	seconds_of_minute	second_of_minute	0	integer	time of day	
10	secondary wins server of <network adapter>: ipv4 address	secondary wins server	secondary wins servers	secondary wins server	0	ipv4 address	network adapter	
2	seconds to expiration of <route>: integer	seconds to expiration	seconds to expirations	seconds to expiration	0	integer	route	
1f	section <string> of <file>: file section	section	sections	section	0	file section	file	string
9	section of <debian versioned package>: string	section	sections	section	0	string	debian versioned package	
9	section of <debianpkg version>: string	section	sections	section	0	string	debianpkg version	
10	secure attribute of <metabase value>: boolean	secure attribute	secure attributes	secure attribute	0	boolean	metabase value	
e0	secure parameter flag of <bes action>: boolean	secure parameter flag	secure parameter flags	secure parameter flag	0	boolean	bes action	
12	secured of <wifi network>: boolean	secured	secureds	secured	0	boolean	wifi network	
12	secured of <wifi>: boolean	secured	secureds	secured	0	boolean	wifi	
10	security account <string>: security account	security account	security accounts	security account	0	security account		string
10	security database: security database	security database	security databases	security database	0	security database		
10	security descriptor <string>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor		string
10	security descriptor of <file>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	file	
10	security descriptor of <folder>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	folder	
10	security descriptor of <network share>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	network share	
10	security descriptor of <registry key>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	registry key	
10	security descriptor of <scheduled task>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	scheduled task	
10	security descriptor of <service>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	service	
10	security descriptor of <task folder>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	task folder	
10	security descriptor of <task registration info>: security descriptor	security descriptor	security descriptors	security descriptor	0	security descriptor	task registration info	
10	security event log: event log	security event log	security event logs	security event log	0	event log		
1f	security_status of <dmi system_enclosure_or_chassis>: integer	security_status	security_statuss	security_status	0	integer	dmi system_enclosure_or_chassis	
1f	segment_group_number of <dmi onboard_devices_extended_information>: integer	segment_group_number	segment_group_numbers	segment_group_number	0	integer	dmi onboard_devices_extended_information	
1f	segment_group_number of <dmi system_slots>: integer	segment_group_number	segment_group_numbers	segment_group_number	0	integer	dmi system_slots	
10	select objects <string> of <wmi>: wmi object	select object	select objects	select objects	1	wmi object	wmi	string
e0	selected groups string of <bes action>: string	selected groups string	selected groups strings	selected groups string	0	string	bes action	
1f	selected server: selected server	selected server	selected servers	selected server	0	selected server		
10	selects <string> of <wmi>: wmi select	select	selects	selects	1	wmi select	wmi	string
b0	selects <string> of <xml dom node>: xml dom node	select	selects	selects	1	xml dom node	xml dom node	string
d	selinux booleans <string>: SELinux Boolean	selinux boolean	selinux booleans	selinux booleans	1	SELinux Boolean		string
d	selinux booleans: SELinux Boolean	selinux boolean	selinux booleans	selinux booleans	1	SELinux Boolean		
d	selinux context of <process>: string	selinux context	selinux contexts	selinux context	0	string	process	
d	selinux domain of <process>: string	selinux domain	selinux domains	selinux domain	0	string	process	
2	sender of <os log entry log>: string	sender	senders	sender	0	string	os log entry log	
2	sent packet count of <route>: integer	sent packet count	sent packets counts	sent packet count	0	integer	route	
d	sep bug of <processor>: boolean	sep bug	sep bugs	sep bug	0	boolean	processor	
ff	september <integer> of <integer>: date	september	septembers	september	0	date	integer	integer
ff	september <integer>: day of year	september	septembers	september	0	day of year		integer
ff	september of <integer>: month and year	september	septembers	september	0	month and year	integer	
ff	september: month	september	septembers	september	0	month		
ff	serial number of <x509 certificate>: string	serial number	serial numbers	serial number	0	string	x509 certificate	
1f	serial of <hardware>: string	serial	serials	serial	0	string	hardware	
1f	serial_number of <dmi base_board_information>: string	serial_number	serial_numbers	serial_number	0	string	dmi base_board_information	
1f	serial_number of <dmi memory_device>: string	serial_number	serial_numbers	serial_number	0	string	dmi memory_device	
1f	serial_number of <dmi portable_battery>: string	serial_number	serial_numbers	serial_number	0	string	dmi portable_battery	
1f	serial_number of <dmi processor_information>: string	serial_number	serial_numbers	serial_number	0	string	dmi processor_information	
1f	serial_number of <dmi system_enclosure_or_chassis>: string	serial_number	serial_numbers	serial_number	0	string	dmi system_enclosure_or_chassis	
1f	serial_number of <dmi system_information>: string	serial_number	serial_numbers	serial_number	0	string	dmi system_information	
1f	serial_number of <dmi system_power_supply>: string	serial_number	serial_numbers	serial_number	0	string	dmi system_power_supply	
d	server arg of <Xinetd Service>: string	server arg	server args	server arg	0	string	Xinetd Service	
e0	server based flag of <bes computer group>: boolean	server based flag	server based flags	server based flag	0	boolean	bes computer group	
1f	server based group <string> of <client>: server based group	server based group	server based groups	server based group	0	server based group	client	string
1f	server based groups of <client>: server based group	server based group	server based groups	server based groups	1	server based group	client	
d	server of <Xinetd Service>: string	server	servers	server	0	string	Xinetd Service	
10	server of <email task action>: string	server	servers	server	0	string	email task action	
10	server operator flag of <user>: boolean	server operator flag	server operator flags	server operator flag	0	boolean	user	
10	server trust account flag of <user>: boolean	server trust account flag	server trust account flags	server trust account flag	0	boolean	user	
40	servers of <bes idp directory>: bes idp directory server	server	servers	servers	1	bes idp directory server	bes idp directory	
e0	servers of <bes ldap directory>: bes ldap directory server	server	servers	servers	1	bes ldap directory server	bes ldap directory	
2	service <string>: dummy	service	services	service	0	dummy		string
1d	service <string>: service	service	services	service	0	service		string
10	service account logon of <task principal>: boolean	service account logon	service account logons	service account logon	0	boolean	task principal	
10	service group: security account	service group	service groups	service group	0	security account		
10	service key value name of <active device>: string	service key value name	service key value names	service key value name	0	string	active device	
12	service name of <firewall rule>: string	service name	service names	service name	0	string	firewall rule	
10	service name of <service>: string	service name	service names	service name	0	string	service	
10	service pack major version of <operating system>: integer	service pack major version	service pack major versions	service pack major version	0	integer	operating system	
10	service pack minor version of <operating system>: integer	service pack minor version	service pack minor versions	service pack minor version	0	integer	operating system	
2	service plane of <registryroot>: registrynode	service plane	service planes	service plane	0	registrynode	registryroot	
10	service restricted <( string, string )> of <firewall service restriction>: boolean	service restricted	service restricteds	service restricted	0	boolean	firewall service restriction	( string, string )
10	service restriction of <firewall>: firewall service restriction	service restriction	service restrictions	service restriction	0	firewall service restriction	firewall	
10	service specific exit code of <service>: integer	service specific exit code	service specific exit codes	service specific exit code	0	integer	service	
10	services of <firewall profile>: firewall service	service	services	services	1	firewall service	firewall profile	
14	services: service	service	services	services	1	service		
12	session id of <logged on user>: integer	session id	session ids	session id	0	integer	logged on user	
10	session id of <process>: integer	session id	session ids	session id	0	integer	process	
10	session lock of <session state change task trigger>: boolean	session lock	session locks	session lock	0	boolean	session state change task trigger	
d	session of <process>: integer	session	sessions	session	0	integer	process	
10	session state change task trigger type: task trigger type	session state change task trigger type	session state change task trigger types	session state change task trigger type	0	task trigger type		
10	session unlock of <session state change task trigger>: boolean	session unlock	session unlocks	session unlock	0	boolean	session state change task trigger	
10	set value permission of <access control entry>: boolean	set value permission	set value permissions	set value permission	0	boolean	access control entry	
d	setgid of <filesystem object>: boolean	setgid	setgids	setgid	0	boolean	filesystem object	
d	setgid of <mode>: boolean	setgid	setgids	setgid	0	boolean	mode	
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
1f	setting <string> of <client>: setting	setting	settings	setting	0	setting	client	string
1f	setting <string> of <site>: setting	setting	settings	setting	0	setting	site	string
1f	setting of <manual group>: setting	setting	settings	setting	0	setting	manual group	
1f	setting of <server based group>: setting	setting	settings	setting	0	setting	server based group	
10	setting of <task definition>: task settings	setting	settings	setting	0	task settings	task definition	
e0	settings flag of <bes action>: boolean	settings flag	settings flags	settings flag	0	boolean	bes action	
1f	settings of <client>: setting	setting	settings	settings	1	setting	client	
1f	settings of <site>: setting	setting	settings	settings	1	setting	site	
d	setuid of <filesystem object>: boolean	setuid	setuids	setuid	0	boolean	filesystem object	
d	setuid of <mode>: boolean	setuid	setuids	setuid	0	boolean	mode	
1f	sha1 of <file>: string	sha1	sha1s	sha1	0	string	file	
ff	sha1 of <string>: string	sha1	sha1s	sha1	0	string	string	
ff	sha1 of <x509 certificate>: string	sha1	sha1s	sha1	0	string	x509 certificate	
1f	sha224 of <file>: string	sha224	sha224s	sha224	0	string	file	
ff	sha224 of <string>: string	sha224	sha224s	sha224	0	string	string	
ff	sha256 download of <license>: boolean	sha256 download	sha256 downloads	sha256 download	0	boolean	license	
1f	sha256 of <file>: string	sha256	sha256s	sha256	0	string	file	
1f	sha256 of <setting>: string	sha256	sha256s	sha256	0	string	setting	
ff	sha256 of <string>: string	sha256	sha256s	sha256	0	string	string	
1f	sha2_224 of <file>: string	sha2_224	sha2_224s	sha2_224	0	string	file	
ff	sha2_224 of <string>: string	sha2_224	sha2_224s	sha2_224	0	string	string	
1f	sha2_256 of <file>: string	sha2_256	sha2_256s	sha2_256	0	string	file	
ff	sha2_256 of <string>: string	sha2_256	sha2_256s	sha2_256	0	string	string	
1f	sha2_384 of <file>: string	sha2_384	sha2_384s	sha2_384	0	string	file	
ff	sha2_384 of <string>: string	sha2_384	sha2_384s	sha2_384	0	string	string	
1f	sha2_512 of <file>: string	sha2_512	sha2_512s	sha2_512	0	string	file	
ff	sha2_512 of <string>: string	sha2_512	sha2_512s	sha2_512	0	string	string	
1f	sha384 of <file>: string	sha384	sha384s	sha384	0	string	file	
ff	sha384 of <string>: string	sha384	sha384s	sha384	0	string	string	
5f	sha384 signature of <license>: boolean	sha384 signature	sha384 signatures	sha384 signature	0	boolean	license	
1f	sha512 of <file>: string	sha512	sha512s	sha512	0	string	file	
ff	sha512 of <string>: string	sha512	sha512s	sha512	0	string	string	
d	shared amount of <ram>: integer	shared amount	shared amounts	shared amount	0	integer	ram	
2	shared folder of <domain>: folder	shared folder	shared folders	shared folder	0	folder	domain	
2	shared folder: folder	shared folder	shared folders	shared folder	0	folder		
2	shared libraries folder of <domain>: folder	shared libraries folder	shared libraries folders	shared libraries folder	0	folder	domain	
2	shared libraries folder: folder	shared libraries folder	shared libraries folders	shared libraries folder	0	folder		
e0	shared variable <( string, string )>: string	shared variable	shared variables	shared variable	0	string		( string, string )
e0	shared variable <string> of <bes wizard>: string	shared variable	shared variables	shared variable	0	string	bes wizard	string
e0	shared variables of <bes wizard>: bes wizard variable	shared variable	shared variables	shared variables	1	bes wizard variable	bes wizard	
4	short form of <rpm package version record>: short rpm package version record	short form	short forms	short form	0	short rpm package version record	rpm package version record	
2	short name of <client process owner>: string	short name	short names	short name	0	string	client process owner	
4	short rpm package version record <rpm package version record>: short rpm package version record	short rpm package version record	short rpm package version records	short rpm package version record	0	short rpm package version record		rpm package version record
4	short rpm package version record <short rpm package version record>: short rpm package version record	short rpm package version record	short rpm package version records	short rpm package version record	0	short rpm package version record		short rpm package version record
2	short version of <filesystem object>: version	short version	short versions	short version	0	version	filesystem object	
10	shortcut of <file>: file shortcut	shortcut	shortcuts	shortcut	0	file shortcut	file	
e0	show message flag of <bes action>: boolean	show message flag	show message flags	show message flag	0	boolean	bes action	
10	show message task action type: task action type	show message task action type	show message task action types	show message task action type	0	task action type		
e0	show other action flag of <bes user>: boolean	show other action flag	show other action flags	show other action flag	0	boolean	bes user	
e0	show running message flag of <bes action>: boolean	show running message flag	show running message flags	show running message flag	0	boolean	bes action	
e0	shutdown flag of <bes action>: boolean	shutdown flag	shutdown flags	shutdown flag	0	boolean	bes action	
2	shutdown items <string>: enableable_file	shutdown item	shutdown items	shutdown items	1	enableable_file		string
2	shutdown items folder of <domain>: folder	shutdown items folder	shutdown items folders	shutdown items folder	0	folder	domain	
2	shutdown items folder: folder	shutdown items folder	shutdown items folders	shutdown items folder	0	folder		
2	shutdown items: enableable_file	shutdown item	shutdown items	shutdown items	1	enableable_file		
2	sibling file <binary_string> of <filesystem object>: file	sibling file	sibling files	sibling file	0	file	filesystem object	binary_string
2	sibling file <string> of <filesystem object>: file	sibling file	sibling files	sibling file	0	file	filesystem object	string
2	sibling folder <string> of <filesystem object>: folder	sibling folder	sibling folders	sibling folder	0	folder	filesystem object	string
2	sibling item <string> of <filesystem object>: filesystem object	sibling item	sibling items	sibling item	0	filesystem object	filesystem object	string
10	sid <string>: security identifier	sid	sids	sid	0	security identifier		string
12	sid of <active directory group>: security identifier	sid	sids	sid	0	security identifier	active directory group	
10	sid of <logged on user>: security identifier	sid	sids	sid	0	security identifier	logged on user	
10	sid of <security account>: security identifier	sid	sids	sid	0	security identifier	security account	
12	sid of <user>: security identifier	sid	sids	sid	0	security identifier	user	
10	sid of <winrt package user information>: security identifier	sid	sids	sid	0	security identifier	winrt package user information	
12	signal strength of <wifi network>: integer	signal strength	signal strengths	signal strength	0	integer	wifi network	
ff	signature algorithm of <x509 certificate>: string	signature algorithm	signature algorithms	signature algorithm	0	string	x509 certificate	
ff	signature hash algorithms of <license>: string	signature hash algorithm	signature hash algorithms	signature hash algorithms	1	string	license	
4	signature keyid of <package>: string	signature keyid	signature keyids	signature keyid	0	string	package	
ff	significance place <integer> of <floating point>: floating point	significance place	significance places	significance place	0	floating point	floating point	integer
ff	significance place of <floating point>: floating point	significance place	significance places	significance place	0	floating point	floating point	
ff	significance threshold of <floating point>: floating point	significance threshold	significance thresholds	significance threshold	0	floating point	floating point	
ff	significant digits <integer> of <hertz>: hertz	significant digits	significant digitss	significant digits	0	hertz	hertz	integer
ff	significant digits <integer> of <integer>: integer	significant digits	significant digitss	significant digits	0	integer	integer	integer
e0	simple name of <bes property>: string	simple name	simple names	simple name	0	string	bes property	
e0	single flag of <bes action>: boolean	single flag	single flags	single flag	0	boolean	bes action	
10	single user ts bit <operating system suite mask>: boolean	single user ts bit	single user ts bits	single user ts bit	0	boolean		operating system suite mask
ff	singular name of <property>: string	singular name	singular names	singular name	0	string	property	
1f	site <string>: site	site	sites	site	0	site		string
e0	site file set of <bes site>: bes site file set	site file set	site files sets	site file set	0	bes site file set	bes site	
e0	site files of <bes site>: bes site file	site file	site files	site files	1	bes site file	bes site	
40	site id of <bes peer download>: integer	site id	site ids	site id	0	integer	bes peer download	
e0	site level relevance of <bes site>: string	site level relevance	site level relevances	site level relevance	0	string	bes site	
ff	site number of <license>: integer	site number	site numbers	site number	0	integer	license	
e0	site of <bes computer group>: bes site	site	sites	site	0	bes site	bes computer group	
e0	site of <bes fixlet>: bes site	site	sites	site	0	bes site	bes fixlet	
40	site of <bes peer download>: bes site	site	sites	site	0	bes site	bes peer download	
e0	site of <bes wizard>: bes site	site	sites	site	0	bes site	bes wizard	
1f	site of <fixlet>: site	site	sites	site	0	site	fixlet	
1f	site tag of <site>: string	site tag	site tags	site tag	0	string	site	
ff	site urls of <bes product>: string	site url	site urls	site urls	1	string	bes product	
ff	site version list <string>: site version list	site version list	site version lists	site version list	0	site version list		string
1f	site version list of <site>: site version list	site version list	site version lists	site version list	0	site version list	site	
40	site version of <bes peer download>: integer	site version	site versions	site version	0	integer	bes peer download	
1f	sites: site	site	sites	sites	1	site		
1f	size of <application usage summary instance>: integer	size	sizes	size	0	integer	application usage summary instance	
2	size of <array>: integer	size	sizes	size	0	integer	array	
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
2	size of <datafork>: integer	size	sizes	size	0	integer	datafork	
2	size of <dictionary>: integer	size	sizes	size	0	integer	dictionary	
1f	size of <dmi memory_device>: integer	size	sizes	size	0	integer	dmi memory_device	
1f	size of <file>: integer	size	sizes	size	0	integer	file	
d	size of <filesystem>: integer	size	sizes	size	0	integer	filesystem	
ff	size of <integer set>: integer	size	sizes	size	0	integer	integer set	
1f	size of <ram>: integer	size	sizes	size	0	integer	ram	
10	size of <registry key value>: integer	size	sizes	size	0	integer	registry key value	
2	size of <resfork>: integer	size	sizes	size	0	integer	resfork	
ff	size of <string set>: integer	size	sizes	size	0	integer	string set	
f	size of <swap>: integer	size	sizes	size	0	integer	swap	
ff	size of <type>: integer	size	sizes	size	0	integer	type	
2	size of <volume>: integer	size	sizes	size	0	integer	volume	
e0	skewness of <statistical bin>: floating point	skewness	skewnesses	skewness	0	floating point	statistical bin	
1f	sku_number of <dmi system_information>: string	sku_number	sku_numbers	sku_number	0	string	dmi system_information	
1f	sleep duration of <evaluation cycle>: time interval	sleep duration	sleep durations	sleep duration	0	time interval	evaluation cycle	
1f	sleep percent of <evaluation cycle>: floating point	sleep percent	sleep percents	sleep percent	0	floating point	evaluation cycle	
1f	slot_characteristics_1 of <dmi system_slots>: integer	slot_characteristics_1	slot_characteristics_1s	slot_characteristics_1	0	integer	dmi system_slots	
1f	slot_characteristics_2 of <dmi system_slots>: integer	slot_characteristics_2	slot_characteristics_2s	slot_characteristics_2	0	integer	dmi system_slots	
1f	slot_data_bus_width of <dmi system_slots>: integer	slot_data_bus_width	slot_data_bus_widths	slot_data_bus_width	0	integer	dmi system_slots	
1f	slot_designation of <dmi system_slots>: string	slot_designation	slot_designations	slot_designation	0	string	dmi system_slots	
1f	slot_id of <dmi system_slots>: integer	slot_id	slot_ids	slot_id	0	integer	dmi system_slots	
1f	slot_length of <dmi system_slots>: integer	slot_length	slot_lengths	slot_length	0	integer	dmi system_slots	
1f	slot_type of <dmi system_slots>: integer	slot_type	slot_types	slot_type	0	integer	dmi system_slots	
ff	small <string> of <html>: html	small	smalls	small	0	html	html	string
ff	small <string> of <string>: html	small	smalls	small	0	html	string	string
10	small business bit <operating system suite mask>: boolean	small business bit	small business bits	small business bit	0	boolean		operating system suite mask
10	small business restricted bit <operating system suite mask>: boolean	small business restricted bit	small business restricted bits	small business restricted bit	0	boolean		operating system suite mask
ff	small of <html>: html	small	smalls	small	0	html	html	
ff	small of <string>: html	small	smalls	small	0	html	string	
1f	smbios: smbios	smbios	smbioses	smbios	0	smbios		
1f	smt capable of <cpupackage>: boolean	smt capable	smt capables	smt capable	0	boolean	cpupackage	
1f	smt enabled of <cpupackage>: boolean	smt enabled	smt enableds	smt enabled	0	boolean	cpupackage	
d	socket file <filesystem object>: socket file	socket file	socket files	socket file	0	socket file		filesystem object
d	socket file <string> of <folder>: socket file	socket file	socket files	socket file	0	socket file	folder	string
d	socket file <string>: socket file	socket file	socket files	socket file	0	socket file		string
d	socket file <symlink>: socket file	socket file	socket files	socket file	0	socket file		symlink
d	socket files of <folder>: socket file	socket file	socket files	socket files	1	socket file	folder	
d	socket type of <Xinetd Service>: string	socket type	socket types	socket type	0	string	Xinetd Service	
1f	socket_designation of <dmi cache_information>: string	socket_designation	socket_designations	socket_designation	0	string	dmi cache_information	
1f	socket_designation of <dmi memory_module_information>: string	socket_designation	socket_designations	socket_designation	0	string	dmi memory_module_information	
1f	socket_designation of <dmi processor_information>: string	socket_designation	socket_designations	socket_designation	0	string	dmi processor_information	
1f	sockets of <network>: socket	socket	sockets	sockets	1	socket	network	
2	sound folder of <domain>: folder	sound folder	sound folders	sound folder	0	folder	domain	
2	sound folder: folder	sound folder	sound folders	sound folder	0	folder		
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
10	source of <event log record>: string	source	sources	source	0	string	event log record	
10	source of <task registration info>: string	source	sources	source	0	string	task registration info	
e0	source release date of <bes fixlet>: date	source release date	source release dates	source release date	0	date	bes fixlet	
e0	source relevance of <bes action>: string	source relevance	source relevances	source relevance	0	string	bes action	
e0	source severity of <bes fixlet>: string	source severity	source severities	source severity	0	string	bes fixlet	
e0	source severity of <fixlet count pair>: string	source severity	source severitys	source severity	0	string	fixlet count pair	
ff	span <string> of <html>: html	span	spans	span	0	html	html	string
ff	span <string> of <string>: html	span	spans	span	0	html	string	string
ff	span of <html>: html	span	spans	span	0	html	html	
ff	span of <string>: html	span	spans	span	0	html	string	
2	speech folder of <domain>: folder	speech folder	speech folders	speech folder	0	folder	domain	
2	speech folder: folder	speech folder	speech folders	speech folder	0	folder		
1f	speed of <dmi memory_device>: integer	speed	speeds	speed	0	integer	dmi memory_device	
1f	speed of <processor>: hertz	speed	speeds	speed	0	hertz	processor	
d	splashimage of <grub config file>: grub file location	splashimage	splashimages	splashimage	0	grub file location	grub config file	
1f	sqlite database of <file>: sqlite database	sqlite database	sqlite databases	sqlite database	0	sqlite database	file	
1f	sqlite version: version	sqlite version	sqlite versions	sqlite version	0	version		
ff	sqrt of <floating point>: floating point	sqrt	sqrts	sqrt	0	floating point	floating point	
ff	sqrt of <integer>: floating point	sqrt	sqrts	sqrt	0	floating point	integer	
12	ssid of <wifi network>: string	ssid	ssids	ssid	0	string	wifi network	
12	ssid of <wifi>: string	ssid	ssids	ssid	0	string	wifi	
2	stage <string>: stage	stage	stages	stage	0	stage		string
2	stage of <version>: stage	stage	stages	stage	0	stage	version	
e0	standard deviation of <statistical bin>: floating point	standard deviation	standard deviations	standard deviation	0	floating point	statistical bin	
ff	standard deviations of <floating point>: floating point	standard deviation	standard deviations	standard deviations	1	floating point	floating point	
ff	standard deviations of <integer>: floating point	standard deviation	standard deviations	standard deviations	1	floating point	integer	
10	standard firewall profile type: firewall profile type	standard firewall profile type	standard firewall profile types	standard firewall profile type	0	firewall profile type		
10	standard profile of <firewall policy>: firewall profile	standard profile	standard profiles	standard profile	0	firewall profile	firewall policy	
12	standby state: power state	standby state	standby states	standby state	0	power state		
10	start boundary of <task trigger>: time	start boundary	start boundaries	start boundary	0	time	task trigger	
e0	start date of <bes action>: date	start date	start dates	start date	0	date	bes action	
ff	start date of <license>: time	start date	start dates	start date	0	time	license	
e0	start flag of <bes action>: boolean	start flag	start flags	start flag	0	boolean	bes action	
10	start in pathname of <file shortcut>: string	start in pathname	start in pathnames	start in pathname	0	string	file shortcut	
ff	start of <binary_substring>: binary position	start	starts	start	0	binary position	binary_substring	
e0	start of <statistic range>: time	start	starts	start	0	time	statistic range	
e0	start of <statistical bin>: time	start	starts	start	0	time	statistical bin	
ff	start of <substring>: string position	start	starts	start	0	string position	substring	
ff	start of <time range>: time	start	starts	start	0	time	time range	
e0	start time of <bes action result>: time	start time	start times	start time	0	time	bes action result	
d	start time of <process>: time	start time	start times	start time	0	time	process	
e0	start time_of_day of <bes action>: time of day	start time_of_day	start times_of_day	start time_of_day	0	time of day	bes action	
10	start type of <service>: string	start type	start types	start type	0	string	service	
10	start when available of <task settings>: boolean	start when available	start when availables	start when available	0	boolean	task settings	
1f	starting_address of <dmi memory_array_mapped_address>: integer	starting_address	starting_addresss	starting_address	0	integer	dmi memory_array_mapped_address	
1f	starting_address of <dmi memory_device_mapped_address>: integer	starting_address	starting_addresss	starting_address	0	integer	dmi memory_device_mapped_address	
2	startup items <string>: enableable_file	startup item	startup items	startup items	1	enableable_file		string
2	startup items folder of <domain>: folder	startup items folder	startup items folders	startup items folder	0	folder	domain	
2	startup items folder: folder	startup items folder	startup items folders	startup items folder	0	folder		
2	startup items: enableable_file	startup item	startup items	startup items	1	enableable_file		
12	state of <agent interface capability>: string	state	states	state	0	string	agent interface capability	
e0	state of <bes action>: string	state	states	state	0	string	bes action	
ff	state of <bes product>: string	state	states	state	0	string	bes product	
2	state of <dummy>: string	state	states	state	0	string	dummy	
12	state of <monitor power interval>: power state	state	states	state	0	power state	monitor power interval	
1d	state of <service>: string	state	states	state	0	string	service	
12	state of <system power interval>: power state	state	states	state	0	power state	system power interval	
1f	statement <string> of <sqlite database>: sqlite statement	statement	statements	statement	0	sqlite statement	sqlite database	string
2	static flag of <route>: boolean	static flag	static flags	static flag	0	boolean	route	
2	stationery of <file>: boolean	stationery	stationeries	stationery	0	boolean	file	
e0	statistic range of <bes property>: statistic range	statistic range	statistic ranges	statistic range	0	statistic range	bes property	
1f	status of <action>: string	status	statuss	status	0	string	action	
10	status of <active device>: integer	status	statuss	status	0	integer	active device	
e0	status of <bes action result>: bes action status	status	statuses	status	0	bes action status	bes action result	
e0	status of <bes activation>: string	status	statuses	status	0	string	bes activation	
10	status of <connection>: connection status	status	statuses	status	0	connection status	connection	
1f	status of <dmi processor_information>: integer	status	statuss	status	0	integer	dmi processor_information	
10	status of <network adapter>: integer	status	statuses	status	0	integer	network adapter	
2	stealth enabled of <firewall>: boolean	stealth enabled	stealth enableds	stealth enabled	0	boolean	firewall	
1f	stepping of <processor>: integer	stepping	steppings	stepping	0	integer	processor	
d	sticky of <mode>: boolean	sticky	stickies	sticky	0	boolean	mode	
10	stop at duration end of <task repetition pattern>: boolean	stop at duration end	stop at duration ends	stop at duration end	0	boolean	task repetition pattern	
10	stop existing instance of <task settings>: boolean	stop existing instance	stop existing instances	stop existing instance	0	boolean	task settings	
10	stop on idle end of <task idle settings>: boolean	stop on idle end	stop on idle ends	stop on idle end	0	boolean	task idle settings	
e0	stop other actions flag of <bes user>: boolean	stop other actions flag	stop other actions flags	stop other actions flag	0	boolean	bes user	
10	stop when going on battery of <task settings>: boolean	stop when going on battery	stop when going on batteries	stop when going on battery	0	boolean	task settings	
e0	stopper of <bes action>: bes user	stopper	stoppers	stopper	0	bes user	bes action	
1f	storage folder of <client>: folder	storage folder	storage folders	storage folder	0	folder	client	
2	string <integer> of <array>: string	string	strings	string	0	string	array	integer
2	string <string> of <dictionary>: string	string	strings	string	0	string	dictionary	string
2	string <string> of <preference>: string	string	strings	string	0	string	preference	string
ff	string <string>: string	string	strings	string	0	string		string
1f	string named files of <folder>: file	string named file	string named files	string named files	1	file	folder	
1f	string named folders of <folder>: folder	string named folder	string named folders	string named folders	1	folder	folder	
2	string of <osxvalue>: string	string	strings	string	0	string	osxvalue	
ff	string of <tuple item>: string	string	strings	string	0	string	tuple item	
10	string value <integer> of <wmi select>: string	string value	string values	string value	0	string	wmi select	integer
1f	string values <string> of <smbios structure>: smbios value	string value	string values	string values	1	smbios value	smbios structure	string
10	string values of <wmi select>: string	string value	string values	string values	1	string	wmi select	
1f	string version of <application usage summary instance>: string	string version	string versions	string version	0	string	application usage summary instance	
1f	strings <string> of <smbios structure>: string	string	strings	strings	1	string	smbios structure	string
ff	strong <string> of <html>: html	strong	strongs	strong	0	html	html	string
ff	strong <string> of <string>: html	strong	strongs	strong	0	html	string	string
ff	strong of <html>: html	strong	strongs	strong	0	html	html	
ff	strong of <string>: html	strong	strongs	strong	0	html	string	
1f	structure of <smbios value>: smbios structure	structure	structures	structure	0	smbios structure	smbios value	
1f	structures <string> of <smbios>: smbios structure	structure	structures	structures	1	smbios structure	smbios	string
1f	structures of <smbios>: smbios structure	structure	structures	structures	1	smbios structure	smbios	
4d	strverscmp version <string>: strverscmp version	strverscmp version	strverscmp versions	strverscmp version	0	strverscmp version		string
ff	sub <string> of <html>: html	sub	subs	sub	0	html	html	string
ff	sub <string> of <string>: html	sub	subs	sub	0	html	string	string
ff	sub of <html>: html	sub	subs	sub	0	html	html	
ff	sub of <string>: html	sub	subs	sub	0	html	string	
10	subcategories of <audit policy category>: audit policy subcategory	subcategory	subcategories	subcategories	1	audit policy subcategory	audit policy category	
ff	subject common name of <x509 certificate>: string	subject common name	subject common names	subject common name	0	string	x509 certificate	
10	subject of <email task action>: string	subject	subjects	subject	0	string	email task action	
ff	subject of <x509 certificate>: string	subject	subjects	subject	0	string	x509 certificate	
1f	subnet address of <network adapter interface>: ipv4or6 address	subnet address	subnet addresses	subnet address	0	ipv4or6 address	network adapter interface	
1f	subnet address of <network adapter>: ipv4 address	subnet address	subnet addresses	subnet address	0	ipv4 address	network adapter	
10	subnet address of <network address list>: ipv4 address	subnet address	subnet addresses	subnet address	0	ipv4 address	network address list	
1f	subnet address of <network ip interface>: ipv4 address	subnet address	subnet addresses	subnet address	0	ipv4 address	network ip interface	
1f	subnet mask of <cidr subnet>: ipv4or6 address	subnet mask	subnet masks	subnet mask	0	ipv4or6 address	cidr subnet	
1f	subnet mask of <network adapter interface>: ipv4or6 address	subnet mask	subnet masks	subnet mask	0	ipv4or6 address	network adapter interface	
1f	subnet mask of <network adapter>: ipv4 address	subnet mask	subnet masks	subnet mask	0	ipv4 address	network adapter	
10	subnet mask of <network address list>: ipv4 address	subnet mask	subnet masks	subnet mask	0	ipv4 address	network address list	
1f	subnet mask of <network ip interface>: ipv4 address	subnet mask	subnet masks	subnet mask	0	ipv4 address	network ip interface	
40	subnet of <bes peer download>: string	subnet	subnets	subnet	0	string	bes peer download	
1f	subscribe time of <site>: time	subscribe time	subscribe times	subscribe time	0	time	site	
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
10	subscription of <event task trigger>: string	subscription	subscriptions	subscription	0	string	event task trigger	
ff	substring <( integer, integer )> of <string>: substring	substring	substrings	substring	0	substring	string	( integer, integer )
ff	substrings <string> of <string>: substring	substring	substrings	substrings	1	substring	string	string
ff	substrings after <string> of <string>: substring	substring after	substrings after	substrings after	1	substring	string	string
ff	substrings before <string> of <string>: substring	substring before	substrings before	substrings before	1	substring	string	string
ff	substrings between <string> of <string>: substring	substring between	substrings between	substrings between	1	substring	string	string
ff	substrings separated by <string> of <string>: substring	substring separated by	substrings separated by	substrings separated by	1	substring	string	string
2	subsystem of <os log entry log>: string	subsystem	subsystems	subsystem	0	string	os log entry log	
2	subtype of <component>: string	subtype	subtypes	subtype	0	string	component	
e0	success on custom relevance of <bes action>: boolean	success on custom relevance	success on custom relevances	success on custom relevance	0	boolean	bes action	
e0	success on custom relevance of <bes fixlet action>: boolean	success on custom relevance	success on custom relevances	success on custom relevance	0	boolean	bes fixlet action	
e0	success on original relevance of <bes action>: boolean	success on original relevance	success on original relevances	success on original relevance	0	boolean	bes action	
e0	success on original relevance of <bes fixlet action>: boolean	success on original relevance	success on original relevances	success on original relevance	0	boolean	bes fixlet action	
e0	success on run to completion of <bes action>: boolean	success on run to completion	success on run to completions	success on run to completion	0	boolean	bes action	
e0	success on run to completion of <bes fixlet action>: boolean	success on run to completion	success on run to completions	success on run to completion	0	boolean	bes fixlet action	
e0	success rate of <statistical bin>: floating point	success rate	success rates	success rate	0	floating point	statistical bin	
10	suite mask of <operating system>: operating system suite mask	suite mask	suite masks	suite mask	0	operating system suite mask	operating system	
ff	sums of <floating point>: floating point	sum	sums	sums	1	floating point	floating point	
ff	sums of <integer>: integer	sum	sums	sums	1	integer	integer	
ff	sums of <time interval>: time interval	sum	sums	sums	1	time interval	time interval	
ff	sunday: day of week	sunday	sundays	sunday	0	day of week		
ff	sup <string> of <html>: html	sup	sups	sup	0	html	html	string
ff	sup <string> of <string>: html	sup	sups	sup	0	html	string	string
ff	sup of <html>: html	sup	sups	sup	0	html	html	
ff	sup of <string>: html	sup	sups	sup	0	html	string	
1f	supported_interleave of <dmi memory_controller_information>: integer	supported_interleave	supported_interleaves	supported_interleave	0	integer	dmi memory_controller_information	
1f	supported_memory_types of <dmi memory_controller_information>: integer	supported_memory_types	supported_memory_typess	supported_memory_types	0	integer	dmi memory_controller_information	
1f	supported_speeds of <dmi memory_controller_information>: integer	supported_speeds	supported_speedss	supported_speeds	0	integer	dmi memory_controller_information	
1f	supported_sram_type of <dmi cache_information>: integer	supported_sram_type	supported_sram_types	supported_sram_type	0	integer	dmi cache_information	
f	swap: swap	swap	swaps	swap	0	swap		
ff	symbol of <binary operator>: string	symbol	symbols	symbol	0	string	binary operator	
ff	symbol of <unary operator>: string	symbol	symbols	symbol	0	string	unary operator	
d	symlink <binary_string> of <encoding>: symlink	symlink	symlinks	symlink	0	symlink	encoding	binary_string
d	symlink <binary_string> of <folder>: symlink	symlink	symlinks	symlink	0	symlink	folder	binary_string
d	symlink <binary_string>: symlink	symlink	symlinks	symlink	0	symlink		binary_string
d	symlink <filesystem object>: symlink	symlink	symlinks	symlink	0	symlink		filesystem object
d	symlink <string> of <encoding>: symlink	symlink	symlinks	symlink	0	symlink	encoding	string
d	symlink <string> of <folder>: symlink	symlink	symlinks	symlink	0	symlink	folder	string
d	symlink <string>: symlink	symlink	symlinks	symlink	0	symlink		string
d	symlink <symlink>: symlink	symlink	symlinks	symlink	0	symlink		symlink
d	symlinks of <folder>: symlink	symlink	symlinks	symlinks	1	symlink	folder	
1f	syn received of <tcp state>: boolean	syn received	syn receiveds	syn received	0	boolean	tcp state	
1f	syn sent of <tcp state>: boolean	syn sent	syn sents	syn sent	0	boolean	tcp state	
10	synchronize permission of <access control entry>: boolean	synchronize permission	synchronize permissions	synchronize permission	0	boolean	access control entry	
10	system category of <audit policy>: audit policy category	system category	system categories	system category	0	audit policy category	audit policy	
1f	system constraint of <action>: integer	system constraint	system constraints	system constraint	0	integer	action	
2	system domain: domain	system domain	system domains	system domain	0	domain		
10	system event log: event log	system event log	system event logs	system event log	0	event log		
10	system file <string>: file	system file	system files	system file	0	file		string
2	system folder of <domain>: folder	system folder	system folders	system folder	0	folder	domain	
1f	system folder: folder	system folder	system folders	system folder	0	folder		
10	system group: security account	system group	system groups	system group	0	security account		
10	system ini device files <string>: file	system ini device file	system ini device files	system ini device files	1	file		string
10	system ini device files: file	system ini device file	system ini device files	system ini device files	1	file		
12	system intervals of <power history>: system power interval	system interval	system intervals	system intervals	1	system power interval	power history	
1d	system language: string	system language	system languages	system language	0	string		
1d	system locale: language	system locale	system locales	system locale	0	language		
10	system of <filesystem object>: boolean	system	systems	system	0	boolean	filesystem object	
10	system policy of <audit policy subcategory>: audit policy information	system policy	system policies	system policy	0	audit policy information	audit policy subcategory	
1d	system ui language: language	system ui language	system ui languages	system ui language	0	language		
2	system version: version	system version	system versions	system version	0	version		
10	system wow64 folder: folder	system wow64 folder	system wow64 folders	system wow64 folder	0	folder		
10	system x32 file <string>: file	system x32 file	system x32 files	system x32 file	0	file		string
10	system x32 folder: folder	system x32 folder	system x32 folders	system x32 folder	0	folder		
10	system x64 file <string>: file	system x64 file	system x64 files	system x64 file	0	file		string
10	system x64 folder: folder	system x64 folder	system x64 folders	system x64 folder	0	folder		
1f	system_bios_major_release of <dmi bios_information>: integer	system_bios_major_release	system_bios_major_releases	system_bios_major_release	0	integer	dmi bios_information	
1f	system_bios_minor_release of <dmi bios_information>: integer	system_bios_minor_release	system_bios_minor_releases	system_bios_minor_release	0	integer	dmi bios_information	
1f	system_boot_information <integer> of <dmi>: dmi system_boot_information	system_boot_information	system_boot_informations	system_boot_information	0	dmi system_boot_information	dmi	integer
1f	system_boot_informations of <dmi>: dmi system_boot_information	system_boot_information	system_boot_informations	system_boot_informations	1	dmi system_boot_information	dmi	
1f	system_cache_type of <dmi cache_information>: integer	system_cache_type	system_cache_types	system_cache_type	0	integer	dmi cache_information	
1f	system_configuration_option <integer> of <dmi>: string	system_configuration_option	system_configuration_options	system_configuration_option	0	string	dmi	integer
1f	system_configuration_options of <dmi>: string	system_configuration_option	system_configuration_options	system_configuration_options	1	string	dmi	
1f	system_enclosure_or_chassis <integer> of <dmi>: dmi system_enclosure_or_chassis	system_enclosure_or_chassis	system_enclosure_or_chassiss	system_enclosure_or_chassis	0	dmi system_enclosure_or_chassis	dmi	integer
1f	system_enclosure_or_chassiss of <dmi>: dmi system_enclosure_or_chassis	system_enclosure_or_chassis	system_enclosure_or_chassiss	system_enclosure_or_chassiss	1	dmi system_enclosure_or_chassis	dmi	
1f	system_information <integer> of <dmi>: dmi system_information	system_information	system_informations	system_information	0	dmi system_information	dmi	integer
1f	system_informations of <dmi>: dmi system_information	system_information	system_informations	system_informations	1	dmi system_information	dmi	
1f	system_power_controls <integer> of <dmi>: dmi system_power_controls	system_power_controls	system_power_controlss	system_power_controls	0	dmi system_power_controls	dmi	integer
1f	system_power_controlss of <dmi>: dmi system_power_controls	system_power_controls	system_power_controlss	system_power_controlss	1	dmi system_power_controls	dmi	
1f	system_power_supply <integer> of <dmi>: dmi system_power_supply	system_power_supply	system_power_supplys	system_power_supply	0	dmi system_power_supply	dmi	integer
1f	system_power_supplys of <dmi>: dmi system_power_supply	system_power_supply	system_power_supplys	system_power_supplys	1	dmi system_power_supply	dmi	
1f	system_reset <integer> of <dmi>: dmi system_reset	system_reset	system_resets	system_reset	0	dmi system_reset	dmi	integer
1f	system_resets of <dmi>: dmi system_reset	system_reset	system_resets	system_resets	1	dmi system_reset	dmi	
1f	system_slots <integer> of <dmi>: dmi system_slots	system_slots	system_slotss	system_slots	0	dmi system_slots	dmi	integer
1f	system_slotss of <dmi>: dmi system_slots	system_slots	system_slotss	system_slotss	1	dmi system_slots	dmi	
ff	table <string> of <html>: html	table	tables	table	0	html	html	string
1f	table <string> of <sqlite database>: sqlite table	table	tables	table	0	sqlite table	sqlite database	string
ff	table <string> of <string>: html	table	tables	table	0	html	string	string
ff	table of <html>: html	table	tables	table	0	html	html	
ff	table of <string>: html	table	tables	table	0	html	string	
1f	tables of <sqlite database>: sqlite table	table	tables	tables	1	sqlite table	sqlite database	
e0	tag of <bes site>: string	tag	tags	tag	0	string	bes site	
40	tagged actions of <string>: bes action	tagged action	tagged actions	tagged actions	1	bes action	string	
40	tagged fixlets of <string>: bes fixlet	tagged fixlet	tagged fixlets	tagged fixlets	1	bes fixlet	string	
40	tags of <bes action>: bes tag	tag	tags	tags	1	bes tag	bes action	
40	tags of <bes fixlet>: bes tag	tag	tags	tags	1	bes tag	bes fixlet	
e0	taken action set of <bes fixlet>: bes action set	taken action set	taken action sets	taken action set	0	bes action set	bes fixlet	
e0	taken actions of <bes fixlet>: bes action	taken action	taken actions	taken actions	1	bes action	bes fixlet	
10	target ip address of <port mapping>: ipv4 address	target ip address	target ip addresses	target ip address	0	ipv4 address	port mapping	
10	target ipv4or6 address of <port mapping>: ipv4or6 address	target ipv4or6 address	target ipv4or6 addresses	target ipv4or6 address	0	ipv4or6 address	port mapping	
10	target name of <port mapping>: string	target name	target names	target name	0	string	port mapping	
e0	targeted by id flag of <bes action>: boolean	targeted by id flag	targeted by id flags	targeted by id flag	0	boolean	bes action	
e0	targeted by list flag of <bes action>: boolean	targeted by list flag	targeted by list flags	targeted by list flag	0	boolean	bes action	
e0	targeted by property flag of <bes action>: boolean	targeted by property flag	targeted by property flags	targeted by property flag	0	boolean	bes action	
e0	targeted computer set of <bes action>: bes computer set	targeted computer set	targeted computer sets	targeted computer set	0	bes computer set	bes action	
e0	targeted computers of <bes action>: bes computer	targeted computer	targeted computers	targeted computers	1	bes computer	bes action	
e0	targeted list of <bes action>: string	targeted list	targeted lists	targeted list	0	string	bes action	
e0	targeted names of <bes action>: string	targeted name	targeted names	targeted names	1	string	bes action	
e0	targeting method of <bes action>: string	targeting method	targeting methods	targeting method	0	string	bes action	
e0	targeting relevance of <bes action>: string	targeting relevance	targeting relevances	targeting relevance	0	string	bes action	
4	targets of <service>: string	target	targets	targets	1	string	service	
10	task action type <integer>: task action type	task action type	task action types	task action type	0	task action type		integer
e0	task flag of <bes filter>: boolean	task flag	task flags	task flag	0	boolean	bes filter	
e0	task flag of <bes fixlet>: boolean	task flag	task flags	task flag	0	boolean	bes fixlet	
10	task folder <string>: task folder	task folder	task folders	task folder	0	task folder		string
10	task folders of <task folder>: task folder	task folder	task folders	task folders	1	task folder	task folder	
10	task name of <application>: string	task name	task names	task name	0	string	application	
e0	task set of <bes filter>: bes fixlet set	task set	task sets	task set	0	bes fixlet set	bes filter	
10	task trigger type <integer>: task trigger type	task trigger type	task trigger types	task trigger type	0	task trigger type		integer
ff	tbody <string> of <html>: html	tbody	tbodys	tbody	0	html	html	string
ff	tbody <string> of <string>: html	tbody	tbodys	tbody	0	html	string	string
ff	tbody of <html>: html	tbody	tbodys	tbody	0	html	html	
ff	tbody of <string>: html	tbody	tbodys	tbody	0	html	string	
1f	tcp of <socket>: boolean	tcp	tcps	tcp	0	boolean	socket	
1f	tcp state of <socket>: tcp state	tcp state	tcp states	tcp state	0	tcp state	socket	
10	tcp: internet protocol	tcp	tcps	tcp	0	internet protocol		
ff	td <string> of <html>: html	td	tds	td	0	html	html	string
ff	td <string> of <string>: html	td	tds	td	0	html	string	string
ff	td of <html>: html	td	tds	td	0	html	html	
ff	td of <string>: html	td	tds	td	0	html	string	
1f	temperature_probe <integer> of <dmi>: dmi temperature_probe	temperature_probe	temperature_probes	temperature_probe	0	dmi temperature_probe	dmi	integer
1f	temperature_probe_handle of <dmi cooling_device>: integer	temperature_probe_handle	temperature_probe_handles	temperature_probe_handle	0	integer	dmi cooling_device	
1f	temperature_probes of <dmi>: dmi temperature_probe	temperature_probe	temperature_probes	temperature_probes	1	dmi temperature_probe	dmi	
10	template file of <site profile>: file	template file	template files	template file	0	file	site profile	
e0	temporal distribution of <bes action>: time interval	temporal distribution	temporal distributions	temporal distribution	0	time interval	bes action	
10	temporary duplicate account flag of <user>: boolean	temporary duplicate account flag	temporary duplicate account flags	temporary duplicate account flag	0	boolean	user	
2	temporary items folder of <domain>: folder	temporary items folder	temporary items folders	temporary items folder	0	folder	domain	
2	temporary items folder: folder	temporary items folder	temporary items folders	temporary items folder	0	folder		
10	temporary of <filesystem object>: boolean	temporary	temporarys	temporary	0	boolean	filesystem object	
40	tenant id of <bes idp directory>: string	tenant id	tenant ids	tenant id	0	string	bes idp directory	
ff	term of <bes product>: boolean	term	terms	term	0	boolean	bes product	
10	terminal bit <operating system suite mask>: boolean	terminal bit	terminal bits	terminal bit	0	boolean		operating system suite mask
10	terminal server user group: security account	terminal server user group	terminal server user groups	terminal server user group	0	security account		
2	text encodings folder of <domain>: folder	text encodings folder	text encodings folders	text encodings folder	0	folder	domain	
2	text encodings folder: folder	text encodings folder	text encodings folders	text encodings folder	0	folder		
e0	text of <bes comment>: string	text	texts	text	0	string	bes comment	
1f	text of <sqlite column type>: boolean	text	texts	text	0	boolean	sqlite column type	
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
2	themes folder of <domain>: folder	themes folder	themes folders	themes folder	0	folder	domain	
2	themes folder: folder	themes folder	themes folders	themes folder	0	folder		
1f	thermal_state of <dmi system_enclosure_or_chassis>: integer	thermal_state	thermal_states	thermal_state	0	integer	dmi system_enclosure_or_chassis	
2	thread identifier of <os log entry log>: integer	thread identifier	thread identifiers	thread identifier	0	integer	os log entry log	
1f	thread of <cpupackage>: integer	thread	threads	thread	0	integer	cpupackage	
1f	thread_count of <dmi processor_information>: integer	thread_count	thread_counts	thread_count	0	integer	dmi processor_information	
1f	threshold_handle of <dmi management_device_component>: integer	threshold_handle	threshold_handles	threshold_handle	0	integer	dmi management_device_component	
ff	thursday: day of week	thursday	thursdays	thursday	0	day of week		
ff	time <string>: time	time	times	time	0	time		string
ff	time <time zone> of <time>: time of day with time zone	time	times	time	0	time of day with time zone	time	time zone
10	time generated of <event log record>: time	time generated	times generated	time generated	0	time	event log record	
2	time generated of <os log entry log>: time	time generated	times generated	time generated	0	time	os log entry log	
ff	time interval <string>: time interval	time interval	time intervals	time interval	0	time interval		string
e0	time issued of <bes action>: time	time issued	times issued	time issued	0	time	bes action	
1f	time of <execution>: time	time	times	time	0	time	execution	
e0	time of <historical computer count>: time	time	times	time	0	time	historical computer count	
e0	time of <historical fixlet count>: time	time	times	time	0	time	historical fixlet count	
ff	time of <time of day with time zone>: time of day	time	times	time	0	time of day	time of day with time zone	
e0	time range end of <bes action>: time of day	time range end	time range ends	time range end	0	time of day	bes action	
e0	time range start of <bes action>: time of day	time range start	time range starts	time range start	0	time of day	bes action	
e0	time stopped of <bes action>: time	time stopped	times stopped	time stopped	0	time	bes action	
10	time task trigger type: task trigger type	time task trigger type	time task trigger types	time task trigger type	0	task trigger type		
10	time value <integer> of <wmi select>: time	time value	time values	time value	0	time	wmi select	integer
10	time values of <wmi select>: time	time value	time values	time values	1	time	wmi select	
1f	time wait of <tcp state>: boolean	time wait	time waits	time wait	0	boolean	tcp state	
10	time written of <event log record>: time	time written	times written	time written	0	time	event log record	
ff	time zone <string>: time zone	time zone	time zones	time zone	0	time zone		string
ff	time_of_day <string>: time of day	time_of_day	times_of_day	time_of_day	0	time of day		string
1f	timeout of <dmi system_reset>: integer	timeout	timeouts	timeout	0	integer	dmi system_reset	
d	timeout of <grub config file>: integer	timeout	timeouts	timeout	0	integer	grub config file	
1f	timer_interval of <dmi system_reset>: integer	timer_interval	timer_intervals	timer_interval	0	integer	dmi system_reset	
e0	timestamp of <bes comment>: time	timestamp	timestamps	timestamp	0	time	bes comment	
ff	title <string> of <html>: html	title	titles	title	0	html	html	string
ff	title <string> of <string>: html	title	titles	title	0	html	string	string
d	title of <grub bootable image>: string	title	titles	title	0	string	grub bootable image	
ff	title of <html>: html	title	titles	title	0	html	html	
10	title of <show message task action>: string	title	titles	title	0	string	show message task action	
ff	title of <string>: html	title	titles	title	0	html	string	
ff	tls cipher list of <license>: string	tls cipher list	tls cipher lists	tls cipher list	0	string	license	
10	to of <email task action>: string	to	tos	to	0	string	email task action	
1f	tolerance of <dmi electrical_current_probe>: integer	tolerance	tolerances	tolerance	0	integer	dmi electrical_current_probe	
1f	tolerance of <dmi temperature_probe>: integer	tolerance	tolerances	tolerance	0	integer	dmi temperature_probe	
1f	tolerance of <dmi voltage_probe>: integer	tolerance	tolerances	tolerance	0	integer	dmi voltage_probe	
e0	top level bes action set: bes action set	top level bes action set	top level bes action sets	top level bes action set	0	bes action set		
e0	top level bes actions: bes action	top level bes action	top level bes actions	top level bes actions	1	bes action		
e0	top level flag of <bes action>: boolean	top level flag	top level flags	top level flag	0	boolean	bes action	
1f	total amount of <ram>: integer	total amount	total amounts	total amount	0	integer	ram	
f	total amount of <swap>: integer	total amount	total amounts	total amount	0	integer	swap	
1f	total duration of <application usage summary instance>: time interval	total duration	total durations	total duration	0	time interval	application usage summary instance	
1f	total duration of <application usage summary>: time interval	total duration	total durations	total duration	0	time interval	application usage summary	
1f	total duration of <evaluation cycle>: time interval	total duration	total durations	total duration	0	time interval	evaluation cycle	
e0	total lower bound of <statistical bin>: floating point	total lower bound	total lower bounds	total lower bound	0	floating point	statistical bin	
e0	total of <statistic range>: statistical bin	total	totals	total	0	statistical bin	statistic range	
10	total processor core count: integer	total processor core count	total processor core counts	total processor core count	0	integer		
1f	total run count of <application usage summary instance>: integer	total run count	total run counts	total run count	0	integer	application usage summary instance	
1f	total run count of <application usage summary>: integer	total run count	total run counts	total run count	0	integer	application usage summary	
1f	total size of <download storage folder>: integer	total size	total sizes	total size	0	integer	download storage folder	
10	total space of <drive>: integer	total space	total spaces	total space	0	integer	drive	
d	total space of <filesystem>: integer	total space	total spaces	total space	0	integer	filesystem	
2	total space of <volume>: integer	total space	total spaces	total space	0	integer	volume	
e0	total upper bound of <statistical bin>: floating point	total upper bound	total upper bounds	total upper bound	0	floating point	statistical bin	
1f	total_width of <dmi memory_device>: integer	total_width	total_widths	total_width	0	integer	dmi memory_device	
e0	totals <time interval> of <statistic range>: statistical bin	total	totals	totals	1	statistical bin	statistic range	time interval
ff	tr <string> of <html>: html	tr	trs	tr	0	html	html	string
ff	tr <string> of <string>: html	tr	trs	tr	0	html	string	string
ff	tr of <html>: html	tr	trs	tr	0	html	html	
ff	tr of <string>: html	tr	trs	tr	0	html	string	
1f	track fixlets of <evaluation cycle>: string	track fixlet	track fixlets	track fixlets	1	string	evaluation cycle	
10	traverse permission of <access control entry>: boolean	traverse permission	traverse permissions	traverse permission	0	boolean	access control entry	
10	trigger strings of <scheduled task>: string	trigger string	trigger strings	trigger strings	1	string	scheduled task	
10	triggers of <task definition>: task trigger	trigger	triggers	triggers	1	task trigger	task definition	
ff	true: boolean	true	trues	true	0	boolean		
10	trustee of <access control entry>: security identifier	trustee	trustees	trustee	0	security identifier	access control entry	
10	trustee type of <access control entry>: integer	trustee type	trustee types	trustee type	0	integer	access control entry	
ff	tt <string> of <html>: html	tt	tts	tt	0	html	html	string
ff	tt <string> of <string>: html	tt	tts	tt	0	html	string	string
ff	tt of <html>: html	tt	tts	tt	0	html	html	
ff	tt of <string>: html	tt	tts	tt	0	html	string	
1f	tty of <logged on user>: string	tty	ttys	tty	0	string	logged on user	
d	tty of <process>: string	tty	ttys	tty	0	string	process	
d	tty of <user>: string	tty	ttys	tty	0	string	user	
ff	tuesday: day of week	tuesday	tuesdays	tuesday	0	day of week		
10	tunnel of <network adapter>: boolean	tunnel	tunnels	tunnel	0	boolean	network adapter	
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
d	type of <Xinetd Service>: string	type	types	type	0	string	Xinetd Service	
e0	type of <bes fixlet>: string	type	types	type	0	string	bes fixlet	
2	type of <bundle>: file type	type	types	type	0	file type	bundle	
2	type of <component>: string	type	types	type	0	string	component	
9	type of <debianpkg dependency>: string	type	types	type	0	string	debianpkg dependency	
b0	type of <distinguished name component>: string	type	types	type	0	string	distinguished name component	
1f	type of <dmi built_in_pointing_device>: integer	type	types	type	0	integer	dmi built_in_pointing_device	
1f	type of <dmi management_device>: integer	type	types	type	0	integer	dmi management_device	
1f	type of <dmi system_enclosure_or_chassis>: integer	type	types	type	0	integer	dmi system_enclosure_or_chassis	
10	type of <drive>: string	type	types	type	0	string	drive	
1f	type of <execution>: string	type	types	type	0	string	execution	
2	type of <file>: file type	type	types	type	0	file type	file	
d	type of <filesystem>: string	type	types	type	0	string	filesystem	
10	type of <firewall profile>: firewall profile type	type	types	type	0	firewall profile type	firewall profile	
10	type of <firewall service>: firewall service type	type	types	type	0	firewall service type	firewall service	
ff	type of <json value>: string	type	types	type	0	string	json value	
ff	type of <license>: string	type	types	type	0	string	license	
10	type of <metabase value>: metabase type	type	types	type	0	metabase type	metabase value	
10	type of <network adapter>: integer	type	types	type	0	integer	network adapter	
10	type of <network share>: integer	type	types	type	0	integer	network share	
2	type of <osxvalue>: string	type	types	type	0	string	osxvalue	
10	type of <processor>: integer	type	types	type	0	integer	processor	
2	type of <processor>: string	type	types	type	0	string	processor	
10	type of <registry key value>: registry key value type	type	types	type	0	registry key value type	registry key value	
2	type of <scsidevice>: string	type	types	type	0	string	scsidevice	
1f	type of <site>: string	type	types	type	0	string	site	
1f	type of <smbios structure>: integer	type	types	type	0	integer	smbios structure	
1f	type of <smbios value>: string	type	types	type	0	string	smbios value	
1f	type of <sqlite column type>: string	type	types	type	0	string	sqlite column type	
1f	type of <sqlite column>: sqlite column type	type	types	type	0	sqlite column type	sqlite column	
10	type of <task action>: task action type	type	types	type	0	task action type	task action	
10	type of <task trigger>: task trigger type	type	types	type	0	task trigger type	task trigger	
2	type of <volume>: string	type	types	type	0	string	volume	
10	type of <wmi select>: integer	type	types	type	0	integer	wmi select	
1f	type of <yaml value>: string	type	types	type	0	string	yaml value	
1f	type_detail of <dmi memory_device>: integer	type_detail	type_details	type_detail	0	integer	dmi memory_device	
ff	types: type	type	types	types	1	type		
1f	udp of <socket>: boolean	udp	udps	udp	0	boolean	socket	
10	udp: internet protocol	udp	udps	udp	0	internet protocol		
40	uid attribute of <bes idp directory>: string	uid attribute	uid attributes	uid attribute	0	string	bes idp directory	
e0	uid attribute of <bes ldap directory>: string	uid attribute	uid attributes	uid attribute	0	string	bes ldap directory	
d	uid of <filesystem object>: integer	uid	uids	uid	0	integer	filesystem object	
d	uid of <symlink>: integer	uid	uids	uid	0	integer	symlink	
5f	uinteger <integer>: uinteger	uinteger	uintegers	uinteger	0	uinteger		integer
5f	uinteger <string>: uinteger	uinteger	uintegers	uinteger	0	uinteger		string
ff	ul <string> of <html>: html	ul	uls	ul	0	html	html	string
ff	ul <string> of <string>: html	ul	uls	ul	0	html	string	string
ff	ul of <html>: html	ul	uls	ul	0	html	html	
ff	ul of <string>: html	ul	uls	ul	0	html	string	
ff	unary operators <string>: unary operator	unary operator	unary operators	unary operators	1	unary operator		string
ff	unary operators returning <type>: unary operator	unary operator returning	unary operators returning	unary operators returning	1	unary operator		type
ff	unary operators: unary operator	unary operator	unary operators	unary operators	1	unary operator		
d	unavailable amount of <ram>: integer	unavailable amount	unavailable amounts	unavailable amount	0	integer	ram	
ff	underflow of <floating point>: boolean	underflow	underflows	underflow	0	boolean	floating point	
10	unicast responses to multicast broadcast disabled of <firewall profile>: boolean	unicast responses to multicast broadcast disabled	unicast responses to multicast broadcast disableds	unicast responses to multicast broadcast disabled	0	boolean	firewall profile	
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
1f	unique id of <cloud provider>: string	unique id	unique ids	unique id	0	string	cloud provider	
4	unique name of <package>: string	unique name	unique names	unique name	0	string	package	
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
9	unique values of <debian package upstream version>: debian package upstream version with multiplicity	unique value	unique values	unique values	1	debian package upstream version with multiplicity	debian package upstream version	
9	unique values of <debian package version epoch>: debian package version epoch with multiplicity	unique value	unique values	unique values	1	debian package version epoch with multiplicity	debian package version epoch	
9	unique values of <debian package version revision>: debian package version revision with multiplicity	unique value	unique values	unique values	1	debian package version revision with multiplicity	debian package version revision	
9	unique values of <debian package version>: debian package version with multiplicity	unique value	unique values	unique values	1	debian package version with multiplicity	debian package version	
ff	unique values of <floating point>: floating point with multiplicity	unique value	unique values	unique values	1	floating point with multiplicity	floating point	
ff	unique values of <hertz>: hertz with multiplicity	unique value	unique values	unique values	1	hertz with multiplicity	hertz	
ff	unique values of <integer>: integer with multiplicity	unique value	unique values	unique values	1	integer with multiplicity	integer	
ff	unique values of <ipv4 address>: ipv4 address with multiplicity	unique value	unique values	unique values	1	ipv4 address with multiplicity	ipv4 address	
ff	unique values of <ipv4or6 address>: ipv4or6 address with multiplicity	unique value	unique values	unique values	1	ipv4or6 address with multiplicity	ipv4or6 address	
ff	unique values of <ipv6 address>: ipv6 address with multiplicity	unique value	unique values	unique values	1	ipv6 address with multiplicity	ipv6 address	
5f	unique values of <large integer>: large integer with multiplicity	unique value	unique values	unique values	1	large integer with multiplicity	large integer	
ff	unique values of <month and year>: month and year with multiplicity	unique value	unique values	unique values	1	month and year with multiplicity	month and year	
ff	unique values of <month>: month with multiplicity	unique value	unique values	unique values	1	month with multiplicity	month	
ff	unique values of <number of months>: number of months with multiplicity	unique value	unique values	unique values	1	number of months with multiplicity	number of months	
e2	unique values of <rate>: rate with multiplicity	unique value	unique values	unique values	1	rate with multiplicity	rate	
4	unique values of <rpm package release>: rpm package release with multiplicity	unique value	unique values	unique values	1	rpm package release with multiplicity	rpm package release	
4	unique values of <rpm package version record>: rpm package version record with multiplicity	unique value	unique values	unique values	1	rpm package version record with multiplicity	rpm package version record	
4	unique values of <rpm package version>: rpm package version with multiplicity	unique value	unique values	unique values	1	rpm package version with multiplicity	rpm package version	
4	unique values of <short rpm package version record>: short rpm package version record with multiplicity	unique value	unique values	unique values	1	short rpm package version record with multiplicity	short rpm package version record	
ff	unique values of <site version list>: site version list with multiplicity	unique value	unique values	unique values	1	site version list with multiplicity	site version list	
ff	unique values of <string>: string with multiplicity	unique value	unique values	unique values	1	string with multiplicity	string	
ff	unique values of <time interval>: time interval with multiplicity	unique value	unique values	unique values	1	time interval with multiplicity	time interval	
ff	unique values of <time of day with time zone>: time of day with time zone with multiplicity	unique value	unique values	unique values	1	time of day with time zone with multiplicity	time of day with time zone	
ff	unique values of <time of day>: time of day with multiplicity	unique value	unique values	unique values	1	time of day with multiplicity	time of day	
ff	unique values of <time range>: time range with multiplicity	unique value	unique values	unique values	1	time range with multiplicity	time range	
ff	unique values of <time zone>: time zone with multiplicity	unique value	unique values	unique values	1	time zone with multiplicity	time zone	
ff	unique values of <time>: time with multiplicity	unique value	unique values	unique values	1	time with multiplicity	time	
5f	unique values of <uinteger>: uinteger with multiplicity	unique value	unique values	unique values	1	uinteger with multiplicity	uinteger	
1f	unique values of <uuid>: uuid with multiplicity	unique value	unique values	unique values	1	uuid with multiplicity	uuid	
ff	unique values of <version>: version with multiplicity	unique value	unique values	unique values	1	version with multiplicity	version	
ff	unique values of <year>: year with multiplicity	unique value	unique values	unique values	1	year with multiplicity	year	
ff	universal time <string>: time	universal time	universal times	universal time	0	time		string
ff	universal time zone: time zone	universal time zone	universal time zones	universal time zone	0	time zone		
1f	unix of <operating system>: boolean	unix	unixes	unix	0	boolean	operating system	
e0	unknown computer count of <bes baseline component>: integer	unknown computer count	unknown computer counts	unknown computer count	0	integer	bes baseline component	
e0	unknown computer set of <bes baseline component>: bes computer set	unknown computer set	unknown computer sets	unknown computer set	0	bes computer set	bes baseline component	
10	unknown state of <running task>: boolean	unknown state	unknown states	unknown state	0	boolean	running task	
10	unknown state of <scheduled task>: boolean	unknown state	unknown states	unknown state	0	boolean	scheduled task	
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
f	up flag of <route>: boolean	up flag	up flags	up flag	0	boolean	route	
1f	up of <network adapter interface>: boolean	up	ups	up	0	boolean	network adapter interface	
1f	up of <network adapter>: boolean	up	ups	up	0	boolean	network adapter	
2	up of <network interface>: boolean	up	ups	up	0	boolean	network interface	
1f	up of <network ip interface>: boolean	up	ups	up	0	boolean	network ip interface	
d	update level of <operating system>: integer	update level	update levels	update level	0	integer	operating system	
1f	upload progress of <client>: string	upload progress	upload progresses	upload progress	0	string	client	
10	upnp firewall service type: firewall service type	upnp firewall service type	upnp firewall service types	upnp firewall service type	0	firewall service type		
ff	upper bound of <integer range>: integer	upper bound	upper bounds	upper bound	0	integer	integer range	
1f	upper_threshold_critical of <dmi management_device_threshold_data>: integer	upper_threshold_critical	upper_threshold_criticals	upper_threshold_critical	0	integer	dmi management_device_threshold_data	
1f	upper_threshold_non_critical of <dmi management_device_threshold_data>: integer	upper_threshold_non_critical	upper_threshold_non_criticals	upper_threshold_non_critical	0	integer	dmi management_device_threshold_data	
1f	upper_threshold_non_recoverable of <dmi management_device_threshold_data>: integer	upper_threshold_non_recoverable	upper_threshold_non_recoverables	upper_threshold_non_recoverable	0	integer	dmi management_device_threshold_data	
1f	ups of <power level>: boolean	ups	upss	ups	0	boolean	power level	
9	upstream of <debian package version>: debian package upstream version	upstream	upstreams	upstream	0	debian package upstream version	debian package version	
1f	uptime of <operating system>: time interval	uptime	uptimes	uptime	0	time interval	operating system	
e0	urgent flag of <bes action>: boolean	urgent flag	urgent flags	urgent flag	0	boolean	bes action	
10	uri of <task registration info>: string	uri	uris	uri	0	string	task registration info	
e0	url of <bes server>: string	url	urls	url	0	string	bes server	
e0	url of <bes site>: string	url	urls	url	0	string	bes site	
e0	url of <bes wizard>: string	url	urls	url	0	string	bes wizard	
1f	url of <site>: string	url	urls	url	0	string	site	
2	usb plane of <registryroot>: registrynode	usb plane	usb planes	usb plane	0	registrynode	registryroot	
2	usb: usb	usb	usbs	usb	0	usb		
10	use count of <network share>: integer	use count	use counts	use count	0	integer	network share	
10	use limit of <network share>: integer	use limit	use limits	use limit	0	integer	network share	
1f	use of <dmi physical_memory_array>: integer	use	uses	use	0	integer	dmi physical_memory_array	
40	use ssl of <bes idp directory>: boolean	use ssl	use ssls	use ssl	0	boolean	bes idp directory	
e0	use ssl of <bes ldap directory>: boolean	use ssl	use ssls	use ssl	0	boolean	bes ldap directory	
1f	used amount of <ram>: integer	used amount	used amounts	used amount	0	integer	ram	
f	used amount of <swap>: integer	used amount	used amounts	used amount	0	integer	swap	
d	used file count of <filesystem>: integer	used file count	used file counts	used file count	0	integer	filesystem	
d	used percent of <filesystem>: integer	used percent	used percents	used percent	0	integer	filesystem	
2	used percent of <volume>: integer	used percent	used percents	used percent	0	integer	volume	
d	used space of <filesystem>: integer	used space	used spaces	used space	0	integer	filesystem	
2	used space of <volume>: integer	used space	used spaces	used space	0	integer	volume	
12	user <string>: user	user	users	user	0	user		string
10	user comment of <user>: string	user comment	user comments	user comment	0	string	user	
5f	user count of <bes product>: integer	user count	user counts	user count	0	integer	bes product	
2	user domain: domain	user domain	user domains	user domain	0	domain		
d	user execute of <filesystem object>: boolean	user execute	user executes	user execute	0	boolean	filesystem object	
40	user filter of <bes idp directory>: string	user filter	user filters	user filter	0	string	bes idp directory	
e0	user filter of <bes ldap directory>: string	user filter	user filters	user filter	0	string	bes ldap directory	
e0	user flag of <bes filter>: boolean	user flag	user flags	user flag	0	boolean	bes filter	
10	user id of <logon task trigger>: string	user id	user ids	user id	0	string	logon task trigger	
10	user id of <session state change task trigger>: string	user id	user ids	user id	0	string	session state change task trigger	
10	user id of <task principal>: string	user id	user ids	user id	0	string	task principal	
1f	user id of <user>: integer	user id	user ids	user id	0	integer	user	
10	user intervals <activity history>: system power interval	user interval	user intervals	user intervals	1	system power interval		activity history
10	user key of <logged on user>: registry key	user key	user keys	user key	0	registry key	logged on user	
10	user language: string	user language	user languages	user language	0	string		
10	user locale: language	user locale	user locales	user locale	0	language		
d	user mask of <filesystem object>: integer	user mask	user masks	user mask	0	integer	filesystem object	
d	user mask of <mode>: mode_mask	user mask	user masks	user mask	0	mode_mask	mode	
d	user name of <filesystem object>: string	user name	user names	user name	0	string	filesystem object	
d	user name of <symlink>: string	user name	user names	user name	0	string	symlink	
10	user object count of <process>: integer	user object count	user object counts	user object count	0	integer	process	
d	user of <Xinetd Service>: string	user	users	user	0	string	Xinetd Service	
1f	user of <logged on user>: user	user	users	user	0	user	logged on user	
10	user of <process>: security identifier	user	users	user	0	security identifier	process	
d	user of <process>: user	user	users	user	0	user	process	
12	user of <security identifier>: user	user	users	user	0	user	security identifier	
10	user privilege of <user>: boolean	user privilege	user privileges	user privilege	0	boolean	user	
d	user read of <filesystem object>: boolean	user read	user reads	user read	0	boolean	filesystem object	
e0	user set of <bes filter>: bes user set	user set	user sets	user set	0	bes user set	bes filter	
e0	user set of <bes role>: bes user set	user set	user sets	user set	0	bes user set	bes role	
10	user sid of <event log record>: security identifier	user sid	user sids	user sid	0	security identifier	event log record	
2	user temp folder of <domain>: folder	user temp folder	user temp folders	user temp folder	0	folder	domain	
2	user temp folder: folder	user temp folder	user temp folders	user temp folder	0	folder		
10	user time of <process>: time interval	user time	user times	user time	0	time interval	process	
10	user type of <metabase value>: metabase user type	user type	user types	user type	0	metabase user type	metabase value	
10	user ui language: language	user ui language	user ui languages	user ui language	0	language		
d	user write of <filesystem object>: boolean	user write	user writes	user write	0	boolean	filesystem object	
d	users <string>: user	user	users	users	1	user		string
2	users folder of <domain>: folder	users folder	users folders	users folder	0	folder	domain	
2	users folder: folder	users folder	users folders	users folder	0	folder		
e0	users of <bes role>: bes user	user	users	users	1	bes user	bes role	
1f	users: user	user	users	users	1	user		
ff	usual name of <property>: string	usual name	usual names	usual name	0	string	property	
e0	utc time flag of <bes action>: boolean	utc time flag	utc time flags	utc time flag	0	boolean	bes action	
2	utilities folder of <domain>: folder	utilities folder	utilities folders	utilities folder	0	folder	domain	
2	utilities folder: folder	utilities folder	utilities folders	utilities folder	0	folder		
1f	uuid <binary_string>: uuid	uuid	uuids	uuid	0	uuid		binary_string
1f	uuid <string>: uuid	uuid	uuids	uuid	0	uuid		string
1f	uuid of <dmi system_information>: uuid	uuid	uuids	uuid	0	uuid	dmi system_information	
d	uuid of <filesystem>: string	uuid	uuids	uuid	0	string	filesystem	
1f	uuid of <hardware>: uuid	uuid	uuids	uuid	0	uuid	hardware	
1f	uuid of <operating system>: uuid	uuid	uuids	uuid	0	uuid	operating system	
10	v1 compatibility of <task settings>: boolean	v1 compatibility	v1 compatibilities	v1 compatibility	0	boolean	task settings	
10	v2 compatibility of <task settings>: boolean	v2 compatibility	v2 compatibilities	v2 compatibility	0	boolean	task settings	
10	value <string> of <file version block>: string	value	values	value	0	string	file version block	string
10	value <string> of <registry key>: registry key value	value	values	value	0	registry key value	registry key	string
d	value accessible of <symlink>: boolean	value accessible	values accessible	value accessible	0	boolean	symlink	
e0	value count of <bes property result>: integer	value count	value counts	value count	0	integer	bes property result	
e0	value of <bes action parameter>: string	value	values	value	0	string	bes action parameter	
e0	value of <bes client setting>: string	value	values	value	0	string	bes client setting	
e0	value of <bes deployment option>: string	value	values	value	0	string	bes deployment option	
40	value of <bes tag>: string	value	values	value	0	string	bes tag	
e0	value of <bes unmanagedasset field>: string	value	values	value	0	string	bes unmanagedasset field	
e0	value of <bes wizard variable>: string	value	values	value	0	string	bes wizard variable	
2	value of <dictionaryentry>: osxvalue	value	values	value	0	osxvalue	dictionaryentry	
b0	value of <distinguished name component>: string	value	values	value	0	string	distinguished name component	
1f	value of <environment variable>: string	value	values	value	0	string	environment variable	
1f	value of <fixlet_header>: string	value	values	value	0	string	fixlet_header	
ff	value of <json key>: json value	value	values	value	0	json value	json key	
e0	value of <mime field>: string	value	values	value	0	string	mime field	
14	value of <plugin store key>: string	value	values	value	0	string	plugin store key	
d	value of <runlevel>: string	value	values	value	0	string	runlevel	
1f	value of <setting>: string	value	values	value	0	string	setting	
10	value of <site profile variable>: string	value	values	value	0	string	site profile variable	
d	value of <symlink>: string	value	values	value	0	string	symlink	
10	value of <task named value pair>: string	value	values	value	0	string	task named value pair	
2	value of <user attribute>: string	value	values	value	0	string	user attribute	
10	value of <winrt enumeration>: integer	value	values	value	0	integer	winrt enumeration	
1f	value of <yaml key>: yaml value	value	values	value	0	yaml value	yaml key	
10	value queries of <event task trigger>: task named value pair	value query	value queries	value queries	1	task named value pair	event task trigger	
1f	values <string> of <smbios structure>: smbios value	value	values	values	1	smbios value	smbios structure	string
2	values of <array>: osxvalue	value	values	values	1	osxvalue	array	
e0	values of <bes fixlet field>: bes fixlet field value	value	values	values	1	bes fixlet field value	bes fixlet field	
e0	values of <bes property result>: string	value	values	values	1	string	bes property result	
10	values of <metabase key>: metabase value	value	values	values	1	metabase value	metabase key	
10	values of <registry key>: registry key value	value	values	values	1	registry key value	registry key	
1f	values of <smbios structure>: smbios value	value	values	values	1	smbios value	smbios structure	
ff	var <string> of <html>: html	var	vars	var	0	html	html	string
ff	var <string> of <string>: html	var	vars	var	0	html	string	string
ff	var of <html>: html	var	vars	var	0	html	html	
ff	var of <string>: html	var	vars	var	0	html	string	
1f	variable <string> of <environment>: environment variable	variable	variables	variable	0	environment variable	environment	string
10	variables <string> of <site profile>: site profile variable	variable	variables	variables	1	site profile variable	site profile	string
e0	variables of <bes wizard>: bes wizard variable	variable	variables	variables	1	bes wizard variable	bes wizard	
1f	variables of <environment>: environment variable	variable	variables	variables	1	environment variable	environment	
1f	variables of <file>: string	variable	variables	variables	1	string	file	
10	variables of <site profile>: site profile variable	variable	variables	variables	1	site profile variable	site profile	
e0	variance of <statistical bin>: floating point	variance	variances	variance	0	floating point	statistical bin	
1f	vendor name of <processor>: string	vendor name	vendor names	vendor name	0	string	processor	
1f	vendor of <dmi bios_information>: string	vendor	vendors	vendor	0	string	dmi bios_information	
2	vendor of <scsidevice>: string	vendor	vendors	vendor	0	string	scsidevice	
1f	vendor_syndrome of <dmi b32_bit_memory_error_information>: integer	vendor_syndrome	vendor_syndromes	vendor_syndrome	0	integer	dmi b32_bit_memory_error_information	
1f	vendor_syndrome of <dmi b64_bit_memory_error_information>: integer	vendor_syndrome	vendor_syndromes	vendor_syndrome	0	integer	dmi b64_bit_memory_error_information	
9	verfiles of <debian versioned package>: debianpkg verfile	verfile	verfiles	verfiles	1	debianpkg verfile	debian versioned package	
2	version <integer> of <file>: version	version	versions	version	0	version	file	integer
ff	version <string>: version	version	versions	version	0	version		string
10	version block <integer> of <file>: file version block	version block	version blocks	version block	0	file version block	file	integer
10	version block <string> of <file>: file version block	version block	version blocks	version block	0	file version block	file	string
10	version blocks of <file>: file version block	version block	version blocks	version blocks	1	file version block	file	
1f	version info of <execution>: string	version info	version infos	version info	0	string	execution	
1f	version of <application usage summary instance>: version	version	versions	version	0	version	application usage summary instance	
e0	version of <bes site>: integer	version	versions	version	0	integer	bes site	
1f	version of <bios>: string	version	versions	version	0	string	bios	
2	version of <bundle>: version	version	versions	version	0	version	bundle	
4	version of <capability>: string	version	versions	version	0	string	capability	
f	version of <client>: version	version	versions	version	0	version	client	
1f	version of <cloud provider>: string	version	versions	version	0	string	cloud provider	
2	version of <component>: version	version	versions	version	0	version	component	
ff	version of <cryptography>: string	version	versions	version	0	string	cryptography	
1f	version of <current relay>: version	version	versions	version	0	version	current relay	
9	version of <debian versioned package>: debian package version	version	versions	version	0	debian package version	debian versioned package	
9	version of <debianpkg dependency>: debian package version	version	versions	version	0	debian package version	debianpkg dependency	
9	version of <debianpkg reverse dependencies>: string	version	versions	version	0	string	debianpkg reverse dependencies	
1f	version of <dmi base_board_information>: string	version	versions	version	0	string	dmi base_board_information	
1f	version of <dmi system_enclosure_or_chassis>: string	version	versions	version	0	string	dmi system_enclosure_or_chassis	
1f	version of <dmi system_information>: string	version	versions	version	0	string	dmi system_information	
10	version of <file>: version	version	versions	version	0	version	file	
2	version of <filesystem object>: version	version	versions	version	0	version	filesystem object	
2	version of <folder>: version	version	versions	version	0	version	folder	
ff	version of <module>: version	version	versions	version	0	version	module	
1f	version of <operating system>: version	version	versions	version	0	version	operating system	
4	version of <package>: version	version	versions	version	0	version	package	
1f	version of <registration server>: version	version	versions	version	0	version	registration server	
4	version of <rpm package version record>: rpm package version	version	versions	version	0	rpm package version	rpm package version record	
2	version of <scsibus>: version	version	versions	version	0	version	scsibus	
1d	version of <service>: version	version	versions	version	0	version	service	
4	version of <short rpm package version record>: rpm package version	version	versions	version	0	rpm package version	short rpm package version record	
1f	version of <site>: integer	version	versions	version	0	integer	site	
10	version of <task registration info>: string	version	versions	version	0	string	task registration info	
2	version of <usb>: version	version	versions	version	0	version	usb	
10	version of <winrt package id>: version	version	versions	version	0	version	winrt package id	
ff	version of <x509 certificate>: integer	version	versions	version	0	integer	x509 certificate	
ff	version string <string> of <module>: string	version string	version strings	version string	0	string	module	string
10	version strings of <bios>: string	version string	version strings	version strings	1	string	bios	
1f	virtual machine of <operating system>: boolean	virtual machine	virtual machines	virtual machine	0	boolean	operating system	
2	virtual memory: boolean	virtual memory	virtual memories	virtual memory	0	boolean		
1f	virtual of <hardware>: boolean	virtual	virtuals	virtual	0	boolean	hardware	
10	virtualizer of <application>: string	virtualizer	virtualizers	virtualizer	0	string	application	
e0	visible flag of <bes fixlet>: boolean	visible flag	visible flags	visible flag	0	boolean	bes fixlet	
12	visible networks of <wifi>: wifi network	visible network	visible networks	visible networks	1	wifi network	wifi	
2	visible of <file>: boolean	visible	visibles	visible	0	boolean	file	
2	voices folder of <domain>: folder	voices folder	voices folders	voices folder	0	folder	domain	
2	voices folder: folder	voices folder	voices folders	voices folder	0	folder		
10	volatile attribute of <metabase value>: boolean	volatile attribute	volatile attributes	volatile attribute	0	boolean	metabase value	
1f	voltage of <dmi processor_information>: integer	voltage	voltages	voltage	0	integer	dmi processor_information	
1f	voltage_probe <integer> of <dmi>: dmi voltage_probe	voltage_probe	voltage_probes	voltage_probe	0	dmi voltage_probe	dmi	integer
1f	voltage_probes of <dmi>: dmi voltage_probe	voltage_probe	voltage_probes	voltage_probes	1	dmi voltage_probe	dmi	
2	volume <integer>: volume	volume	volumes	volume	0	volume		integer
10	volume of <drive>: string	volume	volumes	volume	0	string	drive	
2	volume of <file>: volume	volume	volumes	volume	0	volume	file	
d	volume of <filesystem>: string	volume	volumes	volume	0	string	filesystem	
2	volume of <folder>: volume	volume	volumes	volume	0	volume	folder	
2	volume settings folder of <domain>: folder	volume settings folder	volume settings folders	volume settings folder	0	folder	domain	
2	volume settings folder: folder	volume settings folder	volume settings folders	volume settings folder	0	folder		
2	volumes <string>: volume	volume	volumes	volumes	1	volume		string
2	volumes: volume	volume	volumes	volumes	1	volume		
d	wait of <Xinetd Service>: boolean	wait	waits	wait	0	boolean	Xinetd Service	
10	wait timeout of <task idle settings>: time interval	wait timeout	wait timeouts	wait timeout	0	time interval	task idle settings	
1f	waiting for download of <action>: boolean	waiting for download	waiting for downloads	waiting for download	0	boolean	action	
1f	wake on lan cidr subnet: cidr subnet	wake on lan cidr subnet	wake on lan cidr subnets	wake on lan cidr subnet	0	cidr subnet		
1f	wake on lan subnet cidr string: string	wake on lan subnet cidr string	wake on lan subnet cidr strings	wake on lan subnet cidr string	0	string		
10	wake to run of <task settings>: boolean	wake to run	wake to runs	wake to run	0	boolean	task settings	
1f	wake_up_type of <dmi system_information>: integer	wake_up_type	wake_up_types	wake_up_type	0	integer	dmi system_information	
10	wakeonlan enabled of <network adapter>: boolean	wakeonlan enabled	wakeonlan enableds	wakeonlan enabled	0	boolean	network adapter	
10	warning event log event type: event log event type	warning event log event type	warning event log event types	warning event log event type	0	event log event type		
2	wascloned flag of <route>: boolean	wascloned flag	wascloned flags	wascloned flag	0	boolean	route	
d	web reports service: service	web reports service	web reports services	web reports service	0	service		
e0	webui enabled: boolean	webui enabled	webuis enabled	webui enabled	0	boolean		
1d	webui service: service	webui service	webui services	webui service	0	service		
ff	wednesday: day of week	wednesday	wednesdays	wednesday	0	day of week		
ff	week: time interval	week	weeks	week	0	time interval		
10	weekly task trigger type: task trigger type	weekly task trigger type	weekly task trigger types	weekly task trigger type	0	task trigger type		
10	weeks interval of <weekly task trigger>: time interval	weeks interval	weeks intervals	weeks interval	0	time interval	weekly task trigger	
1f	weight of <selected server>: integer	weight	weights	weight	0	integer	selected server	
10	well known account <integer>: security account	well known account	well known accounts	well known account	0	security account		integer
2	wide16 scsi of <scsibus>: boolean	wide16 scsi	wide16 scsis	wide16 scsi	0	boolean	scsibus	
2	wide32 scsi of <scsibus>: boolean	wide32 scsi	wide32 scsis	wide32 scsi	0	boolean	scsibus	
12	wifi of <network adapter>: wifi	wifi	wifis	wifi	0	wifi	network adapter	
10	win32 exit code of <service>: integer	win32 exit code	win32 exit codes	win32 exit code	0	integer	service	
10	win32 running services: service	win32 running service	win32 running services	win32 running services	1	service		
10	win32 services: service	win32 service	win32 services	win32 services	1	service		
10	win32 type of <service>: boolean	win32 type	win32 types	win32 type	0	boolean	service	
d	window of <route>: integer	window	windows	window	0	integer	route	
10	windows checksum of <file>: integer	windows checksum	windows checksums	windows checksum	0	integer	file	
f0	windows display time <string>: time	windows display time	windows display times	windows display time	0	time		string
10	windows file <string>: file	windows file	windows files	windows file	0	file		string
10	windows folder: folder	windows folder	windows folders	windows folder	0	folder		
1f	windows of <operating system>: boolean	windows	windowses	windows	0	boolean	operating system	
ff	windows server count of <bes product>: integer	windows server count	windows server counts	windows server count	0	integer	bes product	
10	winrt package <string>: winrt package	winrt package	winrt packages	winrt package	0	winrt package		string
10	winrt package users of <winrt package>: winrt package user information	winrt package user	winrt package users	winrt package users	1	winrt package user information	winrt package	
10	winrt packages of <user>: winrt package	winrt package	winrt packages	winrt packages	1	winrt package	user	
10	winrt packages: winrt package	winrt package	winrt packages	winrt packages	1	winrt package		
10	wins enabled of <network adapter>: boolean	wins enabled	wins enableds	wins enabled	0	boolean	network adapter	
10	winsock2 supported of <network>: boolean	winsock2 supported	winsock2 supporteds	winsock2 supported	0	boolean	network	
e0	wizard data of <bes fixlet>: html	wizard data	wizard datas	wizard data	0	html	bes fixlet	
e0	wizard link of <bes fixlet>: string	wizard link	wizard links	wizard link	0	string	bes fixlet	
e0	wizard name of <bes fixlet>: string	wizard name	wizard names	wizard name	0	string	bes fixlet	
e0	wizard of <bes wizard variable>: bes wizard	wizard	wizards	wizard	0	bes wizard	bes wizard variable	
e0	wizard set of <bes site>: bes wizard set	wizard set	wizard sets	wizard set	0	bes wizard set	bes site	
e0	wizards of <bes site>: bes wizard	wizard	wizards	wizards	1	bes wizard	bes site	
10	wmi <string>: wmi	wmi	wmis	wmi	0	wmi		string
10	wmi: wmi	wmi	wmis	wmi	0	wmi		
10	working directory of <exec task action>: string	working directory	working directories	working directory	0	string	exec task action	
10	working set size of <process>: integer	working set size	working set sizes	working set size	0	integer	process	
ff	workstation count of <bes product>: integer	workstation count	workstation counts	workstation count	0	integer	bes product	
10	workstation trust account flag of <user>: boolean	workstation trust account flag	workstation trust account flags	workstation trust account flag	0	boolean	user	
10	wow64 of <process>: boolean	wow64	wow64s	wow64	0	boolean	process	
10	wow64 of <registry key>: boolean	wow64	wow64s	wow64	0	boolean	registry key	
d	wp of <processor>: boolean	wp	wps	wp	0	boolean	processor	
10	write attributes permission of <access control entry>: boolean	write attributes permission	write attributes permissions	write attributes permission	0	boolean	access control entry	
10	write dac permission of <access control entry>: boolean	write dac permission	write dac permissions	write dac permission	0	boolean	access control entry	
10	write extended attributes permission of <access control entry>: boolean	write extended attributes permission	write extended attributes permissions	write extended attributes permission	0	boolean	access control entry	
d	write of <mode_mask>: boolean	write	writes	write	0	boolean	mode_mask	
10	write owner permission of <access control entry>: boolean	write owner permission	write owner permissions	write owner permission	0	boolean	access control entry	
10	write permission of <access control entry>: boolean	write permission	write permissions	write permission	0	boolean	access control entry	
10	write permission of <network share>: boolean	write permission	write permissions	write permission	0	boolean	network share	
e0	writer set of <bes site>: bes user set	writer set	writer sets	writer set	0	bes user set	bes site	
e0	writers of <bes site>: bes user	writer	writers	writers	1	bes user	bes site	
10	x32 application <string>: application	x32 application	x32 applications	x32 application	0	application		string
10	x32 file <string> of <encoding>: file	x32 file	x32 files	x32 file	0	file	encoding	string
10	x32 file <string>: file	x32 file	x32 files	x32 file	0	file		string
10	x32 folder <string> of <encoding>: folder	x32 folder	x32 folders	x32 folder	0	folder	encoding	string
10	x32 folder <string>: folder	x32 folder	x32 folders	x32 folder	0	folder		string
10	x32 of <operating system>: boolean	x32	x32s	x32	0	boolean	operating system	
10	x32 registry: registry	x32 registry	x32 registries	x32 registry	0	registry		
10	x64 application <string>: application	x64 application	x64 applications	x64 application	0	application		string
10	x64 file <string> of <encoding>: file	x64 file	x64 files	x64 file	0	file	encoding	string
10	x64 file <string>: file	x64 file	x64 files	x64 file	0	file		string
10	x64 folder <string> of <encoding>: folder	x64 folder	x64 folders	x64 folder	0	folder	encoding	string
10	x64 folder <string>: folder	x64 folder	x64 folders	x64 folder	0	folder		string
10	x64 of <operating system>: boolean	x64	x64s	x64	0	boolean	operating system	
10	x64 registry: registry	x64 registry	x64 registries	x64 registry	0	registry		
10	x64 variable <string> of <environment>: environment variable	x64 variable	x64 variables	x64 variable	0	environment variable	environment	string
10	x64 variables of <environment>: environment variable	x64 variable	x64 variables	x64 variables	1	environment variable	environment	
d	xinetd services <string>: Xinetd Service	xinetd service	xinetd services	xinetd services	1	Xinetd Service		string
d	xinetd services: Xinetd Service	xinetd service	xinetd services	xinetd services	1	Xinetd Service		
1d	xml document of <file>: xml dom document	xml document	xml documents	xml document	0	xml dom document	file	
bd	xml document of <string>: xml dom document	xml document	xml documents	xml document	0	xml dom document	string	
10	xml of <event log record>: xml dom node	xml	xmls	xml	0	xml dom node	event log record	
10	xml of <scheduled task>: string	xml	xmls	xml	0	string	scheduled task	
10	xml of <task definition>: string	xml	xmls	xml	0	string	task definition	
10	xml of <task registration info>: string	xml	xmls	xml	0	string	task registration info	
10	xml of <task settings>: string	xml	xmls	xml	0	string	task settings	
bd	xpaths <( string, string )> of <xml dom node>: xml dom node	xpath	xpaths	xpaths	1	xml dom node	xml dom node	( string, string )
bd	xpaths <string> of <xml dom node>: xml dom node	xpath	xpaths	xpaths	1	xml dom node	xml dom node	string
2	xresolve flag of <route>: boolean	xresolve flag	xresolve flags	xresolve flag	0	boolean	route	
1f	yaml of <file>: yaml value	yaml	yamls	yaml	0	yaml value	file	
1f	yaml of <string>: yaml value	yaml	yamls	yaml	0	yaml value	string	
ff	year <integer>: year	year	years	year	0	year		integer
ff	year <string>: year	year	years	year	0	year		string
ff	year of <date>: year	year	years	year	0	year	date	
ff	year of <month and year>: year	year	years	year	0	year	month and year	
ff	year: number of months	year	years	year	0	number of months		
ff	zone of <time of day with time zone>: time zone	zone	zones	zone	0	time zone	time of day with time zone	
ff	zoned time_of_day <string>: time of day with time zone	zoned time_of_day	zoned times_of_day	zoned time_of_day	0	time of day with time zone		string
"""

# 475 rows
TYPES: str = """\
5f			1
d	SELinux Boolean		40
d	Xinetd Service		456
10	access control entry		4
10	access control list		4
1f	action		176
1f	action lock state		4
10	active device		36
12	active directory group		408
12	active directory local computer		528
12	active directory local user		536
12	active directory server		1
10	activity history		12
1f	administrative rights		1
12	agent interface		1
12	agent interface capability		1
1f	analysis		8
1f	application	file	832
1f	application usage summary		160
1f	application usage summary instance		120
2	array		8
10	audit policy		1
10	audit policy category		16
10	audit policy information		4
10	audit policy subcategory		4
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
5f	bes product		8
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
5f	binary operator		8
5f	binary position	integer	144
5f	binary_string		136
5f	binary_substring	binary_string	136
1f	bios		1
5f	bit set		8
5f	boolean		1
10	boot task trigger	task trigger	56
2	bundle		24
4	capability		32
5f	cast		8
1f	cidr subnet		58
1f	client	application	832
2	client process owner		1
1f	client_cryptography		40
1f	cloud provider		1
10	com handler task action	task action	12
2	component		8
2	computer		1
10	connection		4
10	connection status		4
2	country		4
1f	cpupackage		1
5f	cryptography		72
1f	current relay		1
10	daily task trigger	task trigger	56
2	datafork		8
5f	date		24
5f	date with multiplicity	date	32
5f	day of month		8
5f	day of month with multiplicity	day of month	16
5f	day of week		4
5f	day of week with multiplicity	day of week	16
5f	day of year		16
5f	day of year with multiplicity	day of year	24
9	debian base package		8
9	debian package upstream version		32
9	debian package upstream version with multiplicity	debian package upstream version	40
9	debian package version		32
9	debian package version epoch		32
9	debian package version epoch with multiplicity	debian package version epoch	40
9	debian package version revision		32
9	debian package version revision with multiplicity	debian package version revision	40
9	debian package version with multiplicity	debian package version	40
9	debian versioned package		8
9	debianpackagecache		16
9	debianpkg dependency		8
9	debianpkg reverse dependencies		8
9	debianpkg verfile		8
9	debianpkg version		8
d	device file	filesystem object	832
2	dictionary		8
2	dictionaryentry		32
10	discretionary access control list	access control list	8
10	distinguished name	string	252
10	distinguished name component	string	104
1d	dmi		8
1f	dmi additional_information		16
1f	dmi b32_bit_memory_error_information		16
1f	dmi b64_bit_memory_error_information		16
1f	dmi base_board_information		16
1f	dmi bios_information		16
1f	dmi bios_language_information		16
1f	dmi built_in_pointing_device		16
1f	dmi cache_information		16
1f	dmi cooling_device		16
1f	dmi electrical_current_probe		16
1f	dmi end_of_table		16
1f	dmi group_associations		16
1f	dmi hardware_security		16
1f	dmi inactive		16
1f	dmi ipmi_device_information		16
1f	dmi management_device		16
1f	dmi management_device_component		16
1f	dmi management_device_threshold_data		16
1f	dmi memory_array_mapped_address		16
1f	dmi memory_channel		16
1f	dmi memory_controller_information		16
1f	dmi memory_device		16
1f	dmi memory_device_mapped_address		16
1f	dmi memory_module_information		16
1f	dmi oem_strings		16
1f	dmi on_board_devices_information		16
1f	dmi onboard_devices_extended_information		16
1f	dmi out_of_band_remote_access		16
1f	dmi physical_memory_array		16
1f	dmi port_connector_information		16
1f	dmi portable_battery		16
1f	dmi processor_information		16
1f	dmi system_boot_information		16
1f	dmi system_configuration_option		16
1f	dmi system_enclosure_or_chassis		16
1f	dmi system_information		16
1f	dmi system_power_controls		16
1f	dmi system_power_supply		16
1f	dmi system_reset		16
1f	dmi system_slots		16
1f	dmi temperature_probe		16
1f	dmi voltage_probe		16
2	domain		2
1f	download server		1
1f	download storage folder	folder	832
10	drive		84
2	dummy		1
2	dummy type		1
10	email task action	task action	12
2	enableable_file	file	656
1f	encoding		64
1f	environment		48
1f	environment variable		192
1f	evaluation cycle		120
10	event log		116
10	event log event type		2
10	event log record		152
10	event task trigger	task trigger	56
10	exec task action	task action	12
1f	execution		72
42	exponential projection		32
d	fifo file	filesystem object	832
1f	file	filesystem object	832
1f	file content		16
1f	file line	string	184
1f	file section		280
10	file shortcut		324
2	file signature		4
2	file type		4
10	file version block		12
d	filesystem		608
1f	filesystem object		832
12	firewall		80
12	firewall action		4
10	firewall authorized application		4
10	firewall icmp settings		4
10	firewall local policy modify state		4
10	firewall open port		4
10	firewall policy		8
10	firewall profile		12
10	firewall profile type		4
10	firewall remote admin settings		4
12	firewall rule		72
10	firewall scope		4
10	firewall service		4
10	firewall service restriction		8
10	firewall service type		4
1f	fixlet		64
40	fixlet count pair		104
1f	fixlet_header		32
5f	floating point		24
5f	floating point with multiplicity	floating point	32
1f	folder	filesystem object	832
5f	format		128
d	grub block list		32
d	grub bootable image		640
d	grub color		32
d	grub color pair		72
d	grub color scheme		160
d	grub config file		640
d	grub device		32
d	grub file location		152
d	grub image choice		48
d	grub kernel		176
d	grub module		40
1f	hardware		8
5f	hertz		8
5f	hertz with multiplicity	hertz	16
40	historical computer count		24
40	historical fixlet count		64
5f	html		160
5f	html attribute list		16
10	idle task trigger	task trigger	56
1f	instance data		16
5f	integer		8
5f	integer range		16
5f	integer set		24
5f	integer with multiplicity	integer	16
10	internet connection firewall		4
10	internet protocol		4
5f	ip version		4
5f	ipv4 address	ipv4or6 address	28
5f	ipv4 address with multiplicity	ipv4 address	40
5f	ipv4or6 address		28
5f	ipv4or6 address with multiplicity	ipv4or6 address	40
5f	ipv6 address	ipv4or6 address	28
5f	ipv6 address with multiplicity	ipv6 address	40
5f	json key		160
5f	json value		16
1d	language		144
5f	large integer		24
5f	large integer with multiplicity	large integer	32
5f	license		2016
42	linear projection		32
10	local group	security account	24
10	local group member	security account	16
10	local mssql database		84
1f	logged on user		208
10	logon task trigger	task trigger	56
1f	manual group		192
10	media type		4
10	metabase		4
10	metabase identifier		4
10	metabase key		36
10	metabase type		4
10	metabase user type		4
10	metabase value		24
40	mime field		8
d	mode		4
d	mode_mask		1
5f	module		8
12	monitor power interval		32
5f	month		4
5f	month and year		16
5f	month and year with multiplicity	month and year	24
5f	month with multiplicity	month	16
10	monthly task trigger	task trigger	56
10	monthlydow task trigger	task trigger	56
1f	network		32
1f	network adapter		8
1f	network adapter interface		200
10	network address list		4
1f	network interface		48
1f	network ip interface	network interface	200
2	network link interface	network interface	64
10	network share		8
2	nothing		1
5f	number of months		8
5f	number of months with multiplicity	number of months	16
1f	operating system		256
10	operating system product type		8
10	operating system suite mask	bit set	8
2	os log entry log		8
2	os log store		8
2	osxvalue		24
4	package		88
14	plugin store		168
14	plugin store key		304
10	port mapping		4
12	power history		48
1f	power level		8
12	power state		4
2	preference		24
1d	primary language		96
10	priority class		4
1f	process		152
1f	processor		216
5f	property		8
1f	ram		48
42	rate		24
42	rate with multiplicity	rate	32
1f	registration server		1
10	registration task trigger	task trigger	56
10	registry		4
10	registry key		96
10	registry key value		100
10	registry key value type		4
2	registrynode		152
2	registryroot		24
5f	regular expression		16
5f	regular expression match	substring	160
2	resfork		8
1f	restricted site		56
1f	root server		1
5f	rope		160
f	route		88
f	routing table		24
4	rpm package release		8
4	rpm package release with multiplicity	rpm package release	16
4	rpm package version		8
4	rpm package version record		24
4	rpm package version record with multiplicity	rpm package version record	32
4	rpm package version with multiplicity	rpm package version	16
4	rpmdatabase		24
d	runlevel		16
10	running task		4
10	scheduled task		112
2	scsibus		1
2	scsidevice		1
10	security account		8
10	security database		1
10	security descriptor		24
12	security identifier		40
1f	selected server		8
1f	server based group		192
1d	service		256
10	session state change task trigger	task trigger	56
1f	setting		552
4	short rpm package version record		24
4	short rpm package version record with multiplicity	short rpm package version record	32
10	show message task action	task action	12
1f	site		8
1f	site group		16
10	site profile		8
10	site profile variable		12
5f	site version list		512
5f	site version list with multiplicity	site version list	520
1f	smbios		8
1f	smbios structure		24
1f	smbios value		248
1f	socket		64
d	socket file	filesystem object	832
1f	sqlite column		168
1f	sqlite column type		152
1f	sqlite database		216
1f	sqlite row		8
1f	sqlite statement		16
1f	sqlite table		152
2	stage		1
40	statistic range		16
40	statistical bin		240
5f	string		144
5f	string position	integer	152
5f	string set		24
5f	string with multiplicity	string	152
4d	strverscmp version	version	56
5f	substring	string	144
f	swap		24
d	symlink		816
10	system access control list	access control list	8
12	system power interval		24
10	task action		8
10	task action type		4
10	task definition		8
10	task folder		4
10	task idle settings		8
10	task named value pair		4
10	task network settings		8
10	task principal		8
10	task registration info		8
10	task repetition pattern		52
10	task settings		8
10	task trigger		52
10	task trigger type		4
1f	tcp state		4
5f	time		8
5f	time interval		8
5f	time interval with multiplicity	time interval	16
5f	time of day		8
5f	time of day with multiplicity	time of day	16
5f	time of day with time zone		16
5f	time of day with time zone with multiplicity	time of day with time zone	24
5f	time range		16
5f	time range with multiplicity	time range	24
10	time task trigger	task trigger	56
5f	time with multiplicity	time	16
5f	time zone		8
5f	time zone with multiplicity	time zone	16
5f	tuple item		152
5f	type		8
5f	uinteger		8
5f	uinteger with multiplicity	uinteger	16
5f	unary operator		8
5f	undefined		1
2	usb		4
1f	user		200
2	user attribute		192
5f	utf8 string		16
1f	uuid		16
1f	uuid with multiplicity	uuid	24
5f	version		56
5f	version with multiplicity	version	64
2	volume	folder	968
10	weekly task trigger	task trigger	56
12	wifi		8
12	wifi network		88
10	winrt enumeration		28
10	winrt package		188
10	winrt package id		188
10	winrt package user information		52
10	wmi		8
10	wmi object		4
10	wmi select		32
5f	x509 certificate		712
1d	xml dom document	xml dom node	40
1d	xml dom node		24
1f	yaml key		208
1f	yaml value		64
5f	year		8
5f	year with multiplicity	year	16
"""

# 7 rows
UNARY_OPERATORS: str = """\
5f	- <floating point>: floating point	minus	-	floating point	floating point
5f	- <hertz>: hertz	minus	-	hertz	hertz
5f	- <integer>: integer	minus	-	integer	integer
5f	- <large integer>: large integer	minus	-	large integer	large integer
5f	- <number of months>: number of months	minus	-	number of months	number of months
42	- <rate>: rate	minus	-	rate	rate
5f	- <time interval>: time interval	minus	-	time interval	time interval
"""
