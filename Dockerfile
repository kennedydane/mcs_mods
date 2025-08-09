FROM ubuntu:22.04

# Install dependencies and uv globally
RUN apt-get update && apt-get install -y \
    python3 \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy server files
COPY bedrock-server-1.21.100.7.zip /tmp/
RUN unzip /tmp/bedrock-server-1.21.100.7.zip -d /app/ && \
    rm /tmp/bedrock-server-1.21.100.7.zip

# Copy Python project files
COPY pyproject.toml uv.lock server_wrapper.py /app/

# Install Python dependencies with uv
RUN uv sync --frozen

# Create directories for configs and add-ons
RUN mkdir -p /app/config /app/behavior_packs /app/resource_packs

# Expose ports
EXPOSE 19132/udp 8000/tcp

# Start the Python wrapper using uv
CMD ["uv", "run", "server_wrapper.py"]