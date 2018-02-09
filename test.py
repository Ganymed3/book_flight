#!/usr/bin/env python3

'''
    Simple test of receiving fastest/cheapest results. Run this script with
    the same arguments as book_flight.py. Use --cheapest or --fastest option.

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
import pprint

# ==============================================================================
# Run the script
# ==============================================================================

c_CURRENCY  = 'CZK'
c_LIMIT = 50      # Number of search results

def test():
   """ Test if the cheapest or fastest flights are found by search_flight() """

   # Booking object
   bf = BookFlight()
   
   # Load arguments
   bf.load_args()
   
   # Find N flights
   bf.iprint( "Searching", c_LIMIT, "flights..." )
   bf.search_flight( _limit = c_LIMIT, _currency = c_CURRENCY )
   
   #pprint.pprint(bf.search_result.json())

   resp_json = bf.search_result.json()

   if '_results' in resp_json:
      n = int(resp_json['_results'])
      print ("Found", n, "results:", "\n")

   price_list = []
   duration_list = []

   # ['data'][n] is one flight record
   if 'data' in resp_json:
      data = resp_json['data']
      
      if n > 0 and len(data) > 0:
         for result_i in data:
            if 'duration' in result_i:
               duration_list.append(result_i['duration']['total'])
            else:
               print ("ERROR: No 'fly_duration' in result_i")

            if 'price' in result_i:
               price_list.append(result_i['price'])
            else:
               print ("ERROR: No 'price' in result_i")
            
      else:
         print ("ERROR: n < 0 or len(data) < 0")
   else:
      print ("ERROR: 'data' is not in resp_json")

   #price_list.append(100)  # Try raise order error
   #duration_list.append("1h 10m")  # Try raise order error

   # Check if the lists are ordered
   p_ordered = all( price_list[i] <= price_list[i+1] for i in range(len(price_list)-1) )
   d_ordered = all( duration_list[i] <= duration_list[i+1] for i in range(len(duration_list)-1) )
   
   print ("Price list:", "\n===================")
   print (price_list, "\n")
   print ("Is PRICE list ordered? ", p_ordered, "\n")
   
   print ("Duration list:", "\n===================")
   print (duration_list, "\n")
   print ("Is DURATION list ordered? ", d_ordered, "\n")

   # Compare with script arguments
   if bf.args.fastest:
      if d_ordered:
         print ("OK: FASTEST flights searched and results are ordered")
      else:
         print ("ERROR: FASTEST flights searched BUT results are NOT ordered!")
   else:
      if p_ordered:
         print ("OK: CHEAPEST flights searched and results are ordered")
      else:
         print ("ERROR: CHEAPEST flights searched BUT results are NOT ordered!")


# Run the script
test()



# End of file



