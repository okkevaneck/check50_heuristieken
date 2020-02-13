# Check50 for Heuristics
**Author:** Okke van Eck  
**Check50 Docs:** https://cs50.readthedocs.io/check50/

#### Setup
You must have python3 installed and a possibility for creating a virtual
environment. The example below uses the python3-venv package, but you can use
your own as well.

###### Install packages.
`sudo apt-get install python3 python3-venv`

###### Create virtual environment and activate it.
```shell script
python3 -m venv venv
source venv/bin/activate
```

###### Install requirements.
`pip install -r requirements.txt`


#### Run
To run a check50, `cd` into the directory of the case you want to test. Let's
denote the folder name of the case as `<case>`.    
Then you can run the check on the CS50 servers via the command:  
`check50 OkkeVanEck/cs50_heuristieken/master/<case>`.  
You can also run the check locally by specifying the `--local` flag.