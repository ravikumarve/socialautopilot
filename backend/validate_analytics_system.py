"""
Validation Script for Analytics System

This script validates the Phase 4 implementation without requiring
full database connectivity or external dependencies.
"""

import os
import sys
import ast
import re
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class AnalyticsValidator:
    """Validator for analytics system implementation"""

    def __init__(self):
        self.validation_results = []
        self.passed_checks = 0
        self.failed_checks = 0

    def record_check(self, check_name: str, passed: bool, message: str = ""):
        """Record validation check result"""
        self.validation_results.append({
            "check": check_name,
            "passed": passed,
            "message": message
        })
        if passed:
            self.passed_checks += 1
        else:
            self.failed_checks += 1

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name}")
        if message:
            print(f"  {message}")

    def validate_file_exists(self, filepath: str) -> bool:
        """Check if a file exists"""
        exists = os.path.exists(filepath)
        self.record_check(
            f"File exists: {filepath}",
            exists,
            f"File found" if exists else "File not found"
        )
        return exists

    def validate_python_syntax(self, filepath: str) -> bool:
        """Validate Python file syntax"""
        try:
            with open(filepath, 'r') as f:
                code = f.read()
            ast.parse(code)
            self.record_check(
                f"Valid Python syntax: {filepath}",
                True,
                "No syntax errors"
            )
            return True
        except SyntaxError as e:
            self.record_check(
                f"Valid Python syntax: {filepath}",
                False,
                f"Syntax error: {e}"
            )
            return False

    def validate_imports(self, filepath: str, required_imports: List[str]) -> bool:
        """Check if required imports are present"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            missing_imports = []
            for imp in required_imports:
                if imp not in content:
                    missing_imports.append(imp)

            passed = len(missing_imports) == 0
            self.record_check(
                f"Required imports in {filepath}",
                passed,
                f"Missing: {missing_imports}" if not passed else "All imports present"
            )
            return passed
        except Exception as e:
            self.record_check(
                f"Required imports in {filepath}",
                False,
                f"Error: {e}"
            )
            return False

    def validate_class_exists(self, filepath: str, class_name: str) -> bool:
        """Check if a class is defined in the file"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Check for class definition
            class_pattern = rf'class\s+{class_name}\s*\(.*?\):'
            found = re.search(class_pattern, content) is not None

            self.record_check(
                f"Class '{class_name}' exists in {filepath}",
                found,
                f"Class found" if found else "Class not found"
            )
            return found
        except Exception as e:
            self.record_check(
                f"Class '{class_name}' exists in {filepath}",
                False,
                f"Error: {e}"
            )
            return False

    def validate_function_exists(self, filepath: str, function_name: str) -> bool:
        """Check if a function is defined in the file"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Check for function definition
            func_pattern = rf'def\s+{function_name}\s*\(.*?\)\s*:'
            found = re.search(func_pattern, content) is not None

            self.record_check(
                f"Function '{function_name}' exists in {filepath}",
                found,
                f"Function found" if found else "Function not found"
            )
            return found
        except Exception as e:
            self.record_check(
                f"Function '{function_name}' exists in {filepath}",
                False,
                f"Error: {e}"
            )
            return False

    def validate_endpoint_exists(self, filepath: str, endpoint_path: str) -> bool:
        """Check if an API endpoint is defined"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Check for endpoint definition
            endpoint_pattern = rf'@router\.(get|post|put|delete)\(["\']{endpoint_path}["\']'
            found = re.search(endpoint_pattern, content) is not None

            self.record_check(
                f"Endpoint '{endpoint_path}' exists in {filepath}",
                found,
                f"Endpoint found" if found else "Endpoint not found"
            )
            return found
        except Exception as e:
            self.record_check(
                f"Endpoint '{endpoint_path}' exists in {filepath}",
                False,
                f"Error: {e}"
            )
            return False

    def validate_docstring_coverage(self, filepath: str) -> bool:
        """Check if functions have docstrings"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Find all function definitions
            func_pattern = r'def\s+(\w+)\s*\([^)]*\)\s*:'
            functions = re.findall(func_pattern, content)

            functions_with_docs = 0
            for func in functions:
                # Look for docstring after function definition
                func_pattern = rf'def\s+{func}\s*\([^)]*\)\s*:\s*"""'
                if re.search(func_pattern, content):
                    functions_with_docs += 1

            coverage = (functions_with_docs / len(functions) * 100) if functions else 0
            passed = coverage >= 80  # At least 80% coverage

            self.record_check(
                f"Docstring coverage in {filepath}",
                passed,
                f"{coverage:.1f}% coverage ({functions_with_docs}/{len(functions)} functions)"
            )
            return passed
        except Exception as e:
            self.record_check(
                f"Docstring coverage in {filepath}",
                False,
                f"Error: {e}"
            )
            return False

    def validate_error_handling(self, filepath: str) -> bool:
        """Check if error handling is present"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Count try-except blocks
            try_blocks = len(re.findall(r'\btry\s*:', content))
            except_blocks = len(re.findall(r'\bexcept\s+', content))

            # Should have at least some error handling
            passed = try_blocks >= 3 and except_blocks >= 3

            self.record_check(
                f"Error handling in {filepath}",
                passed,
                f"Found {try_blocks} try blocks, {except_blocks} except blocks"
            )
            return passed
        except Exception as e:
            self.record_check(
                f"Error handling in {filepath}",
                False,
                f"Error: {e}"
            )
            return False

    def validate_logging(self, filepath: str) -> bool:
        """Check if logging is present"""
        try:
            with open(filepath, 'r') as f:
                content = f.read()

            # Check for logger usage
            log_statements = len(re.findall(r'logger\.(info|error|warning|debug)', content))

            # Should have some logging
            passed = log_statements >= 5

            self.record_check(
                f"Logging in {filepath}",
                passed,
                f"Found {log_statements} log statements"
            )
            return passed
        except Exception as e:
            self.record_check(
                f"Logging in {filepath}",
                False,
                f"Error: {e}"
            )
            return False

    def validate_analytics_service(self):
        """Validate analytics service implementation"""
        print("\n📊 Analytics Service Validation")
        print("-" * 50)

        filepath = "backend/services/analytics_service.py"

        # File existence
        if not self.validate_file_exists(filepath):
            return

        # Syntax validation
        if not self.validate_python_syntax(filepath):
            return

        # Required imports
        required_imports = [
            "from typing import Dict, List, Any, Optional, Tuple",
            "from datetime import datetime, timedelta",
            "from sqlalchemy.orm import Session",
            "from backend import models"
        ]
        self.validate_imports(filepath, required_imports)

        # Class existence
        self.validate_class_exists(filepath, "AnalyticsService")

        # Required methods
        required_methods = [
            "get_overview_stats",
            "get_feedback_patterns",
            "get_performance_trends",
            "get_content_recommendations",
            "get_comprehensive_insights",
            "get_post_performance_details"
        ]

        for method in required_methods:
            self.validate_function_exists(filepath, method)

        # Quality checks
        self.validate_docstring_coverage(filepath)
        self.validate_error_handling(filepath)
        self.validate_logging(filepath)

    def validate_feedback_optimizer(self):
        """Validate feedback optimizer implementation"""
        print("\n🔄 Feedback Optimizer Validation")
        print("-" * 50)

        filepath = "backend/services/feedback_optimizer.py"

        # File existence
        if not self.validate_file_exists(filepath):
            return

        # Syntax validation
        if not self.validate_python_syntax(filepath):
            return

        # Required imports
        required_imports = [
            "from typing import Dict, List, Any, Optional, Tuple",
            "from datetime import datetime, timedelta",
            "from sqlalchemy.orm import Session",
            "from backend import models"
        ]
        self.validate_imports(filepath, required_imports)

        # Class existence
        self.validate_class_exists(filepath, "FeedbackLoopOptimizer")

        # Required methods
        required_methods = [
            "analyze_approval_patterns",
            "get_optimization_suggestions",
            "track_optimization_progress"
        ]

        for method in required_methods:
            self.validate_function_exists(filepath, method)

        # Quality checks
        self.validate_docstring_coverage(filepath)
        self.validate_error_handling(filepath)
        self.validate_logging(filepath)

    def validate_analytics_router(self):
        """Validate analytics router implementation"""
        print("\n🌐 Analytics Router Validation")
        print("-" * 50)

        filepath = "backend/routers/analytics.py"

        # File existence
        if not self.validate_file_exists(filepath):
            return

        # Syntax validation
        if not self.validate_python_syntax(filepath):
            return

        # Required imports
        required_imports = [
            "from fastapi import APIRouter, Depends, HTTPException, Query",
            "from sqlalchemy.orm import Session",
            "from backend.services.analytics_service import get_analytics_service",
            "from backend.services.feedback_optimizer import get_feedback_optimizer"
        ]
        self.validate_imports(filepath, required_imports)

        # Required endpoints
        required_endpoints = [
            "/overview",
            "/feedback-patterns",
            "/performance-trends",
            "/recommendations",
            "/insights",
            "/post/{post_id}",
            "/platform/{platform}",
            "/health",
            "/feedback/patterns",
            "/feedback/optimization",
            "/feedback/progress"
        ]

        for endpoint in required_endpoints:
            self.validate_endpoint_exists(filepath, endpoint)

        # Quality checks
        self.validate_docstring_coverage(filepath)
        self.validate_error_handling(filepath)

    def validate_frontend_component(self):
        """Validate frontend analytics component"""
        print("\n🎨 Frontend Component Validation")
        print("-" * 50)

        filepath = "frontend/components/AnalyticsPanel.tsx"

        # File existence
        if not self.validate_file_exists(filepath):
            return

        # Check for key features
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for tabs
        has_tabs = "activeTab" in content and "useState" in content
        self.record_check(
            "Tab navigation in AnalyticsPanel",
            has_tabs,
            "Tab navigation found" if has_tabs else "Tab navigation not found"
        )

        # Check for health score display
        has_health_score = "health_score" in content
        self.record_check(
            "Health score display in AnalyticsPanel",
            has_health_score,
            "Health score display found" if has_health_score else "Health score display not found"
        )

        # Check for API calls
        has_api_calls = "/analytics/insights" in content or "fetchAnalytics" in content
        self.record_check(
            "API integration in AnalyticsPanel",
            has_api_calls,
            "API integration found" if has_api_calls else "API integration not found"
        )

        # Check for responsive design
        has_responsive = "md:" in content or "lg:" in content
        self.record_check(
            "Responsive design in AnalyticsPanel",
            has_responsive,
            "Responsive design found" if has_responsive else "Responsive design not found"
        )

    def run_validation(self):
        """Run all validation checks"""
        print("=" * 60)
        print("Phase 4: Analytics & Feedback Loop Validation")
        print("=" * 60)

        # Validate all components
        self.validate_analytics_service()
        self.validate_feedback_optimizer()
        self.validate_analytics_router()
        self.validate_frontend_component()

        # Print summary
        print("\n" + "=" * 60)
        print("Validation Summary")
        print("=" * 60)
        print(f"Total Checks: {self.passed_checks + self.failed_checks}")
        print(f"✅ Passed: {self.passed_checks}")
        print(f"❌ Failed: {self.failed_checks}")
        print(f"Success Rate: {(self.passed_checks / (self.passed_checks + self.failed_checks) * 100):.1f}%")

        if self.failed_checks > 0:
            print("\n❌ Failed Checks:")
            for result in self.validation_results:
                if not result["passed"]:
                    print(f"  - {result['check']}: {result['message']}")

        return self.failed_checks == 0


def main():
    """Main validation execution"""
    validator = AnalyticsValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()