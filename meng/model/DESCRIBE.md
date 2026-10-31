# Meng et al. 2020's spine model, reduced

Written by research_notes/open-vertebra-meshes/extract_meng.py on GitHub's runner, from
gitlab.inria.fr/spine/spine_model. Arrays are .npy files; float32 where the original was
float64 and over 16777216 bytes; shapedirs and C cut to their first 40 modes.

## smpl: vertebra_smpl_v10.pkl

1103309681 bytes, md5 b08f8c52ac1999f4ca00401467f7ffc0

| key | what it is | kept |
|---|---|---|
| J | ndarray float64 (24, 3), 576 bytes | J float64 (24, 3) in 1 file |
| J_regressor | scipy.sparse.csc.csc_matrix, state ['_shape', 'data', 'indices', 'indptr', 'maxprint'] | J_regressor.data float64 (48,) in 1 file; J_regressor.indices int32 (48,) in 1 file; J_regressor.indptr int32 (127286,) in 1 file; J_regressor.shape int64 (2,) in 1 file |
| bs_style | str 'lbs' | nothing to keep |
| bs_type | str 'lrotmin' | nothing to keep |
| f | ndarray uint32 (254632, 3), 3055584 bytes | f uint32 (254632, 3) in 1 file |
| kintree_table | ndarray int64 (2, 24), 384 bytes | kintree_table int64 (2, 24) in 1 file |
| posedirs | ndarray float64 (127285, 3, 207), 632351880 bytes | left out: not needed |
| shapedirs | ndarray float64 (127285, 3, 144), 439896960 bytes | shapedirs float32 (127285, 3, 40) in 1 file |
| v_template | ndarray float64 (127285, 3), 3054840 bytes | v_template float64 (127285, 3) in 1 file |
| weights | ndarray float64 (127285, 24), 24438720 bytes | weights float32 (127285, 24) in 1 file |

## ppca: vertebra_smpl_v10_ppca_metadata.pkl

729346730 bytes, md5 1e11face7e67e58a6e1b4e83718c0abd

| key | what it is | kept |
|---|---|---|
| B | ndarray float64 (127308, 3, 144), 439976448 bytes | B float32 (127308, 3, 144) in 3 files |
| C | ndarray float64 (381924, 10), 30553920 bytes | C float32 (381924, 10) in 1 file |
| M | ndarray float64 (127308, 3), 3055392 bytes | M float64 (127308, 3) in 1 file |
| M_pp | ndarray float64 (381924,), 3055392 bytes | M_pp float64 (381924,) in 1 file |
| Var | ndarray float64 (144,), 1152 bytes | Var float64 (144,) in 1 file |
| X | ndarray float64 (144, 10), 11520 bytes | X float64 (144, 10) in 1 file |
| f | ndarray uint32 (254632, 3), 3055584 bytes | f uint32 (254632, 3) in 1 file |
| ss | float64 4.7411343055035834e-07 | ss float64 () in 1 file |

