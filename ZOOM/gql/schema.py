import graphene

import gql.geodata.schema
import gql.indicator.mutation
import gql.indicator.schema
import gql.mapping.mutation
import gql.mapping.schema
import gql.metadata.mutation
import gql.metadata.schema


class Query(gql.geodata.schema.Query, gql.metadata.schema.Query,
            gql.indicator.schema.Query, gql.mapping.schema.Query,
            graphene.ObjectType):
    pass


class Mutation(gql.metadata.mutation.Mutation, gql.indicator.mutation.Mutation,
               gql.mapping.mutation.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
