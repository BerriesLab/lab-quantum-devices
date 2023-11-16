from imaging.segmentation.tools.classes_cnn import *

wrm = NNMealworms()
wrm.load_model(path_to_model="C:\\Users\\dabe\\Desktop\\ct\\dataset_val\\2023.11.16 14.09.11 iter 040 mdl.pth")
wrm.load_params(file_path="C:\\Users\\dabe\\Desktop\\ct\\dataset_val\\2023.11.16 14.09.11 params.dat")
wrm.params["dir_data_trn"] = "C:\\Users\\dabe\\Desktop\\ct\\dataset_trn"
wrm.compose_transforms_tst()
wrm.cache_data()
wrm.testing()