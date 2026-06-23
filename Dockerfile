FROM lmsysorg/sglang:v0.5.13.post1-cu130

RUN apt-get update \
    && apt-get install -y --no-install-recommends screen \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /workspace

COPY pyproject.toml ./
RUN uv pip install --system --break-system-packages --no-cache -r pyproject.toml

COPY . /workspace

CMD ["/bin/bash"]
