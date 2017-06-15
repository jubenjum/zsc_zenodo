

# crontab each half an hour

do
```
    $ crontab -e
    Edit ...
    */30 * * * * cd /fhgfs/bootphon/scratch/jbenjumea/sandbox/zsc_zenodo && bash get_zenodo >> log/crontab.log
```
