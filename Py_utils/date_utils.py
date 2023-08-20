import datetime


class date_util:

	def gen_date(self,days_before):
		day = (datetime.datetime.now() - datetime.timedelta(days_before))
		return (datetime.datetime.strftime(day, "%Y%m%d))
		
	def get_day_of_week(self):
		return (datetime.datetime.today().isoweekday())  #Monday is 1 and Sunday is 7
		
	def get_next_bizdate(self):
		day_of_week = self.get_day_of_week()
		days_after =1
		if  day_of_week == 5:
			days_after = 3
		day = (datetime.datetime.now() - datetime.timedelta(days_after))
		return (datetime.datetime.strftime(day, "%Y%m%d))
		
	def get_prev_bizdate(self):
		day_of_week = self.get_day_of_week()
		days_before =1
		if  day_of_week == 1:
			days_before = 3
		day = (datetime.datetime.now() - datetime.timedelta(days_before))
		return (datetime.datetime.strftime(day, "%Y%m%d))
		
	#Add def days_between(self,from_date,to_date):