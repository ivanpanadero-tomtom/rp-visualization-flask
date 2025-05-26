def country_list():
    countries  = [
        'Spain',                    # ESP
        'Latvia',                   # LVA
        'Poland',                   # POL
        'Brazil',                   # BRA
        'Jordan',                   # JOR
        'France',                   # FRA
        'Brunei Darussalam',        # BRN
        'Uruguay',                  # URY
        'Gibraltar',                # GIB
        'Vatican City',             # VAT
        'Italy',                    # ITA
        'Ukraine',                  # UKR
        'French Guiana',            # GUF
        'Croatia',                  # HRV
        'Kosovo',                   # XKS (Non-standard code)
        'Qatar',                    # QAT
        'Great Britain',            # GBR
        'United Arab Emirates',     # ARE
        'Australia',                # AUS
        'Malta',                    # MLT
        'Mexico',                   # MEX
        'Belarus',                  # BLR
        'Slovakia',                 # SVK
        'Hungary',                  # HUN
        'Réunion',                  # REU
        'New Zealand',              # NZL
        'Saint Martin (French part)',# MAF
        'Thailand',                 # THA
        'Norway',                   # NOR
        'Venezuela',                # VEN
        'Finland',                  # FIN
        'Saudi Arabia',             # SAU
        'Albania',                  # ALB
        'Bahrain',                  # BHR
        'Bosnia and Herzegovina',   # BIH
        'Kuwait',                   # KWT
        'Andorra',                  # AND
        'Peru',                     # PER
        'Netherlands',              # NLD
        'Luxembourg',               # LUX
        'Turkey',                   # TUR
        'Montenegro',               # MNE
        'Austria',                  # AUT
        'USA',                      # USA
        'Morocco',                  # MAR
        'Oman',                     # OMN
        'Vietnam',                  # VNM
        'Liechtenstein',            # LIE
        'Lesotho',                  # LSO
        'South Africa',             # ZAF
        'Israel',                   # ISR
        'Portugal',                 # PRT
        'Tunisia',                  # TUN
        'San Marino',               # SMR
        'Lithuania',                # LTU
        'Cyprus',                   # CYP
        'Taiwan',                   # TWN
        'Malaysia',                 # MYS
        'Chile',                    # CHL
        'Macau',                    # MAC
        'Canada',                   # CAN
        'Colombia',                 # COL
        'Russian Federation',       # RUS
        'Romania',                  # ROU
        'Argentina',                # ARG
        'Denmark',                  # DNK
        'Eswatini',                 # SWZ (formerly Swaziland)
        'Kenya',                    # KEN
        'Mayotte',                  # MYT
        'Estonia',                  # EST
        'Lebanon',                  # LBN
        'Ireland',                  # IRL
        'Sweden',                   # SWE
        'Nigeria',                  # NGA
        'Slovenia',                 # SVN
        'Guadeloupe',               # GLP
        'Martinique',               # MTQ
        'Greece',                   # GRC
        'Singapore',                # SGP
        'India',                    # IND
        'Kazakhstan',               # KAZ
        'Hong Kong',                # HKG
        'Belgium',                  # BEL
        'North Macedonia',          # MKD
        'Indonesia',                # IDN
        'Germany',                  # DEU
        'Algeria',                  # DZA
        'Bulgaria',                 # BGR
        'Monaco',                   # MCO
        'Serbia',                   # SRB
        'Switzerland',              # CHE
        'Czech Republic',           # CZE
        'Philippines',              # PHL
        'Egypt',                    # EGY
        'Iceland'                   # ISL
    ]

    return countries

# def data_paths_dict():
#     data_path = {
#     'Albania': 'data/data_alb',
#     'Algeria': 'data/data_dza',
#     'Andorra': 'data/data_and',
#     'Argentina': 'data/data_arg',
#     'Australia': 'data/data_aus',
#     'Austria': 'data/data_aut',
#     'Bahrain': 'data/data_bhr',
#     'Belarus': 'data/data_blr',
#     'Belgium': 'data/data_bel',
#     'Bosnia and Herzegovina': 'data/data_bih',
#     'Brazil': 'data/data_bra',
#     'Brunei Darussalam': 'data/data_brn',
#     'Bulgaria': 'data/data_bgr',
#     'Canada': 'data/data_can',
#     'Chile': 'data/data_chl',
#     'Colombia': 'data/data_col',
#     'Croatia': 'data/data_hrv',
#     'Cyprus': 'data/data_cyp',
#     'Czech Republic': 'data/data_cze',
#     'Denmark': 'data/data_dnk',
#     'Egypt': 'data/data_egy',
#     'Eswatini': 'data/data_swz',  # Formerly Swaziland
#     'Estonia': 'data/data_est',
#     'Finland': 'data/data_fin',
#     'France': 'data/data_fra',
#     'Germany': 'data/data_deu',
#     'Gibraltar': 'data/data_gib',
#     'Greece': 'data/data_grc',
#     'Great Britain': 'data/data_gbr',
#     'Guadeloupe': 'data/data_glp',
#     'Hong Kong': 'data/data_hkg',
#     'Hungary': 'data/data_hun',
#     'Iceland': 'data/data_isl',
#     'India': 'data/data_ind',
#     'Indonesia': 'data/data_idn',
#     'Ireland': 'data/data_irl',
#     'Israel': 'data/data_isr',
#     'Italy': 'data/data_ita',
#     'Kazakhstan': 'data/data_kaz',
#     'Kuwait': 'data/data_kwt',
#     'Latvia': 'data/data_lva',
#     'Liechtenstein': 'data/data_lie',
#     'Lithuania': 'data/data_ltu',
#     'Luxembourg': 'data/data_lux',
#     'Macau': 'data/data_mac',
#     'Malta': 'data/data_mlt',
#     'Martinique': 'data/data_mtq',
#     'Mayotte': 'data/data_myt',
#     'Mexico': 'data/data_mex',
#     'Montenegro': 'data/data_mne',
#     'Morocco': 'data/data_mar',
#     'Netherlands': 'data/data_nld',
#     'New Zealand': 'data/data_nzl',
#     'North Macedonia': 'data/data_mkd',
#     'Norway': 'data/data_nor',
#     'Oman': 'data/data_omn',
#     'Peru': 'data/data_per',
#     'Philippines': 'data/data_phl',
#     'Poland': 'data/data_pol',
#     'Portugal': 'data/data_prt',
#     'Qatar': 'data/data_qat',
#     'Réunion': 'data/data_reu',
#     'Russian Federation': 'data/data_rus',
#     'San Marino': 'data/data_smr',
#     'Serbia': 'data/data_srb',
#     'Slovakia': 'data/data_svk',
#     'Slovenia': 'data/data_svn',
#     'South Africa': 'data/data_zaf',
#     'Spain': 'data/data_esp',
#     'Sweden': 'data/data_swe',
#     'Switzerland': 'data/data_che',
#     'Taiwan': 'data/data_twn',
#     'Thailand': 'data/data_tha',
#     'Turkey': 'data/data_tur',
#     'Ukraine': 'data/data_ukr',
#     'United Arab Emirates': 'data/data_are',
#     'USA': 'data/data_usa',
#     'Vatican City': 'data/data_vat',
#     'Venezuela': 'data/data_ven',
#     'Vietnam': 'data/data_vnm',
#     'Kosovo': 'data/data_xks',  # Non-standard ISO code
#     }
#     return data_path

def data_paths_dict():
    data_path = {
    'Albania': 'data/data_ALB',
    'Algeria': 'data/data_DZA',
    'Andorra': 'data/data_AND',
    'Argentina': 'data/data_ARG',
    'Australia': 'data/data_AUS',
    'Austria': 'data/data_AUT',
    'Bahrain': 'data/data_BHR',
    'Belarus': 'data/data_BLR',
    'Belgium': 'data/data_BEL',
    'Bosnia and Herzegovina': 'data/data_BIH',
    'Brazil': 'data/data_BRA',
    'Brunei Darussalam': 'data/data_BRN',
    'Bulgaria': 'data/data_BGR',
    'Canada': 'data/data_CAN',
    'Chile': 'data/data_CHL',
    'Colombia': 'data/data_COL',
    'Croatia': 'data/data_HRV',
    'Cyprus': 'data/data_CYP',
    'Czech Republic': 'data/data_CZE',
    'Denmark': 'data/data_DNK',
    'Egypt': 'data/data_EGY',
    'Eswatini': 'data/data_SWZ',  # Formerly Swaziland
    'Estonia': 'data/data_EST',
    'Finland': 'data/data_FIN',
    'France': 'data/data_FRA',
    'Germany': 'data/data_DEU',
    'Gibraltar': 'data/data_GIB',
    'Greece': 'data/data_GRC',
    'Great Britain': 'data/data_GBR',
    'Guadeloupe': 'data/data_GLP',
    'Hong Kong': 'data/data_HKG',
    'Hungary': 'data/data_HUN',
    'Iceland': 'data/data_ISL',
    'India': 'data/data_IND',
    'Indonesia': 'data/data_IDN',
    'Ireland': 'data/data_IRL',
    'Israel': 'data/data_ISR',
    'Italy': 'data/data_ITA',
    'Kazakhstan': 'data/data_KAZ',
    'Kuwait': 'data/data_KWT',
    'Latvia': 'data/data_LVA',
    'Liechtenstein': 'data/data_LIE',
    'Lithuania': 'data/data_LTU',
    'Luxembourg': 'data/data_LUX',
    'Macau': 'data/data_MAC',
    'Malta': 'data/data_MLT',
    'Martinique': 'data/data_MTQ',
    'Mayotte': 'data/data_MYT',
    'Mexico': 'data/data_MEX',
    'Montenegro': 'data/data_MNE',
    'Morocco': 'data/data_MAR',
    'Netherlands': 'data/data_NLD',
    'New Zealand': 'data/data_NZL',
    'North Macedonia': 'data/data_MKD',
    'Norway': 'data/data_NOR',
    'Oman': 'data/data_OMN',
    'Peru': 'data/data_PER',
    'Philippines': 'data/data_PHL',
    'Poland': 'data/data_POL',
    'Portugal': 'data/data_PRT',
    'Qatar': 'data/data_QAT',
    'Réunion': 'data/data_REU',
    'Russian Federation': 'data/data_RUS',
    'San Marino': 'data/data_SMR',
    'Serbia': 'data/data_SRB',
    'Slovakia': 'data/data_SVK',
    'Slovenia': 'data/data_SVN',
    'South Africa': 'data/data_ZAF',
    'Spain': 'data/data_ESP',
    'Sweden': 'data/data_SWE',
    'Switzerland': 'data/data_CHE',
    'Taiwan': 'data/data_TWN',
    'Thailand': 'data/data_THA',
    'Turkey': 'data/data_TUR',
    'Ukraine': 'data/data_UKR',
    'United Arab Emirates': 'data/data_ARE',
    'USA': 'data/data_USA',
    'Vatican City': 'data/data_VAT',
    'Venezuela': 'data/data_VEN',
    'Vietnam': 'data/data_VNM',
    'Kosovo': 'data/data_XKS',  # Non-standard ISO code
    }
    return data_path