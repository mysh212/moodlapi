from core.general import *
import lib.login as login
import lib.moodle as moodle

import json

def encode(x):
    return json.loads(json.dumps(x))

# lg = login.login(*read_from_file('.env').split())

# info(str(type(lg)))

# if lg.auto():
# 	info(lg.session)
# 	write_to_file('session.st', lg.session)

session = read_from_file('session.st')

md = moodle.moodle(session)
debug(encode(md))
info(md)
debug(md.logined)
debug(encode(md.get_courses()))

for i in md.get_courses():
    info(i.name)
    debug(encode(i))