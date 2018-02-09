#!/usr/bin/env python3

'''
    File name: book_flight.py
    Author: Miroslav Macek, macekmirek (at) email.cz
    Date created: 9/02/2018
    Python Version: 3.5.2
'''

# ==============================================================================
# Libraries
# ==============================================================================
from bookflight import BookFlight   # Book flight implementation
from bookflight import Passenger    # Passenger class (data structure)

# ==============================================================================
# Run the script
# ==============================================================================

c_ERROR_OUTPUT = 0          # Print in case of error 

# Required booking informations
c_CURRENCY  = 'CZK'
c_PASSENGER = Passenger (
   _id         = "001",
   _last_name  = "2X4C",
   _first_name = "Kryton",
   _birthday   = "2980-04-06",
   _title      = "Mr",
   _email      = "kryton@reddwarf.space"
)

def main():
   """ The main script function """

   # Booking object
   bf = BookFlight()
   
   # Load arguments
   bf.load_args()
   check_error( bf.error )

   # Search the flight
   bf.iprint( "Searching flight..." )
   token = bf.search_flight( _currency = c_CURRENCY )
   bf.iprint( 'booking_token =', token )
   bf.iprint( 'Searched price =', bf.search_price, bf.search_currency )
   bf.iprint( 'Searched fly_duration =', bf.search_duration )
   check_error( bf.error )
   
   # Check the flight
   bf.iprint( "Checking flight..." )
   bf.check_flight( token, _currency = c_CURRENCY )
   bf.iprint( 'Checked price =', bf.check_price, bf.check_currency )
   check_error( bf.error )

   # Book the flight
   bf.iprint( "Booking flight..." )
   pnr = bf.book_flight( token, c_CURRENCY, c_PASSENGER )
   check_error( bf.error )
   
   # Print PNR code
   print( pnr )
      

def check_error( err ):
   """ In case of error prints error value and exits script """
   if err:
      print ( str(c_ERROR_OUTPUT) )
      exit()   


# Run the script
main()



# End of file



