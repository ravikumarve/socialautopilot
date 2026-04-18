.PHONY: dev backend frontend install-deps

# Run both backend and frontend
dev:
	@echo "Starting Social Autopilot..."
	@echo "Backend will run on http://localhost:8000"
	@echo "Frontend will run on http://localhost:3000"
	@echo "Press Ctrl+C to stop both services"
	@tmux new-session -d -s socialautopilot 'make backend' \\; \
	split-window -h 'make frontend' \\; \
	attach-session -d

# Run backend only
backend:
	@echo "Starting backend server..."
	cd backend && uvicorn main:app --reload --port 8000

# Run frontend only
frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

# Install dependencies
install-deps:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Environment setup
setup:
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
		echo "Please edit .env to add your API keys"; \
	else \
		echo ".env already exists"; \
	fi