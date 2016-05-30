# Makefile for RM2 CACTUS study

## cactus:          Compile CACTUS
.PHONY: cactus
cactus:
	./scripts/make-cactus.sh


## clean-cactus     Clean CACTUS
.PHONY: clean-cactus
clean-cactus:
	cd ./cactus/make && make clean


.PHONY: help
help: Makefile
	@sed -n "s/^##//p" $<
