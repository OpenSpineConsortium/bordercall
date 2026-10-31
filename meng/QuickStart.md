# Quick Start Guide

Please make sure you followed the [Install](Install.md) instructions.
Then come back to run the demo.

Back to the main [README](README.md).

## Running the Spine Model demo

To run the demo code, go to the code folder: 
```
cd code
```

Then, for the Global rotation demo run:
```
python spine_model_demo.py -R
```


The full demo includes the global and local rotations, the shape space, 
the individual joint locations and all joints at the same time. 

```
python spine_model_demo.py -R -r -B -I -J
```


## Running the reconstruction demo

The model can also reconstruct a full spine from a partially observed spine.
In this demo we progressively mask the cervicals and reconstruct them.

Test first that the reconstruction with the PPCA mean works.
Reconstructions should be perfect (zero error)
```
python spine_completion_demo.py -M
```

Then you can test reconstructions from the model. 

```
python spine_completion_demo.py
```

You can modify the beta parameter (line 204) of the model to obtain
different meshes and reconstruction settings.