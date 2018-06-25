from django.db import models
from django.db.models.deletion import PROTECT
from edc_action_item.model_mixins import ActionModelMixin
from edc_base.model_fields import OtherCharField
from edc_base.model_managers import HistoricalRecords
from edc_base.model_mixins import BaseUuidModel, ReportStatusModelMixin
from edc_base.model_validators.date import datetime_not_future
from edc_base.sites import SiteModelMixin
from edc_base.utils import get_utcnow

from ..action_items import AE_TMG_ACTION
from ..choices import AE_CLASSIFICATION
from .ae_initial import AeInitial
from .managers import CurrentSiteManager, AeManager


class AeTmg(ActionModelMixin, ReportStatusModelMixin,
            SiteModelMixin, BaseUuidModel):

    action_name = AE_TMG_ACTION

    tracking_identifier_prefix = 'AT'

    ae_initial = models.ForeignKey(AeInitial, on_delete=PROTECT)

    report_datetime = models.DateTimeField(
        verbose_name="Report date and time",
        validators=[datetime_not_future],
        default=get_utcnow)

    ae_received_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name='Date and time AE form received:')

    clinical_review_datetime = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name='Date and time of clinical review: ')

    investigator_comments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Investigator comments:')

    ae_classification = models.CharField(
        max_length=50,
        choices=AE_CLASSIFICATION)

    ae_classification_other = OtherCharField(
        max_length=250,
        blank=True,
        null=True)

    ae_description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description of AE:')

    officials_notified = models.DateTimeField(
        blank=True,
        null=True,
        validators=[datetime_not_future],
        verbose_name='Date and time regulatory authorities notified (SUSARs)')

    on_site = CurrentSiteManager()

    objects = AeManager()

    history = HistoricalRecords()

    def save(self, *args, **kwargs):
        self.subject_identifier = self.ae_initial.subject_identifier
        super().save(*args, **kwargs)

    def natural_key(self):
        return (self.report_datetime, ) + self.ae_initial.natural_key()
    natural_key.dependencies = ['ambition_ae.ae_initial', 'sites.Site']

    @property
    def action_item_reason(self):
        return self.ae_initial.ae_description

    class Meta:
        verbose_name = 'AE TMG Report'
