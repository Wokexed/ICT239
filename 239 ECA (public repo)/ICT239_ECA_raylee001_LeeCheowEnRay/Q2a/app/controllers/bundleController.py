from flask_login import login_required, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from datetime import datetime, date, timedelta

from models.bundle import Bundle
from models.package import Package
from models.book import Booking
from bson import ObjectId

bundle = Blueprint('bundleController', __name__)

@bundle.route('/manageBundle')
@login_required
def manageBundle():
    """
    Display bundles purchased by the current user (non-admin only).
    Shows message if no bundles purchased.
    Bundles are sorted by ascending purchase date.
    """
    # Check if user is admin - this is a non-admin function
    if current_user.is_admin:
        flash("This is a non-admin function. Please log in as a non-admin user to use this function.", "error")
        return redirect(url_for('packageController.packages'))
    
    # Get all bundles for the current user
    user_bundles = Bundle.getCustomerBundles(str(current_user.id))
    
    # Convert to list and sort by purchase date (ascending)
    bundles_list = list(user_bundles)
    bundles_list.sort(key=lambda b: b.purchased_date)
    
    # Prepare bundle data with package details
    bundles_with_packages = []
    for bundle in bundles_list:
        # Get package details for each bundled package
        packages_info = []
        for bundled_pkg in bundle.bundledPackages:
            # Try to get package by string ID or ObjectId
            try:
                package = Package.objects(id=bundled_pkg.package).first()
            except:
                # If it fails, try converting to ObjectId
                try:
                    package = Package.objects(id=ObjectId(bundled_pkg.package)).first()
                except:
                    package = None
            
            if package:
                # Check if bundle is expired (more than 1 year from purchase date)
                is_expired = (datetime.utcnow() - bundle.purchased_date).days > 365
                
                packages_info.append({
                    'package': package,
                    'utilised': bundled_pkg.utilised,
                    'is_expired': is_expired
                })
        
        bundles_with_packages.append({
            'bundle_id': str(bundle.id),
            'purchased_date': bundle.purchased_date,
            'packages': packages_info
        })
    
    return render_template('manageBundle.html', panel='Manage Bundles', bundles=bundles_with_packages)


@bundle.route('/bookFromBundle', methods=['POST'])
@login_required
def bookFromBundle():
    if current_user.is_admin:
        flash("This is a non-admin function. Please log in as a non-admin user to use this function.", "error")
        return redirect(url_for('packageController.packages'))
    
    bundle_id = request.form.get('bundle_id')
    package_id = request.form.get('package_id')
    check_in_date = request.form.get('check_in_date')
    
    if not all([bundle_id, package_id, check_in_date]):
        flash("Missing required information for booking.", "error")
        return redirect(url_for('bundleController.manageBundle'))
    
    # Get the package
    package = Package.objects(id=package_id).first()
    if not package:
        flash("Package not found.", "error")
        return redirect(url_for('bundleController.manageBundle'))
    
    # Verify the bundle belongs to the current user
    bundle = Bundle.objects(id=bundle_id, customer=str(current_user.id)).first()
    if not bundle:
        flash("Bundle not found or does not belong to you.", "error")
        return redirect(url_for('bundleController.manageBundle'))
    
    # Check if the package is already utilised
    bundled_package = None
    for bp in bundle.bundledPackages:
        if bp.package == package_id:
            bundled_package = bp
            break
    
    if not bundled_package:
        flash("Package not found in this bundle.", "error")
        return redirect(url_for('bundleController.manageBundle'))
    
    if bundled_package.utilised:
        flash("This package has already been utilised.", "error")
        return redirect(url_for('bundleController.manageBundle'))
    
    # Check if bundle is expired (more than 1 year old)
    if (datetime.utcnow() - bundle.purchased_date).days > 365:
        flash("This bundle has expired. Packages must be booked within one year of purchase.", "error")
        return redirect(url_for('bundleController.manageBundle'))
    
    # Create the booking
    try:
        booking = Booking.createBooking(check_in_date, current_user, package)
        
        # Mark the package as utilised in the bundle
        Bundle.markPackageUtilised(bundle_id, package_id)
        
        flash(f"Successfully booked {package.hotel_name} for {check_in_date}!", "success")
    except Exception as e:
        flash(f"Error creating booking: {str(e)}", "error")
    
    return redirect(url_for('bundleController.manageBundle'))