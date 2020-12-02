## Setup Notes

In order to run this project locally I had to make a few changes

### Environment
I use venv to create a python virtual environment to contain all of the packages used for this project. This [link](https://docs.python.org/3/library/venv.html) was helpful in getting setup


### Requirements
The original repo had no requirements.txt file, and although they listed some requirements on the page they were outdated. I ended up just including torch, torchtext, and clicked(v6.7) and everything seems be working. Install with `pip install -r requirements.txt`


### Dataset
The original provider of the dataset from Facebook has broken so I had to use [Archive.org](https://archive.org) in order to get a download of the file. The issue continues, however, because TorchText tries to use the original download link. I modified the torchtext code (go to your virtual environment, then `lib/python3.8/site-packages/torchtext/datasets/babi.py`) to use my url `https://github.com/cameronbracco/MemN2N/raw/master/tasks_1-20_v1-2.tar.gz'`, but it was still failing. I then just tried manually extracting and placing the dataset in `.data/` and that seems to have worked. It's unclear if the other step would be necessary but I'm leaving it for now because it's working.


### Running
It wasn't incredibly clear from the outset how I would run the saved versions of the models to verify the reported performance. This is what seems to be working to run the first task and get 0.1 for the average error.
- Note that if you don't specific which representation to use your error rate will be all over the place
- Note that there will be a bunch of warnings from torchtext (TODO: Figure out a way to supress these)

`python3 cli.py --file BoW_3HOPS/task1 --task 1 --use_bow`
