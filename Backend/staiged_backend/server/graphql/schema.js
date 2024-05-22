const { makeExecutableSchema } = require('@graphql-tools/schema');
const { mergeTypeDefs, mergeResolvers } = require('@graphql-tools/merge');
const pdfTypeDefs = require('./typeDefs/pdfTypeDefs');
const ocrTypeDefs = require('./typeDefs/ocrTypeDefs');
const pdfResolvers = require('./resolvers/pdfResolvers');
const ocrResolvers = require('./resolvers/ocrResolvers');

const typeDefs = mergeTypeDefs([pdfTypeDefs, ocrTypeDefs]);
const resolvers = mergeResolvers([pdfResolvers, ocrResolvers]);

const schema = makeExecutableSchema({
  typeDefs,
  resolvers,
});

module.exports = schema;
