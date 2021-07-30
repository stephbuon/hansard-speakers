from datetime import datetime
from enum import IntEnum
from typing import Dict

from hansard.speaker import SpeakerReplacement

UNKNOWN = 0
HOUSE_OF_COMMONS = 1
HOUSE_OF_LORDS = 2


class Requirement:
    def __call__(self, speechdate, house, debate_id):
        raise NotImplementedError

    def __and__(self, other):
        return ANDRequirement(self, other)

    def __or__(self, other):
        return ORRequirement(self, other)


class NoRequirement(Requirement):
    def __call__(self, *args, **kwargs):
        return True


class ANDRequirement(Requirement):
    def __init__(self, *args):
        self.requirements = args

    def __call__(self, speechdate, house, debate_id):
        for requirement in self.requirements:
            if not requirement(speechdate, house, debate_id):
                return False

        return True


class ORRequirement(Requirement):
    def __init__(self, *args):
        self.requirements = args

    def __call__(self, speechdate, house, debate_id):
        for requirement in self.requirements:
            if requirement(speechdate, house, debate_id):
                return True

        return False


class DateRequirement(Requirement):
    def __init__(self, year, month=1, day=1):
        self.date = datetime(year=year, month=month, day=day)

    def __call__(self, speechdate, house, debate_id):
        raise NotImplementedError


class BeforeDateRequirement(DateRequirement):
    def __call__(self, speechdate, house, debate_id):
        return speechdate < self.date


class AfterDateRequirement(DateRequirement):
    def __call__(self, speechdate, house, debate_id):
        return self.date < speechdate


class OnDateRequirement(DateRequirement):
    def __call__(self, speechdate, house, debate_id):
        return self.date == speechdate


class YearRequirement(Requirement):
    def __init__(self, year: int):
        self.year: int = year

    def __call__(self, speechdate, house, debate_id):
        return speechdate.year == self.year


class WithinYearsRequirement(Requirement):
    def __init__(self, startYear: int, endYear: int, inclusive=True):
        self.startYear: int = startYear
        self.endYear: int = endYear
        self.inclusive: bool = inclusive

    def __call__(self, speechdate, house, debate_id):
        if self.inclusive:
            return self.startYear <= speechdate.year <= self.endYear
        else:
            return self.startYear < speechdate.year < self.endYear


class HouseRequirement(Requirement):
    def __init__(self, house):
        self.house = house

    def __call__(self, speechdate, house, debate_id):
        return self.house == house


class DebateRequirement(Requirement):
    def __init__(self, debate_ids):
        if type(debate_ids) in (list, tuple, set):
            self.debate_ids = debate_ids
        else:
            self.debate_ids = [debate_ids, ]

    def __call__(self, speechdate, house, debate_id):
        return debate_id in self.debate_ids

##################
# Debate ID Sets #
##################


# query: debate title contains "corn "
SIR_PEEL_CORN_DEBATES = {1251, 2233, 15472, 15585, 15644, 15672, 15682, 15703, 15737, 15739, 15740, 15747, 15783, 15863,
                         15869, 15906, 17774, 18602, 18136, 18259, 18678, 18741, 18743, 18745, 18750, 18754, 18767,
                         18773, 18776, 18788, 18794, 18937, 18959}

# query: sentence entities contains "ireland"
SIR_PEEL_IRELAND_DEBATES = {1251, 7005, 7073, 7205, 7326, 7499, 7599, 7625, 7626, 7703, 7900, 15417, 15438, 15469,
                            15612, 15626, 15667, 15679, 15702, 15708, 15766, 15822, 15832, 15849, 15854, 15863, 15906,
                            15910, 15947, 15953, 16070, 16081, 16098, 16129, 16133, 16206, 16505, 16521, 16256, 16278,
                            16294, 16336, 16337, 16416, 16446, 16892, 16999, 17003, 17019, 17029, 17066, 17068, 17081,
                            17083, 17091, 17168, 17201, 17207, 17221, 17247, 17318, 17320, 17322, 17335, 17408, 17415,
                            17416, 17417, 17435, 17436, 17567, 17579, 17580, 17581, 17591, 17637, 17647, 17654, 17681,
                            17711, 17726, 17732, 17769, 17774, 17789, 17811, 17813, 17817, 17829, 17834, 17919, 17945,
                            17951, 17960, 18013, 18050, 18054, 18057, 18060, 18066, 18071, 18320, 18407, 18410, 18415,
                            18418, 18420, 18488, 18556, 18591, 18599, 18602, 18615, 18640, 18110, 18118, 18126, 18138,
                            18156, 18160, 18174, 18250, 18251, 18252, 18257, 18259, 18271, 18275, 18283, 18300, 18678,
                            18687, 18698, 18736, 18741, 18750, 18766, 18771, 18788, 18826, 18830, 18833, 18835, 18862,
                            18865, 18876, 18881, 18888, 18891, 18903, 18935, 18936, 18937, 18943, 18959, 18974, 18986,
                            18991, 19064, 19077, 19079, 19081, 19089, 19348, 19404, 19503, 19571, 19591, 19679, 19828,
                            19859, 20024, 20274, 20289, 20645, 20678, 20767, 20965, 20972, 21028, 21120, 21254, 21268,
                            21304, 21305, 21407, 21472, 21694, 21760, 22089, 22107}

# query: debate title contains "apprentice"
SIR_PEEL_APPRENTICE_DEBATES = {1496, }


# query: debate title contains "cotton"
SIR_PEEL_COTTON_DEBATES = {1464, 1472, 1488, 2944, 3056, 3572}

# query: sentence entities contains "lancashire"
SIR_PEEL_LANCASHIRE_DEBATES = {2233, 7959, 8811, 15417, 15477, 15667, 15687, 15926, 16098,
                               16180, 16951, 18488, 18591, 18750, 18789, 18937, 19571, 19775,
                               19859, 20678, 21254, 21280, 21788}


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
    7539: AfterDateRequirement(year=1900),
    
    # Mr. Healy
    5804: NoRequirement(),
    
    # Mr. Shaw Lefevre
    1030: BeforeDateRequirement(year=1820),
    4783: AfterDateRequirement(year=1880),
    
    # Mr. Whitbread
    7619: AfterDateRequirement(year=1906),
    624: AfterDateRequirement(year=1804) & BeforeDateRequirement(year=1815, month=12, day=31),
    2852: AfterDateRequirement(year=1818) & BeforeDateRequirement(year=1820, month=12, day=31),

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
    
    # Mr. Villiers
    6580: HouseRequirement(HOUSE_OF_LORDS),
    1097: AfterDateRequirement(year=1808) & BeforeDateRequirement(year=1811, month=12, day=31),
    3415: AfterDateRequirement(year=1835) & BeforeDateRequirement(year=1885, month=12, day=31),
    8132: AfterDateRequirement(year=1905),
    
    # Mr. W. Williams
    981: AfterDateRequirement(year=1819) & BeforeDateRequirement(year=1820),
    2123: AfterDateRequirement(year=1821) & BeforeDateRequirement(year=1826),
    3099: AfterDateRequirement(year=1831) & BeforeDateRequirement(year=1832),
    2937: YearRequirement(1837) | YearRequirement(1834) | WithinYearsRequirement(1836, 1839),  # Also Mr. Wynn
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

    # Mr. Bennet
    1463: AfterDateRequirement(year=1812) & BeforeDateRequirement(year=1825),
    6026: AfterDateRequirement(year=1886) & BeforeDateRequirement(year=1887),
    8381: AfterDateRequirement(year=1906) & BeforeDateRequirement(year=1910),

    # Mr. Robinson
    639: (AfterDateRequirement(year=1819) & BeforeDateRequirement(year=1820)) |
         (AfterDateRequirement(year=1808) & BeforeDateRequirement(year=1813)),
    2241: (AfterDateRequirement(year=1820) & BeforeDateRequirement(year=1822)) |
          (AfterDateRequirement(year=1828) & BeforeDateRequirement(year=1833)),
    3247: AfterDateRequirement(year=1832) & BeforeDateRequirement(year=1838),
    5691: AfterDateRequirement(year=1886) & BeforeDateRequirement(year=1887),
    8129: AfterDateRequirement(year=1906) & BeforeDateRequirement(year=1909),

    # Mr. Lefroy
    2995: WithinYearsRequirement(startYear=1838, endYear=1841) |
          (AfterDateRequirement(year=1833, month=1, day=1) & BeforeDateRequirement(year=1833, month=6, day=1)),
    2663: WithinYearsRequirement(startYear=1830, endYear=1832) |
          WithinYearsRequirement(startYear=1834, endYear=1836) |
          WithinYearsRequirement(startYear=1842, endYear=1847) |
          (AfterDateRequirement(year=1833, month=6, day=1) & BeforeDateRequirement(year=1834, month=1, day=1)),

    # Mr. Morton
    6397: WithinYearsRequirement(startYear=1890, endYear=1910),

    # Mr. Pease
    2966: WithinYearsRequirement(startYear=1833, endYear=1839),
    4572: WithinYearsRequirement(startYear=1857, endYear=1865),
    4851: WithinYearsRequirement(startYear=1866, endYear=1882),
    7390: WithinYearsRequirement(startYear=1896, endYear=1910),

    # Mr. Wynn
    1610: YearRequirement(1809),
    3101: YearRequirement(1812) |
          WithinYearsRequirement(1822, 1826) |
          YearRequirement(1831) |
          YearRequirement(1833) |
          YearRequirement(1835) |
          YearRequirement(1841),
    2398: WithinYearsRequirement(1826, 1830),
    3658: WithinYearsRequirement(1842, 1845),
    4758: AfterDateRequirement(year=1868),

    # Mr. Ponsonby
    8432: WithinYearsRequirement(1908, 1910),

    # Mr. Whalley
    5756: WithinYearsRequirement(1880, 1881),
    4339: WithinYearsRequirement(1853, 1877),

    # Mr. Lambert
    2538: WithinYearsRequirement(1830, 1832),
    6438: WithinYearsRequirement(1893, 1910),

    # Mr. ODoherty
    5994: AfterDateRequirement(1886, 1, 1) & BeforeDateRequirement(1889, 12, 31),
    7934: AfterDateRequirement(1901, 1, 1) & BeforeDateRequirement(1905, 12, 31),
    8164: AfterDateRequirement(1906, 1, 1) & BeforeDateRequirement(1910, 12, 31),

    # Mr. Abercromy
    1741: NoRequirement(),

    # Mr. Lonsdale
    7413: NoRequirement(),

    # Mr. Ricardo
    2149: AfterDateRequirement(1817, 1, 1) & BeforeDateRequirement(1823, 12, 31),
    3740: AfterDateRequirement(1847, 1, 1) & BeforeDateRequirement(1858, 12, 31),

    # Mr. Seely
    3978: NoRequirement(),

    # Mr. Knox
    1841: AfterDateRequirement(1814, 1, 1) & BeforeDateRequirement(1819, 12, 31),
    6402: AfterDateRequirement(1890, 1, 1) & BeforeDateRequirement(1895, 12, 31),
    4110: AfterDateRequirement(1851, 1, 1) & BeforeDateRequirement(1853, 12, 31),

    # Mr. Harvey
    2026: AfterDateRequirement(1830, 1, 1) & BeforeDateRequirement(1834, 12, 31),
    8306: AfterDateRequirement(1906, 1, 1) & BeforeDateRequirement(1910, 12, 31),

    # Mr. Blake
    1887: AfterDateRequirement(1819, 1, 1) & BeforeDateRequirement(1820, 12, 31),
    3261: (AfterDateRequirement(1838, 1, 1) & BeforeDateRequirement(1841, 12, 31)) |
          (AfterDateRequirement(1855, 1, 1) & BeforeDateRequirement(1856, 12, 31)),
    4558: AfterDateRequirement(1857, 1, 1) & BeforeDateRequirement(1887, 12, 31),

    # Mr. Barnes
    4158: (AfterDateRequirement(1862, 1, 1) & BeforeDateRequirement(1867, 12, 31)),
    5670: (AfterDateRequirement(1887, 1, 1) & BeforeDateRequirement(1891, 12, 31)),
    8197: (AfterDateRequirement(1906, 1, 1) & BeforeDateRequirement(1910, 12, 31)),

    # Mr. Whitmore
    2196: AfterDateRequirement(1821) & BeforeDateRequirement(1832, 12, 31),
    4163: AfterDateRequirement(1853),

    # Mr. Whitey
    5626: NoRequirement(),

    # Mr. Whitelaw
    5404: AfterDateRequirement(1875),

    # Mr. Whitehead
    8187: NoRequirement(),

    # Mr. White
    4530: AfterDateRequirement(1857) & BeforeDateRequirement(1876, 12, 31),
    3057: AfterDateRequirement(1837) & BeforeDateRequirement(1839, 12, 31),

    # Mr. Wharton
    636: NoRequirement(),

    # Mr. Western
    1510: NoRequirement(),

    # Mr. West
    5129: AfterDateRequirement(1869) & BeforeDateRequirement(1885, 12, 31),
    740: AfterDateRequirement(1804) & BeforeDateRequirement(1806, 12, 31),
    2416: AfterDateRequirement(1826) & BeforeDateRequirement(1832, 12, 31),

    # Mr Weguelin
    4418: NoRequirement(),

    # Mr. Vivian
    4304: AfterDateRequirement(1860, 1, 1) & BeforeDateRequirement(1868, 12, 31),
    8120: AfterDateRequirement(1906, 1, 1) & BeforeDateRequirement(1910, 12, 31),

    # Mr. Verney
    8136: NoRequirement(),

    # Mr. Vansittart
    989: AfterDateRequirement(1803, 1, 1) & BeforeDateRequirement(1811, 12, 31),
    4570: AfterDateRequirement(1857, 1, 1) & BeforeDateRequirement(1858, 12, 31),

    # Mr. Trelawny
    3806: NoRequirement(),

    # Mr. Tottenham
    5722: NoRequirement(),

    # Mr. Thorne
    8371: NoRequirement(),

    # Mr Thesiger
    3611: NoRequirement(),

    # Mr. Tenneyson
    2046: NoRequirement(),

    # Mr Talbot
    1215: YearRequirement(1804),
    2989: AfterDateRequirement(1831, 1, 1) & BeforeDateRequirement(1833, 12, 31),
    5132: AfterDateRequirement(1894, 1, 1) & BeforeDateRequirement(1909, 12, 31),

    # Mr. Younger
    8108: AfterDateRequirement(1906) & BeforeDateRequirement(1911),

    # Mr. Yerburgh
    6254: AfterDateRequirement(1894) & BeforeDateRequirement(1911),

    # Mr. Woods
    7587: AfterDateRequirement(1894) & BeforeDateRequirement(1901),

    # Mr. Wodehouse
    1974: AfterDateRequirement(1818) & BeforeDateRequirement(1854),
    5640: AfterDateRequirement(1880) & BeforeDateRequirement(1887),

    # Mr. Wilse
    4293: AfterDateRequirement(1852) & BeforeDateRequirement(1860),

    # Mr. Williamson
    5781: AfterDateRequirement(1880) & BeforeDateRequirement(1893),
    7518: AfterDateRequirement(1907) & BeforeDateRequirement(1910),

    # Mr. Wilbraham
    1869: AfterDateRequirement(1811) & BeforeDateRequirement(1816),
    2033: AfterDateRequirement(1819) & BeforeDateRequirement(1822),
    2499: AfterDateRequirement(1828) & BeforeDateRequirement(1842),

    # Mr. Stoehron
    2559: NoRequirement(),

    # Mr. Snowden
    8121: NoRequirement(),

    # Mr. Smollett
    4632: NoRequirement(),

    # Mr. Sloan
    8058: NoRequirement(),

    # Mr. Simon
    8362: NoRequirement(),

    # Mr. Shirley
    5993: NoRequirement(),

    # Mr. Sheridan
    1078: AfterDateRequirement(1809) & BeforeDateRequirement(1813),
    3834: AfterDateRequirement(1846) & BeforeDateRequirement(1868),

    # Mr. Sheehan
    6061: YearRequirement(1893),
    8052: AfterDateRequirement(1901) & BeforeDateRequirement(1911),

    # Mr. Sears
    8146: NoRequirement(),

    # Mr. Scarlett
    2148: AfterDateRequirement(1819) & BeforeDateRequirement(1836),

    # Mr. Sandford
    4209: AfterDateRequirement(1874) & BeforeDateRequirement(1879),
    
    # Mr. Ruthven
    1399: AfterDateRequirement(1830) & BeforeDateRequirement(1836),
    
    # Mr. Russell
    6331: AfterDateRequirement(1889) & BeforeDateRequirement(1910),
    1885: YearRequirement(1832),
    
    # Mr. Rowlands
    6266: NoRequirement(),
    
    # Mr. Rose
    709: AfterDateRequirement(1803) & BeforeDateRequirement(1819),
    8070: AfterDateRequirement(1903) & BeforeDateRequirement(1910),
    1066: YearRequirement(1819),
    
    # Mr. Rodgers
    8161: AfterDateRequirement(1906) & BeforeDateRequirement(1910),
    
    # Mr. Roche
    3063: AfterDateRequirement(1838) & BeforeDateRequirement(1856),
    
    # Mr. Rocher
    6408: AfterDateRequirement(1890) & BeforeDateRequirement(1910),
    
    # Mr Robertson
    4606: AfterDateRequirement(1863) & BeforeDateRequirement(1874),
    4756: AfterDateRequirement(1874) & BeforeDateRequirement(1886),
    5959: AfterDateRequirement(1886) & BeforeDateRequirement(1892),
    7775: AfterDateRequirement(1892) & BeforeDateRequirement(1909),
    
    # Mr. Ridley
    1244: AfterDateRequirement(1824) & BeforeDateRequirement(1838),
    3722: AfterDateRequirement(1841) & BeforeDateRequirement(1847),
    5168: AfterDateRequirement(1870) & BeforeDateRequirement(1878),
    7916: YearRequirement(1910),
    
    # Mr. Richardson
    7566: NoRequirement(),
    
    # Mr. Renwick
    8003: NoRequirement(),
    
    # Mr. Remnant
    7949: NoRequirement(),
    
    # Mr. Redmond
    5846: AfterDateRequirement(1881) & BeforeDateRequirement(1883),
    5883: AfterDateRequirement(1892) & BeforeDateRequirement(1910),
    
    # Mr. Rea
    7955: NoRequirement(),
    
    # Mr. Rawlinson
    8141: NoRequirement(),
    
    # Mr. Rathbone
    5150: NoRequirement(),
    
    # Mr. Rankin
    5723: NoRequirement(),
    
    # Mr. Ramsay
    5033: NoRequirement(),
    
    # Mr. Radford
    8227: NoRequirement(),
    
    # Mr. Quilter
    6182: AfterDateRequirement(1886) & BeforeDateRequirement(1898),
    8585: YearRequirement(1910),
    
    # Mr. O'Sullivan
    5431: AfterDateRequirement(1879) & BeforeDateRequirement(1886),
    8516: YearRequirement(1910),
    
    # Mr. O'Shaugnessy
    7984: NoRequirement(),
    
    # Mr. Osborne
    3768: AfterDateRequirement(1846) & BeforeDateRequirement(1874),
    
    # Mr. O'Mara
    7974: NoRequirement(),
    
    # Mr. O'Kelly
    5765: NoRequirement(),
    
    # Mr. O'Conor
    3148: YearRequirement(1839),
    4708: AfterDateRequirement(1870) & BeforeDateRequirement(1881),
    
    # Mr. O'Brien
    2548: AfterDateRequirement(1828) & BeforeDateRequirement(1840),
    2920: YearRequirement(1855),
    5870: AfterDateRequirement(1889) & BeforeDateRequirement(1911),
    
    # Mr. O'Beirne
    4831: NoRequirement(),
    
    # Mr. North
    2352: NoRequirement(),
    
    # Mr. Nolan
    6099: NoRequirement(),
    
    # Mr. O'Connor
    2929: AfterDateRequirement(1831) & BeforeDateRequirement(1852),
    5689: AfterDateRequirement(1889) & BeforeDateRequirement(1911),
    
    # Mr. Hume
    1712: AfterDateRequirement(1812) & BeforeDateRequirement(1855),
    
}


SpecificAliasFunctions = {
    'mr peel': {
      1664: (AfterDateRequirement(year=1810, month=1, day=23) & BeforeDateRequirement(year=1815, month=7, day=4)) |
            (AfterDateRequirement(year=1823, month=4, day=25) & BeforeDateRequirement(year=1828, month=12, day=31)),
      4946: AfterDateRequirement(year=1886, month=1, day=1) & BeforeDateRequirement(year=1886, month=12, day=31),
      7305: AfterDateRequirement(1900, month=1, day=1) & BeforeDateRequirement(year=1910, month=7, day=25),
},

    'sir r peel': {
        1664: (
                  (AfterDateRequirement(year=1810, month=1, day=1) & BeforeDateRequirement(year=1815, month=12, day=31)) &
                  (DebateRequirement(SIR_PEEL_COTTON_DEBATES) | DebateRequirement(SIR_PEEL_CORN_DEBATES) | DebateRequirement(SIR_PEEL_IRELAND_DEBATES))
              ) |
              (
                  (AfterDateRequirement(year=1830, month=11, day=2) & BeforeDateRequirement(year=1850, month=6, day=17))
              )
        ,
        1098: (AfterDateRequirement(year=1810, month=1, day=1) & BeforeDateRequirement(year=1815, month=12, day=31)) &
              (DebateRequirement(SIR_PEEL_APPRENTICE_DEBATES) | DebateRequirement(SIR_PEEL_COTTON_DEBATES) | DebateRequirement(SIR_PEEL_LANCASHIRE_DEBATES)),
    },

    'sir robert peel': {
        1098: (AfterDateRequirement(year=1811, month=3, day=11) & BeforeDateRequirement(year=1815, month=6, day=6)) &
              (DebateRequirement(SIR_PEEL_APPRENTICE_DEBATES) | DebateRequirement(SIR_PEEL_COTTON_DEBATES) | DebateRequirement(SIR_PEEL_LANCASHIRE_DEBATES)),
        1664: (OnDateRequirement(year=1815, month=3, day=6) & DebateRequirement(SIR_PEEL_CORN_DEBATES)) |
              (AfterDateRequirement(year=1830, month=10, day=26) & BeforeDateRequirement(year=1849, month=12, day=31))
    },

    'dr cameron': {
        5403: NoRequirement(),
    },

    'colonel sykes': {
        4571: NoRequirement(),
    },

    'mr james hope': {
        8023: NoRequirement(),
    },
    'james hope': {
        8023: NoRequirement(),
    },

    'mr john oconnor': {
        5912: NoRequirement(),
    },
    'john oconnor': {
        5912: NoRequirement(),
    },

    'sir earlley wilmot': {
        3218: NoRequirement(),
    },

    'sir carles russell': {
        4815: NoRequirement(),
    },

    'sir andrew agnewe': {
        3240: AfterDateRequirement(1831, 1, 1) & BeforeDateRequirement(1837, 12, 31),
        7942: AfterDateRequirement(1901, 1, 1) & BeforeDateRequirement(1905, 12, 31),
    },

    'sir h cotton': {
        8284: NoRequirement(),
    },

    'mr gladstone': {
        3104: NoRequirement(),
    },

    'mr oconnell': {
        2552: NoRequirement(),
    },

    'mr white ridley': {
        7202: NoRequirement(),
    },

    'mr vesey fitzgerald': {
        2561: NoRequirement(),
    },

    'mr v fitzgerald': {
        2561: NoRequirement(),
    },

    'mr vernon harcourt': {
        3122: YearRequirement(1840),
        5172: AfterDateRequirement(1869, 1, 1) & BeforeDateRequirement(1873, 12, 31),
    },

    'mr thomas duncombe': {
        2438: NoRequirement(),
    },

    'mr t wilson': {
        2024: AfterDateRequirement(1819, 1, 1) & BeforeDateRequirement(1826, 12, 31),
    },

    'mr t shaw': {
        7261: NoRequirement(),
    },

    'mr t brassey': {
        4806: NoRequirement(),
    },

    'mr t baring': {
        337: NoRequirement(),
    },

    'sir william scott': {
        996: AfterDateRequirement(1803, 1, 1) & BeforeDateRequirement(1821, 12, 31),
    },

    'sir william molesworth': {
        2930: AfterDateRequirement(1853, 1, 1) & BeforeDateRequirement(1855, 12, 31),
    },

    'sir w lawson': {
        4614: AfterDateRequirement(1889, 1, 1) & BeforeDateRequirement(1899, 12, 31),
    },

    'sir stratford canning': {
        2549: AfterDateRequirement(1831) & BeforeDateRequirement(1838, 12, 31),
    },

    'sir s romilly': {
        1298: AfterDateRequirement(1808) & BeforeDateRequirement(1817, 12, 31),
    },
    'sir samuel romilly': {
        1298: AfterDateRequirement(1808) & BeforeDateRequirement(1817, 12, 31),
    },

    'sir s lushington': {
        1417: AfterDateRequirement(1839) & BeforeDateRequirement(1841, 12, 31),
    },

    'sir thomas acland': {
        3550: AfterDateRequirement(1872) & BeforeDateRequirement(1886, 12, 31),
    },

    'sir stafford northcote': {
        5686: AfterDateRequirement(1888) & BeforeDateRequirement(1889, 12, 31),
    },

    'sir r ferguson': {
        1046: AfterDateRequirement(1818) & BeforeDateRequirement(1839, 12, 31),
    },

    'sir m w ridley': {
        957: YearRequirement(1809),
        1803: AfterDateRequirement(1814) & BeforeDateRequirement(1832, 12, 31),
    },

    'sir joseph yorke': {
        1364: AfterDateRequirement(1812) & BeforeDateRequirement(1831, 12, 31)
    },
    'sir j yorke': {
        1364: AfterDateRequirement(1812) & BeforeDateRequirement(1831, 12, 31)
    },

    'sir john newport': {
        1127: AfterDateRequirement(1803) & BeforeDateRequirement(1832, 12, 31),
    },
    'sir j newport': {
        1127: AfterDateRequirement(1803) & BeforeDateRequirement(1832, 12, 31),
    },
    'sir john brydges': {
        2820: AfterDateRequirement(1823) & BeforeDateRequirement(1832, 12, 31),
    },
    'sir hussey vivian': {
        4304: AfterDateRequirement(1882) & BeforeDateRequirement(1892, 12, 31),
    },
    'sir henry fletcher': {
        5704: AfterDateRequirement(1881) & BeforeDateRequirement(1902, 12, 31),
    },
    'mr william smith': {
        981: AfterDateRequirement(1804) & BeforeDateRequirement(1831),
        7632: YearRequirement(1895),
    },
    
    'mr shaw lefevre': {
        1030: AfterDateRequirement(1808) & BeforeDateRequirement(1822),
        3007: AfterDateRequirement(1830) & BeforeDateRequirement(1834),
        3783: AfterDateRequirement(1876) & BeforeDateRequirement(1897),
    },
    
    'mr sharman crawford': {
        3325: NoRequirement(),
    },
    
    'mr scott dickson': {
        7953: NoRequirement(),
    },
    
    'mr russell rea': {
        7955: NoRequirement(),
    },
    'mr robert ward': {
        723: NoRequirement(),
    },
    'mr robert wallace': {
        3001: AfterDateRequirement(1833) & BeforeDateRequirement(1835),
        6262: YearRequirement(1899),
    },
    'mr r ward': {
        723: NoRequirement(),
    },
    'mr r palmer': {
        2368: NoRequirement(),
    },
    'mr r duncan': {
        8203: NoRequirement(),
    },
    'mr ormsby-gore': {
        7950: AfterDateRequirement(1901) & BeforeDateRequirement(1903),
        8472: YearRequirement(1910),
    },
}


def disambiguate(target: str, speechdate: datetime, house: int, debate_id: int, speaker_dict: Dict[int, SpeakerReplacement]) -> int:
    possibles = []

    function_dictionary = SpecificAliasFunctions.get(target)

    if function_dictionary is not None:
        for member_id, function in function_dictionary.items():
            if function(speechdate, house, debate_id):
                possibles.append(member_id)
    else:
        for member_id in DisambiguateFunctions.keys():
            if target in speaker_dict[member_id].aliases:
                if DisambiguateFunctions[member_id](speechdate, house, debate_id):
                    possibles.append(member_id)

    if len(possibles) == 1:
        return possibles[0]
    elif len(possibles) == 0:
        return -1
    else:
        # raise ValueError('Multiple results from disambiguation of: %s' % target)
        return -1
