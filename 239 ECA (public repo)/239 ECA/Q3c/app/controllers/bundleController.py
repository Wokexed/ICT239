from flask_login import login_required, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash
from datetime import datetime, date, timedelta

from models.bundle import Bundle
from models.package import Package
from models.book import Booking
from bson import ObjectId

from flask import jsonify  

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


@bundle.route('/api/bookFromBundle', methods=['POST'])
@login_required
def apiBookFromBundle():
    """API endpoint for SPA - returns JSON instead of redirect"""
    if current_user.is_admin:
        return {'success': False, 'message': 'This is a non-admin function.'}, 403
    
    data = request.get_json()
    bundle_id = data.get('bundle_id')
    package_id = data.get('package_id')
    check_in_date = data.get('check_in_date')
    
    if not all([bundle_id, package_id, check_in_date]):
        return {'success': False, 'message': 'Missing required information.'}, 400
    
    package = Package.objects(id=package_id).first()
    if not package:
        return {'success': False, 'message': 'Package not found.'}, 404
    
    bundle = Bundle.objects(id=bundle_id, customer=str(current_user.id)).first()
    if not bundle:
        return {'success': False, 'message': 'Bundle not found or does not belong to you.'}, 404
    
    bundled_package = None
    for bp in bundle.bundledPackages:
        if bp.package == package_id:
            bundled_package = bp
            break
    
    if not bundled_package:
        return {'success': False, 'message': 'Package not found in this bundle.'}, 404
    
    if bundled_package.utilised:
        return {'success': False, 'message': 'This package has already been utilised.'}, 400
    
    if (datetime.utcnow() - bundle.purchased_date).days > 365:
        return {'success': False, 'message': 'This bundle has expired.'}, 400
    
    try:
        booking = Booking.createBooking(check_in_date, current_user, package)
        Bundle.markPackageUtilised(bundle_id, package_id)
        return {'success': True, 'message': f'Successfully booked {package.hotel_name}!'}
    except Exception as e:
        return {'success': False, 'message': f'Error: {str(e)}'}, 500