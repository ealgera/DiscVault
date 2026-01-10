# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed, e.g. for sqlite extensions)
# RUN apt-get update && apt-get install -y ...

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app ./app

# Install dependencies using pip (simpler for runtime than uv for now, or install uv)
# We export requirements from pyproject.toml/uv.lock usually, but direct pip install works if standard
# Let's install uv to be consistent with dev environment
RUN pip install uv
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run the application
# We use 'uv run' to use the virtualenv created by uv sync
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
