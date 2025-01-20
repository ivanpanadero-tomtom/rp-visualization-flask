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

def data_paths_dict():
    data_path = {
    'Albania': 'data-branch/data_alb',
    'Algeria': 'data-branch/data_dza',
    'Andorra': 'data-branch/data_and',
    'Argentina': 'data-branch/data_arg',
    'Australia': 'data-branch/data_aus',
    'Austria': 'data-branch/data_aut',
    'Bahrain': 'data-branch/data_bhr',
    'Belarus': 'data-branch/data_blr',
    'Belgium': 'data-branch/data_bel',
    'Bosnia and Herzegovina': 'data-branch/data_bih',
    'Brazil': 'data-branch/data_bra',
    'Brunei Darussalam': 'data-branch/data_brn',
    'Bulgaria': 'data-branch/data_bgr',
    'Canada': 'data-branch/data_can',
    'Chile': 'data-branch/data_chl',
    'Colombia': 'data-branch/data_col',
    'Croatia': 'data-branch/data_hrv',
    'Cyprus': 'data-branch/data_cyp',
    'Czech Republic': 'data-branch/data_cze',
    'Denmark': 'data-branch/data_dnk',
    'Egypt': 'data-branch/data_egy',
    'Eswatini': 'data-branch/data_swz',  # Formerly Swaziland
    'Estonia': 'data-branch/data_est',
    'Finland': 'data-branch/data_fin',
    'France': 'data-branch/data_fra',
    'Germany': 'data-branch/data_deu',
    'Gibraltar': 'data-branch/data_gib',
    'Greece': 'data-branch/data_grc',
    'Great Britain': 'data-branch/data_gbr',
    'Guadeloupe': 'data-branch/data_glp',
    'Hong Kong': 'data-branch/data_hkg',
    'Hungary': 'data-branch/data_hun',
    'Iceland': 'data-branch/data_isl',
    'India': 'data-branch/data_ind',
    'Indonesia': 'data-branch/data_idn',
    'Ireland': 'data-branch/data_irl',
    'Israel': 'data-branch/data_isr',
    'Italy': 'data-branch/data_ita',
    'Kazakhstan': 'data-branch/data_kaz',
    'Kuwait': 'data-branch/data_kwt',
    'Latvia': 'data-branch/data_lva',
    'Liechtenstein': 'data-branch/data_lie',
    'Lithuania': 'data-branch/data_ltu',
    'Luxembourg': 'data-branch/data_lux',
    'Macau': 'data-branch/data_mac',
    'Malta': 'data-branch/data_mlt',
    'Martinique': 'data-branch/data_mtq',
    'Mayotte': 'data-branch/data_myt',
    'Mexico': 'data-branch/data_mex',
    'Montenegro': 'data-branch/data_mne',
    'Morocco': 'data-branch/data_mar',
    'Netherlands': 'data-branch/data_nld',
    'New Zealand': 'data-branch/data_nzl',
    'North Macedonia': 'data-branch/data_mkd',
    'Norway': 'data-branch/data_nor',
    'Oman': 'data-branch/data_omn',
    'Peru': 'data-branch/data_per',
    'Philippines': 'data-branch/data_phl',
    'Poland': 'data-branch/data_pol',
    'Portugal': 'data-branch/data_prt',
    'Qatar': 'data-branch/data_qat',
    'Réunion': 'data-branch/data_reu',
    'Russian Federation': 'data-branch/data_rus',
    'San Marino': 'data-branch/data_smr',
    'Serbia': 'data-branch/data_srb',
    'Slovakia': 'data-branch/data_svk',
    'Slovenia': 'data-branch/data_svn',
    'South Africa': 'data-branch/data_zaf',
    'Spain': 'data-branch/data_esp',
    'Sweden': 'data-branch/data_swe',
    'Switzerland': 'data-branch/data_che',
    'Taiwan': 'data-branch/data_twn',
    'Thailand': 'data-branch/data_tha',
    'Turkey': 'data-branch/data_tur',
    'Ukraine': 'data-branch/data_ukr',
    'United Arab Emirates': 'data-branch/data_are',
    'USA': 'data-branch/data_usa',
    'Vatican City': 'data-branch/data_vat',
    'Venezuela': 'data-branch/data_ven',
    'Vietnam': 'data-branch/data_vnm',
    'Kosovo': 'data-branch/data_xks',  # Non-standard ISO code
    }
    return data_path