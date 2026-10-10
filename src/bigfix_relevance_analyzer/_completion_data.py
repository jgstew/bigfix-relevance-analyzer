"""Completion ranking counts, mined from content. Do not edit by hand.

Regenerate with ``uv run python tools/generate_completion_data.py <content repo>
[<content repo> ...]``; see that script for what is mined, and
``tests/test_completion_data.py`` for what every regeneration must keep.

One row per line, tab-separated: context kind, consumer, whether the consumer
has an index, outer consumer (``-`` for none), producer, then how many distinct
statements used it, how many of those wrote the producer with an index, and how
many wrote it plural. Inspector names and counts only: no content.
"""

from __future__ import annotations

SCHEMA_VERSION: int = 1

SOURCES: tuple[str, ...] = (
    "d524c7381bd53fb7f9ddb826d1ced9223c721d82",
    "unknown",
    "c3ba68d7aea6ac7db53be72828d417a724a686bf",
    "unknown",
    "12545704ac63f71ed6b7608181a9bdf665171ced",
    "4a5c20f25af4ebb8e399f891cdbed741e0a22dd3",
)
"""One entry per content repo mined: its commit, or ``unknown`` for one
that is not a git checkout. Never its name: a private repo contributes
counts only."""

# 1038 rows
ROWS: str = """\
after-of	action script	0	-	bes action	2	0	2
after-of	activation	0	active flag	source analysis	1	0	0
after-of	active	0	-	action	1	0	0
after-of	active flag	0	-	activation	1	0	1
after-of	active flag	0	-	best activation	6	0	0
after-of	active start time	0	-	action	2	0	0
after-of	active start time	0	-	active action	3	0	0
after-of	adapter	0	address	network	2	0	0
after-of	address	0	-	any adapter	2	0	2
after-of	address	0	unique value	adapter	2	0	2
after-of	agent version	0	-	bes computer	1	0	1
after-of	android	0	-	operating system	9	0	0
after-of	any adapter	0	address	network	2	0	2
after-of	applicable computer	0	name	bes fixlet	1	0	1
after-of	architecture	0	-	operating system	17	0	2
after-of	architecture	0	match	operating system	1	0	0
after-of	array	1	string	dictionary	4	0	4
after-of	array	1	value	dictionary	2	0	2
after-of	average	0	-	evaluationcycle	1	0	0
after-of	average duration	0	-	evaluationcycle	1	0	0
after-of	base_board_information	0	serial_number	dmi	1	0	1
after-of	best activation	0	active flag	source analysis	3	0	0
after-of	boot time	0	-	operating system	1	0	0
after-of	build number	0	-	operating system	1	0	0
after-of	child node	0	child node	parent node	4	0	4
after-of	child node	0	node value	child node	4	0	4
after-of	client folder	0	folder	current site	27	0	2
after-of	client folder	0	parent folder	site	24	24	20
after-of	client folder	0	pathname	current site	3	0	0
after-of	client setting	0	name	bes computer	1	0	1
after-of	component string	0	unique value	sid	2	0	2
after-of	computer	0	concatenation	result	1	0	1
after-of	concatenation	0	-	character	1	1	1
after-of	concatenation	0	-	td	3	0	3
after-of	concatenation	0	-	tr	1	0	1
after-of	concatenation	0	-	value	1	0	1
after-of	concatenation	0	substring separated by	value	1	0	1
after-of	concatenation	0	tr	computer	1	0	1
after-of	concatenation	0	tr	td	1	0	1
after-of	concatenation	1	-	download hash algorithm	1	0	1
after-of	concatenation	1	-	element	1	0	1
after-of	concatenation	1	-	html	5	5	0
after-of	concatenation	1	-	line	3	0	3
after-of	concatenation	1	-	mount point	2	0	2
after-of	concatenation	1	-	name	3	0	2
after-of	concatenation	1	-	parameter	1	1	1
after-of	concatenation	1	-	pathname	5	0	4
after-of	concatenation	1	-	preceding text	2	0	2
after-of	concatenation	1	-	site tag	1	0	1
after-of	concatenation	1	-	substring separated by	11	11	11
after-of	concatenation	1	-	type	1	0	1
after-of	concatenation	1	-	unique value	13	0	13
after-of	concatenation	1	-	url	1	0	1
after-of	concatenation	1	substring separated by	substring separated by	4	4	4
after-of	concatenation	1	tbody	tr	2	0	2
after-of	concatenation	1	td	unique value	1	0	1
after-of	concatenation	1	td	value	3	0	3
after-of	concatenation	1	thead	tr	2	0	0
after-of	concatenation	1	tuple string item	name	6	0	6
after-of	concatenation	1	tuple string item	pathname	31	0	31
after-of	concatenation	1	tuple string item	string value	1	0	1
after-of	concatenation	1	tuple string item	unique value	1	0	1
after-of	content	0	-	file	1	1	1
after-of	core	0	sum	cpupackage	1	0	0
after-of	creation time	0	-	file	177	146	177
after-of	creation time	0	maximum	file	6	0	6
after-of	current system interval	0	range	power history	1	0	1
after-of	custom flag	0	-	source analysis	1	0	0
after-of	cve id list	0	substring separated by	relevant fixlet	1	0	1
after-of	data folder	0	-	client	6	0	0
after-of	data folder	0	folder	client	88	0	5
after-of	data folder	0	pathname	client	2	0	0
after-of	date	1	-	minimum	2	0	2
after-of	date	1	-	timestamp	1	0	0
after-of	descendant	0	-	folder	1	1	1
after-of	descendant	0	pathname	folder	2	2	2
after-of	device type	0	-	bes computer	2	0	2
after-of	dictionary	0	array	file	6	6	6
after-of	dictionary	0	dictionary	value	1	0	1
after-of	dictionary	0	entry	node	3	0	3
after-of	dictionary	0	string	file	2	2	2
after-of	dictionary	0	string	service plane	1	0	1
after-of	dictionary	1	string	dictionary	1	0	1
after-of	display name	0	-	service	1	0	1
after-of	display name	0	unique value	subscribed site	1	0	1
after-of	distinguished name	0	-	local computer	3	0	3
after-of	dns domainname	0	-	local computer	2	0	2
after-of	dns domainname	0	unique value	local computer	2	0	2
after-of	drive	0	free space	system folder	1	0	1
after-of	drive	0	name	system folder	4	0	0
after-of	drive	0	root folder	system folder	1	0	0
after-of	drive	0	total space	system folder	1	0	1
after-of	element	0	key	value	2	0	2
after-of	element	0	number	reported computer set	2	0	2
after-of	element	0	number	targeted computer set	2	0	2
after-of	entry	0	key	dictionary	3	0	3
after-of	escape	0	unique value	home directory	1	0	1
after-of	established	0	-	tcp state	1	0	0
after-of	evaluationcycle	0	-	client	6	0	0
after-of	evaluationcycle	0	average	client	1	0	0
after-of	evaluationcycle	0	average duration	client	1	0	0
after-of	evaluationcycle	0	track fixlet	client	1	0	0
after-of	exit code	0	-	action	2	0	0
after-of	exit code	0	-	active action	4	0	1
after-of	explicit owner	0	-	site	1	0	0
after-of	explicit writer	0	-	site	1	0	0
after-of	file	0	-	folder	43	41	40
after-of	file	0	creation time	csidl folder	31	31	31
after-of	file	0	creation time	folder	3	3	3
after-of	file	0	json	folder	2	2	2
after-of	file	0	line	folder	8	7	7
after-of	file	0	line containing	folder	7	5	7
after-of	file	0	locked line containing	folder	2	2	2
after-of	file	0	modification time	folder	3	3	3
after-of	file	0	name	folder	2	2	1
after-of	file	0	number	folder	8	8	7
after-of	file	0	pathname	csidl folder	31	31	31
after-of	file	0	pathname	folder	14	13	12
after-of	file	0	section	folder	1	1	1
after-of	file	0	size	folder	2	2	2
after-of	file	0	version	folder	2	2	2
after-of	file	0	xml document	folder	1	1	1
after-of	file	1	-	folder	39	39	38
after-of	file	1	-	storage folder	2	0	0
after-of	file	1	creation time	csidl folder	146	146	146
after-of	file	1	dictionary	folder	1	0	1
after-of	file	1	json	folder	7	3	7
after-of	file	1	key	folder	2	2	2
after-of	file	1	line	folder	24	23	23
after-of	file	1	line	windows folder	2	0	2
after-of	file	1	line containing	folder	20	20	20
after-of	file	1	locked line containing	folder	2	2	2
after-of	file	1	modification time	folder	9	9	9
after-of	file	1	parent folder	parameter	1	1	0
after-of	file	1	parent folder	unique value	2	0	2
after-of	file	1	pathname	csidl folder	147	147	147
after-of	file	1	pathname	folder	34	30	20
after-of	file	1	pathname	following text	1	0	1
after-of	file	1	pathname	parent folder	2	0	2
after-of	file	1	pathname	storage folder	2	0	2
after-of	file	1	section	folder	4	4	4
after-of	file	1	sqlite database	folder	2	2	2
after-of	file	1	variable	folder	1	1	1
after-of	file	1	version	folder	4	4	4
after-of	file	1	version block	native folder	4	4	4
after-of	file	1	xml document	folder	8	7	8
after-of	file ending in	1	-	folder	2	2	2
after-of	file ending in	1	name	folder	1	1	1
after-of	file ending in	1	number	folder	1	1	1
after-of	file ending in	1	pathname	folder	1	1	1
after-of	find file	1	-	folder	1	1	1
after-of	find file	1	name	folder	1	1	1
after-of	find file	1	number	folder	1	1	1
after-of	find file	1	pathname	folder	3	3	3
after-of	first	1	-	sha256	1	0	0
after-of	first	1	following text	following text	9	0	8
after-of	first	1	following text	line	12	0	12
after-of	first	1	following text	line containing	8	8	8
after-of	first	1	following text	locked line containing	3	3	3
after-of	first	1	following text	name	2	0	2
after-of	first	1	following text	preceding text	8	0	0
after-of	first	1	following text	previous line	1	0	1
after-of	first	1	following text	substring separated by	2	2	2
after-of	first	1	following text	track fixlet	1	0	1
after-of	first	1	following text	url	1	0	0
after-of	first	1	following text	variable	5	0	5
after-of	first	1	preceding text	following text	23	0	20
after-of	first	1	preceding text	line containing	7	7	7
after-of	first	1	preceding text	name	3	0	3
after-of	first	1	preceding text	release	1	0	0
after-of	first	1	preceding text	substring separated by	2	2	2
after-of	fixlet	0	-	bes site	1	0	1
after-of	fixlet	0	-	site	1	0	1
after-of	fixlet	0	header	current site	1	0	1
after-of	fixlet	0	tr	bes site	1	0	1
after-of	fixlet	1	id	current bes site	1	0	0
after-of	fixlet	1	link	bes site	1	0	0
after-of	fixlet	1	link	current bes site	1	0	0
after-of	folder	0	-	data folder	1	0	1
after-of	folder	0	-	folder	17	16	17
after-of	folder	0	-	root folder	1	0	0
after-of	folder	0	file	data folder	3	0	3
after-of	folder	0	file	folder	14	11	14
after-of	folder	0	folder	folder	26	25	26
after-of	folder	0	modification time	folder	4	4	4
after-of	folder	0	name	folder	4	4	4
after-of	folder	0	number	folder	3	3	3
after-of	folder	0	pathname	folder	1	1	1
after-of	folder	0	pathname	parent folder	1	0	1
after-of	folder	1	-	folder	11	8	10
after-of	folder	1	-	parent folder	8	0	2
after-of	folder	1	-	preceding text	13	0	13
after-of	folder	1	-	unique value	6	0	6
after-of	folder	1	-	windows folder	1	0	1
after-of	folder	1	descendant	unique value	1	0	1
after-of	folder	1	file	client folder	24	0	6
after-of	folder	1	file	data folder	4	0	4
after-of	folder	1	file	folder	106	101	105
after-of	folder	1	file	parent folder	27	0	19
after-of	folder	1	file	system folder	1	0	1
after-of	folder	1	file	unique value	13	0	13
after-of	folder	1	file	windows folder	1	0	1
after-of	folder	1	find file	parent folder	3	0	2
after-of	folder	1	folder	client folder	1	0	1
after-of	folder	1	folder	csidl folder	3	3	3
after-of	folder	1	folder	data folder	79	0	79
after-of	folder	1	folder	folder	54	41	54
after-of	folder	1	folder	parent folder	11	0	7
after-of	folder	1	folder	unique value	25	0	17
after-of	folder	1	folder	value	4	0	4
after-of	folder	1	folder	windows folder	1	0	0
after-of	folder	1	number	folder	1	1	1
after-of	folder	1	parent folder	value	11	0	11
after-of	folder	1	pathname	client folder	2	0	1
after-of	folder	1	pathname	csidl folder	1	1	1
after-of	folder	1	pathname	data folder	1	0	1
after-of	folder	1	pathname	folder	10	9	9
after-of	folder	1	pathname	home directory folder	1	0	1
after-of	folder	1	pathname	parent folder	7	0	2
after-of	folder	1	pathname	windows folder	1	0	0
after-of	following text	0	-	first	44	44	31
after-of	following text	0	-	last	15	15	13
after-of	following text	0	-	position	2	2	2
after-of	following text	0	file	first	1	1	1
after-of	following text	0	first	first	32	32	28
after-of	following text	0	last	first	4	4	2
after-of	following text	0	length	position	1	0	1
after-of	following text	0	substring separated by	first	1	1	1
after-of	following text	0	td	first	2	2	2
after-of	following text	0	unique value	first	2	2	2
after-of	free space	0	-	drive	1	0	1
after-of	friendly name	0	unique value	active device	1	0	1
after-of	gather schedule authority	0	unique value	current site	1	0	1
after-of	gather schedule time interval	0	-	current site	1	0	1
after-of	group	1	member	site	1	1	0
after-of	group leader	0	-	active action	1	0	0
after-of	h2	1	-	name	1	0	0
after-of	header	0	-	action	1	0	0
after-of	header	0	-	fixlet	1	0	1
after-of	header	1	value	action	1	0	1
after-of	header	1	value	relevant fixlet	1	0	1
after-of	header	1	value	relevant offer action	1	0	1
after-of	home directory	0	escape	user	1	0	1
after-of	home directory	0	unique value	user	14	0	14
after-of	home directory folder	0	folder	user	1	0	1
after-of	html	1	-	name	1	0	0
after-of	html	1	-	preceding text	1	0	1
after-of	html	1	-	status	1	0	0
after-of	html	1	-	subscription mode	1	0	0
after-of	html	1	html concatenation	unique value	1	0	1
after-of	html	1	tr	unique value	1	0	1
after-of	html concatenation	0	-	html	4	4	4
after-of	html concatenation	0	-	table	1	1	1
after-of	html concatenation	0	-	td	4	1	4
after-of	html concatenation	0	-	tr	5	0	5
after-of	html concatenation	0	table	tr	1	0	1
after-of	html concatenation	0	tbody	tr	2	0	2
after-of	html concatenation	0	td	p	1	0	1
after-of	html concatenation	0	tr	bes computer	1	0	1
after-of	html concatenation	0	tr	bes computer group	1	0	1
after-of	html concatenation	0	tr	bes fixlet	1	0	1
after-of	html concatenation	0	tr	bes property	1	0	1
after-of	html concatenation	0	tr	client setting	1	0	1
after-of	html concatenation	0	tr	property	1	0	1
after-of	html concatenation	0	tr	td	4	0	4
after-of	html concatenation	0	tr	th	1	0	1
after-of	html concatenation	0	ul	li	2	0	2
after-of	html concatenation	1	td	html	2	2	1
after-of	html tag	1	-	concatenation	1	0	1
after-of	html tag	1	-	device type	2	0	2
after-of	html tag	1	-	html concatenation	1	0	1
after-of	html tag	1	-	locked flag	2	0	0
after-of	html tag	1	-	set	1	0	0
after-of	html tag	1	-	top level bes action	1	0	1
after-of	html tag	1	-	unique value	1	0	1
after-of	id	0	-	action	2	0	1
after-of	id	0	-	active action	5	0	0
after-of	id	0	-	bes computer	8	0	8
after-of	id	0	-	current bes site	1	0	0
after-of	id	0	-	current fixlet	1	0	0
after-of	id	0	-	fixlet	1	1	1
after-of	id	0	-	site	3	0	0
after-of	id	0	javascript array	bes computer	1	0	1
after-of	image file	0	pathname	process	1	1	1
after-of	info	0	-	client	1	0	1
after-of	integer value	0	-	property	5	5	5
after-of	integer value	0	-	select	6	6	6
after-of	integer value	0	maximum	select	3	3	3
after-of	integer value	0	sum	select	1	1	1
after-of	integer value	0	unique value	select	1	1	1
after-of	javascript array	1	-	id	1	0	1
after-of	json	0	key	file	9	8	9
after-of	json	0	key	mime field	1	1	1
after-of	json	0	key	value	1	0	1
after-of	json	0	path	file	1	0	1
after-of	key	0	-	entry	3	0	3
after-of	key	0	-	key	557	557	555
after-of	key	0	key	key	8	8	8
after-of	key	0	name	key	7	7	7
after-of	key	0	number	key	2	2	2
after-of	key	0	value	key	681	680	681
after-of	key	1	-	file	2	2	2
after-of	key	1	-	key	2	1	2
after-of	key	1	-	native registry	8	0	0
after-of	key	1	-	registry	4	0	1
after-of	key	1	-	section	15	15	6
after-of	key	1	key	key	3	1	3
after-of	key	1	key	native registry	1	0	0
after-of	key	1	key	registry	13	0	9
after-of	key	1	key	x32 registry	52	0	51
after-of	key	1	key	x64 registry	86	0	86
after-of	key	1	last write time	registry	1	0	1
after-of	key	1	value	element	2	0	2
after-of	key	1	value	json	11	0	11
after-of	key	1	value	key	5	1	5
after-of	key	1	value	native registry	1	0	1
after-of	key	1	value	registry	26	0	23
after-of	key	1	value	value	3	0	3
after-of	key	1	value	x32 registry	1	0	1
after-of	last	1	-	concatenation	1	1	0
after-of	last	1	-	name	4	0	0
after-of	last	1	following text	line containing	2	2	1
after-of	last	1	following text	name	2	0	1
after-of	last	1	following text	preceding text	8	0	8
after-of	last	1	following text	value	1	0	1
after-of	last	1	preceding text	following text	4	0	2
after-of	last	1	preceding text	line containing	2	2	2
after-of	last	1	preceding text	name	3	0	3
after-of	last command time	0	-	client	3	0	0
after-of	last report time	0	maximum	bes computer	1	0	1
after-of	last write time	0	-	key	2	2	2
after-of	length	0	-	concatenation	3	0	3
after-of	length	0	-	following text	1	0	1
after-of	length	0	-	name	2	0	0
after-of	length	0	-	parameter	2	2	0
after-of	li	0	-	unique value	1	0	1
after-of	li	0	html concatenation	element	1	0	1
after-of	li	0	html concatenation	value	1	0	1
after-of	line	0	-	file	40	35	32
after-of	line	0	concatenation	file	3	1	2
after-of	line	0	first	file	12	12	12
after-of	line	0	match	file	3	3	0
after-of	line	0	number	file	2	1	2
after-of	line	0	previous line	file	1	0	1
after-of	line containing	1	-	file	23	22	23
after-of	line containing	1	first	file	15	10	15
after-of	line containing	1	last	file	4	3	4
after-of	line containing	1	number	file	1	1	1
after-of	link	0	-	bes wizard	2	0	2
after-of	link	0	-	fixlet	1	1	0
after-of	link	0	-	source analysis	1	0	1
after-of	link	1	-	fixlet	1	1	0
after-of	local computer	0	distinguished name	active directory	3	0	3
after-of	local computer	0	dns domainname	active directory	4	0	4
after-of	local ports string	0	substring separated by	rule	1	0	1
after-of	locked line containing	1	-	file	2	2	2
after-of	locked line containing	1	first	file	3	1	3
after-of	login account	0	-	service	1	1	1
after-of	mac	0	-	operating system	7	0	0
after-of	manufacturer	0	-	system_information	1	0	1
after-of	master flag	0	-	current console user	2	0	2
after-of	match	1	-	architecture	1	0	0
after-of	match	1	-	line	3	0	3
after-of	match	1	-	name	2	0	0
after-of	maximum	0	-	creation time	6	0	6
after-of	maximum	0	-	integer value	3	0	3
after-of	maximum	0	-	last report time	1	0	1
after-of	maximum	0	-	minimum	2	0	2
after-of	maximum	0	-	modification time	6	0	6
after-of	maximum	0	-	unique value	2	0	2
after-of	maximum	0	unique value	version	1	0	1
after-of	member	0	-	group	1	1	0
after-of	member	0	-	local group	1	1	1
after-of	member	0	number	bes computer group	1	0	1
after-of	mime field	1	-	current fixlet	1	0	0
after-of	minimum	0	-	modification time	1	0	1
after-of	minimum	0	-	subscribe time	13	0	13
after-of	minimum	0	date	subscribe time	2	0	2
after-of	modification time	0	-	file	9	8	9
after-of	modification time	0	-	folder	5	1	5
after-of	modification time	0	maximum	file	6	3	6
after-of	mount point	0	concatenation	filesystem	2	0	2
after-of	name	0	-	applicable computer	1	0	1
after-of	name	0	-	author	1	0	0
after-of	name	0	-	bes action	2	0	2
after-of	name	0	-	bes analysis	2	0	2
after-of	name	0	-	bes baseline	2	0	2
after-of	name	0	-	bes computer group	2	0	2
after-of	name	0	-	bes domain	2	0	2
after-of	name	0	-	bes filter	4	0	4
after-of	name	0	-	bes property	3	0	3
after-of	name	0	-	bes role	2	0	2
after-of	name	0	-	bes site	2	0	2
after-of	name	0	-	bes task	2	0	2
after-of	name	0	-	bes webui app	2	0	2
after-of	name	0	-	bes wizard	2	0	2
after-of	name	0	-	cloud provider	1	0	1
after-of	name	0	-	computer	2	0	0
after-of	name	0	-	current console user	1	0	0
after-of	name	0	-	current fixlet	1	0	1
after-of	name	0	-	drive	4	0	0
after-of	name	0	-	file	1	0	1
after-of	name	0	-	find file	1	1	1
after-of	name	0	-	folder	1	0	1
after-of	name	0	-	key	4	0	4
after-of	name	0	-	logged on user	1	0	1
after-of	name	0	-	mime field	3	0	3
after-of	name	0	-	node	1	0	1
after-of	name	0	-	operating system	85	0	3
after-of	name	0	-	plain bes fixlet	2	0	2
after-of	name	0	-	process	4	0	3
after-of	name	0	-	registration server	1	0	1
after-of	name	0	-	site	3	0	0
after-of	name	0	-	user	1	0	1
after-of	name	0	-	value	2	0	2
after-of	name	0	-	wizard	1	0	0
after-of	name	0	concatenation	bes computer	1	0	1
after-of	name	0	concatenation	bes custom site	2	0	2
after-of	name	0	concatenation	current site	1	0	1
after-of	name	0	concatenation	file	1	0	1
after-of	name	0	concatenation	key	2	0	2
after-of	name	0	concatenation	product	1	0	1
after-of	name	0	concatenation	setting	1	0	1
after-of	name	0	first	drive	1	0	1
after-of	name	0	first	file	1	0	1
after-of	name	0	first	folder	1	0	1
after-of	name	0	first	parent folder	2	0	2
after-of	name	0	html	site	1	0	0
after-of	name	0	last	file ending in	1	1	1
after-of	name	0	match	operating system	2	0	0
after-of	name	0	number	package	1	0	1
after-of	name	0	unique value	client setting	1	0	1
after-of	name	0	unique value	cloud provider	1	0	1
after-of	name	0	unique value	folder	3	0	3
after-of	name	0	unique value	key	1	0	1
after-of	name	0	unique value	package	1	0	1
after-of	name	0	unique value	relevant fixlet	1	0	1
after-of	next line	0	-	line containing	1	1	1
after-of	node	0	name	node	1	0	1
after-of	node	0	node	node	1	1	1
after-of	node	1	-	service plane	3	0	0
after-of	node	1	node	node	2	2	2
after-of	node	1	node	service plane	1	0	1
after-of	node value	0	-	child node	2	0	2
after-of	node value	0	-	select	1	1	1
after-of	node value	0	-	xpath	1	1	1
after-of	node value	0	preceding text	xpath	1	1	1
after-of	node value	0	substring separated by	child node	2	0	2
after-of	node value	0	unique value	select	1	1	1
after-of	number	0	-	bes action	1	0	1
after-of	number	0	-	bes computer	3	0	3
after-of	number	0	-	bes fixlet	3	0	3
after-of	number	0	-	element	6	0	6
after-of	number	0	-	file	8	0	8
after-of	number	0	-	file ending in	1	1	1
after-of	number	0	-	find file	1	1	1
after-of	number	0	-	folder	6	1	6
after-of	number	0	-	key	2	0	2
after-of	number	0	-	line	2	0	2
after-of	number	0	-	line containing	2	2	2
after-of	number	0	-	logged on user	2	0	2
after-of	number	0	-	member	2	0	2
after-of	number	0	-	name	1	0	1
after-of	number	0	-	rawline	1	0	1
after-of	number	0	-	relevant fixlet	4	0	4
after-of	number	0	-	relevant offer action	1	0	1
after-of	number	0	-	setting	2	0	2
after-of	number	0	-	substring separated by	3	3	3
after-of	number	0	-	unique value	12	0	12
after-of	number	0	-	value	1	1	1
after-of	number	0	-	winrt package	1	0	1
after-of	number	0	-	xpath	1	1	1
after-of	number	0	sum	relevant fixlet	1	0	1
after-of	number	0	sum	relevant offer action	1	0	1
after-of	offer	0	-	active action	1	0	0
after-of	offer accepted	0	-	active action	1	0	0
after-of	operating system	0	-	bes computer	1	0	1
after-of	operating system	0	unique value	bes computer	1	0	1
after-of	origin fixlet id	0	-	active action	3	0	0
after-of	p	0	-	b	1	0	1
after-of	p	0	-	concatenation	1	0	1
after-of	p	0	-	html tag	1	1	0
after-of	p	0	html concatenation	value	1	0	1
after-of	package	1	-	debianpackage	15	0	15
after-of	package	1	-	rpm	3	0	3
after-of	parameter	1	-	action	21	0	0
after-of	parameter	1	concatenation	action	1	0	1
after-of	parent folder	0	-	client	1	0	0
after-of	parent folder	0	-	regapp	2	2	2
after-of	parent folder	0	file	file	2	2	2
after-of	parent folder	0	folder	client	22	0	0
after-of	parent folder	0	folder	file	1	1	1
after-of	parent folder	0	folder	folder	11	11	11
after-of	parent folder	0	folder	parent folder	23	0	20
after-of	parent folder	0	parent folder	client folder	24	0	20
after-of	parent folder	0	pathname	parent folder	1	0	0
after-of	parent node	0	child node	parent node	4	0	4
after-of	parent node	0	parent node	xpath	4	4	4
after-of	path	1	-	json	1	0	1
after-of	pathname	0	-	client folder	3	0	0
after-of	pathname	0	-	data folder	2	0	0
after-of	pathname	0	-	descendant	1	0	1
after-of	pathname	0	-	file	196	177	181
after-of	pathname	0	-	find file	3	3	3
after-of	pathname	0	-	folder	26	25	17
after-of	pathname	0	-	image file	1	0	1
after-of	pathname	0	-	native system folder	1	0	0
after-of	pathname	0	-	parent folder	1	0	0
after-of	pathname	0	-	system folder	2	0	0
after-of	pathname	0	-	windows folder	1	0	1
after-of	pathname	0	-	x64 file	3	3	0
after-of	pathname	0	concatenation	descendant	1	0	1
after-of	pathname	0	concatenation	file	32	5	32
after-of	pathname	0	concatenation	file ending in	1	1	1
after-of	pathname	0	concatenation	folder	2	1	2
after-of	pathname	0	unique value	file	11	10	11
after-of	pathname	0	unique value	folder	9	9	9
after-of	pending time	0	-	active action	1	0	0
after-of	pid	0	-	process	1	1	1
after-of	platform id	0	-	operating system	4	0	0
after-of	position	1	following text	preceding text	2	0	2
after-of	preceding text	0	-	first	46	46	21
after-of	preceding text	0	-	first match	1	1	1
after-of	preceding text	0	-	last	22	22	17
after-of	preceding text	0	-	node value	1	0	1
after-of	preceding text	0	-	value	3	0	3
after-of	preceding text	0	concatenation	last	2	2	2
after-of	preceding text	0	first	first	3	3	0
after-of	preceding text	0	first	last	5	5	0
after-of	preceding text	0	folder	value	13	0	13
after-of	preceding text	0	html	following text	1	0	1
after-of	preceding text	0	last	first	5	5	5
after-of	preceding text	0	last	last	3	3	3
after-of	preceding text	0	unique value	first	8	8	8
after-of	previous line	0	first	line	1	0	1
after-of	private ip	0	unique value	cloud provider	1	0	1
after-of	product type	0	-	operating system	3	0	0
after-of	product_name	0	-	system_information	1	0	1
after-of	property	1	-	type	13	13	3
after-of	property	1	integer value	select object	2	2	2
after-of	range	0	start	current system interval	1	0	1
after-of	region	0	unique value	cloud provider	1	0	1
after-of	release	0	first	operating system	1	0	0
after-of	relevant fixlet	0	header	site	1	0	1
after-of	relevant fixlet	0	number	current site	1	0	1
after-of	relevant fixlet	0	number	site	3	0	3
after-of	relevant offer action	0	-	site	1	0	1
after-of	relevant offer action	0	header	site	1	0	1
after-of	relevant offer action	0	number	current site	1	0	1
after-of	relevant offer action	0	number	site	1	0	1
after-of	result	0	computer	bes property	1	0	1
after-of	result	0	substring separated by	bes property	1	1	1
after-of	result	0	value	bes property	2	2	2
after-of	result from	1	value	bes computer	1	0	1
after-of	root folder	0	folder	drive	1	0	0
after-of	row	0	-	statement	2	2	2
after-of	rule	0	local ports string	firewall	1	0	1
after-of	running	0	-	local mssql database	1	0	1
after-of	section	1	key	file	14	13	5
after-of	select	1	-	wmi	4	3	4
after-of	select	1	integer value	wmi	11	7	11
after-of	select	1	node value	xml document	2	0	2
after-of	select	1	string value	wmi	14	10	14
after-of	select object	1	-	wmi	1	1	1
after-of	select object	1	property	wmi	2	2	2
after-of	serial	0	-	hardware	1	0	1
after-of	serial_number	0	-	base_board_information	1	0	1
after-of	serial_number	0	-	system_information	1	0	1
after-of	service name	0	unique value	service	1	0	1
after-of	service plane	0	-	iokit registry	3	0	0
after-of	service plane	0	dictionary	iokit registry	1	0	1
after-of	service plane	0	node	iokit registry	4	0	1
after-of	set	0	-	unique value	2	0	2
after-of	set	0	-	value	1	0	1
after-of	setting	0	-	client	4	0	1
after-of	setting	0	name	client	1	0	1
after-of	setting	0	number	client	2	0	2
after-of	setting	0	value	client	15	0	15
after-of	setting	1	-	client	64	0	0
after-of	setting	1	sha256	client	1	0	0
after-of	setting	1	value	client	68	0	7
after-of	sha1	0	-	concatenation	1	0	1
after-of	sha256	0	-	setting	1	1	1
after-of	sid	0	component string	user	2	0	2
after-of	site	0	-	current fixlet	2	0	0
after-of	site	0	explicit owner	current fixlet	1	0	0
after-of	site	0	explicit writer	current fixlet	1	0	0
after-of	site	0	name	current fixlet	1	0	0
after-of	site tag	0	concatenation	current site	1	0	1
after-of	size	0	-	file	3	3	2
after-of	size	0	-	ram	1	0	1
after-of	size	0	sum	file	3	0	3
after-of	socket	0	-	network	4	0	4
after-of	sqlite database	0	statement	file	2	2	2
after-of	start	0	-	range	1	0	1
after-of	start type	0	-	service	2	2	2
after-of	state	0	-	service	1	1	1
after-of	state	0	unique value	bes action	1	0	1
after-of	statement	1	row	sqlite database	2	0	2
after-of	status	0	-	result	1	0	1
after-of	status	0	html	best activation	1	0	0
after-of	storage folder	0	file	client	4	0	0
after-of	string	0	-	value	1	0	1
after-of	string	1	-	array	4	4	4
after-of	string	1	-	dictionary	3	0	3
after-of	string	1	unique value	dictionary	1	1	1
after-of	string value	0	-	property	3	3	0
after-of	string value	0	-	select	9	9	9
after-of	string value	0	concatenation	select	1	1	1
after-of	string value	0	unique value	select	4	4	4
after-of	structure	0	-	smbios	1	0	0
after-of	structure	1	-	smbios	5	0	4
after-of	structure	1	value	smbios	679	0	4
after-of	subscribe time	0	minimum	site	15	0	15
after-of	subscription mode	0	html	site	1	0	0
after-of	substring separated by	1	-	concatenation	1	0	1
after-of	substring separated by	1	-	local ports string	2	0	2
after-of	substring separated by	1	-	node value	1	0	1
after-of	substring separated by	1	-	substring separated by	3	3	3
after-of	substring separated by	1	-	value	15	0	15
after-of	substring separated by	1	concatenation	computer name	1	0	1
after-of	substring separated by	1	concatenation	concatenation	4	4	4
after-of	substring separated by	1	first	node value	1	0	1
after-of	substring separated by	1	first	unique value	1	0	1
after-of	substring separated by	1	number	unique value	1	0	1
after-of	substring separated by	1	substring separated by	cve id list	1	0	1
after-of	substring separated by	1	substring separated by	following text	1	0	1
after-of	substring separated by	1	substring separated by	substring separated by	10	10	10
after-of	substring separated by	1	unique value	result	1	0	1
after-of	suite mask	0	-	operating system	1	0	0
after-of	sum	0	-	core	1	0	1
after-of	sum	0	-	integer value	1	0	1
after-of	sum	0	-	size	3	0	3
after-of	system_information	0	manufacturer	dmi	1	0	1
after-of	system_information	0	product_name	dmi	1	0	1
after-of	system_information	0	serial_number	dmi	1	0	1
after-of	system_information	0	version	dmi	1	0	1
after-of	table	0	-	tbody	1	0	1
after-of	table	1	html concatenation	html concatenation	1	0	1
after-of	tbody	0	-	concatenation	2	2	2
after-of	tbody	0	-	html concatenation	1	0	1
after-of	tbody	0	table	html concatenation	1	0	1
after-of	td	0	-	concatenation	2	2	1
after-of	td	0	-	html concatenation	6	6	6
after-of	td	0	-	link	3	0	0
after-of	td	0	tr	unique value	1	0	1
after-of	td	1	-	concatenation	2	2	0
after-of	td	1	-	following text	2	0	2
after-of	td	1	-	name	5	0	1
after-of	td	1	-	relay selection method	1	0	0
after-of	td	1	-	relay server	1	0	0
after-of	td	1	-	value	1	0	0
after-of	td	1	html concatenation	html concatenation	1	0	1
after-of	th	0	-	name	1	0	0
after-of	thead	0	-	concatenation	2	2	2
after-of	thead	0	-	tr	1	0	1
after-of	total space	0	-	drive	1	0	1
after-of	tr	0	-	bes computer	1	0	1
after-of	tr	0	-	bes property	1	0	1
after-of	tr	0	-	concatenation	4	0	4
after-of	tr	0	-	html	1	1	0
after-of	tr	0	-	html concatenation	13	0	11
after-of	tr	0	html concatenation	bes computer	3	0	3
after-of	tr	0	html concatenation	fixlet	1	0	1
after-of	tr	0	html concatenation	html concatenation	1	0	1
after-of	tr	0	html concatenation	td	1	0	1
after-of	tr	0	html concatenation	variable	1	0	1
after-of	tr	0	thead	html concatenation	1	0	1
after-of	track fixlet	0	first	evaluationcycle	1	0	0
after-of	tuple string item	1	-	concatenation	52	52	49
after-of	type	0	-	main processor	2	0	0
after-of	type	0	concatenation	current site	1	0	1
after-of	ul	0	-	html concatenation	2	0	2
after-of	unique id	0	unique value	cloud provider	1	0	1
after-of	unique value	0	-	absolute value	1	0	1
after-of	unique value	0	-	address	2	0	2
after-of	unique value	0	-	dns domainname	2	0	2
after-of	unique value	0	-	escape	1	0	1
after-of	unique value	0	-	following text	1	0	1
after-of	unique value	0	-	friendly name	1	0	1
after-of	unique value	0	-	gather schedule authority	1	0	1
after-of	unique value	0	-	home directory	1	0	1
after-of	unique value	0	-	integer value	1	0	1
after-of	unique value	0	-	ip address	2	0	2
after-of	unique value	0	-	maximum	1	0	1
after-of	unique value	0	-	name	5	0	5
after-of	unique value	0	-	node value	1	0	1
after-of	unique value	0	-	operating system	1	0	1
after-of	unique value	0	-	pathname	20	0	20
after-of	unique value	0	-	preceding text	5	0	5
after-of	unique value	0	-	private ip	1	0	1
after-of	unique value	0	-	region	1	0	1
after-of	unique value	0	-	service name	1	0	1
after-of	unique value	0	-	state	1	0	1
after-of	unique value	0	-	string	1	1	1
after-of	unique value	0	-	string value	1	0	1
after-of	unique value	0	-	substring separated by	1	1	1
after-of	unique value	0	-	unique id	1	0	1
after-of	unique value	0	-	value	6	0	6
after-of	unique value	0	-	version	3	0	3
after-of	unique value	0	concatenation	following text	1	0	1
after-of	unique value	0	concatenation	preceding text	1	0	1
after-of	unique value	0	concatenation	string value	3	0	3
after-of	unique value	0	concatenation	value	1	0	1
after-of	unique value	0	folder	home directory	12	0	12
after-of	unique value	0	folder	pathname	12	0	12
after-of	unique value	0	html tag	name	1	0	1
after-of	unique value	0	li	display name	1	0	1
after-of	unique value	0	number	home directory	1	0	1
after-of	unique value	0	number	modification time	1	0	1
after-of	unique value	0	number	name	6	0	6
after-of	unique value	0	number	preceding text	1	0	1
after-of	unique value	0	set	component string	2	0	2
after-of	unique value	0	substring separated by	preceding text	1	0	1
after-of	unique value	0	td	value	1	0	1
after-of	unix	0	-	operating system	15	0	0
after-of	uptime	0	-	operating system	2	0	0
after-of	url	0	concatenation	current site	1	0	1
after-of	url	0	first	current bes server	1	0	0
after-of	value	0	-	header	9	9	9
after-of	value	0	-	key	15	15	15
after-of	value	0	-	mime field	3	0	3
after-of	value	0	-	result	9	9	1
after-of	value	0	-	result from	6	6	6
after-of	value	0	-	setting	54	52	42
after-of	value	0	-	variable	2	2	0
after-of	value	0	concatenation	result	1	1	0
after-of	value	0	concatenation	result from	2	2	2
after-of	value	0	dictionary	array	1	1	1
after-of	value	0	element	key	2	2	2
after-of	value	0	folder	setting	15	15	15
after-of	value	0	json	header	1	1	1
after-of	value	0	key	key	3	3	3
after-of	value	0	last	header	1	1	1
after-of	value	0	li	header	1	1	1
after-of	value	0	name	key	2	2	2
after-of	value	0	p	result from	1	1	1
after-of	value	0	preceding text	result from	3	3	3
after-of	value	0	preceding text	setting	13	0	13
after-of	value	0	set	header	1	1	1
after-of	value	0	string	array	1	1	1
after-of	value	0	substring separated by	variable	5	5	5
after-of	value	0	unique value	result	3	0	3
after-of	value	0	unique value	result from	3	3	3
after-of	value	0	unique value	setting	1	1	1
after-of	value	1	-	key	743	62	735
after-of	value	1	-	structure	682	682	682
after-of	value	1	-	version block	5	0	4
after-of	value	1	number	key	1	1	1
after-of	variable	0	first	file	5	5	5
after-of	variable	0	tr	bes wizard	1	0	1
after-of	variable	1	value	environment	7	0	5
after-of	version	0	-	client	31	0	0
after-of	version	0	-	datastore inspector	1	0	1
after-of	version	0	-	file	4	4	4
after-of	version	0	-	main gather service	1	0	0
after-of	version	0	-	operating system	20	0	1
after-of	version	0	-	package	2	0	2
after-of	version	0	-	registration server	3	0	0
after-of	version	0	-	relay service	1	0	1
after-of	version	0	-	system_information	1	0	1
after-of	version	0	unique value	cloud provider	1	0	1
after-of	version	0	unique value	file	2	0	2
after-of	version block	0	value	file	5	5	4
after-of	version string	0	-	bios	1	0	1
after-of	version string	1	-	module	1	1	0
after-of	virtual	0	-	hardware	4	0	0
after-of	windows	0	-	operating system	55	0	2
after-of	x32	0	-	operating system	1	0	0
after-of	x64	0	-	operating system	8	0	0
after-of	x64 file	1	pathname	expand environment string	3	0	3
after-of	xml document	0	select	file	2	2	2
after-of	xml document	0	xpath	file	7	6	7
after-of	xpath	1	node value	xml document	2	0	2
after-of	xpath	1	number	xml document	1	0	1
after-of	xpath	1	parent node	xml document	4	0	4
statement-start	-	0	-	absolute value	4	0	4
statement-start	-	0	-	active	1	0	0
statement-start	-	0	-	active device	1	0	1
statement-start	-	0	-	active start time	2	0	0
statement-start	-	0	-	android	9	0	0
statement-start	-	0	-	architecture	11	0	3
statement-start	-	0	-	average duration	1	0	0
statement-start	-	0	-	base64 decode	1	1	1
statement-start	-	0	-	bes action	1	0	1
statement-start	-	0	-	bes computer	4	0	4
statement-start	-	0	-	bes fixlet	1	0	1
statement-start	-	0	-	bes site	1	0	0
statement-start	-	0	-	build number	1	0	0
statement-start	-	0	-	cloud provider	1	0	1
statement-start	-	0	-	computer name	5	0	0
statement-start	-	0	-	concatenation	41	38	25
statement-start	-	0	-	content	1	0	1
statement-start	-	0	-	current console user	1	0	0
statement-start	-	0	-	current user	4	0	4
statement-start	-	0	-	debianpackage	3	0	3
statement-start	-	0	-	descendant	1	0	1
statement-start	-	0	-	display name	1	0	1
statement-start	-	0	-	distinguished name	3	0	3
statement-start	-	0	-	dmi	1	0	1
statement-start	-	0	-	dns domainname	2	0	2
statement-start	-	0	-	download path	2	2	0
statement-start	-	0	-	embedded nt bit	1	1	0
statement-start	-	0	-	error	1	1	0
statement-start	-	0	-	exit code	4	0	3
statement-start	-	0	-	explicit owner	1	0	1
statement-start	-	0	-	explicit writer	1	0	1
statement-start	-	0	-	false	15	0	0
statement-start	-	0	-	file	130	100	102
statement-start	-	0	-	file ending in	2	2	2
statement-start	-	0	-	find file	2	2	2
statement-start	-	0	-	folder	32	27	30
statement-start	-	0	-	following text	9	0	4
statement-start	-	0	-	format	1	1	0
statement-start	-	0	-	group leader	1	0	0
statement-start	-	0	-	html	4	4	0
statement-start	-	0	-	html concatenation	8	3	8
statement-start	-	0	-	html tag	3	3	1
statement-start	-	0	-	id	4	0	1
statement-start	-	0	-	in plugin portal context	1	0	0
statement-start	-	0	-	in proxy agent context	26	0	0
statement-start	-	0	-	in web reports context	1	0	0
statement-start	-	0	-	integer value	5	0	5
statement-start	-	0	-	javascript array	1	1	0
statement-start	-	0	-	key	570	16	559
statement-start	-	0	-	last command time	1	0	1
statement-start	-	0	-	last relay select time	1	0	1
statement-start	-	0	-	last write time	2	0	2
statement-start	-	0	-	length	5	0	3
statement-start	-	0	-	less significance	1	1	0
statement-start	-	0	-	li	1	0	1
statement-start	-	0	-	line	40	0	38
statement-start	-	0	-	line containing	28	28	28
statement-start	-	0	-	local mssql database	1	0	1
statement-start	-	0	-	local user	2	0	2
statement-start	-	0	-	locked line containing	2	2	2
statement-start	-	0	-	logged on user	4	0	4
statement-start	-	0	-	login account	1	0	1
statement-start	-	0	-	mac	5	0	0
statement-start	-	0	-	main gather service	16	0	2
statement-start	-	0	-	match	3	3	0
statement-start	-	0	-	maximum	10	0	9
statement-start	-	0	-	member	1	0	1
statement-start	-	0	-	minimum	4	0	3
statement-start	-	0	-	modification time	6	0	6
statement-start	-	0	-	name	79	0	24
statement-start	-	0	-	node value	3	0	3
statement-start	-	0	-	now	6	0	0
statement-start	-	0	-	offer	1	0	0
statement-start	-	0	-	offer accepted	1	0	0
statement-start	-	0	-	origin fixlet id	1	0	0
statement-start	-	0	-	p	3	0	3
statement-start	-	0	-	package	23	20	23
statement-start	-	0	-	parameter	111	111	0
statement-start	-	0	-	parent folder	1	0	0
statement-start	-	0	-	pathname	219	0	167
statement-start	-	0	-	pending restart	1	0	0
statement-start	-	0	-	pending restart name	1	0	1
statement-start	-	0	-	pending time	1	0	0
statement-start	-	0	-	platform id	3	0	0
statement-start	-	0	-	preceding text	3	0	3
statement-start	-	0	-	private variable	1	1	0
statement-start	-	0	-	process	10	9	9
statement-start	-	0	-	property	43	39	7
statement-start	-	0	-	regapp	3	3	2
statement-start	-	0	-	relay service	11	0	2
statement-start	-	0	-	rpm	1	0	1
statement-start	-	0	-	running	1	0	1
statement-start	-	0	-	running application	4	4	1
statement-start	-	0	-	select	2	2	2
statement-start	-	0	-	service	12	7	10
statement-start	-	0	-	setting	64	59	63
statement-start	-	0	-	sha256	1	0	1
statement-start	-	0	-	shared variable	2	2	0
statement-start	-	0	-	size	1	0	0
statement-start	-	0	-	smbios	1	0	0
statement-start	-	0	-	socket	4	0	4
statement-start	-	0	-	start type	2	0	2
statement-start	-	0	-	state	1	0	1
statement-start	-	0	-	string	5	4	5
statement-start	-	0	-	string value	3	0	3
statement-start	-	0	-	substring between	3	3	0
statement-start	-	0	-	substring separated by	2	2	2
statement-start	-	0	-	sum	3	0	3
statement-start	-	0	-	system version	1	0	0
statement-start	-	0	-	table	3	2	2
statement-start	-	0	-	tr	13	0	13
statement-start	-	0	-	true	45	0	0
statement-start	-	0	-	tuple string item	40	40	38
statement-start	-	0	-	ul	1	0	1
statement-start	-	0	-	unique value	83	0	62
statement-start	-	0	-	unix	15	0	0
statement-start	-	0	-	uptime	1	0	0
statement-start	-	0	-	value	716	694	712
statement-start	-	0	-	version	58	1	6
statement-start	-	0	-	webui service	1	0	0
statement-start	-	0	-	windows	25	0	0
statement-start	-	0	-	winrt package	2	0	2
statement-start	-	0	-	wmi	2	2	1
statement-start	-	0	-	x32	1	0	0
statement-start	-	0	-	x64	7	0	0
statement-start	-	0	-	xpath	1	1	1
whose-it	active device	0	-	class	3	0	0
whose-it	active device	0	-	description	7	0	0
whose-it	active device	0	-	location information	1	0	0
whose-it	active device	0	-	manufacturer	1	0	0
whose-it	active device	0	-	service key value name	3	0	0
whose-it	bes action	0	-	group member flag	2	0	0
whose-it	bes action	0	-	issuer	2	0	0
whose-it	bes action	0	-	reapply flag	2	0	0
whose-it	bes action	0	-	state	6	0	0
whose-it	bes action	0	-	targeted by id flag	2	0	0
whose-it	bes action	0	-	targeted by list flag	2	0	0
whose-it	bes action	0	-	time issued	2	0	0
whose-it	bes analysis	0	-	best activation	1	0	0
whose-it	bes computer	0	-	comment	1	0	1
whose-it	bes computer	0	-	last report time	1	0	0
whose-it	bes computer	0	-	operating system	2	0	0
whose-it	bes computer	0	-	relay server flag	3	0	0
whose-it	bes computer	0	-	result from	2	2	2
whose-it	bes computer	0	-	root server flag	1	0	0
whose-it	bes computer group	0	-	name	1	0	0
whose-it	bes custom site	0	-	name	4	0	0
whose-it	bes custom site	0	-	writer	2	0	0
whose-it	bes fixlet	0	-	analysis flag	1	0	0
whose-it	bes fixlet	0	-	baseline flag	1	0	0
whose-it	bes fixlet	0	-	globally visible flag	1	0	0
whose-it	bes fixlet	0	-	group flag	1	0	0
whose-it	bes fixlet	0	-	locally visible flag	1	0	0
whose-it	bes fixlet	0	-	source severity	2	0	0
whose-it	bes fixlet	0	-	task flag	1	0	0
whose-it	bes fixlet	0	-	visible flag	1	0	0
whose-it	bes property	0	-	analysis flag	4	0	0
whose-it	bes property	0	-	custom flag	1	0	0
whose-it	bes property	0	-	default flag	1	0	0
whose-it	bes property	0	-	evaluation period	1	0	0
whose-it	bes property	0	-	name	7	0	0
whose-it	bes property	0	-	reserved flag	1	0	0
whose-it	bes property	0	-	source analysis	5	0	0
whose-it	bes site	0	-	fixlet	1	1	0
whose-it	bes site	0	-	id	1	0	0
whose-it	bes site	0	-	name	3	0	0
whose-it	bes task	0	-	mime field	6	3	6
whose-it	bes task	0	-	name	3	0	0
whose-it	bes wizard	0	-	dashboard id	2	0	0
whose-it	bes wizard	0	-	site	2	0	0
whose-it	child node	0	-	node name	4	0	0
whose-it	client setting	0	-	name	1	0	0
whose-it	current console user	0	-	master flag	1	0	0
whose-it	current system interval	0	-	state	1	0	0
whose-it	descendant	0	-	content	1	0	0
whose-it	descendant	0	-	name	2	0	1
whose-it	descendant	0	-	size	1	0	0
whose-it	drive	0	-	free space	1	0	0
whose-it	drive	0	-	name	1	0	0
whose-it	drive	0	-	total space	3	0	0
whose-it	drive	0	-	type	3	0	0
whose-it	file	0	-	content	1	0	0
whose-it	file	0	-	creation time	2	0	2
whose-it	file	0	-	day_of_month	2	0	0
whose-it	file	0	-	line	7	0	7
whose-it	file	0	-	line containing	1	1	1
whose-it	file	0	-	modification time	12	0	2
whose-it	file	0	-	month	2	0	0
whose-it	file	0	-	name	256	0	0
whose-it	file	0	-	section	1	1	1
whose-it	file	0	-	xml document	1	0	1
whose-it	file	0	-	year	2	0	0
whose-it	file	1	-	content	2	0	2
whose-it	file	1	-	line	12	0	0
whose-it	file	1	-	line containing	4	4	4
whose-it	file	1	-	modification time	6	0	0
whose-it	file	1	-	name	16	0	0
whose-it	file	1	-	sha256	9	0	0
whose-it	file	1	-	size	10	0	0
whose-it	file	1	-	version	1	0	0
whose-it	filesystem	0	-	filesystem type	1	0	0
whose-it	filesystem	0	-	type	1	0	0
whose-it	fixlet	0	-	analysis flag	1	0	0
whose-it	fixlet	0	-	best activation	1	0	0
whose-it	fixlet	0	-	id	1	0	0
whose-it	fixlet	0	-	name	1	0	0
whose-it	fixlet	1	-	applicable computer count	1	0	0
whose-it	folder	0	-	modification time	1	0	1
whose-it	folder	0	-	name	28	0	0
whose-it	folder	1	-	file	2	2	2
whose-it	folder	1	-	folder	2	0	2
whose-it	key	0	-	key	1	1	1
whose-it	key	0	-	name	12	0	0
whose-it	key	0	-	value	1383	1382	11
whose-it	key	1	-	key	1	0	1
whose-it	key	1	-	value	4	4	1
whose-it	line	0	-	match	4	4	0
whose-it	line containing	1	-	first	2	2	2
whose-it	local user	0	-	name	2	0	0
whose-it	member	0	-	last report time	1	0	0
whose-it	mime field	0	-	name	9	0	0
whose-it	name	0	-	length	2	0	0
whose-it	package	0	-	currently installed	7	0	0
whose-it	package	0	-	name	11	0	0
whose-it	package	1	-	currently installed	9	0	0
whose-it	process	0	-	name	2	0	0
whose-it	process	1	-	id	1	0	0
whose-it	process	1	-	user	2	0	0
whose-it	relevant fixlet	0	-	analysis flag	1	0	0
whose-it	relevant fixlet	0	-	best activation	1	0	0
whose-it	relevant fixlet	0	-	header	7	7	7
whose-it	result	0	-	detailed status	1	0	0
whose-it	result	0	-	status	1	0	0
whose-it	rule	0	-	action	1	0	0
whose-it	rule	0	-	enabled	1	0	0
whose-it	rule	0	-	inbound	1	0	0
whose-it	rule	0	-	local ports string	1	0	1
whose-it	rule	0	-	protocol	1	0	0
whose-it	select object	1	-	property	3	3	0
whose-it	service	0	-	display name	8	0	0
whose-it	service	0	-	running	1	0	0
whose-it	service	0	-	start type	3	0	0
whose-it	setting	0	-	effective date	4	0	0
whose-it	setting	0	-	name	13	0	0
whose-it	setting	0	-	value	1	0	0
whose-it	setting	1	-	value	35	0	1
whose-it	site	0	-	name	3	0	3
whose-it	site	0	-	type	4	0	0
whose-it	socket	0	-	local port	3	0	3
whose-it	socket	0	-	process	4	0	3
whose-it	socket	0	-	tcp state	1	0	0
whose-it	string	1	-	length	1	0	0
whose-it	top level bes action	0	-	multiple flag	1	0	0
whose-it	top level bes action	0	-	name	2	0	0
whose-it	top level bes action	0	-	result	1	0	1
whose-it	top level bes action	0	-	state	1	0	0
whose-it	top level bes action	0	-	time issued	1	0	0
whose-it	true	0	-	value	2	2	0
whose-it	unique value	0	-	multiplicity	2	0	0
whose-it	value	0	-	name	4	0	0
whose-it	volume	0	-	type	1	0	0
whose-it	xpath	1	-	node value	4	0	0
"""
