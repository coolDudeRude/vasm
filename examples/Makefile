# Assmebler
AS=vasm
AFLAGS=

all: factorial.cfg sprintf.cfg


factorial.cfg: factorial.s
	$(AS) $(AFLAGS) factorial.s -o factorial.cfg

sprintf.cfg: sprintf.s
	$(AS) $(AFLAGS) sprintf.s -o sprintf.cfg

.PHONY: clean
clean:
	rm *.cfg

