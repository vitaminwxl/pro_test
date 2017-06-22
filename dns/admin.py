from django.contrib import admin

from dns.models import Network, Region, Domain, SOA,Record,RecordType

class NetworkAdmin(admin.ModelAdmin):
    pass

class RegionAdmin(admin.ModelAdmin):
    pass

class DomainAdmin(admin.ModelAdmin):
    pass

class SoaAdmin(admin.ModelAdmin):
    pass

class RecordAdmin(admin.ModelAdmin):
    pass

class RecordTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Record,RecordAdmin)
admin.site.register(RecordType,RecordTypeAdmin)

admin.site.register(Network, NetworkAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Domain, DomainAdmin)
admin.site.register(SOA, SoaAdmin)

