# Assembler
AS=xivasm
AFLAGS=

all: factorial.cfg sprintf.cfg hello.cfg


factorial.cfg: factorial.s
	$(AS) $(AFLAGS) factorial.s -o factorial.cfg

sprintf.cfg: sprintf.s
	$(AS) $(AFLAGS) sprintf.s -o sprintf.cfg

hello.cfg: hello.s
	$(AS) $(AFLAGS) hello.s -o hello.cfg

.PHONY: clean
clean:
	rm -f *.cfg

