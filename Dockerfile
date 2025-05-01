FROM debian:bullseye-slim

# Metadata
LABEL maintainer="Luiz Machado (@cryptobr)"
LABEL description="SecBridge - Integration tool for Prowler and Pacu Framework"
LABEL version="1.2"

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    unzip \
    jq \
    groff \
    less \
    lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install AWS CLI v2
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf aws awscliv2.zip

# Set up working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Prowler
RUN pip3 install prowler

# Install Pacu
RUN git clone https://github.com/RhinoSecurityLabs/pacu.git /opt/pacu \
    && cd /opt/pacu \
    && pip3 install -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/logs /app/reports/data /app/reports/prowler

# Set environment variables
ENV PATH="/opt/pacu:${PATH}"
ENV PYTHONPATH="/opt/pacu:${PYTHONPATH}"

# Default command
ENTRYPOINT ["python3", "secbridge.py"]
CMD ["--help"]
