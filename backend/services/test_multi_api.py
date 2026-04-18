"""
Multi-API Test Script for Social Autopilot AI Service

This script tests the AI service with multiple API providers (Gemini, Claude, NIM)
to ensure proper functionality and compare output quality.

Author: Social Autopilot Team
Version: 1.0.0
"""

import asyncio
import os
import sys
from typing import Dict, Any
from datetime import datetime

# Add the services directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_service import (
    generate_post, 
    validate_api_keys, 
    get_supported_models,
    AIModel,
    AIConstants
)


class TestResults:
    """Class to store and manage test results"""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = datetime.now()
    
    def add_result(self, model: str, success: bool, response: str = None, error: str = None):
        """Add a test result"""
        self.results[model] = {
            "success": success,
            "response": response,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "="*80)
        print("TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for result in self.results.values() if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Duration: {(datetime.now() - self.start_time).total_seconds():.2f} seconds")
        print("="*80)
        
        for model, result in self.results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"\n{status} - {model.upper()} API")
            
            if result["success"]:
                print(f"Response Preview: {result['response'][:100]}...")
            else:
                print(f"Error: {result['error']}")


async def test_single_model(model: str, test_results: TestResults) -> None:
    """
    Test a single AI model
    
    Args:
        model: Name of the model to test
        test_results: TestResults object to store results
    """
    print(f"\n{'='*80}")
    print(f"Testing {model.upper()} API")
    print(f"{'='*80}")
    
    try:
        # Check if API key is available for this model
        if model == AIModel.GEMINI.value:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if not gemini_key or gemini_key == AIConstants.PLACEHOLDER_API_KEY:
                error_msg = "GEMINI_API_KEY not properly configured in .env"
                print(f"⚠️  {error_msg}")
                test_results.add_result(model, False, error=error_msg)
                return
        
        elif model == AIModel.NIM.value:
            nim_key = os.getenv("NIM_API_KEY")
            if not nim_key or nim_key == AIConstants.PLACEHOLDER_API_KEY:
                error_msg = "NIM_API_KEY not properly configured in .env"
                print(f"⚠️  {error_msg}")
                test_results.add_result(model, False, error=error_msg)
                return
        
        # Test parameters
        test_params = {
            "platform": "Twitter",
            "topic": "AI Ethics",
            "brand_voice": "Professional",
            "model": model
        }
        
        print(f"Test Parameters:")
        print(f"  Platform: {test_params['platform']}")
        print(f"  Topic: {test_params['topic']}")
        print(f"  Brand Voice: {test_params['brand_voice']}")
        print(f"  Model: {test_params['model']}")
        
        # Generate post
        print(f"\nGenerating post...")
        result = await generate_post(**test_params)
        
        print(f"\n✅ SUCCESS - Generated Post:")
        print(f"{'-'*80}")
        print(result)
        print(f"{'-'*80}")
        
        test_results.add_result(model, True, response=result)
        
    except Exception as e:
        error_msg = f"Test failed: {str(e)}"
        print(f"\n❌ FAILED - {error_msg}")
        test_results.add_result(model, False, error=error_msg)


async def test_all_models() -> None:
    """
    Test all supported AI models
    """
    print("🚀 Starting Multi-API Test Suite")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize test results
    test_results = TestResults()
    
    # Validate API keys
    print(f"\n🔑 Validating API Keys...")
    api_key_status = validate_api_keys()
    for model, is_valid in api_key_status.items():
        status = "✅" if is_valid else "❌"
        print(f"  {status} {model.upper()}: {'Valid' if is_valid else 'Invalid/Missing'}")
    
    # Get supported models
    supported_models = get_supported_models()
    print(f"\n📋 Supported Models: {', '.join(supported_models)}")
    
    # Test each model
    for model in supported_models:
        await test_single_model(model, test_results)
    
    # Print summary
    test_results.print_summary()
    
    # Provide recommendations
    print(f"\n💡 Recommendations:")
    if not api_key_status[AIModel.GEMINI.value]:
        print("  • Add a valid GEMINI_API_KEY to .env to test Gemini API")
    if not api_key_status[AIModel.NIM.value]:
        print("  • Add a valid NIM_API_KEY to .env to test NIM API")
    
    print(f"\n✨ Test suite completed!")


def main():
    """Main function to run the test suite"""
    try:
        asyncio.run(test_all_models())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()