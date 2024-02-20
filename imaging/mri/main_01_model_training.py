from imaging.mri.utilities import *
from imaging.mri.class_BrainLearn import BrainLearn

bl = BrainLearn()
bl.path_main = "/Users/berri/Desktop/ct"
bl.dataset_trn_ratio = 0.7
bl.dataset_val_ratio = 0.2
bl.dataset_tst_ratio = 0.1

bl.max_iteration_trn = 1000
bl.delta_iteration_trn = 100

bl.build_dataset()
roi_size = bl.find_roi()
bl.compose_transforms_trn()

# Load data (brain atlas, database...)


# Register pre-contrast image



wrm.get_dxdydz()
wrm.compose_transforms_trn()
wrm.compose_transforms_val()
wrm.compose_transforms_tst()
wrm.cache_data()
wrm.build_model_unet(num_res_units=4,
                     channels=(64, 128, 256, 512, 1024),
                     strides=(2, 2, 2, 2))
# wrm.build_model_unetr(img_size=(128, 128, 128),
#                      feature_size=16,
#                      hidden_size=768,
#                      feedfwd_layers=3072,
#                      attention_heads=12)
wrm.save_params()
wrm.train()
wrm.plot_loss()
wrm.plot_metr()
plt.show()

