from django.contrib import admin

from edc_model_admin import audit_fieldset_tuple

from ..admin_site import ambition_ae_admin
from ..forms import AeTmgForm
from ..models import AeTmg
from .modeladmin_mixins import ModelAdminMixin, NonAeInitialModelAdminMixin


@admin.register(AeTmg, site=ambition_ae_admin)
class AeTmgAdmin(ModelAdminMixin, NonAeInitialModelAdminMixin, admin.ModelAdmin):

    form = AeTmgForm

    additional_instructions = 'For completion by TMG Investigators Only'

    list_display = ['subject_identifier', 'dashboard', 'status', 'ae_initial',
                    'report_datetime', 'officials_notified',
                    'report_closed_datetime']

    list_filter = ('report_datetime', 'report_status')

    search_fields = ['ae_initial__tracking_identifier',
                     'ae_initial__action_identifier',
                     'subject_identifier', 'action_identifier', 'tracking_identifier']

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'ae_initial',
                'report_datetime',
                'ae_received_datetime',
                'clinical_review_datetime',
                'investigator_comments',
                'ae_description',
                'ae_classification',
                'ae_classification_other',
                'officials_notified',
                'report_status',
                'report_closed_datetime')}),
        ['Action', {'classes': ('collapse', ), 'fields': (
            'tracking_identifier', 'action_identifier')}],
        audit_fieldset_tuple
    )

    radio_fields = {
        'report_status': admin.VERTICAL,
        'ae_classification': admin.VERTICAL}
