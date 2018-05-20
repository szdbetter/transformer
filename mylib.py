import hmac#http://tool.oschina.net/encrypt?type=2
import hashlib
import requests
#lbank: {"api_key":"16702619-0bc8-446d-a3d0-62fb67a8985e","symbol":"eth_btc",
# "order_id":"24f7ce27-af1d-4dca-a8c1-ef1cbeec1b23,57a80854-cf31-489a-93b3-d25a2d4c12f2",
# "sign":"16702619-0bc8-446d-a3d0-62fb67a8985e",'test':1}

def fParsePercent(f):
	return str(round(f*100,2))+'%'
	
def fParseExBalance(exchange):
	balance={}
	if(exchange.name.lower()=='otcbtc'):
		balance['seer']=float(exchange.balance['seer'])
		balance['eth']=float(exchange.balance['eth'])
	elif(exchange.name.lower()=='lbank'):
		balance['seer']=float(exchange.balance['SEER']['free'])
		balance['eth']=float(exchange.balance['ETH']['free'])
	return balance

def fBuildTestData(exA,exB,sType):
	#***测试需要，手动构建测试数据*****#
	#sType,1:A低B高，2：A高B低
	if(sType==1):
		#		exA			exB
		#Sell	2,200		4,400
		#Buy	1,100		3,300
		exA_data=[(0.00002,2),(0.00001,1)]#(ask_price,ask_amount),(buy_price,buy_amount)
		exB_data=[(0.00004,4),(0.00003,3)]#(ask_price,ask_amount),(buy_price,buy_amount)
	elif(sType==2):
		#		exA			exB
		#Sell	4,400		2,200
		#Buy	3,300		1,100
		exA_data=[(0.00004,4),(0.00003,3)]#(ask_price,ask_amount),(buy_price,buy_amount)
		exB_data=[(0.00002,2),(0.00001,1)]#(ask_price,ask_amount),(buy_price,buy_amount)	
	exA.buy_price=exA_data[1][0]
	exA.buy_amount=exA_data[1][1]
	exA.sell_price=exA_data[0][0]
	exA.sell_amount=exA_data[0][1]
	exB.buy_price=exB_data[1][0]
	exB.buy_amount=exB_data[1][1]
	exB.sell_price=exB_data[0][0]
	exB.sell_amount=exB_data[0][1]


		
#定义exchange 类
class myExchange(object):
	def __init__(self,name,base_url,apiKey,secret):
		self.name=name
		self.base_url=base_url
		self.apiKey=apiKey
		self.secret=secret
		self.orders={}
	
	def fetchBalance(self):#dict {'seer':10000000,'ETH':10000}
		token_list=['seer','eth']
		action_url='/api/v2/users/me'
		payload='GET|'+action_url+'|access_key='+self.apiKey
		signature= hmac.new(bytes(self.secret,'utf-8'),bytes(payload,'utf-8'),digestmod=hashlib.sha256)\
		.hexdigest()
		request_url=self.base_url+action_url+'?access_key='+self.apiKey+\
		'&signature='+signature
		result=requests.get(request_url).json()#dict
		self.balance={}#dict
		for balance_dict in result['accounts']:
			if( balance_dict['currency'].lower() in token_list):
				#print(balance_dict)
				self.balance[balance_dict['currency'].lower()]=balance_dict['balance']
		return self.balance	

	def fetch_order_book(self,sMarket,limit=1):
		#/api/v2/order_book?market=otbeth&sell_limit=1&buy_limit=1
		action_url='/api/v2/order_book'
		request_url=self.base_url+action_url+'?market='+self.my_market+'&sell_limit='+str(limit)+'&buy_limit='+str(limit)
		r=requests.get(request_url)
		if(r.ok):##返回200代表成功
			self.orders=r.json()
			self.buy_id=self.orders['bids'][0]['id']
			self.buy_price=float(self.orders['bids'][0]['price'])
			self.buy_amount=float(self.orders['bids'][0]['remaining_volume'])
			self.buy_currency=self.buy_price*self.buy_amount
			self.orders['bids'][0]['currency']=self.buy_currency
			self.sell_id=self.orders['asks'][0]['id']
			self.sell_price=float(self.orders['asks'][0]['price'])
			self.sell_amount=float(self.orders['asks'][0]['remaining_volume'])
			self.buy_currency=self.sell_price*self.sell_amount
			self.orders['asks'][0]['currency']=self.buy_currency
			# print('--------------------------OTCBTC市场行情--------------------------')
			# print('bids(买):买1价=%.8f'%self.buy_price+',数量=%.2f'%self.buy_amount)
			# print('asks(卖):卖1价=%.8f'%self.sell_price+',数量=%.2f'%self.sell_amount)
		else:	#失败
			print('OTCBTC获取行情失败！Error code:'+result.getcode()+'，continue！')
		return r

	def getMyOrders(self):#return list,use after initiated exchange
		#获取OTCBTC 我的订单数据
		action_url='/api/v2/orders'
		payload='GET|'+action_url+'|access_key='+self.apiKey+'&market='+self.market
		signature= hmac.new(bytes(self.secret,'utf-8'),bytes(payload,'utf-8'),digestmod=hashlib.sha256)\
		.hexdigest()
		request_url=self.base_url+action_url+'?access_key='+self.apiKey+\
		'&market='+self.market+'&signature='+signature
		r=requests.get(request_url)
		self.my_orders=r.json()#返回LIST类型，里面包含若干个DICT
		return self.my_orders
		
	def getMyTrades(self):#return list
		action_url='/api/v2/trades/my'
		payload='GET|'+action_url+'|access_key='+self.apiKey+'&market='+self.market
		signature= hmac.new(bytes(self.secret,'utf-8'),bytes(payload,'utf-8'),digestmod=hashlib.sha256)\
		.hexdigest()
		request_url=self.base_url+action_url+'?access_key='+self.apiKey+\
		'&market='+self.market+'&signature='+signature
		r=requests.get(request_url)
		self.my_trades=r.json()#返回LIST类型，里面包含若干个DICT
		return self.my_trades

	def orderExists(self,sOrder):#-1 not exits
		self.getMyOrders()
#		return (sOrder in self.getMyOrders().values())
		orders_value=''
		for data_dict in self.my_orders:
			# print(data_dict)
			# print(str(i)+':'+str(data_list[i].values()))
			# print(data_dict.keys())
			# i=i+1			
			# for key in data_dict:#结构化获取订单数
				# print(key+':'+str(data_dict[key]))
			# print('\n')
			orders_value=orders_value+'\n'+str(data_dict.values())#订单值拼装到字符串中，方便查找		
		return orders_value.find(sOrder)#-1 not exits
	
	def cancelOrder(self,sOrder):#POST
		action_url='/api/v2/order/delete'
		payload='POST|'+action_url+'|access_key='+self.apiKey+'&id='+sOrder
		signature= hmac.new(bytes(self.secret,'utf-8'),bytes(payload,'utf-8'),digestmod=hashlib.sha256)\
		.hexdigest()
		request_url=self.base_url+action_url
		post_data={'id':sOrder,'access_key':self.apiKey,'signature':signature}#must be dict
		r=requests.post(request_url,post_data)
		return r.ok

	def cancelOrders(self):#Post,Cancel all my orders
		action_url='/api/v2/orders/clear'
		payload='POST|'+action_url+'|access_key='+self.apiKey
		signature= hmac.new(bytes(self.secret,'utf-8'),bytes(payload,'utf-8'),digestmod=hashlib.sha256)\
		.hexdigest()
		request_url=self.base_url+action_url
		post_data={'access_key':self.apiKey,'signature':signature}#must be dict
		r=requests.post(request_url,post_data)
		return r.ok
		
	def createOrder(self,type,market,side,amount,price):#type='limit'(no use,compatible with ccxt)
# Code: 200
# Response Body:
# {  
   # "id": 1,                                   // Unique order id. 
   # "side": "sell",                            // Either 'sell' or 'buy'.
   # "ord_type": "limit",                       // Type of order, now only 'limit'.
   # "price": "0.002",                          // Price for each unit. e.g. If you sell/buy 100 OTB at 0.002 ETH, the price is '0.002'.
   # "avg_price": "0.0",                        // Average execution price, average of price in trades.
   # "state": "wait",                           // One of 'wait', 'done', or 'cancel'. An order in 'wait' is an active order, waiting fullfillment; a 'done' order is an order fullfilled; 'cancel' means the order has been cancelled.
   # "market": "otbeth",                        // The market in which the order is placed, e.g. 'otbeth'. All available markets can be found at /api/v2/markets.
   # "created_at": "2017-02-01T00:00:00+08:00", // Trade create time in iso8601 format.
   # "volume": "100.0",                         // The amount user want to sell/buy. An order could be partially executed, e.g. an order sell 100 otb can be matched with a buy 60 otb order, left 40 otb to be sold; in this case the order's volume would be '100.0', its remaining_volume would be '40.0', its executed volume is '60.0'.
   # "remaining_volume": "100.0",               // The remaining volume
   # "executed_volume": "0.0",                  // The executed volume
   # "trades_count": 0                          // Number of trades under this order
# }
		price=str(price)
		amount=str(amount)
		create_url='/api/v2/orders'
		payload='POST|'+create_url+'|access_key='+self.apiKey+'&market='+market+'&price='+\
		price+'&side='+side+'&volume='+amount
		signature= hmac.new(bytes(self.secret,'utf-8'),bytes(payload,'utf-8'),digestmod=hashlib.sha256)\
		.hexdigest()
		request_url=self.base_url+create_url
		post_data={'market':market,'side':side,'volume':amount,'price':price,'access_key':self.apiKey,\
		'signature':signature}#must be dict
		r=requests.post(request_url,post_data)
		return r
	
	class order(object):
		def __init__(self,market,side,price,remaining_volume):
			self.market=market
			self.side=side
			self.price=price
			self.remaining_volume=remaining_volume