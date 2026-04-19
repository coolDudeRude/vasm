m4_divert(-1)
# This file provides the necessary directives for xivasm
# With some quality of life features
m4_define(`define', `m4_define(`$1', `$2')')
m4_define(`include', `m4_ifdef(`__$1_H__',,`m4_define(__$1_H__)m4_include($1)')')
m4_define(`ifdef', `m4_ifdef(`$1', `$2', `$3')')

m4_define(`INCREMENT', `m4_define(`$1', m4_eval($1 + 1))')
m4_define(`DECREMENT', `m4_define(`$1', m4_eval($1 - 1))')
m4_divert
