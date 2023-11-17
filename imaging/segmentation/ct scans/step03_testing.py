from imaging.segmentation.tools.classes_cnn import *

wrm = NNMealworms()
os.chdir("C:\\Users\\dabe\\Desktop\\ct")
wrm.load_model("2023.11.16 20.07.06 iter 090 mdl.pth")
wrm.load_params("2023.11.16 20.07.06 params.dat")
wrm.compose_transforms_tst()
wrm.cache_data()
wrm.testing()