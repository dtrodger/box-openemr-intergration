# Makefile

help:
	@echo
	@echo "  UGH EHR CDS Integration Development Makefile"
	@echo "  -----------------------------------------------------------------------------------------------------------"
	@echo "  dev                       to run development environment"

dev:
	docker-compose down
	docker-compose up
