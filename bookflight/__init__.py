
'''
    File name: __init__.py
    Author: Miroslav Macek, macekmirek (at) email.cz
    Date created: 9/02/2018
    Python Version: 3.5.2
'''

# ==============================================================================
# Libraries
# ==============================================================================
import argparse                        # Script parameters parser
import requests                        # HTTP requests, JSON
import datetime
import pprint                          # Debug only
import json
from time import sleep
import sys                             # sys.stderr

# ==============================================================================
# Classes
# ==============================================================================

class BookFlight(object):
   """ Main booking flight class """

   def __init__(self):
      self.args = []                # Parsed arguments
      self.search_result = {}       # Search result
      self.check_result  = {}       # Check result
      self.book_result   = {}       # Book result
      self.token = 0                # booking_token received from search_flight
      self.search_price  = 0        # Stored from search response
      self.check_price   = 0        # Stored from check response
      self.search_currency = 0      # Stored from search response
      self.check_currency  = 0      # Stored from check response
      self.search_duration = 0      # Stored from search response
      self.book_pnr      = 0        # Booking PNR code
      self.error         = False
      self.check_attempts= 30      # How many attempts when checking the flight
      self.check_wait    = 10       # Wait in seconds between attempts
      # API Endpoints
      self.c_EP_FLIGHTS = 'https://api.skypicker.com/flights?'
      self.c_EP_CHECK   = 'https://booking-api.skypicker.com/api/v0.1/check_flights?'
      self.c_EP_SAVE_BOOKING = 'https://booking-api.skypicker.com/api/v0.1/save_booking?'
      self.c_EP_BOOK    = 'http://128.199.48.38:8080/booking'
      self.c_HEADERS    = { 'Content-Type': 'application/json' }
      self.c_BAGS_MAX   = 4

   def load_args (self):
      """ Load program arguments 
        
      """
      self.error = False

      # -- Parser configuration ------------------------------------------------
      parser = argparse.ArgumentParser(
         description="This program finds and books the flights.")
      
      # DATE: mandatory, 1 arg (date)
      parser.add_argument(
         '--date', help='departure date in the format YYYY-MM-DD', type=str,
         nargs=1, required=True
      )
      
      # FROM: mandatory, 1 arg (string)
      parser.add_argument(
         '--from', help='IATA code of the departure airport', type=str, nargs=1,
         required=True, dest="from_iata"
      )
      
      # TO: mandatory, 1 arg (string)
      parser.add_argument(
         '--to', help='IATA code of the arrival airport', type=str, nargs=1,
         required=True, dest="to_iata" 
      )
      
      # BAGS: optional, 1 arg (int), default 0
      parser.add_argument(
         '--bags', help='specify the number of bags', type=int, default=0,
         nargs=1
      )
      # VERBOSE: optional, 0 arg
      parser.add_argument(
         '-v', '--verbose', help='prints additional info', action="store_true"
      )
      # DEBUG: optional, 0 arg
      parser.add_argument(
         '--debug', help='prints debug info', action="store_true"
      )
      
      # Exclusive groups
      group_way = parser.add_mutually_exclusive_group()
      # ONE-WAY: optional, exclusive, 0 arg
      group_way.add_argument(
         '--one-way', help='(default) one-way flight option',
         action="store_true", dest="one_way"
      )
      
      # RETURN: optional, exclusive, 1 arg (int)
      group_way.add_argument(
         '--return', help='return flight option', type=int, nargs=1,
         dest="return_n"
      )
      
      group_type = parser.add_mutually_exclusive_group()
      # CHEAPEST: optional, exclusive, 0 arg
      group_type.add_argument(
         '--cheapest', help='(default) choose the cheapest flight',
         action="store_true"
      )
      # FASTEST: optional, exclusive, 0 arg
      group_type.add_argument(
         '--fastest', help='choose the fastest flight', action="store_true"
      )
      
      # -- Save parsing result -------------------------------------------------
      self.args = parser.parse_args()
      
      # -- Validation - check arguments value ----------------------------------
      # DATE
      try:
         test_date = datetime.datetime.strptime(self.args.date[0], "%Y-%m-%d")
      except ValueError:
         self.eprint("Invalid value of DATE argument.")

      # FROM, TO - 3 IATA code chars
      if len(self.args.from_iata[0]) != 3:
         self.eprint("Invalid IATA code in FROM argument.")
      if len(self.args.to_iata[0]) != 3:
         self.eprint("Invalid IATA code in TO argument.")
         
      # RETURN
      if self.args.return_n:                    # optional argument
         if self.args.return_n[0] < 0:
            self.eprint("Invalid nights count in RETURN argument",
                        "(Time travel into the past is not allowed.)")

      # BAGS
      if self.args.bags:                    # optional argument
         if self.args.bags[0] < 0:
            self.eprint("Invalid bags count in BAGS argument",
                        "(Antimatter on board is not allowed.)")
         elif self.args.bags[0] > self.c_BAGS_MAX:
            self.eprint("Invalid bags count in BAGS argument",
                  "(Maximum bags is", self.c_BAGS_MAX, "per one person)")
            
   # End of load_args




   def search_flight (self, _limit=1, _currency='EUR'):
      """ Search the flight based on the program arguments
      
          Arguments:
            _limit     (int): Limit of search results
            _currency  (str): Currency
            
          Return:
            (str): Booking token. Returns 0 if no token has been found
      """
      
      # -- Collect all Kiwi API flights parameters -----------------------------
      
      # Kiwi API flight parameters associative array {'param' : 'value'}
      param = {} 
      
      # Required parameters
      param['flyFrom'] = self.args.from_iata[0]
      param['to']      = self.args.to_iata[0]
      
      date = datetime.datetime.strptime(self.args.date[0], "%Y-%m-%d")
      date_str = date.strftime("%d/%m/%Y")
      param['dateFrom']       = date_str
      param['dateTo']         = date_str
      param['partner']        = 'picky'
      #param['partner_market'] = 'us'            # Required?
      
      # Optional parameters
      # RETURN vs ONEWAY
      if self.args.return_n:
         date_return = date + datetime.timedelta(days = self.args.return_n[0])
         date_return_str = date_return.strftime("%d/%m/%Y")
         param['returnFrom'] = date_return_str
         param['returnTo']   = date_return_str
         param['typeFlight'] = 'round'
      else:
         param['typeFlight'] = 'oneway'         # Default option

      # FASTEST vs CHEAPEST
      # NOTE: In general the checked flight can be cheaper than the searched
      #       one due to different price of baggage. But the description
      #       of assignment is not clear.
      if self.args.fastest:
         sort = 'duration'
      else:
         sort = 'price'             # Default option

      param['sort']  = sort
      param['asc']   = '1'          # 1 = ascending
      param['limit'] = _limit       # count of results
      param['curr']  = _currency   
      
      # -- Send HTTP request ---------------------------------------------------
      self.search_result = self._send_request(self.c_EP_FLIGHTS, param)
      
      # Obtain 'booking_token'
      try:
         json = self.search_result.json()
      except Exception as e:
         json = {}
         self.eprint("JSON: Invalid received data: EXCEPTION:", str(e) )
      
      try:
         self.token = json['data'][0]['booking_token']
      except (IndexError, KeyError):
         self.token = 0
         self.eprint("booking_token was not found in the search response")
               
      
      # Just for information
      try:
         self.search_currency = json['currency']
         self.search_price    = json['data'][0]['price']
         self.search_duration = json['data'][0]['fly_duration']
      except (IndexError, KeyError):
         self.iprint("currency/price/fly_duration not found in search response")

      # Debug purposes
      if self.args.debug:
         pprint.pprint(self.search_result.url)
         pprint.pprint(self.search_result.json())
      
      return self.token
   # End of search_flight




   def check_flight (self, _token, _currency='EUR'):
      """ Check the flight based on search response
          
          Arguments:
            _token     (str): booking_token
            _currency  (str): Currency
      
          Return:
            (bool): flights_checked,
            (bool): flights_invalid
      """

      # -- Collect all required Kiwi API check_flights parameters --------------
      
      # Kiwi API check_flights parameters associative array {'param' : 'value'}
      param = {}
            
      if self.args.bags:
         bags = self.args.bags[0]
      else:
         bags = 0
      
      param['booking_token']  = _token
      param['bnum']           = bags
      param['currency']       = _currency
      param['pnum']           = 1            # Number of passengers
      param['affily']         = 'picky_us'
      param['v']              = 2
      
      # -- Send HTTP request ---------------------------------------------------
      # You need to repeat the check_flights until the value is True
      attempt   = self.check_attempts
      f_ch      = None
      f_i       = None
      
      while True:
         f_ch, f_i = self._send_check_flight(param)
         
         
         if f_ch == True and f_i == False:
            # Successfull response
            
            # Debug purposes
            if self.args.debug:
               pprint.pprint(self.check_result.url)
               pprint.pprint(self.check_result.json())
               
            break
         elif f_i == True:
            # Invalid flight
            self.eprint ('Flight is not bookable anymore: flights_invalid =',
                           f_i, '. Ending...')
            break
         elif self.error:
            # Some HTTP request error
            break
         else:
            if attempt <= 0:
               # Too much attempts => Give it up
               self.eprint ('Unsuccessful. Ending...:', 'flights_checked =',
                            str(f_ch), ', flights_invalid =', str(f_i) )
               break
            else:
               # Repeat after some delay
               self.iprint('Attempts left:', str(attempt),
                           '. Waiting for', str(self.check_wait), 'seconds...')
               attempt -= 1
               sleep(self.check_wait)
               
      return f_ch, f_i
   # End of check_flight




   def book_flight (self, _token, _currency, _passenger):
      """ Book the flight based on check response
         
          Arguments:
            _token     (str):       booking_token
            _currency  (str):       Currency abv.
            _passenger (Passenger): Passenger object
            
          Return:
            (str): PNR booking code
      """

      # -- Collect all required Kiwi API book data -----------------------------
      p = {}
      p['documentID'] = _passenger.id
      p['lastName']   = _passenger.last_name
      p['title']      = _passenger.title
      p['birthday']   = _passenger.birthday
      p['firstName']  = _passenger.first_name
      p['email']      = _passenger.email
      
      data = {}
      data['currency']        = _currency
      data['passengers']      = [p]
      data['booking_token']   = _token
      data['bags']            = self.args.bags[0]
            
      data_json = json.dumps(data)
      
      # Send JSON data by POST method
      try:
         self.book_result = requests.post( self.c_EP_BOOK, data=data_json,
                                           headers=self.c_HEADERS )
      except Exception as e:
         self.eprint( 'EXCEPTION: ' + str(e) )
      
      # Debug purposes
      if self.args.debug:
         pprint.pprint(json.dumps(data))
         pprint.pprint(self.book_result)
         pprint.pprint(self.book_result.status_code)
         pprint.pprint(self.book_result.json())
      
      try:
         resp_json = self.book_result.json()
      except Exception as e:
         resp_json = {}
         self.eprint("JSON: Invalid received data: EXCEPTION:", str(e) )
            
      # Check status
      if 'status' in resp_json:
         if resp_json['status'] == 'confirmed':
            self.iprint('Booking status is confirmed.')
         else:
            self.eprint('Booking status is invalid:', resp_json['status'])
      else:
         self.eprint("Booking response doesn't contain confirmation status.")
      
      # Check PNR
      pnr = "0"
      
      if 'pnr' in resp_json:
         pnr = resp_json['pnr']
         self.iprint('PNR: ', pnr)
      else:
         self.eprint("Booking response doesn't contain PNR code.")
   
      return pnr
   # End of book_flight   




   def eprint(self, *_args, **_kwargs):
      """ Prints message on the stderr and sets self.error attribute
          Arguments: Same as print()
      """
      self.error = True
      if self.args.verbose:
         print('ERROR:', *_args, file=sys.stderr, **_kwargs)
   # End of eprint




   def iprint(self, *_args, **_kwargs):
      """ Prints message on the stdout if VERBOSE argument is True
          Arguments: Same as print()
      """
      if self.args.verbose:
         print('INFO:', *_args, file=sys.stderr, **_kwargs)
   # End of iprint


   
   
   """ -- PRIVATE -- """
   
   def _send_request(self, _ep, _params):
      """ Create and send HTTP request
         
          Arguments:
            _ep     (str):  API Endpoint
            _params (dict): Request parameters
      
          Returns:
            (Response): Response from the server
      """
      resp = requests.Response()
      try:
         resp = requests.get( _ep, params = _params,
                              headers = self.c_HEADERS )
      except Exception as e:
         self.eprint( 'EXCEPTION: ' + str(e) )
      
      return resp
   # End of _send_request
   
   
   
   
   def _send_check_flight(self, _params):
      """ Sends and checks check flight request
         
          Arguments:
            _params (dict): Request parameters
      
          Returns:
            (bool): flights_checked
            (bool): flights_invalid
      """
      f_ch      = None
      f_i       = None
   
      # Send request
      self.check_result = self._send_request(self.c_EP_CHECK, _params)
         
      f_ch_str = 'flights_checked'
      f_i_str  = 'flights_invalid'
      
      try:
         json = self.check_result.json()
      except Exception as e:
         json = {}
         self.eprint("JSON: Invalid received data: EXCEPTION:", str(e) )
      
      # Check response fields
      if f_ch_str in json:
         f_ch = json[f_ch_str]
      else:
         self.iprint("WARNING: flights_checked was not found in the check",
                     "response")

      if f_i_str in json:
         f_i = json[f_i_str]
      else:
         self.iprint("WARNING: flights_invalid was not found in the check",
                     "response")
   
      if f_ch == True and f_i == False:
         # Successfull response
         self.iprint('Successful check response:',
               'flights_checked =', str(f_ch),
               ', flights_invalid =', str(f_i) )
         
         # Just for information
         if 'currency' in json['conversion']:
            self.check_currency = json['conversion']['currency']
         else:
            self.iprint("currency was not found in the check response")
         
         if 'amount' in json['conversion']:
            self.check_price = json['conversion']['amount']
         else:
            self.iprint("amount was not found in the check",
                        "response")
      else:
         # Unsuccessfull response
         self.iprint('Unsuccessful check response:',
               'flights_checked =', str(f_ch),
               ', flights_invalid =', str(f_i) )

      return f_ch, f_i
   # End of _send_check_flight
   
   
   

class Passenger(object):
   """ Passenger's data class """
   
   def __init__(
      self,
      _id         = 0,
      _last_name  = "",
      _first_name = "",
      _birthday   = "",
      _title      = "",
      _email      = "",
   ):
      self.id           = _id
      self.last_name    = _last_name
      self.first_name   = _first_name
      self.birthday     = _birthday
      self.title        = _title
      self.email        = _email
      
      
      

# End of file



