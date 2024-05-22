const typeDefs = `
  type PDF {
    filename: String!
    filepath: String!
    ocrText: String!
  }

  type Query {
    hello: String
  }

  type Mutation {
    uploadPDF(filename: String!, marginSide: String!): PDF!
  }
`;

module.exports = typeDefs;
