# Raw MedQuAD source

The full MedQuAD XML repository is not vendored here. The candidate CSV was extracted from upstream commit `577bd37b96c02d1833b2c9eed2de9f96964e96cb`.

To reproduce the extraction from this exact snapshot:

```bash
git clone https://github.com/abachaa/MedQuAD.git data/raw/MedQuAD
git -C data/raw/MedQuAD checkout 577bd37b96c02d1833b2c9eed2de9f96964e96cb
python src/prepare_medquad.py --input data/raw/MedQuAD
```

Upstream repository: https://github.com/abachaa/MedQuAD
Dataset paper: Ben Abacha & Demner-Fushman (2019), https://doi.org/10.1186/s12859-019-3119-4
License stated by upstream: CC BY 4.0. Retain attribution and mark modifications. The upstream readme says answers were removed from three MedlinePlus collections to respect their copyright. Recheck source rights before redistribution, especially for derived text.
