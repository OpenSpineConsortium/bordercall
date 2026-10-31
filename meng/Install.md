## Installation

Back to the main [README](README.md).

### Downloading the repository

To donwload the repository, please use the https protocol:

```
git clone https://gitlab.inria.fr/spine/spine_model.git 
```

### Installing on a virtual environment

#### PyEnv

It is recommended to use a virtual environment to install this package - but not mandatory.
We recommend using [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv).
The instructions are well detailed [here](https://realpython.com/intro-to-pyenv/#installing-pyenv).

Then go to the base repository folder and

```
pyenv install -v 2.7.16
pyenv virtualenv 2.7.16 spine_model
pyenv local spine_model
```

#### Other Requirements
Then install the basic requirements.txt

```
pip install -r requirements.txt
```


#### Mesh Package

Now install an **old** [PS Body Mesh package](https://github.com/MPI-IS/mesh) from the given
[precompiled sources](https://github.com/MPI-IS/mesh/releases/tag/v0.1):

Mac Osx:
```
pip install https://github.com/MPI-IS/mesh/releases/download/v0.1/psbody_mesh-0.1-cp27-cp27m-macosx_10_11_intel.whl
```

or Linux:
```
pip install https://github.com/MPI-IS/mesh/releases/download/v0.1/psbody_mesh-0.1-cp27-cp27mu-linux_x86_64.whl
```


#### SMPL load function

The last needed code is the SMPL load function (serialization).
To get it:
  * [Register](https://smpl.is.tue.mpg.de)
  * [Login](https://smpl.is.tue.mpg.de/en/sign_in)
  * Download the "Download version 1.0.0 for Python 2.7 (10 shape PCs)"
  * Copy the `smpl_webuser` folder into the `code` folder of the repository 
  

That's it! You should be setup and ready to run the code!

Check out the [QuickStart](QuickStart.md) file.