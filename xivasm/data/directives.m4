m4_divert(-1)
# This file provides the necessary directives for xivasm
# With some quality of life features

# Track the include depth
m4_define(__INCLUDE_DEPTH__, 0)

# Constant variables
m4_define(__xiv_uppers, `ABCDEFGHIJKLMNOPQRESTUVWXYZ')
m4_define(__xiv_lowers, `abcdefghijklmnopqrestuvwxyz')

# Helper function to increment or decrement a value (int) of a macro.
m4_define(`INCREMENT', `m4_define(`$1', m4_eval($1 + 1))')
m4_define(`DECREMENT', `m4_define(`$1', m4_eval($1 - 1))')

# Convert text to upper or lowercase.
m4_define(`UPPERCASE', `m4_translit(`$1', __xiv_lowers, __xiv_uppers)')
m4_define(`LOWERCASE', `m4_translit(`$1', __xiv_uppers, __xiv_lowers)')

# Define macros
m4_define(`define', `m4_define(`$1', `$2')')

# Include files from the cwd or include paths.
m4_define(`include', `m4_ifdef(UPPERCASE(`__$1_H__'),,`m4_dnl
m4_define(UPPERCASE(__$1_H__))m4_dnl
m4_define(`__PARENT__', m4___file__)m4_dnl
INCREMENT(`__INCLUDE_DEPTH__')m4_dnl
m4_include($1)m4_dnl
m4_undefine(`__PARENT__')m4_dnl
DECREMENT(`__INCLUDE_DEPTH__')m4_dnl
')')

# Test if a macro is defined.
m4_define(`ifdef', `m4_ifdef(`$1', `$2', `$3')')

# Test Depth
m4_define(`IFDEPTH', `m4_ifelse(__INCLUDE_DEPTH__, $1, `$2', `$3')')

m4_divert
