# Weather MCP Server

A Model Context Protocol (MCP) server that provides weather forecasts and alerts using the National Weather Service API.

*Built following the official [Model Context Protocol server development guide](https://modelcontextprotocol.io/docs/develop/build-server)*

## Quick Start (Mac/Linux)

### 1. Clone and Setup

```bash
# Clone the repository to your preferred location
git clone <repository-url> ~/weather-mcp
cd ~/weather-mcp

# Check the project structure
ls -la
# You should see: main.py, weather.py, pyproject.toml, README.md, etc.
```

### 2. Configure MCP Client

Add this configuration to your MCP client (e.g., Gemini CLI, Claude Desktop, etc.):

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "~/weather-mcp",
        "run",
        "weather.py"
      ]
    }
  }
}
```

**Important**: Replace `~/weather-mcp` with the actual path where you cloned the repository. For example:
- If you cloned to your home directory: `"/home/yourusername/weather-mcp"`
- If you cloned to a projects folder: `"/home/yourusername/projects/weather-mcp"`

### 3. Monitor Server Activity

The server logs all activity to help you understand what's happening:

```bash
# Navigate to your cloned repository
cd ~/weather-mcp

# Watch server logs in real-time
tail -f weather_mcp.log
```

Keep this terminal open while using the MCP server to see real-time logs of weather requests, API calls, and any errors.

## How It Works

This MCP server acts as a bridge between your AI client and the National Weather Service API:

1. **Your AI client** sends requests to the MCP server via stdio
2. **The MCP server** processes requests and makes API calls to weather.gov
3. **Weather data** is returned to your AI client in a structured format
4. **All activity** is logged to `weather_mcp.log` for debugging and monitoring

## Features

- **Weather Forecasts**: Get detailed weather forecasts for any location using latitude/longitude coordinates
- **Weather Alerts**: Retrieve active weather alerts for any US state
- **Server Information**: Get details about the server configuration and capabilities
- **Comprehensive Logging**: Built-in logging to both console and file with progress reporting

## Development Setup

### Prerequisites

- Python 3.11+ installed
- `uv` package manager ([install uv](https://docs.astral.sh/uv/getting-started/installation/))

### Local Development

```bash
# 1. Clone the repository (if not already done)
git clone <repository-url> ~/weather-mcp-dev
cd ~/weather-mcp-dev

# 2. Install dependencies
uv sync

# 3. Test the server locally
uv run python weather.py

# 4. In another terminal, monitor logs
tail -f weather_mcp.log
```

### Making Changes

1. **Edit the code**: Modify `weather.py` or other files as needed
2. **Test your changes**: Run `uv run python weather.py` to test locally
3. **Check logs**: Monitor `weather_mcp.log` for any issues
4. **Update your MCP client**: Restart your MCP client to pick up changes

### Project Structure

```
weather-mcp/
├── weather.py          # Main MCP server implementation
├── main.py            # Alternative entry point
├── pyproject.toml     # Project configuration and dependencies
├── weather_mcp.log    # Server logs (created when running)
├── LOGGING.md         # Detailed logging documentation
└── README.md          # This file
```

### Testing Tools

Once the server is running in your MCP client, you can test these tools:

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

## Configuration Details

The server uses the National Weather Service API with these settings:

- **User-Agent**: `weather-app/1.0`
- **Base URL**: `https://api.weather.gov`
- **Timeout**: 30 seconds
- **Authentication**: None required (public API)

## Troubleshooting

### Common Issues

1. **Server won't start**: Check that `uv` is installed and the path in your MCP config is correct
2. **No weather data**: Ensure you have internet connectivity and the weather.gov API is accessible
3. **MCP client can't connect**: Verify the stdio connection and server logs

### Debugging Steps

```bash
# Check if uv is installed
uv --version

# Test the server directly
cd ~/weather-mcp
uv run python weather.py

# Check recent logs
tail -20 weather_mcp.log

# Test with verbose logging
export MCP_LOG_LEVEL=debug
uv run python weather.py
```

## Requirements

- Python 3.11+
- httpx>=0.28.1
- mcp[cli]>=1.13.1

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test locally
4. Check logs for any issues: `tail -f weather_mcp.log`
5. Commit and push: `git commit -m "Description" && git push`
6. Submit a pull request

## API Reference

This server uses the National Weather Service API:
- **Base URL**: https://api.weather.gov
- **Documentation**: https://www.weather.gov/documentation/services-web-api
- **Rate Limits**: None specified, but please be respectful
- **Authentication**: None required