from django.contrib import admin
from django.contrib.auth import get_permission_codename
from django.db import models
from .models import Bom, Currency, Period, Supplier, Customer, Category, Part, Size, Material, Product

admin.site.site_header = '进销存系统'


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'period']
    view_on_site = False

@admin.register(Currency)
class CurencyAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'rate']
    view_on_site = False


class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'contacter', 'period', 'status']
    fields = ['title', 'contacter', 'period', 'landline', 'mobile', 'wechat_account', 'email', 'address',
              'description']
    actions = ['make_audited', 'make_stopped']
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100

    def make_audited(self, request, queryset):
        rows = queryset.update(status='A')
        if rows > 0:
            self.message_user(request, u'已完成审核动作')
    make_audited.allowed_permissions = ('audit',)
    make_audited.short_description = u'通过审核'

    def has_audit_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('audit', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def make_stopped(self, request, queryset):
        rows = queryset.update(status='S')
        if rows > 0:
            self.message_user(request, u'已完成终止动作')
    make_stopped.allowed_permissions = ('stop',)
    make_stopped.short_description = u'终止使用'

    def has_stop_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('stop', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Supplier, SupplierAdmin)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'contacter', 'period', 'status']
    fields = ['title', 'contacter', 'period', 'landline', 'mobile', 'wechat_account', 'email', 'address',
              'description']
    actions = ['make_audited']
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100

    def make_audited(self, request, queryset):
        rows = queryset.update(status='A')
        if rows > 0:
            self.message_user(request, u'已完成审核动作')
    make_audited.allowed_permissions = ('audit',)
    make_audited.short_description = u'通过审核'

    def has_audit_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('audit', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def make_stopped(self, request, queryset):
        rows = queryset.update(status='S')
        if rows > 0:
            self.message_user(request, u'已完成终止动作')
    make_stopped.allowed_permissions = ('stop',)
    make_stopped.short_description = u'终止使用'

    def has_stop_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('stop', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Customer, CustomerAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'status']
    fields = ['title', 'description']
    actions = ['make_audited', 'make_stopped']
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100

    def make_audited(self, request, queryset):
        rows = queryset.update(status='A')
        if rows > 0:
            self.message_user(request, u'已完成审核动作')
    make_audited.allowed_permissions = ('audit',)
    make_audited.short_description = u'通过审核'

    def has_audit_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('audit', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def make_stopped(self, request, queryset):
        rows = queryset.update(status='S')
        if rows > 0:
            self.message_user(request, u'已完成终止动作')
    make_stopped.allowed_permissions = ('stop',)
    make_stopped.short_description = u'终止使用'

    def has_stop_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('stop', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Category, CategoryAdmin)


class PartAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'status']
    fields = ['title', 'description']
    actions = ['make_audited', 'make_stopped']
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100

    def make_audited(self, request, queryset):
        rows = queryset.update(status='A')
        if rows > 0:
            self.message_user(request, u'已完成审核动作')
    make_audited.allowed_permissions = ('audit',)
    make_audited.short_description = u'通过审核'

    def has_audit_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('audit', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def make_stopped(self, request, queryset):
        rows = queryset.update(status='S')
        if rows > 0:
            self.message_user(request, u'已完成终止动作')
    make_stopped.allowed_permissions = ('stop',)
    make_stopped.short_description = u'终止使用'

    def has_stop_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('stop', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Part, PartAdmin)


class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'status']
    fields = ['title', 'description']
    actions = ['make_audited', 'make_stopped']
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100

    def make_audited(self, request, queryset):
        rows = queryset.update(status='A')
        if rows > 0:
            self.message_user(request, u'已完成审核动作')
    make_audited.allowed_permissions = ('audit',)
    make_audited.short_description = u'通过审核'

    def has_audit_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('audit', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def make_stopped(self, request, queryset):
        rows = queryset.update(status='S')
        if rows > 0:
            self.message_user(request, u'已完成终止动作')
    make_stopped.allowed_permissions = ('stop',)
    make_stopped.short_description = u'终止使用'

    def has_stop_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('stop', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Size, SizeAdmin)


class MaterialAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image_sub', 'supplier', 'category', 'tax_price', 'currency', 'stock', 'status']
    fields = ['title', 'image_sub', 'supplier', 'category', 'price', 'tax', 'tax_price',
              'description', 'currency']
    actions = ['make_audited', 'make_stopped']
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100

    def make_audited(self, request, queryset):
        rows = queryset.update(status='A')
        if rows > 0:
            self.message_user(request, u'已完成审核动作')
    make_audited.allowed_permissions = ('audit',)
    make_audited.short_description = u'通过审核'

    def has_audit_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('audit', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def make_stopped(self, request, queryset):
        rows = queryset.update(status='S')
        if rows > 0:
            self.message_user(request, u'已完成终止动作')
    make_stopped.allowed_permissions = ('stop',)
    make_stopped.short_description = u'终止使用'

    def has_stop_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('stop', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Material, MaterialAdmin)


class BomInline(admin.TabularInline):
    model = Bom
    fields = ['material', 'quantity']
    raw_id_fields = ['material']
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'part', 'size', 'image_sub', 'tax_price', 'currency', 'stock', 'status']
    fields = ['title', 'part', 'size', 'image_sub', 'price', 'tax', 'tax_price',
              'currency', 'description']
    actions = ['make_audited', 'make_stopped']
    inlines = [BomInline]
    view_on_site = False
    list_filter = ['status']
    list_per_page = 10
    list_max_show_all = 100

    def make_audited(self, request, queryset):
        rows = queryset.update(status='A')
        if rows > 0:
            self.message_user(request, u'已完成审核动作')
    make_audited.allowed_permissions = ('audit',)
    make_audited.short_description = u'通过审核'

    def has_audit_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('audit', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))

    def make_stopped(self, request, queryset):
        rows = queryset.update(status='S')
        if rows > 0:
            self.message_user(request, u'已完成终止动作')
    make_stopped.allowed_permissions = ('stop',)
    make_stopped.short_description = u'终止使用'

    def has_stop_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('stop', opts)
        return request.user.has_perm('%s.%s' % (opts.app_label, codename))


admin.site.register(Product, ProductAdmin)

