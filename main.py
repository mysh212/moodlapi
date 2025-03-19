from core.general import *
import lib.moodle as moodle

md = moodle.moodle(*read_from_file('.env').split())

md.auto()
info(md.session)