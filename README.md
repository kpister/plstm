### Protein Name Recognition

This project uses a keras LSTM to learn protein names.


### Utils

In utils there are a collection of python files.

`generator.py` will convert paragraphs to n-gram line separated files.

`sample.py` will randomly select from a line separated file into a set amount.

`length.py` will normallize line length.

### Project Roadmap

* Project
    * Protein Name Prediction
        * - [ ] Connect to GPU, train more
        * - [ ] Train with concat(protein, normal) as negatives
        * - [ ] Train on full patents
        * - [ ] Investigate tensorflow estimators
        * - [ ] Variable length LSTM input
        * - [x] Finish pipeline
        * - [ ] AUC Graphing
        * - [ ] Clean XML parsing
            * - [ ] Compile problematic patents
        * - [ ] Graph false positives and false negatives
            * - [ ] investigate what causes them at each epoch
        * - [ ] Multithread
            * - [ ] Figure out with multiple keras instances
    * Uniprot Query (normalizing names)
        * - [ ] Investigate Siamese Netorks in [this paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/cikm2013_DSSM_fullversion.pdf)
        * - [ ] Build RNN->MLP network to classify "sameness"
        * - [ ] Investigate UNIPROT API


* Thesis Paper
    * - [ ] Collect references
    * - [ ] Start writing

