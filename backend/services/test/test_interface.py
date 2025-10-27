"""
Interface for Test Service following Interface Segregation Principle (ISP).

This interface defines the contract that all test service implementations
must follow, supporting test suite CRUD operations and execution history.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .models import (
    TestSuiteData,
    TestSuiteSummary,
    TestSuiteExecutionResult
)


class ITestService(ABC):
    """
    Abstract base class defining the interface for test service operations.
    
    This interface supports:
    - CRUD operations for test suites
    - Test suite discovery
    - Execution history retrieval
    - User-scoped operations
    """
    
    @abstractmethod
    async def list_test_suites(
        self, 
        user_id: str, 
        repo_name: str
    ) -> List[TestSuiteSummary]:
        """
        List all test suites in repository.
        
        Args:
            user_id: ID of the user requesting test suites
            repo_name: Repository name
            
        Returns:
            List of TestSuiteSummary objects
            
        Raises:
            NotFoundException: If repository doesn't exist
        """
        pass
    
    @abstractmethod
    async def get_test_suite(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str
    ) -> TestSuiteData:
        """
        Get specific test suite definition.
        
        Args:
            user_id: ID of the user requesting the test suite
            repo_name: Repository name
            suite_name: Test suite name
            
        Returns:
            TestSuiteData object with complete suite definition
            
        Raises:
            NotFoundException: If suite doesn't exist
        """
        pass
    
    @abstractmethod
    async def save_test_suite(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_data: TestSuiteData
    ) -> TestSuiteData:
        """
        Create or update test suite.
        
        Args:
            user_id: ID of the user saving the suite
            repo_name: Repository name
            suite_data: Test suite data to save
            
        Returns:
            Saved TestSuiteData
            
        Raises:
            NotFoundException: If repository doesn't exist
            AppException: If save operation fails
        """
        pass
    
    @abstractmethod
    async def delete_test_suite(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str
    ) -> bool:
        """
        Delete test suite.
        
        Args:
            user_id: ID of the user deleting the suite
            repo_name: Repository name
            suite_name: Test suite name
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            NotFoundException: If suite doesn't exist
        """
        pass
    
    @abstractmethod
    async def get_latest_execution(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str
    ) -> Optional[TestSuiteExecutionResult]:
        """
        Get latest execution result for a test suite.
        
        Args:
            user_id: ID of the user requesting execution
            repo_name: Repository name
            suite_name: Test suite name
            
        Returns:
            Latest TestSuiteExecutionResult or None if no executions exist
        """
        pass
    
    @abstractmethod
    async def list_executions(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str, 
        limit: int = 10
    ) -> List[TestSuiteExecutionResult]:
        """
        List execution history for a test suite.
        
        Args:
            user_id: ID of the user requesting history
            repo_name: Repository name
            suite_name: Test suite name
            limit: Maximum number of executions to return
            
        Returns:
            List of TestSuiteExecutionResult ordered by execution time (newest first)
        """
        pass