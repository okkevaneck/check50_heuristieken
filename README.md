# Check50 for Heuristics
**Author:** Okke van Eck  
**Check50 Docs:** https://cs50.readthedocs.io/check50/  
**Note:** All `test.py` files are ignored!  

#### Setup check environment.
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


#### Run checks.
It is possible to run the check50 tests via the online version on GitHub, or
locally in a development environment. The different options are separated in 
sections. For all checks, you must be in the folder of the check itself. So
`cd` into the directory of the case you want to test. Let's
denote the folder name of the case as `<case>`.    

###### Run on the check50 servers.
You can run the checks on GitHub on the check50-servers by running the command:  
`check50 OkkeVanEck/cs50_heuristieken/master/<case>`

###### Run locally
You can run the checks on GitHub locally by running the same command with the
`--local` flag specified:  
`check50 --local OkkeVanEck/cs50_heuristieken/master/<case>`

###### Run local code
You can run your local version of the checks by running `check50` with the 
`--dev` flag:  
`check50 --dev .`


### Required case changes
There are some changes required for the cases. The changes are de described 
below, devided by case.

##### Protein Powder
- Remove spaces behind comma's in output.csv
- Add a footer to output.csv with the score: `score,<integer>`

##### AmstelHaege
- Remove spaces behind comma's in output.csv
- Ask for all four corners in order instead of two
    - Rename header to structure,corner_1,corner_2,corner_3,corner_4,type
- Add a footer to output.csv with the networth: `networth,<integer>`
