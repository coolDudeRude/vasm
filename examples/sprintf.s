main:
  asis("rpn /VM_VERSION load \"/Running VM %s\" dbpush dbpush")
  call sprintf
  dot
  hlt

sprintf:
  asis("rpn dbpop dbpop sprintf1s dbpush")
  ret
