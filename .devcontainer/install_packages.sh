#!/bin/bash

# Install packages and dependencies
apt-get update

apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    libbz2-dev \
    unzip \
    curl

apt-get clean
