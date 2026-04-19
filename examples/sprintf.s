main:
  asis "rpn /VM_VERSION load \"/Running VM v%s\" dbpush dbpush"
  call sprintf
  dot
  asis "rpn /LIBDIRECTIVES_VERSION load \"/Using Libdirectives v%s\" dbpush dbpush"
  call sprintf
  dot
  hlt

sprintf:
  asis "rpn dbpop dbpop sprintf1s dbpush"
  ret
