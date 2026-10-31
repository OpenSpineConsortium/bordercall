# Human Spine Model

Welcome to the repository containing the spine statistical model learned from incomplete data published
at the ShapeMi 2020 MICCAI Workshop.


# Contact and  Mailing list 

If you are interested in the model and want to be updated with news,
please subscribe to the spine_model@inria.fr mailing list.

To do so, send an email to [sympa@inria.fr](mailto:sympa@inria.fr) with the subjet  `subscribe spine_model`.

For any questions related to the paper and the model release, please contact
[Di Meng](mailto:di.meng@inria.fr) or [Sergi Pujades](mailto:sergi.pujades-rocamora@inria.fr).


# Model Licence

The Spine Model is released under the 
[CC BY-NC-SA 2.0](https://creativecommons.org/licenses/by-nc-sa/2.0/legalcode) licence. 
 
Please check the [Licence](Licence.md) page with the full licence text.


# Model Release

We provide [Install](Install.md) instructions and a [QuickStart](QuickStart.md) guide to 
learn how to use the model and reconstruct a full spine from partial data.

# Citing the work

If you use the spine model in your research project, 
please cite the model paper


    @inproceedings{meng2020spine,
      title={Learning a statistical full spine model from partial observations},
      author={Meng, Di and Keller, Marilyn and Boyer, Edmond and Black, Michael J. and Pujades, Sergi},
      booktitle={International Workshop on Shape in Medical Imaging},
      year={2020},
      organization={Springer}
    }

as well as the Verse 2019 paper

    @article{sekuboyina2020verse,
      title={VerSe: A Vertebrae Labelling and Segmentation Benchmark},
      author={Sekuboyina, Anjany and Bayat, Amirhossein and Husseini, Malek E and 
              L{\"o}ffler, Maximilian and Rempfler, Markus and Kuka{\v{c}}ka, Jan and
              Tetteh, Giles and Valentinitsch, Alexander and Payer, Christian and 
              Urschler, Martin and others},
      journal={arXiv preprint arXiv:2001.09193},
      year={2020}
    }
    

# Variances release

In code/models/pca_variances.txt we release the computed variances. They allow to reproduce the Cumulative relative variance plot in Fig. 2.