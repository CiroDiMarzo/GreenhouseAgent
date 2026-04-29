# The Autonomous Greenhouse Agent

A Python-based greenhouse management system that autonomously monitors and maintains plant health using asynchronous operations and SQLite persistence.

## Overview

This project implements an autonomous gardener agent called "Silvano" that manages a greenhouse with multiple plant zones. The system:

- **Monitors plant health** based on time since last watering, fertilization, and pest treatment
- **Performs automated maintenance** including watering, fertilizing, and applying pesticides
- **Persists data** to SQLite database for reliable state management
- **Runs asynchronously** to handle multiple plants efficiently
- **Imports plant data** from CSV files into the database during initialization

## Architecture

### Core Components

- **Gardener** (`gardener.py`): The main agent that performs plant maintenance tasks asynchronously
- **Plant** (`src/Plant/plant.py`): Represents a plant with health monitoring capabilities
- **PlantZone** (`src/PlantZone/plant_zone.py`): Represents a zone containing multiple plants with moisture level tracking
- **Repositories**: Handle database persistence for plants and zones
- **Migration System** (`migration.py`): Loads plant and zone data from CSV files into SQLite

### Key Features

#### Health Monitoring
Plants are inspected regularly to determine their health status:
- **THIRSTY**: Plant hasn't been watered in the configured time threshold
- **HUNGRY**: Plant hasn't been fertilized in the configured time threshold  
- **SICK**: Plant hasn't been treated with pesticide in the configured time threshold
- **HEALTHY**: Plant is in good condition

Status transitions use probabilistic evaluation (75% chance by default) when time thresholds are exceeded, adding realistic variability to plant behavior.

#### Asynchronous Maintenance Loop
The Gardener operates in a continuous maintenance cycle:
1. Inspects all plants in the garden
2. Performs necessary actions (watering, fertilizing, pest treatment)
3. Re-inspects plants after maintenance
4. Saves plant state to database
5. Waits before the next maintenance cycle (configurable idle time)

#### Data Persistence
- Uses **SQLite database** (`data/garden.db`) instead of CSV for reliability and performance
- Supports database operations through dedicated repository classes
- Includes migration system to import existing CSV data

## Project Structure

```
GreenhouseAgent/
├── src/
│   ├── main.py                    # Application entry point
│   ├── gardener.py                # Gardener agent logic
│   ├── migration.py               # CSV to SQLite migration
│   ├── globals.py                 # Global constants and utilities
│   ├── Plant/
│   │   ├── plant.py               # Plant model and health inspection
│   │   ├── plant_status.py        # Plant health status enum
│   │   └── plant_repository.py    # Database operations for plants
│   └── PlantZone/
│       ├── plant_zone.py          # PlantZone model
│       └── plant_zone_repository.py # Database operations for zones
├── data/
│   └── garden.db                  # SQLite database (created at runtime)
├── plants_registry.csv            # Plant data import file
├── plants_zones_registry.csv      # Plant zone data import file
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.8+
- No external dependencies (uses Python standard library only)

### Running the Application

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Start the greenhouse agent:
```bash
python3 src/main.py
```

The system will:
- Load plant zones from `plants_zones_registry.csv`
- Load plants from `plants_registry.csv`
- Store everything in SQLite database
- **Start the Gardener agent** which enters a continuous maintenance loop
- Monitor and maintain all plants until interrupted (Ctrl+C)

## Configuration

Global settings are defined in `globals.py`:
- `GARDENER_IDLE_TIME`: Time (seconds) between maintenance cycles
- `PLANT_TIME_DELTA_THIRSTY`: Time threshold for water status
- `PLANT_TIME_DELTA_HUNGRY`: Time threshold for fertilizer status
- `PLANT_TIME_DELTA_SICK`: Time threshold for pest treatment status
- `DATE_FORMAT`: Date format string for CSV parsing

## Future Enhancements

Potential additions to the system:
- Real sensor integration (moisture, temperature, light)
- External API integration (weather, plant care recommendations)
- LLM integration for plant disease diagnosis
- Web interface for monitoring
- Telegram/email notifications for alerts
- Hardware mocking for GPIO simulation