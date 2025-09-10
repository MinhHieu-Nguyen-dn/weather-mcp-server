# Weather MCP Server - Logging Implementation

## Overview

This document describes the comprehensive logging implementation added to the Weather MCP Server based on Model Context Protocol (MCP) best practices and the Python SDK documentation.

## Logging Features

### 1. Standard Python Logging

**Configuration:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),        # Console output
        logging.FileHandler('weather_mcp.log')  # File output
    ]
)
```

**Benefits:**
- Dual output: console and file (`weather_mcp.log`)
- Timestamped entries with logger name and level
- Standard Python logging practices
- Persistent log history in file

### 2. MCP Context Logging

**Implementation:**
- `ctx.debug()` - Detailed debugging information
- `ctx.info()` - General information messages  
- `ctx.warning()` - Warning conditions
- `ctx.error()` - Error conditions

**Benefits:**
- Integrated with MCP protocol
- Visible to MCP clients
- Tool-specific logging context
- Real-time feedback to users

### 3. Progress Reporting

**Features:**
- `ctx.report_progress()` for long-running operations
- Real-time progress updates with messages
- User-friendly operation tracking

**Example:**
```python
await ctx.report_progress(
    progress=0.6,
    total=1.0,
    message="Fetching detailed forecast..."
)
```

### 4. Exception Handling

**Best Practices Implemented:**
- Specific exception catching (TimeoutException, HTTPStatusError, etc.)
- `logger.exception()` for automatic exception info capture
- Graceful error recovery with user-friendly messages
- Both MCP context and Python logging for errors

### 5. Input Validation Logging

**Features:**
- Coordinate range validation with warnings
- State code format validation
- Detailed error messages for invalid inputs

## Tools Enhanced with Logging

### `get_alerts(state: str)`
- Input validation logging
- Progress reporting for multiple alerts
- API request/response logging
- Alert processing status updates

### `get_forecast(latitude: float, longitude: float)`
- Coordinate validation
- Two-step process logging (points API → forecast API)
- Progress reporting through forecast steps
- Detailed error handling for each API call

### `server_info()`
- New diagnostic tool
- Returns logging configuration and server status
- Useful for troubleshooting and monitoring

## Log Levels Used

- **DEBUG**: API requests/responses, detailed processing steps
- **INFO**: Major operations, successful completions, server startup
- **WARNING**: Input validation issues, recoverable problems  
- **ERROR**: API failures, data processing errors, critical issues

## Monitoring and Troubleshooting

### Log File Location
- File: `weather_mcp.log` (in server directory)
- Format: Timestamped with logger name and level
- Rotates naturally (append mode)

### Real-time Monitoring
```bash
# Watch log file in real-time
tail -f weather_mcp.log

# Filter for errors only
grep ERROR weather_mcp.log
```

### Server Information
Use the `server_info` tool to get current configuration:
```json
{
  "server_name": "weather",
  "python_log_level": "INFO", 
  "log_file": "weather_mcp.log",
  "nws_api_base": "https://api.weather.gov",
  "available_tools": ["get_alerts", "get_forecast", "server_info"],
  "logging_features": [...]
}
```

## Best Practices Followed

1. **MCP SDK Guidelines:**
   - Use `logger.exception()` for exception logging
   - Catch specific exceptions when possible
   - General `Exception` only for top-level handlers
   - Context logging for user-facing messages

2. **Error Resilience:**
   - Graceful degradation on API failures
   - User-friendly error messages
   - Detailed technical logging for debugging

3. **Performance Monitoring:**
   - Progress reporting for long operations
   - API response time visibility through logs
   - Resource usage transparency

4. **Security:**
   - No sensitive data in logs
   - Appropriate log levels for different information
   - Structured error messages without data leakage

## Testing the Logging

1. **Start the server:**
   ```bash
   uv run weather.py
   ```

2. **Check server startup logs:**
   ```bash
   cat weather_mcp.log
   ```

3. **Test with invalid inputs to see validation logging**

4. **Use `server_info` tool to verify configuration**

This logging implementation provides comprehensive observability while following MCP best practices and ensuring robust error handling.
