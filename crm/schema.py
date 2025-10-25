import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from .models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# Input Types
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

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")
        
        # Validate phone format if provided
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
                # Validate email uniqueness
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
        # Validate price is positive
        if input.price <= 0:
            raise Exception("Price must be positive")
        
        # Validate stock is not negative
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
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Customer does not exist")
        
        # Validate products exist and get them
        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
            except Product.DoesNotExist:
                raise Exception(f"Product with ID {product_id} does not exist")
        
        # Validate at least one product
        if not products:
            raise Exception("At least one product is required")
        
        # Calculate total amount
        total_amount = sum(product.price for product in products)
        
        # Create order
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

class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info):
        return Order.objects.all()
