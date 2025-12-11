from datetime import datetime, date
from decimal import Decimal
from app import db


class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    invoices = db.relationship('Invoice', backref='customer', lazy='dynamic')
    
    def get_total_debt(self):
        total = Decimal('0')
        for invoice in self.invoices:
            total += invoice.get_remaining_balance()
        return total


class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True, index=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_low_stock(self):
        return self.stock_quantity <= self.min_stock_level


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    paid_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    payment_method = db.Column(db.String(20), nullable=False)  # 'cash' or 'installment'
    num_installments = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'partial', 'paid'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = db.relationship('InvoiceItem', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    installments = db.relationship('Installment', backref='invoice', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_remaining_balance(self):
        return Decimal(str(self.total_amount)) - Decimal(str(self.paid_amount))
    
    def update_status(self):
        remaining = self.get_remaining_balance()
        if remaining <= 0:
            self.status = 'paid'
        elif Decimal(str(self.paid_amount)) > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    total_price = db.Column(db.Numeric(12, 2), nullable=False)
    
    product = db.relationship('Product')


class Installment(db.Model):
    __tablename__ = 'installments'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(12, 2), default=0)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'partial', 'paid', 'overdue'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    payments = db.relationship('Payment', backref='installment', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_remaining(self):
        return Decimal(str(self.amount)) - Decimal(str(self.paid_amount))
    
    def update_status(self):
        remaining = self.get_remaining()
        if remaining <= 0:
            self.status = 'paid'
        elif Decimal(str(self.paid_amount)) > 0:
            self.status = 'partial'
        elif self.due_date < date.today():
            self.status = 'overdue'
        else:
            self.status = 'pending'


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    installment_id = db.Column(db.Integer, db.ForeignKey('installments.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
