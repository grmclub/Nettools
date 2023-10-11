SED = sed
SCRIPTS = novomac
BINS = novomacd

RCPATH ?= .
SHPATH ?= .

#RCPATH ?= /etc/crud/novomac
#SHPATH ?= /opt/crud/novomac

novomac: appctl.in
	$(SED) \
		-e s,%%RCPATH%%,$(RCPATH), \
		-e s,%%SHPATH%%,$(SHPATH), \
		$^ > $@
	@chmod +x $@

novomacd: novomacd.py
	@chmod +x $^

all: $(SCRIPTS) $(BINS)

clean:
	rm -f $(SCRIPTS) *.pyc *.swp
	@chmod -x *

.PHONY: clean
