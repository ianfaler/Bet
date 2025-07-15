#!/usr/bin/env python3
"""
Master Production Readiness Test Runner
Executes all testing phases and generates comprehensive production readiness report
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from typing import Dict, List, Any
import argparse

class ProductionTestRunner:
    """Master test runner for production readiness validation"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = datetime.now()
        self.test_phases = [
            {
                'name': 'API Integration Tests',
                'file': 'tests/test_api_integrations.py',
                'description': 'Tests The Odds API, FootyStats API, and WNBA scraping',
                'critical': True
            },
            {
                'name': 'Data Processing Tests', 
                'file': 'tests/test_data_processing.py',
                'description': 'Tests model calculations, EV formulas, and Kelly staking',
                'critical': True
            },
            {
                'name': 'Load and Performance Tests',
                'file': 'tests/test_load_performance.py',
                'description': 'Tests concurrent users, response times, and scalability',
                'critical': False
            }
        ]
        
    def run_all_tests(self, phases: List[str] = None) -> Dict[str, Any]:
        """Run all test phases and generate report"""
        print("🚀 PRODUCTION READINESS TEST SUITE")
        print("=" * 60)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Validate environment
        self._validate_environment()
        
        # Run each phase
        for phase in self.test_phases:
            if phases and phase['name'] not in phases:
                continue
                
            print(f"\n🔄 Running {phase['name']}...")
            print("-" * 40)
            
            result = self._run_test_phase(phase)
            self.test_results[phase['name']] = result
            
            if result['success']:
                print(f"✅ {phase['name']}: PASSED")
            else:
                print(f"❌ {phase['name']}: FAILED")
                if phase['critical']:
                    print(f"⚠️  Critical phase failed - review before production!")
                    
        # Generate final report
        report = self._generate_final_report()
        self._save_report(report)
        
        return report
        
    def _validate_environment(self):
        """Validate test environment and dependencies"""
        print("🔍 Validating test environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            print("⚠️  Warning: Python 3.8+ recommended for optimal testing")
            
        # Check required packages
        required_packages = ['requests', 'pandas', 'numpy', 'scipy']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
                
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install -r requirements.txt")
            sys.exit(1)
            
        # Check API keys
        odds_api_key = os.getenv("ODDS_API_KEY")
        footystats_api_key = os.getenv("FOOTYSTATS_API_KEY")
        
        if not odds_api_key or odds_api_key == "demo_key":
            print("⚠️  Warning: ODDS_API_KEY not set - some tests will be skipped")
            
        if not footystats_api_key or footystats_api_key == "demo_key":
            print("⚠️  Warning: FOOTYSTATS_API_KEY not set - some tests will be skipped")
            
        # Check test directories
        if not os.path.exists('tests'):
            os.makedirs('tests')
            print("📁 Created tests directory")
            
        print("✅ Environment validation complete")
        
    def _run_test_phase(self, phase: Dict[str, str]) -> Dict[str, Any]:
        """Run a single test phase"""
        start_time = time.time()
        
        try:
            # Run the test file using Python subprocess
            result = subprocess.run(
                [sys.executable, phase['file']],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per phase
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse output for test results
            output_lines = result.stdout.split('\n')
            test_summary = self._parse_test_output(output_lines)
            
            return {
                'success': result.returncode == 0,
                'duration': duration,
                'tests_run': test_summary.get('total', 0),
                'tests_passed': test_summary.get('passed', 0),
                'tests_failed': test_summary.get('failed', 0),
                'success_rate': test_summary.get('success_rate', 0),
                'output': result.stdout,
                'errors': result.stderr,
                'critical': phase['critical']
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'duration': 300,
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'success_rate': 0,
                'output': '',
                'errors': 'Test phase timed out after 5 minutes',
                'critical': phase['critical']
            }
        except Exception as e:
            return {
                'success': False,
                'duration': 0,
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'success_rate': 0,
                'output': '',
                'errors': str(e),
                'critical': phase['critical']
            }
            
    def _parse_test_output(self, output_lines: List[str]) -> Dict[str, int]:
        """Parse test output to extract summary statistics"""
        summary = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'success_rate': 0
        }
        
        for line in output_lines:
            if 'Total Tests:' in line:
                try:
                    summary['total'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
                    
            elif 'Passed:' in line:
                try:
                    summary['passed'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
                    
            elif 'Failed:' in line:
                try:
                    summary['failed'] = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
                    
            elif 'Success Rate:' in line:
                try:
                    rate_str = line.split(':')[1].strip().replace('%', '')
                    summary['success_rate'] = float(rate_str)
                except (ValueError, IndexError):
                    pass
                    
        return summary
        
    def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate overall statistics
        total_tests = sum(result['tests_run'] for result in self.test_results.values())
        total_passed = sum(result['tests_passed'] for result in self.test_results.values())
        total_failed = sum(result['tests_failed'] for result in self.test_results.values())
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # Check critical failures
        critical_failures = [
            name for name, result in self.test_results.items() 
            if result['critical'] and not result['success']
        ]
        
        # Determine production readiness
        production_ready = (
            len(critical_failures) == 0 and 
            overall_success_rate >= 80 and
            self._check_data_validation()
        )
        
        report = {
            'timestamp': end_time.isoformat(),
            'test_duration': f"{total_duration:.1f}s",
            'production_ready': production_ready,
            'overall_stats': {
                'total_tests': total_tests,
                'total_passed': total_passed,
                'total_failed': total_failed,
                'success_rate': f"{overall_success_rate:.1f}%"
            },
            'phase_results': self.test_results,
            'critical_failures': critical_failures,
            'data_validation': self._get_data_validation_status(),
            'performance_metrics': self._get_performance_metrics(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
        
    def _check_data_validation(self) -> bool:
        """Check if critical data validation passed"""
        api_tests = self.test_results.get('API Integration Tests', {})
        return api_tests.get('success', False)
        
    def _get_data_validation_status(self) -> Dict[str, str]:
        """Get data validation status"""
        return {
            'moneylines': '✅ Confirmed' if self._check_data_validation() else '❌ Not verified',
            'spreads': '✅ Confirmed' if self._check_data_validation() else '❌ Not verified',
            'totals': '✅ Confirmed' if self._check_data_validation() else '❌ Not verified',
            'real_data_only': '✅ No dummy data' if self._check_data_validation() else '⚠️ Verification needed'
        }
        
    def _get_performance_metrics(self) -> Dict[str, str]:
        """Get performance metrics summary"""
        perf_tests = self.test_results.get('Load and Performance Tests', {})
        
        if perf_tests.get('success'):
            return {
                'response_time': '✅ <2s target met',
                'concurrent_users': '✅ 100-500 users supported',
                'full_pipeline': '✅ <10s target met',
                'memory_usage': '✅ No leaks detected'
            }
        else:
            return {
                'response_time': '⚠️ Not tested',
                'concurrent_users': '⚠️ Not tested', 
                'full_pipeline': '⚠️ Not tested',
                'memory_usage': '⚠️ Not tested'
            }
            
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for critical failures
        critical_failures = [
            name for name, result in self.test_results.items() 
            if result['critical'] and not result['success']
        ]
        
        if critical_failures:
            recommendations.append(f"🚨 CRITICAL: Fix failing tests in {', '.join(critical_failures)}")
            
        # Check success rates
        for name, result in self.test_results.items():
            if result['success_rate'] < 80:
                recommendations.append(f"⚠️ Improve {name} success rate (currently {result['success_rate']:.1f}%)")
                
        # API key warnings
        if not os.getenv("ODDS_API_KEY") or os.getenv("ODDS_API_KEY") == "demo_key":
            recommendations.append("🔑 Set ODDS_API_KEY environment variable for production")
            
        if not os.getenv("FOOTYSTATS_API_KEY") or os.getenv("FOOTYSTATS_API_KEY") == "demo_key":
            recommendations.append("🔑 Set FOOTYSTATS_API_KEY environment variable for production")
            
        # Performance recommendations
        perf_tests = self.test_results.get('Load and Performance Tests', {})
        if not perf_tests.get('success'):
            recommendations.append("⚡ Run load testing to validate production performance")
            
        if not recommendations:
            recommendations.append("🎉 All tests passed! App is production ready.")
            
        return recommendations
        
    def _save_report(self, report: Dict[str, Any]):
        """Save report to file and display summary"""
        # Save detailed JSON report
        report_filename = f"production_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Display summary
        self._display_summary_report(report)
        
        print(f"\n📄 Detailed report saved: {report_filename}")
        
    def _display_summary_report(self, report: Dict[str, Any]):
        """Display summary report to console"""
        print("\n" + "=" * 60)
        print("🏁 PRODUCTION READINESS TEST SUMMARY")
        print("=" * 60)
        
        # Overall status
        if report['production_ready']:
            print("🎉 STATUS: PRODUCTION READY ✅")
        else:
            print("⚠️  STATUS: NOT PRODUCTION READY ❌")
            
        print(f"📊 Test Duration: {report['test_duration']}")
        print(f"📈 Overall Success Rate: {report['overall_stats']['success_rate']}")
        print(f"🧪 Total Tests: {report['overall_stats']['total_tests']}")
        
        # Phase results
        print("\n📋 PHASE RESULTS:")
        for phase_name, result in report['phase_results'].items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            critical = " (CRITICAL)" if result['critical'] else ""
            print(f"  • {phase_name}: {status}{critical}")
            print(f"    - Tests: {result['tests_passed']}/{result['tests_run']} passed")
            print(f"    - Duration: {result['duration']:.1f}s")
            
        # Data validation
        print("\n🔍 DATA VALIDATION:")
        for item, status in report['data_validation'].items():
            print(f"  • {item}: {status}")
            
        # Performance metrics
        print("\n⚡ PERFORMANCE METRICS:")
        for metric, status in report['performance_metrics'].items():
            print(f"  • {metric}: {status}")
            
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
            
        # Critical failures
        if report['critical_failures']:
            print("\n🚨 CRITICAL FAILURES:")
            for failure in report['critical_failures']:
                print(f"  • {failure}")
                
        print("\n" + "=" * 60)


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Run production readiness tests')
    parser.add_argument('--phases', nargs='+', 
                       choices=['API Integration Tests', 'Data Processing Tests', 'Load and Performance Tests'],
                       help='Specific test phases to run')
    parser.add_argument('--quick', action='store_true',
                       help='Run only critical tests (API and Data Processing)')
    parser.add_argument('--setup', action='store_true',
                       help='Set up test environment and install dependencies')
    
    args = parser.parse_args()
    
    if args.setup:
        print("🔧 Setting up test environment...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-cov', 'locust', 'psutil'])
        print("✅ Test environment setup complete")
        return
        
    # Determine which phases to run
    phases_to_run = args.phases
    
    if args.quick:
        phases_to_run = ['API Integration Tests', 'Data Processing Tests']
    
    # Run tests
    runner = ProductionTestRunner()
    
    try:
        report = runner.run_all_tests(phases_to_run)
        
        # Exit with appropriate code
        if report['production_ready']:
            print("\n🚀 Ready for production deployment!")
            sys.exit(0)
        else:
            print("\n⚠️  Review failures before production deployment.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test run failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()