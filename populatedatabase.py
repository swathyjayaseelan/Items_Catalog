from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalogdatabase_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///itemscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
# Sample user
User1 = User(name="Bob", email="bob@email.com")
session.add(User1)
session.commit()

# Category 1
category1 = Category(name="Baseball")
session.add(category1)
session.commit()

item1 = CategoryItem(user_id=1,\
                     name="Bat", description="Made of high quality wood",\
                     category=category1)
session.add(item1)
session.commit()

item2 = CategoryItem(user_id=1, name="Gloves",\
                     description="To protect hands", category=category1)
session.add(item2)
session.commit()

# Category 2
category2 = Category(name="Frisbee")

session.add(category2)
session.commit()

# Category 3
category3 = Category(name="Rock Climbing")
session.add(category3)
session.commit()

# Catgeory 4
category4 = Category(name="BasketBall")
session.add(category4)
session.commit()

item3 = CategoryItem(user_id=1, name="Shoes",\
                     description="For agiilty", category=category4)
session.add(item3)
session.commit()

item4 = CategoryItem(user_id=1, name="Ball",\
                     description="High quality", category=category4)
session.add(item4)
session.commit()

# Catgeory 5
category5 = Category(name="Skating")
session.add(category5)
session.commit()

item5 = CategoryItem(user_id=1, name="Skating shoes",\
                     description="For good balance", category=category5)
session.add(item5)
session.commit()

# Category 6
category6 = Category(name="Hockey")
session.add(category6)
session.commit()

print "added catalog items!"
