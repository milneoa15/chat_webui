"""Invoke entrypoint."""

from invoke import Collection

from infra import tasks as infra_tasks


ns = Collection.from_module(infra_tasks)
