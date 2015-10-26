# Subject patterns in MARC records

A study in subjects present in a large set of MARC records (roughly
900,000).  Uses [Apache Spark](http://spark.apache.org/) to process
the resulting dataset representing one row for every subject across
all those records (n=8,357,060).  This is a little more data than
basic R is comfortable with, so Spark and PySpark give us a nice
set of tools to scale up a little bit and summarize patterns
efficiently , using more than one core but still only one machine.


## Process - data prep

This notebook begins from an assumption that a pile of MARC records
is available.  In our case, we had an extract of files containing
2,500 records each in MARC binary, spread across several directories.
To extract subjects from them into CSV , I ran the ```marc2csv.py```
script, which requires ```pymarc```, on the MARCXML output of
[MarcEdit](http://marcedit.reeset.net/)'s conversion step, which
handled character encoding issues correctly so I didn't have to.
With hundreds of individual files, and a laptop with four cores, I
was able to parallelize this operation using [GNU
Parallel](http://www.gnu.org/software/parallel/).  For example, to
invoke ```marc2csv.py``` on one file:

    % ./marc2csv.py my-records.mrc.xml extracted-subjects.csv

To invoke it using ```parallel``` on hundreds of files:

    % ls *.mrc.xml | parallel -j+0 --eta './marc2csv.py {} csv_extracts/`basename {.}`.csv'

This will result in one csv output file for every input file, generated
using all of the available cores on your machine.  It should give you
linear speedup.

Once that step is complete (it took about 15 minutes on my laptop, which
is much better than an hour), you can combine the output with a simple
redirection step:

    % cat *.csv >> all-extracted-subjects.csv

If that resulting file is big (millions of rows, rather than
thousands), something like Spark might be helpful.  If it's not
quite so big, your favorite tool (R, Python, what have you) will
probably handle it just fine.


## Process - basic analysis with Spark

See the Jupyter notebook in this directory for the rest.


## Requirements

The ```marc2csv.py``` python script requires
[pymarc](https://github.com/edsu/pymarc).

The Jupyter notebook requires a working Spark installation and a
kernel for Jupyter to be installed correctly.  [These
instructions](http://thepowerofdata.io/configuring-jupyteripython-notebook-to-work-with-pyspark-1-4-0/)
helped me with that step quite a lot. For what it's worth, I ran
this on an OSX 10.10 laptop with apache-spark installed via
[homebrew](http://brew.sh/), Jupyter installed via
[Anaconda](https://www.continuum.io/why-anaconda), and the following
kernel installed in ```~/.ipython/kernels/pyspark/kernel.json```:

```json
    {
        "display_name": "pySpark (Spark 1.5.1)",
        "language": "python",
        "argv": [
            "/Users/dchud/anaconda/bin/python2",
            "-m",
            "IPython.kernel",
            "-f",
            "{connection_file}"
        ],
        "env": {
            "SPARK_HOME": "/usr/local/Cellar/apache-spark/1.5.1/libexec",
            "PYTHONPATH": "/usr/local/Cellar/apache-spark/1.5.1/libexec/python/:/usr/local/Cellar/apache-spark/1.5.1/libexec/python/lib/py4j-0.8.2.1-src.zip",
            "PYTHONSTARTUP": "/usr/local/Cellar/apache-spark/1.5.1/libexec/python/pyspark/shell.py",
            "PYSPARK_SUBMIT_ARGS": "pyspark-shell"
        }
    }
```
