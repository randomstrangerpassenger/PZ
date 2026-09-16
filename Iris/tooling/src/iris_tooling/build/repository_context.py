"""Compatibility imports for the shared repository context.

Existing build consumers and domain entry points share the same context state.
"""
from iris_tooling.common.repository_context import (
    RepositoryContext,
    RepositoryContextError,
    configure_repository,
    require_repository_context,
    require_external_workspace,
    current_layer3_generation_root,
)
