from datetime import datetime, timedelta, date
from decimal import Decimal
from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import func, or_
from app import app, db
from models import Customer, Product, Invoice, InvoiceItem, Installment, Payment


def generate_invoice_number():
    today = datetime.now()
    prefix = today.strftime('%Y%m%d')
    last_invoice = Invoice.query.filter(
        Invoice.invoice_number.like(f'{prefix}%')
    ).order_by(Invoice.id.desc()).first()
    
    if last_invoice:
        last_num = int(last_invoice.invoice_number[-4:])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f'{prefix}{new_num:04d}'


@app.route('/')
def dashboard():
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    daily_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        func.date(Invoice.created_at) == today
    ).scalar() or 0
    
    monthly_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.created_at >= month_start
    ).scalar() or 0
    
    yearly_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.created_at >= year_start
    ).scalar() or 0
    
    total_received = db.session.query(func.sum(Invoice.paid_amount)).scalar() or 0
    total_pending = db.session.query(func.sum(Invoice.total_amount - Invoice.paid_amount)).filter(
        Invoice.status != 'paid'
    ).scalar() or 0
    
    recent_invoices = Invoice.query.order_by(Invoice.created_at.desc()).limit(5).all()
    
    low_stock_products = Product.query.filter(
        Product.stock_quantity <= Product.min_stock_level
    ).all()
    
    overdue_installments = Installment.query.filter(
        Installment.status.in_(['pending', 'partial', 'overdue']),
        Installment.due_date < today
    ).all()
    
    for inst in overdue_installments:
        if inst.status != 'overdue':
            inst.status = 'overdue'
            db.session.commit()
    
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    
    return render_template('dashboard.html',
                         daily_sales=daily_sales,
                         monthly_sales=monthly_sales,
                         yearly_sales=yearly_sales,
                         total_received=total_received,
                         total_pending=total_pending,
                         recent_invoices=recent_invoices,
                         low_stock_products=low_stock_products,
                         overdue_installments=overdue_installments,
                         total_customers=total_customers,
                         total_products=total_products)


@app.route('/customers')
def customers_list():
    search = request.args.get('search', '')
    if search:
        customers = Customer.query.filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        ).order_by(Customer.name).all()
    else:
        customers = Customer.query.order_by(Customer.name).all()
    return render_template('customers/list.html', customers=customers, search=search)


@app.route('/customers/add', methods=['GET', 'POST'])
def customer_add():
    if request.method == 'POST':
        customer = Customer(
            name=request.form['name'],
            phone=request.form.get('phone', ''),
            address=request.form.get('address', ''),
            notes=request.form.get('notes', '')
        )
        db.session.add(customer)
        db.session.commit()
        flash('تم إضافة العميل بنجاح', 'success')
        return redirect(url_for('customers_list'))
    return render_template('customers/form.html', customer=None)


@app.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
def customer_edit(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.phone = request.form.get('phone', '')
        customer.address = request.form.get('address', '')
        customer.notes = request.form.get('notes', '')
        db.session.commit()
        flash('تم تحديث بيانات العميل بنجاح', 'success')
        return redirect(url_for('customers_list'))
    return render_template('customers/form.html', customer=customer)


@app.route('/customers/<int:id>/delete', methods=['POST'])
def customer_delete(id):
    customer = Customer.query.get_or_404(id)
    if customer.invoices.count() > 0:
        flash('لا يمكن حذف العميل لوجود فواتير مرتبطة به', 'error')
    else:
        db.session.delete(customer)
        db.session.commit()
        flash('تم حذف العميل بنجاح', 'success')
    return redirect(url_for('customers_list'))


@app.route('/customers/<int:id>')
def customer_view(id):
    customer = Customer.query.get_or_404(id)
    invoices = customer.invoices.order_by(Invoice.created_at.desc()).all()
    return render_template('customers/view.html', customer=customer, invoices=invoices)


@app.route('/products')
def products_list():
    search = request.args.get('search', '')
    if search:
        products = Product.query.filter(
            or_(
                Product.name.ilike(f'%{search}%'),
                Product.barcode.ilike(f'%{search}%')
            )
        ).order_by(Product.name).all()
    else:
        products = Product.query.order_by(Product.name).all()
    return render_template('products/list.html', products=products, search=search)


@app.route('/products/add', methods=['GET', 'POST'])
def product_add():
    if request.method == 'POST':
        product = Product(
            barcode=request.form.get('barcode', ''),
            name=request.form['name'],
            price=Decimal(request.form['price']),
            stock_quantity=int(request.form.get('stock_quantity', 0)),
            min_stock_level=int(request.form.get('min_stock_level', 5))
        )
        db.session.add(product)
        db.session.commit()
        flash('تم إضافة المنتج بنجاح', 'success')
        return redirect(url_for('products_list'))
    return render_template('products/form.html', product=None)


@app.route('/products/<int:id>/edit', methods=['GET', 'POST'])
def product_edit(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.barcode = request.form.get('barcode', '')
        product.name = request.form['name']
        product.price = Decimal(request.form['price'])
        product.stock_quantity = int(request.form.get('stock_quantity', 0))
        product.min_stock_level = int(request.form.get('min_stock_level', 5))
        db.session.commit()
        flash('تم تحديث بيانات المنتج بنجاح', 'success')
        return redirect(url_for('products_list'))
    return render_template('products/form.html', product=product)


@app.route('/products/<int:id>/delete', methods=['POST'])
def product_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('products_list'))


@app.route('/products/search')
def product_search():
    query = request.args.get('q', '')
    if query:
        products = Product.query.filter(
            or_(
                Product.name.ilike(f'%{query}%'),
                Product.barcode.ilike(f'%{query}%')
            )
        ).limit(10).all()
        return jsonify([{
            'id': p.id,
            'barcode': p.barcode,
            'name': p.name,
            'price': float(p.price),
            'stock': p.stock_quantity
        } for p in products])
    return jsonify([])


@app.route('/sales')
def sales_list():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    return render_template('sales/list.html', invoices=invoices)


@app.route('/sales/new', methods=['GET', 'POST'])
def sale_new():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        payment_method = request.form['payment_method']
        num_installments = int(request.form.get('num_installments', 1))
        notes = request.form.get('notes', '')
        
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        prices = request.form.getlist('price[]')
        
        if not product_ids:
            flash('يرجى إضافة منتجات للفاتورة', 'error')
            return redirect(url_for('sale_new'))
        
        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            customer_id=customer_id,
            payment_method=payment_method,
            num_installments=num_installments if payment_method == 'installment' else 1,
            notes=notes
        )
        db.session.add(invoice)
        db.session.flush()
        
        total = Decimal('0')
        for i, product_id in enumerate(product_ids):
            if product_id:
                product = Product.query.get(product_id)
                qty = int(quantities[i])
                unit_price = Decimal(prices[i])
                item_total = unit_price * qty
                
                item = InvoiceItem(
                    invoice_id=invoice.id,
                    product_id=product_id,
                    quantity=qty,
                    unit_price=unit_price,
                    total_price=item_total
                )
                db.session.add(item)
                
                product.stock_quantity -= qty
                total += item_total
        
        invoice.total_amount = total
        
        if payment_method == 'cash':
            invoice.paid_amount = total
            invoice.status = 'paid'
        else:
            invoice.paid_amount = Decimal('0')
            invoice.status = 'pending'
            
            installment_amount = total / num_installments
            for i in range(num_installments):
                due_date = date.today() + timedelta(days=30 * (i + 1))
                installment = Installment(
                    invoice_id=invoice.id,
                    installment_number=i + 1,
                    amount=installment_amount,
                    due_date=due_date
                )
                db.session.add(installment)
        
        db.session.commit()
        flash('تم إنشاء الفاتورة بنجاح', 'success')
        return redirect(url_for('sale_view', id=invoice.id))
    
    customers = Customer.query.order_by(Customer.name).all()
    products = Product.query.filter(Product.stock_quantity > 0).order_by(Product.name).all()
    return render_template('sales/form.html', customers=customers, products=products)


@app.route('/sales/<int:id>')
def sale_view(id):
    invoice = Invoice.query.get_or_404(id)
    return render_template('sales/view.html', invoice=invoice)


@app.route('/sales/<int:id>/delete', methods=['POST'])
def sale_delete(id):
    invoice = Invoice.query.get_or_404(id)
    
    for item in invoice.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock_quantity += item.quantity
    
    db.session.delete(invoice)
    db.session.commit()
    flash('تم حذف الفاتورة بنجاح', 'success')
    return redirect(url_for('sales_list'))


@app.route('/installments')
def installments_list():
    status_filter = request.args.get('status', '')
    customer_filter = request.args.get('customer', '')
    
    query = Installment.query.join(Invoice).join(Customer)
    
    if status_filter:
        query = query.filter(Installment.status == status_filter)
    
    if customer_filter:
        query = query.filter(Invoice.customer_id == customer_filter)
    
    installments = query.order_by(Installment.due_date).all()
    
    today = date.today()
    for inst in installments:
        if inst.status in ['pending', 'partial'] and inst.due_date < today:
            inst.status = 'overdue'
            db.session.commit()
    
    customers = Customer.query.order_by(Customer.name).all()
    
    return render_template('installments/list.html', 
                         installments=installments,
                         customers=customers,
                         status_filter=status_filter,
                         customer_filter=customer_filter)


@app.route('/installments/<int:id>/pay', methods=['GET', 'POST'])
def installment_pay(id):
    installment = Installment.query.get_or_404(id)
    
    if request.method == 'POST':
        amount = Decimal(request.form['amount'])
        notes = request.form.get('notes', '')
        
        remaining = installment.get_remaining()
        if amount > remaining:
            amount = remaining
        
        payment = Payment(
            installment_id=installment.id,
            amount=amount,
            notes=notes
        )
        db.session.add(payment)
        
        installment.paid_amount = Decimal(str(installment.paid_amount)) + amount
        installment.update_status()
        
        invoice = installment.invoice
        invoice.paid_amount = Decimal(str(invoice.paid_amount)) + amount
        invoice.update_status()
        
        db.session.commit()
        flash(f'تم تسجيل دفعة بمبلغ {amount}', 'success')
        return redirect(url_for('installments_list'))
    
    return render_template('installments/pay.html', installment=installment)


@app.route('/reports')
def reports():
    today = date.today()
    month_start = today.replace(day=1)
    year_start = today.replace(month=1, day=1)
    
    start_date = request.args.get('start_date', month_start.strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', today.strftime('%Y-%m-%d'))
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    total_sales = db.session.query(func.sum(Invoice.total_amount)).filter(
        Invoice.created_at >= start,
        Invoice.created_at < end
    ).scalar() or 0
    
    cash_received = db.session.query(func.sum(Invoice.paid_amount)).filter(
        Invoice.created_at >= start,
        Invoice.created_at < end
    ).scalar() or 0
    
    pending_amount = db.session.query(func.sum(Invoice.total_amount - Invoice.paid_amount)).filter(
        Invoice.status != 'paid'
    ).scalar() or 0
    
    inventory_value = db.session.query(
        func.sum(Product.price * Product.stock_quantity)
    ).scalar() or 0
    
    invoices_count = Invoice.query.filter(
        Invoice.created_at >= start,
        Invoice.created_at < end
    ).count()
    
    products_report = db.session.query(
        Product.name,
        Product.stock_quantity,
        Product.min_stock_level,
        Product.price
    ).all()
    
    daily_sales = db.session.query(
        func.date(Invoice.created_at).label('date'),
        func.sum(Invoice.total_amount).label('total')
    ).filter(
        Invoice.created_at >= start,
        Invoice.created_at < end
    ).group_by(func.date(Invoice.created_at)).all()
    
    return render_template('reports/index.html',
                         total_sales=total_sales,
                         cash_received=cash_received,
                         pending_amount=pending_amount,
                         inventory_value=inventory_value,
                         invoices_count=invoices_count,
                         products_report=products_report,
                         daily_sales=daily_sales,
                         start_date=start_date,
                         end_date=end_date)


@app.route('/seed-data')
def seed_data():
    if Customer.query.count() == 0:
        customers = [
            Customer(name='أحمد محمد', phone='0501234567', address='الرياض، حي النزهة'),
            Customer(name='محمد علي', phone='0559876543', address='جدة، حي السلامة'),
            Customer(name='فاطمة أحمد', phone='0541112233', address='الدمام، حي الفيصلية'),
            Customer(name='سارة عبدالله', phone='0533334444', address='الخبر، حي العزيزية'),
            Customer(name='خالد العمري', phone='0522225555', address='مكة، حي العوالي'),
        ]
        for c in customers:
            db.session.add(c)
    
    if Product.query.count() == 0:
        products = [
            Product(barcode='1001', name='لابتوب HP ProBook', price=3500, stock_quantity=10, min_stock_level=3),
            Product(barcode='1002', name='شاشة Dell 24 بوصة', price=850, stock_quantity=15, min_stock_level=5),
            Product(barcode='1003', name='لوحة مفاتيح لاسلكية', price=150, stock_quantity=25, min_stock_level=10),
            Product(barcode='1004', name='ماوس لاسلكي', price=75, stock_quantity=30, min_stock_level=10),
            Product(barcode='1005', name='طابعة HP LaserJet', price=1200, stock_quantity=8, min_stock_level=3),
            Product(barcode='1006', name='سماعات رأس Bluetooth', price=250, stock_quantity=20, min_stock_level=5),
            Product(barcode='1007', name='هارد ديسك خارجي 1TB', price=350, stock_quantity=12, min_stock_level=5),
            Product(barcode='1008', name='فلاش ميموري 32GB', price=45, stock_quantity=50, min_stock_level=15),
            Product(barcode='1009', name='كابل HDMI 2 متر', price=35, stock_quantity=40, min_stock_level=10),
            Product(barcode='1010', name='حقيبة لابتوب', price=120, stock_quantity=18, min_stock_level=5),
        ]
        for p in products:
            db.session.add(p)
    
    db.session.commit()
    flash('تم إضافة البيانات التجريبية بنجاح', 'success')
    return redirect(url_for('dashboard'))
