_init:
  call _main
  hlt

_main:
  push 20
  call square
  ret


_square:
_main
  dup
  mul
  ret
