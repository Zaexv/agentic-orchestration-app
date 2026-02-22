# Weather Tool Integration

##Summary

Successfully added weather tools to the General Agent! The agent can now fetch real-time weather information from any location in the world.

## What Was Added

### 1. Weather Tools (`app/tools/weather.py`)

Two LangChain tools using the free wttr.in API:

**`get_weather(location: str)`**
- Gets current weather conditions
- Returns: temperature, feels like, conditions, humidity, wind, precipitation
- Also includes tomorrow's forecast

**`get_weather_forecast(location: str, days: int = 3)`**
- Gets multi-day weather forecast (1-3 days)
- Returns: daily high/low temperatures and conditions

### 2. Updated General Agent

The general agent now:
- Has weather tools bound to its LLM
- Automatically calls weather tools when users ask about weather
- Handles tool execution and integrates results into responses
- Falls back to normal responses for non-weather queries

## How to Test

### Option 1: Via API (Recommended)

```bash
# Test weather query
curl -X POST http://localhost:8000/api/chat/graph \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the weather like in Madrid?",
    "user_id": "test_user"
  }'
```

**Expected Response:**
```json
{
  "response": "\n[Tool: get_weather]\nWeather in Madrid:\n🌡️ Temperature: 12°C (54°F)\n...",
  "agent_used": "general",
  ...
}
```

### Option 2: Via Swagger UI

1. Open: http://localhost:8000/docs
2. Try POST `/api/chat/graph`
3. Request body:
```json
{
  "message": "How's the weather in Paris today?",
  "user_id": "test_user"
}
```

### Option 3: Via Frontend

If the React frontend is running (http://localhost:5173):

1. Type: "What's the weather in Tokyo?"
2. The general agent will automatically use the weather tool
3. You'll see real-time weather data in the response

## Example Queries

Try these weather-related queries:

- ✅ "What's the weather in London?"
- ✅ "How's the weather in New York today?"
- ✅ "Give me the weather forecast for Tokyo"
- ✅ "What's the temperature in Paris?"
- ✅ "Will it rain in Seattle?"
- ✅ "Weather in Madrid"

Non-weather queries still work normally:
- ✅ "Tell me about Python programming"
- ✅ "What is FastAPI?"
- ✅ "How does LangChain work?"

## How It Works

### Architecture

```
User Question → Router → General Agent
                              ↓
                         LLM with Tools
                              ↓
                    [Detects weather query]
                              ↓
                      Calls get_weather()
                              ↓
                     wttr.in API (free)
                              ↓
                      Returns weather data
                              ↓
                     LLM formats response
                              ↓
                      User sees result
```

### Technical Details

**Tool Binding:**
```python
llm_with_tools = llm.bind_tools(weather_tools)
response = llm_with_tools.invoke(messages)

# If LLM calls a tool:
if response.tool_calls:
    for tool_call in response.tool_calls:
        result = tool.invoke(tool_args)
        # Append result to response
```

**API Used:**
- **Service:** wttr.in (https://wttr.in)
- **No API key required**
- **Free tier:** Unlimited requests
- **Data format:** JSON
- **Coverage:** Worldwide

## Response Format

Weather responses include:

```
Weather in [Location]:
🌡️ Temperature: X°C (Y°F)
🤔 Feels like: Z°C
☁️ Conditions: [Clear/Cloudy/Rainy/etc]
💧 Humidity: X%
🌬️ Wind: X km/h [Direction]
🌧️ Precipitation: X mm

📅 Forecast: High X°C, Low Y°C
```

## Limitations

1. **Free API limits:**
   - wttr.in is free but may have rate limits
   - No API key required
   - Generally reliable for moderate use

2. **Forecast days:**
   - Maximum 3 days forecast
   - Configurable (1-3 days)

3. **Location resolution:**
   - Works with city names
   - Works with country names
   - May not work with very specific addresses

## Adding More Weather APIs

To add OpenWeatherMap, WeatherAPI, or other services:

1. **Get an API key** from the service
2. **Add to `.env`:**
   ```bash
   OPENWEATHER_API_KEY=your_key_here
   ```

3. **Update `app/tools/weather.py`:**
   ```python
   @tool
   def get_weather_openweathermap(location: str) -> str:
       from app.config.settings import settings
       api_key = settings.openweather_api_key
       url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
       # ... implement
   ```

4. **Add to weather_tools list:**
   ```python
   weather_tools = [get_weather, get_weather_forecast, get_weather_openweathermap]
   ```

## Files Modified

- ✅ `app/tools/__init__.py` - New package
- ✅ `app/tools/weather.py` - Weather tools implementation
- ✅ `app/agents/general.py` - Updated to use tools

## Testing

Run the weather tool directly:

```bash
cd /Users/eduardo.pertierrapuche/Development/mw-randd/agent-orchestration-app

# Test weather tool
uv run python -c "
from app.tools.weather import get_weather
result = get_weather.invoke({'location': 'London'})
print(result)
"

# Test forecast tool
uv run python -c "
from app.tools.weather import get_weather_forecast
result = get_weather_forecast.invoke({'location': 'Paris', 'days': 2})
print(result)
"
```

## Troubleshooting

### "Sorry, I couldn't fetch the weather"

**Causes:**
- Network connectivity issue
- wttr.in API temporarily down
- Invalid location name

**Solution:**
- Check internet connection
- Try a major city name (e.g., "London" instead of "Lndon")
- Wait a moment and try again

### Tool not being called

**Causes:**
- Query doesn't clearly indicate weather request
- LLM didn't recognize it as a weather query

**Solution:**
- Make the weather request more explicit
- Examples: "weather in X", "temperature in Y", "forecast for Z"

### ImportError or circular import

**Causes:**
- Circular dependency between modules

**Solution:**
- Already fixed with lazy imports in general.py
- Imports are done inside the function

## Future Enhancements

Possible improvements:

- [ ] Add more weather APIs (OpenWeatherMap, WeatherAPI.com)
- [ ] Add weather alerts/warnings tool
- [ ] Add historical weather data tool
- [ ] Cache weather results (5-10 minutes)
- [ ] Add weather-based recommendations
- [ ] Support GPS coordinates
- [ ] Add air quality index tool
- [ ] Add UV index tool

## Success Verification

✅ Weather tool created (`app/tools/weather.py`)
✅ Tools integrated with general agent
✅ API test successful (Madrid weather fetched)
✅ No circular import issues
✅ Uses free wttr.in API (no API key needed)
✅ Returns formatted, emoji-rich weather data
✅ Works with any location worldwide

**The general agent now has weather superpowers!** 🌤️
