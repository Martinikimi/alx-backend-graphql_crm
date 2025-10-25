import graphene
from graphene_django import DjangoObjectType, DjangoFilterConnectionField
from django.db import transaction
from django.db.models import Q
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

# Types with Node for filtering
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        fields = "__all__"

# Input Types (keep existing)
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# Filter Input Types
class CustomerFilterInput(graphene.InputObjectType):
    name = graphene.String()
    name_icontains = graphene.String()
    email = graphene.String()
    email_icontains = graphene.String()
    created_at_gte = graphene.Date()
    created_at_lte = graphene.Date()
    phone_pattern = graphene.String()

class ProductFilterInput(graphene.InputObjectType):
    name = graphene.String()
    name_icontains = graphene.String()
    price_gte = graphene.Decimal()
    price_lte = graphene.Decimal()
    stock_gte = graphene.Int()
    stock_lte = graphene.Int()
    low_stock = graphene.Boolean()

class OrderFilterInput(graphene.InputObjectType):
    total_amount_gte = graphene.Decimal()
    total_amount_lte = graphene.Decimal()
    order_date_gte = graphene.Date()
    order_date_lte = graphene.Date()
    customer_name = graphene.String()
    customer_name_icontains = graphene.String()
    product_name = graphene.String()
    product_name_icontains = graphene.String()
    product_id = graphene.ID()

# Keep existing Mutations (CreateCustomer, BulkCreateCustomers, CreateProduct, CreateOrder)
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        
        if input.phone and not any(c.isdigit() for c in input.phone.replace('-', '').replace('+', '')):
            raise Exception("Invalid phone format")
        
        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()
        
        return CreateCustomer(customer=customer, message="Customer created successfully")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, inputs):
        customers = []
        errors = []
        
        for i, input_data in enumerate(inputs):
            try:
                if Customer.objects.filter(email=input_data.email).exists():
                    errors.append(f"Row {i+1}: Email {input_data.email} already exists")
                    continue
                
                customer = Customer(
                    name=input_data.name,
                    email=input_data.email,
                    phone=input_data.phone
                )
                customer.save()
                customers.append(customer)
                
            except Exception as e:
                errors.append(f"Row {i+1}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            raise Exception("Stock cannot be negative")
        
        product = Product(
            name=input.name,
            price=input.price,
            stock=stock
        )
        product.save()
        
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer does not exist")
        
        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
            except Product.DoesNotExist:
                raise Exception(f"Product with ID {product_id} does not exist")
        
        if not products:
            raise Exception("At least one product is required")
        
        total_amount = sum(product.price for product in products)
        
        order = Order(
            customer=customer,
            total_amount=total_amount
        )
        order.save()
        order.products.set(products)
        
        return CreateOrder(order=order)

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

# Updated Query with Filtering
class Query(graphene.ObjectType):
    # Filtered queries with relay nodes
    all_customers = DjangoFilterConnectionField(
        CustomerType, 
        filterset_class=CustomerFilter,
        order_by=graphene.List(of_type=graphene.String)
    )
    
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter,
        order_by=graphene.List(of_type=graphene.String)
    )
    
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter,
        order_by=graphene.List(of_type=graphene.String)
    )
    
    # Simple non-filtered queries (keep for backward compatibility)
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info):
        return Order.objects.all()
