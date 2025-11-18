FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --locked

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 7777

CMD ["uv", "run", "-m", "app.main"]