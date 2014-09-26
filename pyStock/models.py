# -*- coding: utf-8 -*-
import datetime

from pyStock import Base

from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    DECIMAL,
    Date,
    Boolean
)


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True


class Broker(Base):
    """
        An agency broker is a broker that acts as a middle man to the stock exchange, and places trades on behalf of clients.
    """
    __tablename__ = 'pystock_broker'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    phone = Column(String)
    identification_code = Column(String, unique=True)

    def commission(self, asset):
        pass


class Account(Base):
    """

    """
    __tablename__ = 'pystock_account'

    id = Column(Integer, primary_key=True)
    broker_id = Column(Integer, ForeignKey('pystock_broker.id'))
    broker = relationship("Broker", backref="accounts")


class Asset(Base):
    """
        An asset that derives value because of a contractual claim. Stocks, bonds, bank deposits, and the like are all examples of financial assets.


    """
    __tablename__ = 'pystock_asset'

    id = Column(Integer, primary_key=True)


class Security(Base):
    """

        ISIN:  International Securities Identification Number (ISIN) uniquely identifies a security. Its structure is defined in ISO 6166.
    """
    __tablename__ = 'pystock_security'
    __mapper_args__ = {
        'polymorphic_identity': 'security',
        'polymorphic_on': type
    }

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    issuer_name = Column(String, nullable=True)
    ISIN = Column(String(12), nullable=False, unique=True)
    CFI = Column(String(6), nullable=True, unique=True)
    exchange = relationship("Exchange", backref="ticks")
    exchange_id = Column(Integer, ForeignKey('pystock_exchange.id'))


class Stock(Base):
    """
        A stock or any other security representing an ownership interest.
        An equity investment generally refers to the buying and holding of
        shares of stock on a stock market by individuals and firms in
        anticipation of income from dividends and capital gains, as the value of the stock rises.

    """
    __tablename__ = 'pystock_stock'

    id = Column(Integer, primary_key=True)
    company = relationship("Company", backref="ticks")
    company_id = Column(Integer, ForeignKey('pystock_company.id'))

    __mapper_args__ = {
        'polymorphic_identity': 'pystock_stock',
    }


class Bond(Base):
    __tablename__ = 'pystock_bond'

    id = Column(Integer, primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'pystock_bond',
    }


class Tick(Base):
    """
        The minimum upward or downward movement in the price of a security.
        The term "tick" also refers to the change in the price of a security from trade to trade.
        Since 2001, with the advent of decimalization, the minimum tick size for stocks trading above $1 is 1 cent.
    """
    __tablename__ = 'pystock_tick'

    id = Column(Integer, primary_key=True)

    created_on = Column(DateTime, onupdate=datetime.datetime.now)
    broker_buyer_id = Column(Integer, ForeignKey('pystock_broker.id'))
    broker_buyer = relationship("Broker", backref="buyer_ticks", foreign_keys=[broker_buyer_id])
    broker_seller_id = Column(Integer, ForeignKey('pystock_broker.id'))
    broker_seller = relationship("Broker", backref="seller_ticks", foreign_keys=[broker_seller_id])
    price = Column(DECIMAL)
    amount = Column(DECIMAL)
    volume = Column(Integer)
    nominal_amount = Column(Integer)
    tick_date = Column(DateTime)
    security_id = Column(Integer, ForeignKey('pystock_security.id'))
    security = relationship("Security", backref="ticks")
    fraction = Column(Boolean)
    expiration = Column(String)
    register_number = Column(String, unique=True)


class Quote(Base):
    """
        This denotes the prevailing buy and sell prices for a particular financial instrument.
        Quotes are displayed as: sell price – buy price.
        For example, if 125.7 – 125.9 is the quote: 125.7 is the sell price and 125.9 is the buy price.
    """
    __tablename__ = 'pystock_quote'
    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, onupdate=datetime.datetime.now)
    tick_date = Column(Date)
    px_open = Column(DECIMAL)
    px_close = Column(DECIMAL)
    px_high = Column(DECIMAL)
    px_low = Column(DECIMAL)
    volume = Column(Integer)
    asset_id = Column(Integer, ForeignKey('pystock_asset.id'))
    asset = relationship("Asset", backref="quotes")


class Action(object):
    SELL = 'sell'
    BUY = 'buy'
    SELL_SHORT = 'sell_short'
    BUY_TO_COVER = 'buy_to_cover'


class Type(object):
    pass


class Order(Base):
    """
        An investor's instructions to a broker or brokerage firm to purchase or sell a security.
        Orders are typically placed over the phone or online. Orders fall into different available
        types which allow investors to place restrictions on their orders affecting the price and
        time at which the order can be executed. These order instructions will affect the investor's
        profit or loss on the transaction and, in some cases, whether the order is executed at all.
    """
    OPEN = 'open'
    FILLED = 'filled'
    CANCELED = 'canceled'

    __tablename__ = 'pystock_order'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('pystock_account.id'))
    account = relationship("Account", backref="orders")
    asset_id = Column(Integer, ForeignKey('pystock_asset.id'))
    asset = relationship("Asset", backref="order")
    order_id = Column(String, unique=True)
    price = Column(DECIMAL)
    share = Column(Integer)
    executed_on = Column(DateTime, onupdate=datetime.datetime.now)
    filled_on = Column(DateTime, onupdate=datetime.datetime.now)


class Split(Base):
    """
        A corporate action in which a company divides its existing shares into multiple shares.
        Although the number of shares outstanding increases by a specific multiple, the total
        dollar value of the shares remains the same compared to pre-split amounts, because the
        split did not add any real value.
    """
    __tablename__ = 'pystock_split'
    id = Column(Integer, primary_key=True)
    announce_date = Column(DateTime)
    split_date = Column(DateTime)
    ratio = Column(Integer)
    asset_id = Column(Integer, ForeignKey('pystock_asset.id'))
    asset = relationship("Asset", backref="split")


class Dividend(Base):
    """
        A distribution of a portion of a company's earnings, decided by the board of directors,
        to a class of its shareholders. The dividend is most often quoted in terms of the dollar
        amount each share receives (dividends per share). It can also be quoted in terms of a
        percent of the current market price, referred to as dividend yield.
    """

    __tablename__ = 'pystock_dividend'
    id = Column(Integer, primary_key=True)
    announce_date = Column(DateTime)
    exdividend_date = Column(DateTime)
    record_date = Column(DateTime)
    payment_date = Column(DateTime)
    amount = Column(DECIMAL)
    asset_id = Column(Integer, ForeignKey('pystock_asset.id'))
    asset = relationship("Asset", backref="dividends")


class Currency(Base):
    """
        A generally accepted form of money, including coins and paper notes,
        which is issued by a government and circulated within an economy.
        Used as a medium of exchange for goods and services, currency is the basis for trade.

        code uses ISO 4217 Currency Code
    """
    __tablename__ = 'pystock_currency'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    name = Column(String)


class MonetarySource(Base):
    __tablename__ = 'pystock_monetary_source'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class FXRates(Base):
    """
        The price of a nation’s currency in terms of another currency.
        An exchange rate thus has two components, the domestic currency
        and a foreign currency, and can be quoted either directly or
        indirectly. In a direct quotation, the price of a unit of foreign
        currency is expressed in terms of the domestic currency.
        In an indirect quotation, the price of a unit of domestic currency
        is expressed in terms of the foreign currency. An exchange rate
        that does not have the domestic currency as one of the two
        currency components is known as a cross currency, or cross rate.
    """
    __tablename__ = 'pystock_fxrates'
    id = Column(Integer, primary_key=True)
    monetary_source = relationship("MonetarySource", backref="fxrates")
    monetary_source_id = Column(Integer, ForeignKey('pystock_monetary_source.id'))
    from_currency_id = Column(Integer, ForeignKey('pystock_currency.id'))
    from_currency = relationship("Currency", backref="from_fxrates", foreign_keys=[from_currency_id])
    to_curreny_id = Column(Integer, ForeignKey('pystock_currency.id'))
    to_currency = relationship("Currency", backref="to_fxrates", foreign_keys=[to_curreny_id])
    buy_rate = Column(DECIMAL)
    sell_rate = Column(DECIMAL)
    created_on = Column(DateTime, onupdate=datetime.datetime.now)
    date = Column(DateTime)


class Company(Base):
    __tablename__ = 'pystock_company'
    id = Column(Integer, primary_key=True)

    name = Column(String)


class Book(Base):
    """
         record of all the positions that a trader is holding.
         This record shows the total amount of long and short position
         that the trader has undertaken.
    """
    __tablename__ = 'pystock_book'
    id = Column(Integer, primary_key=True)

    name = Column(String)
    user = relationship("User", backref="trades")
    user_id = Column(Integer, ForeignKey('pystock_user.id'))


class User(Base):
    """
        Represent how is buying. usually this class is associated with another user model in your app
    """
    __tablename__ = 'pystock_user'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Trade(Base):
    __tablename__ = 'pystock_trade'
    id = Column(Integer, primary_key=True)
    created_on = Column(DateTime, onupdate=datetime.datetime.now)
    trade_date = Column(DateTime)
    price = Column(DECIMAL)
    amount = Column(DECIMAL)
    user = relationship("User", backref="trades")
    user_id = Column(Integer, ForeignKey('pystock_user.id'))
    broker = relationship("Broker", backref="trades")
    broker_id = Column(Integer, ForeignKey('pystock_broker.id'))
    security = relationship("Security", backref="trades")
    security_id = Column(Integer, ForeignKey('pystock_broker.id'))
    operation_code = Column(String)
    trade_type = Column(String)  # Buy or Sell


class Exchange(Base):
    """
        A marketplace in which securities, commodities, derivatives and other financial instruments are traded.
        The core function of an exchange - such as a stock exchange - is to ensure fair and orderly trading,
        as well as efficient dissemination of price information for any securities trading on that exchange.
        Exchanges give companies, governments and other groups a platform to sell securities to the investing public.
    """
    __tablename__ = 'pystock_exchange'
    id = Column(Integer, primary_key=True)

    code = Column(String)
    name = Column(String)
#    country =


class Liability(Base):
    """
        Recorded on the balance sheet (right side), liabilities include loans,
        accounts payable, mortgages, deferred revenues and accrued expenses.
    """
    __tablename__ = 'pystock_liability'
    id = Column(Integer, primary_key=True)


