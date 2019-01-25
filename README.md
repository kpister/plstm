### Protein Name Recognition

This project uses a keras LSTM to learn protein names.


### Utils

In utils there are a collection of python files.

`generator.py` will convert paragraphs to n-gram line separated files.

`sample.py` will randomly select from a line separated file into a set amount.

`length.py` will normallize line length.

### Project Roadmap

* - [ ] Project
    * - [ ] Protein Name Prediction
        * - [ ] Investigate tensorflow estimators
        * - [ ] Variable length LSTM input
        * - [ ] Finish pipeline
        * - [ ] Clean XML parsing
        * - [ ] Graph false positives and false negatives
            * - [ ] investigate what causes them at each epoch
        * - [ ] 
    * - [ ] Uniprot Query
        * - [ ] Investigate Siamese Netorks in [this paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/cikm2013_DSSM_fullversion.pdf)


* - [ ] Thesis Paper
    * - [ ] Collect references
    * - [ ] Start writing

