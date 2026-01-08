FROM langchain/langgraph-api:3.11-wolfi

ADD . /deps/task_maistro

RUN set -ex && \
    for line in '[project]' \
                'name = "task_maistro"' \
                'version = "0.1"' \
                '[tool.setuptools]' \
                'py-modules = ["task_maistro", "configuration"]' \
                '[tool.setuptools.package-data]' \
                '"*" = ["**/*"]'; do \
        echo "$line" >> /deps/task_maistro/pyproject.toml; \
    done

RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -e /deps/*

ENV LANGSERVE_GRAPHS='{"task_maistro": "/deps/task_maistro/task_maistro.py:graph"}'

WORKDIR /deps/task_maistro