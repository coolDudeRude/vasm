m4_divert(-1)
# This file provides the necessary directives for xivasm
m4_define(`define', `m4_define(`$1', `$2')')
m4_define(`include', `m4_ifdef(`__$1_H__',,`m4_define(__$1_H__)m4_include($1)')')
m4_divert
