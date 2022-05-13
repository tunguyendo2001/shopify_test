import { gql, useQuery } from "@apollo/client";
import { Page, Layout, Banner, Card } from "@shopify/polaris";
import { Loading } from "@shopify/app-bridge-react";
import { ProductsList } from "./ProductsList";
import { ApplyRandomPrices } from "./ApplyRandomPrices";


// GraphQL query to retrieve products by IDs.
// The price field belongs to the variants object because
// product variants can have different prices.
const GET_PRODUCTS_BY_ID = gql`
  query getProducts($ids: [ID!]!) {
    nodes(ids: $ids) {
      ... on Product {
        title
        handle
        descriptionHtml
        id
        images(first: 1) {
          edges {
            node {
              id
              originalSrc
              altText
            }
          }
        }
        variants(first: 1) {
          edges {
            node {
              price
              id
            }
          }
        }
      }
    }
  }
`;
export function ProductsPage({ productIds }) {
  const { loading, error, data, refetch } = useQuery(GET_PRODUCTS_BY_ID, {
    variables: { ids: productIds },
  });
  if (loading) return <Loading />;

  if (error) {
    console.warn(error);
    return (
      <Banner status="critical">There was an issue loading products.</Banner>
    );
  }

  return (
    <Page>
      <Layout>
        <Layout.Section>
          <Card>
            <ProductsList data={data} />
          </Card>
          <ApplyRandomPrices selectedItems={data.nodes} onUpdate={refetch} />
        </Layout.Section>
      </Layout>
    </Page>
  );
}