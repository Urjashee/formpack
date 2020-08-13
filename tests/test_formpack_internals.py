# coding: utf-8

from __future__ import (unicode_literals, print_function,
                        absolute_import, division)

import pytest
import json

from copy import deepcopy

from formpack import FormPack, constants
from formpack.utils.iterator import get_first_occurrence
from .fixtures import build_fixture


def test_fixture_has_translations():
    """
    restauraunt_profile@v2 has two translations
    """

    title, schemas, submissions = build_fixture('restaurant_profile')
    fp = FormPack(schemas)
    assert len(fp[1].translations) == 2


def test_to_dict():
    schema = build_fixture('restaurant_profile')[1][2]
    original_content = deepcopy(schema)
    title = schema['settings']['title']
    fp = FormPack([schema])
    assert fp.title == title
    new_content = fp[0].to_dict()
    assert original_content['translations'] == new_content['translations']
    assert original_content['settings'] == new_content['settings']


def test_to_xml():
    """
    at the very least, version.to_xml() does not fail
    """
    title, schemas, submissions = build_fixture('restaurant_profile')
    fp = FormPack(schemas)
    for version in fp.versions.keys():
        fp.versions[version].to_xml()

def test_to_xml_fails_when_null_labels():
    # currently, this form will trigger a confusing error from pyxform:
    #  - Exception: (<type 'NoneType'>, None)

    # it occurs when a named translation has a <NoneType> value
    # (empty strings are OK)
    with pytest.raises(Exception) as exc:
        fp = FormPack({'survey': [
                                  {'type': 'note',
                                   'name': 'n1',
                                   '$anchor': 'n1',
                                   'label': {'tx0': ''},
                                   },
                                  ],
                       'schema': '2',
                       'settings': {'identifier': 'valid',
                                    'title': 'Null labels'},
                       'translations': [{'$anchor': 'tx0', 'name': ''}],
                       })
        fp[0].to_xml()
    assert 'PyXFormError' in repr(exc)

def test_null_untranslated_labels():
    AR_LABELS = ['إذا كان نعم ماهي المساعدات التي تتلقاها؟']
    content = {'choices': {'aid_types': [{'$anchor': 'k907ttxoc',
                                            'label': {'tx0': 'سلل غذائية'},
                                            'value': '1'},
                                           {'$anchor': 'kmixnmmph',
                                            'label': {'tx0': 'سلل شتوية'},
                                            'value': '2'},
                                           {'$anchor': 'z1j25g3lu',
                                            'label': {'tx0': 'سلل زراعية'},
                                            'value': '3'},
                                           {'$anchor': 'miaxyojzk',
                                            'label': {'tx0': 'قسائم'},
                                            'value': '4'},
                                           {'$anchor': 'hf57ckd7w',
                                            'label': {'tx0': 'أخرى'},
                                            'value': '5'}]},
                 'metas': {},
                 'settings': {
                    'identifier': 'arabic_and_null',
                    'title': 'Arabic and Null'
                 },
                 'survey': [{'$anchor': 'vp8um3sk7',
                             'label': {'tx0': AR_LABELS[0],
                              },
                             'name': 'what_aid_do_you_receive',
                             'required': True,
                             'select_from': 'aid_types',
                             'type': 'select_multiple'}],
                 'translations': [{'$anchor': 'tx0', 'name': 'arabic'},
                                  {'$anchor': 'tx1', 'name': ''}]}


    fp = FormPack(content)
    fields = fp.get_fields_for_versions()
    field = fields[0]
    assert len(fields) == 1
    expected_arabic_labels = sorted([
        'إذا كان نعم ماهي المساعدات التي تتلقاها؟',
        'إذا كان نعم ماهي المساعدات التي تتلقاها؟/سلل غذائية',
        'إذا كان نعم ماهي المساعدات التي تتلقاها؟/سلل شتوية',
        'إذا كان نعم ماهي المساعدات التي تتلقاها؟/سلل زراعية',
        'إذا كان نعم ماهي المساعدات التي تتلقاها؟/قسائم',
        'إذا كان نعم ماهي المساعدات التي تتلقاها؟/أخرى',
    ], key=len)
    arabic_labels = sorted(field.get_labels('arabic'), key=len)

    assert arabic_labels == expected_arabic_labels
    untranslated_labels = field.get_labels(constants.UNTRANSLATED)
    question_names = field.get_labels(constants.UNSPECIFIED_TRANSLATION)
    assert untranslated_labels == question_names


def test_get_fields_for_versions_returns_unique_fields():
    """
    As described in #127, `get_field_for_versions()` would return identical
    fields multiple times. This is was a failing test to reproduce that issue
    """
    fp = FormPack(
        [
            {'schema': '2',
                'survey': [
                    {'name': 'hey', 'type': 'image', '$anchor': 'hey'},
                    {'name': 'two', 'type': 'image', '$anchor': 'two'},
                ],
                'translations': [{'$anchor': 'tx0', 'name':''}],
                'settings': {
                    'identifier': 'xx',
                    'title': 'Xx Title',
                    'version': 'vRR7hH6SxTupvtvCqu7n5d',
                }
            },
            {'schema': '2',
                'survey': [
                    {'name': 'one', 'type': 'image', '$anchor': 'one'},
                    {'name': 'two', 'type': 'image', '$anchor': 'two'},
                ],
                'translations': [{'$anchor': 'tx0', 'name':''}],
                'settings': {
                    'identifier': 'xx',
                    'title': 'Xx Title',
                    'version': 'vA8xs9JVi8aiSfypLgyYW2',
                }
            },
            {'schema': '2',
                'survey': [
                    {'name': 'one', 'type': 'image', '$anchor': 'one'},
                    {'name': 'two', 'type': 'image', '$anchor': 'two'},
                ],
                'translations': [{'$anchor': 'tx0', 'name':''}],
                'settings': {
                    'identifier': 'xx',
                    'title': 'Xx Title',
                    'version': 'vNqgh8fJqyjFk6jgiCk4rn',
                }
            },
        ],
    )
    fields = fp.get_fields_for_versions(fp.versions)
    field_names = [field.name for field in fields]
    assert sorted(field_names) == ['hey', 'one', 'two']


def test_get_fields_for_versions_returns_newest_of_fields_with_same_name():
    schemas = [
        {
            'settings': {
                'version': 'v1',
                'title': 'Newest of fields with same name',
                'identifier': 'newest_of_fields_with_same_name',
            },
            'schema': '2',
            'survey': [
                {
                    'name': 'constant_question_name',
                    '$anchor': 'constant_question_name',
                    'type': 'select_one',
                    'select_from': 'choice',
                    'label': {'tx0': 'first version question label'},
                    'tags': ['hxl:#first_version_hxl']
                },
            ],
            'choices': {
                'choice': [
                    {'value': 'constant_choice_name',
                     '$anchor': 'constant_choice_name',
                    'label': {'tx0': 'first version choice label'},
                    },
                ]
            },
            'translations': [{'$anchor': 'tx0', 'name': ''}],
        },
        {
            'settings': {
                'version': 'v2',
                'title': 'Newest of fields with same name',
                'identifier': 'newest_of_fields_with_same_name',
            },
            'schema': '2',
            'survey': [
                {
                    'name': 'constant_question_name',
                    '$anchor': 'constant_question_name',
                    'type': 'select_one',
                    'select_from': 'choice',
                    'label': {'tx0': 'second version question label'},
                    'tags': ['hxl:#second_version_hxl']
                },
            ],
            'choices': {
                'choice': [
                    {'value': 'constant_choice_name',
                     '$anchor': 'constant_choice_name',
                    'label': {'tx0': 'second version choice label'},
                    },
                ]
            },
            'translations': [{'$anchor': 'tx0', 'name': ''}],
        }
    ]
    fp = FormPack(schemas)
    assert fp.title == 'Newest of fields with same name'
    fields = fp.get_fields_for_versions(fp.versions)
    # The first and only field returned should be the first field of the first
    # section of the last version
    section_value = get_first_occurrence(fp[-1].sections.values())
    assert fields[0] == get_first_occurrence(section_value.fields.values())


def test_get_fields_for_versions_returns_all_choices():
    schemas = [
        {
            'settings': {
                'version': 'v1',
                'title': 'Returns All Choices',
                'identifier': 'returns_all_choices',
            },
            'schema': '2',
            'survey': [
                {
                    'name': 'constant_question_name',
                    '$anchor': 'constant_question_name',
                    'type': 'select_one',
                    'select_from': 'choice',
                    'label': {'tx0': 'first version question label'},
                    'tags': ['hxl:#first_version_hxl']
                },
            ],
            'choices': {
                'choice': [
                    {'value': 'first_version_choice_value',
                     '$anchor': 'first_version_choice_value',
                    'label': {'tx0': 'first version choice label'},
                    },
                ]
            },
            'translations': [{'$anchor': 'tx0', 'name': ''}],
        },
        {
            'settings': {
                'version': 'v2',
                'title': 'Returns All Choices',
                'identifier': 'returns_all_choices',
            },
            'schema': '2',
            'survey': [
                {
                    'name': 'constant_question_name',
                    '$anchor': 'constant_question_name',
                    'type': 'select_one',
                    'select_from': 'choice',
                    'label': {'tx0': 'second version question label'},
                    'tags': ['hxl:#second_version_hxl']
                },
            ],
            'choices': {
                'choice': [
                    {'value': 'second_version_choice_value',
                     '$anchor': 'second_version_choice_value',
                    'label': {'tx0': 'second version choice label'},
                    },
                ]
            },
            'translations': [{'$anchor': 'tx0', 'name': ''}],
        }
    ]
    fp = FormPack(schemas)
    assert fp.title == 'Returns All Choices'
    fields = fp.get_fields_for_versions(fp.versions)
    choice_names = fields[0].choice.options.keys()
    assert 'first_version_choice_value' in choice_names
    assert 'second_version_choice_value' in choice_names


def test_field_position_with_multiple_versions():
    title, schemas, submissions = build_fixture(
        'field_position_with_multiple_versions')
    fp = FormPack(schemas)

    all_fields = fp.get_fields_for_versions(fp.versions.keys())
    expected = [
        'City',
        'Firstname',
        'Lastname',
        'Gender',
        'Age',
        'Fullname',
    ]
    field_names = [field.name for field in all_fields]
    assert len(all_fields) == 6
    assert field_names == expected


def test_fields_for_versions_list_index_out_of_range():
    title, schemas, submissions = build_fixture(
        'fields_for_versions_list_index_out_of_range')
    fp = FormPack(schemas)
    all_fields = fp.get_fields_for_versions(fp.versions.keys())
    expected = [
        'one',
        'third',
        'first_but_not_one',
    ]
    field_names = [field.name for field in all_fields]
    assert len(all_fields) == 3
    assert field_names == expected


def _empty_form_with_settings(settings, v=0):
    settings['version'] = 'v{}'.format(v)
    return {
        'settings': settings,
        'schema': '2',
        'survey': [{'type': 'note', '$anchor': 'note', 'name': 'note', 'label': {'tx0': 'Note'}}],
        'translations': [{'$anchor': 'tx0', 'name': ''}],
    }


def test_identifier_setting():
    settings = {'title': 'X'}
    # normal
    FormPack([
        _empty_form_with_settings({**settings, 'identifier': 'my_id'}, 0),
        _empty_form_with_settings({**settings, 'identifier': 'my_id'}, 1),
        _empty_form_with_settings({**settings, 'identifier': 'my_id'}, 2),
    ])

    # fp.id_string comes from the last valid identifier
    fp = FormPack([
        _empty_form_with_settings({**settings, 'identifier': 'my_id1'}, 0),
        _empty_form_with_settings({**settings, 'identifier': 'my_id2'}, 1),
        _empty_form_with_settings({**settings, 'identifier': 'my_id3'}, 2),
    ])
    assert fp.id_string == 'my_id3'


def test_title_setting():
    settings = {'identifier': 'my_id'}
    # normal
    FormPack([
        _empty_form_with_settings({**settings, 'title': 'my title'}, 0),
        _empty_form_with_settings({**settings, 'title': 'my title'}, 1),
        _empty_form_with_settings({**settings, 'title': 'my title'}, 2),
    ])

    # fp.id_string comes from the last valid identifier
    fp = FormPack([
        _empty_form_with_settings({**settings, 'title': 'my title1'}, 0),
        _empty_form_with_settings({**settings, 'title': 'my title2'}, 1),
        _empty_form_with_settings({**settings, 'title': 'my title3'}, 2),
    ])
    assert fp.title == 'my title3'

    fp = FormPack([
        _empty_form_with_settings({**settings, 'title': 'my title1'}, 0),
        _empty_form_with_settings({**settings, 'title': 'my title2'}, 1),
        _empty_form_with_settings(settings, 2),
    ])
    assert fp.title == 'my title2'
