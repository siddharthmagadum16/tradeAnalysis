from datetime import datetime, timedelta

def changeDate(date_str, days):
  date_obj = datetime.strptime(date_str, '%Y-%m-%d')
  new_date_obj = date_obj + timedelta(days)
  new_date_str = new_date_obj.strftime('%Y-%m-%d')
  return new_date_str

# changeDate('2024-06-03', -2)
def writeOp(data):
  with open('./output-reliance.txt', 'w') as file:
    file.write(str(data))
