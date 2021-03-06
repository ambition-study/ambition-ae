from django.apps import AppConfig as DjangoApponfig
from django.conf import settings
from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig


class AppConfig(DjangoApponfig):
    name = 'ambition_ae'
    verbose_name = 'Ambition Adverse Events'


if settings.APP_NAME == 'ambition_ae':

    from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU

    class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
        country = 'botswana'
        definitions = {
            '7-day clinic': dict(days=[MO, TU, WE, TH, FR, SA, SU],
                                 slots=[100, 100, 100, 100, 100, 100, 100]),
            '5-day clinic': dict(days=[MO, TU, WE, TH, FR],
                                 slots=[100, 100, 100, 100, 100])}
