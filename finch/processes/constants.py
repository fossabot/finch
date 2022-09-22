from xclim.testing import list_input_variables

CANDCSU5_MODELS = {
    '24models': [  # The absence of realization specification implies r1 is taken.
        "BNU-ESM",
        "CCSM4",
        "CESM1-CAM5",
        "CNRM-CM5",
        "CSIRO-Mk3-6-0",
        "CanESM2",
        "FGOALS-g2",
        "GFDL-CM3",
        "GFDL-ESM2G",
        "GFDL-ESM2M",
        "HadGEM2-AO",
        "HadGEM2-ES",
        "IPSL-CM5A-LR",
        "IPSL-CM5A-MR",
        "MIROC-ESM-CHEM",
        "MIROC-ESM",
        "MIROC5",
        "MPI-ESM-LR",
        "MPI-ESM-MR",
        "MRI-CGCM3",
        "NorESM1-M",
        "NorESM1-ME",
        "bcc-csm1-1-m",
        "bcc-csm1-1",
    ],
    # taken from: https://www.pacificclimate.org/data/statistically-downscaled-climate-scenarios
    'pcic12': [
        ("ACCESS1-0", "r1i1p1"),
        ("CCSM4", "r2i1p1"),
        ("CNRM-CM5", "r1i1p1"),
        ("CSIRO-Mk3-6-0", "r1i1p1"),
        ("CanESM2", "r1i1p1"),
        ("GFDL-ESM2G", "r1i1p1"),
        ("HadGEM2-CC", "r1i1p1"),
        ("HadGEM2-ES", "r1i1p1"),
        ("MIROC5", "r3i1p1"),
        ("MPI-ESM-LR", "r3i1p1"),
        ("MRI-CGCM3", "r1i1p1"),
        ("inmcm4", "r1i1p1"),
    ]
}


CANDCSU6_MODELS = {
    "26models": [
        'ACCESS-CM2',
        'ACCESS-ESM1-5',
        'BCC-CSM2-MR',
        'CMCC-ESM2',
        'CNRM-CM6-1',
        'CNRM-ESM2-1',
        'CanESM5',
        'EC-Earth3',
        'EC-Earth3-Veg',
        'FGOALS-g3',
        'GFDL-ESM4',
        'HadGEM3-GC31-LL',
        'INM-CM4-8',
        'INM-CM5-0',
        'IPSL-CM6A-LR',
        'KACE-1-0-G',
        'KIOST-ESM',
        'MIROC-ES2L',
        'MIROC6',
        'MPI-ESM1-2-HR',
        'MPI-ESM1-2-LR',
        'MRI-ESM2-0',
        'NorESM2-LM',
        'NorESM2-MM',
        'TaiESM1',
        'UKESM1-0-LL'
    ]
}


bccaq_variables = {"tasmin", "tasmax", "pr"}

xclim_variables = set(list_input_variables(submodules=["atmos", "land", "seaIce"]).keys())

default_percentiles = {
    'days_over_precip_thresh': {'pr_per': 95},
    'days_over_precip_doy_thresh': {'pr_per': 95},
    'fraction_over_precip_doy_thresh': {'pr_per': 95},
    'fraction_over_precip_thresh': {'pr_per': 95},
    'cold_and_dry_days': {'pr_per': 25, 'tas_per': 25},
    'warm_and_dry_days': {'pr_per': 25, 'tas_per': 75},
    'warm_and_wet_days': {'pr_per': 75, 'tas_per': 75},
    'cold_and_wet_days': {'pr_per': 75, 'tas_per': 25},
    'tg90p': {'tas_per': 90},
    'tg10p': {'tas_per': 10},
    'tn90p': {'tasmin_per': 90},
    'tn10p': {'tasmin_per': 10},
    'tx90p': {'tasmax_per': 90},
    'tx10p': {'tasmax_per': 10},
    'cold_spell_duration_index': {'tasmin_per': 10},
    'warm_spell_duration_index': {'tasmax_per': 90},
}
