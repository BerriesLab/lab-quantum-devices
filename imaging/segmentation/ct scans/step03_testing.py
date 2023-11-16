from imaging.segmentation.tools.classes_cnn import *

wrm = NNMealworms()
wrm.load_model("2023.11.16 14.09.11 iter 040 mdl.pth")
wrm.load_params("2023.11.16 14.09.11 params.dat")
os.chdir("C:\\Users\\dabe\\Desktop\\ct")
wrm.compose_transforms_tst()
wrm.cache_data()
wrm.testing()