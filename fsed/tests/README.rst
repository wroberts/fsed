=======
 Notes
=======

On Mac OS X, generate reference output::

    gunzip -c fsed-testinput.utf8.txt.gz | perl fsed-testpats.utf8.pl | gzip > perl-output.utf8.txt.gz
    gunzip -c fsed-testinput.utf8.txt.gz | sed -E -f fsed-testpats.wb.bsd.utf8.sed | gzip > sed-output.utf8.txt.gz

On Mac OS X, generate test output::

    gunzip -c fsed-testinput.utf8.txt.gz | fsed -w fsed-testpats.tsv.gz > fsed-tsv-output.utf8.txt
    gunzip -c fsed-testinput.utf8.txt.gz | fsed fsed-testpats.wb.sed.gz > fsed-sed-output.utf8.txt
    cd ../..
    gunzip -c fsed/tests/fsed-testinput.utf8.txt.gz | python3.4 -m fsed.fsed fsed/tests/fsed-testpats.wb.sed.gz > fsed/tests/fsed-sed-output.utf8.txt
