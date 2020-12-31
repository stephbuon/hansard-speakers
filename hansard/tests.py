import unittest
import datetime

from .speaker import SpeakerReplacement, Office


class TestSpeakerReplacement(unittest.TestCase):
    def test_simple(self):
        first = 'John'
        surname = 'Smith'
        full_name = f'{first} {surname}'

        start = datetime.datetime(year=1850, month=1, day=1)
        end = datetime.datetime(year=1860, month=12, day=31)

        sp = SpeakerReplacement(full_name=full_name, first_name=first, last_name=surname, member_id=1,
                                start=start, end=end)

        self.assertEqual(len(sp.titles), 0)
        self.assertEqual(len(sp.middle_names), 0)
        self.assertEqual(sp.middle_possibilities, [''])

        speech_date = datetime.datetime(year=1855, month=1, day=1)
        self.assertTrue(sp.matches('John Smith', speech_date))
        self.assertTrue(sp.matches('J Smith', speech_date))
        self.assertTrue(sp.matches('J. Smith', speech_date))
        self.assertTrue(sp.matches('Smith', speech_date))

        self.assertFalse(sp.matches('JJ Smith', speech_date))
        self.assertFalse(sp.matches('JohnSmith', speech_date))
        self.assertFalse(sp.matches('John', speech_date))
        self.assertFalse(sp.matches('J', speech_date))
        self.assertFalse(sp.matches('S', speech_date))
        self.assertFalse(sp.matches('J. S', speech_date))
        self.assertFalse(sp.matches('J. S.', speech_date))
        self.assertFalse(sp.matches('', speech_date))
        self.assertFalse(sp.matches('J.', speech_date))

    def test_case_sens(self):
        first = 'jOHN'
        surname = 'SMith'
        full_name = f'{first} {surname}'

        start = datetime.datetime(year=1800, month=1, day=1)
        speech_date = datetime.datetime(year=1850, month=6, day=1)
        end = datetime.datetime(year=1900, month=12, day=31)

        sp = SpeakerReplacement(full_name=full_name, first_name=first, last_name=surname, member_id=1,
                                start=start, end=end)

        self.assertEqual(sp.first_name, 'john')
        self.assertEqual(sp.last_name, 'smith')

        self.assertEqual(len(sp.titles), 0)
        self.assertEqual(len(sp.middle_names), 0)
        self.assertEqual(sp.middle_possibilities, [''])

        self.assertTrue(sp.matches('JOHN SMITH', speech_date))
        self.assertTrue(sp.matches('j. sMiTh', speech_date))
        self.assertTrue(sp.matches('smith', speech_date))

        self.assertFalse(sp.matches('jj smith', speech_date))

    def test_excess_chars(self):
        first = ' Joh^n,\' '
        surname = ' Johnson_-_S.mit,h  \t'
        full_name = f'{first} {surname}'

        start = datetime.datetime(year=1800, month=1, day=1)
        speech_date = datetime.datetime(year=1850, month=6, day=1)
        end = datetime.datetime(year=1900, month=12, day=31)

        sp = SpeakerReplacement(full_name=full_name, first_name=first, last_name=surname, member_id=1,
                                start=start, end=end)

        self.assertEqual(sp.first_name, 'john')
        self.assertEqual(sp.last_name, 'johnson-smith')

        self.assertEqual(len(sp.titles), 0)
        self.assertEqual(len(sp.middle_names), 0)
        self.assertEqual(sp.middle_possibilities, [''])

        self.assertTrue(sp.matches('J. Johnson-Smith', speech_date))
        self.assertTrue(sp.matches('Johnson-Smith', speech_date))

        self.assertFalse(sp.matches('JJ Smith', speech_date))
        self.assertFalse(sp.matches('JohnSmith', speech_date))

        self.assertFalse(sp.matches("John Smith's", speech_date))

    def test_middle_name(self):
        first = 'John'
        middle = 'Doe'
        last = 'Smith'
        full = f'{first} {middle} {last}'

        start = datetime.datetime(year=1800, month=1, day=1)
        speech_date = datetime.datetime(year=1850, month=6, day=1)
        end = datetime.datetime(year=1900, month=12, day=31)

        sp = SpeakerReplacement(full_name=full, first_name=first, last_name=last, member_id=1,
                                start=start, end=end)

        self.assertEqual(sp.first_name, 'john')
        self.assertEqual(sp.last_name, 'smith')

        self.assertEqual(len(sp.titles), 0)
        self.assertEqual(sp.middle_names, ['doe'])

        self.assertTrue(sp.matches('J. Smith', speech_date))
        self.assertTrue(sp.matches('J. D. Smith', speech_date))
        self.assertTrue(sp.matches('J D. Smith', speech_date))
        self.assertTrue(sp.matches('J D Smith', speech_date))
        self.assertTrue(sp.matches('Doe Smith', speech_date))

        self.assertFalse(sp.matches('John Doe', speech_date))
        self.assertFalse(sp.matches('Doe', speech_date))
        self.assertFalse(sp.matches('JD Smith', speech_date))

    def test_multiple_middle(self):
        first = 'John'
        middle = 'Jim Joe Doe'
        last = 'Smith'
        full = f'{first} {middle} {last}'

        start = datetime.datetime(year=1800, month=1, day=1)
        speech_date = datetime.datetime(year=1850, month=6, day=1)
        end = datetime.datetime(year=1900, month=12, day=31)

        sp = SpeakerReplacement(full_name=full, first_name=first, last_name=last, member_id=1,
                                start=start, end=end)

        self.assertEqual(sp.first_name, 'john')
        self.assertEqual(sp.last_name, 'smith')

        self.assertTrue(sp.matches('John Jim Joe Doe Smith', speech_date))
        self.assertTrue(sp.matches('Doe Smith', speech_date))
        self.assertTrue(sp.matches('Jim Smith', speech_date))
        self.assertTrue(sp.matches('John J. J. Doe Smith', speech_date))

        self.assertTrue(sp.matches('J J J D Smith', speech_date))
        self.assertTrue(sp.matches('J. J. J. D. Smith', speech_date))
        self.assertTrue(sp.matches('J. J. D. Smith', speech_date))
        self.assertTrue(sp.matches('J. D. Smith', speech_date))
        self.assertTrue(sp.matches('J. Smith', speech_date))
        self.assertTrue(sp.matches('Smith', speech_date))

        self.assertFalse(sp.matches('John Jim', speech_date))
        self.assertFalse(sp.matches('John Doe', speech_date))
        self.assertFalse(sp.matches('J J J D', speech_date))
        self.assertFalse(sp.matches('John Jim', speech_date))
        self.assertFalse(sp.matches('JJJD Smith', speech_date))
        self.assertFalse(sp.matches('John Doe-Smith', speech_date))


class TestOffice(unittest.TestCase):
    def test1(self):
        office = Office(office_id=1, office_name='Lord of the Treasury')
        self.assertTrue(office.matches('Lord of the Treasury'))
        self.assertTrue(office.matches('  Lord    of Treasury  '))
        self.assertTrue(office.matches('Lord Treasury'))
        self.assertTrue(office.matches('Lord of Treasury'))
        self.assertTrue(office.matches('  LOr,D   of  the\t Trea_sury  '))

        self.assertFalse(office.matches('Treasury'))
        self.assertFalse(office.matches('of the'))
        self.assertFalse(office.matches('Lord of'))
        self.assertFalse(office.matches('of the Treasury'))


if __name__ == '__main__':
    unittest.main()
