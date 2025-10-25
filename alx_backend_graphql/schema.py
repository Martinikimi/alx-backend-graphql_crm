import graphene

class CRMQuery(graphene.ObjectType):
    pass

class Query(CRMQuery, graphene.ObjectType):
    hello = graphene.String()
    
    def resolve_hello(self, info):
        return "Hello, GraphQL!"

schema = graphene.Schema(query=Query)
