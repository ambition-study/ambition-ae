from django.core.exceptions import ObjectDoesNotExist
from edc_action_item import Action, HIGH_PRIORITY, site_action_items
from edc_constants.constants import YES
from django.utils.safestring import mark_safe

from .email_contacts import email_contacts

AE_INITIAL_ACTION = 'submit-initial-ae-report'
AE_TMG_ACTION = 'submit-ae-tmg-report'
AE_FOLLOWUP_ACTION = 'submit-ae-followup-report'
RECURRENCE_OF_SYMPTOMS_ACTION = 'submit-recurrence-of-symptoms'


class BaseNonAeInitialAction(Action):

    parent_model_fk_attr = 'ae_initial'
    show_link_to_changelist = True
    admin_site_name = 'ambition_ae_admin'
    priority = HIGH_PRIORITY

    @property
    def action_item_reason(self):
        return self.ae_initial.action_item_reason


class AeTmgAction(BaseNonAeInitialAction):
    name = AE_TMG_ACTION
    display_name = 'Submit AE TMG Report'
    model = 'ambition_ae.aetmg'
    create_by_user = False
    show_link_to_changelist = True
    admin_site_name = 'ambition_ae_admin'


# TODO: If severity increased from G3,trigger AeTmgAction
class AeFollowupAction(BaseNonAeInitialAction):
    name = AE_FOLLOWUP_ACTION
    display_name = 'Submit AE Followup Report'
    model = 'ambition_ae.aefollowup'
    create_by_user = False
    show_link_to_changelist = True
    admin_site_name = 'ambition_ae_admin'
    instructions = mark_safe(
        f'Email to the TMG at <a href="mailto:'
        f'{email_contacts.get("ae_reports")}">'
        f'{email_contacts.get("ae_reports")}</a>')

    def get_next_actions(self):
        actions = []
        if self.model_obj.followup == YES:
            actions.append(self)
        return actions


class AeInitialAction(Action):

    name = AE_INITIAL_ACTION
    display_name = 'Submit AE Initial Report'
    model = 'ambition_ae.aeinitial'
    show_link_to_changelist = True
    admin_site_name = 'ambition_ae_admin'
    instructions = 'Complete the initial report and forward to the TMG'
    priority = HIGH_PRIORITY

    # TODO: AeTmgAction only triggered for GRADE4
    def get_next_actions(self):
        RecurrenceOfSymptomsAction = site_action_items.get(
            'submit-recurrence-of-symptoms')
        next_actions = [
            AeFollowupAction, AeTmgAction, RecurrenceOfSymptomsAction]
        try:
            self.action_item_model_cls.objects.get(
                subject_identifier=self.model_obj.subject_identifier,
                parent_reference_identifier=self.model_obj.tracking_identifier,
                reference_model=AeTmgAction.model)
        except ObjectDoesNotExist:
            pass
        else:
            index = next_actions.index(AeTmgAction)
            next_actions.pop(index)
        if self.model_obj.ae_cm_recurrence != YES:
            index = next_actions.index(RecurrenceOfSymptomsAction)
            next_actions.pop(index)
        return next_actions


class RecurrenceOfSymptomsAction(Action):
    name = RECURRENCE_OF_SYMPTOMS_ACTION
    display_name = 'Submit Recurrence of Symptoms Report'
    model = 'ambition_ae.recurrencesymptom'
    show_link_to_changelist = True
    admin_site_name = 'ambition_ae_admin'
    priority = HIGH_PRIORITY
    create_by_user = False
    help_text = 'This document is triggered by AE Initial'


site_action_items.register(AeInitialAction)
site_action_items.register(AeTmgAction)
site_action_items.register(AeFollowupAction)
site_action_items.register(RecurrenceOfSymptomsAction)
