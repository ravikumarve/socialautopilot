# CONTRIBUTING TO SOCIAL AUTOPILLOT

Thank you for considering contributing to Social Autopilot! This document will guide you through our contribution process, helping you effectively participate in the project's development.

## Before You Start

### 1. Understand the Project
Social Autopilot is a **local-first, CPU-only** social media automation tool designed for **solo builders** who want to maintain an active online presence without sacrificing authenticity or control. It features:
- AI-powered content generation
- Human-in-the-loop review process
- Platform-specific optimization for Twitter/X, LinkedIn, and Threads
- Privacy-focused design with local processing

### 2. Choose Your Contribution Type
You can contribute in several ways:
- **Code**: Fix bugs, add features, or improve performance
- **Documentation**: Improve this README, contributing guide, or technical docs
- **Testing**: Write tests, identify edge cases, or improve test coverage
- **Design**: Enhance the UI/UX or create visual assets
- **AI Training**: Help improve prompt engineering and AI interactions

## Setting Up for Development

### Prerequisites
- Node.js (v16+)
- Python (v3.8+)
- pip (Python package manager)
- npm or yarn

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social-autopilot
   ```
2. Install dependencies:
   ```bash
   make install-deps
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to add your API keys:
   # GEMINI_API_KEY=your_key_here
   # TWITTER_BEARER_TOKEN=
   # LINKEDIN_ACCESS_TOKEN=
   # THREADS_ACCESS_TOKEN=
   # DATABASE_URL=sqlite:///./social_autopilot.db
   ```

## Development Workflow

### Branching Strategy
- **Main Branch**: `main` - stable releases
- **Feature Branches**: `feat/`, `fix/`, `chore/` prefixes
- **Create a branch**:
   ```bash
   git checkout -b feat/your-feature-name
   ```

### Commit Guidelines
- Follow **Conventional Commits** format:
   `feat:`, `fix:`, `chore:` prefixes
- Example:
   ```bash
   git commit -m "feat: add bulk generation feature"
   ```

### Testing
- Run tests:
   ```bash
   npm run test
   ```
- For TDD:
   ```bash
   npm run test:watch
   ```

### Code Review
1. Push your branch:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request
3. Request review from maintainers
4. Address feedback before merging

## Contribution Guidelines

### Code Contributions
- Follow existing code style and conventions
- Add type annotations where appropriate
- Keep functions small and focused
- Use meaningful variable names

### Documentation Contributions
- Keep documentation concise and developer-focused
- Use clear section headings
- Include code examples where helpful

### AI-Related Contributions
- For prompt engineering:
   - Maintain brand voice consistency
   - Use Gemini's 1M token context effectively
   - Add fallback mechanisms for failed generations

## Reporting Issues

### Bug Reports
1. Search existing issues
2. Create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs Actual behavior
   - Any error messages

### Feature Requests
1. Search existing feature requests
2. Create a new issue with:
   - Use case
   - Proposed implementation
   - Benefits to users

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## Need Help?

- **Documentation**: Refer to this README and AGENTS.md
- **Discussion**: Open an issue for general questions
- **Security**: Report vulnerabilities privately to the maintainers

Thank you for contributing to Social Autopilot!