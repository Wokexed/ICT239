from app import db
from datetime import datetime

class BundledPackage(db.EmbeddedDocument):
    package = db.StringField(required=True)
    utilised = db.BooleanField(default=False)

class Bundle(db.Document):
    meta = {'collection': 'bundles'} 
    purchased_date = db.DateTimeField(default=datetime.utcnow)
    customer = db.StringField(required=True)
    bundledPackages = db.ListField(
        db.EmbeddedDocumentField('BundledPackage')
    )

    @staticmethod
    def purchaseBundle(customer_id, package_ids):
        embedded_packages = [BundledPackage(package=pkg_id) for pkg_id in package_ids]

        bundle = Bundle(customer=customer_id, bundledPackages=embedded_packages)
        bundle.save()
        return bundle
    
    @staticmethod
    def getCustomerBundles(customer_id):
        return Bundle.objects(customer=customer_id)

    @staticmethod
    def markPackageUtilised(bundle_id, package_id):
        bundle = Bundle.objects(id=bundle_id, bundledPackages__package=package_id).first()
        if bundle:
            for bp in bundle.bundledPackages:
                if bp.package == package_id:
                    bp.utilised = True
                    break
            bundle.save()
            return True
        return False

