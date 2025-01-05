#!/bin/bash

# Variables
CONTAINER_NAME="cgdac_postgres"
DUMP_FILE=$1
ENV_FILE="../.env"

# Check if the dump file argument is provided
if [[ -z "$DUMP_FILE" ]]; then
  echo "Usage: $0 <dump_file>"
  exit 1
fi

# Check if the .env file exists
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: .env file not found at '$ENV_FILE'."
  exit 1
fi

# Load database credentials from .env
DB_NAME=$(grep -E '^POSTGRES_DATABASE=' "$ENV_FILE" | cut -d '=' -f2)
DB_USER=$(grep -E '^POSTGRES_USER=' "$ENV_FILE" | cut -d '=' -f2)

# Check if DB_NAME and DB_USER are loaded
if [[ -z "$DB_NAME" || -z "$DB_USER" ]]; then
  echo "Error: DB_NAME or DB_USER not found in .env file."
  exit 1
fi

# Dump the database from the container
echo "Dumping database '$DB_NAME' from container '$CONTAINER_NAME'..."
docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner > "$DUMP_FILE"

# Check if the dump was successful
if [[ $? -eq 0 ]]; then
  echo "Database dump completed successfully. File saved as '$DUMP_FILE'."
else
  echo "Error: Failed to dump the database."
  exit 1
fi