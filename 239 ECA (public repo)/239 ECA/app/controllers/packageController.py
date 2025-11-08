from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash

from models.forms import BookForm

from models.users import User
from models.package import Package

# new imports
from app.models.bundle import Bundle

package = Blueprint('packageController', __name__)

@package.route('/')
@package.route('/packages', methods=['GET', 'POST'])
def packages():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'purchaseBundle':
            if not current_user.is_authenticated:
                flash("Please log in to purchase a bundle.", "error")
                all_packages = Package.getAllPackages()
                return render_template('packages.html', panel="Package", all_packages=all_packages)
            
            if current_user.is_admin:
                flash("This is a non-admin function. Please log in as a non-admin user to use this function.", "error")
                all_packages = Package.getAllPackages()
                return render_template('packages.html', panel="Package", all_packages=all_packages)
            
            selected_packages = request.form.getlist('selected_packages')
            
            num_packages = len(selected_packages)

            if num_packages == 0:
                flash("Please select packages to buy as a bundle", "error")

            elif num_packages == 1:
                selected_hotel_name_str = selected_packages[0]
                single_package = Package.getPackage(selected_hotel_name_str)
                
                if single_package:
                    hotel_name = single_package.hotel_name
                    total_cost = single_package.packageCost()
                    new_message = f"No discount for bundle purchase for {hotel_name}.<br> Total costs: ${total_cost:.2f}"
                    flash(new_message, "success")
                    
                    try:
                        bundle = Bundle.purchaseBundle(str(current_user.id), [str(single_package.id)])
                        flash("Bundle successfully purchased! You can view it in Manage Bundle.", "success")
                    except Exception as e:
                        flash(f"Error creating bundle: {str(e)}", "error")

            elif num_packages >= 2:
                total_cost = 0.0
                hotel_names = []
                package_ids = []
                
                for name_str in selected_packages:
                    package = Package.getPackage(name_str)
                    if package:
                        total_cost += package.packageCost()
                        hotel_names.append(package.hotel_name)
                        package_ids.append(str(package.id))

                if 2 <= num_packages <= 3:
                    discount_rate = 0.10
                    discount_text = "10% discount"
                    discount_multiplier = 0.90
                elif num_packages >= 4:
                    discount_rate = 0.20
                    discount_text = "20% discount"
                    discount_multiplier = 0.80
                
                discounted_cost = total_cost * discount_multiplier
                names_list = ", ".join(hotel_names)
                
                new_message = (
                    f"{discount_text} for bundle purchase for {names_list}.<br>"
                    f"Total cost: ${total_cost:.2f}<br>"
                    f"Discounted total: ${discounted_cost:.2f}"
                )
                
                flash(new_message, "success")

                bundle = Bundle.purchaseBundle(str(current_user.id), package_ids)


    all_packages = Package.getAllPackages()
    return render_template('packages.html', panel="Package", all_packages=all_packages)

@package.route("/viewPackageDetail/<hotel_name>")
def viewPackageDetail(hotel_name):
    the_package = Package.getPackage(hotel_name=hotel_name)
    return render_template('packageDetail.html', panel="Package Detail", package=the_package)
