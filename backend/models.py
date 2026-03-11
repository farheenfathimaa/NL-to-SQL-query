from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime
import os
import time

Base = declarative_base()


class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    sales_reps = relationship("SalesRep", back_populates="region")


class SalesRep(Base):
    __tablename__ = 'sales_reps'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    region_id = Column(Integer, ForeignKey('regions.id'))
    region = relationship("Region", back_populates="sales_reps")
    orders = relationship("Order", back_populates="sales_rep")


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    price = Column(Float, nullable=False)
    order_items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_date = Column(DateTime, default=datetime.datetime.utcnow)
    sales_rep_id = Column(Integer, ForeignKey('sales_reps.id'))
    sales_rep = relationship("SalesRep", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/query_db")


def init_db():
    engine = create_engine(DATABASE_URL)

    # Wait for DB to be ready (retry logic)
    max_retries = 10
    for i in range(max_retries):
        try:
            connection = engine.connect()
            connection.close()
            break
        except Exception as e:
            if i == max_retries - 1:
                print(f"Failed to connect to DB after {max_retries} attempts.")
                raise e
            print(f"Waiting for database... (attempt {i + 1}/{max_retries})")
            time.sleep(5)

    # Create tables if they don't already exist (safe, idempotent — no drop_all)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Only seed if the database is empty (idempotent seeding)
        if session.query(Region).count() > 0:
            print("Database already seeded, skipping.")
            return

        print("Seeding database with sample data...")

        # Regions
        regions = [Region(name=n) for n in ["North", "South", "East", "West"]]
        session.add_all(regions)
        session.commit()

        # Sales reps
        reps = [
            SalesRep(name="Alice", region_id=regions[0].id),
            SalesRep(name="Bob", region_id=regions[1].id),
            SalesRep(name="Charlie", region_id=regions[2].id),
            SalesRep(name="David", region_id=regions[3].id),
        ]
        session.add_all(reps)
        session.commit()

        # Products
        products = [
            Product(name="Laptop", category="Electronics", price=1200.0),
            Product(name="Phone", category="Electronics", price=800.0),
            Product(name="Monitor", category="Electronics", price=300.0),
            Product(name="Desk Chair", category="Furniture", price=150.0),
            Product(name="Coffee Mug", category="Kitchen", price=15.0),
        ]
        session.add_all(products)
        session.commit()

        # Historical orders (last quarter)
        now = datetime.datetime.utcnow()
        last_q_start = now - datetime.timedelta(days=90)

        orders = [
            Order(order_date=last_q_start + datetime.timedelta(days=10), sales_rep_id=reps[0].id),
            Order(order_date=last_q_start + datetime.timedelta(days=20), sales_rep_id=reps[1].id),
            Order(order_date=last_q_start + datetime.timedelta(days=30), sales_rep_id=reps[2].id),
            Order(order_date=last_q_start + datetime.timedelta(days=40), sales_rep_id=reps[3].id),
            Order(order_date=now - datetime.timedelta(days=5), sales_rep_id=reps[0].id),
        ]
        session.add_all(orders)
        session.commit()

        # Order items
        items = [
            OrderItem(order_id=orders[0].id, product_id=products[0].id, quantity=1, unit_price=1200.0),
            OrderItem(order_id=orders[1].id, product_id=products[1].id, quantity=2, unit_price=800.0),
            OrderItem(order_id=orders[2].id, product_id=products[2].id, quantity=3, unit_price=300.0),
            OrderItem(order_id=orders[3].id, product_id=products[3].id, quantity=1, unit_price=150.0),
            OrderItem(order_id=orders[4].id, product_id=products[4].id, quantity=10, unit_price=15.0),
        ]
        session.add_all(items)
        session.commit()

        print("Database seeded successfully.")
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
