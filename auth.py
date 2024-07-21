from kite_trade import *
import os

#option1: # This method will logout from kite web
user_id = "" #XXXXXX
password = "" #kite password
twofa = "" # app code, or other twofa

# enctoken = get_enctoken(user_id, password, twofa)


#option2: easier way is to use enctoken. Copy it from kite web cookies/API header.
# This method will not logout from kite web
# setup ENC_TOKEN env variable
  # linux:export API_KEY="your_secret_api_key"
  # set API_KEY="your_secret_api_key"

enctoken = os.getenv('ENC_TOKEN')


kite = KiteApp(enctoken)
