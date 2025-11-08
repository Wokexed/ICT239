from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app import db
from models.book import Booking

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/trend_chart', methods=['GET', 'POST'])
@login_required
def trend_chart():

    if request.method == 'GET':

        #I want to get some data from the service
        return render_template('trend_chart.html', panel="Dashboard Chart")
    
    elif request.method == 'POST':

        all_bookings = Booking.getAllBookings()
        print(f"There are {len(all_bookings)} of booking records")

        data = request.get_json()
        chart_type = data.get('chartType', 'amount')

        if chart_type == 'amount':
                # Amount Incoming - Line chart
            hotel_costbyDate = {}
                
            for aBooking in list(all_bookings):
                hotel_name = aBooking.package.hotel_name
                check_in_date = aBooking.check_in_date
                        
                if hotel_name not in hotel_costbyDate:
                    hotel_costbyDate[hotel_name] = {}
                if check_in_date not in hotel_costbyDate[hotel_name]:
                    hotel_costbyDate[hotel_name][check_in_date] = 0
                hotel_costbyDate[hotel_name][check_in_date] += aBooking.total_cost
            
            hotel_costbyDateSortedListValues = {}
            for hotel, dateAmts in hotel_costbyDate.items():
                hotel_costbyDateSortedListValues[hotel] = sorted(list(dateAmts.items()))
                
            return jsonify({'chartType': 'amount', 'chartDim': hotel_costbyDateSortedListValues})
            
        elif chart_type == 'bookings':
            # Bookings By Month - Bar chart
            hotel_bookingsByMonth = {}
                
            for aBooking in list(all_bookings):
                hotel_name = aBooking.package.hotel_name
                check_in_date = aBooking.check_in_date
                    
                if isinstance(check_in_date, str):
                    check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
                    
                month_year = check_in_date.strftime("%B %Y")
                    
                if hotel_name not in hotel_bookingsByMonth:
                    hotel_bookingsByMonth[hotel_name] = {}
                if month_year not in hotel_bookingsByMonth[hotel_name]:
                    hotel_bookingsByMonth[hotel_name][month_year] = 0
                hotel_bookingsByMonth[hotel_name][month_year] += 1
                
            hotel_bookingsSortedListValues = {}
            for hotel, monthCounts in hotel_bookingsByMonth.items():
                sorted_items = sorted(
                    list(monthCounts.items()),
                    key=lambda x: datetime.strptime(x[0], "%B %Y")
                )
                hotel_bookingsSortedListValues[hotel] = sorted_items
                
            return jsonify({'chartType': 'bookings', 'chartDim': hotel_bookingsSortedListValues})
            
