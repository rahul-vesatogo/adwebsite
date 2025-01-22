import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from adwebsite.models import Product, User, Chat
from django.contrib.auth.hashers import make_password

class Usertype(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

class Producttype(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "product_name", "product_description", "product_price", "posted_by", "posted_on")

class Messagetype(DjangoObjectType):
    class Meta:
        model = Chat
        fields = ("id", "message", "sent_by", "sent_to", "product_id", "message_timing")

class Query(graphene.ObjectType):
    list_users = graphene.List(Usertype)
    list_products = graphene.List(Producttype)
    list_messages = graphene.List(Messagetype)
    read_product = graphene.List(Producttype, userid=graphene.Int())
    read_message = graphene.List(Messagetype, sentby=graphene.Int(), sentto=graphene.Int())

    def resolve_list_users(root, info):
        users = User.objects.all()
        if users:
            return users
        else:
            raise Exception(f"No Users registered")
    
    def resolve_list_products(root, info):
        products = Product.objects.all()
        if products:
            return products
        else:
            raise Exception(f"No products posted for any users")
    
    def resolve_list_messages(root, info):
        chats = Chat.objects.all()
        if chats:
            return chats
        else:
            raise Exception(f"No messages registered")
    
    def resolve_read_product(root, info, userid):
        products = Product.objects.filter(posted_by=userid)
        if products:
            return products
        else:
            user = User.objects.get(id=userid)
            raise Exception(f"No products posted by the user: {user.username}")
    
    def resolve_read_message(root, info, sentby, sentto):
        chats = Chat.objects.filter(sent_by=sentby, sent_to=sentto)
        if chats:
            return chats
        else:
            from_user = User.objects.get(id=sentby)
            to_user = User.objects.get(id=sentto)
            raise Exception(f"No messages sent by the user: {from_user.username} to the user: {to_user.username}")

class UserMutation(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()
        
    user = graphene.Field(Usertype)

    @classmethod
    def mutate(cls, root, info, username, email, password):
        
        if User.objects.filter(username=username).values() or User.objects.filter(email=email).values():
            if User.objects.filter(username=username).exists():
                raise Exception(f"Username already exists: {username}")
            if User.objects.filter(email=email).exists():
                raise Exception(f"Email already exists: {email}")
        
        
        user = User(username=username, email=email, password=make_password(password))
        user.save()
        return UserMutation(user=user)
    
class UserUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.ID() 
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()
        
    user = graphene.Field(Usertype)

    @classmethod
    def mutate(cls, root, info, username, email, password, id):

        if User.objects.filter(username=username).values() or User.objects.filter(email=email).values():
            if User.objects.filter(username=username).exists():
                raise Exception(f"Username already exists: {username}")
            if User.objects.filter(email=email).exists():
                raise Exception(f"Email already exists: {email}")
            
        if not User.objects.filter(id=id).values():
            raise Exception(f"User with id does not exists: {id}")
            
        user = User.objects.get(id=id)
        user.username = username
        user.email = email
        user.password = make_password(password)
        user.save()
        return UserMutation(user=user)

class UserDelete(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    user = graphene.Field(Usertype)

    @classmethod   
    def mutate(cls, root, info, id):
        if not User.objects.filter(id=id).values():
            raise Exception(f"User with id does not exists: {id}")

        user = User.objects.get(id=id) 
        user.delete()
        return UserMutation(user=user)
    
class ProductMutation(graphene.Mutation):
    class Arguments:
        product_name = graphene.String()
        product_description = graphene.String()
        product_price = graphene.Int()
        posted_by = graphene.Int()
        
    product = graphene.Field(Producttype)

    @classmethod
    def mutate(cls, root, info, product_name, product_description, product_price, posted_by):
        user = User.objects.get(id=posted_by)
        
        if user:
            product = Product(product_name = product_name, product_description = product_description, product_price = product_price, posted_by = user)
            product.save()
            return ProductMutation(product=product)
        else:
            raise Exception(f"User with id {posted_by} does not exists")

class ProductUpdate(graphene.Mutation):
    class Arguments:
        product_id = graphene.Int()
        product_name = graphene.String()
        product_description = graphene.String()
        product_price = graphene.Int()
        posted_by = graphene.Int()
        
    product = graphene.Field(Producttype)

    @classmethod
    def mutate(cls, root, info, product_id, product_name=None, product_description=None, product_price=None, posted_by=None):
        
        product = Product.objects.filter(id=product_id).first()
        if not product:
            raise Exception(f"Product with id {product_id} does not exist.")

        user = User.objects.filter(id=posted_by).first()
        if not user:
            raise Exception(f"User with id {posted_by} does not exist.")
        
        if product.posted_by.id != posted_by:
            raise Exception(f"User with id {posted_by} is not the owner of this ad")

        if product_name:
            product.product_name = product_name
        if product_description:
            product.product_description = product_description
        if product_price:
            product.product_price = product_price
        product.save()

        return ProductUpdate(product=product)
    
class ProductDelete(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_id = graphene.ID()
    product = graphene.Field(Producttype)

    @classmethod   
    def mutate(cls, root, info, id, user_id):
        product = Product.objects.filter(id=id).first()
        user = User.objects.filter(id=user_id).first()

        if not product:
            raise Exception(f"product with this id does not exists: {id}")
        
        if product.posted_by.id != user.id:
            raise Exception(f"User with id {user_id} is not the owner of this ad")

        product = Product.objects.get(id=id) 
        product.delete()
        return True
    
class Mutation(graphene.ObjectType):
    create_user = UserMutation.Field()  
    update_user = UserUpdate.Field()   
    delete_user = UserDelete.Field()

    create_product = ProductMutation.Field()
    update_product = ProductUpdate.Field()
    delete_product = ProductDelete.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
