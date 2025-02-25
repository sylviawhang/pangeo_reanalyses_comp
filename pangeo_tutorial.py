# Pangeo intake-esm tutorial, 2/11/2025, Sylvia Whang siw2111@barnard.edu

import intake
import intake_esm

# Load the catalog
url = intake_esm.tutorial.get_url('google_cmip6')
print(url)
cat = intake.open_esm_datastore(url, progressbar = True) # cat = catalogue
print(cat)
print(cat.df.head())

# Finding unique entries 
unique = cat.unique()
print(unique)
print(unique['source_id']) # query what models 
print(unique['experiment_id']) # query what experiments 
print(unique['table_id']) # query what temporal frequenceis 

# search for specific datasets
cat_subset = cat.search(
    experiment_id=["historical", "ssp585"],
    table_id="Oyr",
    variable_id="o2",
    grid_label="gn",
)
print(cat_subset)

# Load datasets to xarray datasets
cat.esmcat.aggregation_control
dset_dict = cat_subset.to_dataset_dict(
    xarray_open_kwargs={"consolidated": True, "decode_times": True, "use_cftime": True}
)
print(dset_dict)

# access a particular dataset
ds = dset_dict["CMIP.CCCma.CanESM5.historical.Oyr.gn"]
print(ds)

single_ds = cat.search(
    experiment_id=["historical", "ssp585"],
    table_id="Oyr",
    variable_id="o2",
    grid_label="gn",
)

# Use custom preprocessing functions
cat_pp = cat.search(
    experiment_id=["historical"],
    table_id="Oyr",
    variable_id="o2",
    grid_label="gn",
    source_id=["IPSL-CM6A-LR", "CanESM5"],
    member_id="r10i1p1f1",
)
print(cat_pp.df)

dset_dict_raw = cat_pp.to_dataset_dict(xarray_open_kwargs={"consolidated": True})

for k, ds in dset_dict_raw.items():
    print(f"dataset key={k}\n\tdimensions={sorted(list(ds.dims))}\n")

# Robert example
url = 'https://storage.googleapis.com/cmip6/cmip6-pgf-ingestion-test/catalog/catalog.json'
col = intake.open_esm_datastore(url)

cat  = col.search(variable_id='ta', source_id='CESM2', experiment_id='historical', variant_label='r1i1p1f1') 
print(cat.df.head())