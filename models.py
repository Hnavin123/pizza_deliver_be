from database import Base  
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey

from sqlalchemy_utils.types import ChoiceType
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(25), unique=True, index=True, nullable=False)
    email = Column(String(80), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    orders = relationship("Order", back_populates = "user")
    
    def __repr__(self):
        return f"<User(username={self.username})>"
    
    
class Order(Base):
    
    ORDER_STATUS = (
            ('PENDING', 'Pending'),
            ('IN-TRANSIT', 'In-Transit'),
            ('DELIVERED', 'Delivered'),
        )
        
    PIZZA_SIZES = (
            ('SMALL', 'Small'),
            ('MEDIUM', 'Medium'),
            ('LARGE', 'Large'),
            ('EXTRA-LARGE', 'Extra-Large'),
        )   
    
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUS), default='PENDING')
    pizza_size = Column(ChoiceType(choices=PIZZA_SIZES),default='SMALL')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="orders")
    
    def __repr__(self):
        return f"<Order(id={self.id})>"