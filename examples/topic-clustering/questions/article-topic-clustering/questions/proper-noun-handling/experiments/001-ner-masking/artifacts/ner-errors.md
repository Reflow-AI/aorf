# Where NER masking helped and hurt

Sampled 40 article pairs that the baseline placed in different clusters but the evaluation set
labels as the same topic.

| Pattern | Pairs | Effect of masking |
|---|---|---|
| Different analyst quoted, same subject | 11 | merged correctly |
| Different local official named, same policy | 7 | merged correctly |
| Different company, same sector event | 9 | merged **incorrectly** — these are different topics |
| Subject organisation is the topic | 8 | split **incorrectly** — signal removed |
| No proper nouns involved | 5 | unchanged |

The two incorrect rows roughly cancel the two correct ones, which is why the aggregate moved 0.01.

An aggregate metric alone would have read as "masking does nothing". The breakdown shows something
more useful: masking does two opposite things, and the question is how to tell the cases apart.
