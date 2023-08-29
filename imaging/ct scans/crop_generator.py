import nibabel as nib
import matplotlib.pyplot as plt
import random
from skimage.color import label2rgb
from skimage.measure import label, regionprops
from skimage.exposure import rescale_intensity
from matplotlib.patches import Rectangle
from numpy import max, min, rint, all, uint8, argwhere

box_safe_margin = 50
voxelXSize = 200 # px
voxelYSize = 200 # px
voxelZSize = 200 # px
nCrops = 50 # px
PATH_DATA = r"T:\data raw\ct\training data"
ctData = nib.load(rf"{PATH_DATA}\ct_scan.nii.gz")
ctLabels = nib.load(rf"{PATH_DATA}\segmentation.nii.gz")
print(f"CT scan input shape: {ctData.shape}")

"""chop the volume that includes the segmentation only"""
sgm = rint(ctLabels.get_fdata()).astype(uint8)
idxs = argwhere(sgm == 1)
xmin = min(idxs[:, 0]) - box_safe_margin if min(idxs[:, 0]) - box_safe_margin >= 0 else 0
xmax = max(idxs[:, 0]) + box_safe_margin if min(idxs[:, 0]) - box_safe_margin <= ctLabels.shape[0] else ctLabels.shape[0]
ymin = min(idxs[:, 1]) - box_safe_margin if min(idxs[:, 1]) - box_safe_margin >= 0 else 0
ymax = max(idxs[:, 1]) + box_safe_margin if min(idxs[:, 1]) - box_safe_margin <= ctLabels.shape[1] else ctLabels.shape[1]
zmin = min(idxs[:, 2]) - box_safe_margin if min(idxs[:, 2]) - box_safe_margin >= 0 else 0
zmax = max(idxs[:, 2]) + box_safe_margin if min(idxs[:, 2]) - box_safe_margin <= ctLabels.shape[2] else ctLabels.shape[2]
imax = max(ctData.slicer[xmin:xmax, ymin:ymax, zmin:zmax].get_fdata())
imin = min(ctData.slicer[xmin:xmax, ymin:ymax, zmin:zmax].get_fdata())
print(f"CT scan with labels shape: {ctData.shape}")

for idx in range(0, nCrops):
    # define the coordinates of the crop corner.
    # Note: crops are new volumes and therefore theis coordinates start from 0
    x = random.randint(xmin, xmax - voxelXSize)
    y = random.randint(ymin, ymax - voxelYSize)
    z = random.randint(zmin, zmax - voxelZSize)
    # slice image and labels, and retrieve data
    print(f"Crop CT scan {idx:02d}: x[{x}, {x+voxelXSize}], y[{y}, {y+voxelYSize}], z[{z}, {z+voxelZSize}]")
    ctDataCrop = ctData.slicer[x:x+voxelXSize, y:y+voxelYSize, z:z+voxelZSize]
    ctLabelsCrop = ctLabels.slicer[x:x+voxelXSize, y:y+voxelYSize, z:z+voxelZSize]
    img = ctDataCrop.get_fdata()
    sgm = rint(ctLabelsCrop.get_fdata()).astype(uint8)

    fig, ax = plt.subplots(2, 3)

    ax[0, 0].set_title(f"YZ plane at X={x+voxelXSize//2}px")
    ax[0, 0].imshow(img[voxelXSize//2, :, :], cmap='gray', vmin=imin, vmax=imax)
    #ax[0, 0].axhline(voxelYSize//2, linestyle="dashed")
    #ax[0, 0].axvline(voxelZSize//2, linestyle="dashed")
    ax[0, 0].axis('off')
    ax[0, 1].set_title(f"XZ plane at Y={y+voxelYSize//2}px")
    ax[0, 1].imshow(img[:, voxelYSize//2, :], cmap='gray', vmin=imin, vmax=imax)
    #ax[0, 1].axhline(voxelXSize//2, linestyle="dashed")
    #ax[0, 1].axvline(voxelZSize//2, linestyle="dashed")
    ax[0, 1].axis('off')
    ax[0, 2].set_title(f"XY plane at Z={z+voxelZSize//2}px")
    ax[0, 2].imshow(img[:, :, voxelZSize//2], cmap='gray', vmin=imin, vmax=imax)
    #ax[0, 2].axhline(voxelYSize//2, linestyle="dashed")
    #ax[0, 2].axvline(voxelZSize//2, linestyle="dashed")
    ax[0, 2].axis('off')

    # msk = masked_where(sgm == 0, sgm)
    # ax[1, 0].imshow(img[voxelXSize//2, :, :], cmap='gray', vmin=imin, vmax=imax)
    # ax[1, 0].imshow(msk[voxelXSize//2, :, :], cmap='Wistia', alpha=0.7)
    # ax[1, 1].imshow(img[:, voxelYSize//2, :], cmap='gray', vmin=imin, vmax=imax)
    # ax[1, 1].imshow(msk[:, voxelYSize//2, :], cmap='Wistia', alpha=0.7)
    # ax[1, 2].imshow(img[:, :, voxelZSize//2], cmap='gray', vmin=imin, vmax=imax)
    # ax[1, 2].imshow(msk[:, :, voxelZSize//2], cmap='Wistia', alpha=0.7)
    # ax[1, 0].axis('off')
    # ax[1, 1].axis('off')
    # ax[1, 2].axis('off')

    labelsCropX = label(sgm[voxelXSize//2, :, :], connectivity=1)
    labelsCropY = label(sgm[:, voxelYSize//2, :], connectivity=1)
    labelsCropZ = label(sgm[:, :, voxelZSize//2], connectivity=1)
    image_label_overlay_x = label2rgb(label=labelsCropX, image=rescale_intensity(img[voxelXSize//2, :, :], out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
    image_label_overlay_y = label2rgb(label=labelsCropY, image=rescale_intensity(img[:, voxelYSize//2, :], out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
    image_label_overlay_z = label2rgb(label=labelsCropZ, image=rescale_intensity(img[:, :, voxelZSize//2], out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
    ax[1, 0].imshow(image_label_overlay_x)
    ax[1, 1].imshow(image_label_overlay_y)
    ax[1, 2].imshow(image_label_overlay_z)
    ax[1, 0].axis('off')
    ax[1, 1].axis('off')
    ax[1, 2].axis('off')
    regions = regionprops(labelsCropX)
    for region in regions:
        minr, minc, maxr, maxc = region.bbox
        rect = Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
        ax[1, 0].add_patch(rect)
    regions = regionprops(labelsCropY)
    for region in regions:
        minr, minc, maxr, maxc = region.bbox
        rect = Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
        ax[1, 1].add_patch(rect)
    regions = regionprops(labelsCropZ)
    for region in regions:
        minr, minc, maxr, maxc = region.bbox
        rect = Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
        ax[1, 2].add_patch(rect)

    plt.tight_layout()
    plt.savefig(rf"{PATH_DATA}\crop_{idx:02d}_sgm.png", dpi=1200)
    nib.save(ctDataCrop, rf"{PATH_DATA}\crop_{idx:02d}_img.nii.gz")
    nib.save(ctLabelsCrop, rf"{PATH_DATA}\crop_{idx:02d}_lbl.nii.gz")
    plt.close()



