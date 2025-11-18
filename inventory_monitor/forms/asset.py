from core.models import ObjectType
from dcim.models import Device, Location, Module, Rack, Site
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from netbox.forms import (
    NetBoxModelBulkEditForm,
    NetBoxModelFilterSetForm,
    NetBoxModelForm,
    NetBoxModelImportForm,
)
from utilities.forms.fields import (
    CommentField,
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    TagFilterField,
)
from utilities.forms.rendering import FieldSet, InlineFields, TabbedGroups
from utilities.forms.utils import add_blank_choice
from utilities.forms.widgets.datetime import DatePicker

# Local application imports
from inventory_monitor.helpers import get_currency_choices
from inventory_monitor.models import Asset, AssetType, Contract, ExternalInventory
from inventory_monitor.models.asset import (
    ASSIGNED_OBJECT_MODELS_QUERY,
    AssignmentStatusChoices,
    LifecycleStatusChoices,
)


class AssetForm(NetBoxModelForm):
    """
    Form for creating and editing Asset objects
    """

    #
    # Field definitions
    #

    # Identification fields
    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.TextInput(attrs={"placeholder": "Description"}),
    )
    serial = forms.CharField(
        required=True,
        label="Serial",
        widget=forms.TextInput(attrs={"placeholder": "Serial"}),
    )
    partnumber = forms.CharField(
        required=False,
        label="Part Number",
    )

    # Type and classification
    type = DynamicModelChoiceField(queryset=AssetType.objects.all(), required=False, label="Type")

    # Status fields are defined in the model

    # Assignment fields - these represent the GenericForeignKey options
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label="Site",
        selector=True,
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label="Location",
        selector=True,
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label="Rack",
        selector=True,
    )
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
        selector=True,
    )
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        label="Module",
        selector=True,
    )

    # Related object fields
    order_contract = DynamicModelChoiceField(
        queryset=Contract.objects.all(), required=False, label="Order Contract", selector=True
    )
    # Additional information fields
    project = forms.CharField(
        required=False,
        label="Project",
    )
    vendor = forms.CharField(
        required=False,
        label="Vendor",
    )
    quantity = forms.IntegerField(
        required=True,
        label="Items",
        initial=1,
        min_value=1,
        help_text="Number of identical items (e.g., 5 servers with same specifications)",
    )
    price = forms.DecimalField(
        required=False,
        label="Price",
        min_value=0,
        decimal_places=2,
    )
    currency = forms.ChoiceField(
        required=False,
        label=_("Currency"),
        help_text=_("Required if price is set"),
        choices=[],
    )

    # Warranty information
    warranty_start = forms.DateField(required=False, label=("Warranty Start"), widget=DatePicker())
    warranty_end = forms.DateField(
        required=False,
        label=("Warranty End"),
        widget=DatePicker(),
    )

    # Metadata fields
    comments = CommentField(label="Comments")

    #
    # Form layout definition
    #
    fieldsets = (
        # Basic asset information
        FieldSet(
            "partnumber",
            "serial",
            "description",
            "type",
            "project",
            InlineFields("price", "currency", label=_("Price")),
            "vendor",
            "quantity",
            name=_("Asset"),
        ),
        # Status fields
        FieldSet("assignment_status", name=_("Assignment Status")),
        FieldSet("lifecycle_status", name=_("Lifecycle Status")),
        # Assignment options in tabbed interface
        FieldSet(
            TabbedGroups(
                FieldSet("site", name=_("Site")),
                FieldSet("location", name=_("Location")),
                FieldSet("rack", name=_("Rack")),
                FieldSet("device", name=_("Device")),
                FieldSet("module", name=_("Module")),
            ),
            name=_("Component Assignment"),
        ),
        # Related objects
        FieldSet(
            "order_contract",
            name=_("Order Contract"),
        ),
        FieldSet("warranty_start", "warranty_end", name=_("Dates")),
        # Metadata
        FieldSet("tags", name=_("Misc")),
    )

    class Meta:
        model = Asset
        fields = (
            # Identification fields
            "partnumber",
            "serial",
            "description",
            # Type and classification
            "type",
            # Status fields
            "lifecycle_status",
            "assignment_status",
            # Assignment fields
            "site",
            "location",
            "rack",
            "device",
            "module",
            # Related objects
            "order_contract",
            # Additional information
            "project",
            "vendor",
            "quantity",
            "price",
            "currency",
            # Warranty information
            "warranty_start",
            "warranty_end",
            # Metadata
            "comments",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        """
        Override initialization to handle assigned object properly.
        Sets initial values for assigned objects based on instance or passed parameters.
        """
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()
        assigned_object_type = initial.get("assigned_object_type")
        assigned_object_id = initial.get("assigned_object_id")

        if instance:
            # When editing: set the initial value for assigned_object selection
            for assigned_object_model in ObjectType.objects.filter(ASSIGNED_OBJECT_MODELS_QUERY):
                if type(instance.assigned_object) is assigned_object_model.model_class():
                    initial[assigned_object_model.model] = instance.assigned_object
                    break
        elif assigned_object_type and assigned_object_id:
            # When adding the Asset from an assigned_object page
            if (
                object_type := ObjectType.objects.filter(ASSIGNED_OBJECT_MODELS_QUERY)
                .filter(pk=assigned_object_type)
                .first()
            ):
                if assigned_object := object_type.model_class().objects.filter(pk=assigned_object_id).first():
                    initial[object_type.model] = assigned_object

        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

        # Set currency choices with blank option
        self.fields["currency"].choices = add_blank_choice(get_currency_choices())
        # Don't set default - let currency be blank until user adds a price

    def clean(self):
        """
        Custom validation to ensure only one assigned object is selected.
        Sets the assigned_object property based on the selected field.
        """
        super().clean()

        # Handle object assignment - check that only one is selected
        selected_objects = [
            field
            for field in (
                "site",
                "location",
                "rack",
                "device",
                "module",
            )
            if self.cleaned_data[field]
        ]

        if len(selected_objects) > 1:
            raise forms.ValidationError(_("An Asset can only be assigned to a single object."))
        elif selected_objects:
            self.instance.assigned_object = self.cleaned_data[selected_objects[0]]
        else:
            self.instance.assigned_object = None


class AssetFilterForm(NetBoxModelFilterSetForm):
    """
    Filter form for Asset objects, used in list views
    """

    model = Asset

    #
    # Form layout definition
    #
    fieldsets = (
        # Basic search options
        FieldSet("q", "filter_id", "tag", name=_("Misc")),
        # Status fields
        FieldSet("assignment_status", name=_("Assignment Status")),
        FieldSet("lifecycle_status", name=_("Lifecycle Status")),
        # Related objects for filtering
        FieldSet(
            "order_contract",
            "external_inventory_items",
            "external_inventory_number__ic",
            name=_("Related Objects"),
        ),
        # Date range filters
        FieldSet(
            "warranty_start",
            "warranty_start__gte",
            "warranty_start__lte",
            "warranty_end",
            "warranty_end__gte",
            "warranty_end__lte",
            name=_("Warranty Dates"),
        ),
        # Asset information filters
        FieldSet(
            "partnumber",
            "serial",
            "description",
            "type_id",
            "project",
            "vendor",
            name=_("Asset Details"),
        ),
        # Numeric range filters
        FieldSet("quantity", "quantity__gte", "quantity__lte", name=_("Quantity")),
        FieldSet("price", "price__gte", "price__lte", "price__isnull", "currency", name=_("Price")),
        FieldSet("has_external_inventory_items", name=_("External Inventory")),
    )

    #
    # Field definitions
    #

    # Basic search fields
    tag = TagFilterField(model)

    # Identification filters
    description = forms.CharField(required=False)
    serial = forms.CharField(required=False)
    partnumber = forms.CharField(required=False)
    external_inventory_number__ic = forms.CharField(
        required=False, label="External Inventory Number", help_text="Filter by external inventory number"
    )

    # Status filters
    assignment_status = forms.ChoiceField(
        choices=[("", "None")] + list(AssignmentStatusChoices), required=False, initial=None
    )

    lifecycle_status = forms.ChoiceField(
        choices=[("", "None")] + list(LifecycleStatusChoices), required=False, initial=None
    )

    # Type filter
    type_id = DynamicModelMultipleChoiceField(queryset=AssetType.objects.all(), required=False, label=_("Type"))

    # Related object filters
    order_contract = DynamicModelMultipleChoiceField(
        queryset=Contract.objects.all(), required=False, label=_("Order Contract")
    )
    external_inventory_items = DynamicModelMultipleChoiceField(
        queryset=ExternalInventory.objects.all(), required=False, label=_("External Inventory")
    )

    # Additional information filters
    project = forms.CharField(
        required=False,
        label="Project",
    )
    vendor = forms.CharField(
        required=False,
        label="Vendor",
    )

    # Quantity filters (exact and range)
    quantity = forms.IntegerField(required=False, label="Items")
    quantity__gte = forms.IntegerField(required=False, label=("Items: From"))
    quantity__lte = forms.IntegerField(required=False, label=("Items: Till"))

    # Price filters (exact and range)
    price = forms.DecimalField(required=False)
    price__gte = forms.DecimalField(
        required=False,
        label=("Price: From"),
    )
    price__lte = forms.DecimalField(
        required=False,
        label=("Price: Till"),
    )
    price__isnull = forms.ChoiceField(
        required=False,
        label=("Has Price"),
        choices=(
            ("", "Any"),
            ("false", "Yes"),
            ("true", "No"),
        ),
    )
    currency = forms.MultipleChoiceField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set currency choices from config
        self.fields["currency"].choices = get_currency_choices()

    # Warranty date filters (exact and range)
    warranty_start = forms.DateField(required=False, label=("Warranty Start"), widget=DatePicker())
    warranty_start__gte = forms.DateField(required=False, label=("Warranty Start: From"), widget=DatePicker())
    warranty_start__lte = forms.DateField(required=False, label=("Warranty Start: Till"), widget=DatePicker())
    warranty_end = forms.DateField(required=False, label=("Warranty End"), widget=DatePicker())
    warranty_end__gte = forms.DateField(required=False, label=("Warranty End: From"), widget=DatePicker())
    warranty_end__lte = forms.DateField(required=False, label=("Warranty End: Till"), widget=DatePicker())

    has_external_inventory_items = forms.ChoiceField(
        choices=[
            ("", "All"),
            ("true", "With External Inventory items"),
            ("false", "Without External Inventory items"),
        ],
        required=False,
        label=_("Has External Inventory items"),
        help_text=_("Filter by whether Asset object has assigned External Inventory items"),
    )


class AssetBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        required=False,
        label="Description",
        widget=forms.TextInput(attrs={"placeholder": "Description"}),
    )
    type = DynamicModelChoiceField(queryset=AssetType.objects.all(), required=False)

    assignment_status = forms.ChoiceField(choices=add_blank_choice(AssignmentStatusChoices), required=False)

    lifecycle_status = forms.ChoiceField(choices=add_blank_choice(LifecycleStatusChoices), required=False)

    project = forms.CharField(required=False)

    vendor = forms.CharField(required=False)

    order_contract = DynamicModelChoiceField(queryset=Contract.objects.all(), required=False)

    price = forms.DecimalField(required=False, decimal_places=2)

    currency = forms.ChoiceField(required=False, choices=add_blank_choice(get_currency_choices()))

    warranty_start = forms.DateField(required=False, widget=DatePicker())

    warranty_end = forms.DateField(required=False, widget=DatePicker())

    comments = CommentField(required=False)

    model = Asset
    nullable_fields = (
        "description",
        "type",
        "assignment_status",
        "lifecycle_status",
        "project",
        "vendor",
        "order_contract",
        "price",
        "currency",
        "warranty_start",
        "warranty_end",
        "comments",
    )

    fieldsets = (
        FieldSet("description", "type", name=_("Asset")),
        FieldSet("assignment_status", "lifecycle_status", name=_("Status")),
        FieldSet("project", "vendor", "order_contract", name=_("Details")),
        FieldSet("price", "currency", name=_("Financial")),
        FieldSet("warranty_start", "warranty_end", name=_("Warranty")),
        FieldSet("comments", name=_("Comments")),
    )


class AssetBulkImportForm(NetBoxModelImportForm):
    """
    Form for bulk importing Assets
    """

    # Add required fields for CSV import
    partnumber = forms.CharField(required=False)
    serial = forms.CharField(required=True)
    description = forms.CharField(required=False)
    type = CSVModelChoiceField(queryset=AssetType.objects.all(), required=False)
    assignment_status = forms.ChoiceField(choices=AssignmentStatusChoices, required=False)
    lifecycle_status = forms.ChoiceField(choices=LifecycleStatusChoices, required=False)
    project = forms.CharField(required=False)
    vendor = forms.CharField(required=False)
    order_contract = CSVModelChoiceField(
        queryset=Contract.objects.all(),
        required=False,
        to_field_name="name",  # Assuming you want to match by contract name
    )
    quantity = forms.IntegerField(required=False)
    price = forms.DecimalField(required=False, decimal_places=2)
    currency = forms.CharField(required=False)
    warranty_start = forms.DateField(required=False)
    warranty_end = forms.DateField(required=False)
    comments = forms.CharField(required=False)

    class Meta:
        model = Asset
        fields = [
            "partnumber",
            "serial",
            "description",
            "type",
            "assignment_status",
            "lifecycle_status",
            "project",
            "vendor",
            "order_contract",
            "quantity",
            "price",
            "currency",
            "warranty_start",
            "warranty_end",
            "comments",
            "tags",
        ]


class AssetExternalInventoryAssignmentForm(NetBoxModelForm):
    """
    Form for assigning External Inventory objects to an Asset
    """

    external_inventory_items = DynamicModelMultipleChoiceField(
        queryset=ExternalInventory.objects.all(),
        required=False,
        label="External Inventory Items",
        help_text="Add or Remove External Inventory items to this Asset",
        selector=True,
    )

    fieldsets = (
        FieldSet(
            "external_inventory_items",
            name=_("External Inventory Assignment"),
        ),
    )

    class Meta:
        model = Asset
        fields = ("external_inventory_items",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-select currently assigned External Inventory objects
        if self.instance and self.instance.pk:
            self.fields["external_inventory_items"].initial = self.instance.external_inventory_items.all()

        # Remove Custom Fields from form
        for cf_name in self.custom_fields.keys():
            self.fields.pop(cf_name, None)
        self.custom_fields = {}
        self.custom_fields_groups = {}

    def _post_clean(self):
        """
        Override _post_clean to skip model-level validation entirely.

        Since this form only manages the external_inventory_items many-to-many relationship
        and doesn't modify any other Asset fields, we don't need to run the model's clean()
        method which validates price/currency relationships that this form doesn't touch.

        We still perform field-level validation for the fields in this form.
        """
        # Get validation exclusions - this validates form fields
        exclude = self._get_validation_exclusions()

        # Validate field values but skip model.clean() by not calling full_clean()
        # This prevents the price/currency validation in Asset.clean()
        try:
            # Only validate fields, not the model's clean() method
            self.instance.clean_fields(exclude=exclude)
        except ValidationError as e:
            self._update_errors(e)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Get current and new relationships
            old_external_inventory_objects = set(instance.external_inventory_items.all())
            new_external_inventory_objects = set(self.cleaned_data["external_inventory_items"])

            added_objects = new_external_inventory_objects - old_external_inventory_objects
            removed_objects = old_external_inventory_objects - new_external_inventory_objects

            for rem_obj in removed_objects:
                rem_obj.snapshot()
                rem_obj.assets.remove(instance)

            for add_obj in added_objects:
                add_obj.snapshot()
                add_obj.assets.add(instance)

        return instance
