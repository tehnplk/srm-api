"""
Database Logging Module
Logs all SQL commands to db_log.txt with timestamp format
"""

import traceback
from datetime import datetime


def log_sql(sql_command: str):
    """
    Log SQL command to db_log.txt with timestamp
    
    Args:
        sql_command: The SQL command to log
    """
    try:
        timestamp = datetime.now().strftime("(%Y-%m-%d %H:%M:%S)")
        log_entry = f"{timestamp} {sql_command}\n"
        
        log_file = "db_log.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to log SQL: {e}")


def log_sql_with_params(sql_command: str, params: tuple = None):
    """
    Log SQL command with parameters to db_log.txt with timestamp
    
    Args:
        sql_command: The SQL command to log
        params: Optional parameters tuple for the SQL command
    """
    try:
        timestamp = datetime.now().strftime("(%Y-%m-%d %H:%M:%S)")
        
        if params:
            # Clean parameters for logging (truncate long strings, mask sensitive data)
            cleaned_params = []
            for param in params:
                if param is None:
                    cleaned_params.append("NULL")
                elif isinstance(param, str) and len(param) > 100:
                    cleaned_params.append(f"'{param[:50]}...{param[-20:]}'")
                elif isinstance(param, str):
                    cleaned_params.append(f"'{param}'")
                else:
                    cleaned_params.append(str(param))
            
            log_entry = f"{timestamp} {sql_command} | Params: {tuple(cleaned_params)}\n"
        else:
            log_entry = f"{timestamp} {sql_command}\n"
        
        log_file = "db_log.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to log SQL with params: {e}")


def log_operation(operation: str, details: str = ""):
    """
    Log database operation with timestamp
    
    Args:
        operation: Description of the operation
        details: Additional details about the operation
    """
    try:
        timestamp = datetime.now().strftime("(%Y-%m-%d %H:%M:%S)")
        
        if details:
            log_entry = f"{timestamp} [OPERATION] {operation}: {details}\n"
        else:
            log_entry = f"{timestamp} [OPERATION] {operation}\n"
        
        log_file = "db_log.txt"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to log operation: {e}")
