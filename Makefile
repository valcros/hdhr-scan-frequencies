# HDHomeRun Channel Scanner - Makefile
# Streamlined DevOps operations

.PHONY: help install install-dev test lint format clean docker-build docker-run docker-push deploy health-check

# Variables
PYTHON := python3
PIP := pip3
DOCKER_IMAGE := hdhr-scanner
DOCKER_TAG := 3.0
DOCKER_REGISTRY := ghcr.io
DOCKER_REPO := $(DOCKER_REGISTRY)/yourusername/$(DOCKER_IMAGE)

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(GREEN)HDHomeRun Scanner - DevOps Commands$(NC)\n\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Install production dependencies
	@echo "$(GREEN)Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Installation complete$(NC)"

install-dev: ## Install development dependencies
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✓ Development environment ready$(NC)"

setup: ## Full setup (dependencies + pre-commit)
	@echo "$(GREEN)Setting up development environment...$(NC)"
	$(MAKE) install-dev
	pre-commit install
	@echo "$(GREEN)✓ Setup complete$(NC)"

##@ Testing

test: ## Run unit tests
	@echo "$(GREEN)Running unit tests...$(NC)"
	$(PYTHON) -m pytest test_main.py -v

test-coverage: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(PYTHON) -m pytest test_main.py -v --cov=main --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report: htmlcov/index.html$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	$(PYTHON) -m pytest-watch test_main.py -v

##@ Code Quality

lint: ## Run all linters
	@echo "$(GREEN)Running linters...$(NC)"
	flake8 main.py test_main.py --max-line-length=127
	pylint main.py test_main.py --max-line-length=127 || true
	mypy main.py --ignore-missing-imports || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black
	@echo "$(GREEN)Formatting code...$(NC)"
	black main.py test_main.py
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check if code is formatted
	@echo "$(GREEN)Checking code format...$(NC)"
	black --check main.py test_main.py

security-scan: ## Run security scans
	@echo "$(GREEN)Running security scans...$(NC)"
	safety check --json || true
	bandit -r . -f json || true
	@echo "$(GREEN)✓ Security scan complete$(NC)"

##@ Docker Operations

docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest
	@echo "$(GREEN)✓ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

docker-build-no-cache: ## Build Docker image without cache
	@echo "$(GREEN)Building Docker image (no cache)...$(NC)"
	docker build --no-cache -t $(DOCKER_IMAGE):$(DOCKER_TAG) .
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_IMAGE):latest
	@echo "$(GREEN)✓ Docker image built: $(DOCKER_IMAGE):$(DOCKER_TAG)$(NC)"

docker-run: ## Run Docker container interactively
	@echo "$(GREEN)Running Docker container...$(NC)"
	docker run --rm -it --network host \
		-v $$(pwd)/output:/app/output \
		-v $$(pwd)/logs:/app/logs \
		-e OPENAI_API_KEY="$(OPENAI_API_KEY)" \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		$(PYTHON) main.py

docker-scan: ## Run automated scan in Docker
	@echo "$(GREEN)Running automated scan in Docker...$(NC)"
	docker run --rm --network host \
		-v $$(pwd)/output:/app/output \
		-e OPENAI_API_KEY="$(OPENAI_API_KEY)" \
		$(DOCKER_IMAGE):$(DOCKER_TAG) \
		$(PYTHON) main.py --device-id $(DEVICE_ID) --tuner 0 --quiet -o /app/output/scan.csv

docker-test: ## Test Docker image
	@echo "$(GREEN)Testing Docker image...$(NC)"
	docker run --rm $(DOCKER_IMAGE):$(DOCKER_TAG) $(PYTHON) main.py --version
	docker run --rm $(DOCKER_IMAGE):$(DOCKER_TAG) $(PYTHON) main.py --help
	@echo "$(GREEN)✓ Docker image tests passed$(NC)"

docker-security-scan: ## Scan Docker image for vulnerabilities
	@echo "$(GREEN)Scanning Docker image for vulnerabilities...$(NC)"
	docker scan $(DOCKER_IMAGE):$(DOCKER_TAG) || true
	@echo "$(GREEN)✓ Security scan complete$(NC)"

docker-push: ## Push Docker image to registry
	@echo "$(GREEN)Pushing Docker image to registry...$(NC)"
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_REPO):$(DOCKER_TAG)
	docker tag $(DOCKER_IMAGE):$(DOCKER_TAG) $(DOCKER_REPO):latest
	docker push $(DOCKER_REPO):$(DOCKER_TAG)
	docker push $(DOCKER_REPO):latest
	@echo "$(GREEN)✓ Image pushed to $(DOCKER_REPO)$(NC)"

docker-compose-up: ## Start services with docker-compose
	@echo "$(GREEN)Starting services with docker-compose...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"

docker-compose-down: ## Stop services with docker-compose
	@echo "$(GREEN)Stopping services with docker-compose...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-compose-logs: ## View docker-compose logs
	docker-compose logs -f

##@ Kubernetes Operations

k8s-deploy: ## Deploy to Kubernetes
	@echo "$(GREEN)Deploying to Kubernetes...$(NC)"
	kubectl apply -f k8s/
	@echo "$(GREEN)✓ Deployed to Kubernetes$(NC)"

k8s-delete: ## Delete from Kubernetes
	@echo "$(GREEN)Deleting from Kubernetes...$(NC)"
	kubectl delete -f k8s/
	@echo "$(GREEN)✓ Deleted from Kubernetes$(NC)"

k8s-status: ## Check Kubernetes deployment status
	@echo "$(GREEN)Checking Kubernetes status...$(NC)"
	kubectl get pods -l app=hdhr-scanner
	kubectl get deployments -l app=hdhr-scanner
	kubectl get services -l app=hdhr-scanner

k8s-logs: ## View Kubernetes logs
	kubectl logs -l app=hdhr-scanner -f

##@ Local Development

run: ## Run scanner locally
	@echo "$(GREEN)Running scanner...$(NC)"
	$(PYTHON) main.py

run-debug: ## Run scanner in debug mode
	@echo "$(GREEN)Running scanner in debug mode...$(NC)"
	$(PYTHON) main.py --debug

run-test-file: ## Run scanner with test file
	@echo "$(GREEN)Running scanner with test file...$(NC)"
	$(PYTHON) main.py --test-file

config-show: ## Show current configuration
	$(PYTHON) main.py --show-config

config-edit: ## Edit configuration interactively
	$(PYTHON) main.py --edit-config

config-reset: ## Reset configuration to defaults
	$(PYTHON) main.py --reset-config

##@ CI/CD

ci-test: ## Run CI tests locally
	@echo "$(GREEN)Running CI test suite...$(NC)"
	$(MAKE) lint
	$(MAKE) test-coverage
	$(MAKE) security-scan
	@echo "$(GREEN)✓ CI tests complete$(NC)"

ci-build: ## Full CI build process
	@echo "$(GREEN)Running full CI build...$(NC)"
	$(MAKE) install-dev
	$(MAKE) ci-test
	$(MAKE) docker-build
	$(MAKE) docker-test
	@echo "$(GREEN)✓ CI build complete$(NC)"

##@ Health & Monitoring

health-check: ## Run health check
	@echo "$(GREEN)Running health check...$(NC)"
	@bash scripts/health-check.sh

logs-tail: ## Tail application logs
	tail -f hdhr_scan.log

logs-errors: ## Show errors from logs
	grep ERROR hdhr_scan.log

logs-today: ## Show today's logs
	grep "$$(date +%Y-%m-%d)" hdhr_scan.log

##@ Cleanup

clean: ## Clean generated files
	@echo "$(GREEN)Cleaning generated files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache htmlcov .mypy_cache
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: clean ## Clean all generated files including Docker
	@echo "$(GREEN)Cleaning Docker resources...$(NC)"
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true
	docker rmi $(DOCKER_IMAGE):latest 2>/dev/null || true
	@echo "$(GREEN)✓ Full cleanup complete$(NC)"

##@ Documentation

docs-serve: ## Serve documentation locally
	@echo "$(GREEN)Serving documentation...$(NC)"
	@echo "README: http://localhost:8000/README.md"
	@echo "DEPLOYMENT: http://localhost:8000/DEPLOYMENT.md"
	@$(PYTHON) -m http.server 8000

##@ Release

version: ## Show current version
	@$(PYTHON) main.py --version

tag: ## Create git tag for current version
	@echo "$(GREEN)Creating git tag v$(DOCKER_TAG)...$(NC)"
	git tag -a v$(DOCKER_TAG) -m "Release version $(DOCKER_TAG)"
	git push origin v$(DOCKER_TAG)
	@echo "$(GREEN)✓ Tag created and pushed$(NC)"

release: ## Full release process
	@echo "$(GREEN)Starting release process...$(NC)"
	$(MAKE) ci-build
	$(MAKE) docker-push
	$(MAKE) tag
	@echo "$(GREEN)✓ Release complete$(NC)"

##@ Quick Commands

dev: install-dev test ## Quick dev setup and test
	@echo "$(GREEN)✓ Development environment ready$(NC)"

deploy-local: docker-build docker-compose-up ## Build and deploy locally
	@echo "$(GREEN)✓ Deployed locally$(NC)"

deploy-prod: ci-build docker-push k8s-deploy ## Full production deployment
	@echo "$(GREEN)✓ Deployed to production$(NC)"
