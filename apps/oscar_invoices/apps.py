import oscar_invoices.apps as apps


class InvoicesConfig(apps.InvoicesConfig):
    name = 'apps.oscar_invoices'
    label = 'oscar_invoices'
    verbose_name = 'Oscar Invoices'
