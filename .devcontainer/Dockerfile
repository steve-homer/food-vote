# Use a specific version of the base image for reproducibility
FROM python:3.10.13-slim

# Set Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# == STAGE 1: SYSTEM SETUP (as root) ==

# Install system dependencies and uv in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl git && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv && \
    rm -rf /var/lib/apt/lists/*

# Copy only the dependency file first to leverage Docker's build cache
COPY pyproject.toml ./

# Install system-wide dependencies as root, as this is a system modification
RUN uv pip install --system -e ".[dev]"

# Create a directory for the venv and a user
RUN mkdir /opt/venv && \
    groupadd --gid 1000 vscode && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash vscode && \
    mkdir /workspace/data && \
    # Give the user ownership of the venv and workspace
    chown -R vscode:vscode /opt/venv /workspace

# Switch to the non-root user
USER vscode

# Add the venv to the PATH. Now all 'python', 'pip', 'uv' calls will use the venv
ENV PATH="/opt/venv/bin:$PATH"

# Create the virtual environment
RUN python -m venv /opt/venv

# Copy and install dependencies into the venv (no --system needed)
COPY --chown=vscode:vscode pyproject.toml ./
RUN uv pip install -e ".[dev]"

# Copy the rest of the application code
COPY --chown=vscode:vscode . .