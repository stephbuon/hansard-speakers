from datetime import datetime

UNKNOWN = 0
HOUSE_OF_COMMONS = 1
HOUSE_OF_LORDS = 2


class Requirement:
    def __call__(self, speechdate, house):
        raise NotImplementedError

    def __and__(self, other):
        return ANDRequirement(self, other)

    def __or__(self, other):
        return ORRequirement(self, other)


class DateRequirement(Requirement):
    def __init__(self, year, month=1, day=1):
        self.date = datetime(year=year, month=month, day=day)

    def __call__(self, speechdate, house):
        raise NotImplementedError


class BeforeDateRequirement(DateRequirement):
    def __call__(self, speechdate, house):
        return speechdate < self.date


class AfterDateRequirement(DateRequirement):
    def __call__(self, speechdate, house):
        return self.date < speechdate


class HouseRequirement(Requirement):
    def __init__(self, house):
        self.house = house

    def __call__(self, speechdate, house):
        return self.house == house


class NoRequirement(Requirement):
    def __call__(self, *args, **kwargs):
        return True


class ANDRequirement(Requirement):
    def __init__(self, *args):
        self.requirements = args

    def __call__(self, speechdate, house):
        for requirement in self.requirements:
            if not requirement(speechdate, house):
                return False

        return True


class ORRequirement:
    def __init__(self, *args):
        self.requirements = args

    def __call__(self, speechdate, house):
        for requirement in self.requirements:
            if requirement(speechdate, house):
                return True

        return False


DisambiguateFunctions = {
    'mr macaulay': {
        2572: NoRequirement()
    },
    'mr bruce': {
        4253: HouseRequirement(HOUSE_OF_COMMONS),
        6881: HouseRequirement(HOUSE_OF_LORDS),
    },
    'mr odonnell': {
        5521: BeforeDateRequirement(year=1886),
        7973: AfterDateRequirement(year=1900)
    },
    'mr curzon': {
        6317: NoRequirement()
    },
    'mr buchanan': {
        5854: NoRequirement()
    },
    'mr lowe': {
        4218: NoRequirement()
    },
    'mr j lowther': {
        4967: AfterDateRequirement(year=1865),
    },
    'mr ewart': {
        2551: NoRequirement()
    },
    'mr goulburn': {
        1824: NoRequirement()
    },
    'mr warburton': {
        2880: BeforeDateRequirement(year=1848)
    },
    'mr lyttelton': {
        1492: BeforeDateRequirement(year=1821),
        5231: AfterDateRequirement(year=1896),
    },
    'mr mclaren': {
        4853: BeforeDateRequirement(year=1881),
        5830: AfterDateRequirement(year=1881)
    },
    'mr liddell': {
        8168: AfterDateRequirement(year=1903),
        2527: (HouseRequirement(HOUSE_OF_COMMONS) & BeforeDateRequirement(year=1856)) | HouseRequirement(HOUSE_OF_LORDS),
        4264: HouseRequirement(HOUSE_OF_COMMONS) & AfterDateRequirement(year=1856)
    },
    'mr anderson': {
        4295: AfterDateRequirement(year=1869) & BeforeDateRequirement(year=1884, month=12, day=31)
    },
    'mr napier': {
        8189: AfterDateRequirement(year=1906) & BeforeDateRequirement(year=1901, month=12, day=31),
        4063: BeforeDateRequirement(year=1856, month=12, day=31)
    },
    'mr hunter': {
        5922: NoRequirement()
    },
    'mr hunt': {
        2712: AfterDateRequirement(year=1831) & BeforeDateRequirement(year=1832, month=12, day=31),
        6106: AfterDateRequirement(year=1886) & BeforeDateRequirement(year=1892, month=12, day=31),
    },
    'mr bright': {
        3812: NoRequirement()
    },
    'mr rees': {
        8268: NoRequirement()
    },
    'mr dalziel': {
        7489: NoRequirement()
    },
    'colonel sykes': {
        4571: NoRequirement()
    },
    'mr patrick obrien': {
        6238: NoRequirement()
    },
    'mr illingworth': {
        5137: BeforeDateRequirement(year=1892, month=12, day=31),
        8316: AfterDateRequirement(year=1908, month=1, day=1)
    },
    'mr balfour': {
        2523: AfterDateRequirement(year=1831) & BeforeDateRequirement(year=1832),
        5410: AfterDateRequirement(year=1874) & BeforeDateRequirement(year=1911)
    },
}


def disambiguate(target: str, speechdate: datetime, house: int) -> int:
    member_dict = DisambiguateFunctions.get(target)

    if member_dict is None:
        return -1

    possibles = []
    for member_id, requirement in member_dict.items():
        if requirement(speechdate, house):
            possibles.append(member_id)

    if len(possibles) == 1:
        return possibles[0]
    elif len(possibles) == 0:
        return -1
    else:
        # raise ValueError('Multiple results from disambiguation of: %s' % target)
        return -1
