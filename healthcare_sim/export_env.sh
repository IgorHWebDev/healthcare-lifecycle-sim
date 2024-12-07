#!/bin/bash

# Export environment variables from .env
export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2)
export MIMIC_DATABASE_PATH=$(grep MIMIC_DATABASE_PATH .env | cut -d '=' -f2)
export SIMULATION_STEP_DURATION=$(grep SIMULATION_STEP_DURATION .env | cut -d '=' -f2)
export DEBUG_MODE=$(grep DEBUG_MODE .env | cut -d '=' -f2)

# Print exported variables (without showing sensitive values)
echo "Environment variables exported:"
echo "OPENAI_API_KEY=********"
echo "MIMIC_DATABASE_PATH=$MIMIC_DATABASE_PATH"
echo "SIMULATION_STEP_DURATION=$SIMULATION_STEP_DURATION"
echo "DEBUG_MODE=$DEBUG_MODE" 