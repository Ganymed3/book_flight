# book_flight

Python script for searching and booking flights. Script uses [Kiwi API](https://skypickerpublicapi.docs.apiary.io/#reference/flights) for the main three steps:
   1. Search flight - Searches the cheapest or fastest flight from desired location to another.
   2. Check flight - Checks for the possibility of booking a flight and calculates the total price. Number of bags is taken into account. This process may take a while (from 10 seconds to a few minutes).
   3. Book flight - Books the checked flight and returns PNR code.

The output of the script is PNR code if booking is succesfull. The "0" string is printed in case of any error. You can use --verbose/-v option to show additional informations during the process.

### Download
Checkout Git repository:
```
git clone https://github.com/Ganymed3/book_flight.git
```

### Requirements
Required Python >= 3.5.2

To install required modules run:

pip install --requirement requirements.txt

### Script usage
Run the script:
```
./book_flight.py OPTIONS
```
or
```
python3 book_flight.py OPTIONS
```

#### --help, -h
Prints the help with all options list

#### --date DATE
Departure date in the YYYY-MM-DD format

#### --from IATA
IATA code of the departure airport

#### --to IATA
IATA code of the arrival airport

--date, --from and --to options are mandatory.
Example:
```
./book_flight.py --date 2018-04-13 --from BCN --to DUB
```

#### --one-way
Book a one way flight. The default option, implicitly used if no --one-way or --return is specified.
Example:
```
./book_flight.py --date 2018-04-13 --from BRQ --to DUB --one-way
```

#### --return N
Book a return flight. It requires argument N which specifies number of nights in the destination. This is an exclusive option to --one-way.
Example:
```
./book_flight.py --date 2018-04-13 --from PRG --to DME --return 5
```

#### --cheapest 
Choose the cheapest flight. The default option, implicitly used if no --cheapest or --fastest is specified.
Example:
```
./book_flight.py --date 2018-04-13 --from NRT --to SYD --cheapest
```

#### --fastest
Choose the fastest flight. This is an exclusive option to --cheapest.
Example:
```
./book_flight.py --date 2018-04-13 --from DUB --to JFK --fastest
```

#### --bags
Specifies number of bags. Default value is 0 if not specified.
Example:
```
./book_flight.py --date 2018-04-13 --from BTS --to LIS --cheapest --return 7 --bags 1
```

#### --verbose, -v
If used, the script prints additional info about the booking process and evantually error messages.

#### --debug
Prints HTTP requests and responces for the debugging purposes.


### Testing
There is a simple test to check that search flights API returns ordered results. To check this just run the test.py script with the same arguments as book_flight.py and see printed informations. 
Example:
```
./test.py  --date 2018-03-22 --from PRG --to LIS --fastest
./test.py  --date 2018-03-22 --from PRG --to LIS --cheapest
```


### Author
Miroslav Macek
[email](macekmirek@email.cz)



