_init:
  call _main
  hlt

_main:
  asis "echo \"Hello, world!\""
  push 0
  ret
