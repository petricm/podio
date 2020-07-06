#!/usr/bin/env python
"""
Tests for the ClassDefinitionValidator
"""

from __future__ import print_function, absolute_import, unicode_literals
import unittest

from podio_config_reader import ClassDefinitionValidator

class ClassDefinitionValidatorTest(unittest.TestCase):
  def setUp(self):
    pass

  def test_parse_member_valid(self):
    # setup an empty validator
    validator = ClassDefinitionValidator({'datatypes': [], 'components': []})

    parsed = validator.parse_member(r'float someFloat // with an additional comment')
    self.assertEqual(parsed['type'], r'float')
    self.assertEqual(parsed['name'], r'someFloat')
    self.assertEqual(parsed['description'], r'with an additional comment')

    parsed = validator.parse_member(r'float float2 // with numbers')
    self.assertEqual(parsed['type'], r'float')
    self.assertEqual(parsed['name'], r'float2')
    self.assertEqual(parsed['description'], r'with numbers')

    parsed = validator.parse_member(r'  float   spacefloat    //    whitespace everywhere   ')
    self.assertEqual(parsed['type'], r'float')
    self.assertEqual(parsed['name'], r'spacefloat')
    self.assertEqual(parsed['description'], 'whitespace everywhere')

    parsed = validator.parse_member(r'int snake_case // snake case')
    self.assertEqual(parsed['type'], r'int')
    self.assertEqual(parsed['name'], r'snake_case')
    self.assertEqual(parsed['description'], r'snake case')

    parsed = validator.parse_member(r'std::string mixed_UglyCase_12 // who wants this')
    self.assertEqual(parsed['type'], r'std::string')
    self.assertEqual(parsed['name'], r'mixed_UglyCase_12')
    self.assertEqual(parsed['description'], r'who wants this')

    # Check some of the trickier builtin types
    parsed = validator.parse_member(r'unsigned long long uVar // an unsigned long variable')
    self.assertEqual(parsed['type'], r'unsigned long long')
    self.assertEqual(parsed['name'], r'uVar')
    self.assertEqual(parsed['description'], r'an unsigned long variable')

    parsed = validator.parse_member(r'unsigned int uInt // an unsigned integer')
    self.assertEqual(parsed['type'], r'unsigned int')
    self.assertEqual(parsed['name'], r'uInt')
    self.assertEqual(parsed['description'], r'an unsigned integer')

    # an array definition with space everywhere it is allowed
    parsed = validator.parse_member(r'  std::array < double , 4 >   someArray   // a comment  ')
    self.assertEqual(parsed['type'], r'std::array<double, 4>')
    self.assertEqual(parsed['name'], r'someArray')
    self.assertEqual(parsed['description'], r'a comment')

    # an array definition as terse as possible
    parsed = validator.parse_member(r'std::array<int,2>anArray//with a comment')
    self.assertEqual(parsed['type'], r'std::array<int, 2>')
    self.assertEqual(parsed['name'], r'anArray')
    self.assertEqual(parsed['description'], r'with a comment')

    parsed = validator.parse_member('::TopLevelNamespaceType aValidType // hopefully')
    self.assertEqual(parsed['type'], '::TopLevelNamespaceType')
    self.assertEqual(parsed['name'], r'aValidType')
    self.assertEqual(parsed['description'], 'hopefully')


    # mock the presence of the ::GlobalType int the validator by passing it as a
    # list to the components
    validator = ClassDefinitionValidator({'datatypes': [], 'components': ['::GlobalType']})
    parsed = validator.parse_member(r'std::array<::GlobalType, 1> anArray // with a top level type')
    self.assertEqual(parsed['type'], r'std::array<::GlobalType, 1>')
    self.assertEqual(parsed['name'], r'anArray')
    self.assertEqual(parsed['description'], r'with a top level type')


  def test_parse_member_invalid(self):
    # setup an empty validator
    validator = ClassDefinitionValidator({'datatypes': [], 'components': []})

    invalid_inputs = [
        r'int // a type without name',
        r'int anIntWithoutDescription',
        r'__someType name // an illformed type',
        r'double 1WrongNamedDouble // an invalid name',
        r'std::array<double, 3>', # array without name and description
        r'std::array<double, 2> // an array without a name',
        r'std::array<int, 2> anArrayWithoutDescription',
        r'std::array<__foo, 3> anArray // with invalid type',
        r'std::array<double, N> array // with invalid size',
        r'int another ill formed name // some comment'

        # Some examples of valid c++ that are rejected by the validation
        r'unsigned long int uLongInt // technically valid c++, but not in our builtin list'
        r'::std::array<float, 2> a // technically valid c++, but breaks class generation'
        r':: std :: array<int, 3> arr // also technically valid c++ but not in our case'
    ]

    for inp in invalid_inputs:
      with self.assertRaises(Exception):
        validator.parse_member(inp)



if __name__ == '__main__':
  unittest.main()