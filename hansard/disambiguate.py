from datetime import datetime
from typing import Dict

from hansard.speaker import SpeakerReplacement

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


class ORRequirement(Requirement):
    def __init__(self, *args):
        self.requirements = args

    def __call__(self, speechdate, house):
        for requirement in self.requirements:
            if requirement(speechdate, house):
                return True

        return False


DisambiguateFunctions = {
    # mr macaulay
    2572: NoRequirement(),
    # mr bruce
    4253: HouseRequirement(HOUSE_OF_COMMONS),
    6881: HouseRequirement(HOUSE_OF_LORDS),
     # mr odonnell
    5521: BeforeDateRequirement(year=1886),
    7973: AfterDateRequirement(year=1900),
    # mr curzon
    6317: NoRequirement(),
    # mr buchanan
    5854: NoRequirement(),
    # mr lowe
    4218: NoRequirement(),
    # mr j lowther
    4967: AfterDateRequirement(year=1865),
    # mr ewart
    2551: NoRequirement(),
    # mr goulburn
    1824: NoRequirement(),
    # mr warburton
    2880: BeforeDateRequirement(year=1848),
    # mr lyttelton
    1492: BeforeDateRequirement(year=1821),
    5231: AfterDateRequirement(year=1896),
    # mr mclaren
    4853: BeforeDateRequirement(year=1881),
    5830: AfterDateRequirement(year=1881),
    # mr liddell
    8168: AfterDateRequirement(year=1903),
    2527: (HouseRequirement(HOUSE_OF_COMMONS) & BeforeDateRequirement(year=1856)) | HouseRequirement(HOUSE_OF_LORDS),
    4264: HouseRequirement(HOUSE_OF_COMMONS) & AfterDateRequirement(year=1856) & BeforeDateRequirement(year=1873, month=12, day=31),
    # mr anderson
    4295: AfterDateRequirement(year=1869) & BeforeDateRequirement(year=1884, month=12, day=31),
    # mr napier
    8189: AfterDateRequirement(year=1906) & BeforeDateRequirement(year=1901, month=12, day=31),
    4063: BeforeDateRequirement(year=1856, month=12, day=31),
    # mr hunter
    5922: NoRequirement(),
    # mr hunt
    2712: AfterDateRequirement(year=1831) & BeforeDateRequirement(year=1832, month=12, day=31),
    6106: AfterDateRequirement(year=1886) & BeforeDateRequirement(year=1892, month=12, day=31),
    # mr bright
    3812: NoRequirement(),
    # mr rees
    8268: NoRequirement(),
    # mr dalziel
    7489: NoRequirement(),
    # colonel sykes
    4571: NoRequirement(),
    # mr patrick obrien
    6238: NoRequirement(),
    # mr illingworth
    5137: BeforeDateRequirement(year=1892, month=12, day=31),
    8316: AfterDateRequirement(year=1908, month=1, day=1),
    # mr balfour
    2523: AfterDateRequirement(year=1831) & BeforeDateRequirement(year=1832),
    5410: AfterDateRequirement(year=1874) & BeforeDateRequirement(year=1911),
    # mr wotley
    3339: BeforeDateRequirement(year=1859, month=12, day=31),
    5829: AfterDateRequirement(year=1889),
    # mr matthews
    5100: NoRequirement(),

    # Mr. Stanley
    1021: AfterDateRequirement(year=1810, month=12, day=31) & BeforeDateRequirement(year=1812),
    5863: AfterDateRequirement(year=1888) & BeforeDateRequirement(year=1906, month=12, day=31),
    7892: AfterDateRequirement(year=1906),
    2326: AfterDateRequirement(year=1821) & BeforeDateRequirement(year=1843, month=12, day=31),
    4079: AfterDateRequirement(year=1855) & BeforeDateRequirement(year=1864, month=12, day=31),

    # Mr. Gregory
    3783: BeforeDateRequirement(year=1872, month=12, day=31),
    5210: AfterDateRequirement(year=1873),

    # Mr. C Buller
    2577: NoRequirement(),

    # Mr Bernal
    2072: NoRequirement(),

    # Mr Henley
    3716: NoRequirement(),

    # Mr Hobhouse
    3229: AfterDateRequirement(year=1819) & BeforeDateRequirement(year=1851, month=12, day=31),
    7539: AfterDateRequirement(year=1900)
    
    # Mr. Healy
    5804: NoRequirement(),
    
    # Mr. Shaw Lefevre
    1030: BeforeDateRequirement(year=1820),
    4783: AfterDateRequirement(year=1880),
    
    # Mr. Whitbread
    7619: AfterDateRequirement(year=1906),
    624: AfterDateRequirement(year=1804) & BeforeDateRequirement(year=1815, month=12, day=31),
    2852: AfterDateRequirement(year=1818) & BeforeDateRequirement(year=1820, month=12, day=31)

    # Mr. Canning
    1114: BeforeDateRequirement(year=1827, month=12, day=31),
    
    # Mr. Ward
    8340: AfterDateRequirement(year=1900),
    758: AfterDateRequirement(year=1803) & BeforeDateRequirement(year=1823, month=12, day=31),
    2406: AfterDateRequirement(year=1826) & BeforeDateRequirement(year=1831, month=12, day=31),
    3175: AfterDateRequirement(year=1832) & BeforeDateRequirement(year=1849, month=12, day=31),
    
    # Mr. Childers
    2894: BeforeDateRequirement(year=1842, month=12, day=31),
    4705: AfterDateRequirement(year=1863, month=1, day=1),
    
    # Mr. Walpole
    3855: NoRequirement(),
    
    # Mr. Denman
    2118: NoRequirement(),
    
    # Dr. Cameron
    5403: NoRequirement(),
    
    # Mr. Villiers
    6580: HouseRequirement(HOUSE_OF_LORDS),
    1097: AfterDateRequirement(year=1808) & BeforeDateRequirement(year=1811, month=12, day=31),
    3415: AfterDateRequirement(year=1835) & BeforeDateRequirement(year=1885, month=12, day=31),
    8132: AfterDateRequirement(year=1905),
    
    # Mr. W. Williams
    981: AfterDateRequirement(year=1819) & BeforeDateRequirement(year=1820),
    2123: AfterDateRequirement(year=1821) & BeforeDateRequirement(year=1826),
    3099: AfterDateRequirement(year=1831) & BeforeDateRequirement(year=1832),
    2937: AfterDateRequirement(year=1837) & BeforeDateRequirement(year=1838),
    3313: AfterDateRequirement(year=1850) & BeforeDateRequirement(year=1865),
    5084: AfterDateRequirement(year=1869) & BeforeDateRequirement(year=1870),
    
    # Mr. Grattan
    1263: AfterDateRequirement(year=1808) & BeforeDateRequirement(year=1820),
    2302: (AfterDateRequirement(year=1821) & BeforeDateRequirement(year=1827)) |
          (AfterDateRequirement(year=1830) & BeforeDateRequirement(year=1831)) |
          (AfterDateRequirement(year=1831) & BeforeDateRequirement(year=1832)),
    2421: (AfterDateRequirement(year=1832) & BeforeDateRequirement(year=1835)) |
          (AfterDateRequirement(year=1836) & BeforeDateRequirement(year=1837)) |
          (AfterDateRequirement(year=1838) & BeforeDateRequirement(year=1839)) |
          (AfterDateRequirement(year=1841) & BeforeDateRequirement(year=1853)),
    
    # Mr. Hopwood
    5476: AfterDateRequirement(year=1874) & BeforeDateRequirement(year=1886),
    
    # Mr. Samuel Smith
    5869: AfterDateRequirement(year=1883) & BeforeDateRequirement(year=1906),
    
    # Mr. Moore
    1195: AfterDateRequirement(year=1812) & BeforeDateRequirement(year=1820),
    2422: AfterDateRequirement(year=1826) & BeforeDateRequirement(year=1832),
    3989: AfterDateRequirement(year=1847) & BeforeDateRequirement(year=1853),
    4362: AfterDateRequirement(year=1859) & BeforeDateRequirement(year=1860),
    5376: (AfterDateRequirement(year=1875) & BeforeDateRequirement(year=1877)) |
          (AfterDateRequirement(year=1899) & BeforeDateRequirement(year=1900)),
    7896: (AfterDateRequirement(year=1900) & BeforeDateRequirement(year=1901)) |
          (AfterDateRequirement(year=1907) & BeforeDateRequirement(year=1911)),
    
    # Mr. Reynolds
    6197: AfterDateRequirement(year=1886) & BeforeDateRequirement(year=1888),
    
    # Mr. Runciman
    7907: AfterDateRequirement(year=1899) & BeforeDateRequirement(year=1910),
    
    # Mr. Molloy
    5712: AfterDateRequirement(year=1886) & BeforeDateRequirement(year=1901),
    6861: AfterDateRequirement(year=1910) & BeforeDateRequirement(year=1911),
    
    # Mr. Colquhoun
    2958: AfterDateRequirement(year=1833) & BeforeDateRequirement(year=1835),
    3508: (AfterDateRequirement(year=1837) & BeforeDateRequirement(year=1842)) |
          (AfterDateRequirement(year=1842) & BeforeDateRequirement(year=1847)),
    
    # Mr. Cripps
    1329: AfterDateRequirement(year=1809) & BeforeDateRequirement(year=1813),
    3650: AfterDateRequirement(year=1842) & BeforeDateRequirement(year=1848),
    7329: AfterDateRequirement(year=1896) & BeforeDateRequirement(year=1906),
    
    # Mr. Markham
    7991: AfterDateRequirement(year=1900) & BeforeDateRequirement(year=1911),
}


def disambiguate(target: str, speechdate: datetime, house: int, speaker_dict: Dict[int, SpeakerReplacement]) -> int:
    possibles = []

    for member_id in DisambiguateFunctions.keys():
        if target in speaker_dict[member_id].aliases:
            if DisambiguateFunctions[member_id](speechdate, house):
                possibles.append(member_id)

    if len(possibles) == 1:
        return possibles[0]
    elif len(possibles) == 0:
        return -1
    else:
        # raise ValueError('Multiple results from disambiguation of: %s' % target)
        return -1
