# The Autonomous Greenhouse Agent

A Python-based greenhouse management system that autonomously monitors and maintains plant health using asynchronous operations and SQLite persistence.

## Overview

This project implements an autonomous gardener agent called "Silvano" that manages a greenhouse with multiple plant zones. The system:

- **Monitors plant hydration** based on soil moisture levels in each zone
- **Automatically waters plants** when moisture drops below the configured threshold
- **Persists data** to SQLite database for reliable state management
- **Runs asynchronously** to handle multiple plants and zones efficiently
- **Imports plant and zone data** from CSV files into the database during initialization
- **Simulates sensor readings** with realistic moisture level decay over time

## Architecture

### Core Components

- **Gardener** (`gardener.py`): The main agent that performs plant maintenance tasks asynchronously
- **Plant** (`src/Plant/plant.py`): Represents a plant with health monitoring and watering history
- **PlantStatus** (`src/Plant/plant_status.py`): Enumeration of plant health statuses
- **PlantZone** (`src/PlantZone/plant_zone.py`): Represents a zone with moisture sensors and multiple plants
- **Repositories**: Handle database persistence for plants and zones
- **Migration System** (`migration.py`): Loads plant and zone data from CSV files into SQLite
- **BaseEntity** (`src/BaseEntity/base_entity.py`): Base class for persistent entities

### Key Features

#### Health Monitoring
Plants are inspected regularly based on zone moisture levels:
- **NEEDS_WATER**: Zone moisture level is at or below the configured threshold (0.4)
- **HEALTHY**: Zone moisture level is above the threshold

Each plant's status is determined by the moisture level of its zone, ensuring consistent hydration across grouped plants.

#### Sensor Simulation
- **PlantZone** reads simulated moisture sensors each maintenance cycle
- Moisture level decreases by 0.05 units per cycle, simulating water consumption
- Zone moisture levels affect all plants in that zone

#### Asynchronous Maintenance Loop
The Gardener operates in a continuous maintenance cycle:
1. All zones read their moisture sensors
2. Plants are inspected and their status is updated based on zone moisture
3. All plants requiring water are watered
4. Plant watering timestamps are updated in the database
5. Gardener waits before the next maintenance cycle (configurable idle time: 3 seconds by default)

#### Data Persistence
- Uses **SQLite database** (`data/garden.db`) for reliable state management
- Stores plant information including species, planting date, and last watering date
- Stores zone information including zone name and current moisture level
- Database operations handled through dedicated repository classes
- Automatic migration system imports CSV data into SQLite on first run

## Project Structure

```
GreenhouseAgent/
├── src/
│   ├── main.py                        # Application entry point
│   ├── gardener.py                    # Gardener agent logic and maintenance tasks
│   ├── migration.py                   # CSV to SQLite migration system
│   ├── globals.py                     # Global constants and utility functions
│   ├── BaseEntity/
│   │   └── base_entity.py             # Base class for persistent entities
│   ├── Plant/
│   │   ├── plant.py                   # Plant model and health inspection logic
│   │   ├── plant_status.py            # Plant health status enumeration
│   │   └── plant_repository.py        # Database operations for plants
│   └── PlantZone/
│       ├── plant_zone.py              # PlantZone model with moisture sensor simulation
│       └── plant_zone_repository.py   # Database operations for zones
├── data/
│   └── garden.db                      # SQLite database (created at runtime)
├── plants_registry.csv                # Plant data import file
├── plants_zones_registry.csv          # Plant zone data import file
├── venv/                              # Python virtual environment
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.8+
- No external dependencies (uses Python standard library only)

### Setup

1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package (if needed):
```bash
pip install -e .
```

### Running the Application

1. Ensure the virtual environment is activated:
```bash
source venv/bin/activate
```

2. Start the greenhouse agent:
```bash
python3 src/main.py
```

The system will:
- Create or connect to the SQLite database (`data/garden.db`)
- Load plant zones from `plants_zones_registry.csv`
- Load plants from `plants_registry.csv`
- Create a Gardener agent named "Silvano"
- **Start the continuous maintenance loop**:
  - Read moisture sensors from all zones
  - Inspect all plants and update their health status
  - Water any plants that need water
  - Wait for the configured idle time (3 seconds)
  - Repeat until interrupted (Ctrl+C)

### Stopping the Application

Press `Ctrl+C` to gracefully stop the gardener and exit the application.

## Configuration

Global settings are defined in `globals.py`:

- **`GARDENER_IDLE_TIME`**: Time in seconds between maintenance cycles (default: 3)
- **`MOISTURE_THRESHOLD`**: Moisture level threshold below which plants need water (default: 0.4)
- **`DATE_FORMAT`**: Format string for datetime representation (default: `'%d/%m/%Y %H:%M:%S.%f'`)
- **`LOG_FORMAT`**: Format string for log output (default: `'%(asctime)s - %(levelname)s - [%(name)s] - %(message)s'`)

## CSV File Format

### plants_zones_registry.csv
Defines the greenhouse zones with moisture sensors:
```
id,name,moisture_level
1,Zone A,0.8
2,Zone B,0.7
...
```

### plants_registry.csv
Defines the plants in the greenhouse:
```
id,specie,date_added,date_watered,date_fertilized,date_cured,zone_id
1,Tomato,01/01/2024 10:00:00.000000,01/01/2024 10:00:00.000000,01/01/2024 10:00:00.000000,01/01/2024 10:00:00.000000,1
2,Lettuce,01/01/2024 10:00:00.000000,01/01/2024 10:00:00.000000,01/01/2024 10:00:00.000000,01/01/2024 10:00:00.000000,1
...
```

## Asynchronous Architecture

The application uses Python's `asyncio` library for asynchronous operations:
- The main maintenance loop (`perform_maintenance()`) is asynchronous
- Plant watering operations (`open_faucet()`) use `await` for non-blocking execution
- This allows the system to efficiently handle multiple plants and zones without blocking

## Logging

The application uses Python's standard `logging` module with the following configuration:
- **Log Level**: INFO (shows informational messages and above)
- **Log Format**: `%(asctime)s - %(levelname)s - [%(name)s] - %(message)s`
- **Logged Events**: 
  - Gardener movement to/from garden
  - Plant watering operations
  - Maintenance cycle iterations
  - Sensor reading errors

Example log output:
```
2024-04-30 10:15:23,456 - INFO - [main] - Watering plant ID: 1) - Specie: Tomato - Salute: needs_water with 0.2 litres of water.
```

## Troubleshooting

### Database Not Found
If you see errors related to `garden.db`:
- Ensure the `data/` directory exists
- Check that CSV files (`plants_registry.csv`, `plants_zones_registry.csv`) are present in the project root
- The database will be created automatically on first run

### CSV Import Errors
- Verify CSV file format matches the expected structure
- Check that date columns use the correct format: `DD/MM/YYYY HH:MM:SS.ffffff`
- Ensure all required columns are present

### No Plants Watered
- Check the moisture level in `plants_zones_registry.csv` - it should be below or at the `MOISTURE_THRESHOLD` (0.4)
- Verify that plants are correctly associated with zones via the `zone_id` column

## Development

### Project Architecture
- **Object-Oriented Design**: Uses classes (Plant, PlantZone, Gardener) for clean separation of concerns
- **Repository Pattern**: Database operations are abstracted through repository classes
- **Async/Await**: Non-blocking operations for scalability
- **SQLite**: Lightweight, file-based database for portability

### Running Tests
Currently, the project lacks automated tests. Consider adding:
- Unit tests for Plant health inspection logic
- Integration tests for the database layer
- End-to-end tests for the maintenance cycle

## Future Enhancements

Planned features and improvements:
- **Real Sensor Integration**: Support for actual IoT moisture, temperature, and light sensors
- **Advanced Plant Status**: Implement HUNGRY and SICK statuses for fertilization and pest management
- **External APIs**: Weather integration and plant care recommendations
- **AI/LLM Integration**: Plant disease diagnosis and automated care suggestions
- **Web Dashboard**: Real-time monitoring interface for plant health and zone status
- **Notifications**: Telegram/Email alerts for critical plant health issues
- **Hardware Control**: GPIO integration for controlling water pumps and electro-magnetic valves
- **Historical Analytics**: Track plant health trends over time

## License

[Specify your license here - e.g., MIT, Apache 2.0, etc.]

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.