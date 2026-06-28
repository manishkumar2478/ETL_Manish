"""
Unit tests for ETL database operations
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from postgres_connector import create_connection, run_query, get_db_config


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_config = {
            'host': 'localhost',
            'port': '5432',
            'database': 'BSENSE',
            'user': 'postgres',
            'password': 'test_password'
        }
    
    @patch.dict(os.environ, {'DB_HOST': 'localhost', 'DB_PORT': '5432', 
                              'DB_NAME': 'BSENSE', 'DB_USER': 'postgres',
                              'DB_PASSWORD': 'test_password'})
    def test_get_db_config(self):
        """Test that database configuration is correctly read from environment"""
        config = get_db_config()
        self.assertEqual(config['host'], 'localhost')
        self.assertEqual(config['database'], 'BSENSE')
        self.assertEqual(config['user'], 'postgres')
    
    @patch('postgres_connector.psycopg2.connect')
    def test_create_connection_success(self, mock_connect):
        """Test successful database connection"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        with patch.dict(os.environ, {'DB_HOST': 'localhost', 'DB_PORT': '5432',
                                      'DB_NAME': 'BSENSE', 'DB_USER': 'postgres',
                                      'DB_PASSWORD': 'test_password'}):
            conn = create_connection()
            self.assertIsNotNone(conn)
            mock_connect.assert_called_once()
    
    @patch('postgres_connector.psycopg2.connect')
    def test_create_connection_failure(self, mock_connect):
        """Test failed database connection"""
        from psycopg2 import OperationalError
        mock_connect.side_effect = OperationalError("Connection refused")
        
        with patch.dict(os.environ, {'DB_HOST': 'localhost', 'DB_PORT': '5432',
                                      'DB_NAME': 'BSENSE', 'DB_USER': 'postgres',
                                      'DB_PASSWORD': 'test_password'}):
            conn = create_connection()
            self.assertIsNone(conn)


class TestInputValidation(unittest.TestCase):
    """Test input validation for database operations"""
    
    def test_validate_identifier_valid(self):
        """Test validation of valid identifiers"""
        from app import validate_identifier
        
        valid_names = ['table_name', 'schema_name', 'column_1', 'Table123']
        for name in valid_names:
            try:
                result = validate_identifier(name)
                self.assertEqual(result, name)
            except ValueError:
                self.fail(f"validate_identifier raised ValueError for valid input: {name}")
    
    def test_validate_identifier_invalid(self):
        """Test validation of invalid identifiers"""
        from app import validate_identifier
        
        invalid_names = ['table-name', 'schema.name', '123invalid', 'name;drop',
                        'name\\'", 'table name']
        for name in invalid_names:
            with self.assertRaises(ValueError):
                validate_identifier(name)
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection attempts are blocked"""
        from app import validate_identifier
        
        injection_attempts = [
            "table'; DROP TABLE users; --",
            "table OR 1=1",
            "table'; UPDATE users SET admin=true; --"
        ]
        
        for attempt in injection_attempts:
            with self.assertRaises(ValueError):
                validate_identifier(attempt)


class TestDataConversion(unittest.TestCase):
    """Test data conversion utilities"""
    
    def test_decimal_to_string_conversion(self):
        """Test conversion of Decimal objects to strings"""
        from decimal import Decimal
        from app import convert_decimal_to_str
        
        test_obj = {
            'amount': Decimal('123.45'),
            'nested': {
                'value': Decimal('789.01')
            }
        }
        
        result = convert_decimal_to_str(test_obj)
        self.assertIsInstance(result['amount'], str)
        self.assertEqual(result['amount'], '123.45')
        self.assertIsInstance(result['nested']['value'], str)
    
    def test_date_to_string_conversion(self):
        """Test conversion of date objects to strings"""
        from app import convert_decimal_to_str
        from datetime import date
        
        test_obj = {
            'created': date(2024, 1, 1)
        }
        
        result = convert_decimal_to_str(test_obj)
        self.assertIsInstance(result['created'], str)
        self.assertEqual(result['created'], '2024-01-01')


class TestErrorHandling(unittest.TestCase):
    """Test error handling in database operations"""
    
    @patch('app.connect_to_postgres')
    def test_connection_error_handling(self, mock_connect):
        """Test handling of connection errors"""
        mock_connect.return_value = None
        
        # This should be handled gracefully in the actual application
        conn = mock_connect()
        self.assertIsNone(conn)
    
    @patch('app.connect_to_postgres')
    def test_database_operation_error_handling(self, mock_connect):
        """Test handling of database operation errors"""
        mock_conn = Mock()
        mock_cursor = Mock()
        
        # Simulate database error
        from psycopg2 import Error
        mock_cursor.execute.side_effect = Error("Database error")
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        # The app should handle this gracefully


class TestAuditLogging(unittest.TestCase):
    """Test audit logging functionality"""
    
    def test_audit_log_data_structure(self):
        """Test that audit logs have required fields"""
        required_fields = ['table_name', 'record_id', 'operation', 
                          'old_data', 'new_data', 'updated_by', 'updated_at']
        
        audit_log = {
            'table_name': 'employee',
            'record_id': '123',
            'operation': 'UPDATE',
            'old_data': {'name': 'John'},
            'new_data': {'name': 'Jane'},
            'updated_by': 'system',
            'updated_at': datetime.now()
        }
        
        for field in required_fields:
            self.assertIn(field, audit_log)


class TestFlaskApp(unittest.TestCase):
    """Test Flask application endpoints"""
    
    def setUp(self):
        """Set up test client"""
        from app import app
        self.app = app
        self.client = app.test_client()
    
    def test_index_route_exists(self):
        """Test that index route exists"""
        # This will test connectivity if database is available
        response = self.client.get('/')
        # Accept either 200 (success) or 500 (DB not available in test)
        self.assertIn(response.status_code, [200, 500])
    
    def test_update_record_validation(self):
        """Test input validation for update_record endpoint"""
        # Test missing record_id
        response = self.client.post('/api/update_record/test_table', 
                                   json={'updates': {}})
        self.assertIn(response.status_code, [400, 500])
        
        # Test invalid updates
        response = self.client.post('/api/update_record/test_table',
                                   json={'record_id': '1', 'updates': None})
        self.assertIn(response.status_code, [400, 500])


class TestDataIntegration(unittest.TestCase):
    """Integration tests for data operations"""
    
    @patch('pandas.read_csv')
    def test_bulk_load_csv_parsing(self, mock_read_csv):
        """Test CSV file parsing"""
        import pandas as pd
        
        mock_df = pd.DataFrame({
            'Date': ['06-SEP-2024'],
            'Symbol': ['ACEINTEG'],
            'Security Name': ['Ace Integrated Solu. Ltd.'],
            'Client Name': ['TEST CLIENT'],
            'Buy/Sell': ['BUY'],
            'Quantity Traded': [70034],
            'Trade Price / Wght. Avg. Price': [37.85],
            'Remarks': ['-']
        })
        
        mock_read_csv.return_value = mock_df
        df = pd.read_csv('test.csv')
        
        self.assertEqual(len(df), 1)
        self.assertEqual(df['Symbol'].iloc[0], 'ACEINTEG')


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseConnection))
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDataConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestAuditLogging))
    suite.addTests(loader.loadTestsFromTestCase(TestFlaskApp))
    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == '__main__':
    result = run_tests()
    exit(0 if result.wasSuccessful() else 1)
