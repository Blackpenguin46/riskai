# 🤝 Contributing to RiskAI

Thank you for your interest in contributing to RiskAI! This guide will help you get started with contributing to our cybersecurity risk assessment platform.

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Contributing Guidelines](#contributing-guidelines)
5. [Pull Request Process](#pull-request-process)
6. [Issue Guidelines](#issue-guidelines)
7. [Coding Standards](#coding-standards)
8. [Testing Requirements](#testing-requirements)
9. [Documentation](#documentation)
10. [Community](#community)

## 📜 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

### Our Pledge
We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
- **Be respectful** and inclusive in all interactions
- **Be constructive** when giving feedback
- **Be collaborative** and help others learn
- **Be patient** with newcomers and questions
- **Focus on what's best** for the community and project

### Unacceptable Behavior
- Harassment, discrimination, or offensive comments
- Personal attacks or trolling
- Publishing private information without permission
- Any conduct that would be inappropriate in a professional setting

## 🚀 Getting Started

### Prerequisites
- **Git** for version control
- **Docker Desktop** (recommended) or manual setup
- **GitHub account** for contributions
- **Basic knowledge** of Python, JavaScript, or cybersecurity

### First Steps
1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up development environment** (see below)
4. **Find an issue** to work on or propose a new feature
5. **Make your changes** following our guidelines
6. **Submit a pull request**

## 🛠️ Development Setup

### Quick Setup (Docker)
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/riskai.git
cd riskai

# Add upstream remote
git remote add upstream https://github.com/Blackpenguin46/riskai.git

# Start development environment
./start-riskai-dev.sh  # Linux/macOS
# or
start-riskai-dev.bat   # Windows
```

### Manual Setup
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\\Scripts\\activate  # Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start services
# Terminal 1: Backend
cd backend && python main_api.py

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Development Tools
```bash
# Install development dependencies
pip install black flake8 mypy pytest pre-commit
npm install -D @types/node @types/react

# Set up pre-commit hooks
pre-commit install
```

## 📝 Contributing Guidelines

### Types of Contributions

#### 🐛 Bug Reports
- Use the bug report template
- Include steps to reproduce
- Provide system information
- Include error messages and logs

#### ✨ Feature Requests
- Use the feature request template
- Explain the use case and benefits
- Consider implementation complexity
- Discuss with maintainers first for large features

#### 📚 Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update outdated information
- Translate documentation

#### 🧪 Testing
- Add test cases for new features
- Improve test coverage
- Add integration tests
- Performance testing

#### 🎨 UI/UX Improvements
- Follow design system guidelines
- Ensure accessibility compliance
- Test on multiple devices/browsers
- Include screenshots in PRs

### Contribution Areas

#### Backend Development
- **API Endpoints**: New assessment features
- **Scoring Algorithms**: Mathematical improvements
- **Security Features**: Authentication, authorization
- **Database**: Schema improvements, migrations
- **Performance**: Optimization and caching

#### Frontend Development
- **User Interface**: React components and pages
- **Visualization**: Charts and interactive elements
- **Accessibility**: WCAG compliance improvements
- **Mobile**: Responsive design enhancements
- **Performance**: Bundle optimization

#### DevOps & Infrastructure
- **Docker**: Container improvements
- **CI/CD**: GitHub Actions workflows
- **Monitoring**: Logging and metrics
- **Security**: Vulnerability scanning
- **Documentation**: Deployment guides

#### Research & Academic
- **Algorithms**: Bias detection improvements
- **Frameworks**: New compliance standards
- **Validation**: Academic research integration
- **Benchmarking**: Industry comparisons
- **Publications**: Research paper contributions

## 🔄 Pull Request Process

### Before You Start
1. **Check existing issues** to avoid duplication
2. **Discuss large changes** in an issue first
3. **Fork and clone** the repository
4. **Create a feature branch** from `main`

### Making Changes
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... code, test, document ...

# Commit changes
git add .
git commit -m "feat: add new assessment feature"

# Push to your fork
git push origin feature/your-feature-name
```

### Pull Request Checklist
- [ ] **Branch is up to date** with main
- [ ] **Tests pass** locally
- [ ] **Code follows** style guidelines
- [ ] **Documentation updated** if needed
- [ ] **Commit messages** follow conventions
- [ ] **No merge conflicts**
- [ ] **Screenshots included** for UI changes

### Commit Message Format
We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(assessment): add real-time scoring calculation
fix(api): resolve authentication token expiration
docs(readme): update installation instructions
test(scoring): add unit tests for bias detection
```

### Review Process
1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** in staging environment
4. **Documentation review** if applicable
5. **Final approval** and merge

## 🐛 Issue Guidelines

### Bug Reports
Use the bug report template and include:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g. Windows 10, macOS 12.0, Ubuntu 20.04]
- Browser: [e.g. Chrome 95, Firefox 94]
- Version: [e.g. v1.2.0]

**Additional context**
Any other context about the problem.
```

### Feature Requests
Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.
```

### Issue Labels
- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `priority-high`: High priority issue
- `priority-low`: Low priority issue

## 🎨 Coding Standards

### Python (Backend)
```python
# Use Black for formatting
black backend/

# Use flake8 for linting
flake8 backend/

# Use mypy for type checking
mypy backend/

# Follow PEP 8 guidelines
# Use type hints
def calculate_score(responses: Dict[str, Any]) -> float:
    """Calculate assessment score based on responses."""
    pass

# Use docstrings
class AssessmentEngine:
    """Main assessment engine for processing responses."""
    
    def process_responses(self, responses: Dict[str, Any]) -> Dict[str, float]:
        """Process assessment responses and return scores."""
        pass
```

### JavaScript/TypeScript (Frontend)
```typescript
// Use Prettier for formatting
// Use ESLint for linting

// Use TypeScript interfaces
interface AssessmentResponse {
  questionId: string;
  response: string | number | boolean;
  timestamp: Date;
}

// Use functional components with hooks
const AssessmentForm: React.FC<AssessmentFormProps> = ({ onSubmit }) => {
  const [responses, setResponses] = useState<AssessmentResponse[]>([]);
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Component JSX */}
    </form>
  );
};

// Use meaningful variable names
const calculateRiskScore = (responses: AssessmentResponse[]): number => {
  // Implementation
};
```

### CSS/Styling
```css
/* Use Tailwind CSS classes when possible */
.assessment-card {
  @apply bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow;
}

/* Use BEM methodology for custom CSS */
.assessment-form__input {
  @apply w-full px-3 py-2 border border-gray-300 rounded-md;
}

.assessment-form__input--error {
  @apply border-red-500 bg-red-50;
}
```

### Database
```sql
-- Use descriptive table and column names
CREATE TABLE assessment_responses (
    id SERIAL PRIMARY KEY,
    assessment_id UUID NOT NULL,
    question_id VARCHAR(50) NOT NULL,
    response_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add proper indexes
CREATE INDEX idx_assessment_responses_assessment_id ON assessment_responses(assessment_id);
CREATE INDEX idx_assessment_responses_question_id ON assessment_responses(question_id);
```

## 🧪 Testing Requirements

### Backend Testing
```python
# Unit tests with pytest
def test_calculate_score():
    responses = {"q1": "yes", "q2": "no"}
    score = calculate_score(responses)
    assert score >= 0 and score <= 100

# Integration tests
def test_assessment_api_endpoint():
    response = client.post("/api/assessment/start", json={"company": "Test Corp"})
    assert response.status_code == 200
    assert "assessment_id" in response.json()

# Test coverage should be > 80%
pytest --cov=backend tests/
```

### Frontend Testing
```typescript
// Component tests with Jest and React Testing Library
import { render, screen, fireEvent } from '@testing-library/react';
import AssessmentForm from './AssessmentForm';

test('renders assessment form', () => {
  render(<AssessmentForm onSubmit={jest.fn()} />);
  expect(screen.getByText('Assessment Questions')).toBeInTheDocument();
});

test('submits form with responses', () => {
  const mockSubmit = jest.fn();
  render(<AssessmentForm onSubmit={mockSubmit} />);
  
  fireEvent.click(screen.getByText('Submit'));
  expect(mockSubmit).toHaveBeenCalled();
});
```

### End-to-End Testing
```javascript
// Cypress tests
describe('Assessment Flow', () => {
  it('completes full assessment', () => {
    cy.visit('/assessment');
    cy.get('[data-testid="company-name"]').type('Test Company');
    cy.get('[data-testid="start-assessment"]').click();
    
    // Complete assessment questions
    cy.get('[data-testid="question-1"]').click();
    cy.get('[data-testid="submit-section"]').click();
    
    // Verify results
    cy.get('[data-testid="assessment-score"]').should('be.visible');
  });
});
```

## 📚 Documentation

### Code Documentation
- **Python**: Use docstrings following Google style
- **TypeScript**: Use JSDoc comments
- **API**: Document all endpoints with OpenAPI/Swagger
- **README**: Keep installation and usage instructions current

### Documentation Standards
```python
def calculate_risk_score(responses: Dict[str, Any], weights: Dict[str, float]) -> float:
    """Calculate risk score based on assessment responses.
    
    Args:
        responses: Dictionary of question IDs to response values
        weights: Dictionary of question IDs to weight values
        
    Returns:
        Risk score between 0 and 100
        
    Raises:
        ValueError: If responses or weights are invalid
        
    Example:
        >>> responses = {"q1": "yes", "q2": "no"}
        >>> weights = {"q1": 0.6, "q2": 0.4}
        >>> calculate_risk_score(responses, weights)
        75.0
    """
```

### API Documentation
```python
@app.post("/api/assessment/start", response_model=AssessmentResponse)
async def start_assessment(request: AssessmentRequest):
    """Start a new cybersecurity risk assessment.
    
    Creates a new assessment session and returns the assessment ID
    for tracking progress and results.
    
    Args:
        request: Assessment request containing company profile information
        
    Returns:
        AssessmentResponse with assessment_id and initial configuration
        
    Raises:
        HTTPException: 400 if request data is invalid
        HTTPException: 500 if assessment creation fails
    """
```

## 🌟 Recognition

### Contributors
We recognize contributors in several ways:
- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in changelog
- **Social media**: Highlighted on project accounts
- **Swag**: Stickers and merchandise for significant contributions

### Contribution Types
- **Code**: Bug fixes, features, optimizations
- **Documentation**: Guides, tutorials, API docs
- **Design**: UI/UX improvements, graphics
- **Testing**: Test cases, quality assurance
- **Community**: Support, mentoring, advocacy
- **Research**: Academic contributions, validation

## 💬 Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord**: Real-time chat and collaboration
- **Email**: security@riskai.com for security issues

### Getting Help
- **Documentation**: Check README and guides first
- **Search Issues**: Look for existing solutions
- **Ask Questions**: Use GitHub Discussions
- **Join Discord**: Get real-time help from community

### Community Guidelines
- **Be respectful** and professional
- **Help others** when you can
- **Share knowledge** and experiences
- **Follow** the code of conduct
- **Stay on topic** in discussions

## 🎯 Roadmap

### Current Priorities
1. **Performance Optimization**: Improve assessment loading times
2. **Mobile Experience**: Better responsive design
3. **API Enhancements**: More comprehensive endpoints
4. **Security Features**: Enhanced authentication
5. **Documentation**: Comprehensive user guides

### Future Goals
- **Multi-language Support**: Internationalization
- **Advanced Analytics**: Machine learning insights
- **Enterprise Features**: SSO, multi-tenancy
- **Mobile Apps**: Native iOS and Android
- **Integrations**: Third-party security tools

## 📞 Contact

### Maintainers
- **Project Lead**: [@Blackpenguin46](https://github.com/Blackpenguin46)
- **Technical Lead**: [Contact via GitHub Issues]
- **Community Manager**: [Contact via Discord]

### Security Issues
For security vulnerabilities, please email: security@riskai.com
Do not create public issues for security problems.

### General Questions
- **GitHub Discussions**: For general questions
- **GitHub Issues**: For bugs and feature requests
- **Discord**: For real-time chat

---

## 🙏 Thank You

Thank you for contributing to RiskAI! Your contributions help make cybersecurity risk assessment more accessible and effective for organizations worldwide.

**Every contribution matters**, whether it's:
- Fixing a typo in documentation
- Reporting a bug
- Suggesting a new feature
- Contributing code
- Helping other users

Together, we're building a stronger, more secure digital world! 🛡️

---

*This contributing guide is a living document. Please suggest improvements via pull requests or issues.*