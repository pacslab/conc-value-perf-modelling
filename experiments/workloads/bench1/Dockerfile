FROM python:3.6-slim

# Create the user that will run the app
RUN adduser --disabled-password --gecos '' app

ENV FLASK_APP=app.py

# Install requirements
ADD src/requirements.txt /opt/requirements.txt
RUN pip install --upgrade pip && \
    pip --disable-pip-version-check --no-cache-dir install -r /opt/requirements.txt \
    && rm -rf /tmp/pip-tmp

# to enable ps command
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --no-install-recommends -y procps \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

ADD src /opt/src/

WORKDIR /opt/src
RUN chmod +x /opt/src/*.sh
RUN chown -R app:app ./

USER app

EXPOSE 5000

# entrypoint source: https://medium.com/@madflojo/shutdown-signals-with-docker-entry-point-scripts-5e560f4e2d45
ENTRYPOINT [ "/opt/src/entrypoint.sh" ]

CMD ["python", "index.py"]

