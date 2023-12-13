FROM ubuntu:23.10

# Install dependencies
RUN apt-get update \
    && apt-get install -qy git texlive-latex-extra python3 python3-pip python3-venv python3-tk poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install python dependencies
COPY gui_requirements.txt /gui_requirements.txt
RUN pip install -U -r gui_requirements.txt \
    && rm /gui_requirements.txt
