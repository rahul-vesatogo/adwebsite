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
    
class Mutation(graphene.ObjectType):
    create_user = UserMutation.Field()  
    update_user = UserUpdate.Field()   
    delete_user = UserDelete.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
