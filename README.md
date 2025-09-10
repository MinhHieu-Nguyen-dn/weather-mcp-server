# Weather MCP Server

A Model Context Protocol (MCP) server that provides weather forecasts and alerts using the National Weather Service API.

## Features

- **Weather Forecasts**: Get detailed weather forecasts for any location using latitude/longitude coordinates
- **Weather Alerts**: Retrieve active weather alerts for any US state
- **Server Information**: Get details about the server configuration and capabilities
- **Comprehensive Logging**: Built-in logging to both console and file with progress reporting

## Installation

### Using uv (recommended)

```bash
uv add weather-mcp-server
```

### Using pip

```bash
pip install weather-mcp-server
```

## Usage

### As an MCP Server

Run the server in stdio mode (typical for MCP clients):

```bash
weather-mcp-server
```

Or run directly with Python:

```bash
python weather.py
```

### Available Tools

#### `get_forecast(latitude: float, longitude: float)`
Get a detailed weather forecast for a specific location.

**Example:**
```
get_forecast(40.7128, -74.0060)  # New York City
```

#### `get_alerts(state: str)`
Get active weather alerts for a US state (2-letter state code).

**Example:**
```
get_alerts("CA")  # California alerts
```

#### `server_info()`
Get information about the server configuration and capabilities.

## Configuration

The server uses the National Weather Service API and requires no API keys. It includes:

- User-Agent: `weather-app/1.0`
- Base URL: `https://api.weather.gov`
- Timeout: 30 seconds
- Follow redirects: Yes

## Logging

The server provides comprehensive logging:

- **File logging**: `weather_mcp.log`
- **Console logging**: Real-time output
- **MCP Context logging**: Debug, info, warning, and error messages
- **Progress reporting**: For long-running operations

See `LOGGING.md` for detailed logging information.

## Development

### Setup

```bash
git clone <repository-url>
cd weather-mcp-server
uv venv
uv pip install -e .
```

### Running

```bash
uv run python weather.py
```

## Requirements

- Python 3.11+
- httpx>=0.28.1
- mcp[cli]>=1.13.1

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## API Reference

This server uses the National Weather Service API:
- Base URL: https://api.weather.gov
- Documentation: https://www.weather.gov/documentation/services-web-api
- No authentication required