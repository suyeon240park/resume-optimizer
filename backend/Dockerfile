FROM python:3.12-slim

WORKDIR /app

# Install pdflatex and the packages needed to compile typical résumé templates
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-fonts-extra \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

RUN useradd --create-home appuser && \
    mkdir -p /tmp/latex-compile && \
    chown appuser:appuser /tmp/latex-compile
USER appuser

# Railway (and many PaaS) set PORT; local dev defaults to 8000
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
