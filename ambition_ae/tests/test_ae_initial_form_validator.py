from ambition_rando.constants import SINGLE_DOSE, CONTROL
from ambition_rando.randomization_list_importer import RandomizationListImporter
from ambition_rando.randomizer import Randomizer
from ambition_rando.tests.make_test_list import make_test_list
from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase, tag
from edc_base.tests import SiteTestCaseMixin
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NO, NOT_APPLICABLE
from edc_form_validators import NOT_REQUIRED_ERROR
from edc_registration.models import RegisteredSubject

from ..form_validators import AeInitialFormValidator
from ..forms import AeInitialForm


class TestAeInitialFormValidator(SiteTestCaseMixin, TestCase):

    def test_ae_cause_yes(self):
        options = {
            'ae_cause': YES,
            'ae_cause_other': None}
        form_validator = AeInitialFormValidator(cleaned_data=options)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('ae_cause_other', form_validator._errors)

    def test_ae_cause_no(self):
        cleaned_data = {
            'ae_cause': NO,
            'ae_cause_other': YES}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except forms.ValidationError:
            pass
        self.assertIn('ae_cause_other',
                      form_validator._errors)
        self.assertIn(NOT_REQUIRED_ERROR, form_validator._error_codes)

    def test_ambisome_relation_invalid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': NOT_APPLICABLE}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('ambisome_relation', form_validator._errors)

    def test_fluconazole_relation_invalid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': 'possibly_related',
            'fluconazole_relation': NOT_APPLICABLE}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('fluconazole_relation', form_validator._errors)

    def test_amphotericin_b_relation_invalid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': 'possibly_related',
            'fluconazole_relation': 'possibly_related',
            'amphotericin_b_relation': NOT_APPLICABLE}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('amphotericin_b_relation', form_validator._errors)

    def test_flucytosine_relation_invalid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': 'possibly_related',
            'fluconazole_relation': 'possibly_related',
            'amphotericin_b_relation': 'not_related',
            'flucytosine_relation': NOT_APPLICABLE}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('flucytosine_relation', form_validator._errors)

    def test_ambisome_relation_valid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': 'not_related'}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_fluconazole_relation_valid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': 'not_related',
            'fluconazole_relation': 'possibly_related'}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_amphotericin_b_relation_valid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': 'not_related',
            'fluconazole_relation': 'possibly_related',
            'amphotericin_b_relation': 'possibly_related'}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_flucytosine_relation_valid(self):
        cleaned_data = {
            'ae_study_relation_possibility': YES,
            'ambisome_relation': 'not_related',
            'fluconazole_relation': 'possibly_related',
            'amphotericin_b_relation': 'possibly_related',
            'flucytosine_relation': 'not_related'}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')

    def test_sae_reason_not_applicable(self):
        cleaned_data = {
            'sae': YES,
            'sae_reason': NOT_APPLICABLE}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('sae_reason', form_validator._errors)

    def test_susar_reported_not_applicable(self):
        cleaned_data = {
            'susar': YES,
            'susar_reported': NOT_APPLICABLE}
        form_validator = AeInitialFormValidator(cleaned_data=cleaned_data)
        self.assertRaises(ValidationError, form_validator.validate)
        self.assertIn('susar_reported', form_validator._errors)

    def test_ae_initial_form(self):
        subject_identifier = '12345'
        full_path = make_test_list(site_names=self.site_names)
        RandomizationListImporter(path=full_path, overwrite=True)
        rs = RegisteredSubject.objects.create(
            subject_identifier=subject_identifier)
        randomizer = Randomizer(
            subject_identifier=subject_identifier,
            site=rs.site,
            report_datetime=get_utcnow())
        drug_assignment = randomizer.model_obj.drug_assignment
        form = AeInitialForm(
            initial={'subject_identifier': subject_identifier})
        self.assertEqual(
            form.initial.get('regimen'), drug_assignment)
        form = AeInitialForm(
            initial={'subject_identifier': subject_identifier})
        form.is_valid()
        self.assertNotIn('regimen', form.errors)
        opposite_drug_assignment = (
            CONTROL if drug_assignment == SINGLE_DOSE else SINGLE_DOSE)
        form = AeInitialForm(
            data={'subject_identifier': subject_identifier,
                  'regimen': opposite_drug_assignment})
        form.is_valid()
        self.assertIn('regimen', form.errors)
