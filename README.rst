==================================================================
pyhll - simple library for cardinality detection using HyperLogLog
==================================================================

CI status: |cistatus|

.. |cistatus| image:: https://secure.travis-ci.org/blackwithwhite666/pyhll.png?branch=master

pyhll can be used to compute cardinality, i.e. the unique number of elements in some set using HyperLogLog.
This library is a thin python wrapper around HyperLogLog implementation in https://raw.github.com/armon/hlld

Installing
==========

pyhll can be installed via pypi:

::

    pip install pyhll


Building
========

Get the source:

::

    git clone https://github.com/blackwithwhite666/pyhll.git


Compile extension:

::

     python setup.py build_ext --inplace



Usage
=====

::

    from pyhll import Cardinality
    c = Cardinality()
    c.add(b'foo')
    assert 1 == len(c)
    c.add(b'bar')
    assert 2 == len(c)
    c.add(b'bar')
    assert 2 == len(c)
    c.update([b'bar', b'buzz'])
    assert 3 == len(c)


Running the test suite
======================

Use Tox to run the test suite:

::

    tox


References
==========

Here are some related works which we make use of:

* HyperLogLog in Practice: Algorithmic Engineering of a State of The Art Cardinality Estimation Algorithm : http://research.google.com/pubs/pub40671.html
* HyperLogLog: The analysis of a near-optimal cardinality estimation algorithm : http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.142.9475
