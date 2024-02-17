FROM python:3.11.4-slim-bullseye

ENV LANG=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONBUFFERED=1 \
    PYTHONPATH=/workspaces/buget_automation_tool

# Set working directory
WORKDIR /opt/app

# Copy files
COPY install_packages.sh install_dependencies.sh requirements.txt ./

# Install packages
RUN bash ./install_packages.sh && \
    rm ./install_packages.sh

# Install dependencies
RUN bash ./install_dependencies.sh ./requirements.txt && \
    rm ./install_dependencies.sh ./requirements.txt
