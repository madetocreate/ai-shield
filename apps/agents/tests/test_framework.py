"""
Agent Testing Framework - Unit Tests, Integration Tests, Performance Tests

Features:
- Test Framework für Agents
- Mock-System für Dependencies
- Performance Benchmarks
- Load Test Suite
"""

from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import time
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test Ergebnis"""
    name: str
    passed: bool
    duration: float
    error: Optional[str] = None
    assertions: int = 0
    passed_assertions: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceBenchmark:
    """Performance Benchmark"""
    agent_name: str
    operation: str
    avg_duration: float
    min_duration: float
    max_duration: float
    p95_duration: float
    p99_duration: float
    requests_per_second: float
    error_rate: float
    sample_size: int


class AgentTestFramework:
    """
    Agent Test Framework
    
    Framework für Agent-Tests.
    """
    
    def __init__(self):
        """Initialisiert Test Framework"""
        self.test_results: List[TestResult] = []
        self.mocks: Dict[str, Any] = {}
    
    def mock(self, name: str, return_value: Any = None, side_effect: Optional[Callable] = None):
        """
        Erstellt Mock
        
        Args:
            name: Mock Name
            return_value: Return Value
            side_effect: Side Effect Function
        """
        self.mocks[name] = {
            "return_value": return_value,
            "side_effect": side_effect
        }
    
    def get_mock(self, name: str) -> Any:
        """Holt Mock"""
        if name in self.mocks:
            mock = self.mocks[name]
            if mock["side_effect"]:
                return mock["side_effect"]()
            return mock["return_value"]
        return None
    
    def assert_equal(self, actual: Any, expected: Any, message: str = ""):
        """Assert Equal"""
        if actual != expected:
            raise AssertionError(f"Expected {expected}, got {actual}. {message}")
    
    def assert_true(self, condition: bool, message: str = ""):
        """Assert True"""
        if not condition:
            raise AssertionError(f"Expected True, got False. {message}")
    
    def assert_false(self, condition: bool, message: str = ""):
        """Assert False"""
        if condition:
            raise AssertionError(f"Expected False, got True. {message}")
    
    def assert_not_none(self, value: Any, message: str = ""):
        """Assert Not None"""
        if value is None:
            raise AssertionError(f"Expected not None, got None. {message}")
    
    async def run_test(
        self,
        name: str,
        test_func: Callable,
        timeout: float = 30.0
    ) -> TestResult:
        """
        Führt Test aus
        
        Args:
            name: Test Name
            test_func: Test Function
            timeout: Timeout in Sekunden
        
        Returns:
            TestResult
        """
        start_time = time.time()
        assertions = 0
        passed_assertions = 0
        error = None
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                await asyncio.wait_for(test_func(self), timeout=timeout)
            else:
                test_func(self)
            
            passed = True
        except AssertionError as e:
            error = str(e)
            passed = False
        except Exception as e:
            error = str(e)
            passed = False
        finally:
            duration = time.time() - start_time
        
        result = TestResult(
            name=name,
            passed=passed,
            duration=duration,
            error=error,
            assertions=assertions,
            passed_assertions=passed_assertions
        )
        
        self.test_results.append(result)
        return result
    
    async def run_performance_test(
        self,
        agent_name: str,
        operation: str,
        test_func: Callable,
        iterations: int = 100,
        concurrency: int = 10
    ) -> PerformanceBenchmark:
        """
        Führt Performance Test aus
        
        Args:
            agent_name: Agent Name
            operation: Operation Name
            test_func: Test Function
            iterations: Anzahl Iterationen
            concurrency: Parallelität
        
        Returns:
            PerformanceBenchmark
        """
        durations = []
        errors = 0
        
        async def run_iteration():
            try:
                start = time.time()
                if asyncio.iscoroutinefunction(test_func):
                    await test_func(self)
                else:
                    test_func(self)
                duration = time.time() - start
                durations.append(duration)
            except Exception as e:
                errors += 1
                logger.error(f"Performance Test Fehler: {e}")
        
        # Führe Tests parallel aus
        start_time = time.time()
        tasks = []
        for _ in range(iterations):
            tasks.append(run_iteration())
            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks)
                tasks = []
        if tasks:
            await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        if not durations:
            return PerformanceBenchmark(
                agent_name=agent_name,
                operation=operation,
                avg_duration=0.0,
                min_duration=0.0,
                max_duration=0.0,
                p95_duration=0.0,
                p99_duration=0.0,
                requests_per_second=0.0,
                error_rate=1.0,
                sample_size=iterations
            )
        
        durations.sort()
        avg = sum(durations) / len(durations)
        min_dur = min(durations)
        max_dur = max(durations)
        p95_idx = int(len(durations) * 0.95)
        p99_idx = int(len(durations) * 0.99)
        p95 = durations[p95_idx] if p95_idx < len(durations) else durations[-1]
        p99 = durations[p99_idx] if p99_idx < len(durations) else durations[-1]
        
        rps = iterations / total_time if total_time > 0 else 0.0
        error_rate = errors / iterations
        
        return PerformanceBenchmark(
            agent_name=agent_name,
            operation=operation,
            avg_duration=avg,
            min_duration=min_dur,
            max_duration=max_dur,
            p95_duration=p95,
            p99_duration=p99,
            requests_per_second=rps,
            error_rate=error_rate,
            sample_size=iterations
        )
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Holt Test Summary"""
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r.passed)
        failed = total - passed
        total_duration = sum(r.duration for r in self.test_results)
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0.0,
            "total_duration": total_duration,
            "avg_duration": total_duration / total if total > 0 else 0.0
        }


# Globale Test Framework-Instanz
_global_test_framework: Optional[AgentTestFramework] = None


def get_test_framework() -> AgentTestFramework:
    """Holt globale Test Framework-Instanz"""
    global _global_test_framework
    if _global_test_framework is None:
        _global_test_framework = AgentTestFramework()
    return _global_test_framework
