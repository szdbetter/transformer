import ccxt
from pprint import pprint
import time
import datetime
from twilio.rest import Client
import requests
import sqlite3
import mylib	#my python library

def fExits(sPath,str):#-1不存在
	with open(sPath,'r') as f:
		i=(f.read().find(str))
		f.close()
		return i
		
def fAppend(sPath,str):
	with open(sPath,'a') as f:
		i=f.write(str)
		f.close()
		return i

#控制变量
run_max=10000000#程序自动执行多少次退出
error_max=2#达到多少条错误时停止执行
path='C:\\Users\\Administrator\\Desktop\\Python\\'

# CREATE TABLE `orders` (
	# `order_id`	TEXT NOT NULL UNIQUE,
	# `exchange`	TEXT NOT NULL,
	# `side`	TEXT NOT NULL,
	# `price`	REAL NOT NULL,
	# `order_amount`	NUMERIC,
	# `sold_amount`	NUMERIC,
	# `status`	TEXT,
	# `create_time`	TEXT NOT NULL DEFAULT 'now'
# );
if False:
	conn = sqlite3.connect(path+'\\db\\trade.sqlite3')
	# 创建一个Cursor:
	cursor = conn.cursor()
	# 继续执行一条SQL语句，插入一条记录:
	cursor.execute('insert into user (id, name) values (\'1\', \'Michael\')')
	#insert into orders values('3','lbank','sell',1,10,1,'wait',datetime('now'))
	# 通过rowcount获得插入的行数:
	cursor.rowcount
	# 关闭Cursor:
	cursor.close()
	# 提交事务:
	conn.commit()
	# 关闭Connection:
	conn.close()

def fDBOperate(sql):
	sDB=path+'\\db\\trade.sqlite3'
	conn = sqlite3.connect(sDB)
	cursor = conn.cursor()
	cursor.execute(sql)
	#insert into orders values('3','lbank','sell',1,10,1,'wait',datetime('now'))
	iRowCount=cursor.rowcount
	cursor.close()
	conn.commit()
	conn.close()
	return iRowCount

def fDBInsert(sTable,sValue):
	sDB=path+'\\db\\trade.sqlite3'
	conn = sqlite3.connect(sDB)
	cursor = conn.cursor()
	sql='insert into '+sTable+' values('
	for value in sValue:
		sql=sql+str(value)+','
	sql=sql[0:-1]+')'
#	now=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
	cursor.execute(sql)
	iRowCount=cursor.rowcount
	cursor.close()
	conn.commit()
	conn.close()
	return iRowCount

#短信发送配置（Twilio)
twilio_from_number='+19104087972'
twilio_to_number='+8618820465120'
twilio_sid='ACb8c4914cad3188119b26d41146ccebe8'
twilio_token='ff391f0a056f634aa66cab653494b197'
sms=Client(twilio_sid,twilio_token)
#交易策略变量，达到多少利差时执行
config_profit_hedge_rate=0.03
config_profit_future_rate=0.05
config_profit_token_amount=10000
config_token_list=['seer','eth']
#获取多少条交易所订单数据
order_limit=1
buy_limit=order_limit
sell_limit=order_limit

#初始化交易所
#	初始化LBank
lbank=ccxt.lbank({"apiKey":"918150d8-ba8b-4fc6-9a65-a40a9fe54c32","secret":"D67F10FD08972933C9536CDC7FA75457",})
lbank.fee=0.001
lbank.my_market='SEER/ETH'
lbank.balance=lbank.fetch_balance()#lbank.balance['SEER']['free']/lbank.balance['ETH']['free']
lbank.balance=mylib.fParseExBalance(lbank)
#	初始化OTCBTC
otcbtc=mylib.myExchange('otcbtc','https://bb.otcbtc.com','swoEvDN6RUtCxb35afApyMP1yNbxFjPQPFbeMMsr','iMB40jQcwQ9PcdukJ5OfMO7IwuCPID8JsvzndMxz')
otcbtc.my_market='seereth'		#目前仅针对seer
otcbtc.fee=0.001
otcbtc.balance=otcbtc.fetchBalance()#dict {'seer':10000000,'ETH':10000}
otcbtc.balance=mylib.fParseExBalance(otcbtc)
#开始计算并循环获取交易所数据
count=0
#while True:
count=count+1
if(count==10000): exit()#执行若干次退出

#取LBANK市场订单数据
lbank.order_book=lbank.fetch_order_book('SEER/ETH',limit=1)

#lbank.buy_price=format(lbank.order_book['bids'][0][0],'.8f')#不能删除FORMAT！否则只能取到小数点后6位；原始数据用科学计数法表示，需要改为8位小数浮点'2.905e-05'
lbank.buy_price=lbank.order_book['bids'][0][0]
lbank.buy_amount=lbank.order_book['bids'][0][1]
lbank.buy_currency=lbank.buy_price*lbank.buy_amount
lbank.sell_price=lbank.order_book['asks'][0][0]
lbank.sell_amount=lbank.order_book['asks'][0][1]
lbank.sell_currency=lbank.sell_price*lbank.sell_amount


print('--------------------------LBank 市场行情--------------------------')
print('bids(买):买1价=%s'%lbank.buy_price+',数量=%2f'%lbank.buy_amount)
print('asks(卖):卖1价=%s'%lbank.sell_price+',数量=%2f'%lbank.sell_amount)

#取OTCBTC市场订单数据
result=otcbtc.fetch_order_book(otcbtc.my_market,limit=1)
if result.ok:
	print('--------------------------OTCBTC市场行情--------------------------')
	print('bids(买):买1价=%.8f'%otcbtc.buy_price+',数量=%.2f'%otcbtc.buy_amount)
	print('asks(卖):卖1价=%.8f'%otcbtc.sell_price+',数量=%.2f'%otcbtc.sell_amount)
else:	#失败
	print('OTCBTC获取行情失败！Error code:'+result.getcode()+'，continue！')
	sleep(10)
	#continue
	
if True:
	#***测试需要，手动构建测试数据*****#
	mylib.fBuildTestData(lbank,otcbtc,1)
	print('\n'+'*' *20+'LBank Test'+'*' *20)
	print('bids(买):买1价=%.8f'%lbank.buy_price+',数量=%2f'%lbank.buy_amount)
	print('asks(卖):卖1价=%.8f'%lbank.sell_price+',数量=%2f'%lbank.sell_amount)
	print('*' *20+'OTCBTC Test'+'*' *20)
	print('bids(买):买1价=%.8f'%otcbtc.buy_price+',数量=%.2f'%otcbtc.buy_amount)
	print('asks(卖):卖1价=%.8f'%otcbtc.sell_price+',数量=%.2f'%otcbtc.sell_amount)
	#****Test Data End****


#执行量化策略
#1、简单对冲策略（一高一低）
#1.1、A低B高：A卖1价低于B买1价，A买B卖(a.ask_price<b.bid_price)，多买少卖之间即为盈利
#价格判断
now=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
sStrategy=''
if(lbank.buy_price/otcbtc.buy_price>1.05):
	exLow=otcbtc
	exHigh=lbank
	sStrategy='期货对冲1'
if(lbank.buy_price/otcbtc.buy_price<0.95):
	exLow=lbank
	exHigh=otcbtc
	sStrategy='期货对冲2'
if(lbank.sell_price/otcbtc.sell_price>1.05):
	exLow=otcbtc
	exHigh=lbank
	sStrategy='期货对冲3'
if(lbank.sell_price/otcbtc.sell_price<0.95):
	exLow=lbank
	exHigh=otcbtc
	sStrategy='期货对冲4'
if(float(lbank.sell_price)<otcbtc.buy_price):#LBank(A)低OTCBTC(B)高：A卖1价低于B买1价，A买B卖
	exLow=lbank
	exHigh=otcbtc
	sStrategy='现货对冲1'
if(otcbtc.sell_price<float(lbank.buy_price)):
	exLow=otcbtc
	exHigh=lbank
	sStrtegy='现货对冲2'


print(sStrategy)
if(sStrategy.find('现货对冲')>-1):#hedge,send low exchange & high exchange order now
	profit_hedge_rate=(exHigh.buy_price-exLow.sell_price)/exLow.sell_price
	# profit_balance_sell=exHigh.sell_price-exLow.sell_price
	# profit_balance_buy=exHigh.buy_price-exLow.buy_price
	
	if(profit_hedge_rate>=config_profit_hedge_rate):
		currency_hedge=min(exLow.balance['eth'],exLow.sell_currency,exHigh.balance['seer']*exHigh.buy_price,exHigh.buy_currency)
		token_sell_amount=currency_hedge/exHigh.buy_price
		token_buy_amount=currency_hedge/exLow.sell_price
		profit_token_amount=token_buy_amount-token_sell_amount
		#choose deal ETH/currency from 4 params(should be 5,include already traded orders in local DB)
		# print('*'*10+sStrategy+'：'+exLow.name+'低'+exHigh.name+'高'+'*'*10)
		# print(exLow.balance['eth'])
		# print(exLow.sell_currency)
		# print(exHigh.balance['seer']*exHigh.buy_price)
		# print(exHigh.buy_currency)
		# print(currency_hedge)
		# print('sell amount:%f' %token_sell_amount)
		# print('buy amount:%f' % token_buy_amount)
		# print('profit token amount:%f' % profit_token_amount)
		# print(mylib.fParsePercent(profit_hedge_rate))
		# input('wait')
		#Create Order,lower buy , higher sell


		########## continue from here 0519
		order_exLow=exLow.create_order(exLow.my_market,'limit','buy',token_buy_amount,exLow.sell_price/50)
		input('lbank order creating...'+order_exLow['status']+'\nwait...')
		if(order_exLow['status'].lower()=='true'):
			print('牛！Lbank order Created!')
			i=fDBInsert('orders',['\''+order_exLow['id']+'\',\'lbank\'','\'buy\'',\
			token_sell_price/50,token_buy_amount,0,'\'wait\'','datetime(\'now\')'])
			if(i>0): print('订单'+order_exLow['id']+' created!')
		order_exHigh=lbank.create_order(exHigh.my_market,'limit','sell',token_sell_amount,exHigh.buy_price*50)
		if(result.ok):
			print('牛！OTCBTC order Created!')		
			otcbtc.order=result.json()
			i=fDBInsert('orders',['\''+str(otcbtc.order['id'])+'\',\'otcbtc\'','\'sell\'',\
			format(50*token_sell_price,'.8f'),token_sell_amount,0,'\'wait\'','datetime(\'now\')'])
			if(i>0): print('订单'+str(otcbtc.order['id'])+' created!')
		

		msg_body='[SEER/ETH]LBank低OTCBTC高!'
		msg_body=msg_body+'\nLbank卖1价格：'+str(lbank.sell_price)+'，数量'+str(lbank.sell_amount)
		msg_body=msg_body+'\nOTCBTC买1价格：'+str(format(otcbtc.buy_price,'.8f'))+'，数量'+str(otcbtc.buy_amount)
		msg_body=msg_body+'\n统计：利润：'+str(int(token_profit_amount))+'，利差：'+str(format(token_profit_rate*100,'.2f'))+'%'
		if(fExits(path+'sms.txt',msg_body)==-1):#该短信未发送过
			sms.messages.create(to=twilio_to_number,from_=twilio_from_number,body=msg_body)
			fAppend(path+'sms.txt',msg_body)#发送短信并写入文件
			print('短信发送成功！')
		else:
			print('该条提醒短信已发送过！')
			
if(sStrategy.find('期货对冲')>-1):#future,send low exchange bid & high exchange ask order,and keep monitoring
	pass
if(sStrategy==''):#do nothing
	pass

print('---------------- 行情数据(第'+str(count)+'次),'+str(now)+'----------------')
if(float(lbank.sell_price)<otcbtc.buy_price):#LBank(A)低OTCBTC(B)高：A卖1价低于B买1价，A买B卖
	#判断对应市场买1卖1订单是否自己挂的，如果挂的就取消
	#判断OTCBTC买1 / LBANK 卖1是不是自己挂的，是的话挂高（或低）了，取消
	# if(otcbtc.orderExists(str(otcbtc.buy_id))!=-1):#买1单是自己挂的，猪头
		# print('order exitst!')
		# otcbtc.cancelOrder(str(otcbtc.buy_id))
		#start  over
	# else:
		# print('order doesn\'t exist!')
		




	
	if(float(token_profit_rate)>0.02 or float(token_profit_amount)>3000):
		print('\n ********************场景1成交机会出现！********************\n')
		#检查LBANK卖1订单 或 OTCBTC 买1订单自己挂的 OR 
		#YES：取消再进行下一轮判断
		#NO：
		#LBANK 发送购买订单，价格为token_buy_price，数量为token_buy_amount，判断订单状态是否成功
		#OTCBTC发送出售订单，价格为token_sell_price，数量为token_sell_amount（如LBANK购买不成功不发送）
		#如不是双方订单都成功，给出告警
		

else:
	print('//场景1不成立：未发现LBank(A)卖1价低于OTCBTC(B)买1价场景！')
exit()
if(otcbtc.sell_price<float(lbank.buy_price)):#OTCBTC低LBANK高，OTCBTC买，LBANK卖		
#if True:
	print('//场景2：OTCBTC低LBank高：OTCBTC卖1价低于LBank买1价，OTCBTC买LBank卖')
	token_profit_rate=(1-lbank.fee-otcbtc.fee)*(otcbtc.sell_price-float(lbank.buy_price))/otcbtc.sell_price#价差
	#＝＝＝＝＝＝＝OTCBTC买＝＝＝＝＝＝＝
	token_buy_amount=min(lbank.buy_amount,otcbtc.sell_amount)
	token_buy_price=otcbtc.sell_price
	currency_buy=token_buy_amount*token_buy_price#低价交易所（A）购买总价（即ETH总数）
	#＝＝＝＝＝＝＝Lbank 卖＝＝＝＝＝＝＝
	token_sell_price=lbank.buy_price	#以高价交易所买1价卖出
	token_sell_amount=currency_buy/float(token_sell_price)#卖出数量是另一交易所购买总价/买1价
	#＝＝＝＝＝＝＝计算盈利＝＝＝＝＝＝＝
	token_profit_rate=(1-lbank.fee-otcbtc.fee)*(float(token_sell_price)-token_buy_price)/token_buy_price
	token_profit_amount=token_buy_amount-token_sell_amount
	
	print('买入\t价格：%.8f\t数量：%.8f\t总价：%.8f' %(float(token_buy_price),token_buy_amount,currency_buy))
	print('卖出\t价格：%.8f\t数量：%.8f\t总价：%.8f' %(float(token_sell_price),token_sell_amount,currency_buy))
	print('统计\t利润：%f\t利差：%.2f%%' %(token_profit_amount,100*token_profit_rate,))
	if(float(token_profit_rate)>0.02 or float(token_profit_amount)>3000):
		print('\n\033[5;35m ********************场景2成交机会出现！********************\n')
		msg_body='[SEER/ETH]LBank高OTCBTC低!'
		# msg_body=msg_body+'\nLbank卖1价格：'+str(lbank.sell_price)+'，数量'+str(lbank.sell_amount)
		# msg_body=msg_body+'\nOTCBTC买1价格：'+str(format(otcbtc.buy_price,'.8f'))+'，数量'+str(otcbtc.buy_amount)
		msg_body=msg_body+'\n统计：利润：'+str(int(token_profit_amount))+'，利差：'+str(format(token_profit_rate*100,'.2f'))+'%'
		if(fExits(path+'sms.txt',msg_body)==-1):#该短信未发送过
			sms.messages.create(to=twilio_to_number,from_=twilio_from_number,body=msg_body)
			fAppend(path+'sms.txt',msg_body)#发送短信并写入文件
			print('短信发送成功！')
		else:
			print('该条提醒短信已发送过！')
else:
	print('//场景2不成立：未发现OTCBTC(A)卖1价低于LBANK(B)买1价场景！')
print('\n')
time.sleep(5)

# request_url='/api/v2/order_book'
# exchange='otcbtc'
# api_key='1oUTkWjMs06Jnz6gY1gR8p9CuGlxby8y0N8EYKvU'
# payload='GET|/api/v2/users/me|access_key=1oUTkWjMs06Jnz6gY1gR8p9CuGlxby8y0N8EYKvU'
# market='market=seereth'
# sell_limit=1
# buy_limit=1
# param='&sell_limit='+str(sell_limit)+'&buy_limit='+str(buy_limit)	#读取订单

# 测试auth api
# reuqest_url='/api/v2/users/me|access_key='
# param=''
# ref url :/api/v2/order_book?market=otbeth&sell_limit=1&buy_limit=1
# sample url:https://bb.otcbtc.com/api/v2/order_book?market=seereth&sell_limit=1&buy_limit=1
# url=base_url+request_url+'?'+market+param
# print(url)
# page=urllib.request.urlopen(url)
# data=page.read()
# print(data)
# lbank=ccxt.lbank().fetch_order_book('seer/eth',5);
# print(lbank)
