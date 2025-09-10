from typing import Any
import logging
import httpx
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

# Configure Python logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('weather_mcp.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"


async def make_nws_request(url: str, ctx: Context[ServerSession, None] | None = None) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    
    if ctx:
        await ctx.debug(f"Making NWS API request to: {url}")
    logger.debug(f"Making request to NWS API: {url}")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            
            if ctx:
                await ctx.debug(f"NWS API request successful, status: {response.status_code}")
            logger.debug(f"NWS API request successful: {response.status_code}")
            
            return response.json()
            
        except httpx.TimeoutException:
            error_msg = f"Request timeout for URL: {url}"
            if ctx:
                await ctx.error(error_msg)
            logger.exception("Request timeout occurred")
            return None
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code} for URL: {url}"
            if ctx:
                await ctx.error(error_msg)
            logger.exception("HTTP status error occurred")
            return None
            
        except httpx.RequestError:
            error_msg = f"Network error for URL: {url}"
            if ctx:
                await ctx.error(error_msg)
            logger.exception("Network request error occurred")
            return None
            
        except Exception:
            error_msg = f"Unexpected error for URL: {url}"
            if ctx:
                await ctx.error(error_msg)
            logger.exception("Unexpected error during NWS API request")
            return None


async def format_alert(feature: dict, ctx: Context[ServerSession, None] | None = None) -> str:
    """Format an alert feature into a readable string."""
    try:
        props = feature["properties"]
        alert_event = props.get('event', 'Unknown')
        
        if ctx:
            await ctx.debug(f"Formatting alert for event: {alert_event}")
        logger.debug(f"Formatting alert for event: {alert_event}")
        
        formatted_alert = f"""
Event: {alert_event}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""
        return formatted_alert
        
    except KeyError as e:
        error_msg = f"Missing required field in alert data: {e}"
        if ctx:
            await ctx.warning(error_msg)
        logger.warning(error_msg)
        return "Error: Invalid alert data format"
        
    except Exception:
        error_msg = "Unexpected error while formatting alert"
        if ctx:
            await ctx.error(error_msg)
        logger.exception("Unexpected error while formatting alert")
        return "Error: Could not format alert"


@mcp.tool()
async def get_alerts(state: str, ctx: Context[ServerSession, None]) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    await ctx.info(f"Fetching weather alerts for state: {state}")
    logger.info(f"Processing alerts request for state: {state}")
    
    # Validate state code
    if len(state) != 2:
        error_msg = f"Invalid state code format: {state}. Expected 2-letter code."
        await ctx.warning(error_msg)
        logger.warning(error_msg)
        return "Error: State code must be exactly 2 letters (e.g., CA, NY)"
    
    state = state.upper()
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    
    await ctx.debug(f"Requesting alerts from URL: {url}")
    data = await make_nws_request(url, ctx)

    if not data:
        error_msg = f"Unable to fetch alerts for state: {state}"
        await ctx.error(error_msg)
        logger.error(error_msg)
        return "Unable to fetch alerts or no alerts found."

    if "features" not in data:
        error_msg = f"Invalid response format for state: {state}"
        await ctx.error(error_msg)
        logger.error(error_msg)
        return "Invalid response format from weather service."

    if not data["features"]:
        await ctx.info(f"No active alerts found for state: {state}")
        logger.info(f"No active alerts for state: {state}")
        return "No active alerts for this state."

    alert_count = len(data["features"])
    await ctx.info(f"Processing {alert_count} alerts for state: {state}")
    logger.info(f"Found {alert_count} alerts for state: {state}")
    
    # Process alerts with progress reporting
    alerts = []
    for i, feature in enumerate(data["features"]):
        progress = (i + 1) / alert_count
        await ctx.report_progress(
            progress=progress,
            total=1.0,
            message=f"Processing alert {i + 1}/{alert_count}"
        )
        
        formatted_alert = await format_alert(feature, ctx)
        alerts.append(formatted_alert)
    
    await ctx.info(f"Successfully processed {alert_count} alerts for state: {state}")
    logger.info(f"Successfully processed {alert_count} alerts for state: {state}")
    
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float, ctx: Context[ServerSession, None]) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    await ctx.info(f"Fetching weather forecast for coordinates: {latitude}, {longitude}")
    logger.info(f"Processing forecast request for coordinates: {latitude}, {longitude}")
    
    # Validate coordinates
    if not (-90 <= latitude <= 90):
        error_msg = f"Invalid latitude: {latitude}. Must be between -90 and 90."
        await ctx.warning(error_msg)
        logger.warning(error_msg)
        return "Error: Latitude must be between -90 and 90 degrees."
    
    if not (-180 <= longitude <= 180):
        error_msg = f"Invalid longitude: {longitude}. Must be between -180 and 180."
        await ctx.warning(error_msg)
        logger.warning(error_msg)
        return "Error: Longitude must be between -180 and 180 degrees."
    
    # Step 1: Get the forecast grid endpoint
    await ctx.debug("Step 1: Getting forecast grid endpoint from NWS points API")
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    
    await ctx.report_progress(
        progress=0.3,
        total=1.0,
        message="Getting grid information..."
    )
    
    points_data = await make_nws_request(points_url, ctx)

    if not points_data:
        error_msg = f"Unable to fetch forecast grid data for coordinates: {latitude}, {longitude}"
        await ctx.error(error_msg)
        logger.error(error_msg)
        return "Unable to fetch forecast data for this location."

    try:
        # Get the forecast URL from the points response
        forecast_url = points_data["properties"]["forecast"]
        await ctx.debug(f"Retrieved forecast URL: {forecast_url}")
        logger.debug(f"Forecast URL: {forecast_url}")
        
    except KeyError:
        error_msg = f"Invalid points response format for coordinates: {latitude}, {longitude}"
        await ctx.error(error_msg)
        logger.error(error_msg)
        return "Invalid response format from weather service points API."

    # Step 2: Get the detailed forecast
    await ctx.debug("Step 2: Getting detailed forecast data")
    await ctx.report_progress(
        progress=0.6,
        total=1.0,
        message="Fetching detailed forecast..."
    )
    
    forecast_data = await make_nws_request(forecast_url, ctx)

    if not forecast_data:
        error_msg = f"Unable to fetch detailed forecast for coordinates: {latitude}, {longitude}"
        await ctx.error(error_msg)
        logger.error(error_msg)
        return "Unable to fetch detailed forecast."

    try:
        # Format the periods into a readable forecast
        periods = forecast_data["properties"]["periods"]
        if not periods:
            await ctx.warning(f"No forecast periods available for coordinates: {latitude}, {longitude}")
            logger.warning(f"No forecast periods for coordinates: {latitude}, {longitude}")
            return "No forecast periods available for this location."
        
        period_count = min(len(periods), 5)  # Only show next 5 periods
        await ctx.info(f"Processing {period_count} forecast periods")
        logger.info(f"Processing {period_count} forecast periods")
        
        await ctx.report_progress(
            progress=0.8,
            total=1.0,
            message=f"Formatting {period_count} forecast periods..."
        )
        
        forecasts = []
        for i, period in enumerate(periods[:5]):
            forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
            forecasts.append(forecast)
            
            # Report progress for each period processed
            progress = 0.8 + (0.2 * (i + 1) / period_count)
            await ctx.report_progress(
                progress=progress,
                total=1.0,
                message=f"Processed period {i + 1}/{period_count}"
            )

        await ctx.info(f"Successfully processed forecast for coordinates: {latitude}, {longitude}")
        logger.info(f"Successfully processed forecast for coordinates: {latitude}, {longitude}")
        
        return "\n---\n".join(forecasts)
        
    except KeyError as e:
        error_msg = f"Missing required field in forecast data: {e}"
        await ctx.error(error_msg)
        logger.exception("Missing required field in forecast data")
        return "Error: Invalid forecast data format."
        
    except Exception:
        error_msg = f"Unexpected error processing forecast for coordinates: {latitude}, {longitude}"
        await ctx.error(error_msg)
        logger.exception("Unexpected error processing forecast")
        return "Error: Could not process forecast data."


@mcp.tool()
async def server_info(ctx: Context[ServerSession, None]) -> dict:
    """Get information about the current Weather MCP server configuration."""
    await ctx.info("Retrieving server information")
    logger.info("Server info requested")
    
    return {
        "server_name": ctx.fastmcp.name,
        "python_log_level": logging.getLevelName(logger.level),
        "log_file": "weather_mcp.log",
        "nws_api_base": NWS_API_BASE,
        "user_agent": USER_AGENT,
        "available_tools": ["get_alerts", "get_forecast", "server_info"],
        "logging_features": [
            "Standard Python logging to file and console",
            "MCP Context logging (debug, info, warning, error)",
            "Progress reporting for long operations",
            "Structured exception handling"
        ]
    }


def main():
    """Main entry point for the weather MCP server."""
    # Initialize and run the server
    logger.info("Starting Weather MCP Server")
    logger.info(f"Server name: {mcp.name}")
    logger.info(f"NWS API base URL: {NWS_API_BASE}")
    logger.info(f"User agent: {USER_AGENT}")
    
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Weather MCP Server shutdown requested by user")
    except Exception:
        logger.exception("Weather MCP Server encountered an unexpected error")
        raise


if __name__ == "__main__":
    main()
