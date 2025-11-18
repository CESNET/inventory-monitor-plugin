from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from taggit.managers import TaggableManager
from utilities.querysets import RestrictedQuerySet


class Contractor(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    name = models.CharField(max_length=255, blank=False, null=False)
    company = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, default="")
    comments = models.TextField(blank=True)

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="contractors",
        blank=True,
        null=True,
    )

    # Override tags field to avoid reverse accessor clash with other plugins
    tags = TaggableManager(
        through="extras.TaggedItem",
        related_name="inventory_monitor_contractors",
        blank=True,
    )

    class Meta:
        ordering = (
            "name",
            "company",
            "address",
            "comments",
        )

    def clean(self):
        super().clean()

        # Check if the tenant is already assigned to another Contractor
        if self.tenant_id:
            existing_contractor = Contractor.objects.filter(tenant_id=self.tenant_id).exclude(pk=self.pk)
            if existing_contractor.exists():
                raise ValidationError(
                    ("The tenant %(tenant_id)s is already assigned to another contractor."),
                    code="unique_tenant",
                    params={"tenant_id": self.tenant_id},
                )

    def __str__(self):
        parts = [self.name] if self.name else []
        if self.company and self.company != self.name:
            parts.append(f"({self.company})")
        if self.tenant:
            parts.append(f"[{self.tenant}]")

        return " ".join(parts) if parts else f"#{self.pk}"

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:contractor", args=[self.pk])
