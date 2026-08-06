"""
GraphQL filter mixins for the inventory_monitor plugin.

NetBox 4.6 exposes `owner` as an *output* field on its GraphQL types (via
`users.graphql.mixins.OwnerMixin`) but ships no matching **filter** mixin — `owner` appears in no
core `*/graphql/filters.py` outside the `users` app. This module supplies one, modelled directly on
`tenancy.graphql.filter_mixins.TenancyFilterMixin`.

Owner *group* filtering comes for free by nesting, since `users.graphql.filters.OwnerFilter`
declares `group`::

    { owner: { group: { name: { exact: "701 - Oddeleni sitove infrastruktury" } } } }
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

import strawberry
import strawberry_django
from strawberry import ID

if TYPE_CHECKING:
    from users.graphql.filters import OwnerFilter

__all__ = ("OwnerFilterMixin",)


@dataclass
class OwnerFilterMixin:
    """Adds `owner` and `owner_id` filters for models which inherit from PrimaryModel."""

    owner: Annotated["OwnerFilter", strawberry.lazy("users.graphql.filters")] | None = strawberry_django.filter_field()
    owner_id: ID | None = strawberry_django.filter_field()
