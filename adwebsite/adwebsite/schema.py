import graphene
from graphql import GraphQLError
from graphene_django import DjangoObjectType
from adwebsite.models import Product, User, Chat
from django.contrib.auth.hashers import make_password
from graphql_jwt.decorators import login_required

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

    @login_required
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

class MessageMutation(graphene.Mutation):
    class Arguments:
        message = graphene.String()
        sent_to = graphene.Int()
        sent_by = graphene.Int()
        product_id = graphene.Int()

        
    message = graphene.Field(Messagetype)

    @classmethod
    def mutate(cls, root, info, message, sent_by, sent_to, product_id):
        sending_user = User.objects.filter(id=sent_by).first()
        receiving_user = User.objects.filter(id=sent_to).first()
        product = Product.objects.filter(id=product_id).first()

        if not sending_user:
            raise Exception(f"User with id {sent_by} does not exist")
        if not receiving_user:
            raise Exception(f"User with id {sent_to} does not exist")

        if sending_user.id == receiving_user.id:
            raise Exception(f"User cannot message to self")

        if not product:
            raise Exception(f"Product with id {product_id} does not exist")
        
        if product.posted_by.id != receiving_user.id:
            raise Exception(f"Product with id {product_id} is not posted by the receiving user")

        message = Chat(message=message, sent_by=sending_user.id, sent_to=receiving_user, product_id=product)
        message.save()
        return MessageMutation(message=message)
    
class MessageUpdate(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        message = graphene.String()
        user_id = graphene.Int()
        product_id = graphene.Int()
     
    chat = graphene.Field(Messagetype)

    @classmethod
    def mutate(cls, root, info, id, message, user_id, product_id):
        chat = Chat.objects.filter(id=id).first()
        sending_user = User.objects.filter(id=user_id).first()
        product = Product.objects.filter(id=product_id).first()

        if not chat:
            raise Exception(f"Message with id {id} does not exist")
        
        if not sending_user:
            raise Exception(f"User with id {sending_user} does not exist")
        
        if not product:
            raise Exception(f"Product with id {product_id} does not exist")

        if sending_user.id != chat.sent_by:
            raise Exception(f"You cannot update this message")

        if message:
            chat.message = message
        chat.save()

        return MessageUpdate(chat=chat)

class MessageDelete(graphene.Mutation):
    class Arguments:
        id = graphene.ID()
        user_id = graphene.ID()
    
    chat = graphene.Field(Messagetype)

    @classmethod   
    def mutate(cls, root, info, id, user_id):
        chat = Chat.objects.filter(id=id).first()
        user = User.objects.filter(id=user_id).first()

        if not chat:
            raise Exception(f"Message with this id does not exists: {id}")
        
        if chat.sent_by != user.id:
            raise Exception(f"User with id {user_id} is not the owner of this message")

        message = Chat.objects.get(id=id) 
        message.delete()
        return True
        
class Mutation(graphene.ObjectType):
    create_user = UserMutation.Field()  
    update_user = UserUpdate.Field()   
    delete_user = UserDelete.Field()

    create_product = ProductMutation.Field()
    update_product = ProductUpdate.Field()
    delete_product = ProductDelete.Field()

    create_message = MessageMutation.Field()
    update_message = MessageUpdate.Field()
    delete_message = MessageDelete.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
