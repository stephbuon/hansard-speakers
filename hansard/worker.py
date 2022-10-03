import multiprocessing
from queue import Empty
from typing import Tuple, Optional, List, Dict

import numpy

from hansard.disambiguate import disambiguate
from hansard.loader import DataStruct
from datetime import datetime
import pandas as pd
import re

from hansard.speaker import SpeakerReplacement
from util.edit_distance import within_distance_four, within_distance_two, is_distance_one


OUTPUT_COLUMN = 'suggested_speaker'

compile_regex = lambda x: (re.compile(x[0]), x[1])


REGEX_PRE_CORRECTIONS = [
    (r'(?:\([^()]+\))', ''), 
    # Remove all text within parenthesis, including parenthesis 
    ('Mr. Nicltolas Vansittart', 'Mr. Nicholas Vansittart'),
    ('The whole of Mr. Vansittart\'s', 'Mr. Vansittart'),
    ('SIR WILLTAM HARCOURT', 'SIR WILLLIAM HARCOURT'),
    ('SIR WILLIAM HARCOURTM', 'SIR WILLLIAM HARCOURT'),
    ('SRI WILLIAM HARCOURT', 'SIR WILLLIAM HARCOURT'),
    ('SIR WILLIAM HARCOURT )', 'SIR WILLLIAM HARCOURT'),
    ('SIR WILLIAM HARCOURT ()', 'SIR WILLLIAM HARCOURT'),
    ('SIR WILLIAM HARCOURT ( )', 'SIR WILLLIAM HARCOURT'),
    ('Ma. LLOYD - GEORGE', 'Mr. LLOYD-GEORGE'),
    ('(Answered by Mr. Lloyd-George. )', 'Mr. LLOYD-GEORGE'),
    ('The Hon. F. Robinson', 'F. Robinson'),
    ('The Hon. Frederick Robinson', 'Frederick Robinson'),
    ('By Mr. Robinson.', 'Mr. Robinson'),
    ('By Mr. Robinson.', 'Mr. Robinson'),
    ('Mr. Herries explained,', 'Mr. Herries'),
    ('Mr. Goulbum', 'Mr. Goulburn'),
    ('Mr. Goulbum', 'Mr. Goulburn'),
    ('Mr. Goulbourne', 'Mr. Goulburn'),
    ('LOUD DENMAN (who had some difficulty in obtaining a hearing)', 'Lord Denman'),
    ('LORD DENMAN (who was very imperfectly heard)', 'Lord Denman'),
    ('Lord Denman (the Speaker)', 'Lord Denman'),
    ('LORD DENMAN (not having heard the speech of the noble Marquess)', 'Lord Denman'),
    ('Fraticis Baring', 'Francis Baring'),
    ('DR. RUTHERFOORD-HARRIS', 'MR. RUTHERFORD-HARRIS'),
    ('DR. RUTHERFOORD-HARRIS', 'MR. RUTHERFORD-HARRIS'),
    ('CLNINGHAME GRAHAM', 'CUNNINGHAME GRAHAM'),
    ('COUETENAY WAENEE', 'COURTENAY AVENUE'),
    ('DISKAELI', 'DISRAELLI'),
    ('DR.EARQUHARSON', 'DR. FARQUHARSON'),
    ('EARL BEATJCHAMP', 'EARL BEAUCHAMP'),
    ('LORD HERSGHELL', 'LORD HERSCHEL'),
    ('SIR CHAELE8 W. DILKE', 'SIR CHARLES W. DILKE'),
    ('VVASON', 'WASON'),
    ('CATAIAN. BETHFLL', 'CAPTAIN BETHELL'),
    ('CCNINGHAME GRAHAM', 'Cunninghame Graham'),
    ('CHICLTESTER FORTESCUE', 'CHICHESTER FORTESCUE'),
    ('Clninghame Graham', 'Cunninghame Graham'),
    ('Colonel Vercker', 'Colonel Parker'),
    ('COUETENAY WAENEE', 'Courtenay Wayne'),
    ('DR.EARQUHARSON', 'DR. FARQUHARSON'),
    ('EARL BEATJCHAMP', 'Earl Beauchamp'),
    ('Earl Conyngham', 'Earl Cunningham'),
    ('Earl Of Malmesbtjry', 'Earl of Malmesbury'),
    ('FER-GUSSOX', 'FERGUSSON'),
    ('H.C RICHAKDS', 'H. C. Richards'),
    ('HIE BXCHEQUER', 'THE EXCHEQUER'),
    ('HIE BXCHEQUER (the Exch…)', 'THE EXCHEQUER'),
    ('IHE TREASURY (change to The Treasury)', 'THE TREASURY'),
    ('J. POWELL - WILLIAMS', 'J.Powell-Williams'),
    ('KNATCHBITLL-HUGESSEN', 'KNATCHBULL-HUGESSEN'),
    ('Knatchboll-hu-gessen', 'Knatchbull-Hugessen'),
    ('Lord Casdereagh', 'Lord Castlereagh'),
    ('Lord Elph1nston', 'Lord Elphinstone'),
    ('LORD or THE (lord of the)', 'LORD OF THE'),
    ('MACLIVEE', 'MACFIE'),
    ('Mr. Abereromby', 'Mr. Abercrombie'),
    ('MR. B. SAMTTELSON', 'MR. B. SAMUELSON'),
    ('MR. BRADLAITGH', 'MR. BRADLAUGH'),
    ('Mr. Brougkam.', 'Mr.Brougham'),
    ('Mr. Btoughtam.', 'Mr. Brougham'),
    ('Mr. Btoughtam.', 'Mr. Brougham'),
    ('Mr. Buttertvorth', 'Mr. Butterworth'),
    ('MR. CCNINGHAME GRAHAM', 'MR. CUNNINGHAME GRAHAM'),
    ('MR. CDNINGHAME GRAHAM', 'MR. CUNNINGHAME GRAHAM'),
    ('MR. CLNLNGHAME GRAHAM', 'MR. CUNNINGHAME GRAHAM'),
    ('MR. COLLLNTGS', 'MR. COLLINGS'),
    ('Mr. Conusgham', 'Mr. Cunningham'),
    ('MR. CUNENGHAME GRAHAM', 'MR. CUNNINGHAME GRAHAM'),
    ('MR. CUNLNGHAME GRAHAM', 'MR. CUNNINGHAME GRAHAM'),
    ('MR. CUNUSTGHAME GRAHAM', 'MR. CUNNINGHAME GRAHAM'),
    ('MR. DISKAELI (disraeli ??)', 'MR. DISRAELI'),
    ('Mr. G. Jahnstone', 'Mr. G. Johnson'),
    ('MR. HBADLAM', 'MR. BEDLAM'),
    ('MR. KNATCHBOLL-HU-GESSEN', 'MR. KNATCHBULL-HUGESSEN'),
    ('Mr. Marrryatt', 'Mr. Marriott'),
    ('Mr. Nicltolas Vansittart', 'Mr. Nicholas Vansittart'),
    ('MR. O\'KFEFFE', 'MR. O\'KEEFE'),
    ('MR. SYDNEY GBDGE', 'MR. SYDNEY BRIDGE'),
    ('MR. T. M.\'HEALY', 'MR. TIM HEALY'),
    ('MR. TCITE', 'MR. SITE'),
    ('MR. W. E. FOPSTER', 'MR. W. FORSTER'),
    ('SECRETARY OF STATE FOE INULA', 'SECRETARY OF STATE FOR INDIA'),
    ('SECRETARY OF STATE FOII WAR', 'SECRETARY OF STATE FOR WAR'),
    ('SIR BALDWYNLEIGHTON', 'SIR BALDWIN LEIGHTON'),
    ('SIR CHAELE8 W. DILKE', 'SIR CHARLES W. DILKE'),
    ('Sir Chaele8 W. Dilke', 'Sir. Charles W. Dilke'),
    ('Sir F. Burdctt', 'Sir F. Burdell'),
    ('Sir F. Burdctt (change this to Burdell)', 'Sir F. Burdell'),
    ('SIR J. EERGUSSON', 'Sir J. Ferguson'),
    ('SIR J. FERGDSSON', 'SIR J. FERGUSON'),
    ('SIR J. FERGUSSOH', 'SIR J. FERGUSON'),
    ('SIR J. FERGUSSOX', 'SIR J. FERGUSON'),
    ('SIR J. PERGUSSON', 'SIR J. FERGUSON'),
    ('Sir John Anslrutlter', 'Sir John anstruther'),
    ('Sir O. Moselcy', 'Sir O. Mosley'),
    ('Sir O. Moseley or Sir O. Mosley (which one is correct?)', 'Sir O. Mosley'),
    ('STATE FOB THE COLONIES (change to for)', 'STATE FOR THE COLONIES'),
    ('The Chan. of the Exchequer', 'The Chancellor of the Exchequer'),
    ('The Chanc. of the Exchequer', 'The Chancellor of the Exchequer'),
    ('The Chanc. of tie Excheq.', 'The Chancellor of the Exchequer'),
    ('The Chancellar the Exchequer', 'The Chancellor of the Exchequer'),
    ('The Earl of Westn Oreland', 'The Earl of West Ireland'),
    ('The Marquis of Buckinghnm', 'The Marquess of Buckingham'),
    ('The Marquis of Lans-downe', 'Marquess of Lansdowne'),
    ('The Marquis of Lansdownne', 'Marquess of Lansdowne'),
    ('THE UNDERSECRETARY or STATE FOR FOREIGN AFF AIRS (change to the under secretary of state for foreign affairs)', 'the under secretary of state for foreign affairs'),
    ('VICE-PRESIDE VT OF THE DEPARTMENT OF AGRICULTURE FOR IRELAND', 'VICE-PRESIDENT OF THE DEPARTMENT OF AGRICULTURE FOR IRELAND'),
    ('VVASON', 'Wason'),
    ('ZOUCHE OF HARYNG-WORTH', 'ZOUCHE OF HARRINGWORTH'),
    ('CAMP BELL-BANNERMAN', 'CAMPBELL-BANNERMAM'),
    ('CAMPBELL-BANNER-MAN', 'CAMPBELL-BANNERMAM'),
    ('Devoriport', 'Devonport'),
    ('DR. MACNAAIARA', 'DR. MCNAMARA'),
    ('DR. MACNAMARDR.', 'DR. MCNAMARA'),
    ('DR. MACNAMRA', 'DR. MCNAMARA'),
    ('EARL or HALSBCJRY', 'EARL OF HALSBURY'),
    ('EDMUND FITLMALURICE', 'EDMUND FITZMAURICE'),
    ('FOR FOREIGN Ar FAIRS', 'FOR FOREIGN AFFAIRS'),
    ('HAYKS FISHER', 'HANS FISHER'),
    ('LOEDBISHOP OF HEREFORD', 'LORD BISHOP OF HEREFORD'),
    ('LoRD CHANBORNE', 'LORD CRANBOURNE'),
    ('LORD CRAN-BORNE', 'LORD CRANBOURNE'),
    ('LORD EDMUNDFITZMAITRICE', 'LORD EDMUND FITZMAURICE'),
    ('LORD TWKKDMOGTH', 'LORD TWEEDMOUTH'),
    ('MARQUESS or LONDONDEUX', 'MARQUESS OF LONDONDERRY'),
    ('Morimouthshire', 'Monmouthshire'),
    ('MR. ALFRED IIUTTON', 'MR. ALFRED SUTTON'),
    ('MR. BKODRICK', 'MR. BRODERICK'),
    ('MR. HABMSWOBTH', 'MR. HEMSWORTH'),
    ('MR. HERBEIIT ROBERTS', 'MR. HERBERT ROBERTS'),
    ('MR. LLYOD-GEOEGE', 'MR. LLOYD-GEORGE'),
    ('MR. M c C R A E', 'MR. MCRAE'),
    ('MR. M c C R A E', 'MR. MCRAE'),
    ('Mr. PBETYMAN', 'Mr. PRETTYMAN'),
    ('Mr. PNETYMAN', 'Mr. PRETTYMAN'),
    ('MR. RUNCINIAN', 'Mr. RUNCIMAN'),
    ('MR.EAMENDROBERTSON', 'MR. EDMUND ROBERTSON'),
    ('MR.JOHN BURNS(Battersea)', 'MR. JOHN BURNS'),
    ('SIR A. ACLAND-HOOD (Somersetshire', 'SIR A. ACLAND-HOOD'),
    ('SIR GEORGE BAETLEY', 'SIR GEORGE BAILEY'),
    ('SIR H. CAMPBELLBAN-NERMAN', 'SIR H. CAMPBELL-BANNERMAN'),
    ('SIR. MANCHEEJEE BHOWNAGGREE', 'SIR. MANCHERJEE BHOWNAGREE'),
    ('THE ADMIL ALTY', 'THE ADMIRALTY'),
    ('THE CHIEF SECRETARY Foil IRELAND', 'THE CHIEF SECRETARY FOR IRELAND'),
    ('TWEEDMOITTH', 'TWEEDMOUTH'),
    ('UNDER-SECRETARy ofSTATE FOR', 'UNDER SECRETARY OF STATE FOR'),
    ('COEIUE GRANT', 'CORINNE GRANT'),
    ('DR. MACNAMAHA', 'DR. MCNAMARA'),
    ('DR. MACXAMAEA', 'DR. MCNAMARA'),
    ('LORD BALFOUROFBUELEIGH', 'LORD BALFOUR OF BURLEIGH'),
    ('LORD EDMUND FITZ-MAUBICE', 'LORD EDMUND FITZMAURICE'),
    ('MAONAMARA', 'MCNAMARA'),
    ('MR. CHARLES HOBIIOUSE', 'MR. CHARLES HOBHOUSE'),
    ('MR. GUTIIRIE', 'MR. GUTHRIE'),
    ('MR. LAMBTOX (change to Lambton)', 'MR. LAMBTON'),
    ('MR. M\'GOVKRN', 'MR. MCGOVERN'),
    ('CAMPBELL-BAN HERMAN', 'CAMPBELL-BANNERMAN'),
    ('STANLEY OFALDEKLEY', 'STANLEY ALDERLEY'),
    ('EARL CARMNGTON', 'EARL CARRINGTON'),
    ('Mr. CRKMEE', 'Mr. CLARKE'),
    ('MR. COREIE GRANT', 'MR. COREY GRANT'),
    ('EARL OF DONOCJGHMORE', 'EARL OF DONOUGHMORE'),
    ('MAJOR ANSTRUTIIER-GRAY', 'MAJOR ANSTRUTHER-GRAY'),
    ('MR. B E R T R A M', 'MR. BERTRAM'),
    ('A. J.BALPOUR', 'A. J. BALFOUR'),
    ('HERSCHBLL', 'HERSCHEL'),
    ('SIR HENRY HOWORTH(Salford', 'SIR HENRY HOWARTH (Salford'),
    ('HENEAUE', 'HEANUE'),
    ('STATE ROR THE COLONIES', 'STATE FOR THE'),
    ('DEPUTY-CHAIR M AN', 'DEPUTY CHAIRMAN'),
    ('SIR FBEDEEICK BANBUEY', 'SIR FREDERICK BANBURY'),
    ('ASQTJITH', 'ASQUITH'),
    ('POSTMASTER - GENERA', 'POSTMASTER GENERAL'),
    ('CHARLES SCHWANX', 'CHARLES SCHWAB'),
    ('Mr. BROURICK', 'Mr. BRODERICK'),
    ('Mr. BKODRICK', 'Mr. BRODERICK'),
    ('BEODRICK', 'BRODERICK'),
    ('Earl of DONOUOH-MORE', 'Earl of DONOUGHMORE'),
    ('AKERS- DOUWLAS', 'AKERS DOUGLAS'),
    ('Mr. PEETYMAN', 'Mr. PRETTYMAN'),
    ('MR. FETIIERSTONHAUGH', 'MR. FETHERSTONHAUGH'),
    ('MR. WHITTAKEK', 'Mr. Whitaker'),
    ('MR. BAULTON', 'Mr. Bolton'),
    ('MR. BEODRIGK', 'Mr. Broderick'),
    ('MR. CHARLES M\'AETHUR', 'Mr. Charles McArthur'),
    ('MANCHERJEE BHOWNAGGEEE', 'Mancherjee Bhownagree'),
    ('CHRISTOPHER FTJRNESS', 'Christopher Furness'),
    ('SIR FORTESCTJE FLANNERY', 'Sir. Fortescue Flannery'),
    ('SIR WTLLIAM TOMLINSON', 'Sir William Tomlison'),
    ('GRIFFITH BOSOAWEN', 'Arthur Griffith-Boscawen'),
    ('CAMPBEEL-BANNEERMAN', 'Campbell-Bannerman'),
    ('CHANCELLOR OF THE EN-CHEQUER', 'Chancellor of the Exchequer'),
    ('FEEGUSSON', 'Ferguson'),
    ('FEE-GUSSON', 'Ferguson'),
    ('FERGHSSON', 'Ferguson'),
    ('FERGHSSON', 'Ferguson'),
    ('FERGUS-IRON', 'Ferguson'),
    ('MANCHERJEE BHOWKAGGREE', 'Mancherjee Bhownagree'),
    ('MANCHERJEE BHOWNAG-GREK', 'Mancherjee Bhownagree'),
    ('SECRETAEY (secretary)', 'Secretary'),
    ('SECRETARY FOE IRE LAND', 'Secretary for Ireland'),
    ('SECRETARY for IRE', 'Secretary for Ireland'),
    ('SECRETARY OF ST ATE FOR WAR', 'Secretary of State'),
    ('SECRETARY OF STALE', 'Secretary of State for War'),
    ('SECRETARY OK STATE FOR FOREIGN', 'Secretary of State for Foreign Affairs'),
    ('SECRETARY TO TILE TREASURY', 'Secretary to the Treasury'),
    ('SIR CHARLKS DILKE', 'Sir Charles Dike'),
    ('LOED (change to lord)', 'Lord'),
    ('BOAED (change to board)', 'board'),
    ('STATE FOR AVAR', 'State for War'),
    ('PRESIDENT or THE (change to of)', 'President of the'),
    ('TIIE COMMITTEE', 'The Committee'),
    ('MR. T. L. COKBETT', 'Mr. T.L. Corbett'),
    ('MR. T. L. COEBETT', 'Mr. T.L. Corbett'),
    ('PBESIDENT OF THE BOARD OFTRADE', 'President of the Board of Trade'),
    ('O\'SHATHGHNESSY', 'O\'Shaughnessy'),
    ('O\'SIIAUGHNESSY', 'O\'Shaughnessy'),
    ('THE MARQUESS OF LANSDOVVNE', 'The Marquess of Lansdowne'),
    ('THE CHANCELLOR OF THE EX', 'The Chancellor of the Exchequer'),
    ('FORTESCIJE FLANNERY', 'Fortescue Flannery'),
    ('STATE FOB (change to state for)', 'State for'),
    ('TEXNANT (tennant)', 'tennant'),
    ('STATE FOR AVAR (change to war)', 'State for War'),
    ('UNDEB SECBETAEY of STATE FOR WAR', 'Under Secretary of State for War'),
    ('VICE-PEESIDENT OF THE BOAED of EDUCATION', 'Vice President of the Board of Education'),
    ('PRYCE-JONES (make look like PRYCE - JONES)', 'Pryce - Jones'),
    ('EARL BEATJCHAMP', 'Earl Beauchamp'),
    ('THE MARCHESS OE SALISBURY', 'The Marches of Salisbury'),
    ('MR. LABOITCHERE', 'Mr. Labouchre'),
    ('ATTOENEY-GENERA', 'Attorney General'),
    ('ATTORNE-GENERAL', 'Attorney General'),
    ('MR. VICARYGIBBSMR.', 'Mr. Vicary Gibbs'),
    ('GIBSON BOAVLES', 'Gibson Bowles'),
    ('ARNOLD - FORSTEE', 'Arnold-Forster'),
    ('OF:STATE FOE WAR', 'of State for War'),
    ('PAELIAMENTARY SECRETARY', 'Parliamentry Secretary'),
    ('BISHOP OF WINCHES TER', 'Bishop of Manchester'),
    ('SECEETAEY TO THE ADMIE-ALTY', 'Secretary to the Admiralty'),
    ('MEMEBER (change to member)', 'member'),
    ('MARQUESS or LONDON-DERRY', 'The Marquess of Londonderry'),
    ('EOBEET FINLAY', 'Robert Einlay'),
    ('ROBERT F1NLAY', 'Robert Einlay'),
    ('COUNCIL ON EDU-', 'Council of Education')
    
]

PARENTHESIS_REGEX = re.compile(r'(?:\(([^()]+)\))')


REGEX_PRE_CORRECTIONS = list(map(compile_regex, REGEX_PRE_CORRECTIONS))

REGEX_POST_CORRECTIONS = [

    # Regex for misspelled leading the
    ('^this +', 'the '),
    ('^thr +', 'the '),
    ('^then +', 'the '),
    ('^tee +', 'the '),
    ('^thh +', 'the '),
    ('^tue +', 'the '),
    ('^tmk +', 'the '),
    ('^tub +', 'the '),
    ('^he +', 'the '),
    ('^tim +', 'the '),
    ('^tme +', 'the '),
    ('^tihe +', 'the '),
    ('^thk +', 'the '),
    ('^thb +', 'the '),
    ('^tre +', 'the '),
    ('^tile +', 'the '),
    ('^tiie +', 'the '),
    ('^t he +', 'the '),

    ('^the +', ''),  # Remove leading "the"

    ('^me +', 'mr '),  # Leading me -> mr
    ('^mb +', 'mr '),
    ('^mer +', 'mr '),
    ('^mh +', 'mr '),
    ('^mil +', 'mr '),
    ('^mk +', 'mr '),
    ('^mp +', 'mr '),
    ('^ma +', 'mr '),
    ('^mi +', 'mr '),
    ('^mk +', 'mr '),
    
    ('^m r +', 'mr '),  # Fix leading spaced out mr
    
    ('^dir +', 'dr '),
    ('^dk +', 'dr '),
    ('^de +','dr '),
    
    ('^vick +','vice '),
    
    (' image srcsvpi colcol', ''),
    
    ('^marquis +', 'marquess '),
    ('^marqess +', 'marquess '),
    ('^mauquess +', 'marquess '),
    ('^manquess +', 'marquess '),
    ('^marguess +', 'marquess '),
    ('^marquees +', 'marquess '),
    ('^marques +', 'marquess '),
    ('^marquese +', 'marquess '),
    ('^marquese +', 'marquess '),
    ('^marquesss +', 'marquess '),
    ('^mabquess +', 'marquess '),
    ('^maeqttess +', 'marquess '),
    ('^maequess +', 'marquess '),
    ('^marqdess +', 'marquess '),
    ('^marqiess +', 'marquess '),
    ('^marqtjess +', 'marquess '),
    ('^manquess +', 'marquess '),
    ('^marguess +', 'marquess '),
    ('^marquees +', 'marquess '),
    ('^marques +', 'marquess '),
    ('^marquese +', 'marquess '),
    ('^marquese +', 'marquess '),
    
    ('^vicount +', 'viscount '),
    ('^viscovnt +', 'viscount '),
    ('^vicsount +', 'viscount '),
    ('^vis- count +', 'viscount '),
    ('^viscocnt +', 'viscount '),
    ('^viscodnt +', 'viscount '),
    ('^viscolunt +', 'viscount '),
    ('^viscotint +', 'viscount '),
    ('^viscotjnt +', 'viscount '),
    ('^viscouint +', 'viscount '),
    ('^viscoun +', 'viscount '),
    ('^viscouxt +', 'viscount '),
    ('^viscwnt +', 'viscount '),
    ('^visoount +', 'viscount '),
    ('^vtscount +', 'viscount '),
    ('^viscuont +', 'viscount '),
    ('^viscoust +', 'viscount '),
    ('^viscounty +', 'viscount '),
    ('^visct +', 'viscount '),
    ('^lord viscount +', 'viscount '),
    
    ('^lord speaker +', 'speaker '),

    ('^lerd +', 'lord '),
    ('^lard +', 'lord '),
    ('^loed +', 'lord '),
    ('^loro +', 'lord '),
    ('^loud +', 'lord '),
    ('^lort +', 'lord '),
    ('^loup +', 'lord '),
    ('^lobd +', 'lord '),
    ('^loan +', 'lord '),
    ('^load +', 'lord '),
    ('^lokd +', 'lord '),
    ('^lold +', 'lord '),
    ('^lore +', 'lord '),
    ('^lorn +', 'lord '),
    ('^lorrd +', 'lord '),
    ('^lors +', 'lord '),
    ('^losd +', 'lord '),
    ('^lose +', 'lord '),
    ('^lour +', 'lord '),
    ('^lrd +', 'lord '),
    ('^ord +', 'lord '),

    ('^earb +', 'earl '),
    ('^ear +', 'earl '),
    ('^ealr +', 'earl '),
    ('^eari +', 'earl '),
    ('^eaul +', 'earl '),
    ('^early +', 'earl '),
    ('^east +', 'earl '),
    ('^eeal +', 'earl '),
    ('^arl +', 'earl '),
    ('^eahl +', 'earl '),
    ('^eael +', 'earl '),
    ('^eakl +', 'earl '),
    ('^eard +', 'earl '),
    ('^eall +', 'earl '),
    ('^eart +', 'earl '),
    ('^farl +', 'earl '),

    ('^dike +', 'duke '),
    ('^duek +', 'duke '),
    ('^ducke +', 'duke '),
    ('^duck +', 'duke '),
    
    ('^chamberlatn +', 'chamberlain '),
    
    # Fix leading Sir
    ('^sib +', 'sir '),
    ('^sin +', 'sir '),
    ('^sit +', 'sir '),
    ('^sip +', 'sir '),
    ('^siu +', 'sir '),
    ('^sik +', 'sir '),
    ('^sat +', 'sir '),
    ('^sie +', 'sir '),
    ('^silt +', 'sir '),
    ('^sri +', 'sir '),
    ('^sr +', 'sir '),
    ('^str +', 'sir '),
    ('^air +', 'sir '),
    ('^si +', 'sir '),
    ('^sdi +', 'sir '),
    ('^slr +', 'sir '),
    
    ('^abmiral +', 'admiral '),
    ('^admtral +', 'admiral '),
    ('^admieal +', 'admiral '),
    ('^abmiral +', 'admiral '),
    ('^admiraj +', 'admiral '),
    ('^admibal +', 'admiral '),
    
    ('^admtralty +', 'admiralty '),
    ('^adralty +', 'admiralty '),
    ('^admihalty +', 'admiralty '),
    ('^ad-jmiralty +', 'admiralty '),
    ('^admil alty +', 'admiralty '),
    ('^admir alty +', 'admiralty '),
    
    ('^trea-iury +', 'treasury '),
    ('^trea-treasury +', 'treasury '),
    ('^treastry +', 'treasury '),
    ('^trea sury +', 'treasury '),
    
    ('^cafiain +', 'captain '),
    ('^caftain +', 'captain '),
    ('^caitain +', 'captain '),
    ('^capain +', 'captain '),
    ('^capatain +', 'captain '),
    ('^capiain +', 'captain '),
    ('^capt +', 'captain '),
    ('^vaptain +', 'captain '),
    
    ('^col +', 'colonel '),
    ('^colconel +', 'colonel '),
    ('^coionel +', 'colonel '),
    ('^colnel +', 'colonel '),
    ('^colokel +', 'colonel '),
    ('^colonal +', 'colonel '),
    ('^colonbl +', 'colonel '),
    ('^coloxel +','colonel '),
    ('^colonl +','colonel '),
    ('^colosel +','colonel '),
    ('^colonei +','colonel '),
    
    ('^eirst +', 'first '),
    ('^fiest +', 'first '),
    
    ('^archblsiiop +','archbishop '),
    
    ('^bistiop +', 'bishop '),
    ('^bisliop +', 'bishop '),
    ('^bisiiop +', 'bishop '),
    ('^bistiop +', 'bishop '),
    ('^lord bishop +', 'bishop '),
    
    ('^atiorney +', 'attorney'),
    ('^attornby +', 'attorney'),
    ('^attorne +', 'attorney'),
    ('^attorney- +', 'attorney'),
    
    ('^ge neral  +', 'general '),
    ('^gen  +', 'general '),
    ('^genebal  +', 'general '),
    ('^generai  +', 'general '),
    ('^genekal  +', 'general '),
    ('^genenal  +', 'general '),
    ('^genera  +', 'general '),
    ('^gexeral  +', 'general '),
    ('^geneeal  +', 'general '),
    ('^gen  +', 'general '),
    
    ('^solioitor +', 'solicitor '),
    ('^solicttor +', 'solicitor '),
    ('^solioitor +', 'solicitor '),
    
    ('peivy', 'privy'),
    
    ('chanoellor', 'chancellor'),
    
    ('chancellor of the e xciiequer', 'chancellor of the exchequer'),
    ('chancellor of the exchequer-chequer', 'chancellor of the exchequer'),
    ('changellor of the exche-quer', 'chancellor of the exchequer'),
    ('chancellor the exchequee', 'chancellor of the exchequer'),
    ('chancellor of theexche-quer', 'chancellor of the exchequer'),
    ('chancellor of we exchequer', 'chancellor of the exchequer'),
    ('cbancellor of the exche-quer', 'chancellor of the exchequer'),
    ('^chan of the exchequer$', 'chancellor of the exchequer'),
    ('^chancellor the exchequee$', 'chancellor of the exchequer'),
    ('^chanc of the excheq$', 'chancellor of the exchequer'),
    ('^chancellok of the exche-quek$', 'chancellor of the exchequer'),
    ('^chancellor of the exchequerchequer$', 'chancellor of the exchequer'),
    ('^chanc of the exchequer$', 'chancellor of the exchequer'),
    ('^chanc of the exchequer$', 'chancellor of the exchequer'),
    ('^chancelloe of the exche-quer$', 'chancellor of the exchequer'),
    ('^chanc of tie excheq$', 'chancellor of the exchequer'),
    ('^chanckllor of the exchequer$', 'chancellor of the exchequer'),
    ('^chancellor of file exchequer$', 'chancellor of the exchequer'),
    ('^chancelloerof the exche-quer$', 'chancellor of the exchequer'),
    ('^chancelloe of the ex-chequee$', 'chancellor of the exchequer'),
    ('^chancelloe of the exchequer$', 'chancellor of the exchequer'),
    ('^chancellor of the ex-cheqner$','chancellor of the exchequer'),
    ('^chancellor ok the exchequerr$','chancellor of the exchequer'),
    ('^chancellor of tub exchequerr$','chancellor of the exchequer'),
    ('^chancellor ok thk exchequerr$','chancellor of the exchequer'),
    ('^chancellob of the exchequerr$','chancellor of the exchequer'),
    ('^chancelor of the exchequerr$','chancellor of the exchequer'),
    ('^chancelloe of the exche-quer$','chancellor of the exchequer'),
    ('^the chan. of the exchequer$','chancellor of the exchequer'),
    ('^the chanc. of the exchequer$','chancellor of the exchequer'),
    ('^the chancellar the exchequer$','chancellor of the exchequer'),
    ('^the chancellor if the exchequer$','chancellor of the exchequer'),
    ('^the Chancellor of die exchequer$','chancellor of the exchequer'),
    ('^the chancellor of tie exchequer$','chancellor of the exchequer'),
    ('^chanc. of tie excheq.$','chancellor of the exchequer'),
    
    ('ex-chequer', 'exchequer'),
    ('excheque', 'exchequer'),
    ('hie bxchequer', 'exchequer'),
    
    ('mrjor', 'major'),
    
    ('^chairman of ways achancellor of tub exchequerrnd means$', 'chairman'),
    ('^chairman ways and means$', 'chairman'),
    ('^chat rman of ways and means$', 'chairman'),
    ('^ghairman of ways and means$', 'chairman'),
    ('^chairman airman of ways and means$', 'chairman'),
    ('^chairman of wats and means$', 'chairman'),
    ('^chairman of ways and means$', 'chairman'),
    ('^chairman of was and means$', 'chairman'),
    ('^chairman ways and means$', 'chairman'),
    ('^chat rman of ways and means$', 'chairman'),
    ('^chairman airman of ways and means$', 'chairman'),
    
    ('^chairman of committees of ways and means$', 'chairman'),
    
    ('^chairman of committees$', 'chairman'),
    ('^chairman of commhtees$', 'chairman'),
    ('^chairman of commitmees$', 'chairman'),
    
    ('^ceairman$', 'chairman'),
    ('^mr chairman$', 'chairman'),
    ('^ceairman$', 'chairman'),
    ('^chair man$', 'chairman'),
    
    ('speaker-elect', 'speaker'),
    
    ('memberconstituencymemberconstituency', ''), # is this necessary? Seems this pattern has been removed elsewhere. Check with Alexander. 
    
    ('^a +', ''),
    ('^and +', ''),
    ('^answered by +', ''),
    ('^another +', ''),
    ('^both +', ''),
    ('^by +', ''),
    ('^here +', ''),
    
    (' on$', ''),
    (' said$', ''),
    (' ampc$', ''),
    ('ampc$', ''),
    (' i$', ''),
    (' replied$', ''),
    (' continued$', ''),
    (' presumed$', ''),
    (' resumed$', ''),
    (' resuming$', ''),
    (' also$', ''),
    (' felt$', ''),
    
    (' avar$', ' war'),

    ('irelandland', 'ireland'),

    (' tiie ', ' the '),
    (' tile ', ' the '),

    (' de ', ' of '),
    (' oe ', ' of '),
    (' uf ', ' of '),
    (' op ', ' of '),
    (' or ', ' of '),
    (' ov ', ' of '),
    
    (' fob ', ' for '),
    (' foe ', ' for '),
    (' toe ', ' for '),
    
    (' statf ', ' state '),
    
    (' boaed ', ' board '),
    
    (' statf$', ' state$'),

    ('under +secretary', 'under-secretary'),
    ('under +- +secretary', 'under-secretary'),

    ('secketay +','secretary'),

    (r'lieutenant[\- ]?colonel +', ''),
    (r'lieut(.*)col', ''),
    (r'lieut', ''),
    
    ('^the hon ', ''),
    
    ('memberconstituency', ''),

    (r'^right hon +', ''),
    (r' +observed$', ''),

    ('^general sir +', 'sir '),
    ('^mr secretary +', 'mr '),

    ('^vice-president of the council +', 'vice-president of the committee of council on education'),
    ('^vice president of the council +', 'vice-president of the committee of council on education'),
    ('^the vice president of the council +', 'vice-president of the committee of council on education'),

    ('^secretary of state for war +', ''),
    ('^president of the local government board +', ''),
    ('^president of the board of agriculture +', ''),
    ('^president of the board of trade +', ''),
    ('^secretary of state for the home department +', ''),
    ('^secretary of state for the colonies +', ''),
    ('^secretary to the treasurey +', ''),
    ('^first commissioner of works +', ''),
    ('^secretary to the admiralty +', ''),
    ('^secretary of state for india +', ''),
    ('^secretary to the local government board +', ''),
    ('^parliamentary secretary to the local government board +', ''),

    ('^-attorney', 'attorney'),
    ('^mr attorney-?general', 'attorney-general'),
    ('^she attorney', 'attorney'),
    ('^attorney-?general sir [a-z ]+', 'attorney-general'),

    # Fix hyphen surrounded by spaces.
    (' + - +', '-'),

    # Remove words preceding a title word such as (viscount, sir, mr):
    ('^.+ viscount', 'viscount'),
    ('^.+ sir ', 'sir '),
    ('^.+ mr ', 'mr '),


]

REGEX_POST_CORRECTIONS = list(map(compile_regex, REGEX_POST_CORRECTIONS))

IGNORE_KEYWORDS = (
    #'member',
    #'membee',
    #'membek',
    #'evicted tenant',
    #'voice',
    #'british statesman',
    #'bishop',
    #'archbishop',
    #'this parliament'
)

IGNORE_PREFIXES = (
    'mrs ',
    'miss ',
    'a ',
    'an ',
)


def is_ignored(target: str) -> bool:
    if len(target) < 35:  # temp check: some speaker column values contain debate text
        for kw in IGNORE_KEYWORDS:
            if kw in target:
                return True
        for kw in IGNORE_PREFIXES:
            if target.startswith(kw):
                return True

    return False


def match_term(df: pd.DataFrame, date: datetime) -> pd.DataFrame:
    return df[(date >= df['start_search']) & (date < df['end_search'])]


def match_edit_distance_df(target: str,  date: datetime, df: pd.DataFrame,
                           columns: Tuple[str, str, str], speaker_dict: Dict[int, SpeakerReplacement],
                           edit_dist_func=within_distance_two) -> Tuple[Optional[str], bool, List[str]]:
    start_col, end_col, search_col = columns

    match = None
    ambiguity = False
    possibles = []
    max_possibles = 5

    condition = (date >= df[start_col]) & (date < df[end_col])
    query = df[condition]

    for i, alias in enumerate(query[search_col]):
        if edit_dist_func(target, alias, False):
            if match:
                ambig_match = query.iloc[i]['corresponding_id']
                if numpy.isnan(ambig_match):
                    ambig_match = alias
                else:
                    ambig_match = speaker_dict[int(ambig_match)]
                max_possibles -= 1
                match = None
                ambiguity = True
                possibles.append(ambig_match)
                if not max_possibles:
                    break
            else:
                match = query.iloc[i]['corresponding_id']
                if numpy.isnan(match):
                    match = alias
                else:
                    match = speaker_dict[int(match)]
                # print('edit distance found. target=%s match=%s' % (target, repr(match)))

    return match, ambiguity, possibles


from util.jaro_distance import jaro_distance


def find_best_jaro_dist_df(target: str, df: pd.DataFrame, speechdate: datetime, curr_best, col: str, date_start_col='start_search',
                           date_end_col='end_search'):
    condition = (speechdate >= df[date_start_col]) & \
                (speechdate < df[date_end_col])
    query = df[condition]

    for row in query.itertuples(index=False):
        dist = jaro_distance(target, getattr(row, col))
        if dist > curr_best[1]:
            curr_best = [getattr(row, col), dist]
    return curr_best


def find_best_jaro_dist(target: str, alias_dict: Dict[str, List[SpeakerReplacement]],
                        honorary_title_df: pd.DataFrame,
                        lord_titles_df: pd.DataFrame,
                        aliases_df: pd.DataFrame,
                        speechdate: datetime):
    best_match = ['', 0.0]

    best_match = find_best_jaro_dist_df(target, honorary_title_df, speechdate, best_match, 'honorary_title',
                                        'start_search', 'end_search')
    best_match = find_best_jaro_dist_df(target, lord_titles_df, speechdate, best_match, 'alias')
    best_match = find_best_jaro_dist_df(target, aliases_df, speechdate, best_match, 'alias')

    for alias in alias_dict:
        dist = jaro_distance(target, alias)
        if dist > best_match[1]:
            possibles = alias_dict[alias]
            possibles = [speaker for speaker in possibles if speaker.matches(target, speechdate, cleanse=False)]
            if len(possibles) == 1:
                best_match = [alias, dist]

    return best_match


# This function will run per core.
def worker_function(inq: multiprocessing.Queue,
                    outq: multiprocessing.Queue,
                    data: DataStruct):
    from . import cleanse_string

    # Lookup optimization
    misspellings_dict = data.corrections
    alias_dict = data.alias_dict
    terms_df = data.term_df
    speaker_dict = data.speaker_dict
    honorary_title_df = data.honorary_titles_df
    office_title_dfs = data.office_position_dfs
    office_dict = data.office_dict
    lord_titles_df = data.lord_titles_df
    aliases_df = data.aliases_df
    title_df = data.title_df
    holdings_df = data.holdings_df

    hitcount = 0

    fuzzy_flag = 0

    MATCH_CACHE = {}  # (target, speechdate) -> suggested speaker
    MISS_CACHE = set()  # (target, speechdate)
    AMBIG_CACHE = {}  # (target, speechdate) -> suggested speakers
    IGNORED_CACHE = set()  # (target, speechdate)
    FUZZY_CACHE = set()   # (target, speechdate)

    edit_distance_dict = {}  # alias -> list[speaker id's]

    extended_edit_distance_set = set()

    i = 0
    speechdate = None
    target = None
    debate_id = None
    ignored = False
    office_id = None

    for speaker in data.speakers:
        # if len(speaker.last_name) > 8:
        #     for alias in speaker.generate_edit_distance_aliases():
        #         extended_edit_distance_set.add(alias)
        for alias in speaker.generate_edit_distance_aliases():
            edit_distance_dict.setdefault(alias, []).append(speaker.member_id)

    def postprocess(string_val: str) -> str:
        for k, v in REGEX_POST_CORRECTIONS:
            string_val = re.sub(k, v, string_val)
        return string_val.strip()

    def preprocess(string_val: str) -> str:
        # Decide whether to use the text inside parenthesis or not.

        p_match = re.search(PARENTHESIS_REGEX, string_val)
        if p_match:
            inner_string = postprocess(cleanse_string(p_match.group(1)))
            if inner_string in alias_dict:  # is this a speaker name?
                return inner_string

        for k, v in REGEX_PRE_CORRECTIONS:
            string_val = re.sub(k, v, string_val)

        string_val = cleanse_string(string_val)
        for misspell in misspellings_dict:
            string_val = string_val.replace(misspell, misspellings_dict[misspell])
        string_val = cleanse_string(string_val)
        return postprocess(string_val)

    while True:
        try:
            chunk: pd.DataFrame = inq.get(block=True)
        except Empty:
            continue
        else:
            if chunk is None:
                # This is our signal that we are done here. Every other worker thread will get a similar signal.
                return

            chunk[OUTPUT_COLUMN] = chunk['speaker'].map(preprocess)
            chunk['ambiguous'] = 0
            chunk['fuzzy_matched'] = 0
            chunk['ignored'] = 0

            for row in chunk.itertuples():
                fuzzy_flag = 0
                i = row[0]
                speechdate = row.speechdate
                # unmodified_target = row.speaker
                target = getattr(row, OUTPUT_COLUMN)
                debate_id = int(row.debate_id)
                office_id = None

                if(target, speechdate) in FUZZY_CACHE:
                    chunk.loc[i, 'fuzzy_matched'] = 1

                if (target, speechdate) in MISS_CACHE:
                    chunk.loc[i, OUTPUT_COLUMN] = None
                    continue
                elif (target, speechdate) in AMBIG_CACHE:
                    chunk.loc[i, OUTPUT_COLUMN] = AMBIG_CACHE[(target, speechdate)]
                    chunk.loc[i, 'ambiguous'] = 1
                    continue
                elif target in IGNORED_CACHE:
                    chunk.loc[i, OUTPUT_COLUMN] = None
                    chunk.loc[i, 'ignored'] = 1
                    continue

                match = MATCH_CACHE.get((target, speechdate), None)
                ambiguity: bool = False
                possibles = []
                query = []

                # check if we should ignore this row.
                if not match:
                    ignored = is_ignored(target) or target in data.ignored_set

                    if ignored:
                        IGNORED_CACHE.add(target)
                        chunk.loc[i, OUTPUT_COLUMN] = None
                        chunk.loc[i, 'ignored'] = 1
                        continue  # continue onto the next speaker

                # if not match and not len(query):
                #     # Try honorary title
                #     condition = (speechdate >= honorary_title_df['start_search']) &\
                #                 (speechdate < honorary_title_df['end_search']) &\
                #                 (honorary_title_df['honorary_title'].str.contains(target, regex=False))
                #     query = honorary_title_df[condition]

                if not match and not len(query):
                    # try lord/viscount/earl aliases.
                    condition = (speechdate >= lord_titles_df['start_search']) &\
                                (speechdate < lord_titles_df['end_search']) &\
                                (lord_titles_df['alias'].str.contains(target, regex=False))
                    query = lord_titles_df[condition]

                if not match and not len(query):
                    # try name aliases.
                    condition = (speechdate >= aliases_df['start_search']) &\
                                (speechdate < aliases_df['end_search']) &\
                                (aliases_df['alias'].str.contains(target, regex=False))
                    query = aliases_df[condition]

                # if not match and not len(query):
                #     # try a lord title/alias
                #     condition = (speechdate >= title_df['start_search']) &\
                #                 (speechdate < title_df['end_search']) &\
                #                 (title_df['alias'].str.contains(target, regex=False))
                #     query = title_df[condition]

                # if not match and not len(query):
                #     # Try office position
                #     for position in office_title_dfs:
                #         if position in target:
                #             query = match_term(office_title_dfs[position], speechdate)
                #             break
                #         if within_distance_four(position, target, True):
                #             fuzzy_flag = 1
                #             query = match_term(office_title_dfs[position], speechdate)
                #             break

                if not match and not len(query):
                    for office in data.office_dict.values():
                        if target in office.aliases:
                            office_id = office.id
                            break
                        for alias in office.aliases:
                            if alias in target:
                                office_id = office_id
                                break

                    if office_id:
                        condition = (speechdate >= holdings_df['start_search']) & \
                                    (speechdate < holdings_df['end_search']) & \
                                    (office_id == holdings_df['office_id'])
                        query = holdings_df[condition]

                if not match:
                    query = query.drop_duplicates(subset=['corresponding_id'])
                    if len(query) == 1:
                        speaker_id = query.iloc[0]['corresponding_id']
                        if speaker_id != 'N/A' and not numpy.isnan(speaker_id):
                            # TODO: setup logging to keep track of when == n/a
                            # TODO: fix IDs missing due to being malformed entries in speakers.csv
                            # match = speaker_dict[int(speaker_id)]
                            # for now use speaker_id to ensure this counts as a match
                            try:
                                match = speaker_dict[int(speaker_id)]
                            except KeyError as e:
                                print('failed lookup', query)
                                match = None
                                ambiguity = False

                    elif len(query) > 1:
                        ambiguity = True

                if not match:
                    possibles = alias_dict.get(target)
                    if possibles is not None:
                        possibles = [speaker for speaker in possibles if speaker.matches(target, speechdate, cleanse=False)]
                        if len(possibles) == 1:
                            match = possibles[0]
                            ambiguity = False
                        else:
                            ambiguity = True
                    else:
                        possibles = []

                # Try edit distance with lord titles.
                if not match and not ambiguity:
                    match, ambiguity, possibles = match_edit_distance_df(target, speechdate, lord_titles_df,
                                                              ('start_search', 'end_search', 'alias'), speaker_dict)

                    if match: fuzzy_flag = 1

                # if not match and not ambiguity:
                #     match, ambiguity = match_edit_distance_df(target, speechdate, title_df,
                #                                               ('start_search', 'start_search', 'alias'), speaker_dict)
                #     if match: fuzzy_flag = 1

                # Try edit distance with honorary titles.
                # if not match and not ambiguity:
                #     match, ambiguity = match_edit_distance_df(target, speechdate, honorary_title_df,
                #                                               ('start_search', 'end_search', 'honorary_title'),
                #                                               speaker_dict)
                #     if match: fuzzy_match_indexes.append(i)

                # Try edit distance with office holdings.
                if not match and not ambiguity:
                    office_ids = []
                    for office in data.office_dict.values():
                        for alias in office.aliases:
                            if within_distance_four(alias, target, False):
                                office_ids.append(office.id)

                    if office_ids:
                        condition = (speechdate >= holdings_df['start_search']) & \
                                    (speechdate < holdings_df['end_search']) & \
                                    (holdings_df['office_id'].isin(office_ids))
                        query = holdings_df[condition]

                        if len(query) == 1:
                            match = query.iloc[0]['corresponding_id']
                            if not numpy.isnan(match) and type(match) != str:
                                match = speaker_dict[int(match)]
                            else:
                                match = None
                                ambiguity = False
                        elif len(query) > 1:
                            match = None
                            ambiguity = True

                        if match: fuzzy_flag = 1

                # Try edit distance with MP name permutations.
                if not match and not ambiguity:
                    # Remove initials. (Even if we did consider initials, it would cause more unnecessary ambiguities.)
                    target = re.sub(r'\b[a-z]\b', '', target)
                    # Fix multiple whitespace from previous regex.
                    target = re.sub(r'  +', ' ', target)

                    possibles = []
                    for alias in edit_distance_dict:
                        # if len(possibles) > 1:
                        #     break
                        if within_distance_two(target, alias, False):
                            for speaker_id in edit_distance_dict[alias]:
                                speaker = speaker_dict[speaker_id]
                                if speaker.start_date <= speechdate <= speaker.end_date:
                                    fuzzy_flag = 1
                                    possibles.append(speaker)

                    if len(possibles) == 1:
                        match = possibles[0]
                        ambiguity = False
                    elif len(possibles) > 1:
                        ambiguity = True

                if ambiguity and possibles:
                    match = speaker_dict.get(data.inferences.get(debate_id, None), None)
                    if match not in possibles:
                        match = None
                    else:
                        ambiguity = False
                        possibles = []

                if ambiguity and possibles:
                    # Filters out duplicates.
                    speaker_ids = {speaker.member_id for speaker in possibles}
                    possibles.clear()
                    for speaker_id in speaker_ids:
                        speaker = speaker_dict[speaker_id]
                        if speaker.age_at(speechdate) < 20:
                            continue
                        if speaker.is_in_office(speechdate):
                            possibles.append(speaker)

                    if len(possibles) == 1:
                        ambiguity = False
                        match = possibles[0]
                        flag = 6

                if ambiguity:
                    match = disambiguate(target, speechdate, row.speaker_house, row.debate_id, data.speaker_dict)
                    if match == -1:
                        match = None
                    else:
                        ambiguity = False
                        match = speaker_dict.get(match, match)

                if match is not None:
                    chunk.loc[i, 'fuzzy_matched'] = fuzzy_flag
                    if isinstance(match, SpeakerReplacement):
                        chunk.loc[i, OUTPUT_COLUMN] = match.id
                    else:
                        chunk.loc[i, OUTPUT_COLUMN] = match
                    MATCH_CACHE[(target, speechdate)] = match
                elif ambiguity:
                    chunk.loc[i, 'fuzzy_matched'] = fuzzy_flag
                    chunk.loc[i, 'ambiguous'] = 1

                    possibles = [speaker.id if isinstance(speaker, SpeakerReplacement) else speaker for speaker in possibles if speaker]
                    if not possibles:
                        match = None
                    else:
                        match = '|'.join(possibles)
                        chunk.loc[i, OUTPUT_COLUMN] = match
                    AMBIG_CACHE[(target, speechdate)] = match
                else:
                    # TODO: fix this
                    # best_guess = find_best_jaro_dist(target, alias_dict, honorary_title_df, lord_titles_df, aliases_df, speechdate)
                    # print('Best Guess for ', target, ' : ', best_guess)
                    chunk.loc[i, OUTPUT_COLUMN] = None
                    MISS_CACHE.add((target, speechdate))

            # outq.put((0, chunk.loc[matched_indexes, ['sentence_id', OUTPUT_COLUMN]], chunk.loc[missed_indexes, :], chunk.loc[ambiguities_indexes, :], chunk.loc[ignored_indexes, :]))
            outq.put((0, chunk[['sentence_id', 'speaker', OUTPUT_COLUMN, 'ambiguous', 'fuzzy_matched', 'ignored']]))

            hitcount = 0
