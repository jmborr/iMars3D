#!/usr/bin/env python

"""
Workflow
* crop images 
* filter spots 
* normalize
* normalize for beam intensity fluctuation: select ROI
* filter rings
* correct axis tilt
* sinograms
* parallel beam reconstruction
"""

import os, glob, numpy as np, sys
from ivenus.io import ImageSeries, ImageFile

datadir = "../iVenus_large_dataset/reconstruction/turbine"
ct_series = ImageSeries(
    os.path.join(datadir, "*CT*_%.3f_*.fits"),
    angles = np.arange(0, 182, .85),
    )
df_images = [
    ImageFile(p) 
    for p in glob.glob(os.path.join(datadir, "*DF*.fits"))
    ]
# print [im.path for im in df_images]
ob_images = [
    ImageFile(p) 
    for p in glob.glob(os.path.join(datadir, "*OB*.fits"))
    ]


def average(images, prefix, console_out):
    N = len(images)
    assert N
    res = np.array(images[0].getData(), dtype=float)
    for i, im in enumerate(images[1:]):
        console_out.write("\r%s: %2.0f%%" % (prefix, (i+1)*100./(N-1)))
        console_out.flush()
        res += np.array(im.getData(), dtype=float)
        continue
    return res/N


def normalize(ct_series, df_images, ob_images, output_template, console_out):
    df = average(df_images, "Dark field:", console_out)
    console_out.write("\n")
    np.save("df.npy", df)
    ob = average(ob_images, "Open beam:", console_out)
    console_out.write("\n")
    np.save("ob.npy", ob)
    prefix = "Normalize:"
    N = len(ct_series.angles)
    for i, angle in enumerate(ct_series.angles):
        data = np.array(ct_series.getData(angle), dtype=float)
        data -= df
        data /= ob
        f = ImageFile(output_template % angle)
        f.data = data
        f.save()
        console_out.write("\r%s: %2.0f%%" % (prefix, (i+1)*100./N))
        console_out.flush()
        continue
    return


def main():
    normalize(ct_series, df_images, ob_images, "normalized_%7.3f.npy", sys.stdout)
    return


if __name__ == '__main__': main()
