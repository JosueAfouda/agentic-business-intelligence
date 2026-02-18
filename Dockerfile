# Use a slim Python base image
FROM python:3.12.3-slim-bookworm

# Set environment variables for non-interactive debconf
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies:
# - build-essential: For compiling certain Python and Node.js packages if needed
# - libpq-dev: PostgreSQL client libraries (runtime dependencies for psycopg2)
# - postgresql-client: Provides psql and other client tools (and pulls libpq-dev)
# - curl: Needed for various downloads, including Node.js if installed via NVM (though we'll use apt)
# - nodejs, npm: For installing the Gemini CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    postgresql-client \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Gemini CLI globally for the appuser
# Ensure npm's global bin directory is in PATH for appuser
ENV PATH="/home/appuser/.npm-global/bin:$PATH"
RUN npm config set prefix '/home/appuser/.npm-global'
RUN npm install -g @google/gemini-cli

# Copy the rest of the application code
COPY . .

# Set the default entrypoint to run the TUI script
ENTRYPOINT ["python3", "-m", "scripts.tui2"]

# No exposed ports as per requirements
# No CMD explicitly defined, as ENTRYPOINT is sufficient for the default TUI behavior
