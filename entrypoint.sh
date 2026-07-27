#!/bin/bash
# DEPRECATED: This entrypoint is no longer used
#
# The application now uses docker-compose with separate containers:
# - ollama/ollama:latest for LLM services
# - qdrant/qdrant:latest for vector database
# - Custom Python image for Flask + Streamlit
#
# To run the application, use:
#   docker-compose up -d
#
# For more information, see DOCKER_README.md

echo "ERROR: This entrypoint.sh is deprecated."
echo ""
echo "Please use docker-compose instead:"
echo "  docker-compose up -d"
echo ""
echo "See QUICKSTART.md and DOCKER_README.md for details."
exit 1
