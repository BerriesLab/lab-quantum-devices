from imaging.segmentation.tools.classes_cnn import *

wrm = NNMealworms()
wrm.params["dataset_trn_ratio"] = 0.8
wrm.params["dataset_val_ratio"] = 0.2
wrm.params["dataset_tst_ratio"] = 0
wrm.build_dataset()
wrm.get_dxdydz()
wrm.compose_transforms_trn()
wrm.compose_transforms_val()
wrm.compose_transforms_tst()
wrm.cache_data()
wrm.build_model_unet()
wrm.train()
wrm.plot_loss()
wrm.plot_metr()
plt.show()