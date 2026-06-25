import logging
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from source.setup_logger import StreamToLogger, setup_logger


def test_stream_to_logger():
    mock_logger = MagicMock()
    level = logging.INFO
    stream = StreamToLogger(mock_logger, level)
    
    # Test writing multiple lines
    stream.write("Test line 1\nTest line 2\n")
    
    assert mock_logger.log.call_count == 2
    mock_logger.log.assert_any_call(level, "Test line 1")
    mock_logger.log.assert_any_call(level, "Test line 2")
    
    # Test flush
    stream.flush()


@patch('logging.handlers.RotatingFileHandler')
@patch('logging.StreamHandler')
@patch('logging.getLogger')
@patch('source.setup_logger.sys')
def test_setup_logger_console(mock_sys, mock_get_logger, mock_stream_handler, mock_rotating):
    ad = MagicMock()
    ad.args.logging_level = 'DEBUG'
    ad.args.logging_directory = 'logs'
    ad.args.logging_file_name = 'app.log'
    
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    
    # Simulate being in a terminal
    mock_sys.stdin.isatty.return_value = True
    
    setup_logger(ad)
    
    # Check level setting
    mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
    
    # Check that handlers were added
    assert mock_logger.addHandler.call_count >= 2
    
    # Verify RotatingFileHandler was called
    mock_rotating.assert_called_once()
    args, kwargs = mock_rotating.call_args
    assert 'app.log' in args[0]


@patch('logging.handlers.RotatingFileHandler')
@patch('logging.StreamHandler')
@patch('logging.getLogger')
@patch('source.setup_logger.sys')
@patch('source.setup_logger.StreamToLogger')
def test_setup_logger_no_console(mock_stream_to_logger, mock_sys, mock_get_logger, mock_stream_handler, mock_rotating):
    ad = MagicMock()
    ad.args.logging_level = 'INFO'
    ad.args.logging_directory = 'logs'
    ad.args.logging_file_name = 'app.log'
    
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    
    # Simulate NOT being in a terminal
    mock_sys.stdin.isatty.return_value = False
    
    setup_logger(ad)
    
    # Verify redirection of stdout and stderr
    assert mock_sys.stdout == mock_stream_to_logger.return_value
    assert mock_sys.stderr == mock_stream_to_logger.return_value
    assert mock_stream_to_logger.call_count == 2


@pytest.mark.parametrize("level_str, expected_level", [
    ('DEBUG', logging.DEBUG),
    ('INFO', logging.INFO),
    ('WARNING', logging.WARNING),
    ('ERROR', logging.ERROR),
    ('CRITICAL', logging.CRITICAL),
    ('INVALID', logging.WARNING),
])
def test_setup_logger_levels(level_str, expected_level):
    with patch('logging.handlers.RotatingFileHandler'):
        with patch('logging.StreamHandler'):
            with patch('logging.getLogger') as mock_get_logger:
                with patch('source.setup_logger.sys') as mock_sys:
                    mock_sys.stdin.isatty.return_value = True
                    ad = MagicMock()
                    ad.args.logging_level = level_str
                    ad.args.logging_directory = 'logs'
                    ad.args.logging_file_name = 'app.log'
                    
                    mock_logger = MagicMock()
                    mock_get_logger.return_value = mock_logger
                    
                    setup_logger(ad)
                    mock_logger.setLevel.assert_called_once_with(expected_level)
