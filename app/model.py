from app import app, db, Product

products = [
    { "name": "Beyerdynamic DT990 PRO", "price": "126.99", "envimpact": "1", "description": "Open backed over-ear headphones, ideal for professional mixing, mastering and editing", "image": "Beyerdynamic.jpg" },
    { "name": "Beats Studio Pro", "price": "256.99", "envimpact": "4", "description": "Wireless bluetooth noise cancelling headphones", "image": "Beats.jpg" },
    { "name": "Skullcandy Hesh Evo", "price": "89.99", "envimpact": "2", "description": "Flat folding, everyday wireless headphones with supreme audio", "image": "SkullCandy.jpg" },
    { "name": "Sony WH-CH720N", "price": "79.99", "envimpact": "3", "description": "Comfortable, lightweight headphones with crystal clear sound", "image": "Sony.png"},
]

with app.app_context():
    db.create_all()
    
    for product in products:
        newProduct = Product(name=product["name"], price=product["price"], envimpact=product["envimpact"], description=product["description"], image=product["image"])
        db.session.add(newProduct)
    
    db.session.commit()



