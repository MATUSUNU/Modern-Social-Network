FROM python:3.12-slim-bullseye

WORKDIR /usr/src/app

# prevents python creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1

RUN apt-get update && \
  apt-get install -y netcat-traditional \
  curl && \
  rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -
# You need to add Poetry to your PATH after installing it
ENV PATH="/root/.local/bin:$PATH"

# We want to "cache our requirements" and "only reinstall them when pyproject.toml or poetry.lock files change".
# Otherwise builds will be slow. To achieve working cache layer we should put:
# Poetry sees readme = "README.md" in pyproject.toml,
# looks for it, and fails because it’s not inside the container yet.
COPY poetry.lock pyproject.toml ./

# --no-interaction not to ask any interactive questions
# RUN poetry install --no-interaction
RUN poetry install --no-root

# COPY scripts/entrypoint.sh .
COPY scripts/ ./scripts/
RUN sed -i 's/\r$//g' /usr/src/app/scripts/entrypoint.dev.sh && \
  chmod +x /usr/src/app/scripts/entrypoint.dev.sh

COPY . .

ENTRYPOINT ["/usr/src/app/scripts/entrypoint.dev.sh"]

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
