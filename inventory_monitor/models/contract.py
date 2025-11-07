from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from utilities.choices import ChoiceSet
from utilities.querysets import RestrictedQuerySet



class ContractTypeChoices(ChoiceSet):
    key = "Contract.type"

    CHOICES = [
        ("supply", "Supply Contract", "green"),
        ("order", "Order", "red"),
        ("service", "Service Contract", "orange"),
        ("other", "Other", "blue"),
    ]


class Contract(NetBoxModel):
    objects = RestrictedQuerySet.as_manager()
    name = models.CharField(max_length=255, blank=False, null=False)
    name_internal = models.CharField(max_length=255, blank=False, null=False)
    contractor = models.ForeignKey(
        to="inventory_monitor.contractor",  # Contractor,
        on_delete=models.PROTECT,
        related_name="contracts",
        blank=True,
        null=True,
    )
    type = models.CharField(max_length=50, choices=ContractTypeChoices)
    price = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(
        blank=True,
        null=True,
        help_text="Currency for the contract price (required if price is set)",
    )
    signed = models.DateField(
        blank=True,
        null=True,
    )
    accepted = models.DateField(
        blank=True,
        null=True,
    )
    invoicing_start = models.DateField(
        blank=True,
        null=True,
    )
    invoicing_end = models.DateField(
        blank=True,
        null=True,
    )
    parent = models.ForeignKey(
        to="self",
        on_delete=models.CASCADE,
        related_name="subcontracts",
        null=True,
        blank=True,
        verbose_name="Parent contract",
    )
    comments = models.TextField(blank=True)

    @property
    def contract_type(self):
        if self.parent:
            return "subcontract"
        else:
            return "contract"

    class Meta:
        ordering = (
            "name",
            "name_internal",
            "contractor",
            "type",
            "price",
            "signed",
            "accepted",
            "invoicing_start",
            "invoicing_end",
        )

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        else:
            return f"{self.name}"

    def get_type_color(self):
        return ContractTypeChoices.colors.get(self.type)

    def get_absolute_url(self):
        return reverse("plugins:inventory_monitor:contract", args=[self.pk])

    def clean(self):
        super().clean()

        # Validate - currency is required if price is set
        if self.price is not None and self.price != 0 and not self.currency:
            raise ValidationError({"currency": "Currency is required when price is set."})
        
        # If currency is set, price must also be set
        if self.currency and self.price is None:
            raise ValidationError({"price": "Price is required when currency is set."})

        # Validate - subcontract cannot set parent which is subcontract
        if self.parent and self.parent.parent:
            raise ValidationError({"parent": "Subcontract cannot be set as Parent Contract"})

        # Validate - if parent contract has different contractor
        if self.parent and self.parent.contractor != self.contractor:
            raise ValidationError(
                {"contractor": f"Contractor must be same as Parent contractor: {self.parent.contractor}"}
            )

        # Validate invoicing_start and invoicing_end
        if self.invoicing_start and self.invoicing_end and self.invoicing_start > self.invoicing_end:
            raise ValidationError({"invoicing_start": "Invoicing Start cannot be set after Invoicing End"})
