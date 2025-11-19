#!/usr/bin/env python3
"""
Unit tests for HDHomeRun Channel Scanner
Tests all critical functions and edge cases identified in the audit
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
import re

# Mock openai module if not available
sys.modules['openai'] = MagicMock()
sys.modules['openai.error'] = MagicMock()

# Import the main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main


class TestParseLock(unittest.TestCase):
    """Test parse_lock function with various signal strengths including negative values."""

    def test_positive_signal_strength(self):
        """Test parsing lock with positive signal strength."""
        line = "LOCK: 8vsb (ss=87 snq=100 seq=100)"
        result = main.parse_lock(line)

        self.assertEqual(result['Lock'], '8vsb')
        self.assertEqual(result['Signal Strength (dBmV)'], '87')
        self.assertEqual(result['Signal to Noise Quality'], '100')
        self.assertEqual(result['Symbol Error Quality'], '100')

    def test_negative_signal_strength(self):
        """Test parsing lock with negative signal strength (critical bug fix)."""
        line = "LOCK: none (ss=-20 snq=42 seq=100)"
        result = main.parse_lock(line)

        self.assertEqual(result['Lock'], 'none')
        self.assertEqual(result['Signal Strength (dBmV)'], '-20')
        self.assertEqual(result['Signal to Noise Quality'], '42')
        self.assertEqual(result['Symbol Error Quality'], '100')

    def test_zero_signal_strength(self):
        """Test parsing lock with zero signal strength."""
        line = "LOCK: none (ss=0 snq=0 seq=0)"
        result = main.parse_lock(line)

        self.assertEqual(result['Lock'], 'none')
        self.assertEqual(result['Signal Strength (dBmV)'], '0')
        self.assertEqual(result['Signal to Noise Quality'], '0')
        self.assertEqual(result['Symbol Error Quality'], '0')

    def test_invalid_format(self):
        """Test parsing with invalid format returns empty dict."""
        line = "INVALID LINE FORMAT"
        result = main.parse_lock(line)
        self.assertEqual(result, {})

    def test_partial_data(self):
        """Test parsing with partial lock data."""
        line = "LOCK: 8vsb"
        result = main.parse_lock(line)
        self.assertEqual(result, {})


class TestParseFrequency(unittest.TestCase):
    """Test parse_frequency function."""

    def test_valid_frequency(self):
        """Test parsing valid frequency line."""
        line = "SCANNING: 569000000 (us-bcast:23)"
        result = main.parse_frequency(line)

        self.assertEqual(result['Frequency'], '569000000')
        self.assertEqual(result['US-Bcast Channel'], '23')

    def test_invalid_frequency(self):
        """Test parsing invalid frequency line."""
        line = "INVALID"
        result = main.parse_frequency(line)
        self.assertEqual(result, {})


class TestParseTsid(unittest.TestCase):
    """Test parse_tsid function."""

    def test_valid_tsid(self):
        """Test parsing valid TSID."""
        line = "TSID: 0x0123"
        result = main.parse_tsid(line)
        self.assertEqual(result['TSID'], '0x0123')

    def test_decimal_tsid(self):
        """Test parsing decimal TSID."""
        line = "TSID: 12345"
        result = main.parse_tsid(line)
        self.assertEqual(result['TSID'], '12345')

    def test_invalid_tsid(self):
        """Test parsing invalid TSID."""
        line = "TSID:"
        result = main.parse_tsid(line)
        self.assertEqual(result, {})


class TestParseProgram(unittest.TestCase):
    """Test parse_program function."""

    def test_valid_program(self):
        """Test parsing valid program."""
        line = "PROGRAM 1: NBC4-LA"
        result = main.parse_program(line)
        self.assertEqual(result['Program1'], 'NBC4-LA')

    def test_program_with_spaces(self):
        """Test parsing program with spaces in name."""
        line = "PROGRAM 5: Example Program Name"
        result = main.parse_program(line)
        self.assertEqual(result['Program5'], 'Example Program Name')

    def test_invalid_program(self):
        """Test parsing invalid program."""
        line = "PROGRAM"
        result = main.parse_program(line)
        self.assertEqual(result, {})


class TestExtractPrograms(unittest.TestCase):
    """Test extract_programs function."""

    def test_extract_multiple_programs(self):
        """Test extracting multiple programs from scan data."""
        data = [
            'SCANNING: 605000000 (us-bcast:36)',
            'LOCK: 8vsb (ss=100 snq=100 seq=100)',
            'TSID: 0x0123',
            'PROGRAM 3: 4.1 NBC4-LA',
            'PROGRAM 4: 4.2 COZI-TV',
            'PROGRAM 5: 4.3 NBCLX'
        ]
        result = main.extract_programs(data)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], '4.1 NBC4-LA')
        self.assertEqual(result[1], '4.2 COZI-TV')
        self.assertEqual(result[2], '4.3 NBCLX')

    def test_extract_no_programs(self):
        """Test extracting when no programs are present."""
        data = [
            'SCANNING: 695000000 (us-bcast:51)',
            'LOCK: none (ss=24 snq=0 seq=0)'
        ]
        result = main.extract_programs(data)
        self.assertEqual(result, [])


class TestParseResultsInfo(unittest.TestCase):
    """Test parse_results_info function with comprehensive scan data."""

    def test_parse_complete_scan(self):
        """Test parsing complete scan with multiple frequencies."""
        scan_results = [
            'SCANNING: 605000000 (us-bcast:36)',
            'LOCK: 8vsb (ss=100 snq=100 seq=100)',
            'TSID: 0x0123',
            'PROGRAM 3: 4.1 NBC4-LA',
            'PROGRAM 4: 4.2 COZI-TV',
            'SCANNING: 695000000 (us-bcast:51)',
            'LOCK: none (ss=-20 snq=0 seq=0)'
        ]

        result = main.parse_results_info(scan_results)

        self.assertEqual(len(result), 2)

        # First frequency with lock
        self.assertEqual(result[0]['Frequency'], '605000000')
        self.assertEqual(result[0]['US-Bcast Channel'], '36')
        self.assertEqual(result[0]['Lock'], '8vsb')
        self.assertEqual(result[0]['TSID'], '0x0123')
        self.assertEqual(result[0]['Program3'], '4.1 NBC4-LA')

        # Second frequency without lock (negative signal)
        self.assertEqual(result[1]['Frequency'], '695000000')
        self.assertEqual(result[1]['Lock'], 'none')
        self.assertEqual(result[1]['Signal Strength (dBmV)'], '-20')


class TestValidateSignalQuality(unittest.TestCase):
    """Test validate_signal_quality function."""

    def test_valid_quality_values(self):
        """Test validation with valid quality values."""
        self.assertTrue(main.validate_signal_quality(0, "SNQ"))
        self.assertTrue(main.validate_signal_quality(50, "SNQ"))
        self.assertTrue(main.validate_signal_quality(100, "SEQ"))

    def test_invalid_quality_values(self):
        """Test validation with invalid quality values."""
        self.assertFalse(main.validate_signal_quality(-1, "SNQ"))
        self.assertFalse(main.validate_signal_quality(101, "SEQ"))
        self.assertFalse(main.validate_signal_quality(255, "SNQ"))


class TestCheckFileWritable(unittest.TestCase):
    """Test check_file_writable function."""

    def test_writable_current_directory(self):
        """Test that current directory is writable."""
        result = main.check_file_writable("test_output.csv")
        self.assertTrue(result)

    @patch('os.access')
    @patch('os.path.exists')
    def test_non_writable_directory(self, mock_exists, mock_access):
        """Test non-writable directory detection."""
        mock_exists.return_value = True
        mock_access.return_value = False

        result = main.check_file_writable("/readonly/test.csv")
        self.assertFalse(result)


class TestPrepareOpenAIPrompt(unittest.TestCase):
    """Test prepare_openai_prompt function."""

    def test_prompt_creation(self):
        """Test OpenAI prompt preparation."""
        stations = "NBC4-LA KTLA-DT KCBS-HD"
        result = main.prepare_openai_prompt(stations)

        self.assertIn("city or region", result.lower())
        self.assertIn(stations, result)


class TestGetUSBcast(unittest.TestCase):
    """Test get_us_bcast function."""

    def test_extract_channel_number(self):
        """Test extracting US broadcast channel number."""
        line = "SCANNING: 569000000 (us-bcast:23)"
        result = main.get_us_bcast(line)
        self.assertEqual(result, '23')

    def test_no_channel_number(self):
        """Test when no channel number is present."""
        line = "SCANNING: 569000000"
        result = main.get_us_bcast(line)
        self.assertEqual(result, '')


class TestUpdateLockInfo(unittest.TestCase):
    """Test update_lock_info function."""

    def test_update_existing_dict(self):
        """Test updating existing lock info dictionary."""
        lock_info = {'Lock': 'Locked', 'Signal Strength (dBmV)': '10'}
        new_data = {'Signal to Noise Quality': '25', 'Symbol Error Quality': '0'}

        main.update_lock_info(lock_info, new_data)

        self.assertEqual(len(lock_info), 4)
        self.assertEqual(lock_info['Signal to Noise Quality'], '25')
        self.assertEqual(lock_info['Lock'], 'Locked')


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_empty_scan_results(self):
        """Test parsing empty scan results."""
        result = main.parse_results_info([])
        self.assertEqual(result, [])

    def test_malformed_data(self):
        """Test parsing with malformed data."""
        malformed = [
            'RANDOM DATA',
            '12345',
            'LOCK:',
            'PROGRAM: : :'
        ]
        result = main.parse_results_info(malformed)
        # Should not crash, returns empty or partial data
        self.assertIsInstance(result, list)

    def test_negative_signal_edge_case(self):
        """Test very negative signal strength."""
        line = "LOCK: none (ss=-100 snq=0 seq=0)"
        result = main.parse_lock(line)
        self.assertEqual(result['Signal Strength (dBmV)'], '-100')


def run_tests():
    """Run all tests and generate report."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestParseLock))
    suite.addTests(loader.loadTestsFromTestCase(TestParseFrequency))
    suite.addTests(loader.loadTestsFromTestCase(TestParseTsid))
    suite.addTests(loader.loadTestsFromTestCase(TestParseProgram))
    suite.addTests(loader.loadTestsFromTestCase(TestExtractPrograms))
    suite.addTests(loader.loadTestsFromTestCase(TestParseResultsInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestValidateSignalQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestCheckFileWritable))
    suite.addTests(loader.loadTestsFromTestCase(TestPrepareOpenAIPrompt))
    suite.addTests(loader.loadTestsFromTestCase(TestGetUSBcast))
    suite.addTests(loader.loadTestsFromTestCase(TestUpdateLockInfo))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
