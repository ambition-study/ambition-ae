from django.db import models
from django.contrib.sites.models import Site
from edc_base.sites import CurrentSiteManager as BaseCurrentSiteManager

from .ae_initial import AeInitial


class BaseManager(models.Manager):

    def get_by_natural_key(self, action_identifier, site_name,
                           ae_initial_action_identifier, *args):
        site = Site.objects.get(name=site_name)
        ae_initial = AeInitial.objects.get(
            action_identifier=ae_initial_action_identifier,
            site__name=site_name)
        return self.get(
            action_identifier=action_identifier,
            site=site,
            ae_initial=ae_initial)


class AeManager(BaseManager):
    pass


class CurrentSiteManager(BaseManager, BaseCurrentSiteManager):
    pass
