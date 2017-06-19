
Description of directories
==========================

bin: tracks evaluation scripts
donloaded: files downloaded from zenodo
log: logs from `get_zenodo.py` and tracks 
output: results of the evaluations


Evaluation
==========

We developed the evaluation of the Zero Speech Challenge as a two component 
system, the fist one is the a producer that query and download the iformation
from zenodo, the second part is a consumer that makes the evaluations of 
the track 1&2.


Query and donwloading zenodo
----------------------------


```
    $ conda create --name zsc_zenodo --file requirements_3.txt
```

To query and download the doi files you will need to set your own 
varibles (directories, zenodo keys, etc) in the `config` file, 
after you can call `zsc_zenodo` that is a wrap around the python
script ``zsc_zenodo.py. If you are doing crontab each half an hour follow 
these commands:


```
    $ crontab -e
    Edit ...
    */30 * * * * cd /fhgfs/bootphon/scratch/jbenjumea/sandbox/zsc_zenodo && bash get_zenodo 
```

Evaluation
----------


Track 1
~~~~~~~

Track 2 
~~~~~~~


It uses python 2.7, you will need to run the following commands to install
the libraries that this track uses:


```
    $ conda create --name zsc_eval_track2 python=2
    $ source activate zsc_eval_track2
    $ conda install --file requirements_2.txt
    $ pip install cx-Freeze==5.0.1
    $ pip install git+https://github.com/bootphon/tde.git@zerospeech2017

```


To run the evaluation of track-2 you need to decrypt and decompress the files
in in `zsc_zenodo/bin/track2`, follow the decrypt part of the following commands:

```
    # the file resources.tar.enc was crypted using
    $ tar c resources | openssl enc -aes-256-cbc -e > resources.tar.enc 

    # decrypt
    $ openssl enc -aes-256-cbc -d -in resources.tar.enc | tar x
    $ cd resources
    $ bunzip2 *
```

The password is under request (boXXXXX12)

to run the evaluation do for example:
```
    $ source activate zsc_eval_track2
    $ CORPUS='LANG2' python bin/track2/eval2.py -v output/8321/track2/LANG2.txt output/8321/track2/LANG2_out 

```


