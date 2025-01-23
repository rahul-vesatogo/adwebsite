
def get_products():
    query = '''{
  listProducts
  {
    id
    productName
    productDescription
    productPrice
    postedBy {
      id
    }
    postedOn
  }
}'''
    return query