# Makefile for RM2 CACTUS study

## cactus:          Compile CACTUS
.PHONY: cactus
cactus:
	./scripts/make-cactus.sh


.PHONY: help
help: Makefile
	@sed -n "s/^##//p" $<
