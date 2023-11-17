from imaging.segmentation.tools.classes_cnn import *

wrm = NNMealworms()
os.chdir("C:\\Users\\dabe\\Desktop\\ct")
wrm.load_model("2023.11.17 10.07.14 iter 100 mdl.pth")
wrm.load_params("2023.11.17 10.07.14 params.dat")
wrm.compose_transforms_tst()
wrm.cache_data()
wrm.testing()